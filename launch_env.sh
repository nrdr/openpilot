#!/usr/bin/env bash

# nrdr: route the backend to konik. Set here (launch_env.sh is sourced by
# launch_chffrplus.sh on every boot) rather than only in launch_openpilot.sh,
# which is not the boot entry on this base. build_prebuilt.sh strips these for
# the clean branch.
export API_HOST=https://api.konik.ai
export ATHENA_HOST=wss://athena.konik.ai

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

# models get lower priority than ui
# - ui is ~5ms
# - modeld is 20ms
# - DM is 10ms
# in order to run ui at 60fps (16.67ms), we need to allow
# it to preempt the model workloads. we have enough
# headroom for this until ui is moved to the CPU.
export QCOM_PRIORITY=12

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="18.5"
fi

export STAGING_ROOT="/data/safe_staging"
