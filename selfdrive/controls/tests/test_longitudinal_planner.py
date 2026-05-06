import sys
import types
from types import SimpleNamespace

import numpy as np
import pytest

from cereal import log
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner, get_vehicle_min_accel
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import soften_far_radar_lead_accel
from openpilot.selfdrive.modeld.constants import ModelConstants, Plan


def make_lead(*, status: bool, d_rel: float = 200.0, v_lead: float = 0.0, a_lead: float = 0.0,
              radar: bool = False, model_prob: float = 0.0):
  lead = log.RadarState.LeadData.new_message()
  lead.status = status
  lead.dRel = d_rel
  lead.vLead = v_lead
  lead.vLeadK = v_lead
  lead.aLeadK = a_lead
  lead.vRel = 0.0
  lead.aRel = 0.0
  lead.modelProb = model_prob
  lead.radar = radar
  return lead


def make_model(v_ego: float, desired_accel: float, gas_press_prob: float = 1.0):
  model = log.ModelDataV2.new_message()
  t_idxs = ModelConstants.T_IDXS

  model.position.x = [float(v_ego * t) for t in t_idxs]
  model.position.y = [0.0] * len(t_idxs)
  model.position.z = [0.0] * len(t_idxs)
  model.position.t = [float(t) for t in t_idxs]

  model.velocity.x = [float(v_ego)] * len(t_idxs)
  model.velocity.y = [0.0] * len(t_idxs)
  model.velocity.z = [0.0] * len(t_idxs)
  model.velocity.t = [float(t) for t in t_idxs]

  model.acceleration.x = [0.0] * len(t_idxs)
  model.acceleration.y = [0.0] * len(t_idxs)
  model.acceleration.z = [0.0] * len(t_idxs)
  model.acceleration.t = [float(t) for t in t_idxs]

  model.meta.disengagePredictions.gasPressProbs = [float(gas_press_prob)] * 6
  model.action.desiredAcceleration = desired_accel
  model.action.shouldStop = False
  return model


def make_sm(v_ego: float, desired_accel: float, min_accel: float, *, experimental_mode: bool = True,
            tracking_lead: bool = False, lead_one=None, lead_two=None,
            gas_press_prob: float = 1.0, disable_throttle: bool = False):
  return {
    "carControl": SimpleNamespace(orientationNED=[0.0, 0.0, 0.0]),
    "carState": SimpleNamespace(
      vEgo=v_ego,
      vEgoCluster=v_ego,
      aEgo=0.0,
      vCruise=100.0,
      standstill=False,
      steeringAngleDeg=0.0,
    ),
    "controlsState": SimpleNamespace(
      longControlState=LongCtrlState.pid,
      forceDecel=False,
    ),
    "liveParameters": SimpleNamespace(angleOffsetDeg=0.0),
    "modelV2": make_model(v_ego, desired_accel, gas_press_prob=gas_press_prob),
    "radarState": SimpleNamespace(
      leadOne=lead_one if lead_one is not None else make_lead(status=False),
      leadTwo=lead_two if lead_two is not None else make_lead(status=False),
    ),
    "selfdriveState": SimpleNamespace(enabled=True, experimentalMode=experimental_mode, personality=0),
    "starpilotPlan": SimpleNamespace(
      vCruise=v_ego + 5.0,
      minAcceleration=min_accel,
      maxAcceleration=2.0,
      disableThrottle=disable_throttle,
      trackingLead=tracking_lead,
      accelerationJerk=5.0,
      dangerJerk=5.0,
      speedJerk=5.0,
      dangerFactor=1.0,
      tFollow=1.45,
      forcingStopLength=2,
    ),
  }


def make_toggles(model_version: str = "v11"):
  return SimpleNamespace(
    taco_tune=False,
    classic_model=False,
    tinygrad_model=True,
    model_version=model_version,
    stop_distance=6.0,
    vEgoStopping=0.5,
  )


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_experimental_mlsim_uses_vehicle_min_accel_floor(model_version):
  v_ego = 18.0
  desired_accel = -1.0
  comfort_min_accel = -0.5

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(v_ego, desired_accel, comfort_min_accel)

  vehicle_min_accel = get_vehicle_min_accel(CP, v_ego)
  assert vehicle_min_accel < comfort_min_accel

  planner.update(sm, make_toggles(model_version))

  assert planner.mode == "blended"
  assert planner.mlsim
  assert planner.output_a_target == pytest.approx(desired_accel, abs=1e-3)
  assert planner.output_a_target < comfort_min_accel


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_uses_close_raw_lead_when_tracking_lead_is_debounced(model_version):
  v_ego = 5.0

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=-0.6,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
    lead_one=make_lead(status=True, d_rel=24.0, v_lead=0.3),
  )
  sm["starpilotPlan"].vCruise = v_ego + 12.0

  planner.update(sm, make_toggles(model_version))

  assert planner.mode == "acc"
  assert planner.raw_close_lead_needs_control(sm["radarState"].leadOne, v_ego)
  assert planner.output_a_target == pytest.approx(
    planner.get_close_lead_brake_cap(sm["radarState"].leadOne, v_ego, sm["starpilotPlan"].minAcceleration)
  )


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_matches_no_lead_baseline_for_far_vision_only_lead_without_tracking(model_version):
  v_ego = 29.0

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_no_lead = LongitudinalPlanner(CP, init_v=v_ego)
  planner_far_vision = LongitudinalPlanner(CP, init_v=v_ego)
  sm_no_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
  )
  sm_far_vision = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
    lead_one=make_lead(status=True, d_rel=82.0, v_lead=25.0, radar=False, model_prob=0.9),
  )
  sm_no_lead["starpilotPlan"].vCruise = v_ego + 2.0
  sm_far_vision["starpilotPlan"].vCruise = v_ego + 2.0

  no_lead_outputs = []
  far_vision_outputs = []
  for _ in range(8):
    planner_no_lead.update(sm_no_lead, make_toggles(model_version))
    planner_far_vision.update(sm_far_vision, make_toggles(model_version))
    no_lead_outputs.append(planner_no_lead.output_a_target)
    far_vision_outputs.append(planner_far_vision.output_a_target)

  assert planner_far_vision.mode == "acc"
  assert not planner_far_vision.raw_close_lead_needs_control(sm_far_vision["radarState"].leadOne, v_ego)
  np.testing.assert_allclose(far_vision_outputs, no_lead_outputs, atol=1e-6)


def test_soften_far_radar_lead_accel_reduces_gentle_far_brake():
  softened = soften_far_radar_lead_accel(114.8, 28.88, -0.75, 29.26, 1.45, radar=True)
  assert softened > -0.35
  assert softened < 0.0


def test_soften_far_radar_lead_accel_keeps_close_closing_brake():
  baseline = -0.76
  softened = soften_far_radar_lead_accel(68.0, 26.38, baseline, 29.38, 1.45, radar=True)
  assert softened == pytest.approx(baseline)


def test_vision_lead_approach_cap_brakes_before_hard_cap():
  v_ego = 21.535
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  lead = make_lead(status=True, d_rel=38.9, v_lead=18.04, a_lead=-0.026, radar=False, model_prob=0.984)

  hard_cap = planner.get_close_lead_brake_cap(lead, v_ego, -1.0)
  approach_cap = planner.get_vision_lead_approach_cap(lead, v_ego, -1.0, 1.45)

  assert hard_cap == pytest.approx(-0.212, abs=1e-2)
  assert approach_cap is not None
  assert approach_cap < hard_cap
  assert approach_cap > -1.2


def test_vision_lead_approach_cap_brakes_harder_when_inside_tight_gap():
  v_ego = 26.18
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  lead = make_lead(status=True, d_rel=39.72, v_lead=22.46, a_lead=-0.15, radar=False, model_prob=0.97)

  approach_cap = planner.get_vision_lead_approach_cap(lead, v_ego, -1.0, 1.49)

  assert approach_cap is not None
  assert approach_cap < -0.5


def test_vision_lead_approach_cap_ignores_opening_lead_with_large_gap():
  v_ego = 19.37
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  lead = make_lead(status=True, d_rel=66.168, v_lead=20.751, a_lead=0.261, radar=False, model_prob=0.975)

  assert planner.get_vision_lead_approach_cap(lead, v_ego, -1.0, 1.45) is None


def test_vision_untracked_slow_lead_cap_triggers_only_for_meaningful_closing_case():
  route_v_ego = 23.23
  far_v_ego = 29.0

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=route_v_ego)
  route_like_lead = make_lead(status=True, d_rel=66.7, v_lead=18.49, a_lead=0.0, radar=False, model_prob=0.92)
  far_mild_lead = make_lead(status=True, d_rel=82.0, v_lead=25.0, a_lead=0.0, radar=False, model_prob=0.9)

  route_cap = planner.get_vision_untracked_slow_lead_cap(route_like_lead, route_v_ego, -1.0)
  far_cap = planner.get_vision_untracked_slow_lead_cap(far_mild_lead, far_v_ego, -1.0)

  assert route_cap is not None
  assert route_cap < -0.1
  assert far_cap is None


def test_vision_untracked_slow_lead_cap_reaches_high_confidence_far_slower_lead_before_raw_close_lead():
  v_ego = 21.48

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  route_like_lead = make_lead(status=True, d_rel=93.0, v_lead=12.84, a_lead=0.0, radar=False, model_prob=0.935)

  route_cap = planner.get_vision_untracked_slow_lead_cap(route_like_lead, v_ego, -1.0)

  assert route_cap is not None
  assert route_cap < -0.5
  assert not planner.raw_close_lead_needs_control(route_like_lead, v_ego)


def test_vision_untracked_slow_lead_cap_relaxes_confidence_for_near_stopped_high_closure_lead():
  v_ego = 20.35

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  route_like_lead = make_lead(status=True, d_rel=115.4, v_lead=3.76, a_lead=0.0, radar=False, model_prob=0.70)

  route_cap = planner.get_vision_untracked_slow_lead_cap(route_like_lead, v_ego, -1.0)

  assert route_cap is not None
  assert route_cap < -0.55


def test_vision_untracked_slow_lead_cap_keeps_low_confidence_floor_for_less_threatening_lead():
  v_ego = 20.35

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  less_threatening_lead = make_lead(status=True, d_rel=115.4, v_lead=9.5, a_lead=0.0, radar=False, model_prob=0.75)

  assert planner.get_vision_untracked_slow_lead_cap(less_threatening_lead, v_ego, -1.0) is None


def test_vision_slow_stopped_lead_cap_brakes_earlier_for_confident_stop():
  v_ego = 13.207
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  lead = make_lead(status=True, d_rel=49.131, v_lead=1.837, a_lead=-0.312, radar=False, model_prob=0.942)

  slow_stop_cap = planner.get_vision_slow_stopped_lead_cap(lead, v_ego, -1.0, 1.75)

  assert slow_stop_cap is not None
  assert slow_stop_cap < -0.9
  assert slow_stop_cap > -1.25


def test_vision_slow_stopped_lead_cap_ignores_far_high_speed_stop_candidate():
  v_ego = 33.5
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  lead = make_lead(status=True, d_rel=183.0, v_lead=0.0, a_lead=0.0, radar=False, model_prob=0.995)

  assert planner.get_vision_slow_stopped_lead_cap(lead, v_ego, -1.0, 1.45) is None


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_dynamic_t_follow_increases_modestly_for_closing_lead(model_version):
  v_ego = 21.535

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-3.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=38.9, v_lead=18.04, a_lead=-0.026, radar=False, model_prob=0.984),
  )
  sm["starpilotPlan"].vCruise = v_ego + 8.0

  for _ in range(8):
    planner.update(sm, make_toggles(model_version))

  assert planner.effective_t_follow is not None
  assert planner.effective_t_follow > sm["starpilotPlan"].tFollow + 0.15
  assert planner.effective_t_follow < sm["starpilotPlan"].tFollow + 0.45


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_dynamic_t_follow_stays_near_base_for_far_highway_lead(model_version):
  v_ego = 29.26

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=114.8, v_lead=28.88, a_lead=-0.75, radar=True, model_prob=0.9),
  )
  sm["starpilotPlan"].vCruise = v_ego + 3.0

  for _ in range(12):
    planner.update(sm, make_toggles(model_version))

  assert planner.effective_t_follow == pytest.approx(sm["starpilotPlan"].tFollow, abs=0.02)


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_dynamic_t_follow_releases_toward_base_after_lead_opens(model_version):
  v_ego = 21.535

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-3.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=38.9, v_lead=18.04, a_lead=-0.026, radar=False, model_prob=0.984),
  )

  for _ in range(8):
    planner.update(sm, make_toggles(model_version))

  boosted_t_follow = planner.effective_t_follow
  sm["radarState"].leadOne = make_lead(status=True, d_rel=66.168, v_lead=20.751, a_lead=0.261, radar=False, model_prob=0.975)
  for _ in range(12):
    planner.update(sm, make_toggles(model_version))

  assert boosted_t_follow is not None
  assert planner.effective_t_follow < boosted_t_follow
  assert planner.effective_t_follow == pytest.approx(sm["starpilotPlan"].tFollow, abs=0.02)


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_vision_lead_approach_cap_smooths_before_close_brake(model_version):
  approach_v_ego = 21.535
  close_v_ego = 21.435

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_approach = LongitudinalPlanner(CP, init_v=approach_v_ego)
  planner_close = LongitudinalPlanner(CP, init_v=close_v_ego)

  sm_approach = make_sm(
    approach_v_ego,
    desired_accel=0.2,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=38.9, v_lead=18.04, a_lead=-0.026, radar=False, model_prob=0.984),
  )
  sm_close = make_sm(
    close_v_ego,
    desired_accel=0.2,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=27.18, v_lead=15.76, a_lead=-0.824, radar=False, model_prob=0.988),
  )
  sm_approach["starpilotPlan"].vCruise = approach_v_ego + 8.0
  sm_close["starpilotPlan"].vCruise = close_v_ego + 8.0

  planner_approach.update(sm_approach, make_toggles(model_version))
  planner_close.update(sm_close, make_toggles(model_version))

  assert planner_approach.mode == "acc"
  assert planner_close.mode == "acc"
  assert planner_approach.output_a_target < -0.6
  assert planner_close.output_a_target < planner_approach.output_a_target - 0.25


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_pretracking_vision_slow_lead_blocks_positive_catchup(model_version):
  v_ego = 23.23

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_no_lead = LongitudinalPlanner(CP, init_v=v_ego)
  planner_with_lead = LongitudinalPlanner(CP, init_v=v_ego)
  sm_no_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=False,
  )
  sm_with_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=False,
    lead_one=make_lead(status=True, d_rel=66.7, v_lead=18.49, a_lead=0.0, radar=False, model_prob=0.92),
  )
  sm_no_lead["starpilotPlan"].vCruise = v_ego + 6.0
  sm_with_lead["starpilotPlan"].vCruise = v_ego + 6.0

  for _ in range(6):
    planner_no_lead.update(sm_no_lead, make_toggles(model_version))
    planner_with_lead.update(sm_with_lead, make_toggles(model_version))

  assert planner_with_lead.mode == "acc"
  assert not planner_with_lead.raw_close_lead_needs_control(sm_with_lead["radarState"].leadOne, v_ego)
  assert planner_with_lead.output_a_target <= planner_no_lead.output_a_target - 0.04
  assert planner_with_lead.output_a_target < -0.2


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_pretracking_vision_far_slower_lead_starts_braking_before_tracking(model_version):
  v_ego = 21.48

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_no_lead = LongitudinalPlanner(CP, init_v=v_ego)
  planner_with_lead = LongitudinalPlanner(CP, init_v=v_ego)
  sm_no_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
  )
  sm_with_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
    lead_one=make_lead(status=True, d_rel=93.0, v_lead=12.84, a_lead=0.0, radar=False, model_prob=0.935),
  )
  sm_no_lead["starpilotPlan"].vCruise = v_ego + 6.0
  sm_with_lead["starpilotPlan"].vCruise = v_ego + 6.0

  no_lead_outputs = []
  lead_outputs = []
  for _ in range(8):
    planner_no_lead.update(sm_no_lead, make_toggles(model_version))
    planner_with_lead.update(sm_with_lead, make_toggles(model_version))
    no_lead_outputs.append(planner_no_lead.output_a_target)
    lead_outputs.append(planner_with_lead.output_a_target)

  assert planner_with_lead.mode == "acc"
  assert not planner_with_lead.raw_close_lead_needs_control(sm_with_lead["radarState"].leadOne, v_ego)
  assert all(lead_output <= no_lead_output + 1e-6
             for lead_output, no_lead_output in zip(lead_outputs[5:], no_lead_outputs[5:]))
  assert min(lead_outputs[5:]) < min(no_lead_outputs[5:]) - 0.08
  assert lead_outputs[-1] < no_lead_outputs[-1] - 0.15


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_pretracking_near_stopped_vision_lead_does_not_relax_when_confidence_is_midrange(model_version):
  v_ego = 20.35

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_no_lead = LongitudinalPlanner(CP, init_v=v_ego)
  planner_with_lead = LongitudinalPlanner(CP, init_v=v_ego)
  sm_no_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
  )
  sm_with_lead = make_sm(
    v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
    lead_one=make_lead(status=True, d_rel=115.4, v_lead=3.76, a_lead=0.0, radar=False, model_prob=0.70),
  )
  sm_no_lead["starpilotPlan"].vCruise = v_ego + 6.0
  sm_with_lead["starpilotPlan"].vCruise = v_ego + 6.0

  for _ in range(8):
    planner_no_lead.update(sm_no_lead, make_toggles(model_version))
    planner_with_lead.update(sm_with_lead, make_toggles(model_version))

  assert planner_with_lead.mode == "acc"
  assert planner_with_lead.output_a_target < planner_no_lead.output_a_target - 0.12
  assert planner_with_lead.output_a_target < -0.45


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_tracked_pace_matched_lead_caps_positive_catchup(model_version):
  v_ego = 28.7

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_no_lead = LongitudinalPlanner(CP, init_v=v_ego)
  planner_with_lead = LongitudinalPlanner(CP, init_v=v_ego)
  sm_no_lead = make_sm(
    v_ego,
    desired_accel=0.5,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=False,
  )
  sm_with_lead = make_sm(
    v_ego,
    desired_accel=0.5,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=22.0, v_lead=29.4, a_lead=0.0, radar=False, model_prob=0.995),
  )
  sm_no_lead["starpilotPlan"].vCruise = v_ego + 4.0
  sm_with_lead["starpilotPlan"].vCruise = v_ego + 4.0

  for _ in range(8):
    planner_no_lead.update(sm_no_lead, make_toggles(model_version))
    planner_with_lead.update(sm_with_lead, make_toggles(model_version))

  assert planner_with_lead.mode == "acc"
  assert planner_with_lead.output_a_target <= planner_no_lead.output_a_target - 0.15
  assert planner_with_lead.output_a_target < 0.08


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_low_speed_vision_stop_buffer_sets_should_stop_before_tiny_gap(model_version):
  v_ego = 3.8

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=0.1,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=5.75, v_lead=0.58, a_lead=-0.1, radar=False, model_prob=0.99),
  )
  sm["starpilotPlan"].vCruise = v_ego + 4.0

  planner.update(sm, make_toggles(model_version))

  assert planner.mode == "acc"
  assert planner.output_should_stop
  assert planner.output_a_target < -1.0


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_standstill_moving_lead_does_not_force_resume_while_should_stop(model_version):
  v_ego = 0.0

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(
    v_ego,
    desired_accel=0.0,
    min_accel=-0.5,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=7.1, v_lead=2.3, a_lead=1.8, radar=True, model_prob=1.0),
  )
  sm["carState"].standstill = True
  sm["controlsState"].longControlState = LongCtrlState.stopping
  sm["starpilotPlan"].vCruise = 10.0

  planner.update(sm, make_toggles(model_version))

  assert planner.output_should_stop
  assert planner.output_a_target < 0.1


@pytest.mark.parametrize("model_version", ["v11", "v12", "v13", "v14"])
def test_acc_mode_damps_far_radar_mild_lead_brake_more_than_close_brake(model_version):
  far_v_ego = 29.26
  far_v_cruise = 32.22
  close_v_ego = 29.38
  close_v_cruise = 32.22

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner_far = LongitudinalPlanner(CP, init_v=far_v_ego)
  planner_close = LongitudinalPlanner(CP, init_v=close_v_ego)

  sm_far = make_sm(
    far_v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=114.8, v_lead=28.88, a_lead=-0.75, radar=True, model_prob=0.9),
  )
  sm_close = make_sm(
    close_v_ego,
    desired_accel=0.2,
    min_accel=-1.0,
    experimental_mode=False,
    tracking_lead=True,
    lead_one=make_lead(status=True, d_rel=68.0, v_lead=26.38, a_lead=-0.76, radar=True, model_prob=0.9),
  )
  sm_far["starpilotPlan"].vCruise = far_v_cruise
  sm_close["starpilotPlan"].vCruise = close_v_cruise

  for _ in range(80):
    planner_far.update(sm_far, make_toggles(model_version))
    planner_close.update(sm_close, make_toggles(model_version))

  assert planner_far.mode == "acc"
  assert planner_close.mode == "acc"
  assert planner_far.output_a_target > -0.4
  assert planner_close.output_a_target < planner_far.output_a_target - 0.1


def test_modeld_action_passes_tomb_raider_longitudinal_params(monkeypatch):
  monkeypatch.setenv("DEBUG", "0")
  fake_commonmodel = types.ModuleType("openpilot.selfdrive.modeld.models.commonmodel_pyx")
  fake_commonmodel.DrivingModelFrame = object
  fake_commonmodel.CLContext = object
  monkeypatch.setitem(sys.modules, fake_commonmodel.__name__, fake_commonmodel)

  from openpilot.selfdrive.modeld import modeld

  captured = {}

  def fake_get_accel_from_plan(speeds, accels, t_idxs, *, action_t, vEgoStopping):
    captured["speeds"] = speeds
    captured["accels"] = accels
    captured["t_idxs"] = t_idxs
    captured["action_t"] = action_t
    captured["vEgoStopping"] = vEgoStopping
    return 0.4, True

  monkeypatch.setattr(modeld, "get_accel_from_plan_tomb_raider", fake_get_accel_from_plan)

  plan = np.zeros((1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH), dtype=np.float32)
  plan[0, :, Plan.VELOCITY] = 3.0
  plan[0, :, Plan.ACCELERATION] = -0.1
  prev_action = log.ModelDataV2.Action.new_message()
  toggles = SimpleNamespace(vEgoStopping=0.42)

  action = modeld.get_action_from_model(
    {"plan": plan},
    prev_action,
    lat_action_t=0.2,
    long_action_t=0.73,
    v_ego=5.0,
    mlsim=True,
    is_v9=True,
    is_v14=False,
    starpilot_toggles=toggles,
  )

  assert captured["action_t"] == pytest.approx(0.73)
  assert captured["vEgoStopping"] == pytest.approx(0.42)
  assert list(captured["t_idxs"]) == ModelConstants.T_IDXS
  np.testing.assert_allclose(captured["speeds"], 3.0)
  np.testing.assert_allclose(captured["accels"], -0.1)
  assert action.shouldStop


def test_modeld_action_uses_direct_action_head_for_v14(monkeypatch):
  monkeypatch.setenv("DEBUG", "0")
  fake_commonmodel = types.ModuleType("openpilot.selfdrive.modeld.models.commonmodel_pyx")
  fake_commonmodel.DrivingModelFrame = object
  fake_commonmodel.CLContext = object
  monkeypatch.setitem(sys.modules, fake_commonmodel.__name__, fake_commonmodel)

  from openpilot.selfdrive.modeld import modeld

  prev_action = log.ModelDataV2.Action.new_message()
  prev_action.desiredCurvature = 0.05
  prev_action.desiredAcceleration = -0.2
  toggles = SimpleNamespace(vEgoStopping=0.42)

  action = modeld.get_action_from_model(
    {"action": np.array([[12.0, -0.8]], dtype=np.float32)},
    prev_action,
    lat_action_t=0.2,
    long_action_t=0.73,
    v_ego=5.0,
    mlsim=True,
    is_v9=False,
    is_v14=True,
    starpilot_toggles=toggles,
  )

  assert action.desiredCurvature == pytest.approx(0.12)
  assert action.desiredAcceleration < -0.2
  assert not action.shouldStop


def test_allow_throttle_hysteresis_filters_gas_prob_chatter():
  v_ego = 10.0

  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  planner = LongitudinalPlanner(CP, init_v=v_ego)
  sm = make_sm(v_ego, desired_accel=0.0, min_accel=-1.0, experimental_mode=False, gas_press_prob=0.5)
  toggles = make_toggles()

  planner.update(sm, toggles)
  assert planner.model_allow_throttle
  assert planner.allow_throttle

  sm["modelV2"] = make_model(v_ego, desired_accel=0.0, gas_press_prob=0.37)
  planner.update(sm, toggles)
  assert planner.model_allow_throttle
  assert planner.allow_throttle

  sm["modelV2"] = make_model(v_ego, desired_accel=0.0, gas_press_prob=0.34)
  planner.update(sm, toggles)
  assert not planner.model_allow_throttle
  assert not planner.allow_throttle

  sm["modelV2"] = make_model(v_ego, desired_accel=0.0, gas_press_prob=0.43)
  planner.update(sm, toggles)
  assert not planner.model_allow_throttle
  assert not planner.allow_throttle

  sm["modelV2"] = make_model(v_ego, desired_accel=0.0, gas_press_prob=0.46)
  planner.update(sm, toggles)
  assert planner.model_allow_throttle
  assert planner.allow_throttle
