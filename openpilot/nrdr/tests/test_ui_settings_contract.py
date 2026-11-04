"""Focused UI-only contracts; compile in memory without touching generated JSON."""

import json
from pathlib import Path
import unittest

import yaml

from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import (
  DEFAULT_SRC, _canon_panel, _merge_extension_macros, compile_schema,
)
from openpilot.nrdr.ui.sunnylink import SOURCE_ROOT


def _items(node):
  if isinstance(node, dict):
    if "widget" in node and "key" in node:
      yield node
    for value in node.values():
      yield from _items(value)
  elif isinstance(node, list):
    for value in node:
      yield from _items(value)


class TestUiSettingsContract(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.schema = compile_schema(DEFAULT_SRC)
    cls.pages = {page["id"]: page for page in cls.schema["panels"]}
    cls.nrdr = next(section for section in cls.pages["steering"]["sections"] if section["id"] == "nrdr")
    cls.panels = {panel["id"]: panel for panel in cls.nrdr["sub_panels"]}

  def test_moved_items_live_only_in_steering_nrdr(self):
    self.assertEqual(self.nrdr["title"], "nrdr")
    main_keys = [item["key"] for item in self.nrdr["items"]]
    self.assertEqual(main_keys, ["NrdrSuggestedSettings", "NrdrRemoteForceUpdate", "DisablePowerDown"])
    longitudinal = self.panels["nrdr_longitudinal"]
    self.assertEqual(longitudinal["trigger_condition"], {
      "type": "capability", "field": "nrdr_longitudinal_tuning_available", "equals": True,
    })
    moved_keys = {item["key"] for item in _items(longitudinal)} | {"NrdrRemoteForceUpdate", "DisablePowerDown"}
    for page_id in ("cruise", "software", "device"):
      self.assertFalse(moved_keys & {item["key"] for item in _items(self.pages[page_id])})
      self.assertNotIn("nrdr", {section["id"] for section in self.pages[page_id]["sections"]})
    for key in moved_keys:
      self.assertEqual(sum(item["key"] == key for item in _items(self.schema)), 1, key)

  def test_upstream_sections_and_behavior_are_preserved(self):
    root = Path(DEFAULT_SRC)
    macros = yaml.safe_load((root / "_macros.yaml").read_text(encoding="utf-8"))["macros"]
    macros = _merge_extension_macros(macros, yaml.safe_load((SOURCE_ROOT / "_macros.yaml").read_text(encoding="utf-8")), "nrdr")
    for page_id in ("steering", "cruise", "software", "device"):
      page = yaml.safe_load((root / "pages" / f"{page_id}.yaml").read_text(encoding="utf-8"))
      expected = _canon_panel(page, macros)
      upstream_ids = {section["id"] for section in expected["sections"]}
      actual = {**self.pages[page_id], "sections": [section for section in self.pages[page_id]["sections"]
                                                   if section["id"] in upstream_ids]}
      self.assertEqual(actual, expected)
    timer = next(item for item in _items(self.pages["device"]) if item["key"] == "MaxTimeOffroad")
    self.assertIn({"type": "offroad_only"}, timer["enablement"])
    self.assertEqual(timer["enablement"].count({"type": "param", "key": "DisablePowerDown", "equals": False}), 1)
    shutdown = next(item for item in self.nrdr["items"] if item["key"] == "DisablePowerDown")
    self.assertEqual(shutdown["enablement"], [{"type": "offroad_only"}])

  def test_lane_centering_order_keeps_persisted_values_and_exclusivity(self):
    panel = self.panels["nrdr_lane_centering_stack"]
    mode, *tuning = panel["items"]
    self.assertEqual((panel["label"], mode["title"]), ("Lane Centering Method", "Lane Centering Method"))
    self.assertEqual([(option["label"], option["value"]) for option in mode["options"]], [("Off", 0), ("Sunny", 2), ("Star", 1)])
    self.assertEqual(mode["options"][1]["enablement"], [{"type": "capability", "field": "custom_model_active", "equals": True}])
    self.assertNotIn("enablement", mode["options"][0])
    self.assertNotIn("enablement", mode["options"][2])
    for item in tuning:
      self.assertIn({"type": "param", "key": "LaneGuidanceMode", "equals": 1}, item["enablement"])
    self.assertIn("mutually exclusive", mode["details"])

  def test_driver_monitoring_first_reminder_contract(self):
    panel = self.panels["nrdr_driver_monitoring"]
    self.assertEqual(panel["label"], "Driver Monitoring")
    self.assertIsNone(panel["trigger_key"])
    self.assertEqual(panel["trigger_condition"], {
      "type": "capability", "field": "nrdr_driver_monitoring_tuning_available", "equals": True,
    })
    item, = panel["items"]
    self.assertEqual(item["key"], "NrdrDriverMonitoringReminderPercent")
    self.assertEqual(tuple(item[field] for field in ("widget", "min", "max", "step", "unit")), ("option", 50, 250, 5, "%"))
    self.assertEqual(item["title"], "First Reminder Timing")
    self.assertTrue(item["needs_onroad_cycle"])
    self.assertEqual(item["enablement"], [{"type": "offroad_only"}])
    self.assertIn("100% uses upstream timing", item["description"])
    self.assertIn("gaps between later warnings stay unchanged", item["description"])
    for text in ("No disable option", "12.5, 15.5, and 20.5", "12.5, 22.5, and 32.5", "5-second no-response interval",
                 "Changes apply after reboot", "does not guarantee an emergency stop"):
      self.assertIn(text, item["details"])
    self.assertNotIn("capped", item["details"])
    contract = json.loads((Path(DEFAULT_SRC).parent / "settings_ui.schema.json").read_text(encoding="utf-8"))
    self.assertLessEqual(item.keys(), contract["$defs"]["SchemaItem"]["properties"].keys())

  def test_display_copy_uses_nrdr_sunny_and_star_without_renaming_ids(self):
    def strings(node):
      if isinstance(node, dict):
        for key, value in node.items():
          if key in ("title", "label", "description", "details") and isinstance(value, str):
            yield value
          else:
            yield from strings(value)
      elif isinstance(node, list):
        for value in node:
          yield from strings(value)

    copy = "\n".join(strings(self.pages["steering"]))
    self.assertNotIn("NRDR", copy)
    self.assertNotIn("Blendful", copy)
    self.assertNotIn("Lane Centering Stack", copy)
    self.assertIn("nrdr_lane_centering_stack", self.panels)
    self.assertIn("nrdr_special", {section["id"] for section in self.pages["steering"]["sections"]})


if __name__ == "__main__":
  unittest.main()
