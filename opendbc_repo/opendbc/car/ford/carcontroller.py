import math
from collections import deque
import numpy as np
from cereal import messaging
from openpilot.common.params import Params
from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, apply_hysteresis, structs
from opendbc.car.lateral import AVERAGE_ROAD_ROLL, ISO_LATERAL_ACCEL, apply_std_steer_angle_limits
from opendbc.car.common.pid import PIDController
from opendbc.car.ford import fordcan
from opendbc.car.ford.values import CarControllerParams, FordFlags, CAR
from opendbc.car.interfaces import CarControllerBase, V_CRUISE_MAX

LongCtrlState = structs.CarControl.Actuators.LongControlState
VisualAlert = structs.CarControl.HUDControl.VisualAlert

# CAN FD limits:
# Limit to average banked road since safety doesn't have the roll, higher actual roll lowers lateral acceleration
MAX_LATERAL_ACCEL = ISO_LATERAL_ACCEL - (ACCELERATION_DUE_TO_GRAVITY * AVERAGE_ROAD_ROLL)  # ~2.4 m/s^2


def anti_overshoot(apply_curvature, apply_curvature_last, v_ego):
  diff = 0.1
  tau = 5  # 5s smooths over the overshoot
  dt = DT_CTRL * CarControllerParams.STEER_STEP
  alpha = 1 - np.exp(-dt / tau)

  lataccel = apply_curvature * (v_ego ** 2)
  last_lataccel = apply_curvature_last * (v_ego ** 2)
  last_lataccel = apply_hysteresis(lataccel, last_lataccel, diff)
  last_lataccel = alpha * lataccel + (1 - alpha) * last_lataccel

  output_curvature = last_lataccel / (max(v_ego, 1) ** 2)

  return float(np.interp(v_ego, [5, 10], [apply_curvature, output_curvature]))


def apply_ford_curvature_limits(apply_curvature, apply_curvature_last, current_curvature, v_ego_raw, steering_angle, lat_active, CP, max_lat_accel=None):
  # No blending at low speed due to lack of torque wind-up and inaccurate current curvature
  if v_ego_raw > 9:
    apply_curvature = np.clip(apply_curvature, current_curvature - CarControllerParams.CURVATURE_ERROR,
                              current_curvature + CarControllerParams.CURVATURE_ERROR)

  # Curvature rate limit after driver torque limit
  apply_curvature = apply_std_steer_angle_limits(apply_curvature, apply_curvature_last, v_ego_raw, steering_angle, lat_active, CarControllerParams.ANGLE_LIMITS)

  # Ford Q4/CAN FD has more torque available compared to Q3/CAN so we limit it based on lateral acceleration.
  # Safety is not aware of the road roll so we subtract a conservative amount at all times.
  # max_lat_accel defaults to the conservative stock ceiling; the nrdr OEM lateral path can raise it
  # (NrdrFordMaxLatAccel) to address "runs out of torque" on vigorous cornering.
  if CP.flags & FordFlags.CANFD:
    # Limit curvature to conservative max lateral acceleration
    lat_accel_ceiling = MAX_LATERAL_ACCEL if max_lat_accel is None else max_lat_accel
    curvature_accel_limit = lat_accel_ceiling / (max(v_ego_raw, 1) ** 2)
    apply_curvature = float(np.clip(apply_curvature, -curvature_accel_limit, curvature_accel_limit))

  return apply_curvature


def apply_creep_compensation(accel: float, v_ego: float) -> float:
  creep_accel = np.interp(v_ego, [1., 3.], [0.6, 0.])
  creep_accel = np.interp(accel, [0., 0.2], [creep_accel, 0.])
  accel -= creep_accel
  return float(accel)


# --- nrdr Ford OEM-style lateral (ported from BluePilot bp-6.0, behind NrdrFordOemLateral) ---
# Ford's LateralMotionControl2 carries four signals (curvature, curvature_rate, path_angle, path_offset).
# Stock openpilot drives curvature alone; this fills in curvature_rate + path_angle for OEM-level
# steering authority ("runs out of torque") and adds human-turn handling ("throws me off the road").
# ModelConstants.T_IDXS, hardcoded to keep opendbc decoupled from selfdrive: T_IDXS[i] = (i/32)^2 * 10.
FORD_T_IDXS = [(i / 32.0) ** 2 * 10.0 for i in range(33)]
FORD_CURVATURE_LOOKUP_TIME = 0.42          # [s] how far into the model horizon we read predicted curvature
FORD_PC_BLEND_RATIO = 0.40                 # fraction of predicted (vs desired) curvature in the blend
FORD_CURV_RATE_DELTA_T = 0.3               # [s] denominator window for the curvature-rate derivative
FORD_CURV_RATE_SPEED_BP = [0.0, 14.5, 15.5]
FORD_CURV_RATE_SPEED_V = [1.0, 1.0, 0.0]   # curvature_rate only below ~highway entry, faded out above
FORD_CURV_RATE_PC_BP = [0.0, 0.008, 0.01]
FORD_CURV_RATE_PC_V = [0.0, 0.0, 1.0]      # only apply rate when actually in a curve
FORD_LARGE_CURVE_FACTOR_BP = [0.001, 0.02]
FORD_LARGE_CURVE_FACTOR_V = [1.0, 0.80]    # ease curvature_rate in large curves
FORD_PATH_OFFSET_LOOKUP_TIME = 0.2         # [s] model horizon point for lateral position error
FORD_MIN_LANELINE_CONF_BP = [0.6, 0.8]     # laneline-probability -> influence scale
FORD_LC_PID_SPEED_BP = [0.0, 9.0, 15.0]
FORD_LC_PID_SPEED_V = [0.0, 0.0, 1.0]      # lane-centering only engages above ~15 m/s
FORD_LC_PATH_ANGLE_ROC_BP = [5, 15, 25]
FORD_LC_PATH_ANGLE_ROC_V = [0.003, 0.0015, 0.002]  # per-step path_angle rate limit (matches panda)
FORD_LC_PATH_ANGLE_RESET_FRAMES = 30       # 1.5 s * 20 Hz of sustained steer -> reset the centering PID
FORD_LANE_CHANGE_FACTOR_BP = [4.4, 40.23]
FORD_LANE_CHANGE_FACTOR_V = [0.95, 0.85]   # soften curvature into an auto lane change
FORD_HUMAN_TURN_ANGLE = 45.0               # [deg] held-wheel angle that counts as a human turn
FORD_PATH_ANGLE_MAX = 0.5                  # dbc signal range
FORD_PATH_OFFSET_MAX = 2.0
FORD_CURVATURE_MAX = 0.02
FORD_CURVATURE_RATE_MAX = 0.001023
FORD_POST_LC_FRAMES = 160                  # smoothing window after a lane change completes
FORD_MAX_PATH_ANGLE_CHANGE = 0.00125       # per-step clamps during post-lane-change smoothing
FORD_MAX_PATH_OFFSET_CHANGE = 0.00125
FORD_MAX_CURVATURE_RATE_CHANGE = 0.0001
FORD_LAT_PARAM_STEP = 50                   # re-read params every 50 frames (~0.5 s)


def _ford_get_bool(params, key, default=False):
  # Any failure (unregistered key on an un-rebuilt params lib, etc.) -> default, never crash.
  try:
    value = params.get(key)
    if value is None:
      return default
    return params.get_bool(key)
  except Exception:
    return default


def _ford_get_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  try:
    value = params.get(key)
  except Exception:
    value = None
  if value is None:
    ret = default
  else:
    try:
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


class CarController(CarControllerBase):
  def __init__(self, dbc_names, CP, CP_SP):
    super().__init__(dbc_names, CP, CP_SP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.CAN = fordcan.CanBus(CP)

    self.apply_curvature_last = 0
    self.anti_overshoot_curvature_last = 0
    self.accel = 0.0
    self.gas = 0.0
    self.brake_request = False
    self.main_on_last = False
    self.lkas_enabled_last = False
    self.steer_alert_last = False
    self.lead_distance_bars_last = None
    self.distance_bar_frame = 0

    # --- nrdr Ford OEM-style lateral (behind NrdrFordOemLateral, default OFF) ---
    self.param_reader = Params()
    self._ford_lat_param_frame = 0
    self.ford_oem_lateral = False
    self.ford_human_turn = True
    self.ford_lane_positioning = True
    self.ford_lane_pos_gain = 1.0
    self.ford_max_lat_accel = MAX_LATERAL_ACCEL
    self._read_ford_lat_params()

    # modelV2 gives predicted curvature + in-lane position; if messaging is unavailable
    # (e.g. opendbc run standalone) sm stays None and the OEM path is bypassed -> stock behavior.
    try:
      self.lat_sm = messaging.SubMaster(['modelV2'])
    except Exception:
      self.lat_sm = None
    self.model = None

    self.human_turn = False
    self.reset_steering_last = False
    self.post_reset_ramp_active = False
    self.lane_change = False
    self.lane_change_last = False
    self.post_lane_change_active = False
    self.post_lane_change_timer = 0
    self.pre_lane_change_values = {'path_angle': 0.0, 'path_offset': 0.0, 'desired_curvature_rate': 0.0}
    self.path_angle_last = 0.0
    self.lc_path_angle_reset_counter = 0
    deque_len = max(2, int(round(FORD_CURV_RATE_DELTA_T / (DT_CTRL * CarControllerParams.STEER_STEP))))
    self.curvature_rate_deque = deque(maxlen=deque_len)
    self.lc_pid = PIDController(k_p=0.25, k_i=0.05, rate=20)

  def _read_ford_lat_params(self):
    p = self.param_reader
    self.ford_oem_lateral = _ford_get_bool(p, "NrdrFordOemLateral", False)
    self.ford_human_turn = _ford_get_bool(p, "NrdrFordHumanTurn", True)
    self.ford_lane_positioning = _ford_get_bool(p, "NrdrFordLanePositioning", True)
    self.ford_lane_pos_gain = _ford_get_float(p, "NrdrFordLanePosGain", 100.0, 0.0, 300.0) / 100.0
    self.ford_max_lat_accel = _ford_get_float(p, "NrdrFordMaxLatAccel", MAX_LATERAL_ACCEL, 2.0, 3.5)

  def _handle_post_lane_change_transition(self, path_angle, path_offset, desired_curvature_rate):
    # On lane-change completion, rate-limit the path signals back up from zero so the car doesn't
    # snap to the new centering target.
    if self.lane_change_last and not self.lane_change:
      self.post_lane_change_active = True
      self.post_lane_change_timer = 0
      self.pre_lane_change_values = {'path_angle': 0.0, 'path_offset': 0.0, 'desired_curvature_rate': 0.0}
    self.lane_change_last = self.lane_change
    if self.post_lane_change_active:
      self.post_lane_change_timer += 1
      pv = self.pre_lane_change_values
      new_path_angle = float(np.clip(path_angle, pv['path_angle'] - FORD_MAX_PATH_ANGLE_CHANGE, pv['path_angle'] + FORD_MAX_PATH_ANGLE_CHANGE))
      new_path_offset = float(np.clip(path_offset, pv['path_offset'] - FORD_MAX_PATH_OFFSET_CHANGE, pv['path_offset'] + FORD_MAX_PATH_OFFSET_CHANGE))
      new_curv_rate = float(np.clip(desired_curvature_rate, pv['desired_curvature_rate'] - FORD_MAX_CURVATURE_RATE_CHANGE, pv['desired_curvature_rate'] + FORD_MAX_CURVATURE_RATE_CHANGE))
      self.pre_lane_change_values = {'path_angle': new_path_angle, 'path_offset': new_path_offset, 'desired_curvature_rate': new_curv_rate}
      if self.post_lane_change_timer >= FORD_POST_LC_FRAMES:
        self.post_lane_change_active = False
      return new_path_angle, new_path_offset, new_curv_rate
    return path_angle, path_offset, desired_curvature_rate

  def _compute_ford_oem_lateral(self, CC, CS, actuators):
    """OEM-style 4-signal Ford lateral, ported from BluePilot bp-6.0.
    Returns (apply_curvature, path_angle, path_offset, desired_curvature_rate, ramp_type, precision_type).
    Signs here are pre-negation; the caller negates all four into the CAN message (as stock does for curvature)."""
    # Lateral off: zero everything, clear filters, neutral ramp.
    if not CC.latActive:
      self.curvature_rate_deque.clear()
      self.lc_pid.reset()
      self.apply_curvature_last = 0.0
      self.path_angle_last = 0.0
      self.reset_steering_last = False
      self.post_reset_ramp_active = False
      return 0.0, 0.0, 0.0, 0.0, 0, 1

    desired_curvature = actuators.curvature
    current_curvature = -CS.out.yawRate / max(CS.out.vEgoRaw, 0.1)
    steering_pressed = CS.out.steeringPressed
    steering_angle_deg = CS.out.steeringAngleDeg
    precision_type = 1  # Precise (stock default)

    # predicted curvature from model orientationRate, blended with the planner's desired curvature
    if self.model is not None and len(self.model.orientation.x) >= 17:
      curvatures = np.array(self.model.orientationRate.z) / max(0.01, CS.out.vEgoRaw)
      predicted_curvature = float(np.interp(FORD_CURVATURE_LOOKUP_TIME, FORD_T_IDXS, curvatures))
    else:
      predicted_curvature = 0.0
    requested_curvature = (predicted_curvature * FORD_PC_BLEND_RATIO) + (desired_curvature * (1 - FORD_PC_BLEND_RATIO))

    # lane-change detection: soften curvature into the change and (below) zero the path signals so
    # centering can't fight an auto lane change
    lane_change_dir = 0
    if self.model is not None:
      self.lane_change = self.model.meta.laneChangeState in (1, 2, 3)
      lane_change_dir = self.model.meta.laneChangeDirection
    else:
      self.lane_change = False
    lane_change_factor = float(np.interp(CS.out.vEgoRaw, FORD_LANE_CHANGE_FACTOR_BP, FORD_LANE_CHANGE_FACTOR_V))
    if self.lane_change and lane_change_dir == 1 and requested_curvature < 0:
      requested_curvature *= lane_change_factor
      precision_type = 0
    elif self.lane_change and lane_change_dir == 2 and requested_curvature > 0:
      requested_curvature *= lane_change_factor
      precision_type = 0

    # human-turn override: if the driver holds a real turn, stop fighting and reset (also at standstill)
    self.human_turn = steering_pressed and abs(steering_angle_deg) > FORD_HUMAN_TURN_ANGLE
    reset_steering = 1 if ((self.human_turn and self.ford_human_turn) or (CS.out.vEgoRaw < 0.1)) else 0
    if reset_steering == 1:
      requested_curvature = 0.0

    apply_curvature = apply_ford_curvature_limits(requested_curvature, self.apply_curvature_last, current_curvature,
                                                  CS.out.vEgoRaw, 0., CC.latActive, self.CP, max_lat_accel=self.ford_max_lat_accel)

    # reset -> command zero; on release, ramp back up from zero instead of snapping
    if reset_steering == 1:
      apply_curvature = 0.0
      self.post_reset_ramp_active = False
    elif self.reset_steering_last and not reset_steering:
      self.post_reset_ramp_active = True
      self.apply_curvature_last = 0.0
    if self.post_reset_ramp_active:
      apply_curvature = apply_std_steer_angle_limits(requested_curvature, self.apply_curvature_last, CS.out.vEgoRaw,
                                                     0, CC.latActive, CarControllerParams.ANGLE_LIMITS)
      if abs(requested_curvature - apply_curvature) < max(abs(requested_curvature) * 0.1, 0.001):
        self.post_reset_ramp_active = False
    self.reset_steering_last = (reset_steering == 1)

    # curvature rate = scaled derivative of predicted curvature
    self.curvature_rate_deque.append(predicted_curvature)
    desired_curvature_rate = 0.0
    if len(self.curvature_rate_deque) > 1:
      delta_t = (FORD_CURV_RATE_DELTA_T if len(self.curvature_rate_deque) == self.curvature_rate_deque.maxlen
                 else (len(self.curvature_rate_deque) - 1) * (DT_CTRL * CarControllerParams.STEER_STEP))
      desired_curvature_rate = (self.curvature_rate_deque[-1] - self.curvature_rate_deque[0]) / delta_t / max(0.01, CS.out.vEgoRaw)
    desired_curvature_rate *= float(np.interp(abs(predicted_curvature), FORD_CURV_RATE_PC_BP, FORD_CURV_RATE_PC_V))
    desired_curvature_rate *= float(np.interp(CS.out.vEgoRaw, FORD_CURV_RATE_SPEED_BP, FORD_CURV_RATE_SPEED_V))
    desired_curvature_rate *= float(np.interp(abs(predicted_curvature), FORD_LARGE_CURVE_FACTOR_BP, FORD_LARGE_CURVE_FACTOR_V))
    if self.lane_change:
      desired_curvature_rate = 0.0

    # in-lane position error from model position blended with lanelines by confidence
    path_offset = 0.0
    if self.model is not None:
      path_offset_position = float(np.interp(FORD_PATH_OFFSET_LOOKUP_TIME, FORD_T_IDXS, self.model.position.y))
      path_offset_lanelines = (self.model.laneLines[1].y[0] + self.model.laneLines[2].y[0]) / 2
      laneline_width = self.model.laneLines[2].y[0] + (-self.model.laneLines[1].y[0])
      laneline_width_tol = float(np.interp(laneline_width, [3.75, 4.25], [0.81, 0.59]))
      laneline_conf = min(self.model.laneLineProbs[1], self.model.laneLineProbs[2], laneline_width_tol)
      laneline_scale = float(np.interp(laneline_conf, FORD_MIN_LANELINE_CONF_BP, [0.0, 1.0]))
      path_offset = path_offset_position * (1 - laneline_scale) + path_offset_lanelines * laneline_scale
    if self.lane_change:
      path_offset = 0.0

    # path_angle: PID that drives the in-lane offset to zero (the lane-centering authority lever)
    path_offset_error = path_offset * self.ford_lane_pos_gain
    path_offset_error *= float(np.interp(CS.out.vEgoRaw, FORD_LC_PID_SPEED_BP, FORD_LC_PID_SPEED_V))
    if not self.ford_lane_positioning:
      path_offset_error = 0.0
    path_angle = self.lc_pid.update(path_offset_error)
    if not self.ford_lane_positioning or reset_steering == 1:
      path_angle = 0.0
    path_angle_roc = float(np.interp(abs(CS.out.vEgoRaw), FORD_LC_PATH_ANGLE_ROC_BP, FORD_LC_PATH_ANGLE_ROC_V))
    path_angle = float(np.clip(path_angle, self.path_angle_last - path_angle_roc, self.path_angle_last + path_angle_roc))
    if steering_pressed:
      self.lc_path_angle_reset_counter += 1
    else:
      self.lc_path_angle_reset_counter = 0
    if self.lc_path_angle_reset_counter > FORD_LC_PATH_ANGLE_RESET_FRAMES:
      self.lc_pid.reset()

    path_angle, path_offset, desired_curvature_rate = self._handle_post_lane_change_transition(path_angle, path_offset, desired_curvature_rate)
    if reset_steering == 1:
      path_angle = 0.0

    apply_curvature = float(np.clip(apply_curvature, -FORD_CURVATURE_MAX, FORD_CURVATURE_MAX))
    desired_curvature_rate = float(np.clip(desired_curvature_rate, -FORD_CURVATURE_RATE_MAX, FORD_CURVATURE_RATE_MAX))
    path_angle = float(np.clip(path_angle, -FORD_PATH_ANGLE_MAX, FORD_PATH_ANGLE_MAX))
    # path_offset and path_angle disagreeing is uncomfortable; path_angle is strong, so zero path_offset before send
    path_offset = 0.0

    if reset_steering == 1:
      ramp_type = 3  # Immediate
      self.curvature_rate_deque.clear()
      self.lc_pid.reset()
    else:
      ramp_type = 2  # Fast

    self.apply_curvature_last = apply_curvature
    self.path_angle_last = path_angle
    return apply_curvature, path_angle, path_offset, desired_curvature_rate, ramp_type, precision_type

  def update(self, CC, CC_SP, CS, now_nanos):
    can_sends = []

    # nrdr Ford OEM lateral: throttled param refresh + model snapshot (only polled when enabled)
    self._ford_lat_param_frame += 1
    if self._ford_lat_param_frame % FORD_LAT_PARAM_STEP == 0:
      self._read_ford_lat_params()
    if self.ford_oem_lateral and self.lat_sm is not None:
      try:
        self.lat_sm.update(0)
        if self.lat_sm.updated['modelV2']:
          self.model = self.lat_sm['modelV2']
      except Exception:
        self.model = None

    actuators = CC.actuators
    hud_control = CC.hudControl

    main_on = CS.out.cruiseState.available
    steer_alert = hud_control.visualAlert in (VisualAlert.steerRequired, VisualAlert.ldw)
    fcw_alert = hud_control.visualAlert == VisualAlert.fcw

    ### acc buttons ###
    if CC.cruiseControl.cancel:
      can_sends.append(fordcan.create_button_msg(self.packer, self.CAN.camera, CS.buttons_stock_values, cancel=True))
      can_sends.append(fordcan.create_button_msg(self.packer, self.CAN.main, CS.buttons_stock_values, cancel=True))
    elif CC.cruiseControl.resume and (self.frame % CarControllerParams.BUTTONS_STEP) == 0:
      can_sends.append(fordcan.create_button_msg(self.packer, self.CAN.camera, CS.buttons_stock_values, resume=True))
      can_sends.append(fordcan.create_button_msg(self.packer, self.CAN.main, CS.buttons_stock_values, resume=True))
    # if stock lane centering isn't off, send a button press to toggle it off
    # the stock system checks for steering pressed, and eventually disengages cruise control
    elif CS.acc_tja_status_stock_values["Tja_D_Stat"] != 0 and (self.frame % CarControllerParams.ACC_UI_STEP) == 0:
      can_sends.append(fordcan.create_button_msg(self.packer, self.CAN.camera, CS.buttons_stock_values, tja_toggle=True))

    ### lateral control ###
    # send steer msg at 20Hz
    if (self.frame % CarControllerParams.STEER_STEP) == 0:
      if self.ford_oem_lateral and self.lat_sm is not None:
        # nrdr OEM-style 4-signal lateral (curvature + curvature_rate + path_angle), ported from BluePilot.
        # All four are negated into the message, same as stock does for curvature. Stock path is the else below.
        apply_curvature, path_angle, path_offset, curvature_rate, ramp_type, precision_type = self._compute_ford_oem_lateral(CC, CS, actuators)
        if self.CP.flags & FordFlags.CANFD:
          mode = 1 if CC.latActive else 0
          counter = (self.frame // CarControllerParams.STEER_STEP) % 0x10
          can_sends.append(fordcan.create_lat_ctl2_msg(self.packer, self.CAN, mode, -path_offset, -path_angle,
                                                       -apply_curvature, -curvature_rate, counter, ramp_type, precision_type))
        else:
          can_sends.append(fordcan.create_lat_ctl_msg(self.packer, self.CAN, CC.latActive, -path_offset, -path_angle,
                                                      -apply_curvature, -curvature_rate, ramp_type, precision_type))
      else:
        # Bronco and some other cars consistently overshoot curv requests
        # Apply some deadzone + smoothing convergence to avoid oscillations
        if self.CP.carFingerprint in (CAR.FORD_BRONCO_SPORT_MK1, CAR.FORD_F_150_MK14):
          self.anti_overshoot_curvature_last = anti_overshoot(actuators.curvature, self.anti_overshoot_curvature_last, CS.out.vEgoRaw)
          apply_curvature = self.anti_overshoot_curvature_last
        else:
          apply_curvature = actuators.curvature

        # apply rate limits, curvature error limit, and clip to signal range
        current_curvature = -CS.out.yawRate / max(CS.out.vEgoRaw, 0.1)

        self.apply_curvature_last = apply_ford_curvature_limits(apply_curvature, self.apply_curvature_last, current_curvature,
                                                                CS.out.vEgoRaw, 0., CC.latActive, self.CP)

        if self.CP.flags & FordFlags.CANFD:
          # TODO: extended mode
          # Ford uses four individual signals to dictate how to drive to the car. Curvature alone (limited to 0.02m/s^2)
          # can actuate the steering for a large portion of any lateral movements. However, in order to get further control on
          # steer actuation, the other three signals are necessary. Ford controls vehicles differently than most other makes.
          # A detailed explanation on ford control can be found here:
          # https://www.f150gen14.com/forum/threads/introducing-bluepilot-a-ford-specific-fork-for-comma3x-openpilot.24241/#post-457706
          mode = 1 if CC.latActive else 0
          counter = (self.frame // CarControllerParams.STEER_STEP) % 0x10
          can_sends.append(fordcan.create_lat_ctl2_msg(self.packer, self.CAN, mode, 0., 0., -self.apply_curvature_last, 0., counter))
        else:
          can_sends.append(fordcan.create_lat_ctl_msg(self.packer, self.CAN, CC.latActive, 0., 0., -self.apply_curvature_last, 0.))

    # send lka msg at 33Hz
    if (self.frame % CarControllerParams.LKA_STEP) == 0:
      can_sends.append(fordcan.create_lka_msg(self.packer, self.CAN))

    ### longitudinal control ###
    # send acc msg at 50Hz
    if self.CP.openpilotLongitudinalControl and (self.frame % CarControllerParams.ACC_CONTROL_STEP) == 0:
      accel = actuators.accel
      gas = accel

      if CC.longActive:
        # Compensate for engine creep at low speed.
        # Either the ABS does not account for engine creep, or the correction is very slow
        # TODO: verify this applies to EV/hybrid
        accel = apply_creep_compensation(accel, CS.out.vEgo)

        # The stock system has been seen rate limiting the brake accel to 5 m/s^3,
        # however even 3.5 m/s^3 causes some overshoot with a step response.
        accel = max(accel, self.accel - (3.5 * CarControllerParams.ACC_CONTROL_STEP * DT_CTRL))

      accel = float(np.clip(accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))
      gas = float(np.clip(gas, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))

      # Both gas and accel are in m/s^2, accel is used solely for braking
      if not CC.longActive or gas < CarControllerParams.MIN_GAS:
        gas = CarControllerParams.INACTIVE_GAS

      # PCM applies pitch compensation to gas/accel, but we need to compensate for the brake/pre-charge bits
      accel_due_to_pitch = 0.0
      if len(CC.orientationNED) == 3:
        accel_due_to_pitch = math.sin(CC.orientationNED[1]) * ACCELERATION_DUE_TO_GRAVITY

      accel_pitch_compensated = accel + accel_due_to_pitch
      if accel_pitch_compensated > 0.3 or not CC.longActive:
        self.brake_request = False
      elif accel_pitch_compensated < 0.0:
        self.brake_request = True

      stopping = CC.actuators.longControlState == LongCtrlState.stopping
      # TODO: look into using the actuators packet to send the desired speed
      can_sends.append(fordcan.create_acc_msg(self.packer, self.CAN, CC.longActive, gas, accel, stopping, self.brake_request, v_ego_kph=V_CRUISE_MAX))

      self.accel = accel
      self.gas = gas

    ### ui ###
    send_ui = (self.main_on_last != main_on) or (self.lkas_enabled_last != CC.latActive) or (self.steer_alert_last != steer_alert)
    # send lkas ui msg at 1Hz or if ui state changes
    if (self.frame % CarControllerParams.LKAS_UI_STEP) == 0 or send_ui:
      can_sends.append(fordcan.create_lkas_ui_msg(self.packer, self.CAN, main_on, CC.latActive, steer_alert, hud_control, CS.lkas_status_stock_values))

    # send acc ui msg at 5Hz or if ui state changes
    if hud_control.leadDistanceBars != self.lead_distance_bars_last:
      send_ui = True
      self.distance_bar_frame = self.frame

    if (self.frame % CarControllerParams.ACC_UI_STEP) == 0 or send_ui:
      show_distance_bars = self.frame - self.distance_bar_frame < 400
      can_sends.append(fordcan.create_acc_ui_msg(self.packer, self.CAN, self.CP, main_on, CC.latActive,
                                                 fcw_alert, CS.out.cruiseState.standstill, show_distance_bars,
                                                 hud_control, CS.acc_tja_status_stock_values))

    self.main_on_last = main_on
    self.lkas_enabled_last = CC.latActive
    self.steer_alert_last = steer_alert
    self.lead_distance_bars_last = hud_control.leadDistanceBars

    new_actuators = actuators.as_builder()
    new_actuators.curvature = self.apply_curvature_last
    new_actuators.accel = self.accel
    new_actuators.gas = self.gas

    self.frame += 1
    return new_actuators, can_sends
