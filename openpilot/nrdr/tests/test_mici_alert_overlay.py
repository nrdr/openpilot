import ast
from pathlib import Path

import pytest


MICI_ONROAD = Path(__file__).parents[1] / "ui" / "onroad" / "mici_onroad.py"
SPEED_LIMIT_ALERT_EVENTS = frozenset({
  "speedLimitActive",
  "speedLimitChanged",
  "speedLimitPending",
  "speedLimitPreActive",
})


def _load_visibility_helper():
  tree = ast.parse(MICI_ONROAD.read_text(encoding="utf-8"), filename=str(MICI_ONROAD))
  helper = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_confidence_ball_visible")
  namespace = {"SPEED_LIMIT_ALERT_EVENTS": SPEED_LIMIT_ALERT_EVENTS}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[helper], type_ignores=[])), str(MICI_ONROAD), "exec"), namespace)
  return namespace["_confidence_ball_visible"]


_confidence_ball_visible = _load_visibility_helper()


@pytest.mark.parametrize("event_name", SPEED_LIMIT_ALERT_EVENTS)
def test_confidence_ball_is_hidden_for_speed_limit_alerts(event_name):
  assert not _confidence_ball_visible(f"{event_name}/warning")


@pytest.mark.parametrize("alert_type", ("", "controlsMismatch/warning", "laneChange/warning"))
def test_confidence_ball_is_unchanged_for_other_alerts(alert_type):
  assert _confidence_ball_visible(alert_type)


def test_nrdr_view_applies_visibility_before_rendering_overlays():
  tree = ast.parse(MICI_ONROAD.read_text(encoding="utf-8"), filename=str(MICI_ONROAD))
  view = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "NrdrAugmentedRoadView")
  render = next(node for node in view.body if isinstance(node, ast.FunctionDef) and node.name == "_render")

  calls = [
    node for node in ast.walk(render)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
  ]
  set_visible = next(node for node in calls if node.func.attr == "set_visible")
  super_render = next(node for node in calls if node.func.attr == "_render")
  assert set_visible.lineno < super_render.lineno
