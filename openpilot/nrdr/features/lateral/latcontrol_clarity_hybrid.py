
import numpy as np

from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioSelection


__all__ = (
  "BLEND_TO_NNLC_SECONDS",
  "BLEND_TO_PID_SECONDS",
  "NNLC_BLEND_HALF_WIDTH",
  "NNLC_DEFAULT_ACTIVATION_SPEED",
  "ClarityHybridExtension",
  "LatControlClarityHybrid",
  "clarity_nnlc_blend_target",
)


NNLC_DEFAULT_ACTIVATION_SPEED = 30.0 * CV.MPH_TO_MS
NNLC_BLEND_HALF_WIDTH = 3.0 * CV.MPH_TO_MS
BLEND_TO_PID_SECONDS = 0.25
BLEND_TO_NNLC_SECONDS = 0.75

def clarity_nnlc_blend_target(v_ego: float, lane_change_state: log.LaneChangeState,
                              activation_speed: float = NNLC_DEFAULT_ACTIVATION_SPEED) -> float:
  if lane_change_state != log.LaneChangeState.off:
    return 0.0
  activation_speed = float(np.clip(activation_speed, 0.0, 100.0 * CV.MPH_TO_MS))
  pid_full_speed = max(0.0, activation_speed - NNLC_BLEND_HALF_WIDTH)
  nnlc_full_speed = min(100.0 * CV.MPH_TO_MS, activation_speed + NNLC_BLEND_HALF_WIDTH)
  if nnlc_full_speed <= pid_full_speed:
    return float(v_ego >= activation_speed)
  return float(np.interp(v_ego, [pid_full_speed, nnlc_full_speed], [0.0, 1.0]))

class ClarityHybridExtension:

  def __init__(self, torque_extension, pid_controller):
    self._torque_extension = torque_extension
    self._pid_controller = pid_controller

  def __getattr__(self, name):
    return getattr(self._torque_extension, name)

  def update_limits(self):
    self._torque_extension.update_limits()

  def update_model_v2(self, model_v2):
    self._torque_extension.update_model_v2(model_v2)
    self._pid_controller.update_model_v2(model_v2)

  def update_lateral_lag(self, lag):
    self._torque_extension.update_lateral_lag(lag)

class LatControlClarityHybrid(LatControl):

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    pid_cp = CI.get_non_essential_params(CP.carFingerprint, CI.interface_config)
    CI.get_non_essential_params_sp(pid_cp, CP.carFingerprint)
    pid_cp.carFw = CP.carFw
    if pid_cp.lateralTuning.which() != "pid":
      raise RuntimeError(f"Clarity hybrid expected PID defaults, got {pid_cp.lateralTuning.which()}")

    self.pid_controller = LatControlPID(pid_cp.as_reader(), CP_SP, CI, dt)
    self.torque_controller = LatControlTorqueV0(CP, CP_SP, CI, dt)
    self.extension = ClarityHybridExtension(self.torque_controller.extension, self.pid_controller)
    self.nnlc_blend = 0.0

  def reset(self):
    super().reset()
    self.pid_controller.reset()
    self.torque_controller.reset()

  def update_torque_parameters(self, latAccelFactor, latAccelOffset, friction):
    self.torque_controller.update_torque_parameters(latAccelFactor, latAccelOffset, friction)

  def set_steer_ratio_selection(self, selection: SteerRatioSelection):
    super().set_steer_ratio_selection(selection)
    self.pid_controller.set_steer_ratio_selection(selection)
    self.torque_controller.set_steer_ratio_selection(selection)

  def _lane_change_state(self):
    model_v2 = self.torque_controller.extension.model_v2
    return log.LaneChangeState.off if model_v2 is None else model_v2.meta.laneChangeState

  def _update_blend(self, active: bool, target: float, lane_change_state: log.LaneChangeState) -> float:
    if lane_change_state != log.LaneChangeState.off:
      self.nnlc_blend = 0.0
      return self.nnlc_blend

    if not active:
      self.nnlc_blend = target
      return self.nnlc_blend

    transition_seconds = BLEND_TO_PID_SECONDS if target < self.nnlc_blend else BLEND_TO_NNLC_SECONDS
    max_delta = self.dt / transition_seconds
    self.nnlc_blend += float(np.clip(target - self.nnlc_blend, -max_delta, max_delta))
    return self.nnlc_blend

  def _pid_only_result(self, pid_output, pid_angle, pid_log):
    self.nnlc_blend = 0.0
    self.torque_controller.extension._pid.i = 0.0
    torque_log = log.ControlsState.LateralTorqueState.new_message()
    torque_log.active = pid_log.active
    torque_log.error = pid_log.angleError
    torque_log.p = pid_log.p
    torque_log.i = pid_log.i
    torque_log.d = 0.0
    torque_log.f = pid_log.f
    torque_log.output = float(pid_output)
    torque_log.saturated = pid_log.saturated
    return float(pid_output), float(pid_angle), torque_log

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_output, pid_angle, pid_log = self.pid_controller.update(
      active, CS, VM, params, steer_limited_by_safety, desired_curvature,
      calibrated_pose, curvature_limited, lat_delay,
    )
    self.torque_controller.extension.nrdr.update()
    pid_extension = self.pid_controller.nrdr_controller
    if pid_extension is not None and pid_extension.firmware_vgr_selected:
      return self._pid_only_result(pid_output, pid_angle, pid_log)

    nnlc_enabled = self.torque_controller.extension._nnlc_enabled
    lane_change_state = self._lane_change_state()
    target = clarity_nnlc_blend_target(CS.vEgo, lane_change_state,
                                       self.torque_controller.extension.activation_speed_mps) if nnlc_enabled else 0.0
    blend = self._update_blend(active, target, lane_change_state)
    if not nnlc_enabled and blend <= 1e-3:
      return self._pid_only_result(pid_output, pid_angle, pid_log)

    nnlc_output, _, torque_log = self.torque_controller.update(
      active, CS, VM, params, steer_limited_by_safety, desired_curvature,
      calibrated_pose, curvature_limited, lat_delay,
    )

    output = float((1.0 - blend) * float(pid_output) + blend * float(nnlc_output))
    torque_log.output = output
    torque_log.active = active
    torque_log.saturated = pid_log.saturated if blend < 0.5 else torque_log.saturated

    if blend <= 1e-3:
      self.torque_controller.extension._pid.i = 0.0
    elif blend >= 1.0 - 1e-3:
      self.pid_controller.pid.i = 0.0

    return output, float(pid_angle), torque_log
