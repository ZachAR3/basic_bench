# Individual task results

Each table shows functional points, wall-clock time, calculated task cost when available, and the subjective syntax review.

Syntax is reviewer-biased and separate from functional grading. It uses one rubric for every run: clarity, focus, reuse, and maintainability. `N/A` means the agent submitted no implementation patch, so there was no model-authored code to judge.

## GLM-5.2 desktop — ZCode desktop

Run ID: `glm52-test1-manual`
Aggregate: 90/110 points; syntax 8.5/10 across 11/11 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | — | — | 9.0/10 |
| `config-precedence` | PASS | 10/10 | — | — | 9.5/10 |
| `rate-window` | PASS | 10/10 | — | — | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | — | — | 9.5/10 |
| `schema-migration` | PASS | 10/10 | — | — | 8.0/10 |
| `csv-unicode` | PASS | 10/10 | — | — | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | — | — | 8.0/10 |
| `async-retry` | PASS | 10/10 | — | — | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | — | — | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | — | — | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | — | — | 7.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 15 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 6 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 8.0/10: Clear and reasonably focused. 49 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 18 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 69 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 29 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 60 changed lines across 1 file.
- `click-context-provenance` — 7.0/10: Readable, with some duplication or expansion. 206 changed lines across 2 files.

</details>

## GLM-5.2 Z Code CLI — Z Code CLI

Run ID: `glm52-test1-go`
Aggregate: 112/160 points; syntax 8.1/10 across 14/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 53.301 s | $0.0480 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 43.298 s | $0.0399 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 35.032 s | $0.0356 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 269.472 s | $0.1831 | 9.0/10 |
| `schema-migration` | PASS | 10/10 | 70.969 s | $0.0617 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 43.638 s | $0.0346 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 172.398 s | $0.1226 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 57.362 s | $0.0525 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 184.242 s | $0.0972 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 900.040 s | — | 6.0/10 |
| `click-context-provenance` | PASS | 10/10 | 668.739 s | $1.2357 | 7.0/10 |
| `react-offline-sync` | FAIL | 8/10 | 813.239 s | $0.5790 | 6.5/10 |
| `java-idempotency` | FAIL | 6/10 | 621.280 s | $0.3099 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 6/10 | 983.989 s | $0.4770 | 7.5/10 |
| `cpp-memory-bus` | FAIL | 2/10 | 545.412 s | $0.1665 | N/A |
| `rust-wal-queue` | FAIL | 0/10 | 574.103 s | $0.1799 | N/A |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 6 changed lines across 1 file.
- `quoted-tokenizer` — 9.0/10: Very focused and concise. 10 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 31 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 18 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 70 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 31 changed lines across 1 file.
- `webdav-endpoint` — 6.0/10: Understandable but verbose or difficult to audit. 110 changed lines across 1 file. The submitted patch was incomplete when the agent exited.
- `click-context-provenance` — 7.0/10: Readable, with some duplication or expansion. 125 changed lines across 3 files. Included an unnecessary report or changelog edit.
- `react-offline-sync` — 6.5/10: Understandable but verbose or difficult to audit. 235 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 207 changed lines across 1 file.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 84 changed lines across 2 files.
- `cpp-memory-bus` — N/A: No implementation patch to review.
- `rust-wal-queue` — N/A: No implementation patch to review.

</details>

## GLM-5.2 — OpenCode Go

Run ID: `glm-5.2-opencode-go`
Aggregate: 114/160 points; syntax 8.2/10 across 14/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 49.681 s | $0.0561 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 28.921 s | $0.0404 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 26.038 s | $0.0457 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 99.768 s | $0.1046 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 51.339 s | $0.0446 | 8.0/10 |
| `csv-unicode` | PASS | 10/10 | 23.097 s | $0.0449 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 75.245 s | $0.0582 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 88.559 s | $0.0798 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 74.190 s | $0.0879 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 286.174 s | $0.2584 | 7.5/10 |
| `react-offline-sync` | FAIL | 2/10 | 380.407 s | $0.0359 | N/A |
| `java-idempotency` | FAIL | 6/10 | 604.501 s | $0.4071 | 6.5/10 |
| `godot-save-pipeline` | FAIL | 6/10 | 369.189 s | $0.4735 | 7.5/10 |
| `cpp-memory-bus` | PASS | 10/10 | 1006.611 s | $0.4420 | 7.0/10 |
| `rust-wal-queue` | FAIL | 0/10 | 453.156 s | $0.0497 | N/A |
| `click-context-provenance` | PASS | 10/10 | 449.554 s | $1.4604 | 7.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 10 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `schema-migration` — 8.0/10: Clear and reasonably focused. 37 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 55 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 22 changed lines across 1 file.
- `webdav-endpoint` — 7.5/10: Readable, with some duplication or expansion. 87 changed lines across 1 file.
- `react-offline-sync` — N/A: No implementation patch to review.
- `java-idempotency` — 6.5/10: Understandable but verbose or difficult to audit. 231 changed lines across 1 file.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 129 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 194 changed lines across 1 file.
- `rust-wal-queue` — N/A: No implementation patch to review.
- `click-context-provenance` — 7.0/10: Readable, with some duplication or expansion. 153 changed lines across 2 files.

</details>

## GPT-5.5 high — Codex CLI

Run ID: `codex-gpt-5.5-high`
Aggregate: 130/160 points; syntax 8.1/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 42.301 s | — | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 43.936 s | — | 9.5/10 |
| `rate-window` | PASS | 10/10 | 42.829 s | — | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 57.022 s | — | 9.0/10 |
| `schema-migration` | PASS | 10/10 | 65.348 s | — | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 63.173 s | — | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 68.834 s | — | 8.0/10 |
| `async-retry` | PASS | 10/10 | 63.039 s | — | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 99.378 s | — | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 224.747 s | — | 7.5/10 |
| `click-context-provenance` | PASS | 10/10 | 174.532 s | — | 8.0/10 |
| `react-offline-sync` | FAIL | 8/10 | 160.905 s | — | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 233.706 s | — | 7.0/10 |
| `godot-save-pipeline` | FAIL | 8/10 | 106.022 s | — | 7.5/10 |
| `cpp-memory-bus` | PASS | 10/10 | 149.297 s | — | 7.0/10 |
| `rust-wal-queue` | FAIL | 8/10 | 299.370 s | — | 6.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 6 changed lines across 1 file.
- `quoted-tokenizer` — 9.0/10: Very focused and concise. 14 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 18 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 18 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 56 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 14 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 25 changed lines across 1 file.
- `webdav-endpoint` — 7.5/10: Readable, with some duplication or expansion. 99 changed lines across 1 file.
- `click-context-provenance` — 8.0/10: Clear and reasonably focused. 47 changed lines across 2 files.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 186 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 198 changed lines across 2 files.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 122 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 155 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 618 changed lines across 1 file.

</details>

## GPT-5.5 xhigh targeted — Codex CLI

Run ID: `codex-gpt-5.5-xhigh-failures`
Aggregate: 0/20 points; syntax 8.2/10 across 2/2 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `quoted-tokenizer` | FAIL | 0/10 | 86.215 s | — | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 116.043 s | — | 8.0/10 |

<details>
<summary>Syntax review notes</summary>

- `quoted-tokenizer` — 8.5/10: Clear and reasonably focused. 31 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 56 changed lines across 1 file.

</details>

## Kimi K2.7 Code — OpenCode Go

Run ID: `kimi-k2.7-code-opencode-go`
Aggregate: 124/160 points; syntax 8.0/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 49.974 s | $0.0223 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 30.433 s | $0.0181 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 30.655 s | $0.0172 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 286.618 s | $0.1245 | 9.5/10 |
| `schema-migration` | FAIL | 0/10 | 82.304 s | $0.0331 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 43.507 s | $0.0255 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 125.716 s | $0.0621 | 7.5/10 |
| `async-retry` | PASS | 10/10 | 53.110 s | $0.0201 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 130.765 s | $0.0687 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 396.155 s | $0.2499 | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | 693.616 s | $0.8738 | 7.5/10 |
| `react-offline-sync` | FAIL | 8/10 | 491.398 s | $0.4229 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 638.305 s | $0.4949 | 6.5/10 |
| `godot-save-pipeline` | PASS | 10/10 | 219.406 s | $0.1227 | 7.0/10 |
| `cpp-memory-bus` | PASS | 10/10 | 1475.816 s | $0.5180 | 7.0/10 |
| `rust-wal-queue` | PASS | 10/10 | 727.075 s | $0.5690 | 6.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 15 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 18 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 7.5/10: Readable, with some duplication or expansion. 82 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 28 changed lines across 2 files.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 42 changed lines across 1 file.
- `click-context-provenance` — 7.5/10: Readable, with some duplication or expansion. 120 changed lines across 2 files.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 198 changed lines across 3 files.
- `java-idempotency` — 6.5/10: Understandable but verbose or difficult to audit. 223 changed lines across 1 file.
- `godot-save-pipeline` — 7.0/10: Readable, with some duplication or expansion. 152 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 213 changed lines across 1 file.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 643 changed lines across 2 files.

</details>

## Kimi K2.6 — OpenCode Go

Run ID: `kimi-k2.6-opencode-go`
Aggregate: 94/160 points; syntax 7.2/10 across 13/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 104.452 s | $0.0374 | 8.5/10 |
| `config-precedence` | PASS | 10/10 | 50.893 s | $0.0296 | 9.5/10 |
| `rate-window` | FAIL | 0/10 | 320.939 s | $0.0055 | N/A |
| `quoted-tokenizer` | FAIL | 0/10 | 474.589 s | $0.0933 | 1.5/10 |
| `schema-migration` | PASS | 10/10 | 247.820 s | $0.0687 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 76.405 s | $0.0208 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 193.461 s | $0.0617 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 65.807 s | $0.0377 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 718.519 s | $0.1047 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 399.687 s | $0.2101 | 8.0/10 |
| `click-context-provenance` | FAIL | 0/10 | 427.650 s | $0.0597 | N/A |
| `react-offline-sync` | FAIL | 6/10 | 2234.993 s | $0.3701 | 7.0/10 |
| `java-idempotency` | FAIL | 0/10 | 348.088 s | $0.0740 | N/A |
| `godot-save-pipeline` | FAIL | 8/10 | 1083.199 s | $0.2751 | 7.5/10 |
| `cpp-memory-bus` | PASS | 10/10 | 1233.488 s | $0.4125 | 7.0/10 |
| `rust-wal-queue` | FAIL | 0/10 | 2375.687 s | $0.1155 | 1.5/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 8.5/10: Clear and reasonably focused. 16 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `rate-window` — N/A: No implementation patch to review.
- `quoted-tokenizer` — 1.5/10: Patch changed only generated, diagnostic, or summary files.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 54 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 42 changed lines across 1 file.
- `click-context-provenance` — N/A: No implementation patch to review.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 185 changed lines across 3 files.
- `java-idempotency` — N/A: No implementation patch to review.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 93 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 206 changed lines across 1 file.
- `rust-wal-queue` — 1.5/10: Patch changed only generated, diagnostic, or summary files.

</details>

## MiniMax M3 — OpenCode Go

Run ID: `minimax-m3-opencode-go`
Aggregate: 114/160 points; syntax 8.4/10 across 14/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 60.696 s | $0.0048 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 18.454 s | $0.0019 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 35.819 s | $0.0023 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 111.256 s | $0.0071 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 66.729 s | $0.0039 | 9.0/10 |
| `csv-unicode` | PASS | 10/10 | 42.358 s | $0.0027 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 79.677 s | $0.0048 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 37.461 s | $0.0027 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 63.125 s | $0.0051 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 288.204 s | $0.0235 | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | 1031.972 s | $0.1668 | 7.5/10 |
| `react-offline-sync` | FAIL | 8/10 | 1588.011 s | $0.0421 | 6.5/10 |
| `java-idempotency` | FAIL | 0/10 | 1056.740 s | $0.0035 | N/A |
| `godot-save-pipeline` | FAIL | 8/10 | 353.193 s | $0.0256 | 8.0/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 726.030 s | $0.0486 | 7.0/10 |
| `rust-wal-queue` | FAIL | 0/10 | 314.191 s | $0.0155 | N/A |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 9.0/10: Very focused and concise. 11 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 49 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 22 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 39 changed lines across 1 file.
- `click-context-provenance` — 7.5/10: Readable, with some duplication or expansion. 124 changed lines across 2 files.
- `react-offline-sync` — 6.5/10: Understandable but verbose or difficult to audit. 234 changed lines across 3 files.
- `java-idempotency` — N/A: No implementation patch to review.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 65 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 204 changed lines across 1 file.
- `rust-wal-queue` — N/A: No implementation patch to review.

</details>

## DeepSeek V4 Pro — OpenCode Go

Run ID: `deepseek-v4-pro-opencode-go`
Aggregate: 116/160 points; syntax 7.7/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 99.873 s | $0.0412 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 56.874 s | $0.0214 | 9.5/10 |
| `rate-window` | FAIL | 0/10 | 87.889 s | $0.0337 | 1.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 243.971 s | $0.0954 | 9.5/10 |
| `schema-migration` | FAIL | 0/10 | 99.724 s | $0.0364 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 47.895 s | $0.0259 | 8.5/10 |
| `stable-toposort` | PASS | 10/10 | 193.893 s | $0.0773 | 8.5/10 |
| `async-retry` | PASS | 10/10 | 37.640 s | $0.0239 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 94.776 s | $0.0345 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 342.402 s | $0.1365 | 7.5/10 |
| `click-context-provenance` | PASS | 10/10 | 819.166 s | $0.3067 | 8.0/10 |
| `react-offline-sync` | FAIL | 6/10 | 166.367 s | $0.0876 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 206.919 s | $0.1129 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 6/10 | 101.952 s | $0.0577 | 8.0/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 161.848 s | $0.1082 | 7.0/10 |
| `rust-wal-queue` | PASS | 10/10 | 280.799 s | $0.1457 | 6.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 15 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 1.0/10: Patch violated benchmark integrity; code quality is not trusted.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 22 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.5/10: Clear and reasonably focused. 31 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `webdav-endpoint` — 7.5/10: Readable, with some duplication or expansion. 92 changed lines across 1 file.
- `click-context-provenance` — 8.0/10: Clear and reasonably focused. 47 changed lines across 2 files.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 132 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 172 changed lines across 1 file.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 69 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 162 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 815 changed lines across 2 files.

</details>

## MiMo V2.5 Pro — OpenCode Go

Run ID: `mimo-v2.5-pro-opencode-go`
Aggregate: 90/160 points; syntax 8.2/10 across 13/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | FAIL | 0/10 | 1800.050 s | — | N/A |
| `config-precedence` | FAIL | 0/10 | 1800.043 s | — | N/A |
| `rate-window` | PASS | 10/10 | 1084.739 s | $0.0229 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 356.517 s | $0.1046 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 71.733 s | $0.0274 | 9.0/10 |
| `csv-unicode` | PASS | 10/10 | 33.873 s | $0.0197 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 95.206 s | $0.0288 | 7.5/10 |
| `async-retry` | PASS | 10/10 | 48.517 s | $0.0253 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 148.846 s | $0.0440 | 8.5/10 |
| `webdav-endpoint` | FAIL | 0/10 | 308.694 s | $0.0960 | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | 914.692 s | $0.2001 | 8.0/10 |
| `react-offline-sync` | FAIL | 6/10 | 360.915 s | $0.1485 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 87.332 s | $0.0501 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 8/10 | 156.425 s | $0.0673 | 8.0/10 |
| `cpp-memory-bus` | PASS | 10/10 | 1045.615 s | $0.3703 | 7.0/10 |
| `rust-wal-queue` | FAIL | 0/10 | 560.193 s | $0.0397 | N/A |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — N/A: No implementation patch to review.
- `config-precedence` — N/A: No implementation patch to review.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 9.0/10: Very focused and concise. 12 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 7.5/10: Readable, with some duplication or expansion. 73 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 39 changed lines across 1 file.
- `click-context-provenance` — 8.0/10: Clear and reasonably focused. 41 changed lines across 2 files.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 138 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 165 changed lines across 1 file.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 61 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 161 changed lines across 1 file.
- `rust-wal-queue` — N/A: No implementation patch to review.

</details>

## Qwen3.7 Max — OpenCode Go

Run ID: `qwen3.7-max-opencode-go`
Aggregate: 114/160 points; syntax 8.4/10 across 14/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 51.312 s | $0.0835 | 8.5/10 |
| `config-precedence` | PASS | 10/10 | 46.339 s | $0.0705 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 47.025 s | $0.0678 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 82.098 s | $0.0921 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 49.934 s | $0.0643 | 9.0/10 |
| `csv-unicode` | PASS | 10/10 | 39.189 s | $0.0654 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 62.923 s | $0.0934 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 44.417 s | $0.0584 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 98.624 s | $0.1086 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 303.532 s | $0.3056 | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | 970.739 s | $1.3851 | 7.5/10 |
| `react-offline-sync` | FAIL | 8/10 | 228.915 s | $0.2658 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 367.606 s | $0.3485 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 8/10 | 172.070 s | $0.1840 | 8.0/10 |
| `cpp-memory-bus` | FAIL | 2/10 | 238.551 s | $0.0349 | N/A |
| `rust-wal-queue` | FAIL | 0/10 | 266.647 s | $0.0369 | N/A |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 8.5/10: Clear and reasonably focused. 16 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 9.0/10: Very focused and concise. 11 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 52 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 20 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 41 changed lines across 1 file.
- `click-context-provenance` — 7.5/10: Readable, with some duplication or expansion. 93 changed lines across 2 files.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 163 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 137 changed lines across 2 files.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 51 changed lines across 2 files.
- `cpp-memory-bus` — N/A: No implementation patch to review.
- `rust-wal-queue` — N/A: No implementation patch to review.

</details>

## Qwen3.7 Plus — OpenCode Go

Run ID: `qwen3.7-plus-opencode-go`
Aggregate: 130/160 points; syntax 8.0/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 62.775 s | $0.0114 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 38.435 s | $0.0088 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 35.820 s | $0.0083 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 129.414 s | $0.0191 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 47.890 s | $0.0095 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 47.650 s | $0.0089 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 62.368 s | $0.0108 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 50.617 s | $0.0091 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 58.494 s | $0.0130 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 331.163 s | $0.0515 | 8.0/10 |
| `click-context-provenance` | PASS | 10/10 | 795.704 s | $0.2028 | 6.5/10 |
| `react-offline-sync` | FAIL | 8/10 | 447.583 s | $0.0701 | 6.5/10 |
| `java-idempotency` | FAIL | 6/10 | 661.552 s | $0.0488 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 8/10 | 240.753 s | $0.0369 | 8.0/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 443.011 s | $0.0666 | 7.0/10 |
| `rust-wal-queue` | PASS | 10/10 | 579.535 s | $0.0886 | 6.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 15 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 6 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 28 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 46 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 23 changed lines across 1 file.
- `webdav-endpoint` — 8.0/10: Clear and reasonably focused. 51 changed lines across 1 file.
- `click-context-provenance` — 6.5/10: Understandable but verbose or difficult to audit. 147 changed lines across 3 files. Included an unnecessary report or changelog edit.
- `react-offline-sync` — 6.5/10: Understandable but verbose or difficult to audit. 222 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 178 changed lines across 1 file.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 60 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 172 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 407 changed lines across 2 files.

</details>

## MiMo V2.5 — OpenCode Go

Run ID: `mimo-v2.5-opencode-go`
Aggregate: 116/160 points; syntax 8.1/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 33.117 s | $0.0022 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 57.399 s | $0.0019 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 35.893 s | $0.0021 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 105.771 s | $0.0048 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 73.729 s | $0.0026 | 8.5/10 |
| `csv-unicode` | PASS | 10/10 | 40.325 s | $0.0017 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 51.085 s | $0.0028 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 51.639 s | $0.0022 | 9.0/10 |
| `dst-recurrence` | FAIL | 0/10 | 41.747 s | $0.0027 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 439.469 s | $0.0171 | 7.5/10 |
| `react-offline-sync` | FAIL | 6/10 | 233.992 s | $0.0090 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 691.890 s | $0.0171 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 6/10 | 114.809 s | $0.0064 | 7.5/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 213.596 s | $0.0103 | 7.0/10 |
| `rust-wal-queue` | PASS | 10/10 | 582.439 s | $0.0189 | 6.0/10 |
| `click-context-provenance` | PASS | 10/10 | 607.295 s | $0.0441 | 8.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 15 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 19 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 54 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 22 changed lines across 1 file.
- `webdav-endpoint` — 7.5/10: Readable, with some duplication or expansion. 112 changed lines across 1 file.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 191 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 198 changed lines across 2 files.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 72 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 194 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 471 changed lines across 2 files.
- `click-context-provenance` — 8.0/10: Clear and reasonably focused. 49 changed lines across 2 files.

</details>

## DeepSeek V4 Flash — OpenCode Go

Run ID: `deepseek-v4-flash-opencode-go`
Aggregate: 116/160 points; syntax 8.2/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 22.672 s | $0.0018 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 26.866 s | $0.0028 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 30.211 s | $0.0020 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 244.060 s | $0.0102 | 9.0/10 |
| `schema-migration` | PASS | 10/10 | 82.336 s | $0.0032 | 9.0/10 |
| `csv-unicode` | PASS | 10/10 | 37.809 s | $0.0018 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 76.374 s | $0.0038 | 8.0/10 |
| `async-retry` | PASS | 10/10 | 31.100 s | $0.0022 | 9.0/10 |
| `dst-recurrence` | PASS | 10/10 | 48.582 s | $0.0029 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 116.884 s | $0.0044 | 8.5/10 |
| `react-offline-sync` | FAIL | 8/10 | 199.275 s | $0.0084 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 194.101 s | $0.0076 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 6/10 | 74.195 s | $0.0045 | 8.0/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 165.949 s | $0.0090 | 7.0/10 |
| `rust-wal-queue` | FAIL | 8/10 | 301.158 s | $0.0130 | 6.0/10 |
| `click-context-provenance` | FAIL | 0/10 | 680.711 s | $0.0405 | 8.0/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 6 changed lines across 1 file.
- `quoted-tokenizer` — 9.0/10: Very focused and concise. 9 changed lines across 1 file.
- `schema-migration` — 9.0/10: Very focused and concise. 13 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 52 changed lines across 1 file.
- `async-retry` — 9.0/10: Very focused and concise. 7 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 21 changed lines across 1 file.
- `webdav-endpoint` — 8.5/10: Clear and reasonably focused. 32 changed lines across 1 file.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 175 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 164 changed lines across 1 file.
- `godot-save-pipeline` — 8.0/10: Clear and reasonably focused. 59 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 161 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 414 changed lines across 2 files.
- `click-context-provenance` — 8.0/10: Clear and reasonably focused. 40 changed lines across 2 files.

</details>

## Qwen3.6 Plus — OpenCode Go

Run ID: `qwen3.6-plus-opencode-go`
Aggregate: 116/160 points; syntax 8.2/10 across 16/16 patches.

| Task | Result | Points | Time | Cost | Syntax |
|---|---:|---:|---:|---:|---:|
| `lru-update` | PASS | 10/10 | 65.417 s | $0.0191 | 9.0/10 |
| `config-precedence` | PASS | 10/10 | 58.296 s | $0.0121 | 9.5/10 |
| `rate-window` | PASS | 10/10 | 47.280 s | $0.0147 | 9.0/10 |
| `quoted-tokenizer` | FAIL | 0/10 | 117.273 s | $0.0424 | 9.5/10 |
| `schema-migration` | PASS | 10/10 | 83.924 s | $0.0144 | 9.0/10 |
| `csv-unicode` | PASS | 10/10 | 30.288 s | $0.0110 | 8.5/10 |
| `stable-toposort` | FAIL | 0/10 | 69.852 s | $0.0194 | 8.0/10 |
| `async-retry` | FAIL | 0/10 | 116.712 s | $0.0167 | 9.5/10 |
| `dst-recurrence` | PASS | 10/10 | 132.140 s | $0.0225 | 8.5/10 |
| `webdav-endpoint` | PASS | 10/10 | 228.700 s | $0.0407 | 8.5/10 |
| `react-offline-sync` | FAIL | 6/10 | 469.213 s | $0.1046 | 7.0/10 |
| `java-idempotency` | FAIL | 6/10 | 720.662 s | $0.0908 | 7.0/10 |
| `godot-save-pipeline` | FAIL | 8/10 | 103.475 s | $0.0295 | 7.5/10 |
| `cpp-memory-bus` | FAIL | 8/10 | 1121.073 s | $0.1465 | 7.0/10 |
| `rust-wal-queue` | FAIL | 8/10 | 407.551 s | $0.0959 | 6.0/10 |
| `click-context-provenance` | PASS | 10/10 | 896.556 s | $0.2886 | 8.5/10 |

<details>
<summary>Syntax review notes</summary>

- `lru-update` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `config-precedence` — 9.5/10: Very focused and concise. 2 changed lines across 1 file.
- `rate-window` — 9.0/10: Very focused and concise. 8 changed lines across 1 file.
- `quoted-tokenizer` — 9.5/10: Very focused and concise. 4 changed lines across 1 file.
- `schema-migration` — 9.0/10: Very focused and concise. 13 changed lines across 1 file.
- `csv-unicode` — 8.5/10: Clear and reasonably focused. 17 changed lines across 1 file.
- `stable-toposort` — 8.0/10: Clear and reasonably focused. 45 changed lines across 1 file.
- `async-retry` — 9.5/10: Very focused and concise. 5 changed lines across 1 file.
- `dst-recurrence` — 8.5/10: Clear and reasonably focused. 20 changed lines across 1 file.
- `webdav-endpoint` — 8.5/10: Clear and reasonably focused. 32 changed lines across 1 file.
- `react-offline-sync` — 7.0/10: Readable, with some duplication or expansion. 131 changed lines across 3 files.
- `java-idempotency` — 7.0/10: Readable, with some duplication or expansion. 155 changed lines across 1 file.
- `godot-save-pipeline` — 7.5/10: Readable, with some duplication or expansion. 91 changed lines across 2 files.
- `cpp-memory-bus` — 7.0/10: Readable, with some duplication or expansion. 162 changed lines across 2 files.
- `rust-wal-queue` — 6.0/10: Understandable but verbose or difficult to audit. 453 changed lines across 2 files.
- `click-context-provenance` — 8.5/10: Clear and reasonably focused. 35 changed lines across 2 files.

</details>
