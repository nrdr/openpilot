"""Prediction and command timing shared by stock modeld and the firmware wrapper.

The 25 ms command compensation is retained from the development port. Stock's
model action architecture is not Cinque: matching tables is not road validation.
"""
from collections import deque
import math

import numpy as np


DELAY_SCHEDULE_BP = (3.5, 7.0, 12.0, 20.0, 30.0)
DELAY_SCHEDULE_V = (.15, .08, .10, .20, .30)
COMMAND_DELAY_BP = (10.0, 15.0)
DEFAULT_COMMAND_DELAY_LOW = .145
DEFAULT_COMMAND_DELAY_HIGH = .025
CIVIC_COMMAND_DELAY_LOW = .175
MAX_COMMAND_DELAY = .30
CIVIC_COMMAND_DELAY_CALIBRATIONS = ("civic_bosch_c020", "civic_teg_a010", "insight_txm_a040")


def prediction_delay(profile, speed: float, stock_delay: float) -> float:
  if profile is not None and profile.prediction_schedule:
    return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))
  return stock_delay


def _setting(settings, key, default):
  try:
    value = float(settings.get(key, default))
  except (TypeError, ValueError, OverflowError):
    return default
  return min(max(value, 0.), MAX_COMMAND_DELAY) if math.isfinite(value) else default


def command_delay(settings, speed: float, *, calibration="clarity_a020") -> float:
  if calibration in CIVIC_COMMAND_DELAY_CALIBRATIONS:
    low, high = CIVIC_COMMAND_DELAY_LOW, DEFAULT_COMMAND_DELAY_HIGH
  else:
    low = _setting(settings, "NrdrYawCommandDelayLow", DEFAULT_COMMAND_DELAY_LOW)
    high = _setting(settings, "NrdrYawCommandDelayHigh", DEFAULT_COMMAND_DELAY_HIGH)
  return float(np.interp(speed, COMMAND_DELAY_BP, (low, high)))


class CommandDelay:
  def __init__(self, dt: float, max_delay=MAX_COMMAND_DELAY):
    if not math.isfinite(dt) or dt <= 0.:
      raise ValueError("dt must be finite and positive")
    self.dt = dt
    self.buf = deque(maxlen=int(math.ceil(max_delay / dt)) + 2)

  def update(self, value: float, delay: float) -> float:
    self.buf.append(float(value))
    delay = min(max(delay, 0.), MAX_COMMAND_DELAY)
    steps = delay / self.dt
    i = int(steps)
    frac = steps - i
    n = len(self.buf)
    newer, older = self.buf[max(n - 1 - i, 0)], self.buf[max(n - 2 - i, 0)]
    return newer + frac * (older - newer)
