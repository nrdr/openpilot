import math

import numpy as np

from openpilot.cereal import log
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.pid import PIDController
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.sunnypilot.nrdr.lat_stiction import LatStiction
from openpilot.sunnypilot.nrdr.tune_learner import TuneLearner
from openpilot.sunnypilot.nrdr.params import read_bool, read_float
from openpilot.sunnypilot.nrdr.phase_detector import phase_with_latch
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import get_steer_ratio_endpoint_profile


MPH_TO_MS = 0.44704
LOW_SPEED_MAX = 25.0 * MPH_TO_MS
STANDARD_SPEED_MAX = 50.0 * MPH_TO_MS
CENTER_TAPER_FADE_TAU = 0.25
CENTER_BOOST_SPEED_FADE = 5.0 * MPH_TO_MS
RATE_DAMPING_REFERENCE = 0.010
RATE_DAMPING_UNWIND_ANGLE = 30.0
SETTINGS_REFRESH_FRAMES = 300


def _speed_banded_value(v_ego: float, low: float, standard: float, highway: float) -> float:
  if v_ego < LOW_SPEED_MAX:
    return low
  if v_ego < STANDARD_SPEED_MAX:
    return standard
  return highway


def _eps_modified_steering_pressed(raw_pressed, steering_torque: float, torque_command: float,
                                   filter_seconds: float, previous_pressed: bool) -> tuple[float, bool]:
  if not raw_pressed:
    return 0.0, False
  if previous_pressed or abs(torque_command) < 0.10 or steering_torque * torque_command < 0.0:
    return 1.0, True
  filter_seconds = min(1.0, filter_seconds + DT_CTRL)
  return filter_seconds, filter_seconds >= 0.28


def _center_boost(angle: float, v_ego: float, fade: float, magnitude: float,
                  threshold: float, minimum_speed: float) -> float:
  angle_weight = np.clip(threshold + 1.0 - abs(angle), 0.0, 1.0)
  speed_weight = np.clip((v_ego - minimum_speed) / CENTER_BOOST_SPEED_FADE, 0.0, 1.0) if minimum_speed > 0.0 else 1.0
  return 1.0 + angle_weight * magnitude * fade * speed_weight


def _output_scale(angle: float, phase: float, steering_rate: float, v_ego: float, enabled: bool) -> float:
  if not enabled:
    return 1.0

  abs_angle = abs(angle)
  speed_weight = np.clip((v_ego - 4.0) / 10.0, 0.0, 1.0)
  mid_turn_weight = np.clip((abs_angle - 10.0) / 10.0, 0.0, 1.0)
  angle_weight = np.clip((abs_angle - 16.0) / 12.0, 0.0, 1.0)
  is_left = angle > 0.0

  low_speed_weight = np.clip(1.0 - v_ego / (15.0 * MPH_TO_MS), 0.0, 1.0)
  low_speed_unwind = low_speed_weight > 0.0 and angle * steering_rate < -1.0
  mid_turn_scale = 0.1200 if is_left else 0.0150
  mid_turn_turn_in_scale = -0.5500 if is_left else -0.0524
  mid_turn_unwind_scale = -0.0743 if is_left else -0.0842
  base_scale = 0.0722 if is_left else 0.0972
  turn_in_scale = -0.0799 if is_left else 0.0888
  unwind_scale = 0.1600 if is_left else 0.2000

  scale = 1.0 + speed_weight * mid_turn_weight * mid_turn_scale + speed_weight * angle_weight * base_scale
  turn_in_weight = np.clip(phase / 0.5, 0.0, 1.0)
  unwind_weight = np.clip(-phase / 0.5, 0.0, 1.0)
  if low_speed_unwind and speed_weight < 0.1:
    scale += low_speed_weight * mid_turn_weight * 0.18
  else:
    scale += speed_weight * mid_turn_weight * (turn_in_weight * mid_turn_turn_in_scale + unwind_weight * mid_turn_unwind_scale)
    scale += speed_weight * angle_weight * (turn_in_weight * turn_in_scale - unwind_weight * unwind_scale)
  return max(scale, 0.6863)


class NrdrLatControlPID(LatControl):
  @staticmethod
  def supports(CP, CP_SP) -> bool:
    fingerprint = str(CP.carFingerprint)
    eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    return eps_modified or get_steer_ratio_endpoint_profile(fingerprint) is not None

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    self.pid = PIDController(
      (CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
      (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
      pos_limit=self.steer_max,
      neg_limit=-self.steer_max,
    )
    self.ff_factor = CP.lateralTuning.pid.kf
    self.kf_bp = list(getattr(CP.lateralTuning.pid, "kfBP", []) or [])
    self.kf_v = list(getattr(CP.lateralTuning.pid, "kfV", []) or [])
    self.get_steer_feedforward = CI.get_steer_feedforward_function()
    self.is_eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    self.dt = dt
    self.params = Params()
    self.sr_profile = get_steer_ratio_endpoint_profile(str(CP.carFingerprint))
    self.sr_values = list(self.sr_profile.default_values) if self.sr_profile else None
    self.lane_change_endpoint_sr = read_bool(self.params, "NrdrLaneChangeEndpointSteerRatio", True)
    self.center_boost_magnitude = 0.5
    self.center_boost_threshold = 3.0
    self.center_boost_min_speed = 50.0
    self.center_taper = FirstOrderFilter(1.0, CENTER_TAPER_FADE_TAU, dt)
    self.rate_damping = 0.3
    self.rate_damping_fade_speed = 30.0 * MPH_TO_MS
    self.p_scales = [1.0, 1.0, 1.0]
    self.i_scales = [1.0, 1.0, 1.0]
    self.f_scales = [1.0, 1.0, 1.0]
    self.injection_test = False
    self.starpilot = False
    self.stiction_enabled = False
    self.stiction = LatStiction(dt, self.steer_max)
    self.tune_learner = TuneLearner(dt, self.steer_max)
    self.frame = -1
    self.previous_output = 0.0
    self.previous_desired_angle = 0.0
    self.previous_saturated = False
    self.steering_pressed_duration = 0.0
    self.previous_steering_pressed = False
    self.model_v2 = None
    self.phase_direction = 0.0

  def update_model_v2(self, model_v2) -> None:
    self.model_v2 = model_v2

  def _lane_change_active(self) -> bool:
    return self.model_v2 is not None and self.model_v2.meta.laneChangeState != log.LaneChangeState.off

  def _desired_angles(self, VM, CS, params, desired_curvature):
    if self.sr_profile is not None:
      VM.sR = self.sr_values[-1] if self.lane_change_endpoint_sr and self._lane_change_active() else float(
        np.interp(abs(CS.steeringAngleDeg), self.sr_profile.breakpoints, self.sr_values)
      )
    angle_no_offset = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))
    return angle_no_offset, angle_no_offset + params.angleOffsetDeg

  def _reset(self, desired_angle: float) -> None:
    self.steering_pressed_duration = 0.0
    self.previous_steering_pressed = False
    self.center_taper.x = 1.0
    self.previous_output = 0.0
    self.previous_desired_angle = desired_angle
    self.previous_saturated = False
    self.stiction.reset()

  def _feedforward(self, CS, desired_angle: float) -> float:
    factor = float(np.interp(CS.vEgo, self.kf_bp, self.kf_v)) if self.kf_v else self.ff_factor
    return factor * self.get_steer_feedforward(desired_angle, CS.vEgo)

  def _steering_pressed(self, CS) -> bool:
    steering_pressed = bool(CS.steeringPressed)
    if self.is_eps_modified:
      self.steering_pressed_duration, steering_pressed = _eps_modified_steering_pressed(
        steering_pressed,
        float(getattr(CS, "steeringTorque", 0.0)),
        self.previous_output,
        self.steering_pressed_duration,
        self.previous_steering_pressed,
      )
      self.previous_steering_pressed = steering_pressed
    return steering_pressed

  def _refresh_settings(self) -> None:
    scale_keys = (
      (self.p_scales, "LatPScale"),
      (self.i_scales, "LatIScale"),
      (self.f_scales, "LatFScale"),
    )
    for values, prefix in scale_keys:
      values[:] = [
        read_float(self.params, f"{prefix}LowSpeed", 1.0, 0.0, 5.0, scale=100.0),
        read_float(self.params, f"{prefix}Standard", 1.0, 0.0, 5.0, scale=100.0),
        read_float(self.params, f"{prefix}Highway", 1.0, 0.0, 5.0, scale=100.0),
      ]
    self.center_boost_magnitude = read_float(self.params, "HondaCenterScale", 0.5, 0.0, 5.0)
    self.center_boost_threshold = read_float(self.params, "HondaCenterBoostThreshold", 3.0, 0.0, 10.0)
    self.center_boost_min_speed = read_float(self.params, "HondaCenterBoostMinSpeed", 50.0, 0.0, 90.0)
    self.rate_damping = read_float(self.params, "NrdrLatRateDamping", 0.3, 0.0, 3.0, scale=100.0)
    self.rate_damping_fade_speed = read_float(self.params, "NrdrLatRateDampingFadeSpeed", 30.0, 0.0, 60.0) * MPH_TO_MS
    self.injection_test = read_bool(self.params, "HondaInjectionTest")
    self.starpilot = read_bool(self.params, "NrdrStarPilotPid")
    self.stiction_enabled = read_bool(self.params, "NrdrLatStiction")
    if self.sr_profile is not None:
      self.sr_values[:] = [read_float(self.params, key, default, 8.0, 25.0) for key, default in self.sr_profile.param_values]
      self.lane_change_endpoint_sr = read_bool(self.params, "NrdrLaneChangeEndpointSteerRatio", True)

  def _scaled_pid_output(self, CS, desired_angle: float, angle_delta: float, phase: float) -> float:
    p_term = self.pid.p * _speed_banded_value(CS.vEgo, *self.p_scales)
    i_term = self.pid.i * _speed_banded_value(CS.vEgo, *self.i_scales)
    f_term = self.pid.f * _speed_banded_value(CS.vEgo, *self.f_scales)
    if self.is_eps_modified:
      center_fade = 0.0 if (bool(getattr(CS, "leftBlinker", False)) or bool(getattr(CS, "rightBlinker", False))) else float(
        self.center_taper.update(1.0)
      )
      if center_fade == 0.0:
        self.center_taper.x = 0.0
      p_term *= _center_boost(
        desired_angle,
        CS.vEgo,
        center_fade,
        self.center_boost_magnitude,
        self.center_boost_threshold,
        self.center_boost_min_speed * MPH_TO_MS,
      )
    output = p_term + i_term + self.pid.d + f_term
    if self.injection_test:
      output *= 9.99
    if self.is_eps_modified:
      output *= _output_scale(desired_angle, phase, float(CS.steeringRateDeg), CS.vEgo, self.starpilot)
      speed_fade = float(np.clip((self.rate_damping_fade_speed - CS.vEgo) / self.rate_damping_fade_speed, 0.0, 1.0)) \
        if self.rate_damping_fade_speed > 0.0 else 0.0
      unwind_weight = float(np.clip(-phase / 0.5, 0.0, 1.0))
      angle_fade = float(np.clip((RATE_DAMPING_UNWIND_ANGLE - abs(CS.steeringAngleDeg)) / RATE_DAMPING_UNWIND_ANGLE, 0.0, 1.0))
      unwind_factor = 1.0 - unwind_weight + unwind_weight * angle_fade
      output -= self.rate_damping * RATE_DAMPING_REFERENCE * float(CS.steeringRateDeg) * speed_fade * unwind_factor
    return output

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)
    desired_no_offset, desired_angle = self._desired_angles(VM, CS, params, desired_curvature)
    error = desired_angle - CS.steeringAngleDeg
    pid_log.steeringAngleDesiredDeg = desired_angle
    pid_log.angleError = error

    if not active:
      output_torque = 0.0
      pid_log.active = False
      self._reset(desired_no_offset)
    else:
      angle_delta = desired_no_offset - self.previous_desired_angle
      phase, self.phase_direction = phase_with_latch(desired_no_offset, angle_delta, CS.vEgo, self.phase_direction)
      feedforward = self._feedforward(CS, desired_no_offset)
      steering_pressed = self._steering_pressed(CS)
      freeze_speed = 2.0 if self.is_eps_modified else 5.0
      freeze_integrator = steer_limited_by_safety or steering_pressed or CS.vEgo < freeze_speed
      if phase < 0.0 and self.pid.i * error > 0.0:
        freeze_integrator = True

      self.frame += 1
      if self.frame % SETTINGS_REFRESH_FRAMES == 0:
        self._refresh_settings()
      self.pid.update(error, feedforward=feedforward, speed=CS.vEgo, freeze_integrator=freeze_integrator)
      output_torque = self._scaled_pid_output(CS, desired_no_offset, angle_delta, phase)
      if self.is_eps_modified:
        output_torque += self.tune_learner.apply(CS.vEgo, desired_angle, error)
        output_torque = float(np.clip(output_torque, -self.steer_max, self.steer_max))
        params_valid = bool(params.valid and params.angleOffsetValid and params.steerRatioValid and params.stiffnessFactorValid)
        self.tune_learner.learn(
          CS.vEgo, desired_angle, error, float(CS.steeringRateDeg), steering_pressed, params_valid, self.frame,
        )

      lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
      if self.stiction_enabled:
        output_torque = float(self.stiction.update(
          active,
          CS.vEgo,
          error,
          angle_delta / self.dt,
          float(CS.steeringRateDeg),
          output_torque,
          steering_pressed,
          lane_change,
          self.previous_saturated,
        ))
      else:
        self.stiction.reset()

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
      self.previous_output = float(output_torque)
      self.previous_desired_angle = desired_no_offset
      self.previous_saturated = bool(pid_log.saturated)

    return output_torque, desired_angle, pid_log
