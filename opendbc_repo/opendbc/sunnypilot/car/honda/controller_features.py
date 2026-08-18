import math
import time

import numpy as np

from opendbc.car import DT_CTRL, rate_limit, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import HONDA_BOSCH
from opendbc.sunnypilot.car.honda.live_params import get_honda_live_params
from opendbc.sunnypilot.car.honda.longitudinal import HondaParamWriter, LongGasLearner, load_factors


def get_param_bool(params, key, default=False):
  value = params.get(key)
  if value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def get_param_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  value = params.get(key)
  try:
    if isinstance(value, bytes):
      value = value.decode("utf-8")
    result = default if value is None else float(value) / scale
  except (AttributeError, TypeError, ValueError):
    result = default
  if min_value is not None:
    result = max(min_value, result)
  if max_value is not None:
    result = min(max_value, result)
  return result


def initialize_live_learning_gas(params, enable_gas_interceptor: bool) -> None:
  if params.get("HondaLiveLearningGas", return_default=False) is None:
    params.put_bool("HondaLiveLearningGas", not enable_gas_interceptor, block=True)


def torque_lpf_tau(v_ego: float, low_tau: float, standard_tau: float, highway_tau: float) -> float:
  if v_ego < 25.0 * CV.MPH_TO_MS:
    return low_tau
  if v_ego < 50.0 * CV.MPH_TO_MS:
    return standard_tau
  return highway_tau


class HondaControllerFeatures:
  replaces_longitudinal = True

  def __init__(self, CP, CP_SP):
    from openpilot.common.params import Params

    self.CP = CP
    self.CP_SP = CP_SP
    initialize_live_learning_gas(Params(), CP_SP.enableGasInterceptor)
    self.params = get_honda_live_params()
    self.param_writer = HondaParamWriter()
    self._live_generation = -1
    self._live = {}

    gas_factor, wind_factor = load_factors(CP.carFingerprint)
    self.learner = LongGasLearner(gas_factor, wind_factor, CP.carFingerprint)

    self.system_flash_until = 0.0
    self.previous_set_speed = None
    self.last_cruise_button_time = -1e9
    self.torque_lpf = 0.0
    self.override_ramp = 1.0
    self.lat_active_previous = False
    self.steering_pressed_filter = 0.0
    self.steering_pressed_previous = False
    self.last_accel = 0.0
    self.last_accel_sign = 0
    self.sign_change_frames = 0

  @property
  def longitudinal_factors(self):
    return self.learner.gasfactor, self.learner.windfactor

  def live_tuning(self):
    snapshot = self.params.snapshot
    if snapshot.generation != self._live_generation:
      self._live = {
        "override_fade_down_s": get_param_float(snapshot, "HondaOverrideFadeDownSecs", 0.1, 0.0, 10.0),
        "override_fade_up_s": get_param_float(snapshot, "HondaOverrideFadeUpSecs", 0.1, 0.0, 10.0),
        "override_torque_scale": get_param_float(snapshot, "HondaOverrideTorqueScale", 0.0, 0.0, 100.0, scale=100.0),
        "driver_assist_during_override": get_param_bool(snapshot, "HondaDriverAssistDuringOverride", True),
        "live_learning_gas": get_param_bool(snapshot, "HondaLiveLearningGas", not self.CP_SP.enableGasInterceptor),
        "torque_lpf_enabled": get_param_bool(snapshot, "HondaTorqueLowPassFilter", True),
        "lpf_tau_low": get_param_float(snapshot, "HondaLpfTauLowSpeed", 0.1, 0.0, 5.0),
        "lpf_tau_standard": get_param_float(snapshot, "HondaLpfTauStandard", 0.1, 0.0, 5.0),
        "lpf_tau_highway": get_param_float(snapshot, "HondaLpfTauHighway", 0.1, 0.0, 5.0),
        "steer_delta_limiter_enabled": get_param_bool(snapshot, "HondaSteerDeltaLimiter", False),
        "steer_delta_up": get_param_float(snapshot, "HondaSteerDeltaUp", 3.0, 0.0, 100.0),
        "steer_delta_down": get_param_float(snapshot, "HondaSteerDeltaDown", 3.0, 0.0, 100.0),
        "stopping_decel_rate": get_param_float(snapshot, "HondaStoppingDecelRate", 0.3, 0.0, 1.0, scale=100.0),
        "increase_override_tolerance": get_param_bool(snapshot, "NrdrIncreaseOverrideTolerance", False),
        "alt_dashboard_speed": int(get_param_float(snapshot, "HondaAltDashboardSpeed", 0.0, 0.0, 3.0)),
        "alt_dashboard_distance": int(get_param_float(snapshot, "HondaAltDashboardDistance", 0.0, 0.0, 2.0)),
        "clear_dash_faults": get_param_bool(snapshot, "NrdrClearDashFaults", True),
        "spoof_camera_messages": get_param_bool(snapshot, "HondaSpoofCameraMessages", False),
        "sub_mode_enabled": get_param_bool(snapshot, "NrdrCruiseButtonSubMode", False),
        "sub_mode_until": get_param_float(snapshot, "NrdrHudSubModeUntil", 0.0, 0.0),
        "ecu_matched_long": get_param_bool(snapshot, "NrdrHondaEcuMatchedLong", False),
        "full_brake_authority": get_param_bool(snapshot, "NrdrHondaFullBrakeAuthority", True),
        "roen_acceleration_limits": get_param_bool(snapshot, "NrdrRoenAccelerationLimits", True),
      }
      self._live_generation = snapshot.generation
    return self._live

  def update_system_speed_flash(self, CC, CS, hud_control):
    now = time.monotonic()
    cruise_buttons = (structs.CarState.ButtonEvent.Type.accelCruise, structs.CarState.ButtonEvent.Type.decelCruise)
    if any(event.pressed and event.type in cruise_buttons for event in CS.out.buttonEvents):
      self.last_cruise_button_time = now

    set_speed = hud_control.setSpeed if hud_control.speedVisible else None
    externally_changed = (
      set_speed is not None
      and self.previous_set_speed is not None
      and set_speed != self.previous_set_speed
      and CC.enabled
      and now - self.last_cruise_button_time > 0.7
    )
    if externally_changed:
      self.system_flash_until = now + 5.0
    self.previous_set_speed = set_speed

  def hud_sub_mode_state(self, live):
    now = time.monotonic()
    sub_mode_active = live["sub_mode_enabled"] and live["sub_mode_until"] > now
    system_flash_active = self.system_flash_until > now
    if not sub_mode_active and not system_flash_active:
      return False, False, True

    remaining = min(
      live["sub_mode_until"] - now if sub_mode_active else math.inf,
      self.system_flash_until - now if system_flash_active else math.inf,
    )
    phase_ms = 500.0 if remaining <= 5.0 else 1000.0
    blink_on = now * 1000.0 % (2.0 * phase_ms) < phase_ms
    return sub_mode_active, system_flash_active, blink_on

  def _filtered_steering_pressed(self, CS, torque_command: float) -> bool:
    if not CS.out.steeringPressed:
      self.steering_pressed_filter = 0.0
      self.steering_pressed_previous = False
      return False

    steering_torque = float(getattr(CS.out, "steeringTorque", 0.0))
    immediate = self.steering_pressed_previous or abs(torque_command) < 0.10 or steering_torque * torque_command < 0.0
    if immediate:
      self.steering_pressed_filter = 1.0
      self.steering_pressed_previous = True
      return True

    self.steering_pressed_filter = min(1.0, self.steering_pressed_filter + DT_CTRL)
    self.steering_pressed_previous = self.steering_pressed_filter >= 0.28
    return self.steering_pressed_previous

  def update_steering_torque(self, CC, CS, live, previous_torque: float):
    torque_command = float(CC.actuators.torque) if CC.latActive else 0.0
    steering_pressed = False
    if CC.latActive:
      steering_pressed = (
        self._filtered_steering_pressed(CS, torque_command)
        if live["increase_override_tolerance"]
        else bool(CS.out.steeringPressed)
      )
      if not self.lat_active_previous:
        self.override_ramp = 0.0

      if steering_pressed:
        fade_seconds = live["override_fade_down_s"]
        minimum = live["override_torque_scale"]
        self.override_ramp = minimum if fade_seconds <= 0.0 else max(minimum, self.override_ramp - DT_CTRL / fade_seconds)
      else:
        fade_seconds = live["override_fade_up_s"]
        self.override_ramp = 1.0 if fade_seconds <= 0.0 else min(1.0, self.override_ramp + DT_CTRL / fade_seconds)

      torque_command *= self.override_ramp
      if live["torque_lpf_enabled"]:
        tau = torque_lpf_tau(CS.out.vEgo, live["lpf_tau_low"], live["lpf_tau_standard"], live["lpf_tau_highway"])
        alpha = DT_CTRL / (tau + DT_CTRL)
        self.torque_lpf = alpha * torque_command + (1.0 - alpha) * self.torque_lpf
        torque_command = self.torque_lpf
      else:
        self.torque_lpf = torque_command
    else:
      self.override_ramp = 0.0
      self.torque_lpf = 0.0
      self.steering_pressed_filter = 0.0
      self.steering_pressed_previous = False

    if live["steer_delta_limiter_enabled"]:
      torque_command = rate_limit(
        torque_command,
        previous_torque,
        -live["steer_delta_down"] * DT_CTRL,
        live["steer_delta_up"] * DT_CTRL,
      )

    self.lat_active_previous = CC.latActive
    lkas_active = (
      CC.latActive
      and (not live["driver_assist_during_override"] or not steering_pressed)
    )
    return torque_command, lkas_active

  def nidec_accel_command(self, accel: float, enabled: bool) -> float:
    if enabled:
      accel = float(np.clip(accel, self.last_accel - 0.06, self.last_accel + 0.05))
    self.last_accel = accel
    return accel

  def nidec_gas_brake(self, accel: float, gas: float, brake: float, v_ego: float, enabled: bool):
    if not enabled:
      return gas, brake

    deadband = float(np.interp(v_ego, [2.5, 10.0, 20.0, 30.0], [0.08, 0.06, 0.03, 0.005]))
    if gas < deadband and brake < deadband:
      gas = brake = 0.0

    sign = 1 if accel > 0.05 else (-1 if accel < -0.05 else 0)
    if sign and self.last_accel_sign and sign != self.last_accel_sign:
      self.sign_change_frames = 20
    if self.sign_change_frames:
      gas = brake = 0.0
      self.sign_change_frames -= 1
    if sign:
      self.last_accel_sign = sign
    return gas, brake

  def nidec_brake_authority(self, accel: float, brake: float, v_ego: float, enabled: bool) -> float:
    if not enabled or self.CP.carFingerprint in HONDA_BOSCH:
      return brake
    creep_brake = np.interp(v_ego, [0.0, 2.3], [0.15, 0.0]) if v_ego < 2.3 else 0.0
    return float(np.clip(-accel / 4.0 + creep_brake, 0.0, 1.0))

  @staticmethod
  def nidec_brake_command(brake: float, wind_brake: float, full_authority: bool) -> float:
    wind_compensation = wind_brake if not full_authority or brake <= 0.95 else 0.0
    return float(np.clip(brake - wind_compensation, 0.0, 1.0))

  def update_bosch_learner(self, CC, CS, actuators, accel: float, gas_pedal_force: float,
                           wind_brake: float, pitch: float, car_params, learning_enabled: bool):
    if learning_enabled:
      self.learner.update(
        accel_cmd=accel,
        a_ego=CS.out.aEgo,
        gas_pedal_force=gas_pedal_force,
        wind_brake_ms2=wind_brake,
        long_active=CC.longActive,
        long_pid=actuators.longControlState == structs.CarControl.Actuators.LongControlState.pid,
        gas_pressed=CS.out.gasPressed,
        brake_pressed=CS.out.brakePressed,
        v_ego=CS.out.vEgo,
        at_standstill=CS.out.vEgo <= 0.0,
        pitch=pitch,
        brake_addon=0.0,
        at_accel_max=gas_pedal_force >= car_params.BOSCH_ACCEL_MAX,
      )
    return self.longitudinal_factors

  def update_nidec_learner(self, CC, CS, actuators, gas: float, brake: float, wind_brake: float,
                           pitch: float, enabled: bool):
    if enabled:
      self.learner.update(
        accel_cmd=actuators.accel,
        a_ego=CS.out.aEgo,
        gas_pedal_force=gas,
        wind_brake_ms2=wind_brake * 4.8,
        long_active=CC.longActive,
        long_pid=actuators.longControlState == structs.CarControl.Actuators.LongControlState.pid,
        gas_pressed=CS.out.gasPressed,
        brake_pressed=CS.out.brakePressed,
        v_ego=CS.out.vEgo,
        at_standstill=CS.out.vEgo <= 0.0,
        pitch=pitch,
        brake_addon=0.0,
        at_accel_max=gas >= 1.0,
      )
    return gas * self.learner.gasfactor

  def nidec_hud_options(self, CC, CS, hud_control, live):
    speed_factor = CS.v_cruise_factor or 1.0
    sub_mode_active, system_flash_active, blink_on = self.hud_sub_mode_state(live)
    return {
      "speed_design": live["alt_dashboard_speed"],
      "distance_design": live["alt_dashboard_distance"],
      "sub_mode_active": sub_mode_active,
      "blink_on": blink_on,
      "max_flash_active": system_flash_active,
      "lead_speed_display": hud_control.leadVLead / speed_factor,
      "gps_speed_display": CS.out.vEgo / speed_factor,
      "cluster_speed_display": (CS.out.vEgoCluster or CS.out.vEgo) / speed_factor,
      "vehicle_accel": CS.out.aEgo,
      "clear_dash_faults": live["clear_dash_faults"],
    }

  def reset_longitudinal(self):
    self.last_accel = 0.0
    self.last_accel_sign = 0
    self.sign_change_frames = 0

  def persist(self):
    self.param_writer.put_many({
      "HondaGasFactorParams": self.learner.raw_gasfactor,
      "HondaWindFactorParams": self.learner.raw_windfactor,
    }, self.CP.carFingerprint)
