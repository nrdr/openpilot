"""MVL/Sunny boost integration with real planner math and isolated I/O/solver boundaries."""
import copy
import subprocess
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.tests import test_mvl_host_parity as h
from openpilot.nrdr.tests.test_mvl_experimental_selection import messages


@pytest.fixture
def boost_env():
  reads = []
  settings = NS(enabled=False)

  def get_bool(key):
    reads.append(key)
    assert key == 'AccelBoostSP'
    return settings.enabled

  env = h.environment(Params=lambda: NS(get_bool=get_bool), PARAMS_UPDATE_PERIOD=3)
  env.update(h.definitions(h.source(h.SP + 'accel_boost.py'), env))
  return env, settings, reads


def planner_class(env, planner_source=None):
  env = env | {
    'EventsSP': lambda: NS(clear=lambda: None, to_msg=list),
    'E2EAlertsHelper': lambda: NS(update=lambda *_: None),
    'SmartCruiseControl': h.SmartCruiseBoundary, 'SpeedLimitResolver': h.ResolverBoundary,
    'SpeedLimitAssist': h.TargetFeatureBoundary, 'NrdrSpeedLimitAssist': h.TargetFeatureBoundary,
    'get_active_bundle': h.forbidden, 'LongitudinalMpc': h.PlannerMpcDouble,
    'T_IDXS_MPC': np.linspace(0., 10., 13),
  }
  helpers = h.definitions(h.source(h.CORE + 'drive_helpers.py'), env)
  env.update({key: helpers[key] for key in ('get_accel_from_plan', 'should_stop')})
  env['AccelBoost'] = h.definitions(h.source(h.MPC + 'mvl_accel_boost.py'), env)['AccelBoost']
  env['LongitudinalPlannerSP'] = h.definitions(h.source(h.SP + 'longitudinal_planner.py'), env)['LongitudinalPlannerSP']
  return h.definitions(planner_source or h.source(h.MPC + 'mvl_planner.py'), env)['MvlLongitudinalPlanner']


def boost_messages(profile=0):
  sm = messages(profile, True)
  sm['carState'].vCruiseCluster = sm['carState'].vCruise
  sm['carControl'].enabled = True
  sm['carControl'].cruiseControl = NS(override=False)
  model = sm['modelV2']
  model.action = NS(desiredAcceleration=.1, desiredCurvature=0., shouldStop=False)
  model.meta.disengagePredictions = NS(brakePressProbs=[.05, .05], gasPressProbs=[.9, .9])
  return sm


@pytest.mark.parametrize('profile,cap', [(0, .4), (1, .25), (2, .1)])
def test_original_profiles_match_pinned_sunny_math(boost_env, profile, cap):
  env, _, _ = boost_env
  reference = h.definitions(h.source('openpilot/nrdr/tests/fixtures/accel_boost_sp_8cf6ff9a.py.txt'), env)
  actual, expected = env['AccelBoostSP'](), reference['AccelBoostSP']()
  assert env['get_boost_max'](profile, 20.) == cap
  rng = np.random.default_rng(2089)
  for frame in range(300):
    sm = boost_messages(profile)
    sm['carState'].vEgo = float(rng.uniform(0., 40.))
    sm['selfdriveState'].enabled = frame % 71 != 0
    sm['modelV2'].action.shouldStop = frame % 29 < 3
    sm['modelV2'].action.desiredCurvature = float(rng.uniform(-.01, .01))
    sm['modelV2'].meta.disengagePredictions.brakePressProbs[1] = float(rng.uniform(0., .7))
    sm['modelV2'].meta.disengagePredictions.gasPressProbs[1] = float(rng.uniform(0., 1.))
    accel = float(rng.uniform(-1., 5.1))
    assert actual.update(sm, accel, 1., 1.) == expected.update(sm, accel, 1., 1.)
    assert actual.boost == expected.boost
    assert actual.total_boost == expected.total_boost


@pytest.mark.parametrize('speed', [0., 1., 1.5, 2., 6., 7., 10., 13., 17.5, 22.5, 27.5, 40., 55.])
def test_econ_uses_existing_interpolated_ceiling_ratio(boost_env, speed):
  env, _, _ = boost_env
  curves = h.historical_accel_curves()
  bp = curves['C3_ACCEL_PROFILE_BP']
  cap = .1 * np.interp(speed, bp, curves['C3_ACCEL_PROFILE_ECO']) / np.interp(speed, bp, curves['C3_ACCEL_PROFILE_NORMAL'])
  assert 0. < cap < .1
  assert env['get_boost_max'](3, speed) == pytest.approx(cap)
  boost, sm = env['AccelBoostSP'](), boost_messages(3)
  sm['carState'].vEgo = speed
  speed_scale = np.interp(speed, [1., 2.], [0., 1.])
  assert boost.update(sm, .1, 1., 1.) == pytest.approx(.1 + .01 * speed_scale)
  for _ in range(100):
    result = boost.update(sm, .1, 1., 1.)
  assert result == pytest.approx(.1 + cap * speed_scale)
  sm['modelV2'].action.shouldStop = True
  boost.update(sm, .1, 1., 1.)
  assert boost.boost == pytest.approx(max(0., cap - .05))


@pytest.mark.parametrize('profile', range(4))
@pytest.mark.parametrize('fingerprint,interceptor', [('HONDA_CIVIC', False), ('HONDA_CLARITY', True)])
def test_mvl_selects_one_boost_and_preserves_arbitration(boost_env, profile, fingerprint, interceptor):
  env, settings, reads = boost_env
  settings.enabled = True
  cp = h.car_params()
  cp.carFingerprint = fingerprint
  planner = planner_class(env)(cp, NS(enableGasInterceptor=interceptor), init_v=20.)
  sm = boost_messages(profile)
  planner.accel_boost.total_boost = .2  # Existing override boost must not stack.
  override_state = vars(planner.accel_boost).copy()
  for _ in range(80):
    planner.update(sm)
    assert planner.output_a_target <= min(planner.a_cruise, 1.)
    assert h.mvl_enabled(cp) and planner.mpc.kwargs['mvl_enabled']
  assert planner.output_a_target == pytest.approx(.1 + env['get_boost_max'](profile, 20.))
  assert vars(planner.accel_boost) == override_state
  assert reads == ['AccelBoostSP'] * 2  # Existing three-second polling, no new parameter writes.

  # Turning the option off restores donor boost, not model-only acceleration.
  settings.enabled = False
  planner.accel_boost_sp.frame = -1
  planner.update(sm)
  assert planner.output_a_target == pytest.approx(.3)
  assert planner.accel_boost_sp.total_boost == 0.
  settings.enabled = True
  planner.accel_boost_sp.frame = -1
  planner.update(sm)
  assert planner.output_a_target == pytest.approx(.11)

  sm['modelV2'].action.desiredAcceleration = 2.
  for _ in range(80):
    planner.update(sm)
  assert planner.output_a_target <= h.historical_accel_max(20., profile)
  sm['radarState'].accel, sm['radarState'].crash_cnt = -2., 3
  planner.update(sm)
  assert planner.output_a_target == pytest.approx(-2.) and planner.fcw
  sm['modelV2'].action.shouldStop = True
  planner.update(sm)
  assert planner.output_should_stop

  sm['selfdriveState'].experimentalMode = False
  planner.update(sm)
  assert planner.accel_boost_sp.boost == planner.accel_boost_sp.total_boost == planner.accel_boost.total_boost == 0.
  assert planner.output_a_target == pytest.approx(-2.)


@pytest.mark.parametrize('profile', range(4))
def test_boost_off_keeps_pre_change_mvl_outputs(boost_env, profile):
  env, _, _ = boost_env
  previous = subprocess.check_output(['git', 'show', '268018f139e82941d2e067f75cd68a7c2c0158ca:' + h.MPC + 'mvl_planner.py'], cwd=h.ROOT).decode()
  actual = planner_class(env)(h.car_params(), NS(enableGasInterceptor=True), init_v=20.)
  expected = planner_class(env, previous)(h.car_params(), NS(enableGasInterceptor=True), init_v=20.)
  rng = np.random.default_rng(42)
  for frame in range(150):
    sm = boost_messages(profile)
    sm['carState'].gasPressed = frame % 30 > 15
    sm['selfdriveState'].experimentalMode = frame % 70 < 50
    sm['modelV2'].action.desiredAcceleration = float(rng.uniform(-2., 2.))
    sm['radarState'].accel = float(rng.uniform(-2., 2.))
    actual.update(sm)
    expected.update(copy.deepcopy(sm))
    for attr in ('output_a_target', 'output_should_stop', 'a_cruise', 'fcw', 'source'):
      assert getattr(actual, attr) == getattr(expected, attr)
    assert vars(actual.accel_boost) == vars(expected.accel_boost)


def test_stock_longitudinal_does_not_apply_boost(boost_env):
  env, settings, _ = boost_env
  settings.enabled = True
  planner = planner_class(env)(h.car_params(), NS(), init_v=20.)
  planner.openpilot_longitudinal = False
  planner.accel_boost_sp.update_params()
  assert planner.apply_accel_boost(boost_messages(), .1, 1., 1.) == .1
  assert planner.accel_boost_sp.total_boost == 0.
