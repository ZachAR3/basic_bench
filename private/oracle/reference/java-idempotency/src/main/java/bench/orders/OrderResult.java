package bench.orders;

import java.util.Arrays;

public final class OrderResult {
    private final int status;
    private final String orderId;
    private final byte[] body;
    private final String etag;

    public OrderResult(int status, String orderId, byte[] body, String etag) {
        this.status = status;
        this.orderId = orderId;
        this.body = body == null ? new byte[0] : body.clone();
        this.etag = etag;
    }

    public int status() { return status; }
    public String orderId() { return orderId; }
    public byte[] body() { return body.clone(); }
    public String etag() { return etag; }

    public static OrderResult conflict() {
        return new OrderResult(409, null, new byte[0], null);
    }

    public static OrderResult notModified(String etag) {
        return new OrderResult(304, null, new byte[0], etag);
    }

    @Override public boolean equals(Object other) {
        if (!(other instanceof OrderResult value)) return false;
        return status == value.status
            && java.util.Objects.equals(orderId, value.orderId)
            && Arrays.equals(body, value.body)
            && java.util.Objects.equals(etag, value.etag);
    }
}
