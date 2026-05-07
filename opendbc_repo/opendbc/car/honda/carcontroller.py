import math
import numpy as np

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, create_gas_interceptor_command, structs
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import (
  CAR,
  CruiseButtons,
  HONDA_BOSCH,
  HONDA_BOSCH_CANFD,
  HONDA_BOSCH_RADARLESS,
  HONDA_BOSCH_TJA_CONTROL,
  HONDA_NIDEC_ALT_PCM_ACCEL,
  CarControllerParams,
  HondaFlags,
)
from opendbc.car.interfaces import CarControllerBase

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState


def get_civic_bosch_modified_torque_lpf_tau(torque_cmd: float, prev_torque_cmd: float, v_ego: float) -> float:
  torque_delta = abs(float(torque_cmd) - float(prev_torque_cmd))
  torque_cmd_abs = abs(float(torque_cmd))
  sign_change = (float(torque_cmd) * float(prev_torque_cmd)) < 0.0
  highway = v_ego > (50.0 * 0.44704)
  low_speed = v_ego < (30.0 * 0.44704)

  if highway:
    if torque_cmd_abs < 0.12:
      return 0.18 if sign_change else 0.16
    if sign_change and torque_delta > 0.15:
      return 0.10
    return 0.12

  if sign_change and torque_cmd_abs < 0.25:
    return 0.28 if low_speed else 0.22

  # Extra damping for the tiny near-center commands where both modified EPS
  # firmwares still show hunting and escalating sway.
  if torque_cmd_abs < 0.12:
    return 0.28 if low_speed else 0.20

  if low_speed:
    if torque_delta > 0.50:
      return 0.14
    elif torque_delta > 0.20:
      return 0.16
    elif torque_delta > 0.05:
      return 0.18
    else:
      return 0.22

  if torque_delta > 0.50:
    return 0.12
  elif torque_delta > 0.20:
    return 0.13
  elif torque_delta > 0.05:
    return 0.15
  else:
    return 0.18


CLARITY_OVERRIDE_FADE_SPEED = 50.0 * 0.44704
CLARITY_OVERRIDE_FADE_UP_S = 2.0
CLARITY_OVERRIDE_LPF_KILL_S = 0.2
CLARITY_OVERRIDE_RELEASE_GRACE_S = 0.20
CLARITY_OVERRIDE_HOLD_S = 0.8
CLARITY_OVERRIDE_STAGE_2_S = 1.5
CLARITY_OVERRIDE_FULL_DROP_S = 2.0
CLARITY_OVERRIDE_HUD_BLINK_HALF_PERIOD_S = 0.50


def get_clarity_override_fade_from_timer(override_timer_s: float) -> float:
  if override_timer_s <= CLARITY_OVERRIDE_HOLD_S:
    return 1.0

  if override_timer_s <= CLARITY_OVERRIDE_STAGE_2_S:
    progress = (
      (override_timer_s - CLARITY_OVERRIDE_HOLD_S) /
      (CLARITY_OVERRIDE_STAGE_2_S - CLARITY_OVERRIDE_HOLD_S)
    )
    return 1.0 - (0.40 * progress)

  if override_timer_s <= CLARITY_OVERRIDE_FULL_DROP_S:
    progress = (
      (override_timer_s - CLARITY_OVERRIDE_STAGE_2_S) /
      (CLARITY_OVERRIDE_FULL_DROP_S - CLARITY_OVERRIDE_STAGE_2_S)
    )
    return 0.60 * (1.0 - progress)

  return 0.0


def update_clarity_override_fade(
  driver_override: bool,
  v_ego: float,
  fade: float,
  override_timer_s: float,
  release_grace_s: float,
) -> tuple[float, float, float, bool]:
  latched_override = driver_override

  if driver_override:
    release_grace_s = 0.0
  elif override_timer_s > 0.0 and release_grace_s < CLARITY_OVERRIDE_RELEASE_GRACE_S:
    release_grace_s = min(CLARITY_OVERRIDE_RELEASE_GRACE_S, release_grace_s + DT_CTRL)
    latched_override = True
  else:
    release_grace_s = CLARITY_OVERRIDE_RELEASE_GRACE_S

  if latched_override:
    if v_ego >= CLARITY_OVERRIDE_FADE_SPEED:
      return 0.0, CLARITY_OVERRIDE_FULL_DROP_S, release_grace_s, True

    override_timer_s = min(CLARITY_OVERRIDE_FULL_DROP_S, override_timer_s + DT_CTRL)
    return get_clarity_override_fade_from_timer(override_timer_s), override_timer_s, release_grace_s, True

  return min(1.0, fade + DT_CTRL / CLARITY_OVERRIDE_FADE_UP_S), 0.0, release_grace_s, False


def get_clarity_override_lpf_kill(driver_override: bool, lpf_kill: float) -> float:
  if driver_override:
    return min(1.0, lpf_kill + DT_CTRL / CLARITY_OVERRIDE_LPF_KILL_S)

  return 0.0


def get_clarity_override_hud_lanes(
  clarity_active: bool,
  torque_applied: bool,
  lanes_visible: bool,
  steering_available: bool,
  override_latched: bool,
  override_zeroed: bool,
  override_timer_s: float,
  override_fade: float,
  frame: int,
) -> tuple[bool, bool]:
  # Three-state LKAS HUD model:
  # 1. No lines: lateral control was intentionally disabled by the user/system.
  # 2. Dashed lines: lateral control exists, but no steering torque is currently being applied.
  # 3. Solid lines: steering torque is actively being applied.
  if not lanes_visible:
    return False, False

  solid_lanes = bool(torque_applied)
  dashed_lanes = not solid_lanes

  if not clarity_active:
    return solid_lanes, dashed_lanes

  ramping_down = override_latched and not override_zeroed
  ramping_back_in = 0.0 < override_fade < 1.0 and not override_latched

  if ramping_down or ramping_back_in:
    blink_lanes = (int((frame * DT_CTRL) / CLARITY_OVERRIDE_HUD_BLINK_HALF_PERIOD_S) % 2) == 0
    return blink_lanes, not blink_lanes

  if override_zeroed:
    return False, True

  return solid_lanes, dashed_lanes


def apply_torque_lpf(torque_cmd: float, prev_torque_cmd: float, torque_lpf: float, v_ego: float, tau_kill: float = 0.0) -> tuple[float, float]:
  tau = get_civic_bosch_modified_torque_lpf_tau(torque_cmd, prev_torque_cmd, v_ego)
  tau *= max(0.0, 1.0 - tau_kill)
  alpha = DT_CTRL / (tau + DT_CTRL)
  torque_lpf = alpha * torque_cmd + ((1.0 - alpha) * torque_lpf)
  return torque_lpf, torque_cmd


def get_civic_bosch_modified_steering_pressed(
  raw_pressed: bool, steering_torque: float, torque_cmd: float, filter_s: float, was_pressed: bool
) -> tuple[float, bool]:
  torque_product = steering_torque * torque_cmd
  torque_cmd_abs = abs(torque_cmd)

  if raw_pressed:
    if torque_product < 0.0:
      trigger_s = 0.08 if was_pressed else 0.10
      rise_rate = 1.0
    elif torque_cmd_abs < 0.10:
      trigger_s = 0.20 if was_pressed else 0.24
      rise_rate = 0.75
    else:
      trigger_s = 0.70 if was_pressed else 0.80
      rise_rate = 0.50

    filter_s = min(1.0, filter_s + (rise_rate * DT_CTRL))
    steering_pressed = filter_s >= trigger_s
  else:
    filter_s = max(0.0, filter_s - 8.0 * DT_CTRL)
    steering_pressed = filter_s > 0.04 and was_pressed

  return filter_s, steering_pressed


def get_honda_bosch_wind_brake_mps2(v_ego: float) -> float:
  return float(np.interp(v_ego, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441]))


def update_honda_bosch_live_learning(
  gas_factor: float,
  wind_factor: float,
  wind_factor_before_brake: float,
  desired_accel: float,
  actual_accel: float,
  gas_pedal_force: float,
  wind_brake_mps2: float,
  brake_pressed: bool,
  v_ego: float,
) -> tuple[float, float, float]:
  accel_error = desired_accel - actual_accel

  if accel_error != 0.0 and gas_pedal_force > 0.0:
    gas_factor = float(np.clip(gas_factor + accel_error / 50.0 * gas_pedal_force, 0.1, 3.0))

  if accel_error != 0.0 and not brake_pressed and v_ego > 0.0:
    wind_adjust = 1.0 + wind_brake_mps2 / 1000.0
    if accel_error > 0.0:
      wind_factor = float(np.clip(wind_factor * wind_adjust, 0.1, 3.0))
    else:
      wind_factor = float(np.clip(wind_factor / wind_adjust, 0.1, 3.0))

  if gas_pedal_force <= 0.0:
    wind_factor = max(wind_factor, wind_factor_before_brake)
  else:
    wind_factor_before_brake = wind_factor

  return gas_factor, wind_factor, wind_factor_before_brake


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
  brake_hyst_on = 0.02  # to activate brakes exceed this value
  brake_hyst_off = 0.005  # to deactivate brakes below this value
  brake_hyst_gap = 0.01  # don't change the brake command for small oscillations within this value

  # *** hysteresis logic to avoid brake blinking. go above 0.1 to trigger
  if (brake < brake_hyst_on and not braking) or brake < brake_hyst_off:
    brake = 0.0
  braking = brake > 0.0

  # for small brake oscillations within brake_hyst_gap, don't change the brake command
  if brake == 0.0:
    brake_steady = 0.0
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
  if apply_brake > apply_brake_last or (ts - last_pump_ts > 20.0 and apply_brake > 0):
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


class CarController(CarControllerBase):
  def __init__(self, dbc_names, CP):
    super().__init__(dbc_names, CP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)
    self.tja_control = CP.carFingerprint in HONDA_BOSCH_TJA_CONTROL

    self.braking = False
    self.brake_steady = 0.0
    self.brake_last = 0.0
    self.apply_brake_last = 0
    self.last_pump_ts = 0.0
    self.stopping_counter = 0

    self.accel = 0.0
    self.speed = 0.0
    self.gas = 0.0
    self.brake = 0.0
    self.last_torque = 0.0
    self.torque_lpf = 0.0
    self.prev_torque_cmd = 0.0
    self.steering_pressed_filter_s = 0.0
    self.steering_pressed_robust_prev = False
    self.is_clarity_eps_modified = CP.carFingerprint == CAR.HONDA_CLARITY and bool(CP.flags & HondaFlags.EPS_MODIFIED)
    self.clarity_driver_override_fade = 1.0
    self.clarity_driver_override_timer = 0.0
    self.clarity_driver_override_release_grace_s = CLARITY_OVERRIDE_RELEASE_GRACE_S
    self.clarity_driver_override_lpf_kill = 0.0
    self.clarity_driver_override_zeroed = False
    self.clarity_driver_override_latched = False
    self.bosch_gas_factor = 1.0
    self.bosch_wind_factor = 1.0
    self.bosch_wind_factor_before_brake = 0.0
    self.pitch = 0.0

  def _modified_civic_standard_active(self) -> bool:
    return self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH and bool(self.CP.flags & HondaFlags.EPS_MODIFIED)

  def _filtered_steering_pressed(self, CS, torque_cmd: float) -> bool:
    self.steering_pressed_filter_s, steering_pressed = get_civic_bosch_modified_steering_pressed(
      bool(CS.out.steeringPressed),
      float(getattr(CS.out, "steeringTorque", 0.0)),
      float(torque_cmd),
      self.steering_pressed_filter_s,
      self.steering_pressed_robust_prev,
    )
    self.steering_pressed_robust_prev = steering_pressed
    return steering_pressed

  def update(self, CC, CS, now_nanos, starpilot_toggles):
    actuators = CC.actuators
    hud_control = CC.hudControl
    hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if hud_control.speedVisible else 255
    pcm_cancel_cmd = CC.cruiseControl.cancel
    if len(CC.orientationNED) == 3:
      self.pitch = CC.orientationNED[1]
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY

    if CC.longActive:
      accel = actuators.accel
      gas, brake = compute_gas_brake(actuators.accel, CS.out.vEgo, self.CP.carFingerprint)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0

    torque_cmd = float(actuators.torque)
    filtered_steering_pressed = bool(CS.out.steeringPressed)
    if self._modified_civic_standard_active():
      if CC.latActive:
        filtered_steering_pressed = self._filtered_steering_pressed(CS, torque_cmd)
        if filtered_steering_pressed:
          self.torque_lpf = 0.0
          self.prev_torque_cmd = 0.0
          torque_cmd = 0.0
        else:
          tau = get_civic_bosch_modified_torque_lpf_tau(torque_cmd, self.prev_torque_cmd, CS.out.vEgo)
          alpha = DT_CTRL / (tau + DT_CTRL)
          self.torque_lpf = alpha * torque_cmd + ((1.0 - alpha) * self.torque_lpf)
          self.prev_torque_cmd = torque_cmd
          torque_cmd = self.torque_lpf
      else:
        self.torque_lpf = 0.0
        self.prev_torque_cmd = 0.0
        self.steering_pressed_filter_s = 0.0
        self.steering_pressed_robust_prev = False
    elif self.is_clarity_eps_modified:
      if CC.latActive:
        filtered_steering_pressed = self._filtered_steering_pressed(CS, torque_cmd)
        self.clarity_driver_override_fade, self.clarity_driver_override_timer, self.clarity_driver_override_release_grace_s, self.clarity_driver_override_latched = update_clarity_override_fade(
          filtered_steering_pressed,
          CS.out.vEgo,
          self.clarity_driver_override_fade,
          self.clarity_driver_override_timer,
          self.clarity_driver_override_release_grace_s,
        )
        self.clarity_driver_override_lpf_kill = get_clarity_override_lpf_kill(
          self.clarity_driver_override_latched, self.clarity_driver_override_lpf_kill
        )

        torque_cmd *= self.clarity_driver_override_fade
        self.torque_lpf, self.prev_torque_cmd = apply_torque_lpf(
          torque_cmd, self.prev_torque_cmd, self.torque_lpf, CS.out.vEgo, self.clarity_driver_override_lpf_kill
        )
        torque_cmd = self.torque_lpf
        self.clarity_driver_override_zeroed = self.clarity_driver_override_latched and self.clarity_driver_override_fade <= 0.001
      else:
        self.torque_lpf = 0.0
        self.prev_torque_cmd = 0.0
        self.steering_pressed_filter_s = 0.0
        self.steering_pressed_robust_prev = False
        self.clarity_driver_override_fade = 1.0
        self.clarity_driver_override_timer = 0.0
        self.clarity_driver_override_release_grace_s = CLARITY_OVERRIDE_RELEASE_GRACE_S
        self.clarity_driver_override_lpf_kill = 0.0
        self.clarity_driver_override_zeroed = False
        self.clarity_driver_override_latched = False

    # *** rate limit steer ***
    limited_torque = rate_limit(torque_cmd, self.last_torque, -self.params.STEER_DELTA_DOWN * DT_CTRL, self.params.STEER_DELTA_UP * DT_CTRL)
    self.last_torque = limited_torque

    # *** apply brake hysteresis ***
    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(brake, self.braking, self.brake_steady, CS.out.vEgo, self.CP.carFingerprint)

    # *** rate limit after the enable check ***
    self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2.0, DT_CTRL)

    # vehicle hud display, wait for one update from 10Hz 0x304 msg
    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    # **** process the car messages ****

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_torque = int(np.interp(-limited_torque * self.params.STEER_MAX, self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    # Send CAN commands
    can_sends = []

    # tester present - w/ no response (keeps radar disabled)
    if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.frame % 10 == 0:
        can_sends.append(make_tester_present_msg(0x18DAB0F1, 1, suppress_response=True))

    # Send steering command.
    lkas_active = CC.latActive and CS.out.cruiseState.available and not self.clarity_driver_override_zeroed

    can_sends.append(hondacan.create_steering_control(
      self.packer, self.CAN, apply_torque, lkas_active, self.tja_control
    ))

    # wind brake from air resistance decel at high speed
    wind_brake = np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15])
    # all of this is only relevant for HONDA NIDEC
    max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
    # TODO this 1.44 is just to maintain previous behavior
    pcm_speed_BP = [-wind_brake, -wind_brake * (3 / 4), 0.0, 0.5]
    # The Honda ODYSSEY seems to have different PCM_ACCEL
    # msgs, is it other cars too?
    if self.CP.enableGasInterceptorDEPRECATED or not CC.longActive:
      pcm_speed = 0.0
      pcm_accel = int(0.0)
    elif self.CP.carFingerprint in HONDA_NIDEC_ALT_PCM_ACCEL:
      pcm_speed_V = [0.0, np.clip(CS.out.vEgo - 3.0, 0.0, 100.0), np.clip(CS.out.vEgo + 0.0, 0.0, 100.0), np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(1.0 * self.params.NIDEC_GAS_MAX)
    else:
      pcm_speed_V = [0.0, np.clip(CS.out.vEgo - 2.0, 0.0, 100.0), np.clip(CS.out.vEgo + 2.0, 0.0, 100.0), np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
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
          self.accel = float(np.clip(accel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = self.accel
          if self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
            wind_brake_mps2 = get_honda_bosch_wind_brake_mps2(CS.out.vEgo)
            if (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
              gas_pedal_force += wind_brake_mps2 * self.bosch_wind_factor + hill_brake
              self.bosch_gas_factor, self.bosch_wind_factor, self.bosch_wind_factor_before_brake = update_honda_bosch_live_learning(
                self.bosch_gas_factor,
                self.bosch_wind_factor,
                self.bosch_wind_factor_before_brake,
                self.accel,
                CS.out.aEgo,
                gas_pedal_force,
                wind_brake_mps2,
                bool(CS.out.brakePressed),
                CS.out.vEgo,
              )
            else:
              gas_pedal_force += wind_brake_mps2 + hill_brake

          self.gas = float(np.interp(gas_pedal_force * self.bosch_gas_factor, self.params.BOSCH_GAS_LOOKUP_BP, self.params.BOSCH_GAS_LOOKUP_V))

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          can_sends.extend(
            hondacan.create_acc_commands(self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas, self.stopping_counter, self.CP.carFingerprint)
          )
        else:
          apply_brake = np.clip(self.brake_last - wind_brake, 0.0, 1.0)
          apply_brake = int(np.clip(apply_brake * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))

          if self.frame % 20 == 0:
            print(
              "HONDA_LONG_DEBUG",
              "enabled=", CC.enabled,
              "longActive=", CC.longActive,
              "act_state=", actuators.longControlState,
              "accel=", float(accel),
              "gas=", float(gas),
              "brake=", float(brake),
              "brake_last=", float(self.brake_last),
              "wind_brake=", float(wind_brake),
              "apply_brake=", int(apply_brake),
              "pedal_enabled=", self.CP.enableGasInterceptorDEPRECATED,
            )

          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          pcm_override = True
          can_sends.append(
            hondacan.create_brake_command(
              self.packer, self.CAN, apply_brake, pump_on, pcm_override, pcm_cancel_cmd, alert_fcw, self.CP.carFingerprint, CS.stock_brake
            )
          )
          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

          if self.CP.enableGasInterceptorDEPRECATED:
            # Way too aggressive at low speed without this.
            gas_mult = np.interp(CS.out.vEgo, [0.0, 10.0], [0.4, 1.0])
            # Send exactly zero if apply_gas is zero. Interceptor will send the max between read value and apply_gas.
            # This prevents unexpected pedal range rescaling.
            # Sending non-zero gas when OP is not enabled will cause the PCM not to respond to throttle as expected
            # when you do enable.
            if CC.longActive:
              self.gas = float(np.clip(gas_mult * (gas - brake + wind_brake * 3 / 4), 0.0, 1.0))
            else:
              self.gas = 0.0

            if self.frame % 20 == 0:
              print(
                "HONDA_PEDAL_DEBUG",
                "self.gas=", float(self.gas),
                "frame=", self.frame,
                "idx=", self.frame // 2,
              )

            can_sends.append(create_gas_interceptor_command(self.packer, self.gas, self.frame // 2))

    # Send dashboard UI commands.
    if self.frame % 10 == 0:
      if self.CP.openpilotLongitudinalControl:
        # On Nidec, this also controls longitudinal positive acceleration
        can_sends.append(
          hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel, hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud)
        )

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > self.CP.minSteerSpeed
      reduced_steering = filtered_steering_pressed
      torque_applied = bool(lkas_active) and abs(apply_torque) > 0
      solid_lanes, dashed_lanes = get_clarity_override_hud_lanes(
        self.is_clarity_eps_modified,
        torque_applied,
        bool(hud_control.lanesVisible),
        bool(steering_available),
        self.clarity_driver_override_latched,
        self.clarity_driver_override_zeroed,
        self.clarity_driver_override_timer,
        self.clarity_driver_override_fade,
        self.frame,
      )
      can_sends.extend(
        hondacan.create_lkas_hud(
          self.packer, self.CAN.lkas, self.CP, hud_control, solid_lanes, steering_available,
          reduced_steering, alert_steer_required, CS.lkas_hud, dashed_lanes=dashed_lanes
        )
      )

      if self.CP.openpilotLongitudinalControl:
        # TODO: combining with create_acc_hud block above will change message order and will need replay logs regenerated
        if self.CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS):
          can_sends.append(hondacan.create_radar_hud(self.packer, self.CAN.pt))
        if self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH:
          can_sends.append(hondacan.create_legacy_brake_command(self.packer, self.CAN.pt))
        if self.CP.carFingerprint not in HONDA_BOSCH:
          self.speed = pcm_speed
          if not self.CP.enableGasInterceptorDEPRECATED:
            self.gas = pcm_accel / self.params.NIDEC_GAS_MAX

    new_actuators = actuators.as_builder()
    new_actuators.speed = self.speed
    new_actuators.accel = self.accel
    new_actuators.gas = self.gas
    new_actuators.brake = self.brake
    new_actuators.torque = self.last_torque
    new_actuators.torqueOutputCan = apply_torque

    self.frame += 1
    return new_actuators, can_sends
