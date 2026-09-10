import ast
from pathlib import Path
from enum import IntEnum
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MICI_SETTINGS = REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/settings.py"
MICI_TOGGLES = REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/toggles.py"
MICI_SETTINGS_SP = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/settings.py"
TICI_SETTINGS_SP = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/settings.py"
NRDR_LATERAL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/lateral_tuning.py"
NRDR_LAYOUT = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr.py"
LANE_CENTERING_LAYOUT = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/lane_centering.py"


def _tree(path: Path) -> ast.Module:
  return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _method(tree: ast.Module, class_name: str, method_name: str) -> ast.FunctionDef:
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
  return next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)


def _widget_list(method: ast.FunctionDef) -> list[str]:
  calls = [
    node for node in ast.walk(method)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_widgets"
  ]
  assert len(calls) == 1
  widgets = calls[0].args[0]
  assert isinstance(widgets, ast.List)
  return [ast.unparse(item) for item in widgets.elts]


def _callback_body(method: ast.FunctionDef, button_name: str) -> str:
  callbacks = [
    node for node in ast.walk(method)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and ast.unparse(node.func.value) == f"self.{button_name}"
    and node.func.attr == "set_click_callback"
  ]
  assert len(callbacks) == 1
  callback = callbacks[0].args[0]
  assert isinstance(callback, ast.Lambda)
  return ast.unparse(callback.body)


def _lifecycle_class(path: Path, class_name: str, enum_name: str, method_names: tuple[str, ...]):
  tree = _tree(path)
  enum_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == enum_name)
  source_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
  methods = [
    node for node in source_class.body
    if isinstance(node, ast.FunctionDef) and node.name in method_names
  ]
  assignments = [
    node for node in tree.body
    if isinstance(node, (ast.Assign, ast.AnnAssign))
    and any(name.id == "HONDA_ONLY_LATERAL_PANELS" for name in ast.walk(node) if isinstance(name, ast.Name))
  ]
  harness = ast.ClassDef(
    name=f"{class_name}Harness",
    bases=[],
    keywords=[],
    body=methods,
    decorator_list=[],
  )
  module = ast.fix_missing_locations(ast.Module(body=[enum_node, *assignments, harness], type_ignores=[]))
  namespace = {
    "IntEnum": IntEnum,
    "Widget": object,
    "honda_tuning_available": lambda: True,
  }
  exec(compile(module, filename=str(path), mode="exec"), namespace)
  return namespace[f"{class_name}Harness"], namespace[enum_name]


class _LifecycleSpy:
  def __init__(self, *, refresh_on_show: bool = False):
    self.show_count = 0
    self.hide_count = 0
    self.refresh_count = 0
    self._refresh_on_show = refresh_on_show

  def show_event(self):
    self.show_count += 1
    if self._refresh_on_show:
      self.refresh_count += 1

  def hide_event(self):
    self.hide_count += 1


class TestSettingsNavigation(unittest.TestCase):
  def test_mici_root_buttons_keep_named_network_and_device_routes(self) -> None:
    init = _method(_tree(MICI_SETTINGS), "SettingsLayout", "__init__")
    self.assertEqual(
      _widget_list(init),
      [
        "self._toggles_btn",
        "self._network_btn",
        "self._device_btn",
        "self._software_btn",
        "self._pair_btn",
        "self._firehose_btn",
        "self._developer_btn",
      ],
    )
    self.assertEqual(_callback_body(init, "_network_btn"), "gui_app.push_widget(self._network_panel)")
    self.assertEqual(_callback_body(init, "_device_btn"), "gui_app.push_widget(self._device_panel)")

  def test_sunnypilot_mici_uses_semantic_anchors_only(self) -> None:
    tree = _tree(MICI_SETTINGS_SP)
    init = _method(tree, "SettingsLayoutSP", "__init__")

    item_subscripts = [
      node for node in ast.walk(init)
      if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "_items"
    ]
    self.assertEqual(item_subscripts, [])
    hard_coded_insertions = [
      node for node in ast.walk(init)
      if isinstance(node, ast.Call)
      and isinstance(node.func, ast.Attribute)
      and node.func.attr == "insert"
      and node.args
      and isinstance(node.args[0], ast.Constant)
      and isinstance(node.args[0].value, int)
    ]
    self.assertEqual(hard_coded_insertions, [])
    self.assertEqual(_callback_body(init, "_device_btn"), "gui_app.push_widget(self._device_panel)")

    insertions = [
      tuple(ast.unparse(arg) for arg in node.args)
      for node in ast.walk(init)
      if isinstance(node, ast.Call) and ast.unparse(node.func) == "self._insert_after"
    ]
    self.assertCountEqual(insertions, [
      ("items", "self._toggles_btn", "models_btn"),
      ("items", "self._software_btn", "sunnylink_btn"),
    ])

  def test_lane_centering_is_nested_below_mici_toggles(self) -> None:
    init = _method(_tree(MICI_TOGGLES), "TogglesLayoutMici", "__init__")
    widgets = _widget_list(init)
    lane_index = widgets.index("self._lane_centering_btn")
    self.assertEqual(widgets[lane_index - 1], "ldw_toggle")
    self.assertEqual(widgets[lane_index + 1], "always_on_dm_toggle")
    self.assertEqual(_callback_body(init, "_lane_centering_btn"), "gui_app.push_widget(self._lane_centering_panel)")

  def test_lane_centering_is_nested_below_nrdr_lateral_tuning(self) -> None:
    settings_source = TICI_SETTINGS_SP.read_text(encoding="utf-8")
    lateral_source = NRDR_LATERAL.read_text(encoding="utf-8")

    self.assertNotIn("PanelType.LANE_CENTERING", settings_source)
    self.assertNotIn('PanelInfo(tr_noop("Lane Centering")', settings_source)
    self.assertIn("LANE_CENTERING = 5", lateral_source)
    self.assertIn("self._lane_centering_layout = LaneCenteringLayout()", lateral_source)
    self.assertIn("callback=lambda: self._set_panel(LateralPanel.LANE_CENTERING)", lateral_source)
    self.assertIn("if panel == LateralPanel.LANE_CENTERING:", lateral_source)
    self.assertIn("return self._lane_centering_layout", lateral_source)

  def test_nested_lane_lifecycle_survives_back_sidebar_and_settings_close(self) -> None:
    lane_tree = _tree(LANE_CENTERING_LAYOUT)
    lane_show = _method(lane_tree, "LaneCenteringLayout", "show_event")
    lane_hide = _method(lane_tree, "LaneCenteringLayout", "hide_event")
    self.assertEqual([ast.unparse(node) for node in lane_show.body], ["self._refresh()", "self._scroller.show_event()"])
    self.assertEqual([ast.unparse(node) for node in lane_hide.body], ["self._scroller.hide_event()"])

    lateral_class, lateral_panel = _lifecycle_class(
      NRDR_LATERAL,
      "LateralTuningLayout",
      "LateralPanel",
      ("_panel_widget", "_set_panel", "show_event", "hide_event"),
    )
    lateral = lateral_class()
    lateral._shown = False
    lateral._current_panel = lateral_panel.HUB
    lateral._scroller = _LifecycleSpy()
    lateral._vehicle_model_layout = _LifecycleSpy()
    lateral._pidf_layout = _LifecycleSpy()
    lateral._override_layout = _LifecycleSpy()
    lateral._steer_filters_layout = _LifecycleSpy()
    lateral._lane_centering_layout = _LifecycleSpy(refresh_on_show=True)

    nrdr_class, nrdr_panel = _lifecycle_class(
      NRDR_LAYOUT,
      "NrdrLayout",
      "PanelType",
      ("_panel_widget", "_set_current_panel", "show_event", "hide_event"),
    )
    nrdr = nrdr_class()
    nrdr._shown = False
    nrdr._current_panel = nrdr_panel.NRDR
    nrdr._scroller = _LifecycleSpy()
    nrdr._lateral_layout = lateral
    nrdr._longitudinal_layout = _LifecycleSpy()
    nrdr._party_tricks_layout = _LifecycleSpy()

    # Local Back hides Lane Centering and returning to it refreshes Params.
    nrdr.show_event()
    nrdr._set_current_panel(nrdr_panel.LATERAL)
    lateral._set_panel(lateral_panel.LANE_CENTERING)
    self.assertEqual(lateral._lane_centering_layout.refresh_count, 1)
    lateral._set_panel(lateral_panel.HUB)
    self.assertEqual(lateral._lane_centering_layout.hide_count, 1)
    lateral._set_panel(lateral_panel.LANE_CENTERING)
    self.assertEqual(lateral._lane_centering_layout.refresh_count, 2)

    # A sidebar escape must unwind the nested panel before Lateral is reopened.
    nrdr._set_current_panel(nrdr_panel.NRDR)
    self.assertEqual(lateral._current_panel, lateral_panel.HUB)
    self.assertEqual(lateral._lane_centering_layout.hide_count, 2)
    nrdr._set_current_panel(nrdr_panel.LATERAL)
    self.assertEqual(lateral._current_panel, lateral_panel.HUB)
    lateral._set_panel(lateral_panel.LANE_CENTERING)
    self.assertEqual(lateral._lane_centering_layout.refresh_count, 3)

    # Closing and reopening Settings must perform the same unwind and refresh.
    nrdr.hide_event()
    self.assertEqual(nrdr._current_panel, nrdr_panel.NRDR)
    self.assertEqual(lateral._current_panel, lateral_panel.HUB)
    self.assertEqual(lateral._lane_centering_layout.hide_count, 3)
    nrdr.show_event()
    nrdr._set_current_panel(nrdr_panel.LATERAL)
    lateral._set_panel(lateral_panel.LANE_CENTERING)
    self.assertEqual(lateral._lane_centering_layout.refresh_count, 4)


if __name__ == "__main__":
  unittest.main()
