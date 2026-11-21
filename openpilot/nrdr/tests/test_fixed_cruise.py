"""Fixed Civic PCM target ownership; no CAN, Params or native solver I/O.

Run actual cruise/planner source definitions with the existing host doubles.
These tests do not establish native optimizer or vehicle stopping performance.
"""
import ast
from itertools import product
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.common.constants import CV
from openpilot.nrdr.tests.test_mvl_cruise import Button, DEFAULTS, MVL_FLAG, SLA, module, namespace, state
from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, Messages, PlannerMpcDouble, PlannerSPDouble, definitions, environment, source,
)

FIXED_FLAG = 262144
LEGACY_FLAG = 524288
MAX_KPH = 90. * CV.MPH_TO_MS * CV.MS_TO_KPH


def make_helper(*, fixed=True, legacy=False, mvl=False, pcm=True, pcm_speed=False, cp_changes=None, sp_changes=None, values=None):
  flags = 16 | (FIXED_FLAG if fixed else 0) | (LEGACY_FLAG if legacy else 0) | (MVL_FLAG if mvl else 0)
  cp = NS(**({"flags": flags, "brand": "honda", "carFingerprint": "HONDA_CIVIC", "pcmCruise": pcm,
              "openpilotLongitudinalControl": True, "passive": False, "dashcamOnly": False} | (cp_changes or {})))
  sp = NS(**({"flags": 0, "enableGasInterceptor": False, "pcmCruiseSpeed": pcm_speed} | (sp_changes or {})))
  current, _ = module(values=values)
  return current["VCruiseHelper"](cp, sp)


@pytest.fixture(params=list(product((False, True), repeat=3)), ids=lambda p: f"mvl={p[0]}-legacy={p[1]}-pcm_speed={p[2]}")
def fixed_helper(request):
  mvl, legacy, pcm_speed = request.param
  return make_helper(mvl=mvl, legacy=legacy, pcm_speed=pcm_speed)


def engage(helper, speed=10., metric=True, experimental=False, button=Button.decelCruise):
  # card updates before initialize, passing the previous frame's button event.
  previous = state(speed, button=button, pcm_speed=90. * CV.MPH_TO_MS)
  helper.update_v_cruise(previous, False, metric)
  current = state(speed, pcm_speed=90. * CV.MPH_TO_MS)
  helper.update_v_cruise(current, True, metric)
  helper.initialize_v_cruise(previous, experimental)
  helper.update_v_cruise(current, True, metric)


def tap(helper, button, *, metric=True, enabled=True, **kwargs):
  for pressed in (True, False):
    helper.update_v_cruise(state(button=button, pressed=pressed, **kwargs), enabled, metric)


def test_test_helper_masks_match_production_enums():
  env, _ = namespace()
  for path, cls in (("opendbc_repo/opendbc/car/honda/values.py", "HondaFlags"),
                    ("opendbc_repo/opendbc/sunnypilot/car/honda/values_ext.py", "HondaFlagsSP")):
    tree = ast.parse(source(path))
    enum = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    actual = {n.targets[0].id: ast.literal_eval(n.value) for n in enum.body if isinstance(n, ast.Assign)}
    for name, value in vars(env[cls]).items():
      assert actual[name] == value


@pytest.mark.parametrize("fixed,legacy,mvl", list(product((False, True), repeat=3)))
def test_all_flag_combinations_own_only_fixed_targets(fixed, legacy, mvl):
  helper = make_helper(fixed=fixed, legacy=legacy, mvl=mvl, pcm_speed=True)
  assert helper.fixed_cruise_enabled is fixed
  engage(helper, 0.)
  assert helper.v_cruise_kph == (0. if fixed else MAX_KPH)
  assert helper.CP.pcmCruise is True  # no change to CAN engagement/disengagement semantics
  assert helper.v_cruise_max == (MAX_KPH if fixed else 145 if mvl else 169)


@pytest.mark.parametrize("cp_changes,sp_changes", [
  ({"carFingerprint": "HONDA_CIVIC_BOSCH"}, {}), ({"carFingerprint": "HONDA_CLARITY"}, {}),
  ({"carFingerprint": "LEXUS_ES_TSS2", "brand": "toyota"}, {}),
  ({"flags": FIXED_FLAG}, {}), ({"flags": FIXED_FLAG | 16 | 4}, {}),
  ({"openpilotLongitudinalControl": False}, {}), ({"passive": True}, {}), ({"dashcamOnly": True}, {}),
  ({}, {"enableGasInterceptor": True}), ({}, {"flags": 16}),
])
def test_unqualified_stale_flag_cannot_take_ownership(cp_changes, sp_changes):
  helper = make_helper(pcm_speed=True, cp_changes=cp_changes, sp_changes=sp_changes)
  assert not helper.fixed_cruise_enabled
  engage(helper, 0.)
  assert helper.v_cruise_kph == MAX_KPH


@pytest.mark.parametrize("metric,experimental,speed", list(product((False, True), (False, True), (0., .01, 7.3, 45., 60.))))
def test_set_initializes_current_speed_including_zero(fixed_helper, metric, experimental, speed):
  engage(fixed_helper, speed, metric, experimental)
  expected = speed * CV.MS_TO_KPH
  if not metric and not fixed_helper.mvl_enabled:
    expected = (round(expected * .6233 + .0995) - .0995) / .6233
  expected = np.clip(round(expected, 1), 0., MAX_KPH)
  assert fixed_helper.v_cruise_kph == fixed_helper.v_cruise_cluster_kph == expected
  assert fixed_helper.v_cruise_initialized
  assert fixed_helper.v_cruise_min == 0


@pytest.mark.parametrize("metric", (False, True))
def test_no_initial_target_is_invented_from_stock_readback(fixed_helper, metric):
  for enabled, available, stock in product((False, True), (False, True), (-1., 0., 90. * CV.MPH_TO_MS)):
    fixed_helper.update_v_cruise(state(0., available=available, pcm_speed=stock), enabled, metric)
    assert fixed_helper.v_cruise_kph == fixed_helper.v_cruise_cluster_kph == 255
    assert not fixed_helper.v_cruise_initialized
  engage(fixed_helper, 0., metric, button=Button.accelCruise)
  assert fixed_helper.v_cruise_kph == 0.


@pytest.mark.parametrize("speed,button", list(product((0., 13.), (Button.accelCruise, Button.resumeCruise))))
def test_resume_remembers_internal_target_across_disengage_main_off_and_units(fixed_helper, speed, button):
  engage(fixed_helper, speed)
  remembered = fixed_helper.v_cruise_kph
  for metric, available, stock in product((False, True), (False, True), (0., -1., 90. * CV.MPH_TO_MS)):
    for _ in range(3):
      fixed_helper.update_v_cruise(state(30., available=available, pcm_speed=stock), False, metric)
    assert fixed_helper.fixed_cruise_kph == remembered
    assert fixed_helper.v_cruise_kph == (remembered if available else 255)
  engage(fixed_helper, 30., False, button=button)
  assert fixed_helper.v_cruise_kph == fixed_helper.v_cruise_cluster_kph == remembered
  engage(fixed_helper, 0., button=Button.decelCruise)
  assert fixed_helper.v_cruise_kph == 0.  # SET is current speed, not the remembered RES speed.


@pytest.mark.parametrize("button", (Button.accelCruise, Button.resumeCruise, Button.decelCruise, Button.setCruise))
def test_delayed_pcm_engagement_keeps_set_or_resume_intent(fixed_helper, button):
  engage(fixed_helper, 0.)
  tap(fixed_helper, button, enabled=False, speed=20.)
  for _ in range(12):
    fixed_helper.update_v_cruise(state(20.), False, True)
  fixed_helper.update_v_cruise(state(20.), True, True)
  fixed_helper.initialize_v_cruise(state(20.), False)
  expected = 0. if button in (Button.accelCruise, Button.resumeCruise) else 72.
  assert fixed_helper.v_cruise_kph == expected
  assert fixed_helper.fixed_cruise_button is None


@pytest.mark.parametrize("reset", ("cancel", "main", "unavailable"))
def test_cancel_or_main_off_clears_pending_resume_intent(fixed_helper, reset):
  engage(fixed_helper, 0.)
  tap(fixed_helper, Button.accelCruise, enabled=False)
  button = {"cancel": Button.cancel, "main": Button.mainCruise, "unavailable": None}[reset]
  fixed_helper.update_v_cruise(state(button=button, available=reset != "unavailable"), False, True)
  assert fixed_helper.fixed_cruise_button is None
  assert fixed_helper.fixed_cruise_kph == 0.


@pytest.mark.parametrize("metric", (False, True))
def test_short_and_long_decrement_reach_zero_without_donor_floor(fixed_helper, metric):
  engage(fixed_helper, 2., metric)
  for _ in range(15):
    tap(fixed_helper, Button.decelCruise, metric=metric, standstill=True)
  assert fixed_helper.v_cruise_kph == 0.
  engage(fixed_helper, 25., metric)
  for frame in range(1000):
    fixed_helper.update_v_cruise(state(button=Button.decelCruise if frame == 0 else None,
                                      pressed=True, standstill=True), True, metric)
    assert 0 <= fixed_helper.v_cruise_kph <= MAX_KPH
  assert fixed_helper.v_cruise_kph == 0.


@pytest.mark.parametrize("metric", (False, True))
def test_ceiling_for_buttons_gas_override_and_speed_limit_assist(fixed_helper, metric):
  engage(fixed_helper, 80., metric)
  assert fixed_helper.v_cruise_kph == MAX_KPH
  for _ in range(10):
    tap(fixed_helper, Button.accelCruise, metric=metric)
    assert fixed_helper.v_cruise_kph <= MAX_KPH
  tap(fixed_helper, Button.decelCruise, metric=metric, gas=True, speed=80.)
  assert fixed_helper.v_cruise_kph == MAX_KPH
  fixed_helper.sla_state = SLA.active
  fixed_helper.speed_limit_final_last_kph = 200.
  fixed_helper.update_v_cruise(state(), True, metric)
  assert fixed_helper.v_cruise_kph == MAX_KPH


def test_existing_disengage_standstill_and_midpress_guards(fixed_helper):
  engage(fixed_helper)
  remembered = fixed_helper.v_cruise_kph
  for button in (Button.accelCruise, Button.decelCruise, Button.cancel):
    tap(fixed_helper, button, enabled=False)
    assert fixed_helper.v_cruise_kph == remembered
  fixed_helper.update_v_cruise(state(), True, True)
  fixed_helper.update_v_cruise(state(), True, True)
  fixed_helper.update_v_cruise(state(button=Button.accelCruise, pressed=True, standstill=True), True, True)
  fixed_helper.update_v_cruise(state(button=Button.accelCruise, pressed=False, standstill=False), True, True)
  assert fixed_helper.v_cruise_kph == remembered
  fixed_helper.update_v_cruise(state(button=Button.decelCruise, pressed=True), False, True)
  fixed_helper.update_v_cruise(state(button=Button.decelCruise, pressed=False), True, True)
  assert fixed_helper.v_cruise_kph == remembered


@pytest.mark.parametrize("metric", (False, True))
def test_gas_override_still_floors_set_at_current_speed(fixed_helper, metric):
  engage(fixed_helper, 0., metric)
  tap(fixed_helper, Button.decelCruise, metric=metric, gas=True, speed=20.)
  assert fixed_helper.v_cruise_kph == pytest.approx(72., abs=.8)  # Honda imperial display quantization


@pytest.mark.parametrize("mvl,pcm,pcm_speed,metric", list(product((False, True), repeat=4)))
def test_legacy_bit_alone_has_no_cruise_target_effect(mvl, pcm, pcm_speed, metric):
  helpers = [make_helper(fixed=False, legacy=legacy, mvl=mvl, pcm=pcm, pcm_speed=pcm_speed) for legacy in (False, True)]
  for helper in helpers:
    engage(helper, 12., metric)
  for frame in range(220):
    cs = state(button=Button.accelCruise if frame in (10, 12, 40, 95) else None,
               pressed=frame in (10, 40), available=frame % 70 != 0, gas=frame % 7 == 0,
               standstill=50 < frame < 60, pcm_speed=0. if frame % 15 == 0 else 35.)
    for helper in helpers:
      helper.update_v_cruise(cs, frame % 60 > 5, metric)
    for attr in ("v_cruise_kph", "v_cruise_cluster_kph", "v_cruise_kph_last", "v_cruise_min",
                 "button_timers", "button_change_states", "enabled_prev"):
      assert getattr(helpers[0], attr) == getattr(helpers[1], attr)


@pytest.mark.parametrize("increment", (1, 5, 10))
def test_fixed_custom_increment_policy_stays_bounded(increment):
  helper = make_helper(values=DEFAULTS | {"CustomAccIncrementsEnabled": True,
                                         "CustomAccShortPressIncrement": increment})
  engage(helper, 0.)
  tap(helper, Button.accelCruise)
  assert helper.v_cruise_kph == increment
  tap(helper, Button.decelCruise)
  assert helper.v_cruise_kph == 0.


def planner_for(helper, stopping_threshold=.5):
  env = environment(LongitudinalMpc=PlannerMpcDouble, LongitudinalPlannerSP=PlannerSPDouble,
                    T_IDXS_MPC=np.linspace(0., 10., 13), V_CRUISE_MAX=169)
  drive = definitions(source(CORE + "drive_helpers.py"), env)
  env.update({key: drive[key] for key in ("get_accel_from_plan", "should_stop")})
  nrdr = definitions(source("openpilot/nrdr/features/longitudinal/longitudinal_planner.py"), env)["NrdrLongitudinalPlanner"]
  policy = nrdr.__new__(nrdr)
  policy.cruise_scale = 1.05  # correction must leave exact zero unchanged
  policy.v_ego_stopping = stopping_threshold
  policy.refresh = lambda: None
  policy.max_accel = lambda _: 2.
  policy.turn_accel_threshold = lambda: 0.
  policy.stopped_gap = lambda _: 0.
  policy.launch_accel = lambda _sm, _t, _action_t, _v, _stop, accel, _e2e: accel
  env["NrdrLongitudinalPlanner"] = lambda *_: policy
  env["AccelBoost"] = definitions(source(MPC + "mvl_accel_boost.py"), env)["AccelBoost"]
  env["MvlLongitudinalPlanner"] = definitions(source(MPC + "mvl_planner.py"), env)["MvlLongitudinalPlanner"]
  cls = definitions(source(CORE + "longitudinal_planner.py"), env)["LongitudinalPlanner"]
  helper.CP.longitudinalActuatorDelay = .3
  helper.CP.steerRatio, helper.CP.wheelbase = 15., 2.7
  return cls(helper.CP, helper.CP_SP)


def planner_messages(target, speed=0., experimental=False):
  return Messages(carState=NS(vEgo=speed, aEgo=0., vCruise=target, standstill=speed == 0.,
                             steeringAngleDeg=0., gasPressed=False),
                  carControl=NS(orientationNED=[]), vehicleParameters=NS(angleOffsetDeg=0.),
                  controlsState=NS(forceDecel=False, longControlState=1),
                  selfdriveState=NS(enabled=True, personality=1, experimentalMode=experimental),
                  radarState=NS(accel=1., crash_cnt=0),
                  modelV2=NS(action=NS(desiredAcceleration=1., shouldStop=False),
                             meta=NS(disengagePredictions=NS(gasPressProbs=[1., 1.]))))


@pytest.mark.parametrize("mvl,legacy,experimental", list(product((False, True), repeat=3)))
@pytest.mark.parametrize("speed", (0., .1, 10.))
def test_zero_target_drives_modern_planner_decel_then_stop(mvl, legacy, experimental, speed):
  helper = make_helper(mvl=mvl, legacy=legacy)
  engage(helper, 1.)
  for _ in range(4):
    tap(helper, Button.decelCruise)
  assert helper.v_cruise_kph == 0.
  planner = planner_for(helper)
  sm = planner_messages(helper.v_cruise_kph, speed, experimental)
  for _ in range(40):
    planner.update(sm)
  assert planner.seen_cruise_target == 0.
  assert planner.output_a_target <= 0.
  assert planner.output_should_stop == (speed < .3)
  if speed > .3:
    assert planner.output_a_target < 0.


def test_zero_stopping_threshold_requires_separate_planner_policy_decision():
  # Document the existing out-of-scope edge case: NRDR accepts a saved zero
  # threshold, but both stop tests use strict < and cannot trigger at vEgo=0.
  planner = planner_for(make_helper(), stopping_threshold=0.)
  planner.update(planner_messages(0.))
  assert planner.seen_cruise_target == planner.output_a_target == 0.
  assert not planner.output_should_stop
