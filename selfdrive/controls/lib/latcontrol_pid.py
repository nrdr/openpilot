import math
import numpy as np

from cereal import log
from opendbc.car.honda.values import CAR
from opendbc.car.honda.carcontroller import get_eps_modified_steering_pressed
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl


CENTER_TAPER_FADE_TAU = 0.25


def get_param_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  value = params.get(key)
  if value is None:
    ret = default
  else:
    try:
      # sunnypilot Params.get() auto-casts by declared key type, so an INT param
      # comes back as a python int (not bytes). Handle bytes/str/number uniformly.
      if isinstance(value, bytes):
        value = value.decode("utf-8")
      ret = float(value) / scale
    except (AttributeError, TypeError, ValueError):
      ret = default

  if min_value is not None:
    ret = max(min_value, ret)
  if max_value is not None:
    ret = min(max_value, ret)
  return ret


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
  center_taper_low = -0.09
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

  # Blend smoothly between turn-in and unwind modifiers instead of hard branches.
  # Binary if/elif caused a step change in scale the moment phase crossed ±0.2,
  # which felt like an abrupt torque drop at the start of unwind.
  # Ramp from 0 at phase=0 to full modifier at |phase|=0.5.
  turn_in_weight = min(max(phase / 0.5, 0.0), 1.0)
  unwind_weight  = min(max(-phase / 0.5, 0.0), 1.0)

  if low_speed_unwind and speed_weight < 0.1:
    # Low-speed unwind: EPS won't self-center, actively boost output
    scale += low_speed_unwind_weight * mid_turn_weight * 0.18
  else:
    scale += speed_weight * mid_turn_weight * (turn_in_weight * mid_turn_turn_in_scale + unwind_weight * mid_turn_unwind_scale)
    scale += speed_weight * angle_weight    * (turn_in_weight * turn_in_scale          - unwind_weight * unwind_scale)

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
    self.params = Params()
    self.frame = -1
    self.lat_pid_tune_scale = 1.0

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

      # Low-speed unwind needs extra feedforward to overcome EPS/tire stiction.
      # The boost is intentionally limited to the first second of each unwind event.
      unwind_ff_boost = float(np.interp(CS.vEgo, [0.0, 10.0], [2.0, 1.0]))
      unwinding = phase < -0.2

      # Smooth FF blend: ramp from ff_scale at phase=0 to unwind_ff_boost at phase=-0.5.
      # Hard binary (if phase < -0.2) caused a step drop of 3-6x in FF the moment
      # the path planner's angular rate slowed — the main source of abrupt unwind feel.
      abs_angle_des = abs(angle_steers_des_no_offset)
      steering_rate_unwind_ff = (angle_steers_des_no_offset * float(CS.steeringRateDeg)) < -1.0

      ff_unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)
      # Stable floor: if steering rate confirms wheel is still returning and angle is
      # meaningful, hold at least half the boost so we don't drop prematurely.
      if steering_rate_unwind_ff and abs_angle_des > 5.0:
        ff_unwind_weight = max(ff_unwind_weight, 0.5)

      ff_multiplier = ff_scale + ff_unwind_weight * max(unwind_ff_boost - ff_scale, 0.0)
      ff *= ff_multiplier

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

      freeze_threshold = 2.0 if self.is_eps_modified else 5.0
      freeze_integrator = steer_limited_by_safety or steering_pressed or CS.vEgo < freeze_threshold

      self.frame += 1
      if self.frame % 300 == 0:
        # default/min/max are in runtime multiplier units; scale converts the stored
        # percent param (100 -> 1.0x). Unset -> 1.0x (neutral, as if the tuner were off).
        self.lat_pid_tune_scale = get_param_float(
          self.params,
          "LatPidTuneScale",
          1.0,
          0.0,
          5.0,
          scale=100.0,
        )

      output_torque = self.pid.update(
        error,
        feedforward=ff,
        speed=CS.vEgo,
        freeze_integrator=freeze_integrator,
      )

      output_torque *= self.lat_pid_tune_scale

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