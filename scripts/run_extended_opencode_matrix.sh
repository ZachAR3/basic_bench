#!/usr/bin/env bash
set -u

if [[ -z "${OPENCODE_GO_API_KEY:-}" ]] && command -v launchctl >/dev/null; then
  OPENCODE_GO_API_KEY="$(launchctl getenv OPENCODE_GO_API_KEY)"
  export OPENCODE_GO_API_KEY
fi
if [[ -z "${OPENCODE_GO_API_KEY:-}" ]]; then
  echo "OPENCODE_GO_API_KEY is not set." >&2
  exit 2
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
console="$root/results/console-extended"
mkdir -p "$console"
cd "$root"

export OPENCODE_STALL_TIMEOUT="${OPENCODE_STALL_TIMEOUT:-300}"
tasks=(
  "react-offline-sync"
  "java-idempotency"
  "godot-save-pipeline"
  "cpp-memory-bus"
  "rust-wal-queue"
)
models=(
  "glm-5.2"
  "kimi-k2.7-code"
  "kimi-k2.6"
  "minimax-m3"
  "deepseek-v4-pro"
  "mimo-v2.5-pro"
  "qwen3.7-max"
  "qwen3.7-plus"
)

arguments=()
for task in "${tasks[@]}"; do
  arguments+=(--task "$task")
done

for model in "${models[@]}"; do
  run_id="${model}-opencode-go"
  export OPENCODE_MODEL="opencode-go/${model}"
  python3 bench.py run-private \
    --provider opencode \
    --run-id "$run_id" \
    --agent-timeout 2400 \
    --resume \
    "${arguments[@]}" 2>&1 | tee -a "$console/${run_id}.log"
done
