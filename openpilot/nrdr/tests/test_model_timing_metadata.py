from __future__ import annotations

import ast
from pathlib import Path
import re

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
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


def _assignments(tree: ast.AST) -> dict[str, ast.Assign]:
  assignments = {}
  for node in ast.walk(tree):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
      continue
    target = _attribute_name(node.targets[0])
    if target is not None:
      assignments[target] = node
  return assignments


def _ordered_sends(tree: ast.AST) -> list[tuple[str, int]]:
  sends = []
  for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or _attribute_name(node.func) != "pm.send" or len(node.args) < 2:
      continue
    service = node.args[0]
    if isinstance(service, ast.Constant) and isinstance(service.value, str):
      sends.append((service.value, node.lineno))
  return sorted(sends, key=lambda item: item[1])


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


@pytest.mark.parametrize("publisher", PUBLISHERS, ids=("standard-modeld", "sunnypilot-modeld-v2"))
def test_publishers_attach_exact_model_identity_and_actual_action_time(publisher: Path):
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  assignments = _assignments(tree)

  model_time = assignments["mdv2sp_send.modelDataV2SP.modelMonoTime"]
  action_time = assignments["mdv2sp_send.modelDataV2SP.lateralActionTime"]
  assert _attribute_name(model_time.value) == "modelv2_send.logMonoTime"
  assert isinstance(action_time.value, ast.Name) and action_time.value.id == "lat_action_t"

  metadata_send_line = dict(_ordered_sends(tree))["modelDataV2SP"]
  assert model_time.lineno < metadata_send_line
  assert action_time.lineno < metadata_send_line


@pytest.mark.parametrize("publisher", PUBLISHERS, ids=("standard-modeld", "sunnypilot-modeld-v2"))
def test_matching_metadata_is_published_immediately_after_model_v2(publisher: Path):
  tree = ast.parse(publisher.read_text(encoding="utf-8"), filename=str(publisher))
  ordered_sends = _ordered_sends(tree)
  services = [service for service, _ in ordered_sends]
  model_index = services.index("modelV2")

  assert services[model_index:model_index + 2] == ["modelV2", "modelDataV2SP"]
  assert model_index < services.index("drivingModelData")
  assert model_index < services.index("cameraOdometry")
