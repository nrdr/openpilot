#!/usr/bin/env python3
import math
import time
import numpy as np

import openpilot.cereal.messaging as messaging
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc, LongitudinalPlanSource
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, get_accel_from_plan, should_stop
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP
from openpilot.nrdr.features.longitudinal.longitudinal_planner import NrdrLongitudinalPlanner
from openpilot.nrdr.features.longitudinal.policy import longitudinal_personality, nrdr_longitudinal_enabled
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.mvl_planner import MvlLongitudinalPlanner
from openpilot.nrdr.features.radar.radar import is_honda_bosch_a_radar
from openpilot.nrdr.features.longitudinal.bosch_a import human_acceleration, human_following
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_coast_first import BoschACoastFirst
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_onset_ramp import BoschAOnsetRamp
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_release_coast import BoschAReleaseCoast
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_smooth import BoschASmooth
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_stop_gap import BoschAStopGap
from openpilot.nrdr.features.longitudinal.bosch_a.honda_bosch_a_long import HondaBoschALongEnhancement
from openpilot.nrdr.features.longitudinal.bosch_a.model_lead_qualification import ModelLeadHistory, qualified_model_leads

A_CRUISE_MAX_VALS = [1.6, 1.2, 0.8, 0.6]
A_CRUISE_MAX_BP = [0., 10.0, 25., 40.]
J_CRUISE_VALS = [1.6, 1.2, 0.8, 0.6]
A_CRUISE_MIN = -1.2
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
ALLOW_THROTTLE_THRESHOLD = 0.4
MIN_ALLOW_THROTTLE_SPEED = 2.5

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]

def get_max_accel(v_ego):
  return np.interp(v_ego, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)

def get_coast_accel(pitch):
  return np.sin(pitch) * -5.65 - 0.3  # fitted from data using xx/projects/allow_throttle/compute_coast_accel.py

def limit_accel_in_turns(v_ego, angle_steers, a_target, CP, min_lat_accel=0.0):
  """
  This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
  this should avoid accelerating when losing the target in turns
  """
  # FIXME: This function to calculate lateral accel is incorrect and should use the VehicleModel
  # The lookup table for turns should also be updated if we do this
  a_total_max = np.interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
  a_y = v_ego ** 2 * angle_steers * CV.DEG_TO_RAD / (CP.steerRatio * CP.wheelbase)
  if min_lat_accel > 0.0 and abs(a_y) <= min_lat_accel:
    return a_target
  a_x_allowed = math.sqrt(max(a_total_max ** 2 - a_y ** 2, 0.))

  return [a_target[0], min(a_target[1], a_x_allowed)]


def get_cruise_accel(e2e, v_cruise, v_ego, a_cruise_prev, angle_steers, CP, dt, accel_coast, allow_throttle,
                     max_accel_override=None, min_lat_accel=0.0, positive_accel_ceiling=None):
  max_accel = ACCEL_MAX if e2e else (get_max_accel(v_ego) if max_accel_override is None else max_accel_override)

  if not e2e:
    max_accel = limit_accel_in_turns(v_ego, angle_steers, [ACCEL_MIN, max_accel], CP, min_lat_accel)[1]
    if not allow_throttle:
      clipped_accel_coast = max(accel_coast, ACCEL_MIN)
      coast_limit = np.interp(v_ego, [MIN_ALLOW_THROTTLE_SPEED, MIN_ALLOW_THROTTLE_SPEED*2], [max_accel, clipped_accel_coast])
      max_accel = min(max_accel, coast_limit)

  target_accel = np.clip(v_cruise - v_ego, A_CRUISE_MIN, max_accel)
  if not e2e and target_accel > 0.0 and positive_accel_ceiling is not None:
    try:
      ceiling = float(positive_accel_ceiling)
    except (OverflowError, TypeError, ValueError):
      ceiling = math.nan
    if np.isfinite(ceiling):
      target_accel = min(target_accel, max(0.0, ceiling))
  j_cruise = np.interp(v_ego, A_CRUISE_MAX_BP, J_CRUISE_VALS)
  target_accel = float(np.clip(target_accel, a_cruise_prev - j_cruise * dt, a_cruise_prev + j_cruise * dt))

  return target_accel


# Bosch-A engage init only: the same law with the jerk limit made unreachable (dt this large puts the clip bounds far outside
# any cruise target), so the planner's single get_cruise_accel call site and the function itself stay as they were.
_cruise_accel_without_jerk_limit = get_cruise_accel
_NO_JERK_LIMIT_DT = 1.0e6


def bosch_a_human_accel_base(nrdr, experimental: bool, v_ego: float, personality) -> float:
  """HumanAcceleration's base: the planner's own max accel. SOURCE: ACCEL_MAX in experimental mode, else the selected
  profile cap, else the stock get_max_accel(v_ego). NRDR has no profile cap: its equivalent of get_max_accel is
  nrdr.max_accel(v_ego), and its personality ceiling is applied on top exactly as get_cruise_accel applies it
  (min with max(0, ceiling), ignored if None / non-finite), so the cap never exceeds the cruise path's own limit."""
  if experimental:
    return ACCEL_MAX
  max_accel, _, ceiling = nrdr.accel_envelope(v_ego, personality)
  if ceiling is not None:
    try:
      ceiling = float(ceiling)
    except (OverflowError, TypeError, ValueError):
      ceiling = math.nan
    if np.isfinite(ceiling):
      max_accel = min(max_accel, max(0.0, ceiling))
  return max_accel


class LongitudinalPlanner(LongitudinalPlannerSP):
  def __init__(self, CP, CP_SP, init_v=0.0, init_a=0.0, dt=DT_MDL):
    self.mvl_enabled = mvl_longitudinal_enabled(CP)
    if self.mvl_enabled:
      MvlLongitudinalPlanner.__init__(self, CP, CP_SP, init_v, init_a, dt)
      return
    self.CP = CP
    self.honda_bosch_a_radar = is_honda_bosch_a_radar(CP)
    nrdr_enabled = nrdr_longitudinal_enabled(CP)
    # Bosch-A longitudinal tuning (HumanFollowing, HumanAcceleration and the post-MPC chain). Always on for a Bosch-A Honda
    # with openpilot longitudinal; MVL has already returned above.
    from openpilot.nrdr.features.longitudinal.bosch_a import gate as bosch_a_gate
    self.bosch_a_wired = bool(nrdr_enabled and bosch_a_gate.human_following_enabled(CP))
    self.mpc = LongitudinalMpc(dt=dt, honda_bosch_a_radar=self.honda_bosch_a_radar, nrdr_enabled=nrdr_enabled,
                               human_following=self.bosch_a_wired)
    if self.bosch_a_wired:
      self.bosch_a_long = HondaBoschALongEnhancement(CP, dt)
      self.bosch_a_smooth = BoschASmooth(CP, dt)
      self.bosch_a_coast_first = BoschACoastFirst(CP, dt)
      self.bosch_a_release_coast = BoschAReleaseCoast(CP, dt)
      self.bosch_a_onset_ramp = BoschAOnsetRamp(CP, dt)
      self.bosch_a_stop_gap = BoschAStopGap(CP, dt)
      self.bosch_a_model_lead_history = ModelLeadHistory()  # SOURCE planner: model_lead_history
      self.bosch_a_clock_ns = time.monotonic_ns  # SOURCE planner: clock_ns
    self.nrdr = NrdrLongitudinalPlanner(CP, CP_SP, self.mpc.tune) if nrdr_enabled else None
    LongitudinalPlannerSP.__init__(self, self.CP, CP_SP, self.mpc)
    self.fcw = False
    self.dt = dt
    self.allow_throttle = True

    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.a_cruise = init_a
    self.prev_accel_clip = [ACCEL_MIN, ACCEL_MAX]
    self.output_a_target = init_a
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)

  def update(self, sm):
    if self.mvl_enabled:
      return MvlLongitudinalPlanner.update(self, sm)
    LongitudinalPlannerSP.update(self, sm)
    if self.nrdr is not None:
      self.nrdr.refresh()

    if len(sm['carControl'].orientationNED) == 3:
      accel_coast = get_coast_accel(sm['carControl'].orientationNED[1])
    else:
      accel_coast = ACCEL_MAX

    v_ego = sm['carState'].vEgo
    v_cruise_kph = min(sm['carState'].vCruise, V_CRUISE_MAX)
    v_cruise = v_cruise_kph * CV.KPH_TO_MS
    v_cruise_initialized = sm['carState'].vCruise != V_CRUISE_UNSET
    force_slow_decel = sm['controlsState'].forceDecel
    if self.nrdr is None and force_slow_decel:
      v_cruise = 0.0

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    reset_state = reset_state or not v_cruise_initialized

    throttle_probs = sm['modelV2'].meta.disengagePredictions.gasPressProbs
    throttle_prob = throttle_probs[1] if len(throttle_probs) > 1 else 1.0
    self.allow_throttle = throttle_prob > ALLOW_THROTTLE_THRESHOLD or v_ego <= MIN_ALLOW_THROTTLE_SPEED

    accel_clip = [ACCEL_MIN, ACCEL_MAX]
    steer_angle_without_offset = sm['carState'].steeringAngleDeg - sm['vehicleParameters'].angleOffsetDeg
    if self.nrdr is not None:
      accel_clip[1] = self.nrdr.max_accel(v_ego)
      accel_clip = limit_accel_in_turns(
        v_ego, steer_angle_without_offset, accel_clip, self.CP, self.nrdr.turn_accel_threshold(),
      )
      if not self.allow_throttle:
        clipped_accel_coast = max(accel_coast, accel_clip[0])
        coast_limit = np.interp(v_ego, [MIN_ALLOW_THROTTLE_SPEED, MIN_ALLOW_THROTTLE_SPEED * 2],
                                [accel_clip[1], clipped_accel_coast])
        accel_clip[1] = min(accel_clip[1], coast_limit)

    if reset_state:
      self.v_desired_filter.x = v_ego
      self.output_a_target = np.clip(sm['carState'].aEgo, accel_clip[0], accel_clip[1])
      self.a_cruise = self.output_a_target

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    # Get new v_cruise and a_target from Smart Cruise Control and Speed Limit Assist
    v_cruise, self.output_a_target = LongitudinalPlannerSP.update_targets(self, sm, self.v_desired_filter.x, self.output_a_target, v_cruise)

    if self.nrdr is not None:
      if force_slow_decel:
        v_cruise = 0.0
      v_cruise = self.nrdr.cruise_target(v_cruise)

    personality = longitudinal_personality(sm['selfdriveState'].personality, self.nrdr is not None)
    self.mpc.set_weights(prev_accel_constraint, personality=personality)
    self.mpc.set_cur_state(self.v_desired_filter.x, self.output_a_target)
    planner_radar_state = sm['radarState']
    bosch_a_mpc = {}
    human_accel_base = None
    if self.bosch_a_wired:
      # HumanAcceleration scales the planner's own max accel (SOURCE: profile, else the stock cruise curve; here the
      # NRDR cruise curve). The MPC and the enhancement's stock-feel law read the same bounded leads (D-080, a2 seg 50).
      human_accel_base = bosch_a_human_accel_base(self.nrdr, bool(sm['selfdriveState'].experimentalMode), v_ego, personality)
      planner_radar_state = self.bosch_a_long.planner_radar_state(sm['radarState'], float(sm['carState'].aEgo),
                                                                   model_v2=sm['modelV2'])
      bosch_a_mpc = {  # SOURCE: the MPC only sees modelV2 that qualified_model_leads accepted this frame (fresh, matched
                     # to radarState); otherwise None, so each lead keeps its raw aLeadK extrapolation.
                     'lead_paths': human_following.upstream_lead_paths(
                       qualified_model_leads(sm, self.bosch_a_clock_ns(), self.bosch_a_model_lead_history),
                       planner_radar_state, self.mpc.x0[1])}
      # Biscuit-Labs#78: the human acceleration cap is Relaxed, Standard and Econ; Aggressive keeps the planner's own max accel.
      if human_acceleration.applies(personality):
        bosch_a_mpc['acceleration_max'] = human_acceleration.cap(human_accel_base, v_cruise, v_ego)
    self.mpc.update(planner_radar_state, personality=personality,
                    model=sm['modelV2'], v_cruise=v_cruise,
                    extra_stop_distance=self.nrdr.stopped_gap(reset_state) if self.nrdr is not None else 0.0,
                    **bosch_a_mpc)

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = (self.mpc.crash_cnt > 2 and not sm['carState'].standstill and
                (self.nrdr is None or self.mpc.nrdr.fcw_authorized(sm['radarState'].leadOne, v_ego)))
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Save starting point for next iteration
    a_prev = self.output_a_target

    action_t =  self.CP.longitudinalActuatorDelay + DT_MDL
    output_a_target_mpc = get_accel_from_plan(
      self.v_desired_trajectory, self.a_desired_trajectory, CONTROL_N_T_IDX,
      action_t=self.bosch_a_smooth.action_t(self.CP.longitudinalActuatorDelay) if self.bosch_a_wired else action_t)
    output_should_stop_mpc = (bool(self.v_desired_trajectory[0] < self.nrdr.v_ego_stopping and output_a_target_mpc < 0.1)
                              if self.nrdr is not None else should_stop(v_ego, output_a_target_mpc))
    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration
    output_should_stop_e2e = sm['modelV2'].action.shouldStop
    if self.nrdr is not None:
      output_a_target_e2e = self.nrdr.launch_accel(
        sm, T_IDXS_MPC, action_t, v_ego, output_should_stop_e2e, output_a_target_e2e, sm['selfdriveState'].experimentalMode,
      )

    is_e2e = sm['selfdriveState'].experimentalMode

    self.a_cruise = get_cruise_accel(is_e2e, v_cruise, v_ego,
                                     self.a_cruise, steer_angle_without_offset, self.CP, self.dt,
                                     accel_coast, self.allow_throttle,
                                     max_accel_override=self.nrdr.max_accel(v_ego) if self.nrdr is not None else None,
                                     min_lat_accel=self.nrdr.turn_accel_threshold() if self.nrdr is not None else 0.0,
                                     positive_accel_ceiling=(self.nrdr.personality_accel_ceiling(v_ego, personality)
                                                            if self.nrdr is not None else None))
    cruise_should_stop = (bool(v_ego < self.nrdr.v_ego_stopping and self.a_cruise < 0.1)
                          if self.nrdr is not None else should_stop(v_ego, self.a_cruise))

    output_a_target_e2e = LongitudinalPlannerSP.apply_accel_boost(
      self, sm, output_a_target_e2e, output_a_target_mpc, self.a_cruise,
    )

    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),
                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop)]
    if is_e2e:
      candidates.append((output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e))

    output_a_target, self.mpc.source, _ = min(candidates, key=lambda c: c[0])
    self.output_should_stop = any(should_stop for _, _, should_stop in candidates)
    if self.bosch_a_wired:
      # Post-MPC Bosch-A chain, SOURCE order (starpilot longitudinal_planner.py): HumanAcceleration cap (throttle side
      # only; the cap is >= 0 so a braking target passes through), engage init, then bosch_a_long -> coast_first ->
      # release_coast -> smooth -> onset_ramp -> stop_gap.
      output_a_target = min(output_a_target, bosch_a_mpc['acceleration_max'])
      if self.bosch_a_long.stock_feel and reset_state:
        # Engage init: while long is off, a_cruise starts the first engaged frame at min(aEgo, cruise target) instead of
        # aEgo (jerk-limited around aEgo). Lowers only; output_a_target and the MPC state are unchanged.
        max_accel, min_lat_accel, accel_ceiling = self.nrdr.accel_envelope(v_ego, personality)
        self.a_cruise = min(self.a_cruise, float(_cruise_accel_without_jerk_limit(
          is_e2e, v_cruise, v_ego, self.a_cruise, steer_angle_without_offset, self.CP, _NO_JERK_LIMIT_DT,
          accel_coast, self.allow_throttle, max_accel_override=max_accel, min_lat_accel=min_lat_accel,
          positive_accel_ceiling=accel_ceiling)))
      lead_one, lead_two = planner_radar_state.leadOne, planner_radar_state.leadTwo
      standstill = bool(sm['carState'].standstill)
      output_a_target = self.bosch_a_long.step(
        lead_one=lead_one, lead_two=lead_two, prev=float(a_prev), target=float(output_a_target), v_ego=v_ego,
        stopping=bool(self.output_should_stop), standstill=standstill, reset_state=bool(reset_state))
      output_a_target = self.bosch_a_coast_first.step(
        lead_one=lead_one, lead_two=lead_two, target=float(output_a_target), v_ego=v_ego,
        follow_s=float(self.mpc.params[0, 4]), fcw=bool(self.fcw), reset_state=bool(reset_state))
      output_a_target = self.bosch_a_release_coast.update(
        lead_one=lead_one, target=float(output_a_target), lane_change_state=sm['modelV2'].meta.laneChangeState,
        left_blinker=bool(sm['carState'].leftBlinker), right_blinker=bool(sm['carState'].rightBlinker),
        gas_pressed=bool(sm['carState'].gasPressed), reset_state=bool(reset_state))
      output_a_target = self.bosch_a_smooth.step(float(a_prev), float(output_a_target),
                                                 reset=bool(reset_state or standstill))
      output_a_target = self.bosch_a_onset_ramp.step(
        lead_one=lead_one, lead_two=lead_two, prev=float(a_prev), target=float(output_a_target), fcw=bool(self.fcw),
        stopping=bool(self.output_should_stop), reset=bool(reset_state or standstill))
      output_a_target, self.output_should_stop = self.bosch_a_stop_gap.step(
        lead_one=lead_one, lead_two=lead_two, target=float(output_a_target), should_stop=bool(self.output_should_stop),
        v_ego=v_ego, standstill=standstill, reset_state=bool(reset_state))
    if self.nrdr is not None:
      for idx in range(2):
        accel_clip[idx] = np.clip(accel_clip[idx], self.prev_accel_clip[idx] - 0.05, self.prev_accel_clip[idx] + 0.05)
    self.output_a_target = np.clip(output_a_target, accel_clip[0], accel_clip[1])
    self.prev_accel_clip = accel_clip

    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.output_a_target + a_prev) / 2.0

  def publish(self, sm, pm):
    if self.mvl_enabled:
      return MvlLongitudinalPlanner.publish(self, sm, pm)
    plan_send = messaging.new_message('longitudinalPlan')

    plan_send.valid = sm.all_checks()

    longitudinalPlan = plan_send.longitudinalPlan
    longitudinalPlan.modelMonoTime = sm.logMonoTime['modelV2']
    longitudinalPlan.processingDelay = (plan_send.logMonoTime / 1e9) - sm.logMonoTime['modelV2']
    longitudinalPlan.solverExecutionTime = self.mpc.solve_time

    longitudinalPlan.speeds = self.v_desired_trajectory.tolist()
    longitudinalPlan.accels = self.a_desired_trajectory.tolist()
    longitudinalPlan.jerks = self.j_desired_trajectory.tolist()

    longitudinalPlan.hasLead = sm['radarState'].leadOne.present
    longitudinalPlan.longitudinalPlanSource = self.mpc.source
    longitudinalPlan.fcw = self.fcw

    longitudinalPlan.leadTrajectoryX0 = self.mpc.lead_xv_0[:, 0].tolist()
    longitudinalPlan.leadTrajectoryV0 = self.mpc.lead_xv_0[:, 1].tolist()
    longitudinalPlan.leadTrajectoryX1 = self.mpc.lead_xv_1[:, 0].tolist()
    longitudinalPlan.leadTrajectoryV1 = self.mpc.lead_xv_1[:, 1].tolist()

    longitudinalPlan.aTarget = float(self.output_a_target)
    longitudinalPlan.shouldStop = bool(self.output_should_stop)
    longitudinalPlan.allowBrake = True
    longitudinalPlan.allowThrottle = bool(self.allow_throttle)

    pm.send('longitudinalPlan', plan_send)

    self.publish_longitudinal_plan_sp(sm, pm)
