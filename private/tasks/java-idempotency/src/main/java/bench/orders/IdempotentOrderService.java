package bench.orders;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.function.LongSupplier;

public final class IdempotentOrderService {
    private final Map<String, OrderResult> requests = new HashMap<>();
    private final Map<String, OrderResult> orders = new HashMap<>();

    public IdempotentOrderService(LongSupplier clockMillis, long ttlMillis, int maxEntries) {
    }

    public OrderResult create(
        String idempotencyKey,
        byte[] requestBody,
        Callable<OrderResult> createAction
    ) throws Exception {
        OrderResult existing = requests.get(idempotencyKey);
        if (existing != null) return existing;
        OrderResult created = createAction.call();
        requests.put(idempotencyKey, created);
        orders.put(created.orderId(), created);
        return created;
    }

    public OrderResult get(String orderId, String ifNoneMatch) {
        OrderResult result = orders.get(orderId);
        if (result == null) return new OrderResult(404, null, new byte[0], null);
        return result;
    }
}
