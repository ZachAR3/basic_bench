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
console_dir="$root/results/console"
mkdir -p "$console_dir"
cd "$root"

export OPENCODE_STALL_TIMEOUT="${OPENCODE_STALL_TIMEOUT:-300}"

models=(
  "kimi-k2.6"
  "minimax-m3"
  "deepseek-v4-pro"
  "mimo-v2.5-pro"
  "qwen3.7-max"
  "qwen3.7-plus"
)

for model in "${models[@]}"; do
  run_id="${model}-opencode-go"
  result="$root/results/${run_id}.jsonl"
  log="$console_dir/${run_id}.log"
  export OPENCODE_MODEL="opencode-go/${model}"

  echo "Starting ${model} compact tasks" | tee -a "$log"
  if [[ -f "$result" ]]; then
    python3 bench.py run-private \
      --provider opencode \
      --run-id "$run_id" \
      --agent-timeout 1800 \
      --resume 2>&1 | tee -a "$log"
  else
    python3 bench.py run-private \
      --provider opencode \
      --run-id "$run_id" \
      --agent-timeout 1800 2>&1 | tee -a "$log"
  fi

  status="$(
    python3 - "$result" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
tasks = set()
if path.exists():
    for line in path.read_text().splitlines():
        if line.strip():
            tasks.add(json.loads(line)["task_id"])
compact = len(tasks - {"click-context-provenance"})
large = "click-context-provenance" in tasks
print(f"{compact}:{int(large)}")
PY
  )"
  compact="${status%%:*}"
  large="${status##*:}"

  if [[ "$compact" == "10" && "$large" == "0" ]]; then
    echo "Starting ${model} large task" | tee -a "$log"
    python3 bench.py run-large \
      --provider opencode \
      --run-id "$run_id" \
      --agent-timeout 3600 2>&1 | tee -a "$log"
  fi
done
