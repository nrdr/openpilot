#!/usr/bin/env bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export SPINNER_DETAILED=1

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="13.1"
fi

export STAGING_ROOT="/data/safe_staging"

# Ensure crashlogs dir exists (idempotent)
mkdir -p /data/crashlogs
chmod 755 /data/crashlogs

# --- BluePilot: enable core dumps for UI debugging (idempotent) ---
if ! ulimit -c | grep -q "unlimited"; then
  ulimit -c unlimited
fi
sysctl -w kernel.core_uses_pid=1 >/dev/null 2>&1 || true
sysctl -w kernel.core_pattern=/data/crashlogs/core.%e.%p.%t >/dev/null 2>&1 || true
# ---------------------------------------------------------------
