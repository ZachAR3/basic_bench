import bench.orders.IdempotentOrderService;
import bench.orders.OrderResult;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public final class JavaChecks {
    static void require(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
    static OrderResult result(String id, byte[] body) {
        return new OrderResult(201, id, body, null);
    }

    static void dedupe() throws Exception {
        var service = new IdempotentOrderService(System::currentTimeMillis, 10000, 32);
        var calls = new AtomicInteger();
        var start = new CountDownLatch(1);
        try (var pool = Executors.newFixedThreadPool(12)) {
            List<Future<OrderResult>> futures = new ArrayList<>();
            for (int i = 0; i < 12; i++) {
                futures.add(pool.submit(() -> {
                    start.await();
                    return service.create("key", "same".getBytes(), () -> {
                        calls.incrementAndGet();
                        Thread.sleep(40);
                        return result("o-1", "body".getBytes());
                    });
                }));
            }
            start.countDown();
            for (var future : futures) require(future.get().orderId().equals("o-1"), "wrong result");
        }
        require(calls.get() == 1, "create action ran " + calls.get() + " times");
    }

    static void conflictRetry() throws Exception {
        var service = new IdempotentOrderService(System::currentTimeMillis, 10000, 8);
        service.create("key", "one".getBytes(), () -> result("o-1", "one".getBytes()));
        var calls = new AtomicInteger();
        require(service.create("key", "two".getBytes(), () -> {
            calls.incrementAndGet(); return result("bad", new byte[0]);
        }).status() == 409, "different payload was accepted");
        require(calls.get() == 0, "conflicting action ran");
        try {
            service.create("retry", "x".getBytes(), () -> { throw new Exception("boom"); });
        } catch (Exception expected) {}
        require(service.create("retry", "x".getBytes(), () -> result("ok", "ok".getBytes()))
            .orderId().equals("ok"), "failed key was poisoned");
    }

    static void expiryCapacity() throws Exception {
        var now = new AtomicLong(100);
        var service = new IdempotentOrderService(now::get, 10, 2);
        var calls = new AtomicInteger();
        service.create("a", new byte[]{1}, () -> result("a", new byte[]{1}));
        service.create("b", new byte[]{2}, () -> result("b", new byte[]{2}));
        service.create("a", new byte[]{1}, () -> { throw new AssertionError(); });
        service.create("c", new byte[]{3}, () -> result("c", new byte[]{3}));
        service.create("b", new byte[]{2}, () -> { calls.incrementAndGet(); return result("b2", new byte[]{2}); });
        require(calls.get() == 1, "least recently used entry was not evicted");
        now.set(111);
        service.create("a", new byte[]{1}, () -> { calls.incrementAndGet(); return result("a2", new byte[]{1}); });
        require(calls.get() == 2, "expired entry was reused");
    }

    static void defensiveEtag() throws Exception {
        var service = new IdempotentOrderService(System::currentTimeMillis, 10000, 8);
        byte[] request = "request".getBytes(StandardCharsets.UTF_8);
        byte[] body = "response".getBytes(StandardCharsets.UTF_8);
        var created = service.create("k", request, () -> result("id", body));
        request[0] = 0;
        body[0] = 0;
        byte[] exposed = created.body();
        exposed[0] = 0;
        var fetched = service.get("id", null);
        require(new String(fetched.body(), StandardCharsets.UTF_8).equals("response"), "body was shared");
        require(fetched.etag().startsWith("\"") && fetched.etag().endsWith("\""), "etag not strong");
        var cached = service.get("id", fetched.etag());
        require(cached.status() == 304 && cached.body().length == 0, "conditional GET failed");
    }

    static void validationConcurrency() throws Exception {
        try { new IdempotentOrderService(System::currentTimeMillis, 0, 1); throw new AssertionError(); }
        catch (IllegalArgumentException expected) {}
        var service = new IdempotentOrderService(System::currentTimeMillis, 10000, 4);
        var entered = new CountDownLatch(2);
        var release = new CountDownLatch(1);
        try (var pool = Executors.newFixedThreadPool(2)) {
            var one = pool.submit(() -> service.create("a", new byte[]{1}, () -> {
                entered.countDown(); release.await(); return result("a", new byte[]{1});
            }));
            var two = pool.submit(() -> service.create("b", new byte[]{2}, () -> {
                entered.countDown(); release.await(); return result("b", new byte[]{2});
            }));
            require(entered.await(2, java.util.concurrent.TimeUnit.SECONDS), "user action ran under global lock");
            release.countDown();
            one.get(); two.get();
        }
    }

    public static void main(String[] args) throws Exception {
        switch (args[0]) {
            case "dedupe" -> dedupe();
            case "conflict" -> conflictRetry();
            case "expiry" -> expiryCapacity();
            case "etag" -> defensiveEtag();
            case "validation" -> validationConcurrency();
            default -> throw new IllegalArgumentException(args[0]);
        }
    }
}
