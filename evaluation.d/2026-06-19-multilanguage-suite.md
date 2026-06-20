# Multi-language suite extension

Date: 2026-06-19

Five held-out tasks were added for React and Vite, Java 21, Godot GDScript and
C#, C++20 emulator logic, and stable Rust. Each task has five independent
two-point checks. Existing tasks retain strict pass-or-fail scoring, producing
a 160-point suite across sixteen tasks.

All OpenCode Go runs were sequential. Each task used a fresh workspace, no
visible grading tests, no web access, and one scored attempt. Provider recovery
first resumed the same OpenCode session, then used a fresh session in the same
workspace only when the context was unavailable or remained silent.

## Overall results

| Model and route | Task passes | Points | Point rate | Time | Price |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 high, Codex CLI | 10/16 | 130/160 | 81.2% | 1,894 s | Not recorded |
| Qwen3.7 Plus, OpenCode Go | 10/16 | 130/160 | 81.2% | 4,033 s | $0.6642 |
| Kimi K2.7 Code, OpenCode Go | 11/16 | 124/160 | 77.5% | 5,475 s | $3.6428 |
| DeepSeek V4 Pro, OpenCode Go | 9/16 | 116/160 | 72.5% | 3,042 s | $1.3452 |
| GLM-5.2, OpenCode Go | 10/16 | 114/160 | 71.2% | 4,066 s | $3.6892 |
| MiniMax M3, OpenCode Go | 9/16 | 114/160 | 71.2% | 5,874 s | $0.3610 |
| Qwen3.7 Max, OpenCode Go | 9/16 | 114/160 | 71.2% | 3,070 s | $3.2646 |
| Kimi K2.6, OpenCode Go | 8/16 | 94/160 | 58.8% | 10,356 s | $1.9765 |
| MiMo V2.5 Pro, OpenCode Go | 7/16 | 90/160 | 56.2% | 8,873 s | $1.2448 |

Prices are calculated from retained provider usage and the costs reported by
`opencode models opencode-go --verbose`. Unanswered stalled requests have no
reported usage and add no token cost.

Godot scores were regraded from the original retained workspaces after the
grader was fixed to remove sandbox-generated .NET `bin` and `obj` directories.
The original model patches and agent times were unchanged.

## Extension task scores and times

Each cell is `points / seconds`.

| Model | React | Java | Godot | C++ | Rust |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 high | 8 / 161 | 6 / 234 | 8 / 106 | 10 / 149 | 8 / 299 |
| Qwen3.7 Plus | 8 / 448 | 6 / 662 | 8 / 241 | 8 / 443 | 10 / 580 |
| Kimi K2.7 Code | 8 / 491 | 6 / 638 | 10 / 219 | 10 / 1,476 | 10 / 727 |
| DeepSeek V4 Pro | 6 / 166 | 6 / 207 | 6 / 102 | 8 / 162 | 10 / 281 |
| GLM-5.2 | 2 / 380 | 6 / 605 | 6 / 369 | 10 / 1,007 | 0 / 453 |
| MiniMax M3 | 8 / 1,588 | 0 / 1,057 | 8 / 353 | 8 / 726 | 0 / 314 |
| Qwen3.7 Max | 8 / 229 | 6 / 368 | 8 / 172 | 2 / 239 | 0 / 267 |
| Kimi K2.6 | 6 / 2,235 | 0 / 348 | 8 / 1,083 | 10 / 1,233 | 0 / 2,376 |
| MiMo V2.5 Pro | 6 / 361 | 6 / 87 | 8 / 156 | 10 / 1,046 | 0 / 560 |

## Failure analysis

The React URL-state check was the most consistent miss. Seven models failed
deterministic Unicode, repeated-value, empty-state, or unknown-parameter
round-tripping. DeepSeek and MiMo also exposed mutable snapshots; Kimi K2.6
missed request-lifecycle behavior. GLM made no React patch.

On Java, implementations commonly solved concurrent deduplication and retry
but missed expiry-aware capacity eviction and strong ETag defensive-copy
semantics. Kimi K2.6 and MiniMax produced no Java patch.

Godot separated the models cleanly by language boundary. Every model repaired
the GDScript coordinator. Kimi K2.7 also passed both C# checks. GPT-5.5 high,
Kimi K2.6, MiniMax, MiMo, Qwen Max, and Qwen Plus passed atomic save and slot
validation but missed migration isolation. GLM and DeepSeek missed both C#
checks.

The C++ task was the strongest discriminator for low-level reasoning. GPT-5.5
high, GLM-5.2, Kimi K2.7, Kimi K2.6, and MiMo earned full credit. DeepSeek,
MiniMax, and Qwen3.7 Plus missed MMIO width or isolation behavior. Qwen3.7 Max
made no patch and retained only the baseline endian check.

Rust divided the field sharply. Kimi K2.7, DeepSeek, and Qwen3.7 Plus passed
all WAL checks. GPT-5.5 high missed crash-safe compaction. GLM, MiniMax,
Kimi K2.6, MiMo, and Qwen3.7 Max received no credit; four produced no patch,
while Kimi K2.6 timed out with an incomplete implementation.

## Code quality and runner behavior

GPT-5.5 high and Qwen3.7 Plus tied for the best overall point score; GPT was
faster, while Qwen Plus had the lowest calculated OpenCode cost among the top
three. Kimi K2.7 was the only model to fully solve Godot, C++, and Rust, but
its C++ run was slow.

DeepSeek was fast and generally produced focused patches, though its earlier
compact-suite integrity violation remains part of the full result. Kimi K2.6
was the least stable route: React and Rust consumed most of the task timeout,
and Java produced no patch. MiniMax also lost substantial time to context
recovery on React and Java.

Raw JSONL output remains untracked because it contains complete model
transcripts and machine-specific paths. The published task records, scores,
times, tokens, and calculated prices are in [results.json](results.json).
