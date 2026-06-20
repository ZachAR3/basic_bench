A 16-bit emulator memory bus works for simple aligned RAM access but violates
CPU-visible semantics around paging, faults, and devices. Repair it without
changing the public header API.

Requirements:

- Multi-byte operations are little-endian, may cross page boundaries, and wrap
  at `0xffff` exactly as a 16-bit CPU address bus does.
- Enforce read, write, and execute permissions. `MemoryFault` must report the
  exact virtual byte address and requested access.
- Writes are precise: validate the complete operation before changing RAM,
  invoking MMIO, or adding cycles. A fault leaves all state unchanged.
- Page remap and unmap immediately invalidate stale TLB translations.
- An operation fully contained in one MMIO region invokes the device exactly
  once with width 1, 2, or 4. Operations mixing MMIO and RAM fault precisely
  and produce no device side effects.
- `fetch_add32` is one atomic bus operation from the device's perspective and
  returns the old value.
- Charge one cycle for RAM operations and four cycles for MMIO operations,
  independent of width. Faults charge zero.

Use C++20 and the standard library only. No tests or build files are provided.
