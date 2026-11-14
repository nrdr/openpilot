import math

import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.common.simple_kalman import KF1D, get_kalman_gain


ACCEL_TAU = 1.5
COAST_CYCLES = 5
STATIONARY_SPEED = 4.0


class CivicBoschKalmanParams:
  def __init__(self):
    dt = 0.06
    self.A = [[1.0, dt], [0.0, 1.0]]
    self.C = [1.0, 0.0]
    gain = get_kalman_gain(dt, np.asarray(self.A), np.asarray([self.C]), np.diag([0.0, 4.0]), np.asarray([[0.1]]))
    self.K = [[float(gain[0, 0])], [float(gain[1, 0])]]


class CivicBoschTrack:
  def __init__(self, identifier: int, v_lead: float, kalman_params):
    self.identifier = identifier
    self.cnt = 0
    self.measured_sweep_count = 0
    self.unmeasured_cnt = 0
    self.v_ego = 0.0
    self.measured = False
    self.aLeadTau = FirstOrderFilter(ACCEL_TAU, 0.45, DT_MDL)
    self.K_A = kalman_params.A
    self.K_C = kalman_params.C
    self.K_K = kalman_params.K
    self.kf = KF1D([[0.0 if math.isnan(v_lead) else v_lead], [0.0]], self.K_A, self.K_C, self.K_K)

  def update(self, d_rel: float, y_rel: float, v_rel: float, v_lead: float, measured: bool, v_ego: float):
    measured = measured and not math.isnan(v_rel)
    if math.isnan(v_rel):
      v_rel = 0.0
      v_lead = v_ego

    self.dRel = d_rel
    self.yRel = y_rel
    self.vRel = v_rel
    self.vLead = v_lead
    self.measured = measured
    self.v_ego = v_ego

    if self.cnt > 0:
      if measured:
        self.kf.update(v_lead)
        self.unmeasured_cnt = 0
      else:
        self.unmeasured_cnt += 1
        if self.unmeasured_cnt <= COAST_CYCLES:
          velocity, accel = float(self.kf.x[0][0]), float(self.kf.x[1][0])
          self.kf.set_x([[velocity + self.K_A[0][1] * accel], [accel]])
    elif not measured:
      self.unmeasured_cnt += 1

    self.vLeadK = float(self.kf.x[0][0])
    self.aLeadK = float(self.kf.x[1][0])
    if measured:
      self.measured_sweep_count += 1
      if abs(self.aLeadK) < 0.5:
        self.aLeadTau.x = ACCEL_TAU
      else:
        self.aLeadTau.update(0.0)
    self.cnt += 1

  def get_RadarState(self, model_prob: float = 0.0):
    if not self.measured and self.unmeasured_cnt <= COAST_CYCLES:
      v_lead = self.vLeadK
      v_rel = self.vLeadK - self.v_ego
    else:
      v_lead = self.vLead
      v_rel = self.vRel
    return {
      "dRel": float(self.dRel),
      "yRel": float(self.yRel),
      "vRel": float(v_rel),
      "vLead": float(v_lead),
      "vLeadK": float(self.vLeadK),
      "aLeadK": float(self.aLeadK),
      "aLeadTau": float(self.aLeadTau.x),
      "present": True,
      "modelProb": model_prob,
      "radar": True,
      "radarTrackId": self.identifier,
    }

  def potential_low_speed_lead(self, v_ego: float):
    return abs(self.yRel) < 1.0 and v_ego < STATIONARY_SPEED and 0.75 < self.dRel < 25.0

  def __str__(self):
    return f"x: {self.dRel:4.1f}  y: {self.yRel:4.1f}  v: {self.vRel:4.1f}  a: {self.aLeadK:4.1f}"
