"""mmmorks' Pilot shaping rules applied to MVL's non-interceptor PCM path.

Source: nrdr/openpilot dae74e9300fa10bbda50a8c4efdd02031d9af390.
This is a command-shaping port, not a claim that every Nidec shares that ECU.
The original deadband/200 ms transition interval also withhold brake demand.
"""
import math

import numpy as np

from opendbc.car import DT_CTRL


class EcuMatchedPCM:
  def __init__(self):
    self.reset()

  def reset(self):
    self.accel = 0.0
    self.last_sign = 0
    self.coast_frames = 0

  def update_accel(self, requested: float, *, active: bool) -> float:
    if not active or not math.isfinite(requested):
      self.reset()
      return 0.0
    self.accel = float(np.clip(requested, self.accel - 6.0 * DT_CTRL, self.accel + 5.0 * DT_CTRL))
    sign = 1 if self.accel > 0.05 else -1 if self.accel < -0.05 else 0
    if sign and self.last_sign and sign != self.last_sign:
      self.coast_frames = round(0.2 / DT_CTRL)
    if sign:
      self.last_sign = sign
    return self.accel

  def coast(self, gas: float, brake: float, speed: float) -> bool:
    deadband = float(np.interp(speed, [2.5, 10.0, 20.0, 30.0], [0.08, 0.06, 0.03, 0.005]))
    coast = (gas < deadband and brake < deadband) or self.coast_frames > 0
    self.coast_frames = max(0, self.coast_frames - 1)
    return coast
