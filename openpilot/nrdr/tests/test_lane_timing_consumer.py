from __future__ import annotations

import ast
import math
from pathlib import Path
from types import SimpleNamespace

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LANE_CENTERING = REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py"
CONTROLSD = REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py"
PUBLISHERS = (
  REPOSITORY_ROOT / "openpilot/selfdrive/modeld/modeld.py",
  REPOSITORY_ROOT / "openpilot/sunnypilot/modeld_v2/modeld.py",
)


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


def _timing(model_mono_time=123_456_789, lateral_action_time=0.275):
  return SimpleNamespace(modelMonoTime=model_mono_time, lateralActionTime=lateral_action_time)


def test_exact_frame_timing_is_accepted_including_float32_tolerance():
  assert MAX_ACTION_TIME == pytest.approx(0.475)
  model_mono_time = 123_456_789
  for action_time in (0.075, 0.275, MAX_ACTION_TIME, MAX_ACTION_TIME + 1e-6):
    assert lane_centering_action_time(model_mono_time, _timing(model_mono_time, action_time), True) == pytest.approx(action_time)


@pytest.mark.parametrize(
  ("model_mono_time", "timing", "valid"),
  [
    (0, _timing(0, 0.275), True),                         # additive fields from an old message decode as zero
    (123_456_789, _timing(123_456_789, 0.275), False),    # optional service was not seen or its message is invalid
    (123_456_789, _timing(123_456_788, 0.275), True),     # stale metadata from the preceding model frame
    (123_456_789, _timing(123_456_790, 0.275), True),     # metadata arrived ahead of its model frame
    (123_456_789, _timing(123_456_789, 0.0), True),
    (123_456_789, _timing(123_456_789, -0.1), True),
    (123_456_789, _timing(123_456_789, float("nan")), True),
    (123_456_789, _timing(123_456_789, float("inf")), True),
    (123_456_789, _timing(123_456_789, MAX_ACTION_TIME + 1.1e-6), True),
    (123_456_789, SimpleNamespace(), True),
  ],
  ids=(
    "old-metadata-zero",
    "invalid-service",
    "stale-frame",
    "future-frame",
    "zero-action-time",
    "negative-action-time",
    "nan-action-time",
    "infinite-action-time",
    "over-maximum-action-time",
    "missing-fields",
  ),
)
def test_unmatched_or_invalid_timing_fails_closed(model_mono_time, timing, valid):
  assert lane_centering_action_time(model_mono_time, timing, valid) is None


def _submaster_call(tree: ast.AST) -> ast.Call:
  return next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and _attribute_name(node.func) == "messaging.SubMaster"
    and any(isinstance(child, ast.Constant) and child.value == "modelDataV2SP" for child in ast.walk(node))
  )


def test_timing_service_is_optional_to_all_three_submaster_health_checks():
  tree = ast.parse(CONTROLSD.read_text(encoding="utf-8"), filename=str(CONTROLSD))
  call = _submaster_call(tree)
  keywords = {keyword.arg: keyword.value for keyword in call.keywords}

  for mask in ("ignore_alive", "ignore_avg_freq", "ignore_valid"):
    assert mask in keywords
    ignored = [node.value for node in ast.walk(keywords[mask]) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    assert ignored == ["modelDataV2SP"]


def test_controlsd_passes_exact_current_model_identity_to_production_helper():
  tree = ast.parse(CONTROLSD.read_text(encoding="utf-8"), filename=str(CONTROLSD))
  helper_call = next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call) and _attribute_name(node.func) == "lane_centering_action_time"
  )

  assert len(helper_call.args) == 3
  assert ast.unparse(helper_call.args[0]) == "self.sm.logMonoTime['modelV2']"
  assert ast.unparse(helper_call.args[1]) == "self.sm['modelDataV2SP']"
  assert ast.unparse(helper_call.args[2]) == "self.sm.seen['modelDataV2SP'] and self.sm.valid['modelDataV2SP']"

  update_call = next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call) and _attribute_name(node.func) == "self.lane_centering.update"
  )
  action_time_keyword = next(keyword for keyword in update_call.keywords if keyword.arg == "action_time")
  assert ast.dump(action_time_keyword.value, include_attributes=False) == ast.dump(helper_call, include_attributes=False)


def _publisher_assignments(tree: ast.AST) -> dict[str, ast.Assign]:
  assignments = {}
  for node in ast.walk(tree):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
      continue
    target = _attribute_name(node.targets[0])
    if target is not None:
      assignments[target] = node
  return assignments


def _ordered_services(tree: ast.AST) -> list[str]:
  sends = []
  for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or _attribute_name(node.func) != "pm.send" or len(node.args) < 2:
      continue
    service = node.args[0]
    if isinstance(service, ast.Constant) and isinstance(service.value, str):
      sends.append((node.lineno, service.value))
  return [service for _, service in sorted(sends)]


@pytest.mark.parametrize("publisher", PUBLISHERS, ids=("standard-modeld", "sunnypilot-modeld-v2"))
def test_both_model_pipelines_publish_matching_identity_and_actual_action_time(publisher: Path):
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  assignments = _publisher_assignments(tree)
  model_time = assignments["mdv2sp_send.modelDataV2SP.modelMonoTime"]
  action_time = assignments["mdv2sp_send.modelDataV2SP.lateralActionTime"]

  assert _attribute_name(model_time.value) == "modelv2_send.logMonoTime"
  assert isinstance(action_time.value, ast.Name) and action_time.value.id == "lat_action_t"

  services = _ordered_services(tree)
  model_index = services.index("modelV2")
  assert services[model_index:model_index + 2] == ["modelV2", "modelDataV2SP"]
