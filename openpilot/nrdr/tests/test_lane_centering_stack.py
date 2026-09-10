import json
from pathlib import Path
import re
import unittest

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PARAM_HEADER = REPOSITORY_ROOT / "openpilot/common/params_keys.h"
PARAM_INCLUDE = REPOSITORY_ROOT / "openpilot/nrdr/params/generated/params_keys.inc"
TICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/lane_centering.py"
MICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/lane_centering.py"
SUNNYLINK_ROOT = REPOSITORY_ROOT / "openpilot/sunnypilot/sunnylink"
NRDR_STEERING = REPOSITORY_ROOT / "openpilot/nrdr/ui/sunnylink/pages/steering.yaml"

LANE_CENTERING_KEYS = (
  "LaneCentering",
  "LaneCenteringMinSpeed",
  "LaneCenteringPauseOnSignal",
  "LaneCenterOffset",
  "LaneCenteringE2EAuthority",
)


def _collect_keys(node, found: list[str]) -> None:
  if isinstance(node, dict):
    if isinstance(node.get("key"), str):
      found.append(node["key"])
    for name, value in node.items():
      if name not in ("visibility", "enablement", "options"):
        _collect_keys(value, found)
  elif isinstance(node, list):
    for value in node:
      _collect_keys(value, found)


class TestLaneCenteringStack(unittest.TestCase):
  def test_existing_defaults_remain_exact(self) -> None:
    source = PARAM_HEADER.read_text(encoding="utf-8")
    expected = {
      "LaneCentering": 'PERSISTENT | BACKUP, BOOL, "0"',
      "LaneCenteringE2EAuthority": 'PERSISTENT | BACKUP, FLOAT, "1.0"',
      "LaneCenteringPauseOnSignal": 'PERSISTENT | BACKUP, BOOL, "1"',
      "LaneCenterOffset": 'PERSISTENT | BACKUP, FLOAT, "0.0"',
    }
    for key, attributes in expected.items():
      with self.subTest(key=key):
        self.assertEqual(len(re.findall(rf'\{{"{key}", \{{{re.escape(attributes)}\}}\}}', source)), 1)
    generated = PARAM_INCLUDE.read_text(encoding="utf-8")
    self.assertNotIn('"LaneCenteringMinSpeed"', source)
    self.assertEqual(generated.count('{"LaneCenteringMinSpeed", {PERSISTENT | BACKUP, INT, "50"}}'), 1)

  def test_controls_are_rehomed_out_of_developer_pages(self) -> None:
    developer_sources = (
      REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/developer.py",
      REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/developer.py",
    )
    for path in developer_sources:
      with self.subTest(path=path):
        source = path.read_text(encoding="utf-8")
        self.assertFalse(any(key in source for key in LANE_CENTERING_KEYS))

    for path in (TICI_PANEL, MICI_PANEL):
      with self.subTest(path=path):
        source = path.read_text(encoding="utf-8")
        for key in LANE_CENTERING_KEYS:
          self.assertIn(key, source)

    tici_settings = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/settings.py").read_text(encoding="utf-8")
    nrdr_lateral = (REPOSITORY_ROOT / "openpilot/nrdr/ui/settings/lateral_tuning.py").read_text(encoding="utf-8")
    mici_settings = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/settings.py").read_text(encoding="utf-8")
    mici_toggles = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/toggles.py").read_text(encoding="utf-8")
    self.assertNotIn("LaneCenteringLayout()", tici_settings)
    self.assertIn("LaneCenteringLayout()", nrdr_lateral)
    self.assertNotIn("LaneCenteringLayoutMici()", mici_settings)
    self.assertIn("LaneCenteringLayoutMici()", mici_toggles)

  def test_local_write_callbacks_require_offroad_and_not_engaged(self) -> None:
    tici = TICI_PANEL.read_text(encoding="utf-8")
    mici = MICI_PANEL.read_text(encoding="utf-8")
    self.assertIn("if self._write_allowed():", tici)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", tici)
    self.assertEqual(tici.count("if not self._write_allowed():"), 1)
    self.assertEqual(tici.count("if not self._settings_writable():"), 1)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", mici)
    self.assertEqual(mici.count("if not self._write_allowed():"), 1)
    self.assertEqual(mici.count("if not self._settings_writable():"), 4)
    self.assertNotIn('param="LaneCentering"', tici)

  def test_sunnylink_stack_is_nested_under_nrdr_lateral_tuning(self) -> None:
    self.assertFalse((SUNNYLINK_ROOT / "settings_ui_src/pages/lane_centering.yaml").exists())
    source_extension = yaml.safe_load(NRDR_STEERING.read_text(encoding="utf-8"))
    source_developer = yaml.safe_load((SUNNYLINK_ROOT / "settings_ui_src/pages/developer.yaml").read_text(encoding="utf-8"))
    compiled = json.loads((SUNNYLINK_ROOT / "settings_ui.json").read_text(encoding="utf-8"))

    nrdr_section = next(section for section in source_extension["sections"] if section["id"] == "nrdr")
    self.assertEqual(nrdr_section["title"], "nrdr Lateral Tuning")
    source_panels = [panel for panel in nrdr_section["sub_panels"] if panel["id"] == "nrdr_lane_centering_stack"]
    self.assertEqual(len(source_panels), 1)
    source_panel = source_panels[0]
    self.assertEqual(source_panel["label"], "Lane Centering Stack")
    self.assertIsNone(source_panel["trigger_key"])

    source_keys: list[str] = []
    developer_keys: list[str] = []
    _collect_keys(source_panel, source_keys)
    _collect_keys(source_developer, developer_keys)
    self.assertEqual(tuple(source_keys), LANE_CENTERING_KEYS)
    self.assertFalse(set(LANE_CENTERING_KEYS) & set(developer_keys))

    sibling_ids = [panel["id"] for panel in nrdr_section["sub_panels"]]
    self.assertLess(sibling_ids.index("nrdr_pidf_ground"), sibling_ids.index("nrdr_lane_centering_stack"))
    self.assertLess(sibling_ids.index("nrdr_lane_centering_stack"), sibling_ids.index("nrdr_steer_filters"))

    items = source_panel["items"]
    for item in items:
      with self.subTest(key=item["key"]):
        self.assertIn({"$ref": "#/macros/offroad"}, item["enablement"])
        self.assertIn({"$ref": "#/macros/not_engaged"}, item["enablement"])
    for item in items[1:]:
      self.assertIn({"type": "param", "key": "LaneCentering", "equals": True}, item["enablement"])

    minimum_speed = items[1]
    self.assertEqual(
      {field: minimum_speed[field] for field in ("min", "max", "step", "unit")},
      {"min": 12, "max": 100, "step": 1, "unit": "mph"},
    )
    self.assertIn("5 m/s controller floor", minimum_speed["description"])
    self.assertIn("waits when either boundary is uncertain", items[0]["details"])
    self.assertIn("makes no correction while the model path is already centered", items[0]["details"])
    self.assertIn("lane-change maneuver begins", items[2]["description"])
    self.assertIn("stops immediately", items[2]["description"])

    self.assertFalse(any(page["id"] == "lane_centering" for page in compiled["panels"]))
    compiled_steering = next(page for page in compiled["panels"] if page["id"] == "steering")
    compiled_nrdr = next(section for section in compiled_steering["sections"] if section["id"] == "nrdr")
    self.assertEqual(compiled_nrdr["title"], "nrdr Lateral Tuning")
    compiled_panels = [panel for panel in compiled_nrdr["sub_panels"] if panel["id"] == "nrdr_lane_centering_stack"]
    self.assertEqual(len(compiled_panels), 1)
    self.assertEqual(compiled_panels[0]["label"], "Lane Centering Stack")
    self.assertIsNone(compiled_panels[0]["trigger_key"])
    compiled_keys: list[str] = []
    _collect_keys(compiled_panels[0], compiled_keys)
    self.assertEqual(tuple(compiled_keys), LANE_CENTERING_KEYS)

    all_source_keys: list[str] = []
    for source_root in (SUNNYLINK_ROOT / "settings_ui_src", REPOSITORY_ROOT / "openpilot/nrdr/ui/sunnylink"):
      for path in source_root.rglob("*.yaml"):
        _collect_keys(yaml.safe_load(path.read_text(encoding="utf-8")), all_source_keys)
    all_compiled_keys: list[str] = []
    _collect_keys(compiled, all_compiled_keys)
    for key in LANE_CENTERING_KEYS:
      with self.subTest(unique_key=key):
        self.assertEqual(all_source_keys.count(key), 1)
        self.assertEqual(all_compiled_keys.count(key), 1)

  def test_control_path_reads_canonical_mph_setting_once_per_snapshot(self) -> None:
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    extension = (REPOSITORY_ROOT / "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py").read_text(encoding="utf-8")
    self.assertEqual(extension.count('self.params.get("LaneCenteringMinSpeed", return_default=True)'), 1)
    self.assertEqual(controlsd.count("self.lane_centering_min_speed_mph"), 1)
    tici = TICI_PANEL.read_text(encoding="utf-8")
    mici = MICI_PANEL.read_text(encoding="utf-8")
    self.assertIn("value_normalizer=lane_centering_min_speed_mph", tici)
    self.assertIn("lane_centering_min_speed_mph(ui_state.params.get", mici)

  def test_migration_is_restrictive_and_does_not_enable_lane_centering(self) -> None:
    source = PARAM_HEADER.read_text(encoding="utf-8")
    generated = PARAM_INCLUDE.read_text(encoding="utf-8")
    self.assertIn('{"LaneCentering", {PERSISTENT | BACKUP, BOOL, "0"}}', source)
    self.assertIn('{"LaneCenteringMinSpeed", {PERSISTENT | BACKUP, INT, "50"}}', generated)
    self.assertIn("Existing enabled installs adopt the new 50 mph minimum", NRDR_STEERING.read_text(encoding="utf-8"))

  def test_driver_override_is_wired_without_other_starpilot_controls(self) -> None:
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    controller = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py").read_text(encoding="utf-8")
    self.assertIn("bool(CS.steeringPressed))", controlsd)
    self.assertIn("if driver_override:", controller)
    for prohibited in ("left_only", "right_only", "visualizer", "turn_hold", "turn_lead", "lane_change_jerk"):
      self.assertNotIn(prohibited, controller)


if __name__ == "__main__":
  unittest.main()
