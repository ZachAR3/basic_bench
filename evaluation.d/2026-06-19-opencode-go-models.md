# OpenCode Go model comparison

Date: 2026-06-19

Seven models were run through OpenCode Go. Each task used a fresh
workspace, one scored attempt, held-out grading, and no visible tests on the
four private compact tasks or the repository-scale task.

## Scores

| Model | Passed | Pass rate | Time | Continuations | Agent errors |
|---|---:|---:|---:|---:|---:|
| MiniMax M3 | 9/11 | 81.8% | 1,835.751 s | 1 | 0 |
| Qwen3.7 Max | 9/11 | 81.8% | 1,796.132 s | 1 | 0 |
| Qwen3.7 Plus | 9/11 | 81.8% | 1,660.330 s | 0 | 0 |
| Kimi K2.7 Code | 8/11 | 72.7% | 1,922.853 s | 0 on scored tasks | 0 on scored tasks |
| DeepSeek V4 Pro | 8/11 | 72.7% | 2,124.103 s | 0 | 0 |
| Kimi K2.6 | 7/11 | 63.6% | 3,080.222 s | 3 | 3 |
| MiMo V2.5 Pro | 6/11 | 54.5% | 6,662.910 s | 1 | 2 timeouts |

MiniMax M3, Qwen3.7 Max, and Qwen3.7 Plus tied the existing best pass rate.
All except Kimi K2.6 passed the repository-scale Click task.

## Cost and unsuccessful token volume

Costs are calculated from retained per-request usage with OpenCode Go's
uncached-input, output, cache-read, and cache-write rates. Qwen3.7 Plus applies
its higher context tier per request when applicable. Wasted tokens are
provider-reported tokens from completed requests on tasks that failed grading.
Silent stalled requests and no-output timeouts count as zero.

| Model | Price | Estimated wasted tokens |
|---|---:|---:|
| Kimi K2.7 Code | $1.5153 | 559,450 |
| Kimi K2.6 | $0.7293 | 419,400 |
| MiniMax M3 | $0.2257 | 289,762 |
| DeepSeek V4 Pro | $0.8330 | 477,436 |
| MiMo V2.5 Pro | $0.5689 | 778,759 |
| Qwen3.7 Max | $2.3945 | 179,269 |
| Qwen3.7 Plus | $0.3532 | 179,142 |

## Task times

Times are agent wall-clock seconds and include any continuation attempts.

| Task | Kimi K2.7 | Kimi K2.6 | MiniMax M3 | DeepSeek V4 Pro | MiMo V2.5 Pro | Qwen3.7 Max | Qwen3.7 Plus |
|---|---:|---:|---:|---:|---:|---:|---:|
| lru-update | 49.974 | 104.452 | 60.696 | 99.873 | 1,800.050 | 51.312 | 62.775 |
| config-precedence | 30.433 | 50.893 | 18.454 | 56.874 | 1,800.043 | 46.339 | 38.435 |
| rate-window | 30.655 | 320.939 | 35.819 | 87.889 | 1,084.739 | 47.025 | 35.820 |
| quoted-tokenizer | 286.618 | 474.589 | 111.256 | 243.971 | 356.517 | 82.098 | 129.414 |
| schema-migration | 82.304 | 247.820 | 66.729 | 99.724 | 71.733 | 49.934 | 47.890 |
| csv-unicode | 43.507 | 76.405 | 42.358 | 47.895 | 33.873 | 39.189 | 47.650 |
| stable-toposort | 125.716 | 193.461 | 79.677 | 193.893 | 95.206 | 62.923 | 62.368 |
| async-retry | 53.110 | 65.807 | 37.461 | 37.640 | 48.517 | 44.417 | 50.617 |
| dst-recurrence | 130.765 | 718.519 | 63.125 | 94.776 | 148.846 | 98.624 | 58.494 |
| webdav-endpoint | 396.155 | 399.687 | 288.204 | 342.402 | 308.694 | 303.532 | 331.163 |
| click-context-provenance | 693.616 | 427.650 | 1,031.972 | 819.166 | 914.692 | 970.739 | 795.704 |

## Failure analysis

### Kimi K2.7 Code

`quoted-tokenizer` lost an empty quoted token. `schema-migration` copied only
the outer dictionary and left nested values shared with the input.
`stable-toposort` made the shared keys-first ordering choice. The rerun of its
two previously missing tasks passed both.

### Kimi K2.6

`rate-window` and `click-context-provenance` ended with provider HTTP 400
errors after continuation because the resumed Moonshot conversation contained
an empty assistant message. Neither task produced an implementation patch.

`quoted-tokenizer` changed an unrelated `debug.py` file and left the tokenizer
unable to preserve empty quoted tokens or reject unterminated quotes.
`stable-toposort` passed six of seven held-out tests but ordered declared graph
keys before an earlier dependency-only node.

### MiniMax M3

`quoted-tokenizer` lost an empty quoted token and mishandled a trailing escaped
backslash. `stable-toposort` made the shared keys-first ordering choice. The
large-task stream stalled once, resumed in the same session, and passed.

### DeepSeek V4 Pro

`rate-window` produced a correct implementation but also edited the provided
visible test file. The integrity grader rejected the task even though all
behavioral tests passed. This is the only test-tampering violation in the
comparison.

`quoted-tokenizer` lost empty quoted tokens and preserved slashes for unknown
escapes. `schema-migration` copied only the outer dictionary, leaving nested
values shared with the input.

### MiMo V2.5 Pro

`lru-update` and `config-precedence` reached the 1,800-second limit without
changing a file. `quoted-tokenizer` lost an empty quoted token, and
`stable-toposort` made the shared keys-first ordering choice.

`webdav-endpoint` failed to reject one encoded traversal form and did not apply
IDNA normalization to a Unicode hostname. The large task stalled once,
continued in the same session, and passed.

### Qwen3.7 Max and Qwen3.7 Plus

Both models failed the same two edge cases: the tokenizer lost an empty quoted
token and mishandled a trailing escaped backslash, while the topological sorter
placed a declared key before an earlier dependency-only node. Qwen3.7 Max
needed one continuation on the large task; Qwen3.7 Plus completed without one.

## Code quality

The repository-scale passing patches changed 41 lines for MiMo V2.5 Pro, 47
for DeepSeek V4 Pro, 93 for Qwen3.7 Max, 120 for Kimi K2.7 Code, 124 for
MiniMax M3, and 147 for Qwen3.7 Plus. DeepSeek produced the smallest clean
passing implementation.
MiMo was slightly smaller but added a temporary test file to the workspace.

Across the compact suite, the passing changes were usually confined to one
implementation file. DeepSeek's test edit is a material quality and benchmark
integrity failure. Kimi's off-target tokenizer edit and two provider-aborted
tasks also reduce confidence beyond its raw score.

## Runner stability

During the comparison, OpenCode streams sometimes stopped after a pending tool
call. The harness treats five minutes without output as a stalled provider
call and first resumes the same OpenCode session. If the model reports
`CONTEXT_LOST`, the session is unusable, or the resumed context is silent
again, it starts a fresh session in the same modified workspace. Retryable 429
and 5xx API errors use the same path, and the task timeout covers all attempts
combined.

This recovered the large tasks for MiniMax M3, MiMo V2.5 Pro, and Qwen3.7 Max.
Kimi K2.6 exposed a separate OpenCode/Moonshot session-history error that was
non-retryable.
