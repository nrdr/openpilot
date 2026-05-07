#!/usr/bin/env python3
import math

from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL

from openpilot.starpilot.common.starpilot_variables import CITY_SPEED_LIMIT, CRUISING_SPEED, PLANNER_TIME
from openpilot.starpilot.controls.lib.curve_speed_controller import CurveSpeedController
from openpilot.starpilot.controls.lib.speed_limit_controller import SpeedLimitController

CSC_MIN_SPEED = CITY_SPEED_LIMIT * CV.MPH_TO_MS
OVERRIDE_FORCE_STOP_TIMER = 10

# Force-stop kinematic profile. The user tunes one signed knob (ForceStopDistanceOffset,
# in feet); positive = stop later/longer, negative = stop sooner/shorter. All other
# shape parameters are fixed constants converged from FP-Testing Sessions A-O.
COMFORT_DECEL = 1.0       # m/s^2 — kinematic decel ceiling
ACTIVATION_M = 75.0       # m — CEM/model path activates when model_length < this
MPC_HANDOFF_M = 6.0       # m — below this, command 0 and let MPC finish the stop
ADAS_MAX_MS = 17.88       # 40 mph — cross-street ADAS guard
DASH_SEED_M = 27.0        # ~88 ft — typical ADAS detection distance, used to snap
                          # tracked length closer when dashboard confirms a sign
FT_TO_M = 0.3048

# Knob bounds (mirror of UI slider; defense in depth)
OFFSET_FT_MIN = -20
OFFSET_FT_MAX = 20


def get_active_slc_control_target(speed_limit_controller, set_speed_limit, slc_target, slc_offset, overridden_speed, v_ego_diff):
  # `SetSpeedLimit` only controls engage-time set-speed initialization. Ongoing
  # SLC speed matching must remain active whenever Speed Limit Controller is on.
  if not speed_limit_controller:
    return 0.0

  base_target = max(float(overridden_speed), float(slc_target) + float(slc_offset))
  if base_target <= 0.0:
    return 0.0

  return max(0.0, base_target - float(v_ego_diff))


class StarPilotVCruise:
  def __init__(self, StarPilotPlanner):
    self.starpilot_planner = StarPilotPlanner

    self.csc = CurveSpeedController(self)
    self.slc = SpeedLimitController(self)

    self.forcing_stop = False
    self.override_force_stop = False
    self.override_force_standstill = False

    self.override_force_stop_timer = 0
    self.force_stop_timer = 0.0
    # Kinematic distance estimator. Same attribute also published as
    # starpilotPlan.forcingStopLength, so the existing reader keeps working.
    self.tracked_model_length = 0.0

    self.stop_sign_confirmed = False

  # ===== Main update =====

  def update(self, controls_enabled, now, time_validated, v_cruise, v_ego, sm, starpilot_toggles):
    long_control_active = sm["carControl"].longActive

    # ----- Activation paths -----
    # Raw lead check: block Force Stop as soon as a relevant lead is present, without
    # waiting for the tracking_lead filter (~1s ramp). Without this, Force Stop can latch
    # during the filter's settling window and stay committed for the whole stop.
    lead = self.starpilot_planner.lead_one
    lead_present = (bool(getattr(lead, "status", False))
                    and float(getattr(lead, "dRel", float("inf"))) < ACTIVATION_M
                    and float(getattr(lead, "vLead", float("inf"))) < v_ego + 2.0)

    # CEM/model path: model predicted stop within ACTIVATION_M.
    # Exclude when a lead is present (raw or filtered) — the handoff_to_stopped_lead path
    # in CEM can set stop_light_detected even with a lead present, which would incorrectly
    # activate Force Stop and stop the car far behind the lead instead of letting ACC handle it.
    cem_path = (self.starpilot_planner.starpilot_cem.stop_light_detected
                and controls_enabled and starpilot_toggles.force_stops
                and self.starpilot_planner.model_length < ACTIVATION_M
                and self.override_force_stop_timer <= 0
                and not self.starpilot_planner.driving_in_curve
                and not self.starpilot_planner.tracking_lead
                and not lead_present)

    # Dashboard path: ADAS camera confirms a stop sign on our road. Field is 0 on
    # platforms that don't publish ADAS_0x380, so dash_path is naturally inert there.
    dash_value = sm["starpilotCarState"].dashboardStopSign
    dash_active = dash_value > 0
    dash_path = (dash_active and controls_enabled and starpilot_toggles.force_stops
                 and v_ego < ADAS_MAX_MS
                 and self.override_force_stop_timer <= 0
                 and not self.starpilot_planner.driving_in_curve
                 and not self.starpilot_planner.tracking_lead
                 and not lead_present)

    force_stop_active = cem_path or dash_path

    # Latch on first dash frame so the CEM pin can fire and we don't release on
    # transient dashboard dropouts. Cleared in the no-force-stop branch below.
    if dash_path:
      self.stop_sign_confirmed = True

    # Timer ramp. Faster commitment when the dashboard confirms.
    if force_stop_active and not sm["carState"].standstill:
      rate = DT_MDL * 2 if dash_active else DT_MDL
      self.force_stop_timer = min(self.force_stop_timer + rate, 2.0)
    else:
      self.force_stop_timer = max(self.force_stop_timer - DT_MDL * 0.25, 0.0)

    force_stop_enabled = self.force_stop_timer >= 0.5
    # Stay committed across model dropouts until standstill
    force_stop_enabled |= self.forcing_stop and not sm["carState"].standstill

    # Override: gas/accel pedal during an active force stop
    self.override_force_stop |= sm["carState"].gasPressed
    self.override_force_stop |= sm["starpilotCarState"].accelPressed
    self.override_force_stop &= force_stop_enabled

    if self.override_force_stop:
      self.override_force_stop_timer = OVERRIDE_FORCE_STOP_TIMER
    elif self.override_force_stop_timer > 0:
      self.override_force_stop_timer -= DT_MDL

    # ----- Force standstill (independent sibling toggle) -----
    force_standstill_enabled = controls_enabled and starpilot_toggles.force_standstill and sm["carState"].standstill
    if force_standstill_enabled:
      self.override_force_standstill |= sm["carState"].gasPressed
      self.override_force_standstill |= sm["starpilotCarState"].accelPressed
    else:
      self.override_force_standstill = False

    v_cruise_cluster = max(sm["carState"].vCruiseCluster * CV.KPH_TO_MS, v_cruise)
    v_cruise_diff = v_cruise_cluster - v_cruise

    v_ego_cluster = max(sm["carState"].vEgoCluster, v_ego)
    v_ego_diff = v_ego_cluster - v_ego

    # FrogsGoMoo's Curve Speed Controller
    if long_control_active and v_ego > CRUISING_SPEED and self.starpilot_planner.road_curvature_detected and starpilot_toggles.curve_speed_controller:
      self.csc.update_target(v_ego)

      self.csc_controlling_speed = True

      self.csc_target = self.csc.target
    else:
      self.csc.log_data(v_ego, sm)

      self.csc_controlling_speed = False
      self.csc.target_set = False

      self.csc_target = v_cruise

    # Pfeiferj's Speed Limit Controller
    self.slc.starpilot_toggles = starpilot_toggles

    if starpilot_toggles.speed_limit_controller:
      self.slc.update_limits(sm["starpilotCarState"].dashboardSpeedLimit, now, time_validated, v_cruise, v_ego, sm)
      self.slc.update_override(v_cruise, v_cruise_diff, v_ego, v_ego_diff, sm)

      self.slc_offset = self.slc.offset
      self.slc_target = self.slc.target
    elif starpilot_toggles.show_speed_limits:
      self.slc.update_limits(sm["starpilotCarState"].dashboardSpeedLimit, now, time_validated, v_cruise, v_ego, sm, display_only=True)

      self.slc_offset = 0
      self.slc_target = self.slc.target
    else:
      self.slc_offset = 0
      self.slc_target = 0

    # Single tuning knob (signed feet -> meters). Defense clamp on top of UI bounds.
    offset_ft_raw = int(getattr(starpilot_toggles, 'force_stop_distance_offset', 0) or 0)
    offset_ft = max(OFFSET_FT_MIN, min(OFFSET_FT_MAX, offset_ft_raw))
    offset_m = offset_ft * FT_TO_M

    if force_standstill_enabled and not self.override_force_standstill:
      self.forcing_stop = True
      self.tracked_model_length = 0.0
      v_cruise = 0.0

    elif force_stop_enabled and not self.override_force_stop:
      self.forcing_stop |= not sm["carState"].standstill

      # Kinematic distance estimator (also published as forcingStopLength).
      # Decay one-to-one with motion, clamp by current model_length so we adopt
      # the model's view when it regains sight, and snap closer to DASH_SEED_M
      # whenever the dashboard signal is active.
      self.tracked_model_length = max(self.tracked_model_length - (v_ego * DT_MDL), 0.0)
      self.tracked_model_length = min(self.tracked_model_length, self.starpilot_planner.model_length)
      if dash_active:
        self.tracked_model_length = min(self.tracked_model_length, DASH_SEED_M)

      # Kinematic profile with user offset. Positive offset shifts the perceived
      # line further down the road -> car rolls further before commanding 0.
      effective_d = self.tracked_model_length + offset_m
      if effective_d <= MPC_HANDOFF_M:
        v_target = 0.0
      else:
        v_target = math.sqrt(2.0 * COMFORT_DECEL * (effective_d - MPC_HANDOFF_M))

      v_cruise = min(v_target, v_cruise)

    else:
      self.forcing_stop = False
      # Latch is only meaningful during an active force-stop cycle
      self.stop_sign_confirmed = False

      self.tracked_model_length = self.starpilot_planner.model_length

      targets = [self.csc_target, v_cruise]
      slc_control_target = get_active_slc_control_target(
        starpilot_toggles.speed_limit_controller,
        getattr(starpilot_toggles, "set_speed_limit", False),
        self.slc.target_with_offset_for_control,
        0.0,
        self.slc.overridden_speed,
        v_ego_diff,
      )
      if slc_control_target > 0.0:
        targets.append(slc_control_target)
      v_cruise = min([target if target >= CSC_MIN_SPEED else v_cruise for target in targets])

    return v_cruise
