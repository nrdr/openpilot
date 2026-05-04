#!/usr/bin/env bash

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
cd "${DIR}"
export BASEDIR="${DIR}"

is_device_runtime() {
  [[ -f /TICI ]] || [[ -f /AGNOS ]] || [[ "${SP_FORCE_DEVICE_LAUNCH:-0}" == "1" ]]
}

if is_device_runtime; then
  exec ./launch_chffrplus.sh "$@"
fi

# Desktop/laptop path: run manager in the larch64 container so behavior matches device runtime.
if [[ -x /Applications/Docker.app/Contents/Resources/bin/docker ]]; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:${PATH}"
fi

if ! scripts/laptop_device_build.sh doctor >/dev/null 2>&1; then
  echo "Preparing laptop device-build environment..."
  scripts/laptop_device_build.sh setup "${SP_DEVICE_HOST:-}" "${SP_DEVICE_USER:-comma}" "${SP_DEVICE_PORT:-22}"
fi

desktop_jobs() {
  if command -v nproc >/dev/null 2>&1; then
    nproc
  elif command -v sysctl >/dev/null 2>&1; then
    sysctl -n hw.ncpu
  else
    echo 8
  fi
}

if [[ "${SP_SKIP_DOCKER_AUTO_BUILD:-0}" == "1" ]]; then
  exec scripts/laptop_device_build.sh manager --no-build "$@"
else
  exec scripts/laptop_device_build.sh manager "${SP_DOCKER_BUILD_JOBS:-$(desktop_jobs)}" "$@"
fi
