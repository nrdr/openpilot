import numpy as np
import math

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, structs
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import CAR, CruiseButtons, HONDA_BOSCH, HONDA_BOSCH_CANFD, HONDA_BOSCH_RADARLESS, \
                                     HONDA_BOSCH_TJA_CONTROL, HONDA_NIDEC_ALT_PCM_ACCEL, CarControllerParams
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.common.conversions import Conversions as CV

from opendbc.sunnypilot.car.honda.mads import MadsCarController
from opendbc.sunnypilot.car.honda.gas_interceptor import GasInterceptorCarController
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState

_BRAKE_MODIFIER = 0.0


def compute_gb_honda_bosch(accel, speed):
  # TODO returns 0s, is unused
  return 0.0, 0.0


def compute_gb_honda_nidec_new(accel, speed):
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / 4.8 - creep_brake
  return np.clip(gb, 0.0, 1.0), np.clip(-gb, 0.0, 1.0)


def compute_gb_honda_nidec_legacy(accel, speed):
  global _BRAKE_MODIFIER

  if accel < -3.9:
    _BRAKE_MODIFIER += 0.01
  else:
    _BRAKE_MODIFIER = 0.0

  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value

  gb_div = float(np.interp(float(accel), [4.0, 3.5], [4.0, 4.8]))
  gb = float(accel) / gb_div - creep_brake
  just_brake = float(accel) / (-4.8 + _BRAKE_MODIFIER) + creep_brake
  return np.clip(gb, 0.0, 1.0), np.clip(just_brake, 0.0, 1.0)


# TODO not clear this does anything useful
def actuator_hysteresis(brake, braking, brake_steady, v_ego, car_fingerprint):
  brake_hyst_on = 0.02
  brake_hyst_off = 0.005
  brake_hyst_gap = 0.01

  if (brake < brake_hyst_on and not braking) or brake < brake_hyst_off:
    brake = 0.
  braking = brake > 0.

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

  if apply_brake > apply_brake_last or (ts - last_pump_ts > 20. and apply_brake > 0):
    last_pump_ts = ts

  if ts - last_pump_ts < 0.2 and apply_brake > 0:
    pump_on = True

  return pump_on, last_pump_ts


def process_hud_alert(hud_alert):
  alert_fcw = False
  alert_steer_required = False

  if hud_alert == VisualAlert.fcw:
    alert_fcw = True
  elif hud_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
    alert_steer_required = True

  return alert_fcw, alert_steer_required


def _clamp01(x: float) -> float:
  return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)


def _quick_start_curve(x: float) -> float:
  x = _clamp01(x)
  return x ** 0.5


def _driver_override_speed_factor(v_ego: float) -> float:
  full_cut_mph = 20.0
  no_cut_mph = 25.0

  return float(np.interp(v_ego,
                         [full_cut_mph * CV.MPH_TO_MS, no_cut_mph * CV.MPH_TO_MS],
                         [1.0, 0.9]))


def _torque_lpf_tau(torque_cmd: float, prev_torque_cmd: float, v_ego: float) -> float:
  if v_ego > 45.0 * CV.MPH_TO_MS: # Speed at which low-pass filter becomes static value listed below:
    return 0.1

  torque_delta = abs(float(torque_cmd) - float(prev_torque_cmd))
  sign_change = (float(torque_cmd) * float(prev_torque_cmd)) < 0.0

  if sign_change:
    # Unwinding from turn: prioritize fast response to reduce lag
    if torque_delta > 0.15:
      return 0.000
    elif torque_delta > 0.05:
      return 0.050
    else:
      return 0.100

  if torque_delta > 0.50:
    return 0.020
  elif torque_delta > 0.20:
    return 0.050
  elif torque_delta > 0.05:
    return 0.075
  else:
    return 0.100


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

    # New longitudinal behavior is preserved for all Bosch cars and the Nidec Clarity.
    # All other Nidec platforms fall back to the legacy longitudinal behavior.
    self.use_new_long_logic = (CP.carFingerprint in HONDA_BOSCH) or (CP.carFingerprint == CAR.HONDA_CLARITY)

    # Enable steering override behavior only when the modified EPS firmware is detected.
    # Stock EPS cars rely on driver "assist" to achieve tighter curvature; forcing torque-to-zero
    # and additional filtering on stock EPS can degrade lateral performance.
    self.eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)

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

    self.gasfactor = 1.0
    self.gasfactor_before_maxgas = 1.0
    self.windfactor = 1.0
    self.windfactor_before_maxgas = 1.0
    self.windfactor_before_brake = 0.0
    self.pitch = 0.0

    self.torque_lpf = 0.0
    self.prev_torque_cmd = 0.0

    self.override_ramp_down_s = 0.1
    self.override_ramp_up_s = 3.0
    self.steering_pressed_prev = False
    self.override_state = "normal"
    self.override_phase_start_nanos = 0
    self.override_start_torque = 0.0

    self.driver_override_until_nanos = 0

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, self.CP, CC, CC_SP)
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
        accel = 10000.0  # help with lagged accel until pedal tuning is inserted

      if self.CP.carFingerprint in HONDA_BOSCH:
        gas, brake = compute_gb_honda_bosch(actuators.accel + hill_brake, CS.out.vEgo)
      else:
        if self.use_new_long_logic:
          gas, brake = compute_gb_honda_nidec_new(actuators.accel + hill_brake, CS.out.vEgo)
        else:
          gas, brake = compute_gb_honda_nidec_legacy(actuators.accel, CS.out.vEgo)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0

    # *** steer command conditioning (driver interaction + low-pass filter + rate limit) ***
    torque_cmd = actuators.torque

    if CC.latActive:
      steering_pressed = CS.out.steeringPressed

      if self.eps_modified:
        override_factor = _driver_override_speed_factor(CS.out.vEgo)

        steering_rising = (not self.steering_pressed_prev) and steering_pressed
        steering_falling = self.steering_pressed_prev and (not steering_pressed)

        if steering_rising:
          self.override_state = "ramp_down"
          self.override_phase_start_nanos = now_nanos
          self.override_start_torque = float(self.torque_lpf)

        if steering_pressed:
          if self.override_state == "ramp_down":
            fade_ns = int(self.override_ramp_down_s * 1e9)
            dt_ns = now_nanos - self.override_phase_start_nanos
            x = 1.0 if fade_ns <= 0 else _clamp01(float(dt_ns) / float(fade_ns))

            torque_target = self.override_start_torque * (1.0 - x * override_factor)

            self.torque_lpf = torque_target
            torque_cmd = self.torque_lpf

            if x >= 1.0:
              self.override_state = "holding"
          else:
            self.override_state = "holding"
            torque_hold = float(torque_cmd) * (1.0 - override_factor)
            self.torque_lpf = torque_hold
            torque_cmd = torque_hold

        else:
          if steering_falling:
            self.override_state = "ramp_up"
            self.override_phase_start_nanos = now_nanos

          if self.override_state == "ramp_up":
            fade_ns = int(self.override_ramp_up_s * 1e9)
            dt_ns = now_nanos - self.override_phase_start_nanos
            x = 1.0 if fade_ns <= 0 else _clamp01(float(dt_ns) / float(fade_ns))

            scale = _quick_start_curve(x)
            ramp_scale = (1.0 - override_factor) + (override_factor * scale)
            torque_target = float(torque_cmd) * ramp_scale

            self.torque_lpf = torque_target
            torque_cmd = self.torque_lpf

            if x >= 1.0:
              self.override_state = "normal"

          if self.override_state == "normal":
            tau = _torque_lpf_tau(torque_cmd, self.prev_torque_cmd, CS.out.vEgo)
            alpha = DT_CTRL / (tau + DT_CTRL)

            if torque_cmd * self.torque_lpf < 0.0:
              self.torque_lpf = torque_cmd
            else:
              self.torque_lpf = alpha * torque_cmd + (1.0 - alpha) * self.torque_lpf

            self.prev_torque_cmd = float(torque_cmd)
            torque_cmd = self.torque_lpf

        self.steering_pressed_prev = steering_pressed

      else:
        self.torque_lpf = float(torque_cmd)
        self.prev_torque_cmd = float(torque_cmd)
        self.steering_pressed_prev = steering_pressed
        self.override_state = "normal"
        self.override_phase_start_nanos = 0
        self.override_start_torque = 0.0

    else:
      self.torque_lpf = 0.0
      self.prev_torque_cmd = 0.0
      self.last_torque = 0.0
      self.driver_override_until_nanos = 0
      self.steering_pressed_prev = False
      self.override_state = "normal"
      self.override_phase_start_nanos = 0
      self.override_start_torque = 0.0

    limited_torque = rate_limit(
      torque_cmd,
      self.last_torque,
      -self.params.STEER_DELTA_DOWN * DT_CTRL,
      self.params.STEER_DELTA_UP * DT_CTRL
    )

    self.last_torque = limited_torque

    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(
      brake, self.braking, self.brake_steady, CS.out.vEgo, self.CP.carFingerprint
    )

    if self.use_new_long_logic:
      self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., 3 * DT_CTRL)
    else:
      self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., DT_CTRL)

    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    apply_torque = int(np.interp(-limited_torque * self.params.STEER_MAX,
                                 self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    speed_control = 1 if ((accel <= 0.0) and (CS.out.vEgo == 0)) else 0

    can_sends = []

    if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.frame % 10 == 0:
        can_sends.append(make_tester_present_msg(0x18DAB0F1, self.CAN.pt, suppress_response=True))

    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_torque, CC.latActive, self.tja_control))

    wind_brake = np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15]) * self.windfactor
    wind_brake_ms2 = np.interp(CS.out.vEgo, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441])

    speed_control = 0
    max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
    pcm_speed_BP = [-wind_brake,
                    -wind_brake * (3 / 4),
                    0.0,
                    0.5]

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
    elif self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR):
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
      if pcm_cancel_cmd:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.CANCEL, self.CP.carFingerprint))
      elif CC.cruiseControl.resume:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.RES_ACCEL, self.CP.carFingerprint))

    else:
      if self.frame % 2 == 0:
        ts = self.frame * DT_CTRL

        if self.CP.carFingerprint in HONDA_BOSCH:
          self.accel = float(np.clip(accel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = self.accel + wind_brake_ms2 * self.windfactor + hill_brake

          if (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
            gas_error = self.accel - CS.out.aEgo
            if self.CP.carFingerprint == CAR.ACURA_RDX_3G and CS.out.vEgo < 1e-3:
              self.gasfactor = 3.0
            if gas_error != 0.0 and gas_pedal_force > 0.0:
              learn_speed = 150 if (self.CP.carFingerprint == CAR.HONDA_INSIGHT) else 50
              self.gasfactor = np.clip(self.gasfactor + gas_error / learn_speed * gas_pedal_force, 0.1, 3.0)
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              wind_adjust = 1 + wind_brake_ms2 / 1000
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0 / wind_adjust), 0.1, 3.0)
            if gas_pedal_force <= 0.0:
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor
            if gas_pedal_force >= self.params.BOSCH_ACCEL_MAX:
              self.gasfactor = min(self.gasfactor, self.gasfactor_before_maxgas)
              self.windfactor = min(self.windfactor, self.windfactor_before_maxgas)
            else:
              self.gasfactor_before_maxgas = self.gasfactor
              self.windfactor_before_maxgas = self.windfactor

          self.gas = float(np.interp(gas_pedal_force * self.gasfactor,
                                     self.params.BOSCH_GAS_LOOKUP_BP,
                                     self.params.BOSCH_GAS_LOOKUP_V))

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          can_sends.extend(hondacan.create_acc_commands(
            self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas,
            self.stopping_counter, self.CP.carFingerprint, gas_pedal_force
          ))
        else:
          if self.use_new_long_logic:
            apply_brake = np.clip(self.brake_last - wind_brake, 0.0, 1.0)
          else:
            apply_brake = np.clip(self.brake_last - (wind_brake if self.brake_last <= 0.95 else 0.0), 0.0, 1.0)

          apply_brake = int(np.clip(apply_brake * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))
          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          pcm_override = True
          can_sends.append(hondacan.create_brake_command(
            self.packer, self.CAN, apply_brake, pump_on,
            pcm_override, pcm_cancel_cmd, alert_fcw,
            self.CP.carFingerprint, CS.stock_brake, self.CP_SP
          ))
          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

          if self.CP_SP.enableGasInterceptor:
            if self.use_new_long_logic:
              gas_error = actuators.accel - CS.out.aEgo
              if (not CS.out.gasPressed) and (actuators.longControlState == LongCtrlState.pid):
                if gas_error != 0.0 and gas > 0.0:
                  self.gasfactor = np.clip(self.gasfactor + gas_error / 50 * (gas * 4.8), 0.1, 3.0)
                if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
                  wind_adjust = 1 + (wind_brake * 4.8) / 1000
                  self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0 / wind_adjust), 0.1, 5.0)
                if gas <= 0.0:
                  self.windfactor = max(self.windfactor, self.windfactor_before_brake)
                else:
                  self.windfactor_before_brake = self.windfactor

              can_sends.extend(GasInterceptorCarController.update(
                self, CC, CS, gas * self.gasfactor, brake, wind_brake, self.packer, self.frame
              ))
            else:
              can_sends.extend(GasInterceptorCarController.update(
                self, CC, CS, gas, brake, wind_brake, self.packer, self.frame
              ))
          else:
            can_sends.extend(GasInterceptorCarController.update(
              self, CC, CS, gas, brake, wind_brake, self.packer, self.frame
            ))

    if self.frame % 10 == 0:
      if CC.longActive and (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)):
        if (accel >= 0.01) and (CS.out.vEgo < 4.0) and (pcm_speed < 25.0 / 3.6):
          pcm_speed = 25.0 / 3.6

      if self.CP.openpilotLongitudinalControl:
        can_sends.append(hondacan.create_acc_hud(
          self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel,
          hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control
        ))

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > max(self.params.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      reduced_steering = CS.out.steeringPressed
      steer_maxed = abs(apply_torque) >= self.params.STEER_MAX
      can_sends.extend(hondacan.create_lkas_hud(
        self.packer, self.CAN.lkas, self.CP, hud_control, CC.latActive,
        steering_available, reduced_steering, alert_steer_required, CS.lkas_hud, self.dashed_lanes,
        steer_maxed
      ))

      if self.CP.openpilotLongitudinalControl:
        if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS):
          can_sends.append(hondacan.create_radar_hud(self.packer, self.CAN.pt))
        if self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH:
          can_sends.append(hondacan.create_legacy_brake_command(self.packer, self.CAN.pt))
        if self.CP.carFingerprint not in HONDA_BOSCH:
          self.speed = pcm_speed
          if not self.CP_SP.enableGasInterceptor:
            self.gas = pcm_accel / self.params.NIDEC_GAS_MAX

    can_sends.extend(IntelligentCruiseButtonManagementInterface.update(
      self, CC_SP, self.packer, self.frame, self.last_button_frame, self.CAN
    ))

    new_actuators = actuators.as_builder()
    new_actuators.speed = self.speed
    new_actuators.accel = self.accel

    if self.use_new_long_logic:
      new_actuators.gas = float(self.gasfactor)
      new_actuators.brake = float(self.windfactor)
    else:
      new_actuators.gas = float(self.gas)
      new_actuators.brake = float(self.brake)

    new_actuators.torque = float(self.last_torque)
    new_actuators.torqueOutputCan = apply_torque

    self.frame += 1
    return new_actuators, can_sends
