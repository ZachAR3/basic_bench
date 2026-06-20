#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

git -C "$ROOT" submodule update --init --recursive
python3 "$ROOT/scripts/init_large_task.py"
"$ROOT/scripts/setup_multilang.sh"

echo "Setup complete. Run: make audit"
