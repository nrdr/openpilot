import numpy as np

from opendbc.car.interfaces import ACCEL_MAX
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.nrdr.params import read_float


PARAM_REFRESH_FRAMES = 20
LAUNCH_DISARM_SPEED = 2.0
LAUNCH_COMMIT_TIME = 3.5
LAUNCH_MOVING_SPEED = 1.2
LAUNCH_MAX_ACCEL = 3.5
CRUISE_ACCEL_VALUES = (2.0, 1.6, 0.8, 0.6)


class NrdrLongitudinalPlanner:
  def __init__(self, CP, tune):
    self.CP = CP
    self.tune = tune
    self.params = Params()
    self.frame = 0
    self.v_ego_stopping = CP.vEgoStopping
    self.cruise_scale = 1.0
    self.launch_armed = False

  def refresh(self) -> None:
    if self.frame % PARAM_REFRESH_FRAMES == 0:
      self.v_ego_stopping = read_float(self.params, "HondaVEgoStopping", self.CP.vEgoStopping, 0.0, 5.0)
      self.cruise_scale = read_float(self.params, "NrdrCruiseMismatchCorrection", 100.0, 95.0, 105.0) / 100.0
    self.frame += 1

  def max_accel_values(self) -> np.ndarray:
    return np.minimum(np.asarray(CRUISE_ACCEL_VALUES) * self.tune.a_cruise_max_scale, ACCEL_MAX)

  def cruise_target(self, target: float) -> float:
    if target <= 0.0 or self.cruise_scale == 1.0:
      return target
    return min(target * self.cruise_scale, V_CRUISE_MAX * CV.KPH_TO_MS)

  def launch_accel(self, sm, mpc_time_indices, action_time: float, v_ego: float,
                   should_stop: bool, output_accel: float, e2e_active: bool) -> float:
    if sm["carState"].standstill:
      self.launch_armed = True
    elif v_ego > LAUNCH_DISARM_SPEED:
      self.launch_armed = False

    model = sm["modelV2"]
    if (len(model.velocity.x) != ModelConstants.IDX_N or
        len(model.acceleration.x) != ModelConstants.IDX_N):
      return output_accel

    model_v = np.interp(mpc_time_indices, ModelConstants.T_IDXS, model.velocity.x)
    if (not self.launch_armed or not e2e_active or should_stop or
        np.interp(LAUNCH_COMMIT_TIME, mpc_time_indices, model_v) <= LAUNCH_DISARM_SPEED):
      return output_accel

    model_a = np.interp(mpc_time_indices, ModelConstants.T_IDXS, model.acceleration.x)
    time_cut = min(float(mpc_time_indices[np.argmax(model_v > LAUNCH_MOVING_SPEED)]), LAUNCH_COMMIT_TIME)
    shifted_time = mpc_time_indices + time_cut
    shifted_v = np.interp(shifted_time, mpc_time_indices, model_v)
    shifted_a = np.interp(shifted_time, mpc_time_indices, model_a)
    launch_accel = get_accel_from_plan(
      shifted_v,
      shifted_a,
      mpc_time_indices,
      action_t=action_time,
      v_ego_stopping=self.v_ego_stopping,
    )[0]
    maximum = np.interp(v_ego, [LAUNCH_MOVING_SPEED, LAUNCH_DISARM_SPEED], [LAUNCH_MAX_ACCEL, 0.0])
    return max(output_accel, min(launch_accel, maximum))
