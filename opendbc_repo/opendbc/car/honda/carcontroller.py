import math
import threading
import time
from queue import Empty, Queue

import numpy as np
from openpilot.common.params import Params

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import CAR, CruiseButtons, HONDA_BOSCH, HONDA_BOSCH_CANFD, HONDA_BOSCH_RADARLESS, \
                                     HONDA_BOSCH_TJA_CONTROL, HONDA_NIDEC_ALT_PCM_ACCEL, CarControllerParams
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.common.pid import PIDController

from opendbc.sunnypilot.car.honda.mads import MadsCarController
from opendbc.sunnypilot.car.honda.gas_interceptor import GasInterceptorCarController
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState


def get_param_bool(params, key, default=False):
  value = params.get(key)
  if value is None:
    return default
  return params.get_bool(key)


def get_param_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  value = params.get(key)
  if value is None:
    ret = default
  else:
    try:
      # sunnypilot Params.get() auto-casts by declared key type, so INT/FLOAT params
      # come back as python numbers (not bytes). Handle bytes/str/number uniformly.
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


def compute_gb_honda_bosch(accel, speed):
  # TODO returns 0s, is unused
  return 0.0, 0.0


def compute_gb_honda_nidec(accel, speed):
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / 4.8 - creep_brake
  return np.clip(gb, 0.0, 1.0), np.clip(-gb, 0.0, 1.0)


def compute_gas_brake(accel, speed, fingerprint):
  if fingerprint in HONDA_BOSCH:
    return compute_gb_honda_bosch(accel, speed)
  else:
    return compute_gb_honda_nidec(accel, speed)


# TODO not clear this does anything useful
def actuator_hysteresis(brake, braking, brake_steady, v_ego, car_fingerprint):
  # hyst params
  brake_hyst_on = 0.02    # to activate brakes exceed this value
  brake_hyst_off = 0.005  # to deactivate brakes below this value
  brake_hyst_gap = 0.01   # don't change brake command for small oscillations within this value

  # *** hysteresis logic to avoid brake blinking. go above 0.1 to trigger
  if (brake < brake_hyst_on and not braking) or brake < brake_hyst_off:
    brake = 0.
  braking = brake > 0.

  # for small brake oscillations within brake_hyst_gap, don't change the brake command
  if brake == 0.:
    brake_steady = 0.
  elif brake > brake_steady + brake_hyst_gap:
    brake_steady = brake - brake_hyst_gap
  elif brake < brake_steady - brake_hyst_gap:
    brake_steady = brake + brake_hyst_gap
  brake = brake_steady

  return brake, braking, brake_steady


def brake_pump_hysteresis(apply_brake, apply_brake_last, last_pump_ts, ts):
  pump_on = False

  # reset pump timer if:
  # - there is an increment in brake request
  # - we are applying steady state brakes and we haven't been running the pump
  #   for more than 20s (to prevent pressure bleeding)
  if apply_brake > apply_brake_last or (ts - last_pump_ts > 20. and apply_brake > 0):
    last_pump_ts = ts

  # once the pump is on, run it for at least 0.2s
  if ts - last_pump_ts < 0.2 and apply_brake > 0:
    pump_on = True

  return pump_on, last_pump_ts


def process_hud_alert(hud_alert):
  alert_fcw = False
  alert_steer_required = False

  # Make sure FCW is prioritized over steering required
  # TODO: implement separate available LDW alert
  if hud_alert == VisualAlert.fcw:
    alert_fcw = True
  elif hud_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
    alert_steer_required = True

  return alert_fcw, alert_steer_required

def get_eps_modified_steering_pressed(raw_pressed, steering_torque, torque_cmd, filter_s, previous_pressed):
  raw_pressed = bool(raw_pressed)
  steering_torque = float(steering_torque)
  torque_cmd = float(torque_cmd)

  if not raw_pressed:
    return 0.0, False

  torque_product = steering_torque * torque_cmd
  torque_cmd_abs = abs(torque_cmd)

  if previous_pressed or torque_cmd_abs < 0.10 or torque_product < 0.0:
    return 1.0, True

  filter_s = min(1.0, filter_s + DT_CTRL)
  return filter_s, filter_s >= 0.28

def torque_lpf_tau(v_ego: float, low_tau: float, standard_tau: float, highway_tau: float) -> float:
  # Speed-banded low-pass filter time constant (seconds), fully tunable from the UI.
  if v_ego < 25.0 * CV.MPH_TO_MS:
    return low_tau
  if v_ego < 50.0 * CV.MPH_TO_MS:
    return standard_tau
  return highway_tau


def notch_biquad_coeffs(f0: float, q: float, fs: float):
  # Standard RBJ notch (band-reject) biquad. Removes a narrow band around f0 (Hz)
  # with width set by q (higher q = narrower). Near-zero phase lag away from f0,
  # so it kills a fixed EPS resonance without the broadband delay a LPF adds.
  q = max(q, 0.1)
  w0 = 2.0 * math.pi * (f0 / fs)
  cos_w0 = math.cos(w0)
  alpha = math.sin(w0) / (2.0 * q)
  b0 = 1.0
  b1 = -2.0 * cos_w0
  b2 = 1.0
  a0 = 1.0 + alpha
  a1 = -2.0 * cos_w0
  a2 = 1.0 - alpha
  return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


class NotchFilter:
  # Direct-form-II transposed biquad. Recomputes coeffs only when freq/q change.
  def __init__(self, fs: float):
    self.fs = fs
    self.f0 = 0.0
    self.q = 0.0
    self.b0 = 1.0
    self.b1 = 0.0
    self.b2 = 0.0
    self.a1 = 0.0
    self.a2 = 0.0
    self.z1 = 0.0
    self.z2 = 0.0

  def reset(self):
    self.z1 = 0.0
    self.z2 = 0.0

  def update(self, x: float, f0: float, q: float) -> float:
    if f0 != self.f0 or q != self.q:
      self.f0, self.q = f0, q
      self.b0, self.b1, self.b2, self.a1, self.a2 = notch_biquad_coeffs(f0, q, self.fs)
    y = self.b0 * x + self.z1
    self.z1 = self.b1 * x - self.a1 * y + self.z2
    self.z2 = self.b2 * x - self.a2 * y
    return y


class HondaParamWriter:
  def __init__(self):
    self._params = Params()
    self._queue = Queue()
    self._thread = threading.Thread(target=self._run, name="honda-param-writer", daemon=True)
    self._thread.start()

  def put_many(self, values):
    self._queue.put({key: float(value) for key, value in values.items()})

  def _run(self):
    while True:
      pending = self._queue.get()

      # Collapse queued snapshots so delayed writes keep only the newest value per key.
      try:
        while True:
          pending.update(self._queue.get_nowait())
      except Empty:
        pass

      for key, value in pending.items():
        self._params.put_nonblocking(key, value)


class CarController(CarControllerBase, MadsCarController, GasInterceptorCarController, IntelligentCruiseButtonManagementInterface):
  def __init__(self, dbc_names, CP, CP_SP):
    CarControllerBase.__init__(self, dbc_names, CP, CP_SP)
    MadsCarController.__init__(self)
    GasInterceptorCarController.__init__(self, CP, CP_SP)
    IntelligentCruiseButtonManagementInterface.__init__(self, CP, CP_SP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)
    self.tja_control = CP.carFingerprint in HONDA_BOSCH_TJA_CONTROL
    self.param_reader = Params()
    self.param_writer = HondaParamWriter()

    self.braking = False
    self.brake_steady = 0.
    self.brake_last = 0.
    self.apply_brake_last = 0
    self.last_pump_ts = 0.
    self.stopping_counter = 0

    self.accel = 0.0
    self.speed = 0.0
    self.gas = 0.0
    self.brake = 0.0
    self.last_torque = 0.0
    self.bosch_last_gas = 0

    self.gasfactor = get_param_float(self.param_reader, "HondaGasFactorParams", 1.0, 0.1, 3.0)
    self.gasfactor_before_maxgas = self.gasfactor
    self.windfactor = get_param_float(self.param_reader, "HondaWindFactorParams", 1.0, 0.1, 5.0)
    self.windfactor_before_maxgas = self.windfactor_before_brake = self.windfactor
    self.pitch = 0.0

    self.torque_lpf = 0.0
    self.notch_filter = NotchFilter(1.0 / DT_CTRL)
    self.prev_torque_cmd = 0.0
    self.override_ramp = 1.0
    self.lat_active_prev = False
    self.steering_pressed_prev = False
    self.steering_pressed_filter_s = 0.0
    self.steering_pressed_robust_prev = False

    # Bosch extra-brake controller
    self.brake_pid = PIDController(k_p=([0,], [0,]),
                                   k_i=([0.], [0.5]),
                                   pos_limit=0.0,
                                   neg_limit=-2.0,
                                   rate=50)
    self.brake_pid.reset()

  def _filtered_steering_pressed(self, CS, torque_cmd: float) -> bool:
    raw_pressed = bool(CS.out.steeringPressed)
    steering_torque = float(getattr(CS.out, "steeringTorque", 0.0))
    torque_cmd = float(torque_cmd)

    if not raw_pressed:
      self.steering_pressed_filter_s = 0.0
      self.steering_pressed_robust_prev = False
      return False

    torque_product = steering_torque * torque_cmd
    torque_cmd_abs = abs(torque_cmd)

    if self.steering_pressed_robust_prev or torque_cmd_abs < 0.10 or torque_product < 0.0:
      self.steering_pressed_filter_s = 1.0
      self.steering_pressed_robust_prev = True
      return True

    self.steering_pressed_filter_s = min(1.0, self.steering_pressed_filter_s + DT_CTRL)
    steering_pressed = self.steering_pressed_filter_s >= 0.28

    self.steering_pressed_robust_prev = steering_pressed
    return steering_pressed

  def _get_live_tuning_params(self):
    return {
      "override_fade_down_s": get_param_float(self.param_reader, "HondaOverrideFadeDownSecs", 0.0, 0.0, 10.0),
      "override_fade_up_s": get_param_float(self.param_reader, "HondaOverrideFadeUpSecs", 1.5, 0.0, 10.0),
      "override_torque_scale": get_param_float(self.param_reader, "HondaOverrideTorqueScale", 0.0, 0.0, 100.0, scale=100.0),
      "driver_assist_during_override": get_param_bool(self.param_reader, "HondaDriverAssistDuringOverride", True),
      # Default ON for Bosch (gas learns well), OFF for Nidec; only applies when unset.
      "live_learning_gas": get_param_bool(self.param_reader, "HondaLiveLearningGas", self.CP.carFingerprint in HONDA_BOSCH),
      "torque_lpf_enabled": get_param_bool(self.param_reader, "HondaTorqueLowPassFilter", True),
      "lpf_tau_low": get_param_float(self.param_reader, "HondaLpfTauLowSpeed", 0.1, 0.0, 5.0),
      "lpf_tau_standard": get_param_float(self.param_reader, "HondaLpfTauStandard", 0.1, 0.0, 5.0),
      "lpf_tau_highway": get_param_float(self.param_reader, "HondaLpfTauHighway", 0.1, 0.0, 5.0),
      "notch_enabled": get_param_bool(self.param_reader, "HondaNotchEnabled", False),
      "notch_freq": get_param_float(self.param_reader, "HondaNotchFreq", 7.5, 1.0, 20.0),
      "notch_q": get_param_float(self.param_reader, "HondaNotchQ", 1.5, 0.1, 10.0),
      "steer_delta_limiter_enabled": get_param_bool(self.param_reader, "HondaSteerDeltaLimiter", False),
      "steer_delta_up": get_param_float(self.param_reader, "HondaSteerDeltaUp", 3.0, 0.0, 100.0),
      "steer_delta_down": get_param_float(self.param_reader, "HondaSteerDeltaDown", 3.0, 0.0, 100.0),
      "stopping_decel_rate": get_param_float(self.param_reader, "HondaStoppingDecelRate", 0.3, 0.0, 1.0, scale=100.0),
      "increase_override_tolerance": get_param_bool(self.param_reader, "NrdrIncreaseOverrideTolerance", False),
      # Alternative Dashboard designs (Party Tricks)
      "alt_dashboard_speed": int(get_param_float(self.param_reader, "HondaAltDashboardSpeed", 0.0, 0.0, 3.0)),     # 0 Stock, 1 Lead, 2 GPS, 3 Cluster
      "alt_dashboard_distance": int(get_param_float(self.param_reader, "HondaAltDashboardDistance", 0.0, 0.0, 2.0)),  # 0 Stock, 1 Radar, 2 Velocity
      # Special: dashboard fault clearing + dead-camera spoofing
      "clear_dash_faults": get_param_bool(self.param_reader, "NrdrClearDashFaults", True),
      "spoof_camera_messages": get_param_bool(self.param_reader, "HondaSpoofCameraMessages", False),
      # Dynamic HUD (Cruise Button Sub-Mode)
      "sub_mode_enabled": get_param_bool(self.param_reader, "NrdrCruiseButtonSubMode", True),
      "sub_mode_until": get_param_float(self.param_reader, "NrdrHudSubModeUntil", 0.0, 0.0),
      # Must stay in range with SUBMODE_WINDOW_MIN/MAX in openpilot selfdrive/controls/lib/nrdr_hud_submode.py
      "sub_mode_window_s": get_param_float(self.param_reader, "NrdrCruiseButtonSubModeSecs", 15.0, 5.0, 60.0),
    }

  @staticmethod
  def _hud_sub_mode_state(live):
    """Dynamic HUD sub-mode + blink state from the shared NrdrHudSubModeUntil deadline.

    The blink accelerates continuously across the whole user-set window: a lazy
    1000ms ON / 200ms OFF on a fresh press, ramping to a frantic 100/100 (5 Hz)
    right before the sub-mode cuts off - so you can always tell how much time is
    left, whether the window is 5 seconds or 60."""
    if not live["sub_mode_enabled"]:
      return False, True
    now = time.monotonic()
    remaining = live["sub_mode_until"] - now
    if remaining <= 0.0:
      return False, True
    window_s = live["sub_mode_window_s"]
    on_ms = float(np.interp(remaining, [0.0, window_s], [100.0, 1000.0]))
    off_ms = float(np.interp(remaining, [0.0, window_s], [100.0, 200.0]))
    blink_on = (now * 1000.0) % (on_ms + off_ms) < on_ms
    return True, blink_on

  def _update_steering_torque(self, CC, CS, live):
    torque_cmd = float(CC.actuators.torque) if CC.latActive else 0.0
    steering_pressed = False

    if CC.latActive:
      if live["increase_override_tolerance"]:
        steering_pressed = self._filtered_steering_pressed(CS, torque_cmd)
      else:
        steering_pressed = bool(CS.out.steeringPressed)

      if not self.lat_active_prev:
        self.override_ramp = 0.0

      if steering_pressed:
        fade_down_s = live["override_fade_down_s"]
        self.override_ramp = live["override_torque_scale"] if fade_down_s <= 0.0 else max(live["override_torque_scale"], self.override_ramp - DT_CTRL / fade_down_s)
      else:
        fade_up_s = live["override_fade_up_s"]
        self.override_ramp = 1.0 if fade_up_s <= 0.0 else min(1.0, self.override_ramp + DT_CTRL / fade_up_s)

      torque_cmd *= self.override_ramp

      if live["torque_lpf_enabled"]:
        tau = torque_lpf_tau(CS.out.vEgo, live["lpf_tau_low"], live["lpf_tau_standard"], live["lpf_tau_highway"])
        alpha = DT_CTRL / (tau + DT_CTRL)
        self.torque_lpf = alpha * torque_cmd + (1.0 - alpha) * self.torque_lpf
        torque_cmd = self.torque_lpf
      else:
        self.torque_lpf = torque_cmd

      # Notch filter (in series, after LPF): removes the narrow EPS chatter band
      # (~7Hz) without the broadband lag a LPF adds. Independently toggleable.
      if live["notch_enabled"]:
        torque_cmd = self.notch_filter.update(torque_cmd, live["notch_freq"], live["notch_q"])
      else:
        self.notch_filter.reset()

      self.prev_torque_cmd = torque_cmd
    else:
      self.override_ramp = 0.0
      self.torque_lpf = 0.0
      self.notch_filter.reset()
      self.prev_torque_cmd = 0.0
      self.steering_pressed_filter_s = 0.0
      self.steering_pressed_robust_prev = False

    if live["steer_delta_limiter_enabled"]:
      limited_torque = rate_limit(torque_cmd, self.last_torque,
                                  -live["steer_delta_down"] * DT_CTRL,
                                  live["steer_delta_up"] * DT_CTRL)
    else:
      limited_torque = torque_cmd

    self.last_torque = limited_torque
    self.lat_active_prev = CC.latActive
    self.steering_pressed_prev = steering_pressed

    # "Driver assist during override" ON  -> openpilot gives way while you steer (LKAS torque drops out).
    # OFF -> openpilot keeps applying torque during override (more resistant).
    lkas_active = CC.latActive and (not live["driver_assist_during_override"] or not steering_pressed)
    return limited_torque, lkas_active

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, self.CP, CC, CC_SP)
    live = self._get_live_tuning_params()
    gas_pedal_force = 0.0
    actuators = CC.actuators
    hud_control = CC.hudControl
    hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if hud_control.speedVisible else 255
    pcm_cancel_cmd = CC.cruiseControl.cancel

    if len(CC.orientationNED) == 3:
      self.pitch = CC.orientationNED[1]
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY

    if CC.longActive:
      accel = actuators.accel
      if (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)) and (accel > max(0, CS.out.aEgo) + 0.1):
        accel = 10000.0 # help with lagged accel until pedal tuning is inserted
      gas, brake = compute_gas_brake(actuators.accel + hill_brake, CS.out.vEgo, self.CP.carFingerprint)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0

    # *** rate limit / filter steer ***
    limited_torque, lkas_active = self._update_steering_torque(CC, CS, live)

    # *** apply brake hysteresis ***
    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(brake, self.braking, self.brake_steady,
                                                                           CS.out.vEgo, self.CP.carFingerprint)

    # *** rate limit after the enable check ***
    brake_rate_up = live["stopping_decel_rate"] if actuators.longControlState == LongCtrlState.stopping else 3.0
    self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., brake_rate_up * DT_CTRL)

    # vehicle hud display, wait for one update from 10Hz 0x304 msg
    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    # **** process the car messages ****

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_torque = int(np.interp(-limited_torque * self.params.STEER_MAX,
                                 self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    speed_control = 1 if ((accel <= 0.0) and (CS.out.vEgo == 0)) else 0

    # Send CAN commands
    can_sends = []

    # tester present - w/ no response (keeps radar disabled)
    if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.frame % 10 == 0:
        can_sends.append(make_tester_present_msg(0x18DAB0F1, self.CAN.pt, suppress_response=True))

    # Send steering command.
    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_torque, lkas_active, self.tja_control))

    # wind brake from air resistance decel at high speed
    wind_brake = np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15]) * self.windfactor # not in m/s2 units
    wind_brake_ms2 = np.interp(CS.out.vEgo, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441]) # in m/s2 units

    # all of this is only relevant for HONDA NIDEC
    speed_control = 0
    max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
    # TODO this 1.44 is just to maintain previous behavior
    pcm_speed_BP = [-wind_brake,
                    -wind_brake * (3 / 4),
                    0.0,
                    0.5]
    # The Honda ODYSSEY seems to have different PCM_ACCEL
    # msgs, is it other cars too?
    if self.CP_SP.enableGasInterceptor or not CC.longActive:
      pcm_speed = 0.0
      pcm_accel = int(0.0)
    elif self.CP.carFingerprint in HONDA_NIDEC_ALT_PCM_ACCEL:
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 3.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 0.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(1.0 * self.params.NIDEC_GAS_MAX)
    elif (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)):
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 20.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(np.clip((accel / 1.44) / max_accel, 10.0 / self.params.NIDEC_GAS_MAX, 1.0) * self.params.NIDEC_GAS_MAX)
      if speed_control == 1 and CC.longActive:
        pcm_accel = 198
    else:
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(np.clip((accel / 1.44) / max_accel, 0.0, 1.0) * self.params.NIDEC_GAS_MAX)

    if not self.CP.openpilotLongitudinalControl:
      if self.frame % 2 == 0 and self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS | HONDA_BOSCH_CANFD:
        can_sends.append(hondacan.create_bosch_supplemental_1(self.packer, self.CAN))
      # If using stock ACC, spam cancel command to kill gas when OP disengages.
      if pcm_cancel_cmd:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.CANCEL, self.CP.carFingerprint))
      elif CC.cruiseControl.resume:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.RES_ACCEL, self.CP.carFingerprint))

    else:
      # Send gas and brake commands.
      if self.frame % 2 == 0:
        ts = self.frame * DT_CTRL

        if self.CP.carFingerprint in HONDA_BOSCH:
          if (accel < 0) and (CS.out.vEgo > 1e-3):
            brake_addon = self.brake_pid.update(error = accel - CS.out.aEgo, speed = CS.out.vEgo)
            targetaccel = min(accel,accel + brake_addon)
          else:
            self.brake_pid.reset()
            targetaccel = accel

          self.accel = float(np.clip(targetaccel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = self.accel + wind_brake_ms2 * self.windfactor + hill_brake

          # live-learn gas pedal adjustments when openpilot is controlling gas
          if live["live_learning_gas"] and (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
            gas_error = self.accel - CS.out.aEgo
            if gas_error != 0.0 and gas_pedal_force > 0.0:
              if self.CP.carFingerprint == CAR.HONDA_INSIGHT: # Insight gas pedal reacts too slowly
                learn_speed = 150
              elif self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Prevent overreacting to turbo lag
                learn_speed = 300
              else:
                learn_speed = 50
              self.gasfactor = np.clip(self.gasfactor + gas_error / learn_speed * gas_pedal_force, 0.1, 3.0)
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              if self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Faster reaction
                wind_learn_speed = 100
              else:
                wind_learn_speed = 1000
              wind_adjust = 1 + wind_brake_ms2 / wind_learn_speed
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 3.0)
            if gas_pedal_force <= 0.0: # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor
            if gas_pedal_force >= self.params.BOSCH_ACCEL_MAX: # don't increase gasfactor nor windfactor at accel max, allow decreases
              self.gasfactor = min(self.gasfactor, self.gasfactor_before_maxgas)
              self.windfactor = min(self.windfactor, self.windfactor_before_maxgas)
            else:
              self.gasfactor_before_maxgas = self.gasfactor
              self.windfactor_before_maxgas = self.windfactor
          self.gas = float(np.interp(gas_pedal_force * self.gasfactor, self.params.BOSCH_GAS_LOOKUP_BP, self.params.BOSCH_GAS_LOOKUP_V))

          # limit gas ramp to 60 units per frame, matches stock. Higher sometimes causes powertrain to ignore gas command.
          max_gas = max(60, self.bosch_last_gas + 60)
          self.gas = min(self.gas, max_gas)
          self.bosch_last_gas = self.gas

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          can_sends.extend(hondacan.create_acc_commands(self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas,
                                                        self.stopping_counter, self.CP.carFingerprint, gas_pedal_force))
        else:
          apply_brake = np.clip(self.brake_last - wind_brake, 0.0, 1.0)
          apply_brake = int(np.clip(apply_brake * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))
          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          pcm_override = True
          can_sends.append(hondacan.create_brake_command(self.packer, self.CAN, apply_brake, pump_on,
                                                         pcm_override, pcm_cancel_cmd, alert_fcw,
                                                         self.CP.carFingerprint, CS.stock_brake, self.CP_SP,
                                                         clear_dash_faults=live["clear_dash_faults"]))
          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

          gas_error = actuators.accel - CS.out.aEgo
          if live["live_learning_gas"] and (not CS.out.gasPressed) and (actuators.longControlState == LongCtrlState.pid) and self.CP_SP.enableGasInterceptor:
            if gas_error != 0.0 and gas > 0.0:
              self.gasfactor = np.clip(self.gasfactor + gas_error / 150 * (gas * 4.8), 0.1, 3.0)
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              wind_adjust = 1 + (wind_brake * 4.8) / 1000
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 5.0)
            if gas <= 0.0: # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor

          can_sends.extend(GasInterceptorCarController.update(self, CC, CS, gas * self.gasfactor, brake, wind_brake, self.packer, self.frame))

    # Send dashboard UI commands.
    if self.frame % 10 == 0:
      if CC.longActive and (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)):
        # standstill disengage
        if (accel >= 0.01) and (CS.out.vEgo < 4.0) and (pcm_speed < 25.0 / 3.6):
          pcm_speed = 25.0 / 3.6

      if self.CP.openpilotLongitudinalControl:
        # On Nidec, this also controls longitudinal positive acceleration
        # Alternative Dashboard: convert lead/vehicle speed to the cluster's display unit
        # (v_cruise_factor matches the hud_v_cruise conversion above).
        v_factor = CS.v_cruise_factor if CS.v_cruise_factor else 1.0
        lead_speed_display = hud_control.leadVLead / v_factor
        gps_speed_display = CS.out.vEgo / v_factor
        cluster_speed_display = (CS.out.vEgoCluster or CS.out.vEgo) / v_factor
        sub_mode_active, sub_mode_blink_on = self._hud_sub_mode_state(live)
        can_sends.append(hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel,
                                                 hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control,
                                                 speed_design=live["alt_dashboard_speed"], distance_design=live["alt_dashboard_distance"],
                                                 sub_mode_active=sub_mode_active, sub_mode_blink_on=sub_mode_blink_on,
                                                 lead_speed_display=lead_speed_display, gps_speed_display=gps_speed_display,
                                                 cluster_speed_display=cluster_speed_display, vehicle_accel=CS.out.aEgo,
                                                 clear_dash_faults=live["clear_dash_faults"]))

      # Dead-camera support: keep CAMERA_MESSAGES (0x35E) alive so the cluster never
      # raises "Auto High Beam System Problem". Nidec only; OFF unless the stock
      # camera is actually dead/absent (a live camera also sends this message).
      if live["spoof_camera_messages"] and self.CP.carFingerprint not in HONDA_BOSCH:
        can_sends.append(hondacan.create_camera_messages(self.packer, self.CAN.pt))

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > max(self.params.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      reduced_steering = CS.out.steeringPressed
      steer_maxed = abs(apply_torque) >= self.params.STEER_MAX
      can_sends.extend(hondacan.create_lkas_hud(self.packer, self.CAN.lkas, self.CP, hud_control, CC.latActive,
                                                steering_available, reduced_steering, alert_steer_required, CS.lkas_hud, self.dashed_lanes,
                                                steer_maxed))

      if self.CP.openpilotLongitudinalControl:
        # TODO: combining with create_acc_hud block above will change message order and will need replay logs regenerated
        if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS):
          can_sends.append(hondacan.create_radar_hud(self.packer, self.CAN.pt))
        if self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH:
          can_sends.append(hondacan.create_legacy_brake_command(self.packer, self.CAN.pt))
        if self.CP.carFingerprint not in HONDA_BOSCH:
          self.speed = pcm_speed
          if not self.CP_SP.enableGasInterceptor:
            self.gas = pcm_accel / self.params.NIDEC_GAS_MAX

    # Intelligent Cruise Button Management
    can_sends.extend(IntelligentCruiseButtonManagementInterface.update(self, CC_SP, self.packer, self.frame,
                                                                       self.last_button_frame, self.CAN))

    new_actuators = actuators.as_builder()
    new_actuators.speed = self.speed
    new_actuators.accel = self.accel
    new_actuators.gas = float(self.gasfactor)
    new_actuators.brake = float(self.windfactor)
    new_actuators.torque = self.last_torque
    new_actuators.torqueOutputCan = apply_torque

    if self.frame % 6000 == 0:
      self.param_writer.put_many({
        "HondaGasFactorParams": self.gasfactor,
        "HondaWindFactorParams": self.windfactor,
      })

    self.frame += 1
    return new_actuators, can_sends