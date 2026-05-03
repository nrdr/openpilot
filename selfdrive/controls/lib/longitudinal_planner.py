#!/usr/bin/env python3
import math
import numpy as np
import time
import cereal.messaging as messaging
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import desired_follow_distance
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import STOP_DISTANCE
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.common.swaglog import cloudlog

LON_MPC_STEP = 0.2  # first step is 0.2s
A_CRUISE_MIN = -1.0
A_CRUISE_MAX_BP = [0.0, 5., 10., 15., 20., 25., 40.]
A_CRUISE_MAX_VALS = [1.125, 1.125, 1.125, 1.125, 1.25, 1.25, 1.5]
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
ALLOW_THROTTLE_THRESHOLD = 0.4
ALLOW_THROTTLE_HYSTERESIS = 0.05
ALLOW_THROTTLE_ENABLE_THRESHOLD = ALLOW_THROTTLE_THRESHOLD + ALLOW_THROTTLE_HYSTERESIS
ALLOW_THROTTLE_DISABLE_THRESHOLD = ALLOW_THROTTLE_THRESHOLD - ALLOW_THROTTLE_HYSTERESIS
MIN_ALLOW_THROTTLE_SPEED = 5.0
RAW_LEAD_SAFETY_MIN_CLOSING_SPEED = 0.5
RAW_LEAD_SAFETY_TTC = 7.0
RAW_LEAD_SAFETY_DISTANCE = 40.0
STANDSTILL_LEAD_NUDGE_ACCEL = 0.05
STANDSTILL_LEAD_NUDGE_MIN_SPEED = 0.0
CLOSE_LEAD_BRAKE_CAP_MAX_TTC = 25.0
VISION_LEAD_APPROACH_MIN_CLOSING_SPEED = 2.0
VISION_LEAD_APPROACH_TRIGGER_TIME = 4.5
VISION_LEAD_APPROACH_FULL_TIME = 1.0
VISION_LEAD_APPROACH_TIGHT_BUFFER = 2.0
VISION_LEAD_APPROACH_MAX_DECEL = 0.80
VISION_LEAD_APPROACH_MIN_DECEL = 0.15
VISION_LEAD_APPROACH_MIN_MODEL_PROB = 0.85
VISION_LEAD_APPROACH_FULL_MODEL_PROB = 0.98
VISION_LEAD_APPROACH_DEFICIT_MAX_DECEL = 1.30
VISION_LEAD_APPROACH_DEFICIT_BUFFER_MIN = 3.0
VISION_LEAD_APPROACH_DEFICIT_BUFFER_GAIN = 0.20
VISION_UNTRACKED_SLOW_LEAD_MIN_MODEL_PROB = 0.9
VISION_UNTRACKED_SLOW_LEAD_FULL_MODEL_PROB = 0.97
VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_SPEED = 3.0
VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_RATIO = 0.16
VISION_UNTRACKED_SLOW_LEAD_FULL_CLOSING_RATIO = 0.24
VISION_UNTRACKED_SLOW_LEAD_TRIGGER_TTC = 16.0
VISION_UNTRACKED_SLOW_LEAD_FULL_TTC = 8.0
VISION_UNTRACKED_SLOW_LEAD_MAX_DISTANCE_TIME = 4.4
VISION_UNTRACKED_SLOW_LEAD_MIN_DISTANCE = 80.0
VISION_UNTRACKED_SLOW_LEAD_MAX_DISTANCE = 120.0
VISION_UNTRACKED_SLOW_LEAD_MAX_DECEL = 0.85
VISION_UNTRACKED_SLOW_LEAD_MIN_DECEL = 0.1
VISION_SLOW_LEAD_MAX_SPEED = 5.0
VISION_SLOW_LEAD_MIN_CLOSING_SPEED = 1.5
VISION_SLOW_LEAD_TRIGGER_TTC = 4.5
VISION_SLOW_LEAD_FULL_TTC = 2.0
VISION_SLOW_LEAD_MAX_DECEL = 1.2
VISION_SLOW_LEAD_MIN_DECEL = 0.18
VISION_SLOW_LEAD_MIN_MODEL_PROB = 0.9
LEAD_APPROACH_TFOLLOW_TRIGGER_TIME = 4.5
LEAD_APPROACH_TFOLLOW_FULL_TIME = 1.5
LEAD_APPROACH_TFOLLOW_MAX_DELTA = 0.18
LEAD_APPROACH_TFOLLOW_MAX_CLOSING_SPEED = 6.0
LEAD_APPROACH_TFOLLOW_MAX_LEAD_BRAKE = 2.5
LEAD_APPROACH_TFOLLOW_MIN_CLOSING_SPEED = 0.75
LEAD_APPROACH_TFOLLOW_MIN_LEAD_BRAKE = 0.2
LEAD_APPROACH_TFOLLOW_WINDOW_MIN = 6.0
LEAD_APPROACH_TFOLLOW_WINDOW_GAIN = 0.35
LEAD_APPROACH_TFOLLOW_RATE_UP = 1.0
LEAD_APPROACH_TFOLLOW_RATE_DOWN = 0.60
VISION_LEAD_TFOLLOW_MAX_EXTRA_DELTA = 0.24
VISION_LEAD_TFOLLOW_SLOW_LEAD_SPEED = 20.0
VISION_LEAD_TFOLLOW_GAP_BUFFER_MIN = 8.0
VISION_LEAD_TFOLLOW_GAP_BUFFER_GAIN = 0.35
VISION_LOW_SPEED_STOP_BUFFER_MAX_EGO_SPEED = 5.5
VISION_LOW_SPEED_STOP_BUFFER_MAX_LEAD_SPEED = 1.75
VISION_LOW_SPEED_STOP_BUFFER_MIN_MODEL_PROB = 0.9
VISION_LOW_SPEED_STOP_BUFFER_MIN_CLOSING_SPEED = 0.35
VISION_LOW_SPEED_STOP_BUFFER_BASE = 3.2
VISION_LOW_SPEED_STOP_BUFFER_EGO_GAIN = 0.80
VISION_LOW_SPEED_STOP_BUFFER_LEAD_GAIN = 0.25
VISION_LOW_SPEED_STOP_BUFFER_RELEASE_MARGIN = 0.9
VISION_LOW_SPEED_STOP_BUFFER_HOLD_TIME = 0.8
VISION_LOW_SPEED_STOP_BUFFER_MIN_BRAKE = 1.1
VISION_LOW_SPEED_STOP_BUFFER_BRAKE_GAIN = 0.25
LEAD_CATCHUP_ACCEL_MIN_EGO = 8.0
LEAD_CATCHUP_ACCEL_MIN_LEAD_DELTA = -0.5
LEAD_CATCHUP_ACCEL_MAX_GAP_BUFFER_MIN = 4.0
LEAD_CATCHUP_ACCEL_MAX_GAP_BUFFER_GAIN = 0.15

# Uncertainty-based filter disable thresholds
UNCERT_SLOPE_TRIG = 0.12  # per second
UNCERT_MAG_TRIG = 0.50

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]


def get_longitudinal_personality(sm):
  return sm['selfdriveState'].personality


def get_max_accel(v_ego):
  return np.interp(v_ego, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)

def get_coast_accel(pitch):
  return np.sin(pitch) * -5.65 - 0.3  # fitted from data using xx/projects/allow_throttle/compute_coast_accel.py


def limit_accel_in_turns(v_ego, angle_steers, a_target, CP):
  """
  This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
  this should avoid accelerating when losing the target in turns
  """
  # FIXME: This function to calculate lateral accel is incorrect and should use the VehicleModel
  # The lookup table for turns should also be updated if we do this
  a_total_max = np.interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
  a_y = v_ego ** 2 * angle_steers * CV.DEG_TO_RAD / (CP.steerRatio * CP.wheelbase)
  a_x_allowed = math.sqrt(max(a_total_max ** 2 - a_y ** 2, 0.))

  return [a_target[0], min(a_target[1], a_x_allowed)]


def get_vehicle_min_accel(CP, v_ego):
  # Planner-side physical decel capability estimate for GM pedal-long paths.
  if getattr(CP, "carName", "") == "gm" and getattr(CP, "enableGasInterceptorDEPRECATED", False):
    try:
      from opendbc.car.gm.values import GMFlags, CAR
      if bool(CP.flags & GMFlags.PEDAL_LONG.value):
        bolt_pedal_long_cars = {
          CAR.CHEVROLET_BOLT_CC_2017,
          CAR.CHEVROLET_BOLT_CC_2018_2021,
          CAR.CHEVROLET_BOLT_ACC_2022_2023_PEDAL,
          CAR.CHEVROLET_BOLT_CC_2022_2023,
          CAR.CHEVROLET_MALIBU_HYBRID_CC,
        }
        if CP.carFingerprint in bolt_pedal_long_cars:
          return float(np.interp(v_ego, [0.0, 1.5, 4.0, 8.0, 15.0, 30.0],
                                 [-0.93, -1.28, -1.98, -2.58, -2.86, -2.95]))
        return float(np.interp(v_ego, [0.0, 1.5, 4.0, 8.0, 15.0, 30.0],
                               [-0.95, -1.3, -1.85, -2.3, -2.6, -2.8]))
    except Exception:
      pass
  return float(ACCEL_MIN)


def get_planner_v_ego(CP, car_state):
  v_ego = max(car_state.vEgo, car_state.vEgoCluster)

  is_gm = getattr(CP, "carName", "") == "gm" or getattr(CP, "brand", "") == "gm"
  if is_gm and getattr(CP, "enableGasInterceptorDEPRECATED", False):
    try:
      from opendbc.car.gm.values import GMFlags
      is_gm_pedal_long = bool(CP.flags & GMFlags.PEDAL_LONG.value)
      if is_gm_pedal_long:
        return float(car_state.vEgo)
    except Exception:
      pass

  return float(v_ego)


def get_accel_from_plan_classic(CP, speeds, accels, vEgoStopping):
  if len(speeds) == CONTROL_N:
    v_target_now = np.interp(DT_MDL, CONTROL_N_T_IDX, speeds)
    a_target_now = np.interp(DT_MDL, CONTROL_N_T_IDX, accels)

    v_target = np.interp(CP.longitudinalActuatorDelay + DT_MDL, CONTROL_N_T_IDX, speeds)
    if v_target != v_target_now:
      a_target = 2 * (v_target - v_target_now) / CP.longitudinalActuatorDelay - a_target_now
    else:
      a_target = a_target_now

    v_target_1sec = np.interp(CP.longitudinalActuatorDelay + DT_MDL + 1.0, CONTROL_N_T_IDX, speeds)
  else:
    v_target = 0.0
    v_target_1sec = 0.0
    a_target = 0.0
  should_stop = (v_target < vEgoStopping and
                 v_target_1sec < vEgoStopping)
  return a_target, should_stop


def get_accel_from_plan(speeds, accels, action_t=DT_MDL, vEgoStopping=0.05):
  if len(speeds) == CONTROL_N:
    v_now = speeds[0]
    a_now = accels[0]

    v_target = np.interp(action_t, CONTROL_N_T_IDX, speeds)
    a_target = 2 * (v_target - v_now) / (action_t) - a_now
    v_target_1sec = np.interp(action_t + 1.0, CONTROL_N_T_IDX, speeds)
  else:
    v_target = 0.0
    v_target_1sec = 0.0
    a_target = 0.0
  should_stop = (v_target < vEgoStopping and
                 v_target_1sec < vEgoStopping)
  return a_target, should_stop


class LongitudinalPlanner:
  def __init__(self, CP, init_v=0.0, init_a=0.0, dt=DT_MDL):
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.fcw = False
    self.dt = dt
    self.model_allow_throttle = True
    self.allow_throttle = True
    self.mode = 'acc'

    self.generation = None

    self.a_desired = init_a
    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.v_model_error = 0.0
    self.output_a_target = 0.0
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)
    self.solverExecutionTime = 0.0

    # ---- Rubberband mitigation state ----
    # Two uncertainty tracks (slow/fast) for asymmetric gating
    self.uncert_slow = FirstOrderFilter(0.0, 1.6, self.dt)  # ~lam=0.6
    self.uncert_fast = FirstOrderFilter(0.0, 0.9, self.dt)  # faster cool-down for accel decisions
    # Lead stability tracking
    self.prev_lead_dist = None
    self.last_big_brake_t = 0.0
    self.stable_lead = False
    # Smoothed lead distance
    self.lead_dist_f = None

    # Uncertainty slope tracking
    self._uncert_last = 0.0
    self._uncert_last_t = None
    self.effective_t_follow = None
    self.vision_low_speed_stop_hold_until = 0.0

  @property
  def mlsim(self):
    return self.generation in ("v8", "v10", "v11", "v12", "v13")

  def get_mpc_mode(self) -> str:
    if not self.mlsim:
      return self.mode
    return getattr(self.mpc, 'mode', 'acc')

  @staticmethod
  def get_model_speed_error(model_msg, v_ego):
    try:
      if len(model_msg.temporalPose.trans):
        return float(np.clip(model_msg.temporalPose.trans[0] - v_ego, -5.0, 5.0))
    except AttributeError:
      pass
    return 0.0

  @staticmethod
  def parse_model(model_msg, model_error, v_ego, starpilot_toggles):
    if (len(model_msg.position.x) == ModelConstants.IDX_N and
      len(model_msg.velocity.x) == ModelConstants.IDX_N and
      len(model_msg.acceleration.x) == ModelConstants.IDX_N):
      x = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.position.x) - model_error * T_IDXS_MPC
      v = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.velocity.x) - model_error
      a = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.acceleration.x)
      j = np.zeros(len(T_IDXS_MPC))
    else:
      x = np.zeros(len(T_IDXS_MPC))
      v = np.zeros(len(T_IDXS_MPC))
      a = np.zeros(len(T_IDXS_MPC))
      j = np.zeros(len(T_IDXS_MPC))

    if starpilot_toggles.taco_tune:
      max_lat_accel = np.interp(v_ego, [5, 10, 20], [1.5, 2.0, 3.0])
      curvatures = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.orientationRate.z) / np.clip(v, 0.3, 100.0)
      max_v = np.sqrt(max_lat_accel / (np.abs(curvatures) + 1e-3)) - 2.0
      v = np.minimum(max_v, v)

    if len(model_msg.meta.disengagePredictions.gasPressProbs) > 1:
      throttle_prob = model_msg.meta.disengagePredictions.gasPressProbs[1]
    else:
      throttle_prob = 1.0
    return x, v, a, j, throttle_prob

  def get_close_lead_brake_cap(self, lead, v_ego, accel_min):
    if lead is None or not lead.status:
      return None

    lead_brake = max(0.0, -float(lead.aLeadK))
    reaction_t = max(self.CP.longitudinalActuatorDelay, self.dt)
    closing_speed = max(0.0, v_ego - lead.vLead)
    projected_closing_speed = closing_speed + lead_brake * reaction_t
    if projected_closing_speed < 0.1 and lead_brake < 0.5:
      return None

    target_gap = float(np.clip(2.0 + 0.2 * v_ego, 2.0, 6.0))
    delay_buffer = projected_closing_speed * reaction_t
    available_gap = max(float(lead.dRel) - target_gap - delay_buffer, 0.5)
    projected_ttc = available_gap / max(projected_closing_speed, 0.1)
    if projected_ttc > CLOSE_LEAD_BRAKE_CAP_MAX_TTC:
      return None
    required_decel = (projected_closing_speed ** 2) / (2.0 * available_gap) + 0.7 * lead_brake
    if required_decel < 0.2:
      return None

    return max(accel_min, -required_decel)

  def get_vision_lead_approach_cap(self, lead, v_ego, accel_min, t_follow):
    if lead is None or not lead.status or bool(getattr(lead, "radar", False)):
      return None

    lead_prob = float(getattr(lead, "modelProb", 0.0))
    if lead_prob < VISION_LEAD_APPROACH_MIN_MODEL_PROB:
      return None

    lead_brake = max(0.0, -float(lead.aLeadK))
    reaction_t = max(self.CP.longitudinalActuatorDelay, self.dt)
    closing_speed = max(0.0, v_ego - lead.vLead)
    projected_closing_speed = closing_speed + lead_brake * reaction_t
    if projected_closing_speed < VISION_LEAD_APPROACH_MIN_CLOSING_SPEED:
      return None

    tight_follow_gap = float(t_follow * v_ego + VISION_LEAD_APPROACH_TIGHT_BUFFER)
    gap_to_tight_follow = float(lead.dRel) - tight_follow_gap
    time_to_tight_follow = gap_to_tight_follow / max(projected_closing_speed, 0.1)
    if time_to_tight_follow > VISION_LEAD_APPROACH_TRIGGER_TIME:
      return None

    desired_gap = float(desired_follow_distance(v_ego, lead.vLead, t_follow))
    if float(lead.dRel) > desired_gap + VISION_LEAD_APPROACH_TIGHT_BUFFER:
      return None

    time_factor = float(np.clip((VISION_LEAD_APPROACH_TRIGGER_TIME - time_to_tight_follow) /
                                (VISION_LEAD_APPROACH_TRIGGER_TIME - VISION_LEAD_APPROACH_FULL_TIME), 0.0, 1.0))
    prob_factor = float(np.clip((lead_prob - VISION_LEAD_APPROACH_MIN_MODEL_PROB) /
                                (VISION_LEAD_APPROACH_FULL_MODEL_PROB - VISION_LEAD_APPROACH_MIN_MODEL_PROB), 0.0, 1.0))
    closing_factor = float(np.clip(projected_closing_speed / (VISION_LEAD_APPROACH_MIN_CLOSING_SPEED + 2.5), 0.0, 1.0))
    tight_follow_deficit = max(tight_follow_gap - float(lead.dRel), 0.0)
    tight_follow_buffer = max(VISION_LEAD_APPROACH_DEFICIT_BUFFER_MIN,
                              VISION_LEAD_APPROACH_DEFICIT_BUFFER_GAIN * float(v_ego) + 1.0)
    deficit_factor = float(np.clip(tight_follow_deficit / tight_follow_buffer, 0.0, 1.0))

    approach_decel = VISION_LEAD_APPROACH_MAX_DECEL * time_factor * (0.45 + 0.55 * prob_factor)
    approach_decel *= 0.6 + 0.4 * closing_factor
    deficit_decel = VISION_LEAD_APPROACH_DEFICIT_MAX_DECEL * deficit_factor * prob_factor
    deficit_decel *= 0.5 + 0.5 * closing_factor
    approach_decel = max(approach_decel, deficit_decel)
    if approach_decel < VISION_LEAD_APPROACH_MIN_DECEL:
      return None

    return max(accel_min, -approach_decel)

  def get_vision_untracked_slow_lead_cap(self, lead, v_ego, accel_min):
    if lead is None or not lead.status or bool(getattr(lead, "radar", False)):
      return None

    lead_prob = float(getattr(lead, "modelProb", 0.0))
    if lead_prob < VISION_UNTRACKED_SLOW_LEAD_MIN_MODEL_PROB:
      return None

    lead_brake = max(0.0, -float(lead.aLeadK))
    reaction_t = max(self.CP.longitudinalActuatorDelay, self.dt)
    closing_speed = max(0.0, v_ego - lead.vLead)
    projected_closing_speed = closing_speed + lead_brake * reaction_t
    if projected_closing_speed < VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_SPEED:
      return None

    closing_ratio = projected_closing_speed / max(float(v_ego), 0.1)
    if closing_ratio < VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_RATIO:
      return None

    max_distance = float(np.clip(VISION_UNTRACKED_SLOW_LEAD_MAX_DISTANCE_TIME * v_ego,
                                 VISION_UNTRACKED_SLOW_LEAD_MIN_DISTANCE,
                                 VISION_UNTRACKED_SLOW_LEAD_MAX_DISTANCE))
    if float(lead.dRel) > max_distance:
      return None

    projected_ttc = float(lead.dRel) / max(projected_closing_speed, 0.1)
    if projected_ttc > VISION_UNTRACKED_SLOW_LEAD_TRIGGER_TTC:
      return None

    time_factor = float(np.clip((VISION_UNTRACKED_SLOW_LEAD_TRIGGER_TTC - projected_ttc) /
                                (VISION_UNTRACKED_SLOW_LEAD_TRIGGER_TTC - VISION_UNTRACKED_SLOW_LEAD_FULL_TTC),
                                0.0, 1.0))
    prob_factor = float(np.clip((lead_prob - VISION_UNTRACKED_SLOW_LEAD_MIN_MODEL_PROB) /
                                (VISION_UNTRACKED_SLOW_LEAD_FULL_MODEL_PROB - VISION_UNTRACKED_SLOW_LEAD_MIN_MODEL_PROB),
                                0.0, 1.0))
    closing_factor = float(np.clip((closing_ratio - VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_RATIO) /
                                   (VISION_UNTRACKED_SLOW_LEAD_FULL_CLOSING_RATIO - VISION_UNTRACKED_SLOW_LEAD_MIN_CLOSING_RATIO),
                                   0.0, 1.0))
    approach_decel = VISION_UNTRACKED_SLOW_LEAD_MAX_DECEL * np.clip(
      0.5 * time_factor + 0.3 * prob_factor + 0.2 * closing_factor, 0.0, 1.0)
    if approach_decel < VISION_UNTRACKED_SLOW_LEAD_MIN_DECEL:
      return None

    return max(accel_min, -approach_decel)

  def get_vision_slow_stopped_lead_cap(self, lead, v_ego, accel_min, t_follow):
    if lead is None or not lead.status or bool(getattr(lead, "radar", False)):
      return None

    lead_prob = float(getattr(lead, "modelProb", 0.0))
    if lead_prob < VISION_SLOW_LEAD_MIN_MODEL_PROB or float(lead.vLead) > VISION_SLOW_LEAD_MAX_SPEED:
      return None

    lead_brake = max(0.0, -float(lead.aLeadK))
    reaction_t = max(self.CP.longitudinalActuatorDelay, self.dt)
    closing_speed = max(0.0, v_ego - lead.vLead)
    projected_closing_speed = closing_speed + lead_brake * reaction_t
    if projected_closing_speed < VISION_SLOW_LEAD_MIN_CLOSING_SPEED:
      return None

    stop_gap = float(max(STOP_DISTANCE + 1.0, 2.5 + 0.15 * max(float(lead.vLead), 0.0)))
    delay_buffer = projected_closing_speed * reaction_t
    available_gap = max(float(lead.dRel) - stop_gap - delay_buffer, 0.5)
    projected_ttc = available_gap / max(projected_closing_speed, 0.1)
    if projected_ttc > VISION_SLOW_LEAD_TRIGGER_TTC:
      return None

    time_factor = float(np.clip((VISION_SLOW_LEAD_TRIGGER_TTC - projected_ttc) /
                                (VISION_SLOW_LEAD_TRIGGER_TTC - VISION_SLOW_LEAD_FULL_TTC), 0.0, 1.0))
    prob_factor = float(np.clip((lead_prob - VISION_SLOW_LEAD_MIN_MODEL_PROB) /
                                (VISION_LEAD_APPROACH_FULL_MODEL_PROB - VISION_SLOW_LEAD_MIN_MODEL_PROB), 0.0, 1.0))
    speed_factor = float(np.clip((VISION_SLOW_LEAD_MAX_SPEED - max(float(lead.vLead), 0.0)) /
                                 VISION_SLOW_LEAD_MAX_SPEED, 0.0, 1.0))
    required_decel = (projected_closing_speed ** 2) / (2.0 * available_gap)
    decel_scale = 0.45 + 0.35 * time_factor + 0.20 * speed_factor
    approach_decel = min(VISION_SLOW_LEAD_MAX_DECEL, required_decel * decel_scale)
    approach_decel *= 0.65 + 0.35 * prob_factor
    if approach_decel < VISION_SLOW_LEAD_MIN_DECEL:
      return None

    return max(accel_min, -approach_decel)

  def get_dynamic_t_follow(self, base_t_follow, lead, v_ego):
    base_t_follow = float(base_t_follow)
    target_t_follow = base_t_follow

    if lead is not None and lead.status:
      lead_prob = float(getattr(lead, "modelProb", 1.0 if bool(getattr(lead, "radar", False)) else 0.0))
      if bool(getattr(lead, "radar", False)) or lead_prob >= VISION_LEAD_APPROACH_MIN_MODEL_PROB:
        lead_brake = max(0.0, -float(lead.aLeadK))
        closing_speed = max(0.0, v_ego - lead.vLead)
        if closing_speed >= LEAD_APPROACH_TFOLLOW_MIN_CLOSING_SPEED or lead_brake >= LEAD_APPROACH_TFOLLOW_MIN_LEAD_BRAKE:
          desired_gap = float(desired_follow_distance(v_ego, lead.vLead, base_t_follow))
          approach_window = max(LEAD_APPROACH_TFOLLOW_WINDOW_MIN, LEAD_APPROACH_TFOLLOW_WINDOW_GAIN * float(v_ego))
          if float(lead.dRel) <= desired_gap + approach_window:
            reaction_t = max(self.CP.longitudinalActuatorDelay, self.dt)
            projected_closing_speed = closing_speed + 0.5 * lead_brake * reaction_t
            gap_to_follow = max(float(lead.dRel) - desired_gap, 0.0)
            time_to_follow = gap_to_follow / max(projected_closing_speed, 0.1)
            time_factor = float(np.clip((LEAD_APPROACH_TFOLLOW_TRIGGER_TIME - time_to_follow) /
                                        (LEAD_APPROACH_TFOLLOW_TRIGGER_TIME - LEAD_APPROACH_TFOLLOW_FULL_TIME), 0.0, 1.0))
            closing_factor = float(np.clip(closing_speed / LEAD_APPROACH_TFOLLOW_MAX_CLOSING_SPEED, 0.0, 1.0))
            brake_factor = float(np.clip(lead_brake / LEAD_APPROACH_TFOLLOW_MAX_LEAD_BRAKE, 0.0, 1.0))
            target_delta = LEAD_APPROACH_TFOLLOW_MAX_DELTA * np.clip(
              0.55 * time_factor + 0.25 * closing_factor + 0.20 * brake_factor, 0.0, 1.0)
            if not bool(getattr(lead, "radar", False)):
              gap_deficit = max(desired_gap - float(lead.dRel), 0.0)
              gap_buffer = max(VISION_LEAD_TFOLLOW_GAP_BUFFER_MIN,
                               VISION_LEAD_TFOLLOW_GAP_BUFFER_GAIN * float(v_ego))
              gap_factor = float(np.clip(gap_deficit / gap_buffer, 0.0, 1.0))
              slow_lead_factor = float(np.clip((VISION_LEAD_TFOLLOW_SLOW_LEAD_SPEED - float(lead.vLead)) /
                                               VISION_LEAD_TFOLLOW_SLOW_LEAD_SPEED, 0.0, 1.0))
              vision_extra = VISION_LEAD_TFOLLOW_MAX_EXTRA_DELTA * np.clip(
                0.40 * time_factor + 0.30 * gap_factor + 0.20 * slow_lead_factor + 0.10 * closing_factor,
                0.0, 1.0)
              target_delta += vision_extra
            target_t_follow = base_t_follow + float(target_delta)

    if self.effective_t_follow is None:
      self.effective_t_follow = base_t_follow

    rate = LEAD_APPROACH_TFOLLOW_RATE_UP if target_t_follow > self.effective_t_follow else LEAD_APPROACH_TFOLLOW_RATE_DOWN
    step = rate * self.dt
    self.effective_t_follow = float(np.clip(target_t_follow, self.effective_t_follow - step, self.effective_t_follow + step))
    self.effective_t_follow = max(base_t_follow, self.effective_t_follow)
    return self.effective_t_follow

  def get_vision_low_speed_stop_buffer_cap(self, lead, v_ego, accel_min):
    if lead is None or not lead.status or bool(getattr(lead, "radar", False)):
      return None, False

    lead_prob = float(getattr(lead, "modelProb", 0.0))
    if lead_prob < VISION_LOW_SPEED_STOP_BUFFER_MIN_MODEL_PROB:
      return None, False

    lead_speed = max(float(lead.vLead), 0.0)
    closing_speed = max(0.0, v_ego - lead_speed)
    valid_context = (
      v_ego <= VISION_LOW_SPEED_STOP_BUFFER_MAX_EGO_SPEED and
      lead_speed <= VISION_LOW_SPEED_STOP_BUFFER_MAX_LEAD_SPEED and
      closing_speed >= VISION_LOW_SPEED_STOP_BUFFER_MIN_CLOSING_SPEED
    )

    now_t = time.monotonic()
    entry_buffer = max(3.2, VISION_LOW_SPEED_STOP_BUFFER_BASE +
                       VISION_LOW_SPEED_STOP_BUFFER_EGO_GAIN * float(v_ego) +
                       VISION_LOW_SPEED_STOP_BUFFER_LEAD_GAIN * lead_speed)
    release_buffer = entry_buffer + VISION_LOW_SPEED_STOP_BUFFER_RELEASE_MARGIN
    if valid_context and float(lead.dRel) <= entry_buffer:
      self.vision_low_speed_stop_hold_until = now_t + VISION_LOW_SPEED_STOP_BUFFER_HOLD_TIME

    latched = now_t < self.vision_low_speed_stop_hold_until
    active = valid_context and (float(lead.dRel) <= entry_buffer or (latched and float(lead.dRel) <= release_buffer))
    if not active:
      return None, False

    min_stop_brake = VISION_LOW_SPEED_STOP_BUFFER_MIN_BRAKE + VISION_LOW_SPEED_STOP_BUFFER_BRAKE_GAIN * float(v_ego)
    return max(accel_min, -min_stop_brake), True

  def get_lead_catchup_accel_cap(self, lead, v_ego, t_follow):
    if lead is None or not lead.status or v_ego < LEAD_CATCHUP_ACCEL_MIN_EGO:
      return None

    lead_delta = float(lead.vLead) - float(v_ego)
    if lead_delta < LEAD_CATCHUP_ACCEL_MIN_LEAD_DELTA:
      return None

    desired_gap = float(desired_follow_distance(v_ego, lead.vLead, t_follow))
    gap_buffer = max(LEAD_CATCHUP_ACCEL_MAX_GAP_BUFFER_MIN, LEAD_CATCHUP_ACCEL_MAX_GAP_BUFFER_GAIN * float(v_ego))
    gap_error = float(lead.dRel) - desired_gap
    if gap_error > gap_buffer:
      return None

    # If the lead is already pace-matched or pulling away, keep any catch-up
    # accel very small while we're near the follow target so we don't surge into
    # the lead and immediately ask for brake again.
    edge_cap = float(np.interp(lead_delta, [-0.5, 0.0, 1.0], [0.16, 0.08, 0.02]))
    near_cap = min(edge_cap, 0.03)
    gap_factor = float(np.clip(max(gap_error, 0.0) / max(gap_buffer, 0.1), 0.0, 1.0))
    return float(np.interp(gap_factor, [0.0, 1.0], [near_cap, edge_cap]))

  @staticmethod
  def raw_close_lead_needs_control(lead, v_ego):
    if lead is None or not lead.status:
      return False

    closing_speed = float(v_ego - lead.vLead)
    lead_braking = float(lead.aLeadK) < -0.5
    if closing_speed <= RAW_LEAD_SAFETY_MIN_CLOSING_SPEED and not lead_braking:
      return False

    d_rel = max(float(lead.dRel), 0.0)
    dynamic_distance = max(RAW_LEAD_SAFETY_DISTANCE, 3.0 * float(v_ego))
    ttc = d_rel / max(closing_speed, 0.1) if closing_speed > 0.1 else float("inf")
    return d_rel < dynamic_distance and (ttc < RAW_LEAD_SAFETY_TTC or lead_braking)

  def update(self, sm, starpilot_toggles):
    self.generation = getattr(starpilot_toggles, "model_version", None)
    self.mode = 'blended' if sm['selfdriveState'].experimentalMode else 'acc'
    self.mpc.mode = 'acc'
    if not self.mlsim:
      self.mpc.mode = self.mode

    if len(sm['carControl'].orientationNED) == 3:
      accel_coast = get_coast_accel(sm['carControl'].orientationNED[1])
    else:
      accel_coast = ACCEL_MAX

    v_ego = get_planner_v_ego(self.CP, sm['carState'])
    v_cruise = sm['starpilotPlan'].vCruise
    if not np.isfinite(v_cruise):
      cloudlog.error(f"Longitudinal planner received non-finite vCruise={v_cruise}, falling back to v_ego={v_ego:.2f}")
      v_cruise = max(v_ego, 0.0)
    v_cruise_initialized = sm['carState'].vCruise != V_CRUISE_UNSET

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off
    force_slow_decel = sm['controlsState'].forceDecel

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    reset_state = reset_state or not v_cruise_initialized

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    if self.mpc.mode == 'acc':
      accel_limits = [sm['starpilotPlan'].minAcceleration, sm['starpilotPlan'].maxAcceleration]
      steer_angle_without_offset = sm['carState'].steeringAngleDeg - sm['liveParameters'].angleOffsetDeg
      accel_limits_turns = limit_accel_in_turns(v_ego, steer_angle_without_offset, accel_limits, self.CP)
      accel_limits_turns[0] = max(get_vehicle_min_accel(self.CP, v_ego), accel_limits_turns[0])
    else:
      accel_limits = [ACCEL_MIN, ACCEL_MAX]
      accel_limits_turns = [ACCEL_MIN, ACCEL_MAX]

    if reset_state:
      self.v_desired_filter.x = v_ego
      # Clip aEgo to cruise limits to prevent large accelerations when becoming active
      self.a_desired = np.clip(sm['carState'].aEgo, accel_limits[0], accel_limits[1])
      self.model_allow_throttle = True

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))
    # Compute model v_ego error
    self.v_model_error = self.get_model_speed_error(sm['modelV2'], v_ego)
    x, v, a, j, throttle_prob = self.parse_model(sm['modelV2'], self.v_model_error, v_ego, starpilot_toggles)
    # Don't clip at low speeds since throttle_prob doesn't account for creep. Use
    # hysteresis here because raw gasPressProb noise can chatter the throttle gate.
    if v_ego <= MIN_ALLOW_THROTTLE_SPEED:
      self.model_allow_throttle = True
    elif self.model_allow_throttle:
      self.model_allow_throttle = throttle_prob > ALLOW_THROTTLE_DISABLE_THRESHOLD
    else:
      self.model_allow_throttle = throttle_prob > ALLOW_THROTTLE_ENABLE_THRESHOLD
    self.allow_throttle = self.model_allow_throttle and not sm['starpilotPlan'].disableThrottle

    if not self.allow_throttle:
      clipped_accel_coast = max(accel_coast, accel_limits_turns[0])
      clipped_accel_coast_interp = np.interp(v_ego, [MIN_ALLOW_THROTTLE_SPEED, MIN_ALLOW_THROTTLE_SPEED*2], [accel_limits_turns[1], clipped_accel_coast])
      accel_limits_turns[1] = min(accel_limits_turns[1], clipped_accel_coast_interp)
    no_throttle_output_max = accel_limits_turns[1]

    if force_slow_decel:
      v_cruise = 0.0
    # clip limits, cannot init MPC outside of bounds
    accel_limits_turns[0] = min(accel_limits_turns[0], self.a_desired + 0.05)
    accel_limits_turns[1] = max(accel_limits_turns[1], self.a_desired - 0.05)

    tracking_lead = bool(sm['starpilotPlan'].trackingLead)
    self.lead_one = sm['radarState'].leadOne
    self.lead_two = sm['radarState'].leadTwo
    raw_close_lead_control = any(self.raw_close_lead_needs_control(lead, v_ego) for lead in (self.lead_one, self.lead_two))
    # StarPilot trackingLead is debounce/model-length based. Keep a raw close-lead
    # safety path so ACC/chill does not ignore a visible lead during that debounce.
    lead_control_active = tracking_lead or raw_close_lead_control
    lead_one_active = bool(self.lead_one.status and lead_control_active)
    effective_t_follow = self.get_dynamic_t_follow(sm['starpilotPlan'].tFollow, self.lead_one if lead_one_active else None, v_ego)

    lead_dist = self.lead_one.dRel if lead_one_active else 50.0

    # Smooth lead distance (EMA) to avoid chatter in thresholds
    alpha = max(0.02, min(0.15, 0.05 + 0.002 * v_ego))
    if self.lead_dist_f is None:
      self.lead_dist_f = float(lead_dist)
    else:
      self.lead_dist_f += alpha * (float(lead_dist) - self.lead_dist_f)

    # Lead stability estimation and recent-brake timer
    now_t = time.monotonic()
    # relative speed (ego - lead) positive when closing
    v_rel = (v_ego - self.lead_one.vLead) if lead_one_active else 0.0
    if self.prev_lead_dist is None:
      d_rel_dot = 0.0
    else:
      d_rel_dot = (lead_dist - self.prev_lead_dist) / max(self.dt, 1e-3)
    self.prev_lead_dist = lead_dist

    # Remember time of last non-trivial model brake risk
    if 'raw_brake_max' in locals() and raw_brake_max is not None and raw_brake_max > 0.02:
      self.last_big_brake_t = now_t

    # Stable lead heuristic (short window, cheap to compute)
    recently_braked = (now_t - self.last_big_brake_t) < 0.7
    self.stable_lead = (
      lead_one_active and
      abs(v_rel) < 0.5 and
      abs(d_rel_dot) < 0.5 and
      not recently_braked
    )

    # Calculate scene uncertainty from model desire prediction entropy and disengage predictions
    uncertainty = 0.0
    if hasattr(sm['modelV2'], 'meta'):
      # Desire prediction entropy (maneuver uncertainty), normalized to [0, 1]
      desire_entropy = 0.0
      if hasattr(sm['modelV2'].meta, 'desirePrediction'):
        desire_probs = sm['modelV2'].meta.desirePrediction
        if len(desire_probs) > 1:
          probs = np.asarray(desire_probs, dtype=float)
          total = float(np.sum(probs))
          if total > 1e-6:
            p = probs / total
            entropy = -np.sum(p * np.log(p + 1e-10))
            max_entropy = np.log(len(p))
            desire_entropy = float(entropy / max(max_entropy, 1e-6))  # normalized entropy in [0,1]
          else:
            desire_entropy = 0.0  # guard against all-zero vector

      # Disengage prediction risk (intervention likelihood)
      disengage_risk = 0.0
      raw_brake_max = -1.0
      lam = -1.0
      if hasattr(sm['modelV2'].meta, 'disengagePredictions'):
        # Use brake press probabilities as primary risk indicator
        brake_probs = sm['modelV2'].meta.disengagePredictions.brakePressProbs
        if len(brake_probs) > 0:
          # Exponentially decayed max over the full horizon
          probs = np.asarray(brake_probs, dtype=float)
          # Clip tiny brake blips so they don't inflate uncertainty
          if float(np.max(probs)) < 0.015:
            probs = probs * 0.5
          raw_brake_max = float(np.max(probs))
          # Time vector assuming model horizon step = DT_MDL
          t = np.arange(len(probs), dtype=float) * DT_MDL
          lam = 0.6  # decay rate per second (tunable: 0.5–0.9 typical)
          weights = np.exp(-lam * t)
          disengage_risk = float(np.max(probs * weights))

      # Combined uncertainty metric (range roughly 0..2), with dual-track filtering
      raw_uncertainty = desire_entropy + disengage_risk
      # Update filters
      self.uncert_slow.update(raw_uncertainty)
      self.uncert_fast.update(raw_uncertainty)
      # Use a more permissive track for accel decisions
      uncertainty = self.uncert_slow.x
    uncertainty_accel = min(self.uncert_slow.x, self.uncert_fast.x)

    # --- Slope-based panic bypass ---
    if self._uncert_last_t is None:
      uncert_slope = 0.0
    else:
      dt_u = max(1e-3, now_t - self._uncert_last_t)
      uncert_slope = (uncertainty - self._uncert_last) / dt_u
    self._uncert_last = uncertainty
    self._uncert_last_t = now_t

    closing_fast = lead_one_active and (v_ego - self.lead_one.vLead) > 0.5
    # Trigger if either slope is high or magnitude is high; require a valid lead and closing
    panic_bypass = closing_fast and (uncert_slope > UNCERT_SLOPE_TRIG or uncertainty >= UNCERT_MAG_TRIG)

    if panic_bypass:
      try:
        cloudlog.error(f"LON_SLOPE; slope={uncert_slope:.3f}/s; uncertainty={uncertainty:.3f}; v_ego={v_ego:.2f}; v_rel={(v_ego - self.lead_one.vLead) if lead_one_active else 0.0:.2f}; lead_dist={self.lead_dist_f if self.lead_dist_f is not None else -1:.2f}; trigger=True")
      except Exception:
        pass

    personality = get_longitudinal_personality(sm)

    self.mpc.set_weights(sm['starpilotPlan'].accelerationJerk,
                         sm['starpilotPlan'].dangerJerk,
                         sm['starpilotPlan'].speedJerk,
                         prev_accel_constraint,
                         personality=personality,
                         v_ego=v_ego,
                         lead_dist=self.lead_dist_f if lead_one_active and self.lead_dist_f is not None else 50.0,
                         uncertainty=uncertainty,
                         panic_bypass=panic_bypass)
    self.mpc.set_accel_limits(accel_limits_turns[0], accel_limits_turns[1])
    self.mpc.set_cur_state(self.v_desired_filter.x, self.a_desired)
    # After deciding the MPC mode via get_mpc_mode(), ensure MPC uses that mode when not mlsim
    dec_mpc_mode = self.get_mpc_mode()
    if not self.mlsim:
      self.mpc.mode = dec_mpc_mode
    self.mpc.update(sm['radarState'], v_cruise, x, v, a, j,
                    sm['starpilotPlan'].dangerFactor, effective_t_follow,
                    personality=personality, tracking_lead=lead_control_active)

    self.a_desired_trajectory_full = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = self.mpc.crash_cnt > 2 and not sm['carState'].standstill
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Safety checks for rubber-banding mitigation
    max_jerk = np.max(np.abs(self.mpc.j_solution))
    max_accel_change = np.max(np.abs(np.diff(self.mpc.a_solution)))
    if max_jerk > 5.0:  # m/s^3
      cloudlog.warning(f"High jerk detected: {max_jerk:.2f} m/s^3")
    if max_accel_change > 2.0:  # m/s^2
      cloudlog.warning(f"High acceleration change: {max_accel_change:.2f} m/s^2")

    # Interpolate 0.05 seconds and save as starting point for next iteration
    a_prev = self.a_desired
    self.a_desired = float(np.interp(self.dt, CONTROL_N_T_IDX, self.a_desired_trajectory))
    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.a_desired + a_prev) / 2.0

    # Anticipatory pre-brake to avoid "coming in hot" when closing on a lead
    if lead_one_active:
      rel_v = max(0.0, v_ego - self.lead_one.vLead)
      # dynamic time headway adds a small buffer when uncertainty is elevated
      base_th = max(1.6, effective_t_follow)
      th = base_th + 0.6 * max(0.0, uncertainty - 0.42)
      desired_gap = th * v_ego
      if (self.lead_dist_f is not None and self.lead_dist_f < desired_gap and rel_v > 0.5):
        k_rel, k_unc = 0.04, 0.20
        pre_brake = k_rel * rel_v + k_unc * max(0.0, uncertainty - 0.42)
        pre_brake = min(pre_brake, 0.06)
        self.a_desired = float(self.a_desired - pre_brake)

    # Small deadzone around zero accel to kill micro-dithers
    if -0.05 < self.a_desired < 0.05:
      self.a_desired = 0.0

    classic_model = bool(getattr(starpilot_toggles, "classic_model", False))
    tinygrad_model = bool(getattr(starpilot_toggles, "tinygrad_model", False))
    experimental_mlsim = bool(tinygrad_model and self.mlsim and self.mode != 'acc')
    action_t = self.CP.longitudinalActuatorDelay + DT_MDL

    if classic_model:
      output_a_target, output_should_stop = get_accel_from_plan_classic(
        self.CP, self.v_desired_trajectory, self.a_desired_trajectory, starpilot_toggles.vEgoStopping)
    elif tinygrad_model:
      output_a_target_mpc, output_should_stop_mpc = get_accel_from_plan(
        self.v_desired_trajectory, self.a_desired_trajectory,
        action_t=action_t, vEgoStopping=starpilot_toggles.vEgoStopping)
      output_a_target_e2e = sm['modelV2'].action.desiredAcceleration
      output_should_stop_e2e = sm['modelV2'].action.shouldStop

      if self.mode == 'acc' or self.generation == 'v9':
        output_a_target = output_a_target_mpc
        output_should_stop = output_should_stop_mpc
      else:
        output_a_target = min(output_a_target_mpc, output_a_target_e2e)
        output_should_stop = output_should_stop_e2e or output_should_stop_mpc
    else:
      output_a_target, output_should_stop = get_accel_from_plan(
        self.v_desired_trajectory, self.a_desired_trajectory,
        action_t=action_t, vEgoStopping=starpilot_toggles.vEgoStopping)

    comfort_output_accel_min = get_vehicle_min_accel(self.CP, v_ego) if experimental_mlsim else accel_limits_turns[0]
    vision_cap_accel_min = min(comfort_output_accel_min, get_vehicle_min_accel(self.CP, v_ego))
    output_accel_min = comfort_output_accel_min

    if not tracking_lead:
      pretracking_vision_caps = []
      for lead in (self.lead_one, self.lead_two):
        if lead.status and not bool(getattr(lead, "radar", False)):
          pretracking_cap = self.get_vision_untracked_slow_lead_cap(lead, v_ego, vision_cap_accel_min)
          if pretracking_cap is not None:
            pretracking_vision_caps.append(pretracking_cap)

      if pretracking_vision_caps:
        pretracking_vision_cap = min(pretracking_vision_caps)
        self.a_desired = min(self.a_desired, pretracking_vision_cap)
        output_a_target = min(output_a_target, pretracking_vision_cap)

    close_lead_caps = []
    vision_low_speed_stop_active = False
    vision_brake_cap_active = False
    if lead_control_active:
      for lead in (self.lead_one, self.lead_two):
        cap = self.get_close_lead_brake_cap(lead, v_ego, output_accel_min)
        if cap is not None:
          close_lead_caps.append(cap)
        slow_stop_cap = self.get_vision_slow_stopped_lead_cap(lead, v_ego, vision_cap_accel_min, effective_t_follow)
        if slow_stop_cap is not None:
          close_lead_caps.append(slow_stop_cap)
          vision_brake_cap_active = True
        approach_cap = self.get_vision_lead_approach_cap(lead, v_ego, vision_cap_accel_min, effective_t_follow)
        if approach_cap is not None:
          close_lead_caps.append(approach_cap)
          vision_brake_cap_active = True
        low_speed_stop_cap, low_speed_stop_active = self.get_vision_low_speed_stop_buffer_cap(lead, v_ego, vision_cap_accel_min)
        if low_speed_stop_cap is not None:
          close_lead_caps.append(low_speed_stop_cap)
          vision_brake_cap_active = True
        vision_low_speed_stop_active |= low_speed_stop_active
    if close_lead_caps:
      close_lead_brake_cap = min(close_lead_caps)
      self.a_desired = min(self.a_desired, close_lead_brake_cap)
      output_a_target = min(output_a_target, close_lead_brake_cap)

    if lead_control_active and sm['carState'].standstill:
      standstill_nudge_gap = max(float(getattr(starpilot_toggles, "stop_distance", STOP_DISTANCE)), STOP_DISTANCE) - 0.5
      moving_leads = [lead for lead in (self.lead_one, self.lead_two)
                      if lead.status and lead.vLead > STANDSTILL_LEAD_NUDGE_MIN_SPEED and lead.dRel >= standstill_nudge_gap]
      if moving_leads:
        output_a_target = max(output_a_target, STANDSTILL_LEAD_NUDGE_ACCEL)

    if lead_one_active:
      lead_catchup_accel_cap = self.get_lead_catchup_accel_cap(self.lead_one, v_ego, effective_t_follow)
      if lead_catchup_accel_cap is not None:
        self.a_desired = min(self.a_desired, lead_catchup_accel_cap)
        output_a_target = min(output_a_target, lead_catchup_accel_cap)

    if lead_control_active and np.isfinite(v_cruise) and any(lead.status for lead in (self.lead_one, self.lead_two)):
      # Keep follow/catchup behavior from pulling past the cruise target. Using the
      # same action horizon as the planner preserves normal accel farther below set speed.
      cruise_accel_cap = (v_cruise - v_ego + 0.01) / max(action_t, self.dt)
      output_a_target = min(output_a_target, cruise_accel_cap)

    if vision_brake_cap_active:
      output_accel_min = min(output_accel_min, vision_cap_accel_min)

    output_accel_max = no_throttle_output_max if not self.allow_throttle else accel_limits_turns[1]
    output_a_target = float(np.clip(output_a_target, output_accel_min, output_accel_max))

    self.output_a_target = output_a_target
    self.output_should_stop = bool(output_should_stop or vision_low_speed_stop_active)

  def publish(self, sm, pm):
    plan_send = messaging.new_message('longitudinalPlan')

    plan_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'selfdriveState', 'radarState'])

    longitudinalPlan = plan_send.longitudinalPlan
    longitudinalPlan.modelMonoTime = sm.logMonoTime['modelV2']
    longitudinalPlan.processingDelay = (plan_send.logMonoTime / 1e9) - sm.logMonoTime['modelV2']
    longitudinalPlan.solverExecutionTime = self.mpc.solve_time

    longitudinalPlan.speeds = self.v_desired_trajectory.tolist()
    longitudinalPlan.accels = self.a_desired_trajectory.tolist()
    longitudinalPlan.jerks = self.j_desired_trajectory.tolist()

    longitudinalPlan.hasLead = sm['radarState'].leadOne.status
    longitudinalPlan.longitudinalPlanSource = self.mpc.source
    longitudinalPlan.fcw = self.fcw

    longitudinalPlan.aTarget = float(self.output_a_target)
    longitudinalPlan.shouldStop = bool(self.output_should_stop) or (sm['starpilotPlan'].forcingStop and sm['starpilotPlan'].forcingStopLength < 1)
    longitudinalPlan.allowBrake = True
    longitudinalPlan.allowThrottle = bool(self.allow_throttle)

    pm.send('longitudinalPlan', plan_send)
