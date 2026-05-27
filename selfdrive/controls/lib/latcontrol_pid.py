import math
import numpy as np

from cereal import log
from opendbc.car.honda.values import CAR
from opendbc.car.honda.carcontroller import get_eps_modified_steering_pressed
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl


CENTER_TAPER_FADE_TAU = 0.25


def _center_taper_high(car_fingerprint) -> float:
  if car_fingerprint in (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CIVIC_BOSCH_DIESEL):
    return 0.25
  if car_fingerprint == CAR.HONDA_CLARITY:
    return 1.24

  return 0.5


def _pid_output_scale(
  desired_angle_deg: float,
  desired_angle_delta_deg: float,
  steering_rate_deg: float,
  v_ego: float,
  center_taper_scale: float = 1.0,
  center_taper_high: float = 2.0,
) -> float:
  abs_angle = abs(desired_angle_deg)
  speed_weight = min(max((v_ego - 4.0) / 10.0, 0.0), 1.0)
  center_speed_weight = 0.65 + (0.35 * speed_weight)
  center_weight = min(max((16.0 - abs_angle) / 16.0, 0.0), 1.0)
  mid_turn_weight = min(max((abs_angle - 10.0) / 10.0, 0.0), 1.0)
  angle_weight = min(max((abs_angle - 16.0) / 12.0, 0.0), 1.0)
  phase = desired_angle_deg * desired_angle_delta_deg
  is_left = desired_angle_deg > 0.0

  # At very low speeds, steering angle changes more slowly during unwind,
  # which can delay phase detection and cause late steering release.
  low_speed_unwind_weight = min(max(1.0 - (v_ego / (15.0 * 0.44704)), 0.0), 1.0)
  unwind_phase_threshold = -0.2 + (0.17 * low_speed_unwind_weight)
  steering_rate_unwind = desired_angle_deg * steering_rate_deg < -1.0
  low_speed_unwind = low_speed_unwind_weight > 0.0 and steering_rate_unwind

  # Center taper is intentionally negative at very low speeds to reduce
  # center twitchiness, then ramps back to the vehicle-specific positive taper by 50 mph.
  center_taper_low = -0.1764
  center_taper_speed_weight = min(max(v_ego / (50.0 * 0.44704), 0.0), 1.0)
  center_taper = (center_taper_low + ((center_taper_high - center_taper_low) * center_taper_speed_weight)) * center_taper_scale

  mid_turn_scale = 0.1200 if is_left else 0.0150
  mid_turn_turn_in_scale = -0.5500 if is_left else -0.0524
  mid_turn_unwind_scale = -0.0743 if is_left else -0.0842
  base_scale = 0.0722 if is_left else 0.0972
  turn_in_scale = -0.0799 if is_left else 0.0888
  unwind_scale = 0.1600 if is_left else 0.2000

  scale = 1.0 + (center_speed_weight * center_weight * center_taper)
  scale += speed_weight * mid_turn_weight * mid_turn_scale
  scale += speed_weight * angle_weight * base_scale

  if phase > 0.2:
    scale += speed_weight * mid_turn_weight * mid_turn_turn_in_scale
    scale += speed_weight * angle_weight * turn_in_scale
  elif phase < unwind_phase_threshold or low_speed_unwind:
    scale += speed_weight * mid_turn_weight * mid_turn_unwind_scale
    scale -= speed_weight * angle_weight * unwind_scale

  return max(scale, 0.6863)


class LatControlPID(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    self.pid = PIDController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                             (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                             pos_limit=self.steer_max, neg_limit=-self.steer_max)

    self.ff_factor = CP.lateralTuning.pid.kf
    self.CI = CI
    self.get_steer_feedforward = CI.get_steer_feedforward_function()

    self.is_eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    self.center_taper_high = _center_taper_high(CP.carFingerprint)

    self.eps_modified_steering_pressed_filter_s = 0.0
    self.eps_modified_steering_pressed_prev = False
    self.center_taper_scale = FirstOrderFilter(1.0, CENTER_TAPER_FADE_TAU, dt)
    self.prev_output_torque = 0.0
    self.prev_angle_steers_des_no_offset = 0.0

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
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
      self.center_taper_scale.x = 1.0
      self.prev_output_torque = 0.0
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset

    else:
      desired_angle_delta = angle_steers_des_no_offset - self.prev_angle_steers_des_no_offset
      phase = angle_steers_des_no_offset * desired_angle_delta

      # Offset does not contribute to resistive torque.
      ff = self.ff_factor * self.get_steer_feedforward(angle_steers_des_no_offset, CS.vEgo)

      # Smooth feedforward scaling: matches PID ramp (0–10 m/s → 0.1–1.0).
      ff_scale = float(np.interp(CS.vEgo, [0.0, 10.0, 35.0], [0.1, 0.5, 1.0]))

      # Low-speed unwind needs extra feedforward to overcome EPS/tire stiction,
      # but the boost fades out as speed increases to avoid twitchiness.
      unwind_ff_boost = float(np.interp(CS.vEgo, [0.0, 10.0], [6.0, 1.0]))

      if phase < -0.2:
        ff *= max(ff_scale, unwind_ff_boost)
      else:
        ff *= ff_scale

      steering_pressed = CS.steeringPressed
      if self.is_eps_modified:
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

      if self.is_eps_modified:
        lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))

        if lane_change:
          self.center_taper_scale.x = 0.0
          center_taper_scale = 0.0
        else:
          center_taper_scale = float(self.center_taper_scale.update(1.0))

        output_torque *= _pid_output_scale(
          angle_steers_des_no_offset,
          desired_angle_delta,
          float(CS.steeringRateDeg),
          CS.vEgo,
          center_taper_scale,
          self.center_taper_high,
        )
        output_torque = float(max(min(output_torque, self.steer_max), -self.steer_max))

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(output_torque)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output_torque) < 1e-3,
        CS,
        steer_limited_by_safety,
        curvature_limited,
      ))

      self.prev_output_torque = float(output_torque)
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset

    return output_torque, angle_steers_des, pid_log