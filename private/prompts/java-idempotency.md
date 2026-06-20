A Java order backend occasionally creates duplicate orders and serves mutable
response data. Repair the standard-library-only implementation without changing
the public constructors or method signatures.

Requirements:

- Concurrent calls using the same idempotency key and identical request bytes
  must execute `createAction` exactly once and receive equivalent results.
- Reusing a live key with different bytes returns HTTP 409 without executing
  the action.
- Failed or cancelled actions must not poison the key; a later retry may run.
- Entries expire using the injected clock and TTL. Capacity is bounded by
  `maxEntries`; evict expired entries first, then the least recently completed
  idempotency entry. Non-positive constructor arguments are invalid.
- Inputs and returned bodies must be defensively copied.
- Successful creates are retrievable by order ID. `get` must implement strong
  ETag matching and return 304 with an empty body when `If-None-Match` matches.
- Keep the implementation thread-safe without holding a global lock while
  user code runs.

No tests or build system are provided. Use only Java 21 standard-library APIs.
