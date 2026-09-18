from __future__ import annotations

import ast
import math
from pathlib import Path
from types import SimpleNamespace

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LANE_CENTERING = REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py"
CONTROLSD = REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py"


def _attribute_name(node: ast.AST) -> str | None:
  if isinstance(node, ast.Name):
    return node.id
  if isinstance(node, ast.Attribute):
    parent = _attribute_name(node.value)
    return f"{parent}.{node.attr}" if parent is not None else None
  return None


def _lane_centering_tree() -> ast.Module:
  return ast.parse(LANE_CENTERING.read_text(encoding="utf-8"), filename=str(LANE_CENTERING))


def _load_action_time_helper():
  """Execute the production acceptance helper with only its NumPy finite check stubbed."""
  tree = _lane_centering_tree()
  max_action_assignment = next(
    node for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "_MAX_ACTION_TIME" for target in node.targets)
  )
  helper = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "lane_centering_action_time"
  )
  max_action_time = float(ast.literal_eval(max_action_assignment.value))
  namespace = {
    "_MAX_ACTION_TIME": max_action_time,
    "np": SimpleNamespace(isfinite=math.isfinite),
  }
  executable = ast.fix_missing_locations(ast.Module(body=[helper], type_ignores=[]))
  exec(compile(executable, str(LANE_CENTERING), "exec"), namespace)
  return namespace["lane_centering_action_time"], max_action_time


lane_centering_action_time, MAX_ACTION_TIME = _load_action_time_helper()


def _model(lateral_action_time=0.275):
  return SimpleNamespace(action=SimpleNamespace(
    lateralActionTime=lateral_action_time, desiredCurvature=0.0012,
    desiredAcceleration=-0.3, shouldStop=False,
  ))


def test_atomic_timing_is_accepted_without_changing_the_model_action():
  assert MAX_ACTION_TIME >= 0.545
  for action_time in (0.075, 0.275, 0.545, MAX_ACTION_TIME, MAX_ACTION_TIME + 1e-6):
    model = _model(action_time)
    original = vars(model.action).copy()
    assert lane_centering_action_time(model) == pytest.approx(action_time)
    assert vars(model.action) == original


@pytest.mark.parametrize(
  "model",
  [
    _model(0.0),  # old serialized actions decode the new optional field as zero
    _model(-0.1),
    _model(float("nan")),
    _model(float("inf")),
    _model(MAX_ACTION_TIME + 1.1e-6),
    _model("malformed"),
    SimpleNamespace(),
    SimpleNamespace(action=SimpleNamespace()),
  ],
  ids=(
    "legacy-zero",
    "negative-action-time",
    "nan-action-time",
    "infinite-action-time",
    "over-maximum-action-time",
    "malformed-action-time",
    "missing-action",
    "missing-timing",
  ),
)
def test_invalid_atomic_timing_is_unavailable(model):
  assert lane_centering_action_time(model) is None


def test_controlsd_has_no_separate_timing_service_or_health_dependency():
  source = CONTROLSD.read_text(encoding="utf-8")
  assert "modelDataV2SP" not in source
  assert "bool(self.sm.all_checks(['modelV2']))" in source


@pytest.mark.parametrize("model_valid", [True, False], ids=["valid-model", "invalid-model"])
@pytest.mark.parametrize("action_time", [0.0, 0.325, 0.545], ids=["legacy-model", "standard-delay", "recorded-tsfdom-delay"])
def test_controlsd_uses_current_action_and_preserves_model_validity(model_valid, action_time):
  # Execute the actual production call. This harness has NO timing side channel:
  # subscribing to or indexing one again is a regression, even if its flag is ignored.
  tree = ast.parse(CONTROLSD.read_text(encoding="utf-8"), filename=str(CONTROLSD))
  update_call = next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call) and _attribute_name(node.func) == "self.lane_centering.update"
  )

  class SubMasterHarness:
    valid = {"lateralManeuverPlan": False}
    logMonoTime = {"modelV2": 123_456_789}

    def all_checks(self, services):
      assert services == ["modelV2"]
      return model_valid

  model = _model(action_time)
  captured = []
  controls = SimpleNamespace(
    sm=SubMasterHarness(),
    lane_centering=SimpleNamespace(update=lambda *args, **kwargs: captured.append((args, kwargs))),
    lane_centering_min_speed_mph=12, lane_centering_enabled=True, lane_center_offset=0.0,
    lane_centering_e2e_authority=0.0, lane_centering_strength=1.0, lane_centering_pause_on_signal=True,
  )
  namespace = {
    "self": controls, "model_v2": model, "new_desired_curvature": model.action.desiredCurvature,
    "CS": SimpleNamespace(vEgo=25.0, leftBlinker=False, rightBlinker=False, steeringPressed=False),
    "CC": SimpleNamespace(latActive=True), "lane_centering_action_time": lane_centering_action_time,
  }
  eval(compile(ast.Expression(body=update_call), str(CONTROLSD), "eval"), namespace)
  args, kwargs = captured[0]
  assert args[0] == model.action.desiredCurvature
  assert args[1] is model
  assert args[8] is True  # lateral availability was not modified by timing
  assert args[9] is model_valid
  assert kwargs["model_frame"] == controls.sm.logMonoTime["modelV2"]
  assert kwargs["action_time"] == (None if action_time == 0.0 else pytest.approx(action_time))
