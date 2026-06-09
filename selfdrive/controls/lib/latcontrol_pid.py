import math
import numpy as np

from cereal import log
from opendbc.car.honda.carcontroller import get_eps_modified_steering_pressed
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.selfdrive.modeld.constants import ModelConstants


CENTER_TAPER_FADE_TAU = 0.25

# Unwind integrator-freeze: when the desired angle is dropping toward center,
# stop accumulating integrator so it doesn't keep pushing torque through the release.
UNWIND_FREEZE_PHASE_THRESHOLD = -0.2   # phase below this = unwinding
UNWIND_FREEZE_ANGLE_NEAR_CENTER = 8.0  # deg; only freeze when heading near center

# Model-trajectory unwind lookahead: read the model's planned lateral-accel profile
# to anticipate the turn release before the instantaneous desired curvature drops.
UNWIND_LOOKAHEAD_MIN_IDX = 5            # skip samples inside the actuator delay window
UNWIND_LOOKAHEAD_SECONDS = 1.0         # how far ahead in the plan to look
UNWIND_LOOKAHEAD_MIN_LAT_ACCEL = 0.3   # m/s^2; ignore near-center noise


_MPH_TO_MS = 0.44704
_LAT_SCALE_LOW_MAX = 25.0 * _MPH_TO_MS    # below this -> low-speed scale
_LAT_SCALE_STD_MAX = 50.0 * _MPH_TO_MS    # below this -> standard scale, else highway


def _lat_pid_scale_banded(v_ego: float, low: float, standard: float, highway: float) -> float:
  # Speed-banded lateral PID output scale. Hard bands mirror carcontroller.torque_lpf_tau
  # so the scale and tau bands line up at the same 25/50 mph boundaries.
  if v_ego < _LAT_SCALE_LOW_MAX:
    return low
  if v_ego < _LAT_SCALE_STD_MAX:
    return standard
  return highway


def _sign(x: float) -> float:
  return 1.0 if x > 0.0 else (-1.0 if x < 0.0 else 0.0)


def _lookahead_release(future_vals, current_val) -> float:
  # If any future planned value flips sign vs. the current command, the plan shows a
  # release coming -> return 0.0. Otherwise return the smallest-magnitude same-sign value.
  if not future_vals:
    return current_val
  same_sign = [v for v in future_vals if _sign(v) == _sign(current_val)]
  if len(same_sign) < len(future_vals):
    return 0.0
  return min(same_sign + [current_val], key=lambda x: abs(x))


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
  # Binary if/elif caused a step change in scale the moment phase crossed +-0.2,
  # which felt like an abrupt torque drop at the start of unwind.
  # Ramp from 0 at phase=0 to full modifier at |phase|=0.5.
  turn_in_weight = min(max(phase / 0.5, 0.0), 1.0)
  unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)

  if low_speed_unwind and speed_weight < 0.1:
    # Low-speed unwind: EPS won't self-center, actively boost output
    scale += low_speed_unwind_weight * mid_turn_weight * 0.18
  else:
    scale += speed_weight * mid_turn_weight * (turn_in_weight * mid_turn_turn_in_scale + unwind_weight * mid_turn_unwind_scale)
    scale += speed_weight * angle_weight * (turn_in_weight * turn_in_scale - unwind_weight * unwind_scale)

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
    # Live-tunable high-speed center taper (replaces the old per-car lookup).
    self.center_taper_high = 0.5

    self.eps_modified_steering_pressed_filter_s = 0.0
    self.eps_modified_steering_pressed_prev = False
    self.center_taper_scale = FirstOrderFilter(1.0, CENTER_TAPER_FADE_TAU, dt)
    self.prev_output_torque = 0.0
    self.prev_angle_steers_des_no_offset = 0.0
    self.params = Params()
    self.frame = -1
    # Speed-banded lateral PID output scale (multiplier units; 1.0 = neutral).
    self.lat_pid_scale_low = 1.0
    self.lat_pid_scale_standard = 1.0
    self.lat_pid_scale_highway = 1.0
    self.unwind_freeze_enabled = False
    self.unwind_lookahead_enabled = False
    self.model_v2 = None
    self.model_valid = False

  def update_model_v2(self, model_v2):
    self.model_v2 = model_v2
    self.model_valid = model_v2 is not None and len(model_v2.acceleration.y) >= CONTROL_N

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
      ff_scale = 1.0

      # Low-speed unwind needs extra feedforward to overcome EPS/tire stiction.
      # The boost is intentionally limited to the first second of each unwind event.
      unwind_ff_boost = float(np.interp(CS.vEgo, [0.0, 10.0], [2.0, 1.0]))

      # Smooth FF blend: ramp from ff_scale at phase=0 to unwind_ff_boost at phase=-0.5.
      abs_angle_des = abs(angle_steers_des_no_offset)
      steering_rate_unwind_ff = (angle_steers_des_no_offset * float(CS.steeringRateDeg)) < -1.0

      ff_unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)
      # Stable floor: if steering rate confirms wheel is still returning and angle is
      # meaningful, hold at least half the boost so we don't drop prematurely.
      if steering_rate_unwind_ff and abs_angle_des > 5.0:
        ff_unwind_weight = max(ff_unwind_weight, 0.5)

      # Forward-looking unwind: read the model's planned lateral-accel profile to see if
      # the turn is about to release, and ramp the unwind weight early. predicted_unwind_*
      # stay zero/False unless the lookahead toggle is on AND the model frame is valid,
      # so default behavior falls back to the backward-difference phase logic above.
      predicted_unwind_weight = 0.0
      unwind_predicted = False
      if self.unwind_lookahead_enabled and self.model_valid:
        lat_accels = list(self.model_v2.acceleration.y)
        if len(lat_accels) > UNWIND_LOOKAHEAD_MIN_IDX:
          current_la = float(lat_accels[0])
          upper_idx = next((i for i, t in enumerate(ModelConstants.T_IDXS) if t > UNWIND_LOOKAHEAD_SECONDS), len(lat_accels))
          future = [float(v) for v in lat_accels[UNWIND_LOOKAHEAD_MIN_IDX:upper_idx]]
          lookahead_la = _lookahead_release(future, current_la)
          if abs(current_la) > UNWIND_LOOKAHEAD_MIN_LAT_ACCEL:
            predicted_unwind_weight = min(max(1.0 - abs(lookahead_la) / abs(current_la), 0.0), 1.0)
            unwind_predicted = lookahead_la == 0.0 or predicted_unwind_weight > 0.5

      ff_unwind_weight = max(ff_unwind_weight, predicted_unwind_weight)
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

      # Unwind integrator-freeze (opt-in): when the desired angle is dropping toward
      # center, stop the integrator growing so it doesn't push torque through the release.
      unwind_detected = phase < UNWIND_FREEZE_PHASE_THRESHOLD and abs_angle_des < UNWIND_FREEZE_ANGLE_NEAR_CENTER
      if self.unwind_freeze_enabled and (unwind_detected or unwind_predicted):
        freeze_integrator = True

      self.frame += 1
      if self.frame % 300 == 0:
        # Speed-banded PID output scale. default/min/max are in runtime multiplier
        # units; scale converts the stored percent param (100 -> 1.0x). Each band
        # unset -> 1.0x (neutral). Band selection by vEgo happens every frame below.
        self.lat_pid_scale_low = get_param_float(
          self.params, "LatPidScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0,
        )
        self.lat_pid_scale_standard = get_param_float(
          self.params, "LatPidScaleStandard", 1.0, 0.0, 5.0, scale=100.0,
        )
        self.lat_pid_scale_highway = get_param_float(
          self.params, "LatPidScaleHighway", 1.0, 0.0, 5.0, scale=100.0,
        )
        # High-speed center taper target. FLOAT param stored as the real value
        # (UI use_float_scaling), so no scale. Unset -> 0.5 (old generic default).
        self.center_taper_high = get_param_float(
          self.params,
          "HondaCenterScale",
          0.5,
          0.0,
          5.0,
        )
        self.unwind_freeze_enabled = self.params.get_bool("HondaUnwindFreeze")
        self.unwind_lookahead_enabled = self.params.get_bool("HondaUnwindLookahead")

      output_torque = self.pid.update(
        error,
        feedforward=ff,
        speed=CS.vEgo,
        freeze_integrator=freeze_integrator,
      )

      output_torque *= _lat_pid_scale_banded(
        CS.vEgo, self.lat_pid_scale_low, self.lat_pid_scale_standard, self.lat_pid_scale_highway,
      )

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
