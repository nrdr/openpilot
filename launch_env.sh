#!/usr/bin/env bash

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
  # AGNOS is per-device. The mici (comma 4) runs 18.4 from agnos-mici.json; the
  # tizi (C3X) runs 18.3 from agnos.json (comma's tici images at v0.11.1 - same
  # firmware as 18.4, tici system image; 18.4 has no tici system build). Never
  # flash mici images on a C3X (PR #3 lesson). The C3 never reads this - it has
  # its own env + manifest under sunnypilot/system/hardware/c3/.
  if grep -q "comma mici" /sys/firmware/devicetree/base/model 2>/dev/null; then
    export AGNOS_VERSION="18.4"
  else
    export AGNOS_VERSION="18.3"
  fi
fi

export STAGING_ROOT="/data/safe_staging"
