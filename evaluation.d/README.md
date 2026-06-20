# Evaluations

This directory contains reviewed summaries derived from local JSONL result
files. Raw results remain untracked because they include full agent output and
machine-specific paths.

## Complete 16-task runs

OpenCode Go prices are calculated from retained per-request usage using
uncached input, output, cache-read, and cache-write rates. Qwen3.7 Plus applies
its higher context tier per request when applicable. They exclude discarded
logs and unanswered stalled requests.

Wasted tokens are provider-reported tokens from tasks that failed grading,
plus completed requests discarded when a successful task required a fresh
context. Silent stalled requests and no-output timeouts count as zero because
no usage was returned.

| Model and route | Task passes | Points | Price | Unsuccessful or abandoned tokens |
|---|---:|---:|---:|---:|
| GPT-5.5 high, Codex CLI | 10/16 | 130/160 | Not recorded | 877,415 |
| Qwen3.7 Plus, OpenCode Go | 10/16 | 130/160 | $0.6642 calculated | 1,430,643 |
| Kimi K2.7 Code, OpenCode Go | 11/16 | 124/160 | $3.6428 calculated | 3,376,377 |
| DeepSeek V4 Pro, OpenCode Go | 9/16 | 116/160 | $1.3452 calculated | 1,616,167 |
| GLM-5.2, OpenCode Go | 10/16 | 114/160 | $3.6892 calculated | 2,261,616 |
| MiniMax M3, OpenCode Go | 9/16 | 114/160 | $0.3610 calculated | 3,641,410 |
| Qwen3.7 Max, OpenCode Go | 9/16 | 114/160 | $3.2646 calculated | 851,278 |
| GLM-5.2, Z Code CLI | 9/16 | 112/160 | $3.6230 calculated | 3,275,137 |
| Kimi K2.6, OpenCode Go | 8/16 | 94/160 | $1.9765 calculated | 2,040,271 |
| MiMo V2.5 Pro, OpenCode Go | 7/16 | 90/160 | $1.2448 calculated | 1,915,041 |

The manual GLM desktop run remains an 11-task historical result and is not
ranked with complete 16-task runs.

Evaluations:

- [2026-06-19: Multi-language suite extension](2026-06-19-multilanguage-suite.md)
- [2026-06-19: OpenCode Go model comparison](2026-06-19-opencode-go-models.md)
- [2026-06-18: GLM-5.2 routes and GPT-5.5 high](2026-06-18-glm-5.2-gpt-5.5.md)
- [2026-06-19: Kimi K2.7 Code](2026-06-19-kimi-k2.7-code.md)
