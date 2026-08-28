#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null && pwd)"
exec "$REPO_ROOT/openpilot/nrdr/tools/device/opsync.sh" "$@"
