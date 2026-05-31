"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car import structs

DriveMode = structs.CarStateSP.DriveMode

# Design intent: drive mode changes how OP drives, not normalize PCM remap.
#   ECO:    40% less gas than NORMAL ??? genuinely gentle, conserves battery/fuel.
#           Honda's PCM ECO is already conservative; this stacks on top of that.
#   NORMAL: Baseline ??? OP behaves like a normal car.
#   SPORT:  ~8% more gas than NORMAL ??? modestly assertive. Honda's SPORT PCM already
#           amplifies throttle response so this doesn't need to be dramatic.
#
# Previous design tried to cancel Honda's per-mode PCM remap so OP drove identically
# across all modes ??? that made ECO as aggressive as SPORT, defeating the point.
_GAS_BP_ECO    = [0.,  3.,  6., 10., 15., 20.]
_GAS_V_ECO     = [0.05, 0.13, 0.21, 0.26, 0.30, 0.30]

_GAS_BP_NORMAL = [0.,  3.,  6., 10., 15., 20.]
_GAS_V_NORMAL  = [0.09, 0.22, 0.35, 0.43, 0.50, 0.50]

_GAS_BP_SPORT  = [0.,  3.,  6., 10., 15., 20.]
_GAS_V_SPORT   = [0.10, 0.24, 0.38, 0.46, 0.54, 0.54]


class GasProfileController:
  def __init__(self):
    self._last_drive_mode: DriveMode = DriveMode.unknown

  def get_gas_multiplier(self, v_ego: float, drive_mode: DriveMode) -> tuple[float, bool]:
    """Returns (gas_multiplier, mode_changed). Caller resets adaptive state on mode_changed."""
    mode_changed = drive_mode != self._last_drive_mode and self._last_drive_mode != DriveMode.unknown
    self._last_drive_mode = drive_mode

    if drive_mode == DriveMode.eco:
      bp, v = _GAS_BP_ECO, _GAS_V_ECO
    elif drive_mode == DriveMode.sport:
      bp, v = _GAS_BP_SPORT, _GAS_V_SPORT
    else:
      bp, v = _GAS_BP_NORMAL, _GAS_V_NORMAL

    return float(np.interp(v_ego, bp, v)), mode_changed
