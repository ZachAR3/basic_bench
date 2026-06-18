#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN=""
for candidate in python3.11 python3.10 python3.12 python3.13 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$candidate")"
    break
  fi
done
if [[ -z "$PYTHON_BIN" ]]; then
  echo "Python 3.10+ is required." >&2
  exit 1
fi

clone_pinned() {
  local url="$1"
  local commit="$2"
  local destination="$3"

  if [[ ! -d "$destination/.git" ]]; then
    git clone --filter=blob:none --no-checkout "$url" "$destination"
  fi
  git -C "$destination" fetch --depth 1 origin "$commit"
  git -C "$destination" checkout --detach "$commit"
}

clone_pinned \
  "https://github.com/LiveCodeBench/LiveCodeBench.git" \
  "28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24" \
  "$ROOT/vendor/LiveCodeBench"

clone_pinned \
  "https://github.com/Aider-AI/polyglot-benchmark.git" \
  "7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f" \
  "$ROOT/vendor/polyglot-benchmark"

clone_pinned \
  "https://github.com/SWE-bench/SWE-bench.git" \
  "f7bbbb2ccdf479001d6467c9e34af59e44a840f9" \
  "$ROOT/vendor/SWE-bench"

"$PYTHON_BIN" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --upgrade pip
"$ROOT/.venv/bin/python" -m pip install anthropic "datasets>=3.2,<4" numpy tqdm pebble
"$ROOT/.venv/bin/python" -m pip install -e "$ROOT/vendor/SWE-bench"

echo "Public benchmark Python dependencies installed in $ROOT/.venv"
echo "SWE-bench additionally requires Docker with substantial disk space."
