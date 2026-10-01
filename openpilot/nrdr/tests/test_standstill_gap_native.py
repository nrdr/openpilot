"""Native solver/planner acceptance; no CAN output or vehicle communication."""
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest

if sys.platform == "win32":
  pytest.skip("Native acados acceptance runs on Linux", allow_module_level=True)

from openpilot.cereal import custom, log
from opendbc.car.structs import car
from openpilot.common.params import Params
from openpilot.nrdr.params.snapshots import get_live_params
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP
from openpilot.nrdr.tests.test_longitudinal_mpc import model_lead, radar_lead


@pytest.mark.parametrize("nrdr_enabled", [False, True])
def test_solver_gap_does_not_modify_logged_leads_or_fcw_distance(nrdr_enabled):
  radar = NS(leadOne=radar_lead(distance=8, speed=0), leadTwo=radar_lead(present=False))
  solvers = [LongitudinalMpc(nrdr_enabled=nrdr_enabled) for _ in range(2)]
  for solver, gap in zip(solvers, (0.0, 2.0), strict=True):
    solver.set_cur_state(0.0, 0.0)
    solver.update(radar, extra_stop_distance=gap)
    assert solver.solution_status == 0
  a, b = solvers
  np.testing.assert_array_equal(a.lead_xv_0, b.lead_xv_0)
  assert a.crash_cnt == b.crash_cnt == 0
  np.testing.assert_allclose(a.params[:, 2] - b.params[:, 2], 2.0 if nrdr_enabled else 0.0)
  if not nrdr_enabled:
    np.testing.assert_array_equal(a.x_sol, b.x_sol)
    np.testing.assert_array_equal(a.u_sol, b.u_sol)


def simulate_stop(monkeypatch, extra, e2e, lead_slot):
  params = Params()
  params.put("NrdrStandstillGapExtra", float(extra), block=True)
  params.put("NrdrCruiseMismatchCorrection", 100.0, block=True)
  params.put("NrdrCruiseOverspeedAllowance", 0, block=True)
  live = get_live_params("plannerd")
  live.refresh_all()
  # Isolate the tested planner from optional map/remote services, not from its
  # real lead policy, compiled MPC, stop decision, or E2E candidate arbitration.
  monkeypatch.setattr(LongitudinalPlannerSP, "__init__", lambda *_: None)
  monkeypatch.setattr(LongitudinalPlannerSP, "update", lambda *_: None)
  monkeypatch.setattr(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a))
  monkeypatch.setattr(LongitudinalPlannerSP, "is_e2e", lambda self, sm: e2e)
  cp = car.CarParams.new_message()
  cp.brand = "honda"
  cp.carFingerprint = "HONDA_CLARITY"
  cp.openpilotLongitudinalControl = True
  cp.steerRatio, cp.wheelbase = 16.5, 2.75
  cp.longitudinalActuatorDelay = 0.3
  cp.deprecated.vEgoStopping = 0.5
  planner = LongitudinalPlanner(cp, custom.CarParamsSP.new_message(), init_v=8.0)
  speed, accel, distance = 8.0, 0.0, 0.0
  lead_position = 50.0
  speeds, gaps = [], []
  for frame in range(900):
    # Model keeps asking to accelerate, including at standstill; MPC must
    # continue to limit it and prevent creeping away the selected clearance.
    leads = [radar_lead(present=i == lead_slot, distance=lead_position - distance, speed=0.0) for i in range(2)]
    model = NS(leadsV3=[model_lead(speed=0.0), model_lead(speed=0.0)],
               meta=NS(disengagePredictions=NS(gasPressProbs=[1.0, 1.0])),
               action=NS(desiredAcceleration=1.0, shouldStop=False),
               velocity=NS(x=[]), acceleration=NS(x=[]))
    sm = {'carState': NS(vEgo=speed, aEgo=accel, standstill=speed == 0.0, vCruise=36.0, steeringAngleDeg=0.0),
          'carControl': NS(orientationNED=[0.0, 0.0, 0.0], actuators=NS(accel=accel)),
          'controlsState': NS(forceDecel=False, longControlState=0 if frame == 0 else 1),
          'selfdriveState': NS(enabled=frame > 0, personality=log.LongitudinalPersonality.standard, experimentalMode=e2e),
          'vehicleParameters': NS(angleOffsetDeg=0.0), 'modelV2': model,
          'radarState': NS(leadOne=leads[0], leadTwo=leads[1])}
    planner.update(sm)
    assert planner.mpc.solution_status == 0
    assert planner.nrdr.standstill_gap_extra == extra
    accel = float(planner.output_a_target)
    if planner.output_should_stop:
      accel = min(accel, -0.5)  # Same idealized brake hold as upstream maneuver plant.
    speed = max(0.0, speed + accel * 0.05)
    distance += speed * 0.05
    speeds.append(speed)
    gaps.append(lead_position - distance)
    assert np.isfinite(accel) and gaps[-1] > 0.4
  assert max(speeds[-200:]) < 0.01
  assert max(gaps[-200:]) - min(gaps[-200:]) < 0.01
  return gaps[-1]


@pytest.mark.parametrize("e2e", [False, True])
@pytest.mark.parametrize("lead_slot", [0, 1])
def test_final_stopped_clearance_remains_larger_after_creeping(monkeypatch, e2e, lead_slot):
  baseline = simulate_stop(monkeypatch, 0.0, e2e, lead_slot)
  enlarged = simulate_stop(monkeypatch, 2.0, e2e, lead_slot)
  assert enlarged - baseline == pytest.approx(2.0, abs=0.3), (baseline, enlarged)
