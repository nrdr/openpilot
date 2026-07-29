"""Clarity-only PID/NNLC hybrid lateral controller."""

import numpy as np

from cereal import log
from openpilot.common.constants import CV
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0


# Keep the road-proven PID fully in charge below the transition and NNLC fully in
# charge above it. The narrow speed blend plus the time-domain slew limit prevents
# a step in commanded torque while crossing 30 mph.
PID_FULL_SPEED = 27.0 * CV.MPH_TO_MS
NNLC_FULL_SPEED = 33.0 * CV.MPH_TO_MS
BLEND_TO_PID_SECONDS = 0.25
BLEND_TO_NNLC_SECONDS = 0.75


def clarity_nnlc_blend_target(v_ego: float, lane_change_state: log.LaneChangeState) -> float:
  if lane_change_state != log.LaneChangeState.off:
    return 0.0
  return float(np.interp(v_ego, [PID_FULL_SPEED, NNLC_FULL_SPEED], [0.0, 1.0]))


class ClarityHybridExtension:
  """Preserve controlsd's Torque extension API while also feeding PID model state."""

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
  """Run Clarity PID and NNLC every frame, then blend their torque outputs."""

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    # setup_interfaces() changes the runtime CarParams union to Torque before
    # controlsd starts. Recreate the unmodified per-car parameters solely for the
    # parallel PID controller; this retains the Clarity PID tune and VGR curve.
    pid_cp = CI.get_non_essential_params(CP.carFingerprint)
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

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_controller.update_live_torque_params(latAccelFactor, latAccelOffset, friction)

  def _lane_change_state(self):
    model_v2 = self.torque_controller.extension.model_v2
    return log.LaneChangeState.off if model_v2 is None else model_v2.meta.laneChangeState

  def _update_blend(self, active: bool, target: float, lane_change_state: log.LaneChangeState) -> float:
    # preLaneChange is emitted before laneChangeStarting. Select the already-warm
    # PID immediately so the first lane-change curvature cannot receive NNLC torque.
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

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    # PID intentionally runs first. Its fingerprint-scoped SR(|angle|) update is
    # applied to the shared VehicleModel before NNLC measures actual curvature.
    pid_output, pid_angle, pid_log = self.pid_controller.update(
      active, CS, VM, params, steer_limited_by_safety, desired_curvature,
      calibrated_pose, curvature_limited, lat_delay,
    )
    nnlc_output, _, torque_log = self.torque_controller.update(
      active, CS, VM, params, steer_limited_by_safety, desired_curvature,
      calibrated_pose, curvature_limited, lat_delay,
    )

    lane_change_state = self._lane_change_state()
    target = clarity_nnlc_blend_target(CS.vEgo, lane_change_state)
    if not self.torque_controller.extension._nnlc_enabled:
      target = 0.0
    blend = self._update_blend(active, target, lane_change_state)

    output = float((1.0 - blend) * float(pid_output) + blend * float(nnlc_output))
    torque_log.output = output
    torque_log.active = active
    torque_log.saturated = pid_log.saturated if blend < 0.5 else torque_log.saturated

    # Do not carry a hidden integrator charge across a controller handoff. P and
    # feedforward still run every frame, while the inactive controller's I stays neutral.
    if blend <= 1e-3:
      self.torque_controller.extension._nnlc_pid.i = 0.0
    elif blend >= 1.0 - 1e-3:
      self.pid_controller.pid.i = 0.0

    return output, float(pid_angle), torque_log
