import ast
from pathlib import Path

import pytest


ALERT_RENDERER = Path(__file__).parents[1] / "onroad" / "alert_renderer.py"
HELPER_NAMES = {
  "SPEED_LIMIT_ALERT_EVENTS",
  "SPEED_LIMIT_ALERT_FONT_MIN",
  "SPEED_LIMIT_ALERT_SMALL_FONT_MIN",
  "SPEED_LIMIT_ALERT_FONT_STEP",
  "SPEED_LIMIT_ALERT_VERTICAL_INSET",
}


def _load_layout_helper():
  tree = ast.parse(ALERT_RENDERER.read_text(encoding="utf-8"), filename=str(ALERT_RENDERER))
  body = []
  for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in HELPER_NAMES for target in node.targets):
      body.append(node)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {
      "_fit_speed_limit_alert_fonts",
      "_remaining_text_height",
    }:
      body.append(node)

  namespace = {}
  exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])), str(ALERT_RENDERER), "exec"), namespace)
  return namespace


_HELPER = _load_layout_helper()
SPEED_LIMIT_ALERT_EVENTS = _HELPER["SPEED_LIMIT_ALERT_EVENTS"]
SPEED_LIMIT_ALERT_VERTICAL_INSET = _HELPER["SPEED_LIMIT_ALERT_VERTICAL_INSET"]
_fit_speed_limit_alert_fonts = _HELPER["_fit_speed_limit_alert_fonts"]
_remaining_text_height = _HELPER["_remaining_text_height"]


@pytest.mark.parametrize(
  ("event_name", "message", "font_size", "small_font_size", "measured_heights", "expected"),
  (
    (
      "speedLimitPreActive",
      "press distance button to accept 50 km/h speed limit",
      44,
      None,
      {(44, None): 244.6, (42, None): 195.6},
      (42, None),
    ),
    (
      "speedLimitActive",
      "automatically changing max speed / the new speed limit has been applied.",
      54,
      32,
      {(54, 32): 217.5, (52, 30): 207.5},
      (52, 30),
    ),
    (
      "speedLimitPending",
      "automatically changing max speed / the last known speed limit has been applied.",
      54,
      32,
      {(54, 32): 217.5, (52, 30): 207.5},
      (52, 30),
    ),
    (
      "speedLimitChanged",
      "set speed changed",
      54,
      None,
      {(54, None): 107.1},
      (54, None),
    ),
  ),
)
def test_speed_limit_alert_fonts_fit_mici_measurements(event_name, message, font_size, small_font_size,
                                                       measured_heights, expected):
  # Measurements reproduce the shipped 476x240 mici renderer with its 354px
  # icon-aware confirmation width and 458px notification width.
  assert message
  available_height = 240
  fitted = _fit_speed_limit_alert_fonts(
    event_name,
    font_size,
    small_font_size,
    available_height,
    lambda main, secondary: measured_heights[(main, secondary)],
  )

  assert fitted == expected
  assert measured_heights[fitted] <= available_height - 2 * SPEED_LIMIT_ALERT_VERTICAL_INSET


def test_speed_limit_alert_event_scope_is_exact():
  assert SPEED_LIMIT_ALERT_EVENTS == {
    "speedLimitActive",
    "speedLimitChanged",
    "speedLimitPending",
    "speedLimitPreActive",
  }


def test_ordinary_alert_font_sizes_and_measurement_path_are_untouched():
  def should_not_measure(*_):
    raise AssertionError("ordinary mici alerts must bypass the speed-limit fit path")

  assert _fit_speed_limit_alert_fonts("controlsMismatch", 54, 32, 240, should_not_measure) == (54, 32)


def test_speed_limit_alert_keeps_existing_sizes_when_the_viewport_is_roomy():
  assert _fit_speed_limit_alert_fonts("speedLimitActive", 54, 32, 300, lambda *_: 217.5) == (54, 32)


def test_speed_limit_alert_font_fit_stops_at_readable_floors():
  assert _fit_speed_limit_alert_fonts("speedLimitActive", 54, 32, 100, lambda *_: 1000) == (36, 24)


@pytest.mark.parametrize(
  ("text_y", "text_height", "next_line_y", "expected"),
  ((0, 240, 150, 90), (-50, 240, 120, 70), (20, 240, 120, 140), (0, 100, 120, 0)),
)
def test_secondary_text_height_uses_the_absolute_bottom(text_y, text_height, next_line_y, expected):
  assert _remaining_text_height(text_y, text_height, next_line_y) == expected


def test_mici_renderer_wires_measured_fit_and_absolute_secondary_height():
  tree = ast.parse(ALERT_RENDERER.read_text(encoding="utf-8"), filename=str(ALERT_RENDERER))
  renderer = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "AlertRenderer")
  draw_text = next(node for node in renderer.body if isinstance(node, ast.FunctionDef) and node.name == "_draw_text")
  call_names = {
    node.func.id
    for node in ast.walk(draw_text)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
  }
  content_height_calls = [
    node
    for node in ast.walk(draw_text)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get_content_height"
  ]

  assert {"_fit_speed_limit_alert_fonts", "_remaining_text_height"} <= call_names
  assert len(content_height_calls) >= 3
