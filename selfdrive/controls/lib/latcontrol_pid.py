import math

from cereal import log
from opendbc.car.honda.carcontroller import get_eps_modified_steering_pressed
from opendbc.car.honda.values import CAR as HONDA
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController


def _clarity_pid_output_scale(desired_angle_deg: float, desired_angle_delta_deg: float, v_ego: float) -> float:
  abs_angle = abs(desired_angle_deg)
  speed_weight = min(max((v_ego - 4.0) / 10.0, 0.0), 1.0)
  center_speed_weight = 0.65 + (0.35 * speed_weight)
  center_weight = min(max((16.0 - abs_angle) / 16.0, 0.0), 1.0)
  angle_weight = min(max((abs_angle - 16.0) / 12.0, 0.0), 1.0)
  phase = desired_angle_deg * desired_angle_delta_deg

  is_left = desired_angle_deg > 0.0
  center_taper = 0.30
  base_scale = 0.10 if is_left else 0.12
  turn_in_scale = 0.10 if is_left else 0.14
  unwind_scale = 0.14 if is_left else 0.20

  scale = 1.0 - (center_speed_weight * center_weight * center_taper)
  scale += speed_weight * angle_weight * base_scale
  if phase > 0.2:
    scale += speed_weight * angle_weight * turn_in_scale
  elif phase < -0.2:
    scale -= speed_weight * angle_weight * unwind_scale

  return max(scale, 0.74)


class LatControlPID(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    self.pid = PIDController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                             (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                             pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.ff_factor = CP.lateralTuning.pid.kf
    self.CI = CI
    self.get_steer_feedforward = CI.get_steer_feedforward_function()
    self.is_clarity_eps_modified = (
      CP.carFingerprint == HONDA.HONDA_CLARITY and
      bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    )
    self.eps_modified_steering_pressed_filter_s = 0.0
    self.eps_modified_steering_pressed_prev = False
    self.prev_output_torque = 0.0
    self.prev_angle_steers_des_no_offset = 0.0

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)

    angle_steers_des_no_offset = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))
    angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg
    error = angle_steers_des - CS.steeringAngleDeg

    pid_log.steeringAngleDesiredDeg = angle_steers_des
    pid_log.angleError = error
    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.eps_modified_steering_pressed_filter_s = 0.0
      self.eps_modified_steering_pressed_prev = False
      self.prev_output_torque = 0.0
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset

    else:
      # offset does not contribute to resistive torque
      ff = self.ff_factor * self.get_steer_feedforward(angle_steers_des_no_offset, CS.vEgo)

      steering_pressed = CS.steeringPressed
      if self.is_clarity_eps_modified:
        self.eps_modified_steering_pressed_filter_s, steering_pressed = get_eps_modified_steering_pressed(
          bool(CS.steeringPressed),
          float(getattr(CS, "steeringTorque", 0.0)),
          float(self.prev_output_torque),
          self.eps_modified_steering_pressed_filter_s,
          self.eps_modified_steering_pressed_prev,
        )
        self.eps_modified_steering_pressed_prev = steering_pressed

      freeze_integrator = steer_limited_by_safety or steering_pressed or CS.vEgo < 5

      output_torque = self.pid.update(error,
                                feedforward=ff,
                                speed=CS.vEgo,
                                freeze_integrator=freeze_integrator)

      if self.is_clarity_eps_modified:
        desired_angle_delta = angle_steers_des_no_offset - self.prev_angle_steers_des_no_offset
        output_torque *= _clarity_pid_output_scale(angle_steers_des_no_offset, desired_angle_delta, CS.vEgo)
        output_torque = float(max(min(output_torque, self.steer_max), -self.steer_max))

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(output_torque)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
      self.prev_output_torque = float(output_torque)
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset

    return output_torque, angle_steers_des, pid_log
