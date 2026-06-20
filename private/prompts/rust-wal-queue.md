A dependency-free Rust job queue acknowledges work in memory but loses or
duplicates jobs after crashes. Implement a durable write-ahead log while
preserving the public API.

Requirements:

- Every state-changing operation appends a framed record with a length and
  checksum before publishing the new in-memory state.
- Opening replays the log. An incomplete final frame is an interrupted append
  and must be ignored; checksum corruption in a complete frame is an error.
- Task IDs are globally idempotent, including after acknowledgement and
  compaction. Re-enqueueing a known ID returns `false`.
- Claims use the injected clock. Expired leases become claimable again with a
  new token. `ack` succeeds only for the current lease token; stale tokens
  cannot acknowledge reassigned work.
- Concurrent callers must not claim one live lease twice.
- `compact` writes a complete replacement to a unique temporary file, syncs
  it, atomically renames it, and preserves pending, leased, and acknowledged
  IDs across reopen. Temporary files are removed on failure.
- Reject empty IDs and zero-length leases. Do not panic on poisoned locks or
  malformed input.

Use stable Rust and the standard library only. Do not add crates.
