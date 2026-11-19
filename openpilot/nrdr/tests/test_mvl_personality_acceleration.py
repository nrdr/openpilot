"""Historical personality ceilings apply to MVL without changing its control law."""
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.tests.test_mvl_experimental_selection import messages
from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, PlannerSPDouble, car_params, definitions, environment, git_source,
  historical_accel_max, planner_modules, source,
)


@pytest.mark.parametrize("profile", range(4))
def test_cruise_curve_matches_historical_values_across_speed_range(profile):
  env = environment(LongitudinalPlannerSP=PlannerSPDouble)
  current = definitions(source(MPC + "mvl_planner.py"), env)
  for speed in np.linspace(0., 60., 121):
    # A long interval exposes the ceiling rather than the jerk transient.
    actual = (env["econ_cruise_accel"](100., speed, 0., 100.) if profile == 3 else
              current["get_cruise_accel"](100., speed, 0., 100., profile))
    assert actual == pytest.approx(historical_accel_max(speed, profile))


@pytest.mark.parametrize("profile", range(3))
def test_cruise_braking_and_jerk_match_unmodified_donor(profile):
  env = environment(LongitudinalPlannerSP=PlannerSPDouble)
  current = definitions(source(MPC + "mvl_planner.py"), env)["get_cruise_accel"]
  donor = definitions(git_source(CORE + "longitudinal_planner.py"), env)["get_cruise_accel"]
  for speed in (0., 5., 15., 25., 40.):
    for previous in (-2., -.3, 0., 1.5):
      assert current(0., speed, previous, .05, profile) == donor(0., speed, previous, .05)


@pytest.mark.parametrize("fingerprint,interceptor", [
  ("HONDA_CLARITY", True), ("HONDA_CIVIC", False), ("HONDA_CIVIC_BOSCH", False),
])
@pytest.mark.parametrize("profile", range(4))
@pytest.mark.parametrize("experimental", (False, True))
def test_routed_mvl_ceiling_and_braking(fingerprint, interceptor, profile, experimental):
  current, _ = planner_modules()
  cp = car_params()
  cp.carFingerprint = fingerprint
  planner = current["LongitudinalPlanner"](cp, NS(enableGasInterceptor=interceptor), init_v=25.)
  sm = messages(profile, experimental)
  sm["carState"].vEgo = 25.
  sm["carState"].vCruise = 130.
  sm["modelV2"].action.desiredAcceleration = 2.
  sm["modelV2"].action.shouldStop = False
  sm["radarState"].accel = 2.
  planner.accel_boost.total_boost = .2

  for _ in range(80):
    planner.update(sm)
    assert 0. <= planner.output_a_target <= historical_accel_max(25., profile) + 1e-12
  assert planner.output_a_target == pytest.approx(historical_accel_max(25., profile))

  # Neither the curve nor its jerk ramp can delay the separate lead-braking candidate.
  sm["radarState"].accel = -2.
  sm["radarState"].crash_cnt = 3
  planner.update(sm)
  assert planner.output_a_target == pytest.approx(-2.)
  assert planner.fcw
  if experimental:
    sm["modelV2"].action.desiredAcceleration = -2.8
    sm["modelV2"].action.shouldStop = True
    planner.update(sm)
    assert planner.output_a_target == pytest.approx(-2.8)
    assert planner.output_should_stop


def test_personality_change_uses_existing_jerk_ramp():
  current, _ = planner_modules()
  planner = current["LongitudinalPlanner"](car_params(), NS(), init_v=25.)
  sm = messages(0, False)
  sm["carState"].vEgo = 25.
  sm["carState"].vCruise = 130.
  sm["radarState"].accel = 2.
  for _ in range(80):
    planner.update(sm)
  assert planner.output_a_target == pytest.approx(.8)

  sm["selfdriveState"].personality = 2
  planner.update(sm)
  assert planner.output_a_target == pytest.approx(.8 - .8 * .05)
  for _ in range(20):
    planner.update(sm)
  assert planner.output_a_target == pytest.approx(.42)
