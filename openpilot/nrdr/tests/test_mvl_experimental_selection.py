"""Manual ACC/Experimental selection must control the MVL model candidate."""
import copy
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.tests.test_mvl_host_parity import (
  SOURCE, STATE, car_params, planner_messages, planner_modules,
)


def messages(profile, experimental):
  sm = planner_messages(1, np.random.default_rng(109), profile)
  sm['carState'].vEgo = 20.
  sm['carState'].vCruise = 100.
  sm['carState'].aEgo = 0.
  sm['carState'].standstill = False
  sm['carState'].gasPressed = False
  sm['controlsState'].longControlState = STATE.pid
  sm['controlsState'].forceDecel = False
  sm['selfdriveState'].enabled = True
  sm['selfdriveState'].experimentalMode = experimental
  sm['radarState'].accel = 1.
  sm['radarState'].crash_cnt = 0
  sm['modelV2'].action.desiredAcceleration = -2.5
  sm['modelV2'].action.shouldStop = True
  return sm


@pytest.mark.parametrize('profile', range(4))
@pytest.mark.parametrize('interceptor', [False, True])
def test_off_excludes_model_acceleration_stop_and_boost_on_every_tick(profile, interceptor):
  current, _ = planner_modules()
  cls = current['LongitudinalPlanner']
  planners = [cls(car_params(), NS(enableGasInterceptor=interceptor), init_v=20.) for _ in range(2)]
  for frame in range(180):
    sm = messages(profile, False)
    # Neither accelerator overrides nor arbitrary model output may influence
    # ACC-only selection. Lead deceleration and forced slowdown remain active.
    sm['carState'].gasPressed = frame % 10 > 3
    sm['radarState'].accel = -1.2 if 20 <= frame < 50 else 1.
    sm['radarState'].crash_cnt = 3 if frame == 40 else 0
    sm['controlsState'].forceDecel = frame >= 60
    neutral = copy.deepcopy(sm)
    neutral['modelV2'].action.desiredAcceleration = 2.
    neutral['modelV2'].action.shouldStop = False
    for planner, msg in zip(planners, (sm, neutral), strict=True):
      planner.update(msg)
      assert planner.mpc.source != SOURCE.e2e
      assert not planner.output_should_stop
      assert planner.accel_boost.total_boost == 0.
    actual, expected = planners
    assert actual.output_a_target == expected.output_a_target
    assert actual.v_desired_filter.x == expected.v_desired_filter.x
    assert actual.fcw == (frame == 40)
    if 20 <= frame < 50:
      assert actual.output_a_target == pytest.approx(-1.2)
    if frame >= 60:
      assert actual.seen_cruise_target == 0.
    if frame >= 150:
      assert actual.output_a_target < 0.


@pytest.mark.parametrize('profile', range(4))
def test_on_off_on_takes_effect_without_recreating_planner(profile):
  current, _ = planner_modules()
  planner = current['LongitudinalPlanner'](car_params(), NS(), init_v=20.)
  sm = messages(profile, True)
  planner.update(sm)
  assert planner.output_a_target == -2.5
  assert planner.output_should_stop and planner.mpc.source == SOURCE.e2e
  planner.accel_boost.total_boost = .2
  planner.accel_boost.boost_eligible = True

  sm['selfdriveState'].experimentalMode = False
  planner.update(sm)
  assert planner.output_a_target >= 0.
  assert not planner.output_should_stop and planner.mpc.source != SOURCE.e2e
  assert planner.accel_boost.total_boost == 0.
  assert not planner.accel_boost.boost_eligible

  sm['selfdriveState'].experimentalMode = True
  planner.update(sm)
  assert planner.output_a_target == -2.5
  assert planner.output_should_stop and planner.mpc.source == SOURCE.e2e


@pytest.mark.parametrize('profile', range(4))
def test_off_keeps_radar_stop_request(profile):
  current, _ = planner_modules()
  planner = current['LongitudinalPlanner'](car_params(), NS(), init_v=.1)
  sm = messages(profile, False)
  sm['carState'].vEgo = .1
  sm['radarState'].accel = 0.
  sm['modelV2'].action.desiredAcceleration = 2.
  sm['modelV2'].action.shouldStop = False
  planner.update(sm)
  assert planner.output_a_target == 0.
  assert planner.output_should_stop
  assert planner.mpc.source == SOURCE.lead0
