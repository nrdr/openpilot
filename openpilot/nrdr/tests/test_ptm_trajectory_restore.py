"""Offline timing regression checks without loading model hardware or native Params."""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.features.lateral import lane_change_tuning as lane_change
from openpilot.nrdr.features.lateral.yaw_control_timing import COMMAND_DELAY_ENDPOINTS, command_delay
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py")


def load_function(path, name, env):
  node, = [n for n in ast.walk(ast.parse((ROOT / path).read_text())) if isinstance(n, ast.FunctionDef) and n.name == name]
  exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), env)
  return env[name]


@pytest.fixture
def timing():
  env = {"np": np, "DT_CTRL": .01, "DT_MDL": .05, "ModelConstants": ModelConstants, "Plan": Plan,
         "log": NS(ModelDataV2=NS(Action=NS)), "LAT_SMOOTH_SECONDS": 0., "LONG_SMOOTH_SECONDS": .3,
         "MIN_LAT_CONTROL_SPEED": .3, "command_delay": command_delay}
  for path in ("selfdrive/controls/lib/drive_helpers.py", "nrdr/features/lateral/model_source.py"):
    tree = ast.parse((ROOT / path).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, "exec"), env)
  load_function("sunnypilot/modeld_v2/fill_model_msg.py", "get_curvature_from_output", env)
  return env


@pytest.mark.parametrize("names,mlsim,expected", [
  ({"plan"}, False, True), ({"plan"}, True, True),
  ({"plan", "desired_curvature"}, True, True),  # inherited Sunny generation-11+ behavior
  ({"plan", "desired_curvature"}, False, False),
  ({"plan", "desired_curvature", "action"}, True, False),
  ({"plan", "action"}, False, False),
])
def test_declared_outputs_choose_the_horizon(timing, names, mlsim, expected):
  assert timing["model_uses_plan"](names, mlsim) is expected


@pytest.mark.parametrize("path", RUNNERS)
@pytest.mark.parametrize("ptm", [False, True])
@pytest.mark.parametrize("uses_plan", [False, True])
@pytest.mark.parametrize("smooth", [0., .05, .2])
def test_prediction_horizon_matches_the_model_path(timing, path, ptm, uses_plan, smooth):
  assignment, = [n for n in ast.walk(ast.parse((ROOT / path).read_text())) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "lat_delay" for t in n.targets)]
  timing.update(model=NS(lat_delay=.08, LAT_SMOOTH_SECONDS=smooth, uses_plan=uses_plan),
                LAT_SMOOTH_SECONDS=smooth, firmware_profile=object() if ptm else None)
  actual = eval(compile(ast.Expression(assignment.value), path, "eval"), timing)
  assert actual == pytest.approx(.08 + (.1 if ptm and not uses_plan else smooth))


@pytest.mark.parametrize("path", RUNNERS)
@pytest.mark.parametrize("generation", [9, 10, 11, 12])
@pytest.mark.parametrize("speed", [.2, 7., 25.])
@pytest.mark.parametrize("smooth", [0., .05])
def test_trajectory_decoder_returns_to_ordinary_model_processing(timing, path, generation, speed, smooth):
  action = load_function(path, "get_action_from_model", timing)
  model = NS(generation=generation, mlsim=generation >= 11, LAT_SMOOTH_SECONDS=smooth,
             LONG_SMOOTH_SECONDS=.3, MIN_LAT_CONTROL_SPEED=.3, constants=ModelConstants, PLANPLUS_CONTROL=1.)
  timing["LAT_SMOOTH_SECONDS"] = smooth
  plan = np.zeros((1, 33, 15))
  plan[0, :, 11] = .1 * np.asarray(ModelConstants.T_IDXS) ** 2
  plan[0, :, 3] = speed
  output = {"plan": plan}
  if generation >= 11 and path.startswith("sunnypilot"):
    output["desired_curvature"] = np.array([[.09]])  # still deliberately bypassed
  prev = NS(desiredCurvature=.004, desiredAcceleration=.2)
  args = (output, prev, .155, .3, speed)
  if path.startswith("sunnypilot"):
    args = (model, *args)
  normal, ptm = action(*args), action(*args, ptm_controller=True)
  assert vars(ptm) == vars(normal)
  if speed > .3 and smooth == 0:
    # Read heading at .3 s, rescale to .155 s; do not read the earlier heading directly.
    expected = 2 * np.interp(.3, ModelConstants.T_IDXS, plan[0, :, 11]) / (.3 * speed)
    assert ptm.desiredCurvature == pytest.approx(expected)


@pytest.mark.parametrize("path", RUNNERS)
def test_action_head_keeps_ptm_smoothing_and_low_speed_divisor(timing, path):
  action = load_function(path, "get_action_from_model", timing)
  model = NS(generation=12, mlsim=True, LAT_SMOOTH_SECONDS=0., LONG_SMOOTH_SECONDS=.3, MIN_LAT_CONTROL_SPEED=.3)
  output = {"action": np.array([[.025, .4]])}
  prev = NS(desiredCurvature=.001, desiredAcceleration=.2)
  args = (output, prev, .275, .3, 1.)
  if path.startswith("sunnypilot"):
    args = (model, *args)
  actual = action(*args, ptm_controller=True)
  assert actual.desiredCurvature == pytest.approx(timing["smooth_value"](.025 / 2.5 ** 2, .001, .1))
  assert actual.desiredAcceleration == pytest.approx(timing["smooth_value"](.4, .2, .3))


def test_direct_curvature_head_keeps_ptm_smoothing(timing):
  action = load_function(RUNNERS[1], "get_action_from_model", timing)
  model = NS(generation=9, mlsim=False, LAT_SMOOTH_SECONDS=0., LONG_SMOOTH_SECONDS=.3,
             MIN_LAT_CONTROL_SPEED=.3, constants=ModelConstants, PLANPLUS_CONTROL=1.)
  output = {"plan": np.zeros((1, 33, 15)), "desired_curvature": np.array([[.003]])}
  actual = action(model, output, NS(desiredCurvature=.001, desiredAcceleration=0.), .275, .3, 20., ptm_controller=True)
  assert actual.desiredCurvature == pytest.approx(timing["smooth_value"](.003, .001, .1))


@pytest.mark.parametrize("calibration", COMMAND_DELAY_ENDPOINTS)
def test_plan_delay_compensation_and_return_to_head_calibration(timing, calibration):
  delay = load_function("nrdr/features/lateral/latcontrol_fw.py", "_command_delay", timing)
  model = NS(action=NS(lateralSource="plan", lateralActionTime=.155))
  controller = NS(firmware_profile=NS(calibration=calibration), delay_schedule=True,
                  model_v2=model, cmd_delay_slew=timing["CommandDelaySlew"](.01))
  assert delay(controller, 7.) == pytest.approx(.145)
  model.action.lateralActionTime = .375
  values = [.145] + [delay(controller, 25.) for _ in range(100)]
  assert values[-1] == 0.
  assert max(abs(np.diff(values))) <= .003 + 1e-12
  model.action.lateralSource = "actionHead"
  values = [0.] + [delay(controller, 7.) for _ in range(100)]
  assert values[-1] == pytest.approx(command_delay(None, 7., calibration=calibration))
  assert max(abs(np.diff(values))) <= .003 + 1e-12
  model.action.lateralSource, model.action.lateralActionTime = "plan", 0.
  assert delay(controller, 7.) == values[-1]  # missing horizon uses calibration, not zero


@pytest.mark.parametrize("source", ["plan", "actionHead", "curvatureHead"])
@pytest.mark.parametrize("active", [False, True])
def test_controlsd_holds_trajectory_requests_but_still_ramps_heads(timing, source, active):
  tree = ast.parse((ROOT / "selfdrive/controls/controlsd.py").read_text())
  block, = [n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == "self.sm.valid['lateralManeuverPlan']"]
  ramp = timing["ModelActionRamp"]()
  ramp.reset(.001)
  timing.update(self=NS(sm=NS(valid={"lateralManeuverPlan": False}, updated={"modelV2": True}),
                        model_action_ramp=ramp, curvature=-.002), CC=NS(latActive=active),
                model_v2=NS(action=NS(desiredCurvature=.006, lateralSource=source)))
  code = compile(ast.Module(body=[block], type_ignores=[]), "controlsd", "exec")
  exec(code, timing)
  expected = (.006 if source == "plan" else .001) if active else -.002
  assert timing["new_desired_curvature"] == expected
  if source == "plan":
    assert ramp.output == expected  # no stale interpolation when a head resumes


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("saved_reduction", [0., 3., 5., 100.])
def test_lane_change_hook_cannot_change_request_or_geometry(monkeypatch, enabled, saved_reduction):
  monkeypatch.setattr(lane_change, "active_model_supports_optimized_lane_changes", lambda: True)
  env = {"LaneChangeEntry": lane_change.LaneChangeEntry, "shape_lane_change_curvature": lane_change.shape_lane_change_curvature}
  hook = load_function("nrdr/hooks/controlsd.py", "lane_change_request", env)
  settings = {"NrdrOptimizedLaneChanges": enabled, "NrdrLaneChangeEntrySrReduction": saved_reduction}
  # No geometry methods supplied: any geometry access would fail this test.
  selection = NS(available=True, effective_label="PTM (Auto)")
  controls = NS(CP=NS(brand="honda"), steer_ratio_latch=NS(selection=selection), VM=NS(sR=17.45),
                nrdr_lane_change_entry=lane_change.LaneChangeEntry(), nrdr_lateral_snapshot=settings,
                sm=NS(valid={"lateralManeuverPlan": False}, all_checks=lambda _: True),
                nrdr_live_params=NS(record_applied_settings=lambda *a, **kw: None))
  cs = NS(steeringPressed=False, steeringAngleDeg=30., vEgo=20.)
  for state in (0, 1, 2, 3, 0):
    model = NS(meta=NS(laneChangeState=NS(raw=state), laneChangeDirection=NS(raw=1)))
    for _ in range(120):
      assert hook(controls, cs, model, NS(roll=.01), .003, True, .01) == .003
  assert controls.VM.sR == 17.45
  assert settings["NrdrLaneChangeEntrySrReduction"] == saved_reduction
