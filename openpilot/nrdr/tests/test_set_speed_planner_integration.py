"""Set Speed Assist against the immediate pre-PR planner, with a recording MPC."""
import copy
import subprocess
from types import SimpleNamespace as NS

import numpy as np
import pytest

pytest.importorskip("msgq")  # Real controller imports native messaging; run this suite on the comma/Linux.

from openpilot.cereal import log
from opendbc.car.honda.tests.test_civic_pcm import interface
from opendbc.car.honda.values import CAR
from openpilot.nrdr.tests.test_sunny_accel_boost import boost_env as boost_env, h, messages, planners, PATHS


@pytest.fixture(scope='module')
def before_pr():
  return {path: subprocess.check_output(['git', 'show', 'd8afee6230:' + path], cwd=h.ROOT).decode()
          for path in (h.CORE + 'longitudinal_planner.py', h.SUNNY + 'longitudinal_planner.py')}


def full_messages(frame, e2e=0., mpc=1., personality=1):
  sm = messages(10_000_000_000 + frame * 50_000_000, e2e, mpc, personality)
  sm['modelV2'].velocity = NS(x=[20.] * 33)
  sm['modelV2'].orientationRate = NS(z=[0.] * 33)
  sm['modelV2'].meta.laneChangeState = log.LaneChangeState.off
  sm['radarState'].leadOne = NS(present=False)
  sm['controlsState'].curvature = 0.
  return sm


@pytest.mark.parametrize('car,mode,interceptor', PATHS)
@pytest.mark.parametrize('personality', range(4))
def test_default_off_matches_immediate_pre_pr(boost_env, before_pr, car, mode, interceptor, personality):
  ci, _ = interface(car, interceptor=interceptor, pcm_mode=mode)
  actual, baseline = planners(boost_env, before_pr, ci.CP, ci.CP_SP, enabled=True, set_speed=False)
  rng = np.random.default_rng(33)
  for frame in range(120):
    sm = full_messages(frame, float(rng.uniform(-2., 1.)), float(rng.uniform(-3., 2.)), personality)
    sm['selfdriveState'].experimentalMode = frame % 40 < 20
    sm['controlsState'].longControlState = h.STATE.off if frame % 13 == 0 else h.STATE.pid
    sm['modelV2'].action.shouldStop = frame % 7 == 0
    actual.update(copy.deepcopy(sm))
    baseline.update(copy.deepcopy(sm))
    for key in ('output_a_target', 'output_should_stop', 'a_cruise', 'fcw', 'allow_throttle'):
      assert getattr(actual, key) == getattr(baseline, key), (frame, key)


def test_enabled_assist_keeps_mpc_braking_and_stop_requests(boost_env, before_pr):
  ci, _ = interface(CAR.HONDA_CLARITY, interceptor=True)
  actual, _ = planners(boost_env, before_pr, ci.CP, ci.CP_SP, enabled=True, set_speed=True)
  for frame in range(200):
    actual.update(full_messages(frame))
  assert actual.e2e_set_speed.lift > 0.
  assert actual.accel_boost_sp.total_boost == 0.
  sm = full_messages(200, mpc=-2.)
  sm['modelV2'].action.shouldStop = True
  actual.update(sm)
  assert actual.output_a_target <= -2.
  assert actual.output_should_stop
  sm = full_messages(201)
  sm['controlsState'].longControlState = h.STATE.off
  actual.update(sm)
  assert actual.e2e_set_speed.lift == 0.


def test_disabling_assist_does_not_stack_boost_during_fadeout(boost_env, before_pr):
  ci, _ = interface(CAR.HONDA_CLARITY, interceptor=True)
  actual, _ = planners(boost_env, before_pr, ci.CP, ci.CP_SP, enabled=True, set_speed=True)
  for frame in range(200):
    actual.update(full_messages(frame))
  actual.e2e_set_speed.params.values['ExperimentalModeSetSpeed'] = False
  actual.e2e_set_speed.frame = actual.e2e_set_speed.params_frames - 1
  actual.update(full_messages(200))
  assert not actual.e2e_set_speed.enabled and actual.e2e_set_speed.lift > 0.
  assert actual.accel_boost_sp.total_boost == 0.


def test_curve_correction_gating_and_mpc_priority(boost_env, before_pr):
  from openpilot.nrdr.features.longitudinal.curve_speed import CurveSpeed
  ci, _ = interface(CAR.HONDA_CLARITY, interceptor=True)
  actual, _ = planners(boost_env, before_pr, ci.CP, ci.CP_SP, enabled=True, set_speed=False)
  actual.curve_speed = CurveSpeed(.05)
  def frame(i, mpc=1.):
    sm = full_messages(i, .4, mpc)
    sm['vehicleParameters'].roll, sm['vehicleParameters'].valid = 0., True
    sm['modelV2'].position = NS(t=np.linspace(0., 8., 33))
    sm['modelV2'].orientationRate.z = [.4] * 33
    return sm
  for i in range(30):
    actual.update(frame(i))
  assert actual.output_a_target < -1. and actual.curve_speed.correction > 1.
  sm = frame(30, mpc=-2.5)
  sm['modelV2'].action.shouldStop = True
  actual.update(sm)
  assert actual.output_should_stop and actual.output_a_target <= -2.5
  for i, (key, field, value) in enumerate((
      ('selfdriveState', 'experimentalMode', False), ('carControl', 'longActive', False), ('carState', 'gasPressed', True),
      ('carState', 'brakePressed', True), ('vehicleParameters', 'valid', False), ('controlsState', 'longControlState', h.STATE.off),
      ('override', '', True), ('stale', '', True))):
    actual.update(frame(31+2*i))
    assert actual.curve_speed.correction > 0.
    sm = frame(32+2*i)
    if key == 'override':
      sm['carControl'].cruiseControl.override = True
    elif key == 'stale':
      sm.valid = False
    else:
      setattr(sm[key], field, value)
    actual.update(sm)
    assert actual.curve_speed.correction == 0.
