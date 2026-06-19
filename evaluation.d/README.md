# Evaluations

This directory contains reviewed summaries derived from local JSONL result
files. Raw results remain untracked because they include full agent output and
machine-specific paths.

## Summary

Wasted tokens are estimated provider token volume for tasks that failed
grading. Failed tasks with no usage response use the median completed compact
task for that model. Kimi K2.7 also includes two abandoned sessions. These
figures estimate unsuccessful inference volume, not exact billing.

| Model and route | Score | Price | Estimated wasted tokens |
|---|---:|---:|---:|
| GLM-5.2, ZCode desktop | 9/11 | Not recorded | Not recorded |
| GLM-5.2, OpenCode Go | 9/11 | $2.44 | 520,304 |
| GPT-5.5 high, Codex CLI | 9/11 | Not recorded | 122,856 |
| Kimi K2.7 Code, OpenCode Go | 8/11 | $1.06 before final two tasks | ~1,051,450 |
| Kimi K2.6, OpenCode Go | 7/11 | $2.19 | 419,400 |
| MiniMax M3, OpenCode Go | 9/11 | $0.30 | 289,762 |
| DeepSeek V4 Pro, OpenCode Go | 8/11 | $1.22 | 477,436 |
| MiMo V2.5 Pro, OpenCode Go | 6/11 | $1.17 | ~976,047 |
| Qwen3.7 Max, OpenCode Go | 9/11 | $2.57 | 179,269 |
| Qwen3.7 Plus, OpenCode Go | 9/11 | $0.39 | 179,142 |

Evaluations:

- [2026-06-19: OpenCode Go model comparison](2026-06-19-opencode-go-models.md)
- [2026-06-18: GLM-5.2 routes and GPT-5.5 high](2026-06-18-glm-5.2-gpt-5.5.md)
- [2026-06-19: Kimi K2.7 Code](2026-06-19-kimi-k2.7-code.md)
