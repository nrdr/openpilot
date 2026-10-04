"""Controller copy parity without starting the UI, Params, or vehicle services."""
import ast
from collections.abc import Callable
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC


ROOT = Path(__file__).resolve().parents[3]
BANDS = (("LowSpeed", "[0-25MPH]"), ("Standard", "[25-50MPH]"), ("Highway", "[50+MPH]"))
TERMS = (("P", "Proportional"), ("I", "Integral"), ("D", "Derivative"), ("F", "Feedforward"))
DESCRIPTIONS = {
  "P": "Corrects steering error as it occurs.",
  "I": "Builds correction over time for persistent steering error, such as an alignment bias.",
    "D": "Opposes steering-wheel motion to help reduce overshoot (steering-rate damping). "
       + "Defaults to 0% (off). Optimized lane changes bypass it.",
  "F": "Supplies anticipated steering torque before an error occurs.",
}


def _panel(schema, page_id, panel_id):
  page = next(p for p in schema["panels"] if p["id"] == page_id)
  section = next(s for s in page["sections"] if s["id"] == "nrdr")
  return next(p for p in section["sub_panels"] if p["id"] == panel_id)


def _native_class(filename, name):
  # Execute the real layout construction with inert widget factories. Hardware
  # and IPC imports are deliberately excluded; this checks copy, not rendering.
  path = ROOT / "openpilot/nrdr/ui/settings" / filename
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name]
  env = {
    "Widget": object, "Callable": Callable, "tr": lambda text: text,
    "get_native_option_spec": get_native_option_spec,
    "NavButton": lambda *_: SimpleNamespace(set_click_callback=lambda *_: None),
    "Scroller": lambda items, **_: items, "LineSeparatorSP": lambda *_: None,
    **{factory: lambda **kwargs: kwargs for factory in (
      "button_item_sp", "toggle_item_sp", "option_item_sp", "simple_button_item_sp",
    )},
  }
  exec(compile(tree, str(path), "exec"), env)
  return env[name]


class TestControllerUiLabels(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.schema = compile_schema(DEFAULT_SRC)

  def test_native_and_sunnylink_speed_prefix_copy_order_and_ranges_match(self):
    native = _native_class("pidf_ground.py", "PidfGroundLayout")(lambda: None, lambda: None)
    panel = _panel(self.schema, "steering", "nrdr_pidf_ground")
    remote = {item["key"]: item for item in panel["items"]}
    expected_keys = []
    for band, prefix in BANDS:
      for term, name in TERMS:
        key = f"NrdrLatRateDamping{band}" if term == "D" else f"Lat{term}Scale{band}"
        expected_keys.append(key)
        with self.subTest(key=key):
          local, web = native._tuning_items[key], remote[key]
          self.assertEqual(local["title"](), f"{prefix} {name}")
          self.assertEqual(web["title"], local["title"]())
          self.assertEqual(local["description"](), DESCRIPTIONS[term])
          self.assertEqual(web["description"], DESCRIPTIONS[term])
          self.assertEqual(local["param"], key)
          expected_range = (0, 300 if term == "D" else 500, 5)
          self.assertEqual(tuple(local[k] for k in ("min_value", "max_value", "value_change_step")), expected_range)
          self.assertEqual(tuple(web[k] for k in ("min", "max", "step")), expected_range)
          self.assertEqual(local["label_callback"](100), "100%")
          self.assertEqual(web["unit"], "%")
          lock_rules = json.dumps(web["enablement"])
          self.assertIn("NrdrSuggestedSettings", lock_rules)
          self.assertIn("NrdrLateralController", lock_rules)
    self.assertEqual([key for key in native._tuning_items if key in expected_keys], expected_keys)
    self.assertEqual([key for key in remote if key in expected_keys], expected_keys)

  def test_stopped_gap_rename_keeps_parameter_units_and_limits(self):
    cls = _native_class("longitudinal_tuning.py", "LongitudinalTuningLayout")
    layout = cls.__new__(cls)
    layout._initialize_items()
    local = layout._standstill_gap
    web = next(item for item in _panel(self.schema, "cruise", "nrdr_longitudinal")["items"]
               if item["key"] == "NrdrStandstillGapExtra")
    self.assertEqual(web["title"], "Extra Stopped Lead Gap")
    self.assertEqual(local["title"](), "Extra Stopped Lead Gap (Default: 0 m)")
    self.assertEqual(local["param"], web["key"])
    self.assertEqual(tuple(local[k] for k in ("min_value", "max_value", "value_change_step")), (0, 500, 25))
    self.assertTrue(local["use_float_scaling"])
    self.assertEqual(local["label_callback"](125), "+1.25 m")
    self.assertEqual(tuple(web[k] for k in ("min", "max", "step", "unit")), (0.0, 5.0, 0.25, "m"))

  def test_device_yaw_switch_is_near_top_separate_from_full_controller_and_locked_consistently(self):
    key = "NrdrDeviceYawCorrection"
    native = _native_class("pidf_ground.py", "PidfGroundLayout")(lambda: None, lambda: None)
    panel = _panel(self.schema, "steering", "nrdr_pidf_ground")
    self.assertEqual([item["key"] for item in panel["items"][:4]],
                     ["NrdrLateralController", "NrdrLatStiction", key, "NrdrOptimizedLaneChanges"])
    local, web = native._tuning_items[key], panel["items"][2]
    self.assertEqual(local["title"], "Use Device Yaw Correction")
    self.assertEqual(web["title"], local["title"])
    self.assertEqual(web["description"], local["description"])
    self.assertEqual(web["widget"], "toggle")
    self.assertEqual(web["visibility"], [{
      "type": "not", "condition": {"type": "param", "key": "NrdrLateralController", "equals": 1},
    }])
    self.assertEqual([option["label"] for option in panel["items"][0]["options"]],
                     ["PIF Control", "Firmware Controller"])
    self.assertEqual(web["enablement"][0], {
      "type": "capability", "field": "nrdr_interpolated_torque_pif_blend_available", "equals": True,
    })
    locks = {rule["condition"]["key"] for rule in web["enablement"] if rule["type"] == "not"}
    self.assertEqual(locks, {"NrdrSuggestedSettings", "NrdrHandcraftedLateralTune", "NrdrLateralController"})
    self.assertTrue(tuning_write_allowed({}, key))
    for settings in ({"NrdrSuggestedSettings": True}, {"NrdrHandcraftedLateralTune": True}, {"NrdrLateralController": 1}):
      self.assertFalse(tuning_write_allowed(settings, key))

  def test_committed_sunnylink_output_matches_source(self):
    path = ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json"
    self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.schema)


if __name__ == "__main__":
  unittest.main()
