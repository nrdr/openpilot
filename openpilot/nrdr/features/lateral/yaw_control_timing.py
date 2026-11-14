"""PTM Controller timing from Biscuit-Labs Honda-PTM-Testing 45e5b91fae.

Prediction schedules and command delays are firmware-calibration data, not user tuning.
Legacy NrdrYawCommandDelayLow/High values remain stored but are no longer consumed.
"""
from collections import deque
import math

import numpy as np

DELAY_SCHEDULE_BP = (3.5, 7.0, 12.0, 20.0, 30.0)
DELAY_SCHEDULE_V = (0.15, 0.08, 0.10, 0.20, 0.30)
TEG_A010_DELAY_SCHEDULE_V = (0.20, 0.20, 0.20, 0.20, 0.20)
CIVIC_C020_DELAY_SCHEDULE_V = (0.28, 0.28, 0.28, 0.26, 0.26)
_PREDICTION_SCHEDULE_V = {
  "civic_teg_a010": TEG_A010_DELAY_SCHEDULE_V, "civic_tba_a030": TEG_A010_DELAY_SCHEDULE_V,
  "civic_bosch_c020": CIVIC_C020_DELAY_SCHEDULE_V, "civic_tba_c120": CIVIC_C020_DELAY_SCHEDULE_V,
  "civic_tgg_a120": CIVIC_C020_DELAY_SCHEDULE_V,
  "rdx_tjb_a220": (0.15, 0.40, 0.40, 0.22, 0.30),
}
COMMAND_DELAY_BP = (10.0, 15.0)
COMMAND_DELAY_ENDPOINTS = {
  "clarity_a020": (0.20, 0.10),
  "civic_bosch_c020": (0.15, 0.15), "civic_teg_a010": (0.15, 0.15),
  "civic_tba_c120": (0.15, 0.15), "civic_tgg_a120": (0.15, 0.15), "civic_tba_a030": (0.15, 0.15),
  "insight_txm_a040": (0.15, 0.0),
  "crv_tla_a040": (0.18, 0.0), "crv_tla_a220": (0.12, 0.0),
  "rdx_tjb_a220": (0.12, 0.0), "odyssey_thr_a020": (0.12, 0.0), "ridgeline_t6z_a110": (0.12, 0.0),
}
MAX_COMMAND_DELAY = 0.30  # buffer capacity; not an adjustable timing limit


def clarity_lateral_delay(speed: float) -> float:
  return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))


def prediction_delay_schedule(profile):
  if profile is None or not profile.prediction_schedule:
    return None
  return DELAY_SCHEDULE_BP, _PREDICTION_SCHEDULE_V.get(profile.calibration, DELAY_SCHEDULE_V)


def command_delay(settings, speed: float, *, calibration: str = "clarity_a020") -> float:
  """Donor's fixed per-car speed interpolation; saved settings cannot alter the calibration."""
  return float(np.interp(speed, COMMAND_DELAY_BP, COMMAND_DELAY_ENDPOINTS[calibration]))


class CommandDelay:
  """Fixed-rate delay line, linearly interpolated between samples. Fills while inactive so
  engagement starts from the delayed history rather than a step."""

  def __init__(self, dt: float, max_delay: float = MAX_COMMAND_DELAY):
    self.dt = dt
    self.buf: deque[float] = deque(maxlen=int(math.ceil(max_delay / dt)) + 2)

  def update(self, value: float, delay: float) -> float:
    self.buf.append(float(value))
    if delay <= 0.0:
      return float(value)
    steps = delay / self.dt
    i = int(steps)
    frac = steps - i
    n = len(self.buf)
    newer = self.buf[max(n - 1 - i, 0)]
    older = self.buf[max(n - 2 - i, 0)]
    return newer + frac * (older - newer)
