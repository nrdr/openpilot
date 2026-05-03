from dataclasses import dataclass

import numpy as np
from opendbc.can import CANPacker
from opendbc.car import Bus, DT_CTRL, make_tester_present_msg, structs
from opendbc.car.lateral import apply_driver_steer_torque_limits, apply_steer_angle_limits_vm, common_fault_avoidance
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.hyundai import hyundaicanfd, hyundaican
from opendbc.car.hyundai.hyundaicanfd import CanBus
from opendbc.car.hyundai.values import HyundaiFlags, Buttons, CarControllerParams, CAR
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.params import Params

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState

# EPS faults if you apply torque while the steering angle is above 90 degrees for more than 1 second
# All slightly below EPS thresholds to avoid fault
MAX_ANGLE = 85
MAX_ANGLE_FRAMES = 89
MAX_ANGLE_CONSECUTIVE_FRAMES = 2
CANFD_BLINDSPOT_STATUS_STALE_NS = 200_000_000
CANFD_BLINKER_STALKS_STALE_NS = 200_000_000
HYUNDAI_CANFD_SCC_ACCEL_STEP = 5.0 / 50.0
HYUNDAI_CANFD_SCC_DECEL_STEP = 12.5 / 50.0
IONIQ_6_RESPONSE_MULTIPLIER = 1.2
IONIQ_6_CANFD_SCC_ACCEL_STEP = (6.0 / 50.0) * IONIQ_6_RESPONSE_MULTIPLIER
IONIQ_6_CANFD_SCC_DECEL_STEP = (15.0 / 50.0) * IONIQ_6_RESPONSE_MULTIPLIER
GENESIS_G90_STOP_HOLD_SPEED_BP = [0.0, 0.03, 0.08, 0.16, 0.3, 0.5, 0.8, 1.2, 2.0, 3.0]
GENESIS_G90_STOP_HOLD_ACCEL_V = [-0.10, -0.10, -0.12, -0.18, -0.30, -0.50, -0.75, -1.00, -1.40, -1.80]
GENESIS_G90_STOP_HOLD_RELAX_SPEED_BP = [0.0, 0.08, 0.16, 0.3, 0.5, 0.8, 1.2, 2.0, 3.0]
GENESIS_G90_STOP_HOLD_RELAX_STEP_V = [0.10, 0.10, 0.08, 0.06, 0.04, 0.035, 0.03, 0.022, 0.018]
GENESIS_G90_RELEASE_SPEED_BP = [0.0, 0.3, 0.6]
GENESIS_G90_RELEASE_ACCEL_STEP_V = [0.05, 0.07, 0.11]
GENESIS_G90_RELEASE_DECEL_STEP_V = [0.16, 0.18, 0.18]
GENESIS_G90_RELEASE_MAX_SPEED = 0.8
IONIQ_6_LONG_MIN_JERK = 0.5 * IONIQ_6_RESPONSE_MULTIPLIER
IONIQ_6_LONG_JERK_LIMIT = 4.8 * IONIQ_6_RESPONSE_MULTIPLIER
IONIQ_6_LONG_LOOKAHEAD_JERK_BP = [2.0, 5.0, 20.0]
IONIQ_6_LONG_LOOKAHEAD_JERK_V = [0.3 / IONIQ_6_RESPONSE_MULTIPLIER,
                                 0.45 / IONIQ_6_RESPONSE_MULTIPLIER,
                                 0.6 / IONIQ_6_RESPONSE_MULTIPLIER]
IONIQ_6_DYNAMIC_LOWER_JERK_BP = [-2.0, -1.5, -1.0, -0.25, -0.1, -0.025, -0.01, -0.005]
IONIQ_6_DYNAMIC_LOWER_JERK_V = [3.3, 1.5, 1.0, 0.8, 0.7, 0.65, 0.55, 0.5]
IONIQ_6_LAUNCH_HOLD_SPEED_BP = [0.0, 0.6, 1.25, 2.5]
IONIQ_6_LAUNCH_HOLD_SPEED_V = [0.75, 0.6, 0.4, 0.0]
IONIQ_6_STOP_HOLD_SPEED_BP = [0.0, 0.08, 0.25, 0.6, 1.2]
IONIQ_6_STOP_HOLD_SPEED_V = [-0.09, -0.095, -0.10, -0.05, 0.0]
IONIQ_6_STOP_HOLD_JERK_BP = [0.0, 0.15, 0.6, 1.2]
IONIQ_6_STOP_HOLD_JERK_V = [0.35, 0.40, 0.52, 0.65]
IONIQ_6_STOP_RELEASE_JERK_BP = [0.0, 0.15, 0.5]
IONIQ_6_STOP_RELEASE_JERK_V = [3.6 * IONIQ_6_RESPONSE_MULTIPLIER,
                               4.2 * IONIQ_6_RESPONSE_MULTIPLIER,
                               4.8 * IONIQ_6_RESPONSE_MULTIPLIER]


@dataclass
class Ioniq6LongitudinalTuningState:
  desired_accel: float = 0.0
  actual_accel: float = 0.0
  accel_last: float = 0.0
  jerk_upper: float = 0.0
  jerk_lower: float = 0.0
  launch_active: bool = False
  stopping: bool = False
  stopping_count: int = 0
  long_control_state_last: LongCtrlState = LongCtrlState.off


@dataclass
class GenesisG90LongitudinalTuningState:
  actual_accel: float = 0.0
  release_active: bool = False
  long_control_state_last: LongCtrlState = LongCtrlState.off


def _jerk_limited_integrator(desired_accel: float, last_accel: float, jerk_upper: float, jerk_lower: float) -> float:
  step = (jerk_upper if desired_accel >= last_accel else jerk_lower) * DT_CTRL * 5.0
  return float(np.clip(desired_accel, last_accel - step, last_accel + step))


def _calculate_ioniq_6_dynamic_lower_jerk(accel_error: float) -> float:
  if accel_error < 0.0:
    scaled_values = np.array(IONIQ_6_DYNAMIC_LOWER_JERK_V) * (IONIQ_6_LONG_JERK_LIMIT / IONIQ_6_DYNAMIC_LOWER_JERK_V[0])
    return float(np.interp(accel_error, IONIQ_6_DYNAMIC_LOWER_JERK_BP, scaled_values))
  return IONIQ_6_LONG_MIN_JERK


def update_ioniq_6_longitudinal_tuning(state: Ioniq6LongitudinalTuningState, accel_cmd: float, v_ego: float, a_ego: float,
                                       long_control_state: LongCtrlState, long_active: bool) -> Ioniq6LongitudinalTuningState:
  starting = long_control_state == LongCtrlState.starting
  stopping = long_control_state == LongCtrlState.stopping
  restart_from_stop = state.long_control_state_last in (LongCtrlState.stopping, LongCtrlState.starting) and \
                      long_control_state in (LongCtrlState.starting, LongCtrlState.pid) and accel_cmd > 0.0 and v_ego < 0.5

  if not long_active or not stopping:
    state.stopping = False
    state.stopping_count = 0
  elif state.long_control_state_last == LongCtrlState.off:
    state.stopping = True
  else:
    if state.stopping_count > 1 / (DT_CTRL * 5):
      state.stopping = True
    state.stopping_count += 1

  if not long_active:
    state.desired_accel = 0.0
    state.actual_accel = 0.0
    state.accel_last = 0.0
    state.jerk_upper = 0.0
    state.jerk_lower = 0.0
    state.launch_active = False
    state.long_control_state_last = long_control_state
    return state

  if accel_cmd <= 0.0 or v_ego >= IONIQ_6_LAUNCH_HOLD_SPEED_BP[-1]:
    state.launch_active = False
  elif starting or (state.launch_active and v_ego < IONIQ_6_LAUNCH_HOLD_SPEED_BP[-1]) or \
      (state.long_control_state_last == LongCtrlState.starting and long_control_state == LongCtrlState.pid and v_ego < IONIQ_6_LAUNCH_HOLD_SPEED_BP[-1]):
    state.launch_active = True

  upper_speed_limit = float(np.interp(v_ego, [0.0, 5.0, 20.0], [2.0, 3.0, 2.0])) * IONIQ_6_RESPONSE_MULTIPLIER if long_control_state == LongCtrlState.pid else IONIQ_6_LONG_MIN_JERK
  lower_speed_limit = float(np.interp(v_ego, [0.0, 5.0, 20.0], [5.0, 3.5, 3.0])) * IONIQ_6_RESPONSE_MULTIPLIER

  future_t_upper = float(np.interp(v_ego, IONIQ_6_LONG_LOOKAHEAD_JERK_BP, IONIQ_6_LONG_LOOKAHEAD_JERK_V))
  future_t_lower = float(np.interp(v_ego, IONIQ_6_LONG_LOOKAHEAD_JERK_BP, IONIQ_6_LONG_LOOKAHEAD_JERK_V))

  accel_error = accel_cmd - state.accel_last
  j_ego_upper = float(np.clip(accel_error / future_t_upper, -IONIQ_6_LONG_JERK_LIMIT, IONIQ_6_LONG_JERK_LIMIT))
  j_ego_lower = float(np.clip(accel_error / future_t_lower, -IONIQ_6_LONG_JERK_LIMIT, IONIQ_6_LONG_JERK_LIMIT))
  desired_jerk_upper = min(max(j_ego_upper, IONIQ_6_LONG_MIN_JERK), upper_speed_limit)

  dynamic_accel_error = a_ego - state.accel_last
  dynamic_lower_jerk = _calculate_ioniq_6_dynamic_lower_jerk(dynamic_accel_error)
  state.jerk_upper = desired_jerk_upper
  state.jerk_lower = min(dynamic_lower_jerk, lower_speed_limit)

  if state.stopping:
    state.desired_accel = float(np.interp(v_ego, IONIQ_6_STOP_HOLD_SPEED_BP, IONIQ_6_STOP_HOLD_SPEED_V))
    state.jerk_upper = min(state.jerk_upper, float(np.interp(v_ego, IONIQ_6_STOP_HOLD_JERK_BP, IONIQ_6_STOP_HOLD_JERK_V)) * IONIQ_6_RESPONSE_MULTIPLIER)
  else:
    state.desired_accel = float(np.clip(accel_cmd, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))
    if state.launch_active:
      state.desired_accel = max(state.desired_accel, float(np.interp(v_ego, IONIQ_6_LAUNCH_HOLD_SPEED_BP, IONIQ_6_LAUNCH_HOLD_SPEED_V)))
      state.jerk_upper = max(state.jerk_upper, float(np.interp(v_ego, [0.0, 2.5], [4.8, 3.2])) * IONIQ_6_RESPONSE_MULTIPLIER)
      state.jerk_lower = max(state.jerk_lower, 1.0)
    if restart_from_stop:
      state.jerk_upper = min(state.jerk_upper, float(np.interp(v_ego, IONIQ_6_STOP_RELEASE_JERK_BP, IONIQ_6_STOP_RELEASE_JERK_V)))

  state.actual_accel = _jerk_limited_integrator(state.desired_accel, state.accel_last, state.jerk_upper, state.jerk_lower)
  state.accel_last = state.actual_accel
  state.long_control_state_last = long_control_state
  return state


def update_genesis_g90_longitudinal_tuning(state: GenesisG90LongitudinalTuningState, accel_cmd: float, v_ego: float,
                                           long_control_state: LongCtrlState, long_active: bool) -> GenesisG90LongitudinalTuningState:
  if not long_active:
    state.actual_accel = 0.0
    state.release_active = False
    state.long_control_state_last = long_control_state
    return state

  stopping = long_control_state == LongCtrlState.stopping
  if stopping and v_ego <= GENESIS_G90_STOP_HOLD_SPEED_BP[-1]:
    state.release_active = False
    stop_brake_cap = float(np.interp(v_ego, GENESIS_G90_STOP_HOLD_SPEED_BP, GENESIS_G90_STOP_HOLD_ACCEL_V))
    target_hold = min(0.0, max(accel_cmd, stop_brake_cap))
    if state.actual_accel < target_hold:
      relax_step = float(np.interp(v_ego, GENESIS_G90_STOP_HOLD_RELAX_SPEED_BP, GENESIS_G90_STOP_HOLD_RELAX_STEP_V))
      state.actual_accel = min(state.actual_accel + relax_step, target_hold)
    else:
      state.actual_accel = target_hold
  else:
    if state.long_control_state_last == LongCtrlState.stopping and long_control_state == LongCtrlState.pid and \
        accel_cmd > 0.0 and v_ego < GENESIS_G90_RELEASE_MAX_SPEED:
      state.release_active = True

    if state.release_active:
      accel_step = float(np.interp(v_ego, GENESIS_G90_RELEASE_SPEED_BP, GENESIS_G90_RELEASE_ACCEL_STEP_V))
      decel_step = float(np.interp(v_ego, GENESIS_G90_RELEASE_SPEED_BP, GENESIS_G90_RELEASE_DECEL_STEP_V))
      state.actual_accel = float(np.clip(accel_cmd, state.actual_accel - decel_step, state.actual_accel + accel_step))
      if v_ego >= GENESIS_G90_RELEASE_MAX_SPEED or accel_cmd <= 0.0 or state.actual_accel >= accel_cmd - 1e-3:
        state.release_active = False
    else:
      state.actual_accel = accel_cmd

  state.long_control_state_last = long_control_state
  return state


def process_hud_alert(enabled, fingerprint, hud_control):
  sys_warning = (hud_control.visualAlert in (VisualAlert.steerRequired, VisualAlert.ldw))

  # initialize to no line visible
  # TODO: this is not accurate for all cars
  sys_state = 1
  if hud_control.leftLaneVisible and hud_control.rightLaneVisible or sys_warning:  # HUD alert only display when LKAS status is active
    sys_state = 3 if enabled or sys_warning else 4
  elif hud_control.leftLaneVisible:
    sys_state = 5
  elif hud_control.rightLaneVisible:
    sys_state = 6

  # initialize to no warnings
  left_lane_warning = 0
  right_lane_warning = 0
  if hud_control.leftLaneDepart:
    left_lane_warning = 1 if fingerprint in (CAR.GENESIS_G90, CAR.GENESIS_G80) else 2
  if hud_control.rightLaneDepart:
    right_lane_warning = 1 if fingerprint in (CAR.GENESIS_G90, CAR.GENESIS_G80) else 2

  return sys_warning, sys_state, left_lane_warning, right_lane_warning


class CarController(CarControllerBase):
  def __init__(self, dbc_names, CP):
    super().__init__(dbc_names, CP)
    self.CAN = CanBus(CP)
    self.params = CarControllerParams(CP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.angle_limit_counter = 0
    self.VM = VehicleModel(CP)

    self.accel_last = 0
    self.apply_torque_last = 0
    self.apply_angle_last = 0.0
    self.car_fingerprint = CP.carFingerprint
    self.last_button_frame = 0
    self.ecu_disable_failed = False
    self._ecu_disable_checked = False
    self._params = Params()
    self.long_active_ecu = self.CP.openpilotLongitudinalControl
    self._ioniq_6_lane_change_ui_side = None
    self._ioniq_6_lane_change_ui_trigger_frames = 0
    self._ioniq_6_long_tuning = Ioniq6LongitudinalTuningState()
    self._genesis_g90_long_tuning = GenesisG90LongitudinalTuningState()

  def update(self, CC, CS, now_nanos, starpilot_toggles):
    actuators = CC.actuators
    hud_control = CC.hudControl

    self.params = CarControllerParams(self.CP, CS.out.vEgoRaw)
    apply_angle = CS.out.steeringAngleDeg

    if self.CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING:
      desired_angle = float(np.clip(actuators.steeringAngleDeg,
                                    -self.params.ANGLE_LIMITS.STEER_ANGLE_MAX,
                                    self.params.ANGLE_LIMITS.STEER_ANGLE_MAX))
      apply_angle = apply_steer_angle_limits_vm(desired_angle, self.apply_angle_last, CS.out.vEgoRaw,
                                                CS.out.steeringAngleDeg, CC.latActive, self.params, self.VM)

      if CS.out.steeringPressed and abs(CS.out.steeringTorque) > self.params.STEER_THRESHOLD:
        apply_torque = self.params.ANGLE_MIN_TORQUE_REDUCTION_GAIN
      elif CC.latActive and CS.out.vEgoRaw < 0.3:
        apply_torque = self.params.ANGLE_ACTIVE_TORQUE_REDUCTION_GAIN
      else:
        apply_torque = self.params.ANGLE_MAX_TORQUE_REDUCTION_GAIN if CC.latActive else 0.0

      apply_steer_req = CC.latActive and apply_torque > 0.0
      torque_fault = False
      self.apply_angle_last = apply_angle
    else:
      # steering torque
      new_torque = int(round(actuators.torque * self.params.STEER_MAX))
      apply_torque = apply_driver_steer_torque_limits(new_torque, self.apply_torque_last, CS.out.steeringTorque, self.params)

      # >90 degree steering fault prevention
      self.angle_limit_counter, apply_steer_req = common_fault_avoidance(abs(CS.out.steeringAngleDeg) >= MAX_ANGLE, CC.latActive,
                                                                         self.angle_limit_counter, MAX_ANGLE_FRAMES,
                                                                         MAX_ANGLE_CONSECUTIVE_FRAMES)

      if not CC.latActive:
        apply_torque = 0

      # Hold torque with induced temporary fault when cutting the actuation bit
      # FIXME: we don't use this with CAN FD?
      torque_fault = CC.latActive and not apply_steer_req

    self.apply_torque_last = apply_torque

    # accel + longitudinal
    accel_cmd = float(np.clip(actuators.accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))
    accel = accel_cmd
    stopping = actuators.longControlState == LongCtrlState.stopping
    set_speed_in_units = hud_control.setSpeed * (CV.MS_TO_KPH if CS.is_metric else CV.MS_TO_MPH)

    can_sends = []

    # Check EcuDisableFailed once after init() has run
    if not self._ecu_disable_checked and self.frame > 0:
      self.ecu_disable_failed = self._params.get_bool("EcuDisableFailed")
      self._ecu_disable_checked = True

    # When ECU disable was skipped (car started in READY mode), don't send any
    # longitudinal messages - stock ECU is still active and these would conflict
    self.long_active_ecu = self.CP.openpilotLongitudinalControl and not self.ecu_disable_failed

    use_ioniq_6_dynamic_long_tuning = self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6 and self.long_active_ecu and \
                                      actuators.longControlState in (LongCtrlState.starting, LongCtrlState.pid, LongCtrlState.stopping)
    if use_ioniq_6_dynamic_long_tuning and self.frame % 5 == 0:
      self._ioniq_6_long_tuning = update_ioniq_6_longitudinal_tuning(self._ioniq_6_long_tuning, accel_cmd,
                                                                      CS.out.vEgo, CS.out.aEgo,
                                                                      actuators.longControlState, self.long_active_ecu)
    use_ioniq_6_smoothed_accel = use_ioniq_6_dynamic_long_tuning and (
      accel_cmd >= self._ioniq_6_long_tuning.actual_accel or
      self._ioniq_6_long_tuning.launch_active or
      self._ioniq_6_long_tuning.stopping
    )
    if self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6 and self.long_active_ecu:
      if use_ioniq_6_smoothed_accel:
        accel = self._ioniq_6_long_tuning.actual_accel
        stopping = self._ioniq_6_long_tuning.stopping
      elif use_ioniq_6_dynamic_long_tuning:
        accel = float(np.clip(accel_cmd,
                              self.accel_last - IONIQ_6_CANFD_SCC_DECEL_STEP,
                              self.accel_last + IONIQ_6_CANFD_SCC_ACCEL_STEP))
        self._ioniq_6_long_tuning.desired_accel = accel_cmd
        self._ioniq_6_long_tuning.actual_accel = accel
        self._ioniq_6_long_tuning.accel_last = accel
        self._ioniq_6_long_tuning.jerk_upper = 3.0
        self._ioniq_6_long_tuning.jerk_lower = 5.0 if CC.enabled else 1.0
        self._ioniq_6_long_tuning.launch_active = False
        self._ioniq_6_long_tuning.stopping = stopping
        self._ioniq_6_long_tuning.long_control_state_last = actuators.longControlState

    if self.CP.carFingerprint == CAR.GENESIS_G90 and self.long_active_ecu:
      self._genesis_g90_long_tuning = update_genesis_g90_longitudinal_tuning(self._genesis_g90_long_tuning, accel_cmd,
                                                                              CS.out.vEgo, actuators.longControlState,
                                                                              self.long_active_ecu)
      accel = self._genesis_g90_long_tuning.actual_accel

    # *** common hyundai stuff ***

    # tester present - w/ no response (keeps relevant ECU disabled)
    if self.frame % 100 == 0 and not (self.CP.flags & HyundaiFlags.CANFD_CAMERA_SCC) and self.long_active_ecu:
      # for longitudinal control, either radar or ADAS driving ECU
      addr, bus = 0x7d0, self.CAN.ECAN if self.CP.flags & (HyundaiFlags.CANFD | HyundaiFlags.CAN_CANFD_BLENDED) else 0
      if self.CP.flags & HyundaiFlags.CANFD_LKA_STEERING.value:
        addr, bus = 0x730, self.CAN.ECAN
      can_sends.append(make_tester_present_msg(addr, bus, suppress_response=True))

      # for blinkers
      if self.CP.flags & HyundaiFlags.ENABLE_BLINKERS:
        can_sends.append(make_tester_present_msg(0x7b1, self.CAN.ECAN, suppress_response=True))

    # *** CAN/CAN FD specific ***
    if self.CP.flags & HyundaiFlags.CANFD:
      can_sends.extend(self.create_canfd_msgs(now_nanos, apply_steer_req, apply_torque, apply_angle, set_speed_in_units, accel,
                                              stopping, hud_control, CS, CC))
    else:
      can_sends.extend(self.create_can_msgs(apply_steer_req, apply_torque, torque_fault, set_speed_in_units, accel,
                                            stopping, hud_control, actuators, CS, CC))

    new_actuators = actuators.as_builder()
    if self.CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING:
      new_actuators.steeringAngleDeg = apply_angle
      new_actuators.torque = 0
      new_actuators.torqueOutputCan = 0
    else:
      new_actuators.torque = apply_torque / self.params.STEER_MAX
      new_actuators.torqueOutputCan = apply_torque
    new_actuators.accel = accel

    self.frame += 1
    return new_actuators, can_sends

  def create_can_msgs(self, apply_steer_req, apply_torque, torque_fault, set_speed_in_units, accel, stopping, hud_control, actuators, CS, CC):
    can_sends = []
    can_canfd_blended = bool(self.CP.flags & HyundaiFlags.CAN_CANFD_BLENDED)

    # HUD messages
    sys_warning, sys_state, left_lane_warning, right_lane_warning = process_hud_alert(CC.enabled, self.car_fingerprint,
                                                                                      hud_control)

    if can_canfd_blended:
      can_sends.extend(hyundaican.create_lkas11_can_canfd_blended(self.packer, self.frame, self.CP, apply_torque, apply_steer_req,
                                                                  torque_fault, CS.lkas11, sys_warning, sys_state, CC.enabled,
                                                                  hud_control.leftLaneVisible, hud_control.rightLaneVisible,
                                                                  left_lane_warning, right_lane_warning, CS.msg_364))
    else:
      can_sends.append(hyundaican.create_lkas11(self.packer, self.frame, self.CP, apply_torque, apply_steer_req,
                                                torque_fault, CS.lkas11, sys_warning, sys_state, CC.enabled,
                                                hud_control.leftLaneVisible, hud_control.rightLaneVisible,
                                                left_lane_warning, right_lane_warning))

    # Button messages
    if not self.long_active_ecu:
      if CC.cruiseControl.cancel:
        can_sends.append(hyundaican.create_clu11(self.packer, self.frame, CS.clu11, Buttons.CANCEL, self.CP))
      elif CC.cruiseControl.resume:
        # send resume at a max freq of 10Hz
        if (self.frame - self.last_button_frame) * DT_CTRL > 0.1:
          # send 25 messages at a time to increases the likelihood of resume being accepted
          can_sends.extend([hyundaican.create_clu11(self.packer, self.frame, CS.clu11, Buttons.RES_ACCEL, self.CP)] * 25)
          if (self.frame - self.last_button_frame) * DT_CTRL >= 0.15:
            self.last_button_frame = self.frame

    if self.long_active_ecu and can_canfd_blended:
      can_sends.extend(hyundaican.create_radar_aux_messages(self.packer, self.CAN, self.frame))

    if self.frame % 2 == 0 and self.long_active_ecu:
      # TODO: unclear if this is needed
      jerk = 3.0 if actuators.longControlState == LongCtrlState.pid else 1.0
      use_fca = self.CP.flags & HyundaiFlags.USE_FCA.value
      if can_canfd_blended:
        can_sends.extend(hyundaican.create_acc_commands_can_canfd_blended(self.packer, CC.enabled, accel, jerk,
                                                                          int(self.frame / 2), hud_control,
                                                                          set_speed_in_units, stopping,
                                                                          CC.cruiseControl.override, use_fca, self.CP))
      else:
        can_sends.extend(hyundaican.create_acc_commands(self.packer, CC.enabled, accel, jerk, int(self.frame / 2),
                                                        hud_control, set_speed_in_units, stopping,
                                                        CC.cruiseControl.override, use_fca, self.CP))

    # 20 Hz LFA MFA message
    if self.frame % 5 == 0 and self.CP.flags & HyundaiFlags.SEND_LFA.value:
      can_sends.append(hyundaican.create_lfahda_mfc(self.packer, CC.enabled, self.frame, self.CP))

    # 5 Hz ACC options
    if self.frame % 20 == 0 and self.long_active_ecu and not can_canfd_blended:
      can_sends.extend(hyundaican.create_acc_opt(self.packer, self.CP))

    # 2 Hz front radar options
    if self.frame % 50 == 0 and self.long_active_ecu and not can_canfd_blended:
      can_sends.append(hyundaican.create_frt_radar_opt(self.packer))

    return can_sends

  def create_canfd_msgs(self, now_nanos, apply_steer_req, apply_torque, apply_angle, set_speed_in_units, accel, stopping, hud_control, CS, CC):
    can_sends = []

    lka_steering = self.CP.flags & HyundaiFlags.CANFD_LKA_STEERING
    lka_steering_long = lka_steering and self.long_active_ecu
    use_ioniq_6_dynamic_long_tuning = self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6 and self.long_active_ecu and \
                                      CC.actuators.longControlState == LongCtrlState.pid
    use_ioniq_6_smoothed_accel = use_ioniq_6_dynamic_long_tuning and CC.actuators.accel >= self._ioniq_6_long_tuning.actual_accel

    # steering control
    can_sends.extend(hyundaicanfd.create_steering_messages(self.packer, self.CP, self.CAN, CC.enabled,
                                                           apply_steer_req, apply_torque, apply_angle,
                                                           CS.stock_lfa_msg))

    # prevent LFA from activating on LKA steering cars by sending "no lane lines detected" to ADAS ECU
    if self.frame % 5 == 0 and lka_steering:
      can_sends.append(hyundaicanfd.create_suppress_lfa(self.packer, self.CAN, CS.lfa_block_msg,
                                                        self.CP.flags & HyundaiFlags.CANFD_LKA_STEERING_ALT))

    # LFA and HDA icons
    if self.frame % 5 == 0 and (not lka_steering or lka_steering_long):
      can_sends.append(hyundaicanfd.create_lfahda_cluster(self.packer, self.CAN, CC.enabled, CS.stock_lfahda_cluster_msg))

    # blinkers
    if lka_steering and self.CP.flags & HyundaiFlags.ENABLE_BLINKERS:
      can_sends.extend(hyundaicanfd.create_spas_messages(self.packer, self.CAN, CC.leftBlinker, CC.rightBlinker))

    if self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6:
      lane_change_ui_side = None
      if CC.leftBlinker and not CC.rightBlinker:
        lane_change_ui_side = "left"
      elif CC.rightBlinker and not CC.leftBlinker:
        lane_change_ui_side = "right"
      stock_blinker_stalks_live = now_nanos - CS.stock_blinker_stalks_ts <= CANFD_BLINKER_STALKS_STALE_NS

      if lane_change_ui_side != self._ioniq_6_lane_change_ui_side:
        self._ioniq_6_lane_change_ui_side = lane_change_ui_side
        self._ioniq_6_lane_change_ui_trigger_frames = 6 if lane_change_ui_side is not None else 0

      if stock_blinker_stalks_live:
        self._ioniq_6_lane_change_ui_trigger_frames = 0

      if lane_change_ui_side is not None and not stock_blinker_stalks_live:
        trigger = self._ioniq_6_lane_change_ui_trigger_frames > 0
        can_sends.extend(hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(self.CAN, self.frame,
                                                                                   lane_change_ui_side, trigger))
        if self._ioniq_6_lane_change_ui_trigger_frames > 0:
          self._ioniq_6_lane_change_ui_trigger_frames -= 1

    if self.long_active_ecu:
      if lka_steering:
        can_sends.extend(hyundaicanfd.create_adrv_messages(self.packer, self.CAN, self.frame))
      else:
        can_sends.extend(hyundaicanfd.create_fca_warning_light(self.packer, self.CAN, self.frame))
      if self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6 and self.frame % 5 == 0:
        rear_stale = now_nanos - CS.blindspots_rear_corners_ts > CANFD_BLINDSPOT_STATUS_STALE_NS
        front_stale = now_nanos - CS.blindspots_front_corner_1_ts > CANFD_BLINDSPOT_STATUS_STALE_NS
        if CS.blindspots_rear_corners_ts > 0 and CS.blindspots_front_corner_1_ts > 0 and rear_stale and front_stale:
          can_sends.extend(hyundaicanfd.create_blindspot_status_messages(self.packer, self.CAN,
                                                                         CS.blindspots_rear_corners,
                                                                         CS.blindspots_front_corner_1,
                                                                         CS.left_blindspot_from_radar,
                                                                         CS.right_blindspot_from_radar,
                                                                         CC.leftBlinker,
                                                                         CC.rightBlinker))
      if self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6:
        can_sends.extend(hyundaicanfd.create_ioniq_6_cluster_blindspot_messages(self.CAN, self.frame,
                                                                                 CS.left_blindspot_from_radar,
                                                                                 CS.right_blindspot_from_radar,
                                                                                 CC.leftBlinker,
                                                                                 CC.rightBlinker))
      if self.frame % 2 == 0:
        acc_kwargs = {
          "main_mode_acc": int(CS.out.cruiseState.available),
          "direct_accel": True,
          "jerk_lower": 5.0,
          "jerk_upper": 3.0 if CC.actuators.longControlState == LongCtrlState.pid else 1.0,
        }
        if self.CP.carFingerprint == CAR.HYUNDAI_IONIQ_6:
          if use_ioniq_6_smoothed_accel:
            acc_kwargs["jerk_lower"] = self._ioniq_6_long_tuning.jerk_lower
            acc_kwargs["jerk_upper"] = self._ioniq_6_long_tuning.jerk_upper
        can_sends.append(hyundaicanfd.create_acc_control(self.packer, self.CAN, CC.enabled, self.accel_last, accel, stopping, CC.cruiseControl.override,
                                                         set_speed_in_units, hud_control, **acc_kwargs))
        self.accel_last = accel
    else:
      # button presses
      if (self.frame - self.last_button_frame) * DT_CTRL > 0.25:
        # cruise cancel - suppress when stock ACC is the fallback (ECU disable failed),
        # so openpilot doesn't fight/cancel the user's stock cruise
        if CC.cruiseControl.cancel and not self.ecu_disable_failed:
          if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
            can_sends.append(hyundaicanfd.create_acc_cancel(self.packer, self.CP, self.CAN, CS.cruise_info))
            self.last_button_frame = self.frame
          else:
            for _ in range(20):
              can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, self.CAN, CS.buttons_counter + 1, Buttons.CANCEL))
            self.last_button_frame = self.frame

        # cruise standstill resume
        elif CC.cruiseControl.resume:
          if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
            # TODO: resume for alt button cars
            pass
          else:
            for _ in range(20):
              can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, self.CAN, CS.buttons_counter + 1, Buttons.RES_ACCEL))
            self.last_button_frame = self.frame

    return can_sends
