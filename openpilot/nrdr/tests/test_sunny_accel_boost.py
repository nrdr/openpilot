"""Offline port regressions; real source math, stubbed Params/IPC/native MPC.

Baseline parity loads the pinned pre-port Git blobs, never moving HEAD. This
does not validate the native optimizer, model calibration or vehicle behavior.
"""
import ast
import copy
import hashlib
import json
import subprocess
from collections import deque
from collections.abc import Callable
from enum import IntEnum
from types import SimpleNamespace as NS
from typing import Union
from unittest.mock import Mock

import numpy as np
import pytest

from openpilot.cereal import custom, log
from opendbc.car.honda.tests.test_civic_pcm import interface
from opendbc.car.honda.values import CAR, HondaFlags
from openpilot.nrdr.tests import test_non_honda_longitudinal as h

BASE = '963bc4a5fc842e009ab2cb1770126cc555519a76'
BOOST = h.SUNNY + 'accel_boost.py'
UPSTREAM = h.ROOT / 'openpilot/nrdr/tests/fixtures/accel_boost_sp_8cf6ff9a.py.txt'
UPSTREAM_BLOB = 'd2bb8b3b64f784aaeb48c32285ae585467f2f430'
SERVICES = ('modelV2', 'carState', 'selfdriveState', 'controlsState', 'radarState', 'carControl')


class Params:
  def __init__(self, enabled=False):
    self.enabled = enabled

  def get_bool(self, key):
    assert key == 'AccelBoostSP'
    return self.enabled


class SM(dict):
  target_limit = 100.
  valid = True

  def all_checks(self, services):
    return self.valid and all(s in self for s in services)


def messages(now=10_000_000_000, e2e=.2, mpc=1., personality=0):
  sm = SM(
    carState=NS(vEgo=20., aEgo=.1, standstill=False, canValid=True, accFaulted=False, gasPressed=False, brakePressed=False,
                stockAeb=False, vCruise=108., vCruiseCluster=108., steeringAngleDeg=0.),
    carControl=NS(enabled=True, longActive=True, orientationNED=[], actuators=NS(accel=.2), cruiseControl=NS(cancel=False, override=False)),
    selfdriveState=NS(enabled=True, experimentalMode=True, personality=personality),
    controlsState=NS(forceDecel=False, longControlState=h.STATE.pid),
    vehicleParameters=NS(angleOffsetDeg=0.),
    radarState=NS(accel=mpc, crash_cnt=0, leadOne=NS(present=True)),
    modelV2=NS(action=NS(desiredAcceleration=e2e, desiredCurvature=0., shouldStop=False),
               meta=NS(disengagePredictions=NS(t=[2., 4., 6., 8., 10.], brakePressProbs=[.05] * 6, gasPressProbs=[.9] * 6)),
               velocity=NS(x=[]), acceleration=NS(x=[])),
  )
  sm.logMonoTime = dict.fromkeys(SERVICES, now)
  return sm


def load_text(text, env, filename):
  tree = ast.parse(text, filename)
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
  namespace = dict(env, __file__=filename)
  exec(compile(tree, filename, 'exec'), namespace)
  return namespace


@pytest.fixture
def boost_env():
  clock = [10_000_000_000]
  env = h.environment(log=log, Params=Params, PARAMS_UPDATE_PERIOD=3, time=NS(monotonic_ns=lambda: clock[0]))
  return h.definitions(h.ROOT / BOOST, env), clock


def enabled_boost(boost_env):
  module, _ = boost_env
  boost = module['AccelBoostSP']()
  boost.params.enabled = True
  boost.update_params()
  return boost


def apply(boost, sm=None, e2e=.2, mpc=1., cruise=1.):
  return boost.update(messages() if sm is None else sm, e2e, mpc, cruise)


@pytest.fixture
def upstream_module(boost_env):
  # Exact PR #2089 blob, kept locally so the reference needs no network or
  # upstream Git objects during CI. Verify its Git blob ID independently.
  source = UPSTREAM.read_bytes().replace(b'\r\n', b'\n')
  assert hashlib.sha1(b'blob ' + str(len(source)).encode() + b'\0' + source).hexdigest() == UPSTREAM_BLOB
  return h.definitions(UPSTREAM, boost_env[0])


def test_only_econ_changes_upstream_helper_source(boost_env, upstream_module):
  actual = ast.parse((h.ROOT / BOOST).read_text())
  expected = ast.parse(UPSTREAM.read_text())
  actual_class = next(n for n in actual.body if isinstance(n, ast.ClassDef))
  expected_class = next(n for n in expected.body if isinstance(n, ast.ClassDef))
  actual_update = next(n for n in actual_class.body if isinstance(n, ast.FunctionDef) and n.name == 'update')
  check = next(n for n in actual_update.body if isinstance(n, ast.If))
  econ = check.test.values.pop()
  assert ast.unparse(econ) == "sm['selfdriveState'].personality == log.LongitudinalPersonality.econ"
  assert ast.dump(actual_class) == ast.dump(expected_class)
  for tree in (actual, expected):
    tree.body = [n for n in tree.body if isinstance(n, (ast.Assign, ast.FunctionDef))]
  assert ast.dump(actual) == ast.dump(expected)


@pytest.mark.parametrize('personality', [0, 1, 2])
@pytest.mark.parametrize('sequence', [
  'positive', 'mild_negative', 'strong_negative', 'stop_release', 'curve', 'speed',
  'gas_reopens', 'missing_predictions', 'disengage', 'unrelated_gates', 'mixed',
])
def test_enabled_exact_upstream_reference_sequence(boost_env, upstream_module, personality, sequence):
  actual = enabled_boost(boost_env)
  reference = upstream_module['AccelBoostSP']()
  rng = np.random.default_rng(2089)
  saw_stop_release = False
  for frame in range(400):
    e2e, mpc, cruise = .2, 1., 1.
    sm = messages(personality=personality)
    model, cs = sm['modelV2'], sm['carState']
    pred = model.meta.disengagePredictions
    if sequence == 'positive':
      e2e = (0., .2, 1., 5., 5.01)[frame // 80]
    elif sequence == 'mild_negative':
      e2e = (-.05, -.2, -.3, -.69, -.7)[frame // 80]
    elif sequence == 'strong_negative':
      e2e = (-1., -2., -3.5, -.7)[frame // 100]
    elif sequence == 'stop_release':
      model.action.shouldStop = 100 <= frame < 120 or 300 <= frame < 320
      e2e = -.3 if model.action.shouldStop else .2
    elif sequence == 'curve':
      model.action.desiredCurvature = (0., 1.5, 2., 2.5, -2.)[frame // 80] / cs.vEgo ** 2
    elif sequence == 'speed':
      cs.vEgo = (0., .5, 1., 1.5, 2.)[frame // 80]
    elif sequence == 'gas_reopens':
      pred.brakePressProbs[1] = .5
      pred.gasPressProbs[1] = (.3, .6, .7, .8, .9)[frame // 80]
    elif sequence == 'missing_predictions':
      if 100 <= frame < 120:
        pred.brakePressProbs = []
      if 200 <= frame < 220:
        pred.gasPressProbs = [0.]
      if frame >= 300:
        pred.brakePressProbs, pred.gasPressProbs = [.05] * 2, [.9] * 2
        pred.t = []  # Upstream does not require a time array or six predictions.
    elif sequence == 'disengage':
      sm['selfdriveState'].enabled = frame % 120 < 100
    elif sequence == 'unrelated_gates':
      # Do not accidentally reintroduce the previous port's extra gating.
      sm.valid = False
      sm.logMonoTime = dict.fromkeys(SERVICES, 0)
      cs.canValid, cs.accFaulted = False, True
      cs.gasPressed = cs.brakePressed = cs.stockAeb = True
      sm['carControl'].longActive = False
      sm['controlsState'].forceDecel = True
      sm['controlsState'].longControlState = h.STATE.stopping
      sm['selfdriveState'].experimentalMode = False
      mpc, cruise = -2., -3.
    elif sequence == 'mixed':
      e2e, mpc, cruise = (float(x) for x in rng.uniform(-3.5, 6., 3))
      cs.vEgo = float(rng.uniform(0., 40.))
      model.action.desiredCurvature = float(rng.uniform(-.02, .02))
      pred.gasPressProbs[1], pred.brakePressProbs[1] = (float(x) for x in rng.uniform(0., 1., 2))
      model.action.shouldStop = frame % 19 < 3
    model.action.desiredAcceleration = e2e
    got = actual.update(copy.deepcopy(sm), e2e, mpc, cruise)
    want = reference.update(copy.deepcopy(sm), e2e, mpc, cruise)
    assert got == want, (sequence, frame)
    assert actual.boost == reference.boost
    assert actual.total_boost == reference.total_boost
    if sequence == 'stop_release' and frame == 100:
      assert actual.boost > 0 and actual.total_boost > 0  # original release, not immediate reset
      saw_stop_release = True
  if sequence == 'stop_release':
    assert saw_stop_release


def test_upstream_param_poll_and_reset_parity(boost_env, upstream_module):
  actual = boost_env[0]['AccelBoostSP']()
  reference = upstream_module['AccelBoostSP']()
  for frame in range(300):
    enabled = frame < 80 or frame >= 170
    actual.params.enabled = reference.params.enabled = enabled
    assert actual.update_params() == reference.update_params()
    assert actual.enabled == reference.enabled
    if actual.enabled:
      assert apply(actual) == apply(reference)
    assert (actual.boost, actual.total_boost) == (reference.boost, reference.total_boost)


def test_econ_immediately_has_no_boost_and_no_new_calibration(boost_env):
  boost = enabled_boost(boost_env)
  for _ in range(100):
    apply(boost)
  assert boost.boost > 0
  assert apply(boost, messages(personality=log.LongitudinalPersonality.econ)) == .2
  assert boost.boost == boost.total_boost == 0.
  # Returning to a supported personality starts with the original build step.
  assert apply(boost) == pytest.approx(.21)


def test_no_headroom_or_negative_reset_in_helper(boost_env):
  boost = enabled_boost(boost_env)
  for _ in range(100):
    apply(boost)
  assert apply(boost, mpc=-2., cruise=-3.) == pytest.approx(.6)
  assert apply(boost, e2e=-.3) == pytest.approx(.02)
  assert apply(boost, e2e=-1.) == -1.
  assert boost.boost == .4  # strong deceleration fades output, not internal state


class Mpc(h.FakePlannerMpc):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.nrdr = NS(fcw_authorized=lambda *_: True) if kwargs.get('nrdr_enabled') else None


@pytest.fixture(scope='module')
def preport_sources():
  return {path: subprocess.check_output(['git', '-C', str(h.ROOT), 'show', f'{BASE}:{path}']).decode()
          for path in (h.CORE + 'longitudinal_planner.py', h.SUNNY + 'longitudinal_planner.py')}


def planners(boost_env, preport_sources, cp, sp, enabled=False, tune_scale=1., roen=False, boost_module=None):
  module, _ = boost_env
  module = module if boost_module is None else boost_module
  helpers = h.definitions(h.ROOT / (h.CORE + 'drive_helpers.py'), h.environment(ACCELERATION_DUE_TO_GRAVITY=9.81))
  env = h.environment(LongitudinalMpc=Mpc, T_IDXS_MPC=np.linspace(0., 10., 13), log=log, custom=custom, HondaFlags=HondaFlags,
                      should_stop=helpers['should_stop'], get_accel_from_plan=helpers['get_accel_from_plan'])
  nrdr_class = h.definitions(h.ROOT / 'openpilot/nrdr/features/longitudinal/longitudinal_planner.py', env)['NrdrLongitudinalPlanner']

  def nrdr_factory(CP, SP, _tune):
    obj = nrdr_class.__new__(nrdr_class)
    obj.CP, obj.CP_SP = CP, SP
    obj.tune = NS(a_cruise_max_scale=tune_scale)
    obj.params = NS(generation=1)
    obj.settings_generation = 1
    obj.v_ego_stopping = CP.deprecated.vEgoStopping
    obj.cruise_scale, obj.cruise_overspeed_allowance = 1., 0.
    obj.standstill_gap_extra = obj.standstill_gap_requested = 0.
    obj.roen_acceleration_limits, obj.launch_armed = roen, False
    return obj

  def boost_factory():
    boost = module['AccelBoostSP']()
    boost.params.enabled = enabled
    return boost

  env.update(NrdrLongitudinalPlanner=nrdr_factory, AccelBoostSP=boost_factory,
             EventsSP=lambda: NS(clear=lambda: None), SmartCruiseControl=lambda: None,
             SpeedLimitResolver=lambda **_: None, NrdrSpeedLimitAssist=lambda *_: None,
             SpeedLimitAssist=lambda *_: None, get_active_bundle=lambda: None,
             E2EAlertsHelper=lambda: NS(update=lambda *_: None))
  instances = []
  for baseline in (False, True):
    sp_path, core_path = h.SUNNY + 'longitudinal_planner.py', h.CORE + 'longitudinal_planner.py'
    extension = (load_text(preport_sources[sp_path], env, BASE + ':' + sp_path) if baseline else
                 h.definitions(h.ROOT / sp_path, env))['LongitudinalPlannerSP']
    # SCC/SLA target selection and the native MPC are boundaries of this test;
    # the production boost hook, NRDR policy and final arbitration run verbatim.
    extension.update_targets = h.FakePlannerSP.update_targets
    core_env = dict(env, LongitudinalPlannerSP=extension)
    core = (load_text(preport_sources[core_path], core_env, BASE + ':' + core_path) if baseline else
            h.definitions(h.ROOT / core_path, core_env))
    instances.append(core['LongitudinalPlanner'](cp.as_reader(), copy.deepcopy(sp)))
  return instances


PATHS = [
  pytest.param(CAR.HONDA_CIVIC, 0, False, id='civic-mvl'),
  pytest.param(CAR.HONDA_CIVIC, 1, False, id='civic-ecu'),
  pytest.param(CAR.HONDA_CIVIC, 2, False, id='civic-experimental'),
  pytest.param(CAR.HONDA_CLARITY, 0, False, id='clarity-pcm'),
  pytest.param(CAR.HONDA_CIVIC, 0, True, id='civic-interceptor'),
  pytest.param(CAR.HONDA_CLARITY, 0, True, id='clarity-interceptor'),
]


@pytest.mark.parametrize('car,mode,interceptor', PATHS)
@pytest.mark.parametrize('personality', range(4))
@pytest.mark.parametrize('experimental', [False, True])
def test_off_exact_planner_parity_against_preport(boost_env, preport_sources, car, mode, interceptor, personality, experimental):
  ci, _ = interface(car, interceptor=interceptor, pcm_mode=mode)
  actual, base = planners(boost_env, preport_sources, ci.CP, ci.CP_SP)
  rng = np.random.default_rng(2089)
  for frame in range(320):
    now = 10_000_000_000 + frame * 50_000_000
    boost_env[1][0] = now
    sm = messages(now, float(rng.uniform(-3., 1.)), float(rng.uniform(-3., 2.)), personality)
    sm['carState'].vEgo = float(rng.choice([0., .5, 2., 10., 20., 30.]))
    sm['carState'].standstill = sm['carState'].vEgo == 0.
    sm['carState'].steeringAngleDeg = float(rng.uniform(-50., 50.))
    sm['carState'].vCruise = 255 if frame % 17 == 0 else 108.
    sm['controlsState'].forceDecel = frame % 13 == 0
    sm['controlsState'].longControlState = h.STATE.off if frame % 11 == 0 else h.STATE.pid
    sm['selfdriveState'].experimentalMode = experimental
    sm['modelV2'].action.shouldStop = frame % 7 == 0
    sm['modelV2'].meta.disengagePredictions.gasPressProbs[1] = .1 if frame % 3 == 0 else .9
    sm['carControl'].orientationNED = [0., .1, 0.]
    sm.target_limit = 15. if frame % 5 == 0 else 100.
    actual.update(copy.deepcopy(sm))
    base.update(copy.deepcopy(sm))
    for name in ('output_a_target', 'output_should_stop', 'a_cruise', 'allow_throttle', 'fcw', 'prev_accel_clip', 'seen_cruise_target'):
      assert getattr(actual, name) == getattr(base, name), (frame, name)
    assert actual.v_desired_filter.x == base.v_desired_filter.x
    assert actual.mpc.source == base.mpc.source
    for name in ('v_desired_trajectory', 'a_desired_trajectory', 'j_desired_trajectory'):
      np.testing.assert_array_equal(getattr(actual, name), getattr(base, name))


@pytest.mark.parametrize('scale', [.2, 1., 2.])
@pytest.mark.parametrize('roen', [False, True])
@pytest.mark.parametrize('car,mode,interceptor', PATHS)
def test_enabled_respects_nrdr_scale_and_current_bounds(boost_env, preport_sources, scale, roen, car, mode, interceptor):
  ci, _ = interface(car, interceptor=interceptor, pcm_mode=mode)
  actual, base = planners(boost_env, preport_sources, ci.CP, ci.CP_SP, True, scale, roen)
  for frame in range(150):
    now = 10_000_000_000 + frame * 50_000_000
    boost_env[1][0] = now
    sm = messages(now, e2e=.05)
    actual.update(copy.deepcopy(sm))
    base.update(copy.deepcopy(sm))
    assert actual.prev_accel_clip == base.prev_accel_clip
    assert actual.a_cruise == base.a_cruise
    assert actual.output_should_stop == base.output_should_stop
    assert actual.output_a_target >= base.output_a_target
    assert actual.output_a_target <= min(actual.a_cruise, 1., actual.prev_accel_clip[1])
  assert actual.output_a_target > base.output_a_target
  # Preserve upstream's mild-deceleration offset, then the unchanged final
  # MPC/cruise minimum and platform clip. No positive-only port behavior.
  sm = messages(now, e2e=-.3)
  actual.update(copy.deepcopy(sm))
  base.update(copy.deepcopy(sm))
  assert base.output_a_target == pytest.approx(-.3)
  assert actual.output_a_target == pytest.approx(min(-.3 + .4 * .8, actual.a_cruise, actual.prev_accel_clip[1]))
  assert actual.accel_boost_sp.total_boost == pytest.approx(.32)


@pytest.mark.parametrize('car,mode,interceptor', PATHS)
@pytest.mark.parametrize('personality', [0, 1, 2])
def test_enabled_combined_planner_matches_upstream_helper(boost_env, upstream_module, preport_sources, car, mode, interceptor, personality):
  ci, _ = interface(car, interceptor=interceptor, pcm_mode=mode)
  actual, _ = planners(boost_env, preport_sources, ci.CP, ci.CP_SP, True)
  reference, _ = planners(boost_env, preport_sources, ci.CP, ci.CP_SP, True, boost_module=upstream_module)
  for frame in range(400):
    e2e = (.2, -.3, -1., .2)[frame // 100]
    sm = messages(e2e=e2e, personality=personality)
    sm['modelV2'].action.shouldStop = 120 <= frame < 130
    sm['modelV2'].action.desiredCurvature = .005 if frame % 70 < 20 else 0.
    sm['carState'].vEgo = 1.5 if frame % 100 < 20 else 20.
    sm['radarState'].accel = -2. if 200 <= frame < 225 else 1.
    sm['carState'].vCruise = 60. if 300 <= frame < 325 else 108.
    actual.update(copy.deepcopy(sm))
    reference.update(copy.deepcopy(sm))
    for name in ('output_a_target', 'output_should_stop', 'prev_accel_clip', 'a_cruise', 'allow_throttle'):
      assert getattr(actual, name) == getattr(reference, name), (frame, name)
    assert actual.mpc.source == reference.mpc.source
    assert actual.v_desired_filter.x == reference.v_desired_filter.x
    assert actual.accel_boost_sp.boost == reference.accel_boost_sp.boost
    assert actual.accel_boost_sp.total_boost == reference.accel_boost_sp.total_boost


def test_call_point_is_only_core_planner_change(preport_sources):
  path = h.CORE + 'longitudinal_planner.py'
  actual = ast.parse((h.ROOT / path).read_text())
  baseline = ast.parse(preport_sources[path])
  update = next(n for n in ast.walk(actual) if isinstance(n, ast.FunctionDef) and n.name == 'update')
  def calls(statement, name):
    return any(isinstance(n, ast.Call) and
               ((isinstance(n.func, ast.Attribute) and n.func.attr == name) or
                (isinstance(n.func, ast.Name) and n.func.id == name)) for n in ast.walk(statement))
  insertion = next(i for i, n in enumerate(update.body) if calls(n, 'apply_accel_boost'))
  assert next(i for i, n in enumerate(update.body) if calls(n, 'launch_accel')) < insertion
  assert next(i for i, n in enumerate(update.body) if calls(n, 'get_cruise_accel')) < insertion
  candidate_index = next(i for i, n in enumerate(update.body) if isinstance(n, ast.Assign) and
                         any(isinstance(t, ast.Name) and t.id == 'candidates' for t in n.targets))
  assert insertion < candidate_index
  del update.body[insertion]
  assert ast.dump(actual) == ast.dump(baseline)


@pytest.mark.parametrize('gate', ['stock_long', 'non_e2e', 'econ', 'missing_predictions'])
def test_enabled_planner_gating_keeps_baseline(boost_env, preport_sources, gate):
  ci, _ = interface(pcm_mode=0)
  if gate == 'stock_long':
    ci.CP.openpilotLongitudinalControl = False
  actual, base = planners(boost_env, preport_sources, ci.CP, ci.CP_SP, True)
  for frame in range(100):
    now = 10_000_000_000 + frame * 50_000_000
    boost_env[1][0] = now
    sm = messages(now)
    if gate == 'non_e2e':
      sm['selfdriveState'].experimentalMode = False
    elif gate == 'econ':
      sm['selfdriveState'].personality = log.LongitudinalPersonality.econ
    elif gate == 'missing_predictions':
      sm['modelV2'].meta.disengagePredictions.brakePressProbs = []
    actual.update(copy.deepcopy(sm))
    base.update(copy.deepcopy(sm))
    assert actual.output_a_target == base.output_a_target
    assert actual.output_should_stop == base.output_should_stop
    if gate != 'non_e2e':
      assert actual.accel_boost_sp.total_boost == 0.


@pytest.mark.parametrize('interceptor,learning', [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize('scale', [0., .5, 1., 5.])
@pytest.mark.parametrize('static_feedforward', [False, True])
def test_existing_pid_scaling_cannot_raise_outer_accel_bounds(boost_env, interceptor, learning, scale, static_feedforward):
  env = h.environment(deque=deque, HondaFlags=HondaFlags,
                      NrdrParamKey=NS(**{f'LONG_PID_TUNE_SCALE_{name}': name for name in ('AGGRESSIVE', 'STANDARD', 'RELAXED', 'ECON')}))
  module = h.definitions(h.ROOT / 'openpilot/nrdr/features/longitudinal/longcontrol.py', env)
  cls = module['NrdrLongControl']
  control = cls.__new__(cls)
  ci, _ = interface(interceptor=interceptor, pcm_mode=0)
  control.CP, control.CP_SP = ci.CP, ci.CP_SP
  control.params, control.settings_generation = NS(generation=1), 1
  control.tune = NS(refresh=lambda: None)
  control.frame = 0
  control.last_output_accel = 0.
  control.long_control_state = h.STATE.pid
  control.pid = h.PIDController(.5, .5, rate=100)
  control.pid_scales = (scale,) * 4
  control.pid_scale = module['effective_long_pid_scale'](control.pid_scales, 0, interceptor, learning)
  control.live_learning_gas, control.static_feedforward = learning, static_feedforward
  control.roen_acceleration_limits = False
  control.v_ego_starting = .5
  control.drel_window, control.drel_filtered = deque(maxlen=10), float('inf')
  cs = NS(vEgo=20., aEgo=.1, brakePressed=False, cruiseState=NS(standstill=False))
  boost = enabled_boost(boost_env)
  for _ in range(150):
    target = apply(boost)
    output = control.update(True, cs, target, False, (-3.5, .55), personality=0)
    assert -3.5 <= output <= .55
    assert .2 <= target <= .6 + 1e-12
  # Same negative target into identical existing controller state: no second
  # boost/scaling stage was inserted in LongControl or the Honda controller.
  reference = copy.deepcopy(control)
  target = apply(boost, e2e=-1.)
  assert target == -1.
  assert control.update(True, cs, target, False, (-3.5, .55), personality=0) == reference.update(
    True, cs, -1., False, (-3.5, .55), personality=0)


def test_default_off_and_remote_registry():
  header = (h.ROOT / 'openpilot/common/params_keys.h').read_text()
  assert '{"AccelBoostSP", {PERSISTENT | BACKUP, BOOL, "0"}}' in header
  remote = json.loads((h.ROOT / 'openpilot/sunnypilot/sunnylink/settings_ui.json').read_text())
  def walk(value):
    if isinstance(value, dict):
      yield value
      for item in value.values():
        yield from walk(item)
    elif isinstance(value, list):
      for item in value:
        yield from walk(item)
  controls = [node for node in walk(remote) if node.get('key') == 'AccelBoostSP']
  assert len(controls) == 1
  assert controls[0]['enablement'] == [{'type': 'capability', 'field': 'has_longitudinal_control', 'equals': True}]


class WidgetDouble:
  def __init__(self, *args, **kwargs):
    self.text = args[0] if args else ''
    self.description = kwargs.get('description', '')
    self._checked = kwargs.get('initial_state', False)
    self.enabled = True
    self.visible = True

  def set_enabled(self, value):
    self.enabled = value

  def set_visible(self, value):
    self.visible = value

  def set_checked(self, value):
    self._checked = value

  def set_click_callback(self, callback):
    self.callback = callback

  def _handle_mouse_release(self, _mouse_pos):
    self._checked = not self._checked


class NavDouble:
  def __init__(self):
    self.items = []
    self._scroller = NS(add_widgets=self.items.extend)


class UIParams:
  def __init__(self):
    self.values, self.writes = {}, []

  def get_bool(self, key, *_):
    return self.values.get(key, False)

  get = get_bool

  def put_bool(self, key, value, **kwargs):
    self.values[key] = value
    self.writes.append((key, value, kwargs))


def test_c4_native_toggle_is_reachable_persistent_and_capability_gated():
  params = UIParams()
  state = NS(params=params, CP=NS(), has_longitudinal_control=True, engaged=False,
             add_engaged_transition_callback=lambda _: None, update_params=lambda: None)
  # Execute the real parameter-control class, replacing only its drawing and
  # input-widget base. This exercises its actual synchronous Params writer.
  button_path = h.ROOT / 'openpilot/selfdrive/ui/mici/widgets/button.py'
  button_tree = ast.parse(button_path.read_text())
  button = next(n for n in button_tree.body if isinstance(n, ast.ClassDef) and n.name == 'BigParamControl')
  env = {'Params': lambda: params, 'BigToggle': WidgetDouble, 'Callable': Callable, 'Union': Union,
         'rl': NS(Texture=object), 'MousePos': object}
  exec(compile(ast.Module(body=[button], type_ignores=[]), str(button_path), 'exec'), env)
  native_env = dict(env, log=log, NavScroller=NavDouble, BigParamControl=env['BigParamControl'],
                    BigMultiParamToggle=WidgetDouble, BigButton=WidgetDouble, GreyBigButton=WidgetDouble,
                    BigConfirmationCircleButton=WidgetDouble, LaneCenteringLayoutMici=lambda: None,
                    restart_needed_callback=lambda *_: None, ui_state=state, gui_app=NS(texture=lambda *_: None))
  module = h.definitions(h.ROOT / 'openpilot/selfdrive/ui/mici/layouts/settings/toggles.py', native_env)
  layout = module['TogglesLayoutMici']()
  toggle = layout._accel_boost_toggle
  assert toggle in layout.items
  assert layout.items.index(toggle) == layout.items.index(layout._experimental_btn) + 1
  assert toggle.param == 'AccelBoostSP'
  assert not toggle._checked and toggle.enabled()
  assert len(toggle.description) < 90
  toggle._handle_mouse_release(None)
  assert params.writes[-1] == ('AccelBoostSP', True, {'block': True})
  params.put_bool('AccelBoostSP', False)
  layout._update_toggles()
  assert not toggle._checked  # external Off is reflected, not overwritten
  state.has_longitudinal_control = False
  assert not toggle.enabled()
  state.has_longitudinal_control, state.CP = True, None
  assert not toggle.enabled()

  settings = (h.ROOT / 'openpilot/selfdrive/ui/mici/layouts/settings/settings.py').read_text()
  sunny_settings = (h.ROOT / 'openpilot/selfdrive/ui/sunnypilot/mici/layouts/settings.py').read_text()
  assert 'self._toggles_panel = TogglesLayoutMici()' in settings
  assert 'gui_app.push_widget(self._toggles_panel)' in settings
  assert 'OP.SettingsLayout.__init__(self)' in sunny_settings
  assert 'self._toggles_panel =' not in sunny_settings


def test_sunnylink_source_compiles_the_boost_toggle():
  from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC
  compiled = compile_schema(DEFAULT_SRC)
  stored = json.loads((h.ROOT / 'openpilot/sunnypilot/sunnylink/settings_ui.json').read_text())
  def items(node):
    if isinstance(node, dict):
      if node.get('key') == 'AccelBoostSP':
        yield node
      for value in node.values():
        yield from items(value)
    elif isinstance(node, list):
      for value in node:
        yield from items(value)
  assert list(items(compiled)) == list(items(stored))
  assert len(list(items(compiled))) == 1


@pytest.mark.parametrize('initial', (False, True))
@pytest.mark.parametrize('has_cp,has_long', ((True, True), (True, False), (False, False)))
@pytest.mark.parametrize('refresh', ('show_event', '_update_state'))
def test_c3x_boost_refresh_reads_external_choice_without_writes(initial, has_cp, has_long, refresh):
  from openpilot.nrdr.tests.test_experimental_button_regressions import RecordingParams
  from openpilot.nrdr.tests.test_optional_longitudinal_preferences import execute, method

  params = RecordingParams({'AccelBoostSP': initial})
  widget = type('Widget', (), {'_update_state': lambda self: None})
  env = {'Widget': widget, 'Callable': Callable, 'Params': lambda: params}

  def load_class(relative, name, base, methods):
    # Keep the production constructor and state accessors; omit drawing only.
    execute([ast.ClassDef(name=name, bases=[ast.Name(id=base, ctx=ast.Load())], keywords=[],
                          body=[method(relative, name, m) for m in methods], decorator_list=[])], env)
    return env[name]

  load_class('openpilot/system/ui/widgets/toggle.py', 'Toggle', 'Widget', ('__init__', 'get_state', 'set_state'))
  toggle = load_class('openpilot/system/ui/sunnypilot/widgets/toggle.py', 'ToggleSP', 'Toggle', ('__init__',))
  action = load_class('openpilot/system/ui/widgets/list_view.py', 'ToggleAction', 'Widget', ('get_state', 'set_state'))

  def toggle_item(**kwargs):
    control = action()
    control.toggle = toggle(param=kwargs['param'], callback=kwargs.get('callback'))
    control.enabled, control.set_enabled = True, Mock()
    return Mock(action_item=control, description=kwargs.get('description', ''))

  state = NS(params=params, has_longitudinal_control=has_long, has_icbm=False, is_offroad=lambda: True,
             CP=NS(alphaLongitudinalAvailable=True, pcmCruise=False) if has_cp else None,
             CP_SP=NS(intelligentCruiseButtonManagementAvailable=False) if has_cp else None)
  env = h.definitions(h.ROOT / 'openpilot/nrdr/ui/settings_policy.py', dict(env, tr=lambda text: text))
  env.update(IntEnum=IntEnum, tr_noop=lambda text: text, ui_state=state, toggle_item_sp=toggle_item,
             option_item_sp=Mock(), simple_button_item_sp=Mock(), Scroller=Mock(), SpeedLimitSettingsLayout=Mock())
  module = h.definitions(h.ROOT / 'openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise.py', env)
  layout = module['CruiseLayout']()
  boost_control = layout.accel_boost_toggle.action_item
  assert boost_control.get_state() is initial
  assert params.actions == []  # Construction does not rewrite saved choices.
  layout.show_event()
  assert params.actions == []

  # Both external directions must refresh on reopening and while visible,
  # even without car parameters or longitudinal capability.
  for external in (not initial, initial):
    params.put_bool('AccelBoostSP', external, block=True)
    expected_actions = [a for a in params.actions if a[1] == 'AccelBoostSP']
    for _ in range(3):
      getattr(layout, refresh)()
      assert boost_control.get_state() is external
      params.flush()
      assert params.get_bool('AccelBoostSP') is external
      assert [a for a in params.actions if a[1] == 'AccelBoostSP'] == expected_actions
