"""Exercise the actual frame-input builders without running a GPU or a vehicle."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.features.model_inputs import action_time_input, clarity_manual_lookahead, lateral_model_times


ROOT = Path(__file__).resolve().parents[2]
KEY = "NrdrClarityAngleLookaheadMs"


class Params(dict):
  def get(self, key, *, return_default=False):
    return super().get(key)

  def get_bool(self, key):
    return bool(self.get(key))


@pytest.mark.parametrize("ms", [0, None, -5, 1, 7, True, 405, 5, 225, 400])
def test_selected_horizon_only_for_manual_angle_clarity(ms):
  params = Params({KEY: ms, "LagdToggle": False})
  cp = NS(brand="honda", carFingerprint="HONDA_CLARITY", steerControlType="angle")
  assert clarity_manual_lookahead(params, cp) == (ms / 1000 if ms in (5, 225, 400) else None)
  params["LagdToggle"] = True
  assert clarity_manual_lookahead(params, cp) is None
  params["LagdToggle"] = False
  for field, value in (("brand", "toyota"), ("carFingerprint", "HONDA_CIVIC"), ("steerControlType", "torque")):
    assert clarity_manual_lookahead(params, NS(**(vars(cp) | {field: value}))) is None


@pytest.mark.parametrize("relative", ["selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"])
@pytest.mark.parametrize("cap", [False, True])
def test_runner_inputs_across_model_changes(relative, cap):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"))
  main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")

  def assigned(n, key):
    return isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == key

  loop, = [n for n in main.body if isinstance(n, ast.While) and any(assigned(stmt, "frame_delay") for stmt in n.body)]
  start = next(i for i, n in enumerate(loop.body) if assigned(n, "frame_delay"))
  end = next(i for i, n in enumerate(loop.body[start:], start) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "model.frame_drop_ratio")
  frame_inputs = compile(ast.Module(loop.body[start:end], type_ignores=[]), str(path), "exec")

  class LocalModel(NS):
    pass

  ctx = dict(np=np, DT_MDL=.05, ModelState=LocalModel, lateral_model_times=lateral_model_times, action_time_input=action_time_input,
             cap_action_t=cap, JETLINK=False, v_ego=10., vec_desire=np.zeros(8), traffic_convention=np.zeros(2))
  # Same vehicle and saved knob throughout: legacy -> timed head -> plan fallback -> external runner.
  for ms, cls, timed, expected in [(0, LocalModel, True, .225), (5, LocalModel, True, .005), (400, LocalModel, True, .4),
                                    (5, LocalModel, False, .225), (5, NS, True, .225)]:
    model_inputs = {"action_t": None, "lateral_control_params": None}
    model = cls(timed_action_head=timed, numpy_inputs=model_inputs, npy=model_inputs, desire_key="desire")
    ctx.update(model=model, manual_lookahead=ms / 1000 if ms else None, lat_delay=.15, long_delay=.5)
    exec(frame_inputs, ctx)
    assert ctx["lat_action_t"] == pytest.approx(expected)
    assert ctx["inputs"]["action_t"] == pytest.approx([expected, .4 if cap else .575])
    if "lateral_control_params" in ctx["inputs"]:
      assert ctx["inputs"]["lateral_control_params"] == pytest.approx([10., .15 if expected == .225 else expected])


def _frame_inputs(relative="sunnypilot/modeld_v2/modeld.py"):
  path = ROOT / relative
  main = next(n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef) and n.name == "main")
  loop, = [n for n in main.body if isinstance(n, ast.While) and any(
    isinstance(s, ast.Assign) and ast.unparse(s.targets[0]) == "frame_delay" for s in n.body)]
  start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "frame_delay")
  end = next(i for i, n in enumerate(loop.body[start:], start) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "model.frame_drop_ratio")
  return compile(ast.Module(loop.body[start:end], type_ignores=[]), str(path), "exec")


@pytest.mark.parametrize("jetlink", [False, True])
@pytest.mark.parametrize("small_has_action_t", [False, True])
def test_jetlink_large_model_always_gets_action_t(jetlink, small_has_action_t):
  """JetLink's large model has an action_t input however the small bundle (e.g. Pop Model v2) is built."""
  class LocalModel(NS):
    pass

  small_inputs = {"desire": None, **({"action_t": None} if small_has_action_t else {})}
  model = LocalModel(timed_action_head=False, numpy_inputs=small_inputs, npy=small_inputs, desire_key="desire")
  ctx = dict(np=np, DT_MDL=.05, ModelState=LocalModel, lateral_model_times=lateral_model_times, action_time_input=action_time_input,
             cap_action_t=False, JETLINK=jetlink, v_ego=10., vec_desire=np.zeros(8), traffic_convention=np.zeros(2),
             model=model, manual_lookahead=None, lat_delay=.15, long_delay=.5)
  exec(_frame_inputs(), ctx)
  assert ("action_t" in ctx["inputs"]) == (jetlink or small_has_action_t)
  if jetlink or small_has_action_t:
    assert ctx["inputs"]["action_t"] == pytest.approx([ctx["lat_action_t"], .575])
