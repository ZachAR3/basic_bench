# Evaluations

This directory contains reviewed summaries derived from local JSONL result
files. Raw results remain untracked because they include full agent output and
machine-specific paths.

## Summary

OpenCode Go prices are calculated from retained per-request usage using
uncached input, output, cache-read, and cache-write rates. Qwen3.7 Plus applies
its higher context tier per request when applicable. They exclude discarded
logs and unanswered stalled requests.

Wasted tokens are provider-reported tokens from completed requests associated
with tasks that failed grading. Silent stalled requests and no-output timeouts
count as zero because no usage was returned.

| Model and route | Score | Price | Estimated wasted tokens |
|---|---:|---:|---:|
| GLM-5.2, ZCode desktop | 9/11 | Not recorded | Not recorded |
| GLM-5.2, OpenCode Go | 9/11 | $2.44 | 520,304 |
| GPT-5.5 high, Codex CLI | 9/11 | Not recorded | 122,856 |
| Kimi K2.7 Code, OpenCode Go | 8/11 | $1.52 calculated | 559,450 |
| Kimi K2.6, OpenCode Go | 7/11 | $0.73 calculated | 419,400 |
| MiniMax M3, OpenCode Go | 9/11 | $0.23 calculated | 289,762 |
| DeepSeek V4 Pro, OpenCode Go | 8/11 | $0.83 calculated | 477,436 |
| MiMo V2.5 Pro, OpenCode Go | 6/11 | $0.57 calculated | 778,759 |
| Qwen3.7 Max, OpenCode Go | 9/11 | $2.39 calculated | 179,269 |
| Qwen3.7 Plus, OpenCode Go | 9/11 | $0.35 calculated | 179,142 |

Evaluations:

- [2026-06-19: OpenCode Go model comparison](2026-06-19-opencode-go-models.md)
- [2026-06-18: GLM-5.2 routes and GPT-5.5 high](2026-06-18-glm-5.2-gpt-5.5.md)
- [2026-06-19: Kimi K2.7 Code](2026-06-19-kimi-k2.7-code.md)
