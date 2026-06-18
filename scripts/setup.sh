#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

git -C "$ROOT" submodule update --init --recursive
python3 "$ROOT/scripts/init_large_task.py"

echo "Setup complete. Run: make audit"
