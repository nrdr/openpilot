"""New controls retain parameter identities, parked guards and panel lifecycle."""
from types import SimpleNamespace
import unittest

from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.tests.test_settings_navigation import NRDR_LAYOUT, _lifecycle_class, _LifecycleSpy, _method, _tree
from openpilot.nrdr.tests.test_ui_settings_contract import _items
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema


class TestJetlinkSettings(unittest.TestCase):
  def test_saved_jetlink_choices_are_locked_onroad_without_writes(self):
    saved = {"JetlinkLink": 2, "JetlinkChargePhone": True}
    params = SimpleNamespace(get=lambda key: saved.get(key))
    for key in saved:
      self.assertTrue(tuning_write_allowed(params, key, is_offroad=True))
      self.assertFalse(tuning_write_allowed(params, key, is_offroad=False))
      self.assertFalse(tuning_write_allowed(params, key))  # Unknown road state.
    self.assertEqual(saved, {"JetlinkLink": 2, "JetlinkChargePhone": True})

  def test_jetlink_panel_is_reachable_without_honda_and_unwinds(self):
    cls, panel = _lifecycle_class(NRDR_LAYOUT, "NrdrLayout", "PanelType",
                                ("_panel_widget", "_set_current_panel", "show_event", "hide_event"))
    layout = cls()
    layout._shown = False
    layout._current_panel = panel.NRDR
    layout._scroller = _LifecycleSpy()
    layout._jetlink_layout = _LifecycleSpy(refresh_on_show=True)
    layout._set_current_panel.__globals__["honda_tuning_available"] = lambda: False
    layout.show_event()
    layout._set_current_panel(panel.JETLINK)
    self.assertEqual(layout._jetlink_layout.show_count, 1)
    layout.hide_event()
    self.assertEqual(layout._jetlink_layout.hide_count, 1)
    self.assertEqual(layout._current_panel, panel.NRDR)

  def test_remote_locations_and_parked_guards(self):
    schema = compile_schema(DEFAULT_SRC)
    steering = next(p for p in schema["panels"] if p["id"] == "steering")
    nrdr = next(s for s in steering["sections"] if s["id"] == "nrdr")
    panels = {p["id"]: p for p in nrdr["sub_panels"]}
    self.assertEqual(list(panels)[-1], "nrdr_jetlink")
    self.assertIn("ExperimentalModeSetSpeed", [i["key"] for i in panels["nrdr_longitudinal"]["items"]])
    all_items = list(_items(schema))
    for key in ("ExperimentalModeSetSpeed", "JetlinkLink", "JetlinkChargePhone"):
      self.assertEqual(sum(i["key"] == key for i in all_items), 1)
    link, charge = panels["nrdr_jetlink"]["items"]
    self.assertEqual([(o["label"], o["value"]) for o in link["options"]], [("Off", 0), ("USB", 1), ("iOS", 2)])
    for item in (link, charge):
      self.assertIn({"type": "offroad_only"}, item["enablement"])
    self.assertEqual(charge["visibility"], [{"type": "param", "key": "JetlinkLink", "equals": 2}])

  def test_compact_device_keeps_jetlink_last_after_base_reorders(self):
    source = NRDR_LAYOUT.parents[4] / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py"
    import ast
    show = ast.unparse(_method(_tree(source), "DeviceLayoutMiciSP", "show_event"))
    self.assertLess(show.index("super().show_event()"), show.index("append(self._jetlink_btn)"))


if __name__ == "__main__":
  unittest.main()
