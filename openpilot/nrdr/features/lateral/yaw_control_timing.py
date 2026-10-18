"""Timing for Firmware Controller: per-profile prediction and command delays.

Ported by JamesL787 in nrdr/openpilot PR #18 (ab868ea15561dd65a4bc52199ec11abbbd4bf789),
from vfn-yaw-trim a434a79b19 (096aedb9 delay refit, 0fb4a6dc command delay).
Clarity's measured table replaces the temporary fixed 0.30-second override.
The TEG-A010 and the C020 have their own prediction tables (2026-10-18), measured
by speed band like the Clarity's; before them lagd told the Civics 0.37-0.39 s and
they ran early. Civic command delay comes from JamesL787 59eb99e318 (0.15 seconds),
with the same +25 ms SunnyPilot model-action interpolation compensation as the
existing Clarity port, held flat with speed.
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
# The Civics' own, on the same speeds: each car's lag from the camera frame to its yaw-sensor curvature, less modeld's
# fixed 0.075 s (frame + half a model step), measured per speed band (JamesL787 ns-bosch-radar-testing, 2026-10-18).
# - TEG-A010: 0.26-0.31 s at every speed on its owner's routes 12e/12f/133/134/137/139/13d (Pop v2 on this
#   controller, the command delay taken out), so 0.20 s flat. lagd told it 0.37-0.39 s: with the plan read 0.44 s
#   out and the car there at ~0.28 s, it turned in early even with the 0.175 s command delay, and ~0.15 s early above
#   15 m/s, where that delay fades out.
# - C020 (provisional): 0.37-0.43 s on route 380 (NovaSpark, an older PID + firmware FF with a 0.09-0.10 s output filter
#   and no command delay); with this controller's filter that is ~0.35-0.41 s in town and ~0.33 s on the highway.
TEG_A010_DELAY_SCHEDULE_V = (0.20, 0.20, 0.20, 0.20, 0.20)  # s
CIVIC_C020_DELAY_SCHEDULE_V = (0.28, 0.28, 0.28, 0.26, 0.26)  # s
# The A030 (the same car as the TEG) takes the TEG's; the C120 and TGG (the C020's chassis) the C020's.
_PREDICTION_SCHEDULE_V = {
  "civic_teg_a010": TEG_A010_DELAY_SCHEDULE_V, "civic_tba_a030": TEG_A010_DELAY_SCHEDULE_V,
  "civic_bosch_c020": CIVIC_C020_DELAY_SCHEDULE_V, "civic_tba_c120": CIVIC_C020_DELAY_SCHEDULE_V,
  "civic_tgg_a120": CIVIC_C020_DELAY_SCHEDULE_V,
}

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
# The TEG-A010 keeps it: with 0.175 applied, plan timing on its owner's routes 12e/134/137/139 (5-12 m/s turns)
# measured the car 0.05 s early (+0.02/-0.06/-0.06/-0.08), so there is no case for less; mostly highway drives.
# The Insight takes it too: its source command delay is the C020's 0.15 s (JamesL787 ns-bosch-radar-testing, the
# calibration it drove on).
CIVIC_COMMAND_DELAY_CALIBRATIONS = ("civic_bosch_c020", "civic_teg_a010", "insight_txm_a040")
# Calibrations whose town command delay is fixed (their source's measured or inferred value + 0.025 s port
# compensation), so persisted Clarity command-delay settings never retune them.
FIXED_COMMAND_DELAY_LOW = dict.fromkeys(CIVIC_COMMAND_DELAY_CALIBRATIONS, CIVIC_COMMAND_DELAY_LOW)
# Corrected-PTM starting calibrations: the C120, TGG-A120 and A030 take the C020's / TEG's 0.15 s; the CR-Vs the
# default 0.12 s (their owner's PID drive ran late, not early). Each + 0.025 s port compensation, re-checked with
# plan timing after a drive.
FIXED_COMMAND_DELAY_LOW.update({"civic_tba_c120": CIVIC_COMMAND_DELAY_LOW, "civic_tgg_a120": CIVIC_COMMAND_DELAY_LOW,
                                "civic_tba_a030": CIVIC_COMMAND_DELAY_LOW, "crv_tla_a040": DEFAULT_COMMAND_DELAY_LOW,
                                "crv_tla_a220": DEFAULT_COMMAND_DELAY_LOW})
# The Civics hold it above 15 m/s too: they ran as early there as in town (TEG -0.13 to -0.17 s at 12-40 m/s with
# it faded out; C020 -0.16 s at 20-40 m/s on route 380), and the C120, TGG and A030 follow them. The Insight's
# highway timing did not need it; the CR-Vs have no timing measured.
CIVIC_FLAT_COMMAND_DELAY_CALIBRATIONS = ("civic_bosch_c020", "civic_teg_a010", "civic_tba_c120", "civic_tgg_a120",
                                         "civic_tba_a030")
MAX_COMMAND_DELAY = 0.30  # s


def clarity_lateral_delay(speed: float) -> float:
  return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))


def prediction_delay_schedule(profile):
  if profile is None or not profile.prediction_schedule:
    return None
  return DELAY_SCHEDULE_BP, _PREDICTION_SCHEDULE_V.get(profile.calibration, DELAY_SCHEDULE_V)


def _command_delay_setting(settings, key, default: float) -> float:
  if settings is None:
    return default
  value = read_float(settings, key, default)
  return min(max(value, 0.0), MAX_COMMAND_DELAY) if math.isfinite(value) else default


def command_delay(settings, speed: float, *, calibration: str = "clarity_a020") -> float:
  if calibration in FIXED_COMMAND_DELAY_LOW:
    # Do not let persisted Clarity command-delay settings silently retune another car.
    low = FIXED_COMMAND_DELAY_LOW[calibration]
    high = low if calibration in CIVIC_FLAT_COMMAND_DELAY_CALIBRATIONS else DEFAULT_COMMAND_DELAY_HIGH
    return float(np.interp(speed, COMMAND_DELAY_BP, (low, high)))
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
