import json
from pathlib import Path
import re
import unittest

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PARAM_HEADER = REPOSITORY_ROOT / "openpilot/common/params_keys.h"
TICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/lane_centering.py"
MICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/lane_centering.py"
SUNNYLINK_ROOT = REPOSITORY_ROOT / "openpilot/sunnypilot/sunnylink"

LANE_CENTERING_KEYS = (
  "LaneCentering",
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
    mici_settings = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/settings.py").read_text(encoding="utf-8")
    self.assertIn("LaneCenteringLayout()", tici_settings)
    self.assertIn("LaneCenteringLayoutMici()", mici_settings)

  def test_local_write_callbacks_require_offroad_and_not_engaged(self) -> None:
    tici = TICI_PANEL.read_text(encoding="utf-8")
    mici = MICI_PANEL.read_text(encoding="utf-8")
    self.assertIn("if self._write_allowed():", tici)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", tici)
    self.assertEqual(tici.count("if not self._write_allowed():"), 1)
    self.assertEqual(tici.count("if not self._settings_writable():"), 1)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", mici)
    self.assertEqual(mici.count("if not self._write_allowed():"), 1)
    self.assertEqual(mici.count("if not self._settings_writable():"), 3)
    self.assertNotIn('param="LaneCentering"', tici)

  def test_sunnylink_has_one_offroad_only_dedicated_page(self) -> None:
    source_page = yaml.safe_load((SUNNYLINK_ROOT / "settings_ui_src/pages/lane_centering.yaml").read_text(encoding="utf-8"))
    source_developer = yaml.safe_load((SUNNYLINK_ROOT / "settings_ui_src/pages/developer.yaml").read_text(encoding="utf-8"))
    compiled = json.loads((SUNNYLINK_ROOT / "settings_ui.json").read_text(encoding="utf-8"))

    source_keys: list[str] = []
    developer_keys: list[str] = []
    _collect_keys(source_page, source_keys)
    _collect_keys(source_developer, developer_keys)
    self.assertEqual(tuple(source_keys), LANE_CENTERING_KEYS)
    self.assertFalse(set(LANE_CENTERING_KEYS) & set(developer_keys))

    items = source_page["sections"][0]["items"]
    for item in items:
      with self.subTest(key=item["key"]):
        self.assertIn({"$ref": "#/macros/offroad"}, item["enablement"])
        self.assertIn({"$ref": "#/macros/not_engaged"}, item["enablement"])
    for item in items[1:]:
      self.assertIn({"type": "param", "key": "LaneCentering", "equals": True}, item["enablement"])

    compiled_pages = [page for page in compiled["panels"] if page["id"] == "lane_centering"]
    self.assertEqual(len(compiled_pages), 1)
    compiled_keys: list[str] = []
    _collect_keys(compiled_pages[0], compiled_keys)
    self.assertEqual(tuple(compiled_keys), LANE_CENTERING_KEYS)

  def test_driver_override_is_wired_without_other_starpilot_controls(self) -> None:
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    controller = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py").read_text(encoding="utf-8")
    self.assertIn("bool(CS.steeringPressed))", controlsd)
    self.assertIn("if driver_override:", controller)
    for prohibited in ("turn_hold", "turn_lead", "lane_change_jerk"):
      self.assertNotIn(prohibited, controller)


if __name__ == "__main__":
  unittest.main()
