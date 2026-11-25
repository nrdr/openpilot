"""Native acados MVL parity acceptance; no CAN, Params writes, or car connection.

Run in the parent's isolated Linux/C4 staging checkout, never as a live process.
Uses the same pinned references as test_mvl_host_parity.py.
"""
import copy
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest

if sys.platform == "win32":
  pytest.skip("Native acados acceptance runs in isolated Linux staging", allow_module_level=True)

from opendbc.car.honda.values import HondaFlags
from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.longcontrol import LongControl
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc, mvl_planner
from openpilot.sunnypilot.selfdrive.controls.lib import longitudinal_planner as sp_planner
from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, constant, definitions, donor_with_personality_limits, git_source, historical_accel_max,
)
from openpilot.nrdr.tests.test_mvl_cruise_targets import IsolatedTargetParams


@pytest.fixture(autouse=True)
def isolated_target_settings(monkeypatch):
  # Keep real SCC/resolver/NRDR SLA constructors and update methods. Only their
  # Params boundary is isolated; disabled target features preserve donor parity.
  from openpilot.sunnypilot.selfdrive.car import cruise_ext
  from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control import map_controller, vision_controller
  from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import speed_limit_assist, speed_limit_resolver
  settings = IsolatedTargetParams()
  for module in (cruise_ext, map_controller, vision_controller, speed_limit_assist, speed_limit_resolver):
    monkeypatch.setattr(module, "Params", lambda *_args: settings)
  yield settings


def target_context(sm):
  """Messages consumed by restored SCC/SLA, with no map/car speed limit."""
  sm["carState"].vCruiseCluster = sm["carState"].vCruise
  sm["carControl"] = NS(enabled=sm["selfdriveState"].enabled, cruiseControl=NS(override=False))
  sm["carStateSP"] = NS(speedLimit=0.)
  sm["gpsLocation"] = NS(unixTimestampMillis=-1e12)
  sm["liveMapDataSP"] = NS(speedLimitValid=False, speedLimitAheadValid=False)
  return sm


def donor_mpc():
  namespace = {"__name__": "_pinned_mvl_native_mpc", "__file__": long_mpc.__file__}
  exec(compile(git_source(MPC + "long_mpc.py"), "<pinned donor MPC>", "exec"), namespace)
  return namespace["LongitudinalMpc"]


def cp():
  params = car.CarParams.new_message()
  params.brand = "honda"
  params.flags = int(HondaFlags.MVL_LONGITUDINAL)
  params.openpilotLongitudinalControl = True
  params.longitudinalActuatorDelay = .3
  params.stopAccel = -.5
  params.longitudinalTuning.kiBP = [0., 10., 30.]
  params.longitudinalTuning.kiV = [1.2, .8, .5]
  return params


def lead(present=True, distance=45., speed=15., accel=0.):
  return NS(present=present, dRel=distance, vLead=speed, aLeadK=accel, aLeadTau=1.5, modelProb=.99,
            radar=True, deprecated=NS(fcw=False), vLeadK=99., radarTrackId=1)


@pytest.mark.parametrize("profile", [0, 1, 2])
def test_native_mpc_matches_pinned_donor(profile):
  actual, expected = long_mpc.LongitudinalMpc(mvl_enabled=True, nrdr_enabled=True), donor_mpc()()
  for frame in range(100):
    radar = NS(leadOne=lead(present=frame > 5, distance=45. - .2 * frame, speed=15., accel=-.5 if frame > 30 else 0.),
               leadTwo=lead(present=frame > 60, distance=20., speed=14.))
    for solver in (actual, expected):
      solver.set_cur_state(20. - frame * .03, -.3)
      solver.set_weights(frame > 0, profile)
    actual.update(radar, profile, model=object(), v_cruise=99., extra_stop_distance=5.)
    expected.update(radar, profile)
    assert actual.solution_status == expected.solution_status == 0
    np.testing.assert_array_equal(actual.params, expected.params)
    np.testing.assert_allclose(actual.x_sol, expected.x_sol, atol=1e-10, rtol=0.)
    np.testing.assert_allclose(actual.u_sol, expected.u_sol, atol=1e-10, rtol=0.)
    assert actual.source == expected.source
    assert actual.crash_cnt == expected.crash_cnt


@pytest.mark.parametrize("profile", [0, 1, 2])
def test_native_planner_and_longcontrol_match_donor_with_historical_ceilings(monkeypatch, profile):
  # Advisory alert I/O is irrelevant to acceleration parity. Do not read/write
  # the device Params namespace while running the isolated acceptance suite.
  monkeypatch.setattr(sp_planner, "E2EAlertsHelper", lambda: NS(update=lambda *_: None))
  env = vars(mvl_planner).copy()
  env["historical_accel_max"] = historical_accel_max
  env["V_CRUISE_MAX"] = constant(git_source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")
  env["LongitudinalMpc"] = donor_mpc()
  expected_cls = definitions(donor_with_personality_limits(git_source(CORE + "longitudinal_planner.py")), env)["LongitudinalPlanner"]
  params, params_sp = cp(), custom.CarParamsSP.new_message()
  actual, expected = LongitudinalPlanner(params, params_sp, init_v=20.), expected_cls(params, params_sp, init_v=20.)
  import openpilot.selfdrive.controls.lib.longcontrol as controller_module
  donor_controller = definitions(git_source(CORE + "longcontrol.py"), vars(controller_module))["LongControl"]
  controllers = LongControl(params, params_sp), donor_controller(params, params_sp)
  for frame in range(120):
    speed = max(0., 20. - .15 * frame)
    cs = NS(vEgo=speed, aEgo=-.3, standstill=False, vCruise=100., gasPressed=15 < frame < 35,
            brakePressed=False, cruiseState=NS(standstill=False))
    sm = {"carState": cs, "controlsState": NS(forceDecel=frame > 100, longControlState=0 if frame == 0 else 1),
          "selfdriveState": NS(enabled=frame > 0, personality=profile, experimentalMode=True),
          "modelV2": NS(action=NS(desiredAcceleration=.5, shouldStop=False)),
          "radarState": NS(leadOne=lead(distance=40., speed=10.), leadTwo=lead(present=False))}
    target_context(sm)
    for planner in (actual, expected):
      planner.update(sm)
    assert actual.mpc.solution_status == expected.mpc.solution_status == 0
    assert actual.output_a_target == pytest.approx(expected.output_a_target, abs=1e-10)
    assert actual.output_should_stop == expected.output_should_stop
    assert actual.fcw == expected.fcw
    outputs = [controller.update(True, cs, planner.output_a_target, planner.output_should_stop, (-3.5, 2.))
               for controller, planner in zip(controllers, (actual, expected), strict=True)]
    assert outputs[0] == pytest.approx(outputs[1], abs=1e-10)


@pytest.mark.parametrize("profile", [0, 1, 2])
def test_actual_imports_high_speed_donor_ceiling(monkeypatch, profile):
  from openpilot.selfdrive.car import cruise
  assert cruise.V_CRUISE_MAX == 169  # Leave the host/non-MVL selector untouched.
  donor_maximum = constant(git_source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")
  assert mvl_planner.V_CRUISE_MAX == donor_maximum == 145
  monkeypatch.setattr(sp_planner, "E2EAlertsHelper", lambda: NS(update=lambda *_: None))
  planner = LongitudinalPlanner(cp(), custom.CarParamsSP.new_message(), init_v=44.)
  sm = {"carState": NS(vEgo=44., aEgo=0., standstill=False, vCruise=160., gasPressed=False),
        "controlsState": NS(forceDecel=False, longControlState=1),
        "selfdriveState": NS(enabled=True, personality=profile, experimentalMode=False),
        "modelV2": NS(action=NS(desiredAcceleration=2., shouldStop=False)),
        "radarState": NS(leadOne=lead(present=False), leadTwo=lead(present=False))}
  target_context(sm)
  planner.update(sm)
  assert planner.mpc.solution_status == 0
  assert planner.output_v_target == pytest.approx(donor_maximum / 3.6)
  assert planner.a_cruise == pytest.approx(-.03)
  assert planner.output_a_target <= -.03


@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("pcm_speed", [False, True])
@pytest.mark.parametrize("experimental", [False, True])
def test_native_cruise_standstill_initialization_and_minimums(metric, pcm_speed, experimental):
  from openpilot.selfdrive.car.cruise import VCruiseHelper
  helper = VCruiseHelper(cp(), custom.CarParamsSP.new_message(pcmCruiseSpeed=pcm_speed))
  cs = car.CarState.new_message(vEgo=0., standstill=True, cruiseState={"available": True, "standstill": True})
  helper.initialize_v_cruise(cs, experimental)
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == 40.
  assert helper.nrdr is None and isinstance(helper.params, IsolatedTargetParams)
  for frame in range(700):
    cs.buttonEvents = [{"type": "decelCruise", "pressed": True}] if frame == 3 else []
    helper.update_v_cruise(cs, True, metric)
    assert helper.v_cruise_kph <= 145.
  assert helper.v_cruise_kph == (8 if pcm_speed else 30 if metric else 20)


@pytest.mark.parametrize("profile", range(4))
@pytest.mark.parametrize("lead_present", [False, True])
def test_native_experimental_off_excludes_model_after_live_switch(monkeypatch, profile, lead_present):
  monkeypatch.setattr(sp_planner, "E2EAlertsHelper", lambda: NS(update=lambda *_: None))
  planners = [LongitudinalPlanner(cp(), custom.CarParamsSP.new_message(), init_v=20.) for _ in range(2)]
  for frame in range(60):
    experimental = frame < 20
    sm = {"carState": NS(vEgo=20., aEgo=0., standstill=False, vCruise=100., gasPressed=False),
          "controlsState": NS(forceDecel=False, longControlState=1),
          "selfdriveState": NS(enabled=True, personality=profile, experimentalMode=experimental),
          "modelV2": NS(action=NS(desiredAcceleration=-3.5, shouldStop=True)),
          "radarState": NS(leadOne=lead(present=lead_present, distance=40., speed=10.), leadTwo=lead(present=False))}
    target_context(sm)
    neutral = copy.deepcopy(sm)
    if not experimental:
      neutral["modelV2"].action.desiredAcceleration = 2.
      neutral["modelV2"].action.shouldStop = False
    for planner, msg in zip(planners, (sm, neutral), strict=True):
      planner.update(msg)
      assert planner.mpc.solution_status == 0
      if not experimental:
        assert planner.mpc.source != long_mpc.LongitudinalPlanSource.e2e
        assert not planner.output_should_stop
        assert planner.accel_boost.total_boost == 0.
    assert planners[0].output_a_target == pytest.approx(planners[1].output_a_target, abs=1e-10)
    assert planners[0].output_should_stop == planners[1].output_should_stop
    assert planners[0].fcw == planners[1].fcw
