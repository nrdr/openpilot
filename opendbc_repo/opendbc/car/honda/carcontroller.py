import numpy as np
import math

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, structs
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import CAR, CruiseButtons, HONDA_BOSCH, HONDA_BOSCH_CANFD, HONDA_BOSCH_RADARLESS, \
                                     HONDA_NIDEC_ALT_PCM_ACCEL, CarControllerParams
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.common.conversions import Conversions as CV

from opendbc.roenpilot.common.numpy_fast import clip, interp

from opendbc.sunnypilot.car.honda.mads import MadsCarController
from opendbc.sunnypilot.car.honda.gas_interceptor import GasInterceptorCarController
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState

_BrakeModifier = 0.0


def compute_gb_honda_bosch(accel, speed):
  # TODO returns 0s, is unused
  return 0.0, 0.0


def compute_gb_honda_nidec(accel, speed):
  global _BrakeModifier
  if accel < -3.9:
    _BrakeModifier += 0.01
  else:
    _BrakeModifier = 0.0
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / interp(float(accel), [4.0, 3.5], [4.0, 4.8]) - creep_brake
  just_brake = float(accel) / (-4.8 + _BrakeModifier) + creep_brake
  return clip(gb, 0.0, 1.0), clip(just_brake, 0.0, 1.0)


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


class CarController(CarControllerBase, MadsCarController, GasInterceptorCarController, IntelligentCruiseButtonManagementInterface):
  def __init__(self, dbc_names, CP, CP_SP):
    CarControllerBase.__init__(self, dbc_names, CP, CP_SP)
    MadsCarController.__init__(self)
    GasInterceptorCarController.__init__(self, CP, CP_SP)
    IntelligentCruiseButtonManagementInterface.__init__(self, CP, CP_SP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)

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
    self.gasfactor = 1.0
    self.windfactor = 1.0
    self.windfactor_before_brake = 0.0
    self.pitch = 0.0
    self.last_torque = 0.0
    self.torque_lpf = 0.0

    # Driver override behavior for steer LPF:
    # - while steeringPressed (and a short time after), force OP steer torque to 0
    #   and reset filter state so it doesn't "push back"
    # Requested change: Only do the force-to-0 behavior below 20 mph
    self.driver_override_until_nanos = 0
    self.override_hold_s = 0.35  # try 0.20–0.50

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, self.CP, CC, CC_SP)
    actuators = CC.actuators
    hud_control = CC.hudControl
    hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if hud_control.speedVisible else 255
    pcm_cancel_cmd = CC.cruiseControl.cancel

    if len(CC.orientationNED) == 3:
      self.pitch = CC.orientationNED[1]
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY

    if CC.longActive:
      accel = float(actuators.accel)

      # -------------------------------------------------
      # Hard speed guard: never gas above set speed,
      # never brake below set speed
      # -------------------------------------------------
      if hud_control.speedVisible and hud_control.setSpeed > 0.1:
        v_set_mps = hud_control.setSpeed
        speed_error = v_set_mps - CS.out.vEgo

        OVERSPEED_DEADBAND_MPS = 0.3  # ≈ 0.7 mph, tune 0.2–0.5
        if abs(speed_error) < OVERSPEED_DEADBAND_MPS:
          speed_error = 0.0

        # Above set speed → forbid positive accel
        if speed_error < 0.0:
          accel = min(accel, 0.0)

        # Below set speed → forbid braking
        elif speed_error > 0.0:
          accel = max(accel, 0.0)

      gas, brake = compute_gas_brake(accel, CS.out.vEgo, self.CP.carFingerprint)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0

    # *** rate limit steer (with low-pass filter) ***
    torque_cmd = actuators.torque

    # Only filter while lateral is active; otherwise keep state sane
    if CC.latActive:
      steering_pressed = CS.out.steeringPressed
      below_override_cutoff = CS.out.vEgo < (20.0 * CV.MPH_TO_MS)

      # Only apply the "cut torque to 0" override behavior below 20 mph.
      # Above that, use the existing/normal LPF behavior.
      if below_override_cutoff:
        # Latch override so OP doesn't instantly re-grab
        if steering_pressed:
          self.driver_override_until_nanos = now_nanos + int(self.override_hold_s * 1e9)
        bypass = now_nanos < self.driver_override_until_nanos
      else:
        # Make sure a previously-latched low-speed override can't carry upward
        self.driver_override_until_nanos = 0
        bypass = False

      if bypass:
        # "Get out of the way" immediately
        torque_cmd = 0.0
        self.torque_lpf = 0.0
        self.last_torque = 0.0
      else:
        tau = 0.20  # seconds; try 0.20–0.40
        alpha = DT_CTRL / (tau + DT_CTRL)

        # don't smear through sign flips
        if torque_cmd * self.torque_lpf < 0:
          self.torque_lpf = torque_cmd
        else:
          self.torque_lpf = alpha * torque_cmd + (1.0 - alpha) * self.torque_lpf

        torque_cmd = self.torque_lpf
    else:
      # prevent "snap" when re-engaging
      self.torque_lpf = 0.0
      self.last_torque = 0.0
      self.driver_override_until_nanos = 0

    limited_torque = rate_limit(torque_cmd, self.last_torque,
                                -self.params.STEER_DELTA_DOWN * DT_CTRL,
                                self.params.STEER_DELTA_UP * DT_CTRL)
    self.last_torque = limited_torque

    # *** apply brake hysteresis ***
    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(brake, self.braking, self.brake_steady,
                                                                           CS.out.vEgo, self.CP.carFingerprint)

    # *** rate limit after the enable check ***
    self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., DT_CTRL)

    # vehicle hud display, wait for one update from 10Hz 0x304 msg
    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    # **** process the car messages ****

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_torque = int(interp(-limited_torque * self.params.STEER_MAX,
                                 self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    # Send CAN commands
    can_sends = []

    # tester present - w/ no response (keeps radar disabled)
    if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.frame % 10 == 0:
        can_sends.append(make_tester_present_msg(0x18DAB0F1, 1, suppress_response=True))

    # Send steering command.
    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_torque, CC.latActive))

    # wind brake from air resistance decel at high speed
    wind_brake = float(np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15]))  # not in m/s2 units
    wind_brake_ms2 = float(np.interp(CS.out.vEgo, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441]))  # in m/s2 units

    # all of this is only relevant for HONDA NIDEC
    max_accel = interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
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
                     clip(CS.out.vEgo - 3.0, 0.0, 100.0),
                     clip(CS.out.vEgo + 0.0, 0.0, 100.0),
                     clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(1.0 * self.params.NIDEC_GAS_MAX)
    else:
      pcm_speed_V = [0.0,
                     clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                     clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                     clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(clip((accel / 1.44) / max_accel, 0.0, 1.0) * self.params.NIDEC_GAS_MAX)

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
          self.accel = float(clip(accel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = self.accel + wind_brake_ms2 * self.windfactor + hill_brake

          # live-learn gas pedal adjustments when openpilot is controlling gas
          if (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
            gas_error = self.accel - CS.out.aEgo
            if gas_error != 0.0 and gas_pedal_force > 0.0:
              self.gasfactor = float(np.clip(self.gasfactor + gas_error / 50 * gas_pedal_force, 0.1, 3.0))
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              wind_adjust = 1 + wind_brake_ms2 / 1000
              self.windfactor = float(np.clip(
                self.windfactor * (wind_adjust if (gas_error > 0) else 1.0 / wind_adjust),
                0.1, 3.0
              ))
            if gas_pedal_force <= 0.0:  # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor

          self.gas = float(np.interp(
            gas_pedal_force * self.gasfactor,
            self.params.BOSCH_GAS_LOOKUP_BP,
            self.params.BOSCH_GAS_LOOKUP_V
          ))

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          can_sends.extend(hondacan.create_acc_commands(
            self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas,
            self.stopping_counter, self.CP.carFingerprint, gas_pedal_force
          ))
        else:
          apply_brake = clip(self.brake_last - (wind_brake if self.brake_last <= 0.95 else 0.0), 0.0, 1.0)
          apply_brake = int(clip(apply_brake * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))
          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          pcm_override = True
          can_sends.append(hondacan.create_brake_command(
            self.packer, self.CAN, apply_brake, pump_on,
            pcm_override, pcm_cancel_cmd, alert_fcw,
            self.CP.carFingerprint, CS.stock_brake, self.CP_SP
          ))
          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

          can_sends.extend(GasInterceptorCarController.update(self, CC, CS, gas, brake, wind_brake, self.packer, self.frame))

    # Send dashboard UI commands.
    if self.frame % 10 == 0:
      if self.CP.openpilotLongitudinalControl:
        # On Nidec, this also controls longitudinal positive acceleration
        can_sends.append(hondacan.create_acc_hud(
          self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel,
          hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud
        ))

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > self.CP.minSteerSpeed
      reduced_steering = CS.out.steeringPressed
      can_sends.extend(hondacan.create_lkas_hud(
        self.packer, self.CAN.lkas, self.CP, hud_control, CC.latActive,
        steering_available, reduced_steering, alert_steer_required, CS.lkas_hud, self.dashed_lanes
      ))

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
    can_sends.extend(IntelligentCruiseButtonManagementInterface.update(
      self, CC_SP, self.packer, self.frame, self.last_button_frame, self.CAN
    ))

    new_actuators = actuators.as_builder()
    new_actuators.speed = float(self.speed)
    new_actuators.accel = float(self.accel)
    new_actuators.gas = float(self.gas)
    new_actuators.brake = float(self.brake)
    new_actuators.torque = float(self.last_torque)
    new_actuators.torqueOutputCan = apply_torque

    self.frame += 1
    return new_actuators, can_sends