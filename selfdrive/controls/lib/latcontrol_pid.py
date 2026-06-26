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

# Center boost speed gate: boost ramps in over this many mph above the min-speed floor,
# so it engages smoothly instead of stepping in the moment the car crosses the threshold.
CENTER_BOOST_SPEED_FADE_MS = 5.0 * _MPH_TO_MS

# Unwind FF boost fades out over this many seconds approaching its time cap, so the boost
# doesn't drop as a torque step the instant the cap is reached.
UNWIND_BOOST_FADE_S = 0.3

# Rate-damping (D) reference gain: output torque per (deg/s) of steering-wheel rate at 100%
# strength. The wheel is torque-commanded, so the plant is a double integrator that pure P
# can't damp at low speed (tire self-aligning torque and the v^2 feedforward both vanish);
# this is the derivative term that flattens it. 0.010 -> 1.0 torque at 100 deg/s @ 100%.
RATE_DAMPING_REF = 0.010

# Derivative Tuning Experiment: during winddown the D term fights the pullback we want at high
# angle, but helps the wheel settle cleanly at center. So while unwinding, fade D out above this
# wheel angle (deg) and back in below it. Full D for normal driving and windup.
D_UNWIND_FADE_ANGLE = 30.0


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
  center_boost_threshold_deg: float = 3.0,
  center_boost_min_speed_ms: float = 0.0,
) -> float:
  abs_angle = abs(desired_angle_deg)
  speed_weight = min(max((v_ego - 4.0) / 10.0, 0.0), 1.0)
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

  # Center boost: one static value across all speed ranges (the old low-speed
  # negative taper and 0-50 mph interp are gone). Active only while the desired
  # angle is within the Center Boost Threshold of dead-center, with a short 1 deg
  # linear fade past the threshold so the boost doesn't step off abruptly.
  center_fade_deg = 1.0
  center_weight = min(max((center_boost_threshold_deg + center_fade_deg - abs_angle) / center_fade_deg, 0.0), 1.0)
  # Speed gate: no center boost below center_boost_min_speed_ms, with a short ramp just
  # above it so the boost doesn't step in abruptly. Center boost is meant for straight,
  # higher-speed roads; gating it off at low speed stops the wheel oscillating at stops
  # and in parking-lot crawl, where the near-center boost was wildly overtuned.
  if center_boost_min_speed_ms > 0.0:
    center_speed_weight = min(max((v_ego - center_boost_min_speed_ms) / CENTER_BOOST_SPEED_FADE_MS, 0.0), 1.0)
  else:
    center_speed_weight = 1.0
  center_taper = center_taper_high * center_taper_scale * center_speed_weight

  mid_turn_scale = 0.1200 if is_left else 0.0150
  mid_turn_turn_in_scale = -0.5500 if is_left else -0.0524
  mid_turn_unwind_scale = -0.0743 if is_left else -0.0842
  base_scale = 0.0722 if is_left else 0.0972
  turn_in_scale = -0.0799 if is_left else 0.0888
  unwind_scale = 0.1600 if is_left else 0.2000

  scale = 1.0 + (center_weight * center_taper)
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
    # Speed-banded feedforward (kfBP/kfV). When set (baked-tune cars) kf is interpolated by speed
    # like kp/ki; when empty, fall back to the scalar kf above. getattr stays safe against a stale
    # capnp that predates the kfBP/kfV fields.
    self.kf_bp = list(getattr(CP.lateralTuning.pid, "kfBP", []) or [])
    self.kf_v = list(getattr(CP.lateralTuning.pid, "kfV", []) or [])
    self.CI = CI
    self.get_steer_feedforward = CI.get_steer_feedforward_function()

    self.is_eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    # Baked-tune cars carry their full per-band P/I/F tune in interface.py, so the UI scale sliders
    # are forced neutral (1.0) for them in update() -- the tune lives in the base, not the scales.
    self.lat_tune_baked = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.LAT_TUNE_BAKED.value)
    # Live-tunable center boost (replaces the old per-car lookup). Static across
    # all speeds; active only within the Center Boost Threshold of dead-center.
    self.center_taper_high = 0.5
    self.center_boost_threshold = 3.0
    self.center_boost_min_speed = 50.0  # mph; below this (with a short ramp) center boost is gated off
    # Unwind FF boost: peak multiplier (strongest at a standstill) + a real time cap that
    # holds the boost only for the first N seconds of each unwind, then fades it out.
    self.dt = dt
    self.unwind_ff_multiplier = 2.0
    self.unwind_boost_cap_s = 1.0
    self.unwind_boost_elapsed = 0.0
    # Rate damping (the missing "D"): live-tunable strength (0 = off) and the speed at which
    # it fades out (above which tire self-aligning torque damps the steering on its own).
    self.rate_damping_scale = 0.0
    self.rate_damping_fade_speed_ms = 30.0 * _MPH_TO_MS

    self.eps_modified_steering_pressed_filter_s = 0.0
    self.eps_modified_steering_pressed_prev = False
    self.center_taper_scale = FirstOrderFilter(1.0, CENTER_TAPER_FADE_TAU, dt)
    self.prev_output_torque = 0.0
    self.prev_angle_steers_des_no_offset = 0.0
    self.params = Params()
    self.frame = -1
    # Independent speed-banded P / I / F output scales (multiplier units; 1.0 = neutral).
    self.lat_p_scale_low = 1.0
    self.lat_p_scale_standard = 1.0
    self.lat_p_scale_highway = 1.0
    self.lat_i_scale_low = 1.0
    self.lat_i_scale_standard = 1.0
    self.lat_i_scale_highway = 1.0
    self.lat_f_scale_low = 1.0
    self.lat_f_scale_standard = 1.0
    self.lat_f_scale_highway = 1.0
    self.unwind_freeze_enabled = False
    self.unwind_lookahead_enabled = False
    self.injection_test_enabled = False  # Party Tricks: x9.99 PID scale stress test
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
      self.unwind_boost_elapsed = 0.0
    else:
      desired_angle_delta = angle_steers_des_no_offset - self.prev_angle_steers_des_no_offset
      phase = angle_steers_des_no_offset * desired_angle_delta

      # Offset does not contribute to resistive torque. Speed-banded kf (kfBP/kfV) when present,
      # else the scalar kf.
      ff_factor = float(np.interp(CS.vEgo, self.kf_bp, self.kf_v)) if self.kf_v else self.ff_factor
      ff = ff_factor * self.get_steer_feedforward(angle_steers_des_no_offset, CS.vEgo)
      ff_scale = 1.0

      # Low-speed unwind needs extra feedforward to overcome EPS/tire stiction. The peak
      # multiplier is live-tunable and fades to 1x (no boost) by ~22 mph; a separate time
      # cap (applied below) limits how long the boost is held into each unwind.
      unwind_ff_boost = float(np.interp(CS.vEgo, [0.0, 10.0], [self.unwind_ff_multiplier, 1.0]))

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

      # Time cap: hold the boost only for the first unwind_boost_cap_s of each unwind event.
      # Accumulate elapsed while the (pre-cap) unwind weight is active and reset when the
      # unwind ends, so the timer tracks the real event; fade out over UNWIND_BOOST_FADE_S
      # approaching the cap so the boost doesn't drop as a torque step. cap == 0 -> no boost.
      if ff_unwind_weight > 0.0:
        self.unwind_boost_elapsed += self.dt
      else:
        self.unwind_boost_elapsed = 0.0
      if self.unwind_boost_cap_s > 0.0:
        fade = min(UNWIND_BOOST_FADE_S, self.unwind_boost_cap_s)
        time_gate = min(max((self.unwind_boost_cap_s - self.unwind_boost_elapsed) / fade, 0.0), 1.0)
      else:
        time_gate = 0.0
      ff_unwind_weight *= time_gate

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

      # Derivative Tuning Experiment: force the integrator off during ANY winddown (phase < 0),
      # independent of the opt-in freeze above. Pullback is exactly what we want here; I fights it.
      if phase < 0.0:
        freeze_integrator = True

      self.frame += 1
      if self.frame % 300 == 0:
        # Independent speed-banded P / I / F scales. default/min/max are runtime
        # multipliers; scale converts the stored percent (100 -> 1.0x). Band selection
        # by vEgo happens every frame below. Defaults preserve the prior P+I = 100/135/200
        # tune (split equally across P and I) with feedforward left static (F = 100%).
        self.lat_p_scale_low = get_param_float(self.params, "LatPScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_p_scale_standard = get_param_float(self.params, "LatPScaleStandard", 1.35, 0.0, 5.0, scale=100.0)
        self.lat_p_scale_highway = get_param_float(self.params, "LatPScaleHighway", 2.0, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_low = get_param_float(self.params, "LatIScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_standard = get_param_float(self.params, "LatIScaleStandard", 1.35, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_highway = get_param_float(self.params, "LatIScaleHighway", 2.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_low = get_param_float(self.params, "LatFScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_standard = get_param_float(self.params, "LatFScaleStandard", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_highway = get_param_float(self.params, "LatFScaleHighway", 1.0, 0.0, 5.0, scale=100.0)
        # Center boost target. FLOAT param stored as the real value
        # (UI use_float_scaling), so no scale. Unset -> 0.5 (old generic default).
        self.center_taper_high = get_param_float(
          self.params,
          "HondaCenterScale",
          0.5,
          0.0,
          5.0,
        )
        # Degrees from dead-center within which the center boost is active.
        self.center_boost_threshold = get_param_float(
          self.params,
          "HondaCenterBoostThreshold",
          3.0,
          0.0,
          10.0,
        )
        # mph floor below which center boost is disabled (low-speed center-oscillation fix).
        self.center_boost_min_speed = get_param_float(
          self.params,
          "HondaCenterBoostMinSpeed",
          50.0,
          0.0,
          90.0,
        )
        self.unwind_freeze_enabled = self.params.get_bool("HondaUnwindFreeze")
        self.unwind_lookahead_enabled = self.params.get_bool("HondaUnwindLookahead")
        # Unwind FF boost: peak multiplier + time cap (both FLOAT, stored as real values).
        self.unwind_ff_multiplier = get_param_float(self.params, "HondaUnwindFfMultiplier", 2.0, 1.0, 10.0)
        self.unwind_boost_cap_s = get_param_float(self.params, "HondaUnwindBoostSeconds", 1.0, 0.0, 3.0)
        # Rate damping (D): strength (stored 0-300% -> 0.0-3.0) and fade-out speed (mph).
        self.rate_damping_scale = get_param_float(self.params, "NrdrLatRateDamping", 0.0, 0.0, 3.0, scale=100.0)
        self.rate_damping_fade_speed_ms = get_param_float(self.params, "NrdrLatRateDampingFadeSpeed", 30.0, 0.0, 60.0) * _MPH_TO_MS
        self.injection_test_enabled = self.params.get_bool("HondaInjectionTest")

      output_torque = self.pid.update(
        error,
        feedforward=ff,
        speed=CS.vEgo,
        freeze_integrator=freeze_integrator,
      )

      # Independently scale each PID term by its own speed-banded multiplier (P / I / F).
      # Preserve-tune defaults (P=I per band, F=1.0) reproduce the prior single P+I scale.
      # Baked-tune cars carry the full per-band tune in interface.py, so their sliders are forced
      # neutral here -- the tune stands on the base alone (and ignores any stale stored scales).
      if self.lat_tune_baked:
        p_scale = i_scale = f_scale = 1.0
      else:
        p_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_p_scale_low, self.lat_p_scale_standard, self.lat_p_scale_highway)
        i_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_i_scale_low, self.lat_i_scale_standard, self.lat_i_scale_highway)
        f_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_f_scale_low, self.lat_f_scale_standard, self.lat_f_scale_highway)
      output_torque = self.pid.p * p_scale + self.pid.i * i_scale + self.pid.d + self.pid.f * f_scale

      # Party Tricks: Injection Test multiplies the PID scale by 999% (diagnostic only).
      if self.injection_test_enabled:
        output_torque *= 9.99

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
          self.center_boost_threshold,
          self.center_boost_min_speed * _MPH_TO_MS,
        )

        # Rate damping (the missing "D"): torque opposing how fast the wheel is moving, applied
        # after the output scale so it's a clean physical term. Strongest at low speed (where the
        # plant is an undamped double integrator) and faded to zero by rate_damping_fade_speed,
        # where tire self-aligning torque resumes damping. Relies on this EPS being precise + low-lag.
        rate_damp_fade = 0.0
        if self.rate_damping_fade_speed_ms > 0.0:
          rate_damp_fade = min(max((self.rate_damping_fade_speed_ms - CS.vEgo) / self.rate_damping_fade_speed_ms, 0.0), 1.0)
        # Unwind/angle scheduling: during winddown, D resists the pullback we want at high angle
        # but helps the wheel settle at center, so fade D out above D_UNWIND_FADE_ANGLE and in
        # below it. Blend by the unwind phase weight so D doesn't step when phase crosses zero;
        # full D for normal driving and windup.
        unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)
        d_angle_fade = min(max((D_UNWIND_FADE_ANGLE - abs(CS.steeringAngleDeg)) / D_UNWIND_FADE_ANGLE, 0.0), 1.0)
        d_unwind_factor = (1.0 - unwind_weight) + unwind_weight * d_angle_fade
        output_torque += -self.rate_damping_scale * RATE_DAMPING_REF * float(CS.steeringRateDeg) * rate_damp_fade * d_unwind_factor

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
