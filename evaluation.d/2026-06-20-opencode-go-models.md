# MiMo V2.5, DeepSeek V4 Flash, and Qwen3.6 Plus

Date: 2026-06-20

The three models were run sequentially through OpenCode Go on all sixteen
tasks. Each task used a fresh workspace, held-out grading, no web access, and
one scored attempt. No provider timeout or fresh-session reset affected these
runs.

Costs are calculated per task from provider-reported uncached input, output,
cache reads, and cache writes. The rates came from
`opencode models opencode-go --verbose` on the test date. Qwen3.6 Plus uses its
higher rate for requests above 256K context.

## Summary

| Model | Task passes | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| MiMo V2.5 | 9/16 | 116/160 | 3,374.195 s | $0.1459 | 7.0/10 |
| DeepSeek V4 Flash | 8/16 | 116/160 | 2,332.283 s | $0.1181 | 7.5/10 |
| Qwen3.6 Plus | 8/16 | 116/160 | 4,668.412 s | $0.9689 | 8.0/10 |

The syntax score is subjective and reviewer-biased. It rates readability,
reuse, focus, and maintainability, not functional correctness.

## MiMo V2.5

| Task | Score | Time | Cost |
|---|---:|---:|---:|
| lru-update | 10/10 | 33.117 s | $0.0022 |
| config-precedence | 10/10 | 57.399 s | $0.0019 |
| rate-window | 10/10 | 35.893 s | $0.0021 |
| quoted-tokenizer | 0/10 | 105.771 s | $0.0048 |
| schema-migration | 10/10 | 73.729 s | $0.0026 |
| csv-unicode | 10/10 | 40.325 s | $0.0017 |
| stable-toposort | 0/10 | 51.085 s | $0.0028 |
| async-retry | 10/10 | 51.639 s | $0.0022 |
| dst-recurrence | 0/10 | 41.747 s | $0.0027 |
| webdav-endpoint | 10/10 | 439.469 s | $0.0171 |
| react-offline-sync | 6/10 | 233.992 s | $0.0090 |
| java-idempotency | 6/10 | 691.890 s | $0.0171 |
| godot-save-pipeline | 6/10 | 114.809 s | $0.0064 |
| cpp-memory-bus | 8/10 | 213.596 s | $0.0103 |
| rust-wal-queue | 10/10 | 582.439 s | $0.0189 |
| click-context-provenance | 10/10 | 607.295 s | $0.0441 |
| **Total** | **116/160** | **3,374.195 s** | **$0.1459** |

Failures:

- `quoted-tokenizer` discarded an explicitly empty quoted token.
- `stable-toposort` gave declared keys priority over an earlier
  dependency-only node.
- `dst-recurrence` counted a skipped nonexistent wall time against the
  requested occurrence count.
- `react-offline-sync` mutated the caller's initial item array and parsed the
  wrong warehouse parameter shape, dropping repeated and unknown values.
- `java-idempotency` mishandled capacity/expiry eviction and still exposed a
  shared response body.
- `godot-save-pipeline` used an unexpected temporary filename and left
  migrated values as `JsonElement`, breaking numeric access and isolation.
- `cpp-memory-bus` detected mixed RAM/MMIO access but reported the operation's
  starting address rather than the first conflicting byte.

Quality: the code is readable and generally idiomatic, and the full Rust and
Click solutions are strong. The main weakness is patch size: several solutions
are much larger than necessary, duplicate state-transition logic, and become
harder to audit. Syntax score: **7.0/10**.

## DeepSeek V4 Flash

| Task | Score | Time | Cost |
|---|---:|---:|---:|
| lru-update | 10/10 | 22.672 s | $0.0018 |
| config-precedence | 10/10 | 26.866 s | $0.0028 |
| rate-window | 10/10 | 30.211 s | $0.0020 |
| quoted-tokenizer | 0/10 | 244.060 s | $0.0102 |
| schema-migration | 10/10 | 82.336 s | $0.0032 |
| csv-unicode | 10/10 | 37.809 s | $0.0018 |
| stable-toposort | 0/10 | 76.374 s | $0.0038 |
| async-retry | 10/10 | 31.100 s | $0.0022 |
| dst-recurrence | 10/10 | 48.582 s | $0.0029 |
| webdav-endpoint | 10/10 | 116.884 s | $0.0044 |
| react-offline-sync | 8/10 | 199.275 s | $0.0084 |
| java-idempotency | 6/10 | 194.101 s | $0.0076 |
| godot-save-pipeline | 6/10 | 74.195 s | $0.0045 |
| cpp-memory-bus | 8/10 | 165.949 s | $0.0090 |
| rust-wal-queue | 8/10 | 301.158 s | $0.0130 |
| click-context-provenance | 0/10 | 680.711 s | $0.0405 |
| **Total** | **116/160** | **2,332.283 s** | **$0.1181** |

Failures:

- `quoted-tokenizer` split adjacent quoted/unquoted segments, doubled a
  trailing escape, and accepted an unterminated quote.
- `stable-toposort` made the same declared-key-first ordering error.
- `react-offline-sync` represented repeated warehouse and unknown URL values
  through a private symbol and parsed the required parameter incorrectly.
- `java-idempotency` did not implement least-recently-completed eviction and
  returned results without the required strong ETag.
- `godot-save-pipeline` cleared current dirty state after a failed completion
  and left migrated JSON values in incompatible `JsonElement` form.
- `cpp-memory-bus` reported the wrong precise fault address for mixed
  RAM/MMIO access.
- `rust-wal-queue` compaction changed queue order, allowing pending work to be
  claimed before an expired leased item.
- `click-context-provenance` returned a mutable dictionary copy. It protected
  internal state but did not satisfy the immutable snapshot contract used by
  the property and decorator.

Quality: this was the fastest and cheapest run. Patches were focused and
usually smaller than MiMo's, with sensible use of futures and helper state.
Several shortcuts were brittle, especially the private-symbol URL metadata,
mutable Click snapshot, and repeated C++ translation work. Syntax score:
**7.5/10**.

## Qwen3.6 Plus

| Task | Score | Time | Cost |
|---|---:|---:|---:|
| lru-update | 10/10 | 65.417 s | $0.0191 |
| config-precedence | 10/10 | 58.296 s | $0.0121 |
| rate-window | 10/10 | 47.280 s | $0.0147 |
| quoted-tokenizer | 0/10 | 117.273 s | $0.0424 |
| schema-migration | 10/10 | 83.924 s | $0.0144 |
| csv-unicode | 10/10 | 30.288 s | $0.0110 |
| stable-toposort | 0/10 | 69.852 s | $0.0194 |
| async-retry | 0/10 | 116.712 s | $0.0167 |
| dst-recurrence | 10/10 | 132.140 s | $0.0225 |
| webdav-endpoint | 10/10 | 228.700 s | $0.0407 |
| react-offline-sync | 6/10 | 469.213 s | $0.1046 |
| java-idempotency | 6/10 | 720.662 s | $0.0908 |
| godot-save-pipeline | 8/10 | 103.475 s | $0.0295 |
| cpp-memory-bus | 8/10 | 1,121.073 s | $0.1465 |
| rust-wal-queue | 8/10 | 407.551 s | $0.0959 |
| click-context-provenance | 10/10 | 896.556 s | $0.2886 |
| **Total** | **116/160** | **4,668.412 s** | **$0.9689** |

Failures:

- `quoted-tokenizer` lost empty quoted tokens and doubled a trailing escape.
- `stable-toposort` made the same dependency-only ordering mistake.
- `async-retry` did not reject zero attempts up front and eventually tried to
  raise `None`.
- `react-offline-sync` mutated the caller's initial array and collapsed
  repeated URL parameters into a single-value object.
- `java-idempotency` missed least-recently-completed eviction and never
  generated the required ETag.
- `godot-save-pipeline` correctly rejected future versions but threw
  `InvalidOperationException` instead of the public contract's
  `InvalidDataException`.
- `cpp-memory-bus` used a reusable region classifier but still reported the
  wrong byte address for mixed RAM/MMIO faults.
- `rust-wal-queue` changed claim ordering during compaction, returning pending
  work before an expired leased item.

Quality: the Click patch is concise and fully correct, and the C++ region
helper is the best reuse among these three implementations. Naming and control
flow are consistently clear. The main deductions are large Rust/C++ patches
and several assumptions that were tidy in code but wrong at API boundaries.
Syntax score: **8.0/10**.

## Grading correction

React and Godot were regraded from the original retained workspaces after the
grader was updated to ignore generated Vite cache directories and clear
sandbox-owned .NET `bin` and `obj` output. Original patches, model usage, and
agent times were unchanged.
