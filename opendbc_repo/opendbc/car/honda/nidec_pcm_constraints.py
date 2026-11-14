"""Opt-in propulsion shaping for Nidec PCM speed control, never pedal interceptors.

The ramp/deadband numbers are carried from the NRDR Pilot experiment. They are
not an identified Civic plant model. Brake requests and the planner speed
reference remain outside this comfort filter.
"""
import math

import numpy as np

from opendbc.car import DT_CTRL
from opendbc.car.honda.values import CarControllerParams, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


ACCEL_RAMP_UP = 5.0  # m/s^3; original +0.05 per 100 Hz tick
ACCEL_RAMP_DOWN = 6.0  # m/s^3; original -0.06 per 100 Hz tick


def uses_nidec_pcm(CP, CP_SP) -> bool:
  return bool(CP.flags & HondaFlags.NIDEC and CP.openpilotLongitudinalControl and
              not CP.flags & HondaFlags.BOSCH and not CP_SP.enableGasInterceptor and
              not CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL)


def neutral_accel_deadband(speed: float) -> float:
  # The original values were in normalized gas/brake units (accel / 4.8),
  # NOT raw PCM_GAS ticks or physical throttle percentage.
  return 4.8 * float(np.interp(speed, [2.5, 10.0, 20.0, 30.0], [0.08, 0.06, 0.03, 0.005]))


def taper_positive_accel(accel: float, speed: float) -> float:
  """Linear neutral-zone taper, with the original full-acceleration endpoint.

  Regaining the full command at twice the deadband made the local slope reach
  3x: continuous, but a larger PCM-speed step than the raw request. Spread that
  recovery over the existing 2 m/s2 range instead; maximum slope is about 1.24
  at parking speed and 1.01 on the highway. Do not lower the full-accel endpoint.
  """
  deadband = neutral_accel_deadband(speed)
  maximum = CarControllerParams.NIDEC_ACCEL_MAX
  if accel >= maximum:
    return accel
  return max(accel - deadband, 0.0) * maximum / (maximum - deadband)


class NidecPCMConstraints:
  def __init__(self):
    self.accel = 0.0

  def update(self, requested: float, speed: float, *, enabled: bool, active: bool,
             launch: bool = False) -> float:
    if not enabled or not active or not math.isfinite(requested) or not math.isfinite(speed):
      self.accel = max(requested, 0.0) if active and math.isfinite(requested) else 0.0
      return requested

    # Never turn a falling/negative request into retained positive feedforward.
    # Grade/creep braking is independent, including its hysteresis: never reset
    # this filter when a tiny computed brake crosses zero on a hill. Otherwise
    # alternating bypass/reset would inject large speed-target steps even while
    # the actual brake packet stays at zero. Launch retains its existing law.
    if requested <= 0.0 or launch:
      self.accel = max(requested, 0.0) if launch else 0.0
      return requested

    # The old fixed 200 ms sign-change blackout suppressed braking and added
    # a hold/release edge. Use the continuous neutral zone, not a timed gap.
    target = taper_positive_accel(requested, speed)
    self.accel = min(max(target, self.accel - ACCEL_RAMP_DOWN * DT_CTRL), self.accel + ACCEL_RAMP_UP * DT_CTRL)
    return self.accel
