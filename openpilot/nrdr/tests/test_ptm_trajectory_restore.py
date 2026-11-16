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
def test_prediction_horizon_matches_former_off_for_every_model_path(timing, path, ptm, uses_plan, smooth):
  assignment, = [n for n in ast.walk(ast.parse((ROOT / path).read_text())) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "lat_delay" for t in n.targets)]
  timing.update(model=NS(lat_delay=.08, LAT_SMOOTH_SECONDS=smooth, uses_plan=uses_plan),
                LAT_SMOOTH_SECONDS=smooth, firmware_profile=object() if ptm else None)
  actual = eval(compile(ast.Expression(assignment.value), path, "eval"), timing)
  assert actual == pytest.approx(.08 + (.1 if ptm else smooth))


@pytest.mark.parametrize("path,source", [(RUNNERS[0], "plan"), (RUNNERS[0], "action"),
                                       *[(RUNNERS[1], source) for source in ("plan", "planplus", "action", "curvature", "zero")]])
@pytest.mark.parametrize("generation", [None, 9, 10, 11, 12])
@pytest.mark.parametrize("speed", [0., .3, .300001, 1., 2.49, 2.5, 7., 25.])
@pytest.mark.parametrize("smooth", [0., .05])
@pytest.mark.parametrize("ptm", [False, True])
def test_decoders_match_former_off_vectors_and_preserve_non_ptm(timing, path, source, generation, speed, smooth, ptm):
  action = load_function(path, "get_action_from_model", timing)
  sunny = path.startswith("sunnypilot")
  mlsim = generation is not None and generation >= 11
  model = NS(generation=generation, mlsim=mlsim, LAT_SMOOTH_SECONDS=smooth,
             LONG_SMOOTH_SECONDS=.3, MIN_LAT_CONTROL_SPEED=.3, constants=ModelConstants, PLANPLUS_CONTROL=1.4)
  timing["LAT_SMOOTH_SECONDS"] = smooth
  times = np.asarray(ModelConstants.T_IDXS)
  plan = np.zeros((1, 33, 15))
  plan[0, :, 11] = .1 * times ** 2 + .02 * times
  plan[0, :, 14] = .02
  plan[0, :, 3] = speed + .4 * times
  plan[0, :, 6] = .4
  output = {"plan": plan}
  if source == "action":
    output["action"] = np.array([[-.025, -.1]])
  elif source in ("curvature", "zero"):
    output["desired_curvature"] = np.array([[-.003 if source == "curvature" else 0.]])
  elif source == "planplus":
    output["planplus"] = .25 * plan
  prev = NS(desiredCurvature=.004, desiredAcceleration=.2)
  for action_time in (.155, .3, .475):
    args = (output, prev, action_time, .3, speed)
    actual = action(*((model, *args) if sunny else args), ptm_controller=ptm)
    # Independent former-OFF equations, including Sunny's generation and zero-head fallbacks.
    if source == "action":
      raw = -.025 / max(2.5 if sunny or ptm else 1., speed) ** 2
      accel = -.1
    else:
      curvature_plan = plan[0] + .4 * output["planplus"][0] if source == "planplus" else plan[0]
      horizon = max(action_time, 0. if ptm else .3)
      raw = 2 * np.interp(horizon, times, curvature_plan[:, 11]) / (max(speed, 1.) * horizon) - curvature_plan[0, 14] / max(speed, 1.)
      if source == "curvature" and not mlsim:
        raw = -.003
      accel = 2 * (np.interp(.3, times, plan[0, :, 3]) - speed) / .3 - .4
    if ptm or not sunny or (generation is not None and generation >= 10):
      tau = .1 if ptm else smooth
      alpha = 1 - np.exp(-.05 / tau) if tau else 1.
      expected = alpha * raw + (1 - alpha) * prev.desiredCurvature if speed > .3 else prev.desiredCurvature
    else:
      expected = raw
    assert actual.desiredCurvature == pytest.approx(expected, abs=1e-14)
    alpha_long = 1 - np.exp(-.05 / .3)
    assert actual.desiredAcceleration == pytest.approx(alpha_long * accel + (1 - alpha_long) * prev.desiredAcceleration)
    assert actual.shouldStop == (speed < .3 and accel < .1)
    prev = actual


@pytest.mark.parametrize("source", ["plan", "actionHead", "curvatureHead", "unknown"])
@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("legacy_mode", [None, False, True])
@pytest.mark.parametrize("ptm,maneuver", [(True, False), (False, False), (True, True), (False, True)])
def test_controlsd_matches_off_ramp_ignoring_old_logged_mode(timing, source, active, legacy_mode, ptm, maneuver):
  tree = ast.parse((ROOT / "selfdrive/controls/controlsd.py").read_text())
  block, = [n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == "self.sm.valid['lateralManeuverPlan']"]
  ramp = timing["ModelActionRamp"]()
  ramp.reset(.001)
  class Messages(dict):
    valid = {"lateralManeuverPlan": maneuver}
    updated = {"modelV2": True}
  sm = Messages(lateralManeuverPlan=NS(desiredCurvature=.008))
  model_action = NS(desiredCurvature=.006, lateralSource=source)
  if legacy_mode is not None:
    model_action.ptmTimingRestored = legacy_mode
  timing.update(self=NS(sm=sm, model_action_ramp=ramp if ptm else None, curvature=-.002),
                CC=NS(latActive=active), model_v2=NS(action=model_action))
  code = compile(ast.Module(body=[block], type_ignores=[]), "controlsd", "exec")
  for frame in range(8):
    sm.updated["modelV2"] = frame == 0
    exec(code, timing)
    expected = .008 if maneuver else (.001 + min(frame / 5., 1.) * .005 if ptm else .006)
    assert timing["new_desired_curvature"] == pytest.approx(expected if active else -.002)


@pytest.mark.parametrize("calibration", COMMAND_DELAY_ENDPOINTS)
@pytest.mark.parametrize("legacy_mode", [None, False, True])
def test_command_delay_matches_off_source_ramp_ignoring_old_mode_and_horizon(timing, calibration, legacy_mode):
  delay = load_function("nrdr/features/lateral/latcontrol_fw.py", "_command_delay", timing)
  action = NS(lateralSource="plan", lateralActionTime=.155)
  if legacy_mode is not None:
    action.ptmTimingRestored = legacy_mode
  controller = NS(firmware_profile=NS(calibration=calibration), delay_schedule=True, dt=.01,
                  model_v2=NS(action=action), cmd_delay_scale=1.)
  scale = 1.
  for source in ("plan", "actionHead", "curvatureHead", "unknown", "plan"):
    action.lateralSource = source
    for speed in np.linspace(7., 25., 120):
      action.lateralActionTime = speed / 60.  # old restoration floor must never affect command delay
      scale += np.clip((0. if source == "plan" else 1.) - scale, -.01, .01)
      assert delay(controller, speed) == pytest.approx(scale * command_delay(None, speed, calibration=calibration))
  action.ptmTimingRestored = not legacy_mode
  assert delay(controller, 7.) == 0.
  controller.model_v2 = None
  assert delay(controller, 7.) == pytest.approx(.01 * command_delay(None, 7., calibration=calibration))


@pytest.mark.parametrize("path", RUNNERS)
def test_publishers_do_not_poll_or_pass_a_restoration_mode(path):
  tree = ast.parse((ROOT / path).read_text())
  calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
  for name in ("get_action_from_model", "set_lateral_action_timing"):
    call, = [n for n in calls if getattr(n.func, "id", getattr(n.func, "attr", None)) == name]
    assert not any(k.arg == "timing_restored" for k in call.keywords)
  assert "timing_mode" not in ast.unparse(tree)
  assert "timing_params" not in ast.unparse(tree)


def test_no_runtime_path_can_read_stale_saved_or_logged_restoration():
  paths = (*RUNNERS, "sunnypilot/modeld_v2/fill_model_msg.py", "sunnypilot/jetlink_adapter/__init__.py",
           "nrdr/features/lateral/model_source.py", "nrdr/features/lateral/latcontrol_fw.py", "selfdrive/controls/controlsd.py")
  for path in paths:
    source = (ROOT / path).read_text()
    for retired in ("NrdrPtmTimingRestoration", "PtmTimingMode", "ptm_timing_restored", "timing_restored",
                    "plan_floor_command_delay", "CommandDelaySlew"):
      assert retired not in source, (path, retired)
    tree = ast.parse(source)
    assert not any(isinstance(n, ast.Attribute) and n.attr == "ptmTimingRestored" and isinstance(n.ctx, ast.Load)
                   for n in ast.walk(tree))


@pytest.mark.parametrize("ptm", [False, True])
@pytest.mark.parametrize("speed", [0., .3, .300001, 1., 2.5, 20.])
@pytest.mark.parametrize("source", ["plan", "action"])
def test_jetlink_wrapper_preserves_off_decoder_and_blendful_order(timing, ptm, speed, source):
  decoder = load_function(RUNNERS[0], "get_action_from_model", timing)
  wrap = load_function("sunnypilot/jetlink_adapter/__init__.py", "with_blendful", timing)
  plan = np.zeros((1, 33, 15))
  plan[0, :, 11] = .1 * np.asarray(ModelConstants.T_IDXS) ** 2
  output = {"plan": plan} if source == "plan" else {"action": np.array([[.025, .4]])}
  args = (output, NS(desiredCurvature=.001, desiredAcceleration=.2), .155, .3, speed)
  baseline = decoder(*args, ptm_controller=ptm)
  seen = []
  def blendful(curvature):
    seen.append(curvature)
    return .002
  actual = wrap(decoder, .3)(*args, blendful=blendful, ptm_controller=ptm)
  assert seen == [baseline.desiredCurvature]
  assert actual.desiredCurvature == baseline.desiredCurvature + (.002 if speed > .3 else 0.)
  assert (actual.desiredAcceleration, actual.shouldStop) == (baseline.desiredAcceleration, baseline.shouldStop)


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
