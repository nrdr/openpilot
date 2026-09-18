"""Offline parity against the frozen pre-NRDR MVL baseline.

Execute the actual source definitions with native I/O/solver boundaries replaced
by deterministic doubles. This runs on Windows too; it does NOT validate the
native solver, messaging, device startup, or vehicle behavior.
"""
import ast
import copy
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Literal
from collections.abc import Callable

import numpy as np
import pytest

from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.modeld.constants import ModelConstants, index_function
from openpilot.nrdr.features.driver_policy.dec import enforce_mode_dwell, slow_down_threshold
from openpilot.nrdr.features.longitudinal import policy
from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures" / "longitudinal_baseline"
CORE = "openpilot/selfdrive/controls/lib/"
SUNNY = "openpilot/sunnypilot/selfdrive/controls/lib/"
PERSONALITY = NS(aggressive=0, standard=1, relaxed=2, econ=3,
                 schema=NS(enumerants={"aggressive": 0, "standard": 1, "relaxed": 2, "econ": 3}))
STATE = NS(off=0, pid=1, stopping=2, starting=3)
SOURCE = NS(cruise=0, lead0=1, lead1=2, e2e=3)


def forbidden(*_args, **_kwargs):
  raise AssertionError("Baseline path accessed NRDR tuning")


def definitions(path, env):
  """Retain source definitions verbatim, excluding platform-dependent imports."""
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  tree.body = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
  namespace = dict(env, __file__=str(path))
  exec(compile(tree, str(path), "exec"), namespace)
  return namespace


def environment(**overrides):
  env = {
    "np": np, "math": math, "os": os, "DT_CTRL": 0.01, "DT_MDL": 0.05, "CONTROL_N": 17,
    "ACCEL_MIN": -3.5, "ACCEL_MAX": 2.0, "CV": CV, "PIDController": PIDController,
    "ModelConstants": ModelConstants, "FirstOrderFilter": FirstOrderFilter,
    "LongCtrlState": STATE, "LongitudinalPlanSource": SOURCE, "index_function": index_function,
    "car": NS(CarControl=NS(Actuators=NS(LongControlState=STATE)), CarState=NS(ButtonEvent=NS(Type=NS(gapAdjustCruise=1)))),
    "log": NS(LongitudinalPersonality=PERSONALITY, LongitudinalPlan=NS(LongitudinalPlanSource=SOURCE)),
    "cloudlog": NS(info=lambda *_: None, warning=lambda *_: None),
    "messaging": NS(SubMaster=object, PubMaster=object), "structs": NS(CarParams=object, CarParamsSP=object),
    "time": NS(monotonic=lambda: 100.0), "Literal": Literal, "interp": np.interp,
    "WMACConstants": WMACConstants, "enforce_mode_dwell": enforce_mode_dwell, "slow_down_threshold": slow_down_threshold,
    "nrdr_longitudinal_enabled": policy.nrdr_longitudinal_enabled,
    "longitudinal_personality": policy.longitudinal_personality,
    "NrdrLongControl": forbidden, "NrdrLongitudinalPlanner": forbidden, "NrdrLongitudinalMpc": forbidden,
    "is_honda_bosch_a_radar": lambda _: False, "_LEAD_ACCEL_TAU": 1.5,
    "V_CRUISE_MAX": 145, "V_CRUISE_UNSET": 255,
  }
  env.update(overrides)
  return env


def pair(relative, env):
  return (definitions(ROOT / relative, env), definitions(FIXTURES / (Path(relative).name + ".txt"), env))


def cp(brand="toyota"):
  return NS(brand=brand, carFingerprint="LEXUS_ES_TSS2", openpilotLongitudinalControl=True,
            stopAccel=-0.5, steerRatio=15.0, wheelbase=2.87, longitudinalActuatorDelay=0.3, radarUnavailable=False,
            longitudinalTuning=NS(kiBP=[0., 10., 30.], kiV=[1.2, 0.8, 0.5]))


@pytest.mark.parametrize("brand", ["toyota", "lexus", "hyundai", "ford", "gm", "subaru", "tesla", "", "unknown"])
def test_non_honda_fails_closed(brand):
  car_params = cp(brand)
  # Neither a stale Honda fingerprint nor old Honda settings can enable a car.
  car_params.carFingerprint = "HONDA_CIVIC"
  assert not policy.nrdr_longitudinal_enabled(car_params)
  assert not policy.nrdr_longitudinal_enabled(None)
  assert not policy.TUNED_NON_HONDA_CARS


def test_explicit_exception_requires_exact_brand_and_fingerprint(monkeypatch):
  monkeypatch.setattr(policy, "TUNED_NON_HONDA_CARS", frozenset({("test_brand", "TEST_PROFILE")}))
  assert policy.nrdr_longitudinal_enabled(NS(brand="test_brand", carFingerprint="TEST_PROFILE"))
  assert not policy.nrdr_longitudinal_enabled(NS(brand="toyota", carFingerprint="TEST_PROFILE"))
  assert not policy.nrdr_longitudinal_enabled(NS(brand="test_brand", carFingerprint="ANOTHER_CAR"))
  assert policy.nrdr_longitudinal_enabled(cp("honda"))


@pytest.mark.parametrize("value,expected", [(0, 0), (1, 1), (2, 2), (3, 2), (-1, 1), (9, 1), (None, 1), (True, 1)])
def test_personality_domain(value, expected):
  assert policy.longitudinal_personality(value, False) == expected
  assert policy.longitudinal_personality(NS(raw=value), False) == expected
  assert policy.longitudinal_personality(3, True) == 3


@pytest.mark.parametrize("brand", ["toyota", "hyundai", "subaru", "gm", "unknown"])
@pytest.mark.parametrize("gas_interceptor", [False, True])
def test_controller_matches_baseline_through_stop_recovery_and_disengage(brand, gas_interceptor):
  current, baseline = pair(CORE + "longcontrol.py", environment())
  CP, SP = cp(brand), NS(enableGasInterceptor=gas_interceptor)
  actual, expected = (module["LongControl"](CP, SP) for module in (current, baseline))
  assert actual.nrdr_controller is None
  rng = np.random.default_rng(350)
  for frame in range(600):
    stopping = 120 <= frame < 300
    CS = NS(aEgo=float(rng.uniform(-2, 1)), vEgo=0.1 if stopping else float(rng.uniform(0, 35)),
            brakePressed=frame % 61 == 0, cruiseState=NS(standstill=240 <= frame < 330))
    args = (frame % 100 > 5, CS, float(rng.uniform(-4, 3)), stopping, (-3.5, 2.0))
    assert actual.update(*args, pitch=0.4, drel=1.0, personality=3) == expected.update(*args)
    assert actual.long_control_state == expected.long_control_state
    assert actual.pid.i == expected.pid.i


def test_honda_controller_is_still_selected():
  sentinel = NS(pid=object())
  module = definitions(ROOT / (CORE + "longcontrol.py"), environment(NrdrLongControl=lambda *_: sentinel))
  controller = module["LongControl"](cp("honda"), NS(enableGasInterceptor=False))
  assert controller.nrdr_controller is sentinel
  assert controller.pid is sentinel.pid


class RecordingSolver:
  def __init__(self, *_):
    self.calls = []

  def reset(self):
    self.calls.clear()

  def cost_set(self, index, key, value):
    self.calls.append((index, key, np.copy(value)))

  set = cost_set


def mpc_pair():
  return pair(CORE + "longitudinal_mpc_lib/long_mpc.py", environment(AcadosOcpSolverCython=RecordingSolver))


@pytest.mark.parametrize("personality", [0, 1, 2, 3])
@pytest.mark.parametrize("present", [False, True])
def test_mpc_costs_inputs_and_fcw_match_baseline(personality, present):
  current, baseline = mpc_pair()
  actual, expected = (module["LongitudinalMpc"]() for module in (current, baseline))
  assert actual.nrdr is None and actual.tune is None
  for controller in (actual, expected):
    controller.run = lambda: None  # validate inputs/FCW, not the native optimizer
    controller.set_cur_state(27., -0.4)
    controller.x_sol[:, 0] = np.linspace(0., 150., 13)
  lead = NS(present=present, dRel=18., vLead=18., aLeadK=-1., aLeadTau=1.5, modelProb=0.95)
  radar = NS(leadOne=lead, leadTwo=NS(**(vars(lead) | {"dRel": 35., "vLead": 28.})))
  actual.set_weights(False, personality)
  expected.set_weights(False, min(personality, 2))
  actual.update(radar, personality, model=object(), v_cruise=40.)
  expected.update(radar, min(personality, 2))
  np.testing.assert_array_equal(actual.params, expected.params)
  assert actual.source == expected.source
  assert actual.crash_cnt == expected.crash_cnt
  assert len(actual.solver.calls) == len(expected.solver.calls)
  for a, b in zip(actual.solver.calls, expected.solver.calls, strict=True):
    assert a[:2] == b[:2]
    np.testing.assert_array_equal(a[2], b[2])


class FakePlannerSP:
  def __init__(self, *_):
    pass

  def update(self, _sm):
    pass

  def update_targets(self, sm, _v, a, cruise):
    self.seen_cruise_target = cruise
    return min(cruise, sm.target_limit), a

  def is_e2e(self, sm):
    return sm['selfdriveState'].experimentalMode


class FakePlannerMpc:
  def __init__(self, **kwargs):
    self.nrdr = None
    self.tune = None
    self.kwargs = kwargs
    self.crash_cnt = 0
    self.source = SOURCE.lead0

  def set_weights(self, prev, personality):
    self.weights = (prev, personality)

  def set_cur_state(self, v, a):
    self.v, self.a = v, a

  def update(self, radar, personality, **_):
    self.v_solution = np.maximum(0., self.v + np.linspace(0., 10., 13) * radar.accel)
    self.a_solution = np.full(13, radar.accel)
    self.j_solution = np.zeros(12)
    self.crash_cnt = radar.crash_cnt
    self.source = SOURCE.lead0


class SM(dict):
  target_limit = 100.0


def planner_pair(**overrides):
  helpers = definitions(ROOT / (CORE + "drive_helpers.py"), environment(ACCELERATION_DUE_TO_GRAVITY=9.81))
  env = environment(LongitudinalMpc=FakePlannerMpc, LongitudinalPlannerSP=FakePlannerSP,
                    T_IDXS_MPC=np.linspace(0., 10., 13), should_stop=helpers['should_stop'],
                    get_accel_from_plan=helpers['get_accel_from_plan'])
  env.update(overrides)
  return pair(CORE + "longitudinal_planner.py", env)


@pytest.mark.parametrize("brand", ["toyota", "hyundai", "subaru", "unknown"])
@pytest.mark.parametrize("openpilot_long", [True, False])
@pytest.mark.parametrize("personality", [0, 1, 2, 3])
def test_planner_update_matches_baseline(brand, openpilot_long, personality):
  current, baseline = planner_pair()
  CP = cp(brand)
  CP.openpilotLongitudinalControl = openpilot_long
  actual, expected = (module['LongitudinalPlanner'](CP, NS()) for module in (current, baseline))
  assert actual.nrdr is None and actual.mpc.kwargs['nrdr_enabled'] is False
  rng = np.random.default_rng(2024)
  for frame in range(160):
    v = float(rng.choice([0., 0.2, 0.29, 0.3, 2., 5., 15., 30., 40.]))
    sm = SM(carState=NS(vEgo=v, aEgo=float(rng.uniform(-4, 3)), standstill=v == 0,
                        steeringAngleDeg=float(rng.uniform(-45, 45)), vCruise=255 if frame % 21 == 0 else 110),
            carControl=NS(orientationNED=[] if frame % 2 else [0., 0.2, 0.], actuators=NS(accel=-0.7)),
            controlsState=NS(forceDecel=frame % 7 == 0, longControlState=STATE.off if frame % 5 == 0 else STATE.pid),
            selfdriveState=NS(enabled=frame % 5 != 0, personality=personality, experimentalMode=frame % 3 == 0),
            vehicleParameters=NS(angleOffsetDeg=1.5),
            modelV2=NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 0.1 if frame % 3 else 0.9])),
                       action=NS(desiredAcceleration=float(rng.uniform(-3., 2.)), shouldStop=frame % 4 == 0)),
            radarState=NS(accel=float(rng.uniform(-3., 2.)), crash_cnt=3 if frame % 9 == 0 else 0))
    sm.target_limit = 18.0 if frame % 4 == 0 else 100.
    baseline_sm = copy.deepcopy(sm)
    baseline_sm['selfdriveState'].personality = min(personality, 2)
    actual.update(sm)
    expected.update(baseline_sm)
    for attr in ('output_a_target', 'output_should_stop', 'a_cruise', 'allow_throttle', 'fcw', 'seen_cruise_target'):
      assert getattr(actual, attr) == getattr(expected, attr), (frame, attr)
    assert actual.v_desired_filter.x == expected.v_desired_filter.x
    assert actual.mpc.weights == expected.mpc.weights
    for attr in ('v_desired_trajectory', 'a_desired_trajectory', 'j_desired_trajectory'):
      np.testing.assert_array_equal(getattr(actual, attr), getattr(expected, attr))


def test_honda_planner_still_constructs_nrdr_policy():
  sentinel = object()
  current, _ = planner_pair(NrdrLongitudinalPlanner=lambda *_: sentinel)
  planner = current['LongitudinalPlanner'](cp('honda'), NS())
  assert planner.nrdr is sentinel
  assert planner.mpc.kwargs['nrdr_enabled'] is True


@pytest.mark.parametrize("radarless", [True, False])
def test_dec_sequence_matches_baseline(radarless):
  current, baseline = pair(SUNNY + 'dec/dec.py', environment())
  CP = cp()
  CP.radarUnavailable = radarless
  params = NS(get_bool=lambda _: True)
  controllers = [module['DynamicExperimentalController'](CP, NS(crash_cnt=0), params=params) for module in (current, baseline)]
  for frame in range(120):
    sm = {'carState': NS(vEgo=frame % 31, vCruise=100, standstill=frame % 15 == 0),
          'radarState': NS(leadOne=NS(present=frame % 7 == 0)),
          'modelV2': NS(position=NS(x=np.linspace(0., (frame % 20) * 15., 33 if frame % 11 else 0)),
                        orientation=NS(x=np.zeros(33))),
          'selfdriveState': NS(experimentalMode=True)}
    for controller in controllers:
      controller._mpc.crash_cnt = int(frame % 13 == 0)
      controller.update(sm)
    a, b = controllers
    assert (a.mode(), a._has_slow_down, a._urgency, a._has_slowness) == (b.mode(), b._has_slow_down, b._urgency, b._has_slowness)


def test_non_honda_gap_button_ignores_nrdr_submode_and_reservations():
  assist = NS(preActive=1)
  custom = NS(LongitudinalPlanSP=NS(SpeedLimit=NS(AssistState=assist)))
  module = definitions(ROOT / 'openpilot/nrdr/hooks/selfdrived.py', environment(custom=custom, consume_button_press=forbidden))
  hook = module['NrdrSelfdrive'](cp())
  assert not hook.reserve_distance_button(assist.preActive)
  writes = []
  state = NS(CP=cp(), params=NS(put=lambda *args: writes.append(args)), personality=3, experimental_mode_switched=False)
  for expected in (1, 0, 2, 1):
    assert hook.update_personality(state, NS(buttonEvents=[NS(pressed=False, type=1)]), False)
    assert state.personality == expected
  assert writes == [('LongitudinalPersonality', p) for p in (1, 0, 2, 1)]


def test_speed_limit_map_calculation_matches_baseline():
  source = NS(map=1, schema=NS(enumerants={'map': 1}))
  custom = NS(LongitudinalPlanSP=NS(SpeedLimit=NS(Source=source)))
  current, baseline = pair(SUNNY + 'speed_limit/speed_limit_resolver.py', environment(
    custom=custom, apply_map_limit=forbidden, LIMIT_ADAPT_ACC=-1.0))
  for distance in (0., 20., 150., 900.):
    for speed, next_speed in ((20., 10.), (10., 20.), (0., 15.), (20., 0.)):
      outputs = []
      for module in (current, baseline):
        resolver = object.__new__(module['SpeedLimitResolver'])
        resolver.nrdr_enabled = False
        resolver.v_ego = 25.
        resolver._gps_location_service = 'gps'
        resolver.limit_solutions, resolver.distance_solutions = {}, {}
        sm = {'gps': NS(unixTimestampMillis=99000), 'liveMapDataSP': NS(speedLimitAheadDistance=distance)}
        resolver._calculate_map_data_limits(sm, speed, next_speed)
        outputs.append((resolver.limit_solutions, resolver.distance_solutions))
      assert outputs[0] == outputs[1]


def test_sunny_planner_selects_baseline_sla_and_resolver():
  source = NS(cruise=0)
  custom = NS(LongitudinalPlanSP=NS(LongitudinalPlanSource=source,
                                  DynamicExperimentalControl=NS(DynamicExperimentalControlState=object)))
  baseline_sla = object()
  env = environment(custom=custom, EventsSP=lambda: object(),
                    DynamicExperimentalController=lambda *_: object(), SmartCruiseControl=lambda: object(),
                    SpeedLimitResolver=lambda **kwargs: NS(**kwargs), SpeedLimitAssist=lambda *_: baseline_sla,
                    NrdrSpeedLimitAssist=forbidden, get_active_bundle=lambda: None, E2EAlertsHelper=lambda: object())
  module = definitions(ROOT / (SUNNY + 'longitudinal_planner.py'), env)
  planner = module['LongitudinalPlannerSP'](cp(), NS(), object())
  assert planner.sla is baseline_sla
  assert planner.resolver.nrdr_enabled is False


def test_honda_mpc_retains_fourth_personality_and_fcw_authorization():
  calls = []

  class PolicySpy:
    tune = object()

    def __init__(self, *_args, **kwargs):
      assert kwargs['honda_bosch_a_radar'] is True

    def reset(self):
      calls.append('reset')

    def base_jerk(self, personality, _fallback):
      calls.append(('personality', personality))
      return 1.5

    def jerk_factors(self, personality, jerk, _accel):
      return jerk, jerk

    def fcw_authorized(self, *_):
      calls.append('fcw')
      return False

  module = definitions(ROOT / (CORE + 'longitudinal_mpc_lib/long_mpc.py'),
                       environment(AcadosOcpSolverCython=RecordingSolver, NrdrLongitudinalMpc=PolicySpy))
  controller = module['LongitudinalMpc'](nrdr_enabled=True, honda_bosch_a_radar=True)
  controller.run = lambda: None
  controller.x_sol[:, 0] = 100.
  controller.set_weights(personality=3)
  lead = NS(present=True, dRel=10., vLead=0., aLeadK=0., aLeadTau=1.5, modelProb=0.95)
  controller.update(NS(leadOne=lead, leadTwo=lead), personality=3)
  assert ('personality', 3) in calls
  assert 'fcw' in calls
  assert controller.crash_cnt == 0


@pytest.mark.parametrize('brand,enabled', [('honda', True), ('toyota', False), ('', False)])
def test_native_tuning_controls_follow_vehicle_policy(brand, enabled):
  widget = type('Widget', (), {'_update_state': lambda _: None})
  state = NS(CP=cp(brand), is_offroad=lambda: True)
  module = definitions(ROOT / 'openpilot/nrdr/ui/settings/longitudinal_tuning.py', {"Widget": widget, "Callable": Callable,
                       "ui_state": state, "nrdr_longitudinal_enabled": policy.nrdr_longitudinal_enabled})
  layout = object.__new__(module['LongitudinalTuningLayout'])
  values = []
  layout._live_learning_gas = NS(action_item=NS(set_enabled=lambda value: values.append(('gas', value))))
  layout._tuning_items = [layout._live_learning_gas, NS(), NS(action_item=NS(set_enabled=lambda value: values.append(('tune', value))))]
  layout._update_state()
  assert values == [('gas', enabled), ('tune', enabled), ('gas', enabled)]


def test_generated_sunnylink_schema_gates_nrdr_panel_and_econ():
  schema = json.loads((ROOT / 'openpilot/sunnypilot/sunnylink/settings_ui.json').read_text(encoding='utf-8'))

  def walk(node):
    if isinstance(node, dict):
      yield node
      for value in node.values():
        yield from walk(value)
    elif isinstance(node, list):
      for value in node:
        yield from walk(value)

  nodes = list(walk(schema))
  required = {'type': 'capability', 'field': 'nrdr_longitudinal_tuning_available', 'equals': True}
  panel = next(node for node in nodes if node.get('id') == 'nrdr_longitudinal')
  assert panel['trigger_condition'] == required
  item = next(node for node in nodes if node.get('key') == 'LongitudinalPersonality')
  econ = next(option for option in item['options'] if option['value'] == 3)
  assert econ['enablement'] == [required]
  for option in item['options'][:3]:
    assert not option.get('enablement')
