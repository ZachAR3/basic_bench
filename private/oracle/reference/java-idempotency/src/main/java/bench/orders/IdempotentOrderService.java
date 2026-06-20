package bench.orders;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.function.LongSupplier;

public final class IdempotentOrderService {
    private static final class Entry {
        final byte[] fingerprint;
        final CompletableFuture<OrderResult> future = new CompletableFuture<>();
        long expiresAt = Long.MAX_VALUE;
        long access;

        Entry(byte[] fingerprint, long access) {
            this.fingerprint = fingerprint;
            this.access = access;
        }
    }

    private final Object lock = new Object();
    private final Map<String, Entry> requests = new HashMap<>();
    private final Map<String, OrderResult> orders = new HashMap<>();
    private final LongSupplier clockMillis;
    private final long ttlMillis;
    private final int maxEntries;
    private long sequence;

    public IdempotentOrderService(LongSupplier clockMillis, long ttlMillis, int maxEntries) {
        if (clockMillis == null || ttlMillis <= 0 || maxEntries <= 0) {
            throw new IllegalArgumentException("invalid cache configuration");
        }
        this.clockMillis = clockMillis;
        this.ttlMillis = ttlMillis;
        this.maxEntries = maxEntries;
    }

    public OrderResult create(
        String idempotencyKey,
        byte[] requestBody,
        Callable<OrderResult> createAction
    ) throws Exception {
        if (idempotencyKey == null || idempotencyKey.isBlank()
            || requestBody == null || createAction == null) {
            throw new IllegalArgumentException("missing request data");
        }
        byte[] fingerprint = MessageDigest.getInstance("SHA-256")
            .digest(requestBody.clone());
        Entry entry;
        boolean owner = false;
        synchronized (lock) {
            long now = clockMillis.getAsLong();
            requests.entrySet().removeIf(item ->
                item.getValue().future.isDone() && item.getValue().expiresAt <= now);
            entry = requests.get(idempotencyKey);
            if (entry != null) {
                if (!Arrays.equals(entry.fingerprint, fingerprint)) {
                    return OrderResult.conflict();
                }
                entry.access = ++sequence;
            } else {
                if (requests.size() >= maxEntries) {
                    requests.entrySet().stream()
                        .filter(item -> item.getValue().future.isDone())
                        .min(Comparator.comparingLong(item -> item.getValue().access))
                        .ifPresent(item -> requests.remove(item.getKey()));
                }
                if (requests.size() >= maxEntries) {
                    throw new IllegalStateException("all idempotency slots are busy");
                }
                entry = new Entry(fingerprint, ++sequence);
                requests.put(idempotencyKey, entry);
                owner = true;
            }
        }

        if (owner) {
            try {
                OrderResult created = normalize(createAction.call());
                synchronized (lock) {
                    orders.put(created.orderId(), created);
                    entry.expiresAt = Math.addExact(clockMillis.getAsLong(), ttlMillis);
                    entry.access = ++sequence;
                }
                entry.future.complete(created);
            } catch (Throwable failure) {
                synchronized (lock) {
                    requests.remove(idempotencyKey, entry);
                }
                entry.future.completeExceptionally(failure);
                if (failure instanceof Exception exception) throw exception;
                throw failure;
            }
        }
        try {
            return copy(entry.future.get());
        } catch (ExecutionException failure) {
            Throwable cause = failure.getCause();
            if (cause instanceof Exception exception) throw exception;
            throw new RuntimeException(cause);
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw interrupted;
        }
    }

    public OrderResult get(String orderId, String ifNoneMatch) {
        OrderResult result;
        synchronized (lock) {
            result = orders.get(orderId);
        }
        if (result == null) return new OrderResult(404, null, new byte[0], null);
        if (result.etag().equals(ifNoneMatch)) return OrderResult.notModified(result.etag());
        return copy(result);
    }

    private static OrderResult normalize(OrderResult value) throws Exception {
        if (value == null || value.orderId() == null || value.status() < 200
            || value.status() >= 300) {
            throw new IllegalArgumentException("create action returned invalid result");
        }
        String etag = value.etag();
        if (etag == null) {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.body());
            etag = "\"" + java.util.HexFormat.of().formatHex(digest) + "\"";
        }
        return new OrderResult(value.status(), value.orderId(), value.body(), etag);
    }

    private static OrderResult copy(OrderResult value) {
        return new OrderResult(value.status(), value.orderId(), value.body(), value.etag());
    }
}
