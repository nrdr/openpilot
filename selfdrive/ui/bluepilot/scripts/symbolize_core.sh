#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 <ui-binary> <core-file>"
  exit 1
fi
BIN="$1"
CORE="$2"
if ! command -v gdb >/dev/null 2>&1; then
  echo "gdb not found. Install it first."
  exit 2
fi
gdb -batch \
  -ex "set pagination off" \
  -ex "thread apply all bt full" \
  -ex "quit" \
  "$BIN" "$CORE"
