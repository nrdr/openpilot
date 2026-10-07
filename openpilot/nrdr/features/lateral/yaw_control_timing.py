"""Timing for Firmware Controller: per-profile prediction and command delays.

Ported by JamesL787 in nrdr/openpilot PR #18 (ab868ea15561dd65a4bc52199ec11abbbd4bf789),
from vfn-yaw-trim a434a79b19 (096aedb9 delay refit, 0fb4a6dc command delay).
Clarity's measured table replaces the temporary fixed 0.30-second override.
Civic has no measured prediction table and retains live/manual delay. Its command
delay comes from JamesL787 59eb99e318 (0.15 -> 0 seconds), with the same +25 ms
SunnyPilot model-action interpolation compensation as the existing Clarity port.
"""
from collections import deque
import math

import numpy as np

from openpilot.nrdr.params import NrdrParamKey, read_float

# Reference lateral delay VFN supplied to the model instead of lagd/SteerDelay. Each value is the
# measured lag of yaw-sensor curvature behind the logged model action, minus the fixed pipeline offset,
# so the car reaches the requested curvature when the model intends it to. Refit 2026-10-01 against a
# per-route gain: 2.5-5 m/s 0.18/0.14, 5-9 m/s 0.08, 9-15 m/s 0.10 s. Above 15 m/s the values sum the
# stage lags. lagd only learns above 15 m/s, so it cannot find the low-speed end.
DELAY_SCHEDULE_BP = (3.5, 7.0, 12.0, 20.0, 30.0)  # m/s, centres of the measured bands
DELAY_SCHEDULE_V = (0.15, 0.08, 0.10, 0.20, 0.30)  # s

# Command delay: the curvature controlsd hands over is executed this much later. This controller
# reaches a command ~0.07 s after controlsd issues it, faster than the PID it replaced, so on the
# source model (Cinque v3, which aims ~0.28 s after the frame whatever delay it is told) it ran the
# model's plan 0.12-0.14 s early on 5-12 m/s turns. 0.12 s fixed that; the defaults add 0.025 s that
# stands in for the source branch's model-action interpolation, which this port does not carry.
# Other models aim differently, so both ends are settings; the delay fades between them on speed.
COMMAND_DELAY_BP = (10.0, 15.0)  # m/s
DEFAULT_COMMAND_DELAY_LOW = 0.145  # s
DEFAULT_COMMAND_DELAY_HIGH = 0.025  # s
CIVIC_COMMAND_DELAY_LOW = 0.175  # 0.15 source + 0.025 port compensation
MAX_COMMAND_DELAY = 0.30  # s


def clarity_lateral_delay(speed: float) -> float:
  return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))


def prediction_delay_schedule(profile):
  return (DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V) if profile is not None and profile.prediction_schedule else None


def _command_delay_setting(settings, key, default: float) -> float:
  if settings is None:
    return default
  value = read_float(settings, key, default)
  return min(max(value, 0.0), MAX_COMMAND_DELAY) if math.isfinite(value) else default


def command_delay(settings, speed: float, *, calibration: str = "clarity_a020") -> float:
  if calibration == "civic_bosch_c020":
    # Do not let persisted Clarity command-delay settings silently retune Civic.
    return float(np.interp(speed, COMMAND_DELAY_BP, (CIVIC_COMMAND_DELAY_LOW, DEFAULT_COMMAND_DELAY_HIGH)))
  low = _command_delay_setting(settings, NrdrParamKey.NRDR_YAW_COMMAND_DELAY_LOW, DEFAULT_COMMAND_DELAY_LOW)
  high = _command_delay_setting(settings, NrdrParamKey.NRDR_YAW_COMMAND_DELAY_HIGH, DEFAULT_COMMAND_DELAY_HIGH)
  return float(np.interp(speed, COMMAND_DELAY_BP, (low, high)))


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
