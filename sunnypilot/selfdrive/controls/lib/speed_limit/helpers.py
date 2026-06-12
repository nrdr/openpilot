"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom, car
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode as SpeedLimitMode

# Honda cluster MPH rounding quirks (legacy behavior).
HONDA_MPH_PER_KPH = 0.6233
HONDA_MPH_OFFSET = 0.0995


def _honda_ms_to_mph_int(v_ms: float) -> int:
  """Convert m/s to the integer MPH value a Honda cluster would display."""
  kph = v_ms * CV.MS_TO_KPH
  return int(round(kph * HONDA_MPH_PER_KPH + HONDA_MPH_OFFSET))


def compare_cluster_target(v_cruise_cluster: float,
                           target_set_speed: float,
                           is_metric: bool,
                           honda_imperial: bool = False) -> tuple[bool, bool]:
  """
  Compare current cluster set speed vs target set speed and decide if SLA should request + or -.

  For most cars:
    - Convert using round(ms->kph/mph).

  For Honda in imperial mode:
    - Use Honda's cluster MPH ladder mapping (kph*0.6233 + 0.0995) for both values.
  """
  if not is_metric and honda_imperial:
    v_cruise_cluster_conv = _honda_ms_to_mph_int(v_cruise_cluster)
    target_set_speed_conv = _honda_ms_to_mph_int(target_set_speed)
  else:
    speed_conv = CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH
    v_cruise_cluster_conv = round(v_cruise_cluster * speed_conv)
    target_set_speed_conv = round(target_set_speed * speed_conv)

  req_plus = v_cruise_cluster_conv < target_set_speed_conv
  req_minus = v_cruise_cluster_conv > target_set_speed_conv

  return req_plus, req_minus


def set_speed_limit_assist_availability(CP: car.CarParams, CP_SP: custom.CarParamsSP, params: Params = None) -> bool:
  if params is None:
    params = Params()

  is_release = params.get_bool("IsReleaseSpBranch")
  disallow_in_release = CP.brand == "tesla" and is_release
  always_disallow = CP.brand == "rivian"
  allowed = True

  if disallow_in_release or always_disallow:
    allowed = False

  if not CP.openpilotLongitudinalControl and CP_SP.pcmCruiseSpeed:
    allowed = False

  if not allowed:
    if params.get("SpeedLimitMode", return_default=True) == SpeedLimitMode.assist:
      params.put("SpeedLimitMode", int(SpeedLimitMode.warning), block=True)

  return allowed
