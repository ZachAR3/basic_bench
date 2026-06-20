#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$ROOT/private/tasks/react-offline-sync"

required=(node npm dotnet cargo rustc clang++)
for command in "${required[@]}"; do
  if ! command -v "$command" >/dev/null; then
    echo "Missing required command: $command" >&2
    exit 2
  fi
done

JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home}"
GODOT="${GODOT:-/Applications/Godot.app/Contents/MacOS/Godot}"

if [[ ! -x "$JAVA_HOME/bin/javac" ]]; then
  echo "Missing Java 21. On macOS: brew install openjdk@21" >&2
  exit 2
fi
if [[ ! -x "$GODOT" ]]; then
  echo "Missing Godot. On macOS: brew install --cask godot" >&2
  exit 2
fi

npm ci --ignore-scripts --prefix "$WEB"
npm rebuild esbuild --prefix "$WEB"

echo "Multi-language task runtimes are ready."
