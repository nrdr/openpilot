"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.common.params import Params

MIN_SOFTWARE_DELAY = 0.05
MAX_SOFTWARE_DELAY = 1.0
DEFAULT_SOFTWARE_DELAY = 0.2
LAT_DELAY_BUFFER_SECONDS = 2.0


def _finite_float(value, fallback: float) -> float:
  try:
    result = float(value)
  except (TypeError, ValueError):
    return fallback
  return result if math.isfinite(result) else fallback


def get_lat_delay(params: Params, live_lat_delay: float, steer_actuator_delay: float) -> float:
  actuator_delay = max(_finite_float(steer_actuator_delay, 0.0), 0.0)
  fallback = min(LAT_DELAY_BUFFER_SECONDS, actuator_delay + DEFAULT_SOFTWARE_DELAY)
  if params.get_bool("LagdToggle"):
    live_delay = _finite_float(live_lat_delay, fallback)
    return min(LAT_DELAY_BUFFER_SECONDS, live_delay) if live_delay > 0.0 else fallback

  software_delay = _finite_float(params.get("LagdToggleDelay", return_default=True), DEFAULT_SOFTWARE_DELAY)
  software_delay = min(MAX_SOFTWARE_DELAY, max(MIN_SOFTWARE_DELAY, software_delay))
  return min(LAT_DELAY_BUFFER_SECONDS, actuator_delay + software_delay)
