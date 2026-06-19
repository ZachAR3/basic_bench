# Provider examples

The benchmark is model-neutral. Provider adapters only define how an agent is
launched and how local tool permissions are configured.

## Generic command adapter

Set a JSON command template:

```bash
export BENCH_AGENT_COMMAND='[
  "agent-cli",
  "--workspace", "{workspace}",
  "--prompt", "{prompt}"
]'
export BENCH_AGENT_LABEL='agent-model-name'
```

Run:

```bash
python3 bench.py run-private --provider command --run-id example
python3 bench.py run-large --provider command --run-id example
```

The command must run non-interactively and exit after completing the task.

## Codex CLI with ChatGPT sign-in

Confirm that the CLI is using the ChatGPT account:

```bash
./bin/codex login status
```

For GPT-5.5 with high reasoning:

```bash
export BENCH_AGENT_LABEL='codex-gpt-5.5-high'
export BENCH_AGENT_COMMAND='[
  "{codex}", "exec",
  "--model", "gpt-5.5",
  "--config", "model_reasoning_effort=\"high\"",
  "--config", "web_search=\"disabled\"",
  "--disable", "plugins",
  "--disable", "apps",
  "--disable", "browser_use",
  "--disable", "computer_use",
  "--disable", "memories",
  "--disable", "multi_agent",
  "--ephemeral",
  "--ignore-user-config",
  "--ignore-rules",
  "--dangerously-bypass-approvals-and-sandbox",
  "--json",
  "--cd", "{workspace}",
  "{prompt}"
]'
```

The final flag disables Codex's inner sandbox because the benchmark applies its
own macOS sandbox around the entire agent process. Do not use this command
outside the benchmark harness.

Run:

```bash
python3 bench.py smoke-provider --provider command

python3 bench.py run-private \
  --provider command \
  --run-id codex-gpt-5.5-high \
  --agent-timeout 1800

python3 bench.py run-large \
  --provider command \
  --run-id codex-gpt-5.5-high \
  --agent-timeout 3600
```

## ZCode desktop

Desktop subscriptions are evaluated manually because the application session
is separate from API credentials.

```bash
python3 bench.py prepare-manual-run --run-id zcode-manual --profile zcode
python3 bench.py prepare-large-manual --run-id zcode-manual
```

Follow the generated instructions, then run:

```bash
python3 bench.py finalize-manual-run --run-id zcode-manual
python3 bench.py finalize-large-manual --run-id zcode-manual
```

The generated `zcode.json` disables `WebFetch`, `WebSearch`, and
`ReadSessionContext` without selecting a provider or model.

## ZCode CLI with OpenCode Go

Set the provider key in the current shell:

```bash
export OPENCODE_GO_API_KEY='...'
```

Verify the route:

```bash
python3 bench.py smoke-provider --provider zcode-go
```

Run:

```bash
python3 bench.py run-private --provider zcode-go --run-id zcode-go
python3 bench.py run-large --provider zcode-go --run-id zcode-go
```

Provider configuration lives in `config/zcode-go.json`.

## OpenCode

Copy the example configuration and adjust the provider and model:

```bash
cp config/opencode.example.jsonc opencode.jsonc
```

Then run:

```bash
python3 bench.py run-private --provider opencode --run-id opencode-model
python3 bench.py run-large --provider opencode --run-id opencode-model
```

Local provider files are ignored by Git.

The OpenCode provider watches the JSON event stream. If a provider call emits
nothing for five minutes, the CLI process is stopped and the same session is
resumed first. The continuation is instructed to return `CONTEXT_LOST` if its
conversation history is unavailable. A lost context, unusable session, or
second silent call starts a fresh session in the same workspace, preserving
files already changed. Retryable API errors, including rate limits and server
errors, use the same context-first recovery path. The overall
`--agent-timeout` applies across all attempts.

When a fresh session is required, the result records provider-reported tokens
from completed requests in the abandoned context. The unanswered stalled
request contributes zero tokens.

Change the inactivity threshold when needed:

```bash
export OPENCODE_STALL_TIMEOUT=600
```

Use one OpenCode run at a time. Concurrent subscription requests can increase
rate limiting and make wall-clock comparisons less meaningful.

Run the maintained OpenCode Go comparison matrix sequentially:

```bash
export OPENCODE_GO_API_KEY='...'
./scripts/run_opencode_go_matrix.sh
```

The script covers Kimi K2.6, MiniMax M3, DeepSeek V4 Pro, MiMo V2.5 Pro,
Qwen3.7 Max, and Qwen3.7 Plus. Each model receives a separate run ID and
workspace.

For a long run launched outside the shell that holds the key, place it in the
current macOS login session without printing it:

```bash
read -s "OPENCODE_GO_API_KEY?OpenCode Go key: "
echo
launchctl setenv OPENCODE_GO_API_KEY "$OPENCODE_GO_API_KEY"
unset OPENCODE_GO_API_KEY
```

Remove it after the run:

```bash
launchctl unsetenv OPENCODE_GO_API_KEY
```

### OpenCode Go with Kimi K2.7 Code

```bash
cp config/opencode-go-kimi.example.jsonc opencode.jsonc
export OPENCODE_MODEL='opencode-go/kimi-k2.7-code'
```

The API key is read from `OPENCODE_GO_API_KEY`.
