"""Timing for the Clarity Yaw Control: model delay schedule and command delay.

Ported by JamesL787 in nrdr/openpilot PR #18 (ab868ea15561dd65a4bc52199ec11abbbd4bf789),
from vfn-yaw-trim a434a79b19 (096aedb9 delay refit, 0fb4a6dc command delay).
Pure functions and a small buffer; settings arrive as a startup value or the controlsd live snapshot.
"""
from collections import deque
import math

import numpy as np

from openpilot.nrdr.params import NrdrParamKey, read_bool, read_float

# Lateral delay the model is told in place of lagd/SteerDelay, scheduled on speed. Each value is the
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
MAX_COMMAND_DELAY = 0.30  # s


def clarity_lateral_delay(speed: float) -> float:
  return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))


def delay_schedule_enabled(settings) -> bool:
  """Startup-only: modeld and controlsd must agree for the whole onroad session."""
  return read_bool(settings, NrdrParamKey.NRDR_YAW_DELAY_SCHEDULE, True)


def _command_delay_setting(settings, key, default: float) -> float:
  if settings is None:
    return default
  value = read_float(settings, key, default)
  return min(max(value, 0.0), MAX_COMMAND_DELAY) if math.isfinite(value) else default


def command_delay(settings, speed: float) -> float:
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
