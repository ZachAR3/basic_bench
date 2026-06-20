# Evaluations

This directory contains reviewed summaries derived from local JSONL result
files. Raw results remain untracked because they include full agent output and
machine-specific paths.

## Complete 16-task runs

OpenCode Go prices are calculated from retained per-request usage using
uncached input, output, cache-read, and cache-write rates. Models with context
pricing tiers apply them per request when applicable. They exclude discarded
logs and unanswered stalled requests. Published JSON includes the same
calculation for each task.

Wasted tokens are provider-reported tokens from tasks that failed grading,
plus completed requests discarded when a successful task required a fresh
context. Silent stalled requests and no-output timeouts count as zero because
no usage was returned.

| Model and route | Task passes | Points | Price | Unsuccessful or abandoned tokens | Syntax |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 high, Codex CLI | 10/16 | 130/160 | Not recorded | 877,415 | Not reviewed |
| Qwen3.7 Plus, OpenCode Go | 10/16 | 130/160 | $0.6642 calculated | 1,430,643 | Not reviewed |
| Kimi K2.7 Code, OpenCode Go | 11/16 | 124/160 | $3.6428 calculated | 3,376,377 | Not reviewed |
| DeepSeek V4 Pro, OpenCode Go | 9/16 | 116/160 | $1.3452 calculated | 1,616,167 | Not reviewed |
| MiMo V2.5, OpenCode Go | 9/16 | 116/160 | $0.1459 calculated | 1,689,378 | 7.0/10 |
| DeepSeek V4 Flash, OpenCode Go | 8/16 | 116/160 | $0.1181 calculated | 5,928,450 | 7.5/10 |
| Qwen3.6 Plus, OpenCode Go | 8/16 | 116/160 | $0.9689 calculated | 2,295,789 | 8.0/10 |
| GLM-5.2, OpenCode Go | 10/16 | 114/160 | $3.6892 calculated | 2,261,616 | Not reviewed |
| MiniMax M3, OpenCode Go | 9/16 | 114/160 | $0.3610 calculated | 3,641,410 | Not reviewed |
| Qwen3.7 Max, OpenCode Go | 9/16 | 114/160 | $3.2646 calculated | 851,278 | Not reviewed |
| GLM-5.2, Z Code CLI | 9/16 | 112/160 | $3.6230 calculated | 3,275,137 | Not reviewed |
| Kimi K2.6, OpenCode Go | 8/16 | 94/160 | $1.9765 calculated | 2,040,271 | Not reviewed |
| MiMo V2.5 Pro, OpenCode Go | 7/16 | 90/160 | $1.2448 calculated | 1,915,041 | Not reviewed |

Syntax is a subjective, reviewer-biased score for readability, reuse, focus,
and maintainability. It is not produced by held-out tests and should not be
treated as an objective benchmark metric.

The manual GLM desktop run remains an 11-task historical result and is not
ranked with complete 16-task runs.

Evaluations:

- [2026-06-20: MiMo V2.5, DeepSeek V4 Flash, and Qwen3.6 Plus](2026-06-20-opencode-go-models.md)
- [2026-06-19: Multi-language suite extension](2026-06-19-multilanguage-suite.md)
- [2026-06-19: OpenCode Go model comparison](2026-06-19-opencode-go-models.md)
- [2026-06-18: GLM-5.2 routes and GPT-5.5 high](2026-06-18-glm-5.2-gpt-5.5.md)
- [2026-06-19: Kimi K2.7 Code](2026-06-19-kimi-k2.7-code.md)
