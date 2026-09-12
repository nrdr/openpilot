from __future__ import annotations

import ast
from pathlib import Path
import re
from types import SimpleNamespace

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LOG_SCHEMA = REPOSITORY_ROOT / "openpilot/cereal/log.capnp"
CUSTOM_SCHEMA = REPOSITORY_ROOT / "openpilot/cereal/custom.capnp"
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


def _calls(tree: ast.AST, name: str) -> list[ast.Call]:
  return sorted(
    (node for node in ast.walk(tree) if isinstance(node, ast.Call) and _attribute_name(node.func) == name),
    key=lambda node: node.lineno,
  )


def _assignment(tree: ast.AST, target_name: str) -> ast.Assign:
  return next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and len(node.targets) == 1
    and _attribute_name(node.targets[0]) == target_name
  )


def _ordered_sends(tree: ast.AST) -> list[tuple[str, int]]:
  sends = []
  for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or _attribute_name(node.func) != "pm.send" or len(node.args) < 2:
      continue
    service = node.args[0]
    if isinstance(service, ast.Constant) and isinstance(service.value, str):
      sends.append((service.value, node.lineno))
  return sorted(sends, key=lambda item: item[1])


def _production_timing_helper():
  publisher = PUBLISHERS[0]
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  helper = next(
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "set_lateral_action_timing"
  )
  namespace: dict[str, object] = {}
  exec(compile(ast.Module(body=[helper], type_ignores=[]), str(publisher), "exec"), namespace)
  return namespace["set_lateral_action_timing"]


def test_model_v2_action_timing_field_is_additive_and_zero_when_unavailable():
  schema = LOG_SCHEMA.read_text(encoding="utf-8")
  model_schema = schema[schema.index("struct ModelDataV2 {"):]
  match = re.search(r"\n  struct Action \{(?P<body>.*?)\n  \}", model_schema, flags=re.DOTALL)
  assert match is not None
  body = match.group("body")

  assert "desiredCurvature @0 :Float32;" in body
  assert "desiredAcceleration @1 :Float32;" in body
  assert "shouldStop @2 :Bool;" in body
  assert "lateralActionTime @3 :Float32;" in body
  assert "zero means unavailable" in body


def test_model_data_v2_sp_timing_fields_are_additive_and_optional_by_default():
  schema = CUSTOM_SCHEMA.read_text(encoding="utf-8")
  match = re.search(r"struct ModelDataV2SP .*?\{(?P<body>.*?)\n\s*enum TurnDirection", schema, flags=re.DOTALL)
  assert match is not None
  body = match.group("body")

  assert "laneTurnDirection @0 :TurnDirection;" in body
  assert "leftLaneChangeEdgeBlock @1 :Bool;" in body
  assert "rightLaneChangeEdgeBlock @2 :Bool;" in body
  assert "modelMonoTime @3 :UInt64;" in body
  assert "lateralActionTime @4 :Float32;" in body
  assert "zero is the unavailable value" in body


@pytest.mark.parametrize("valid", (False, True), ids=("invalid-model", "valid-model"))
@pytest.mark.parametrize("action_time", (0.325, 0.475))
def test_production_helper_attaches_atomic_timing_without_changing_model_action(valid: bool, action_time: float):
  helper = _production_timing_helper()
  action = SimpleNamespace(
    desiredCurvature=-0.0125,
    desiredAcceleration=0.625,
    shouldStop=True,
    lateralActionTime=-1.0,
  )
  model = SimpleNamespace(
    valid=valid,
    logMonoTime=987654321,
    modelV2=SimpleNamespace(action=action),
  )
  compatibility = SimpleNamespace(
    valid=not valid,
    modelDataV2SP=SimpleNamespace(modelMonoTime=0, lateralActionTime=-1.0),
  )
  baseline_action = (action.desiredCurvature, action.desiredAcceleration, action.shouldStop)

  helper(model, compatibility, action_time)

  assert model.valid is valid
  assert model.logMonoTime == 987654321
  assert (action.desiredCurvature, action.desiredAcceleration, action.shouldStop) == baseline_action
  assert action.lateralActionTime == action_time
  assert compatibility.valid is valid
  assert compatibility.modelDataV2SP.modelMonoTime == model.logMonoTime
  assert compatibility.modelDataV2SP.lateralActionTime == action_time


@pytest.mark.parametrize("publisher", PUBLISHERS, ids=("standard-modeld", "sunnypilot-modeld-v2"))
def test_publishers_attach_exact_model_identity_and_actual_action_time(publisher: Path):
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  helper_calls = _calls(tree, "set_lateral_action_timing")
  assert len(helper_calls) == 1
  helper_call = helper_calls[0]
  assert [_attribute_name(arg) for arg in helper_call.args] == ["modelv2_send", "mdv2sp_send", "lat_action_t"]

  action_assignment = next(
    node for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "action" for target in node.targets)
    and isinstance(node.value, ast.Call)
    and (_attribute_name(node.value.func) or "").endswith("get_action_from_model")
  )
  fill_call = _calls(tree, "fill_model_msg")[0]
  metadata_send_line = dict(_ordered_sends(tree))["modelDataV2SP"]
  assert action_assignment.lineno < fill_call.lineno < helper_call.lineno < metadata_send_line


def test_standard_driving_model_action_is_copied_after_atomic_timing():
  publisher = PUBLISHERS[0]
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  helper_call = _calls(tree, "set_lateral_action_timing")[0]
  driving_copy = _calls(tree, "fill_driving_model_data")[0]
  driving_send_line = dict(_ordered_sends(tree))["drivingModelData"]

  assert helper_call.lineno < driving_copy.lineno < driving_send_line


def test_sunny_driving_model_mirrors_only_atomic_timing_after_fill():
  publisher = PUBLISHERS[1]
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  fill_call = _calls(tree, "fill_model_msg")[0]
  helper_call = _calls(tree, "set_lateral_action_timing")[0]
  timing_mirror = _assignment(tree, "drivingdata_send.drivingModelData.action.lateralActionTime")
  driving_send_line = dict(_ordered_sends(tree))["drivingModelData"]
  assert _attribute_name(timing_mirror.value) == "modelv2_send.modelV2.action.lateralActionTime"
  assert fill_call.lineno < helper_call.lineno < timing_mirror.lineno < driving_send_line

  driving_action = SimpleNamespace(
    desiredCurvature=-0.0125,
    desiredAcceleration=0.625,
    shouldStop=True,
    lateralActionTime=0.0,
  )
  drivingdata_send = SimpleNamespace(
    valid=False,
    drivingModelData=SimpleNamespace(action=driving_action),
  )
  modelv2_send = SimpleNamespace(
    valid=True,
    modelV2=SimpleNamespace(action=SimpleNamespace(lateralActionTime=0.545)),
  )
  baseline_action = (driving_action.desiredCurvature, driving_action.desiredAcceleration, driving_action.shouldStop)

  exec(
    compile(ast.Module(body=[timing_mirror], type_ignores=[]), str(publisher), "exec"),
    {"drivingdata_send": drivingdata_send, "modelv2_send": modelv2_send},
  )

  assert (driving_action.desiredCurvature, driving_action.desiredAcceleration, driving_action.shouldStop) == baseline_action
  assert driving_action.lateralActionTime == modelv2_send.modelV2.action.lateralActionTime
  assert drivingdata_send.valid is False
  assert modelv2_send.valid is True


@pytest.mark.parametrize("publisher", PUBLISHERS, ids=("standard-modeld", "sunnypilot-modeld-v2"))
def test_matching_metadata_is_published_immediately_after_model_v2(publisher: Path):
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  ordered_sends = _ordered_sends(tree)
  services = [service for service, _ in ordered_sends]
  model_index = services.index("modelV2")

  assert services[model_index:model_index + 2] == ["modelV2", "modelDataV2SP"]
  assert model_index < services.index("drivingModelData")
  assert model_index < services.index("cameraOdometry")
