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


def _native_class(filename, name, *, saved_bools=None):
  # Execute the real layout construction with inert widget factories. Hardware
  # and IPC imports are deliberately excluded; this checks copy, not rendering.
  path = ROOT / "openpilot/nrdr/ui/settings" / filename
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name]
  saved_bools = dict(saved_bools or {})
  env = {
    "Widget": object, "Callable": Callable, "tr": lambda text: text,
    "ui_state": SimpleNamespace(params=SimpleNamespace(get_bool=lambda key: saved_bools.get(key, False))),
    "get_native_option_spec": get_native_option_spec,
    "large_reset_button": lambda: object(),
    "NavButton": lambda *_: SimpleNamespace(set_click_callback=lambda *_: None),
    "Scroller": lambda items, **_: items, "LineSeparatorSP": lambda *_: None,
    **{factory: lambda **kwargs: kwargs for factory in (
      "button_item_sp", "toggle_item_sp", "option_item_sp", "simple_button_item_sp", "multiple_button_item_sp",
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
    web = next(item for item in _panel(self.schema, "steering", "nrdr_longitudinal")["items"]
               if item["key"] == "NrdrStandstillGapExtra")
    self.assertEqual(web["title"], "Extra Stopped Lead Gap")
    self.assertEqual(local["title"](), "Extra Stopped Lead Gap (Default: 0 m)")
    self.assertEqual(local["param"], web["key"])
    self.assertEqual(tuple(local[k] for k in ("min_value", "max_value", "value_change_step")), (0, 500, 25))
    self.assertTrue(local["use_float_scaling"])
    self.assertEqual(local["label_callback"](125), "+1.25 m")
    self.assertEqual(tuple(web[k] for k in ("min", "max", "step", "unit")), (0.0, 5.0, 0.25, "m"))

  def test_engine_braking_uses_saved_state_without_automatic_param_binding(self):
    for saved in (False, True):
      with self.subTest(saved=saved):
        cls = _native_class("longitudinal_tuning.py", "LongitudinalTuningLayout",
                            saved_bools={"NrdrExperimentalEngineBraking": saved})
        layout = cls.__new__(cls)
        layout._initialize_items()
        engine = layout._engine_braking
        self.assertIs(engine["initial_state"], saved)
        # ToggleSP writes bound params after callbacks, bypassing a rejected save.
        self.assertNotIn("param", engine)
        self.assertEqual(engine["callback"], layout._set_engine_braking)
        self.assertTrue(callable(engine["enabled"]))

  def test_engine_braking_metadata_is_live_but_still_civic_pcm_only(self):
    items = _panel(self.schema, "steering", "nrdr_longitudinal")["items"]
    engine = next(item for item in items if item.get("key") == "NrdrExperimentalEngineBraking")
    self.assertFalse(engine.get("needs_onroad_cycle", False))
    self.assertNotIn("Restart required", engine["details"])
    self.assertIn("Applies live", engine["details"])
    self.assertIn("Defaults on for an eligible Civic PCM without a gas interceptor when no choice is saved", engine["details"])
    self.assertIn("Existing On/Off choices are preserved", engine["details"])
    self.assertEqual(engine["visibility"], engine["enablement"])
    self.assertEqual(engine["enablement"], [
      {"type": "capability", "field": "nrdr_honda_pcm_tuning_available", "equals": True},
      {"type": "capability", "field": "car_fingerprint", "equals": "HONDA_CIVIC"},
    ])

  def test_honda_pcm_mode_and_wind_order_copy_and_parked_restart_rules(self):
    cls = _native_class("longitudinal_tuning.py", "LongitudinalTuningLayout")
    layout = cls.__new__(cls)
    local_items = layout._initialize_items()
    self.assertEqual(local_items[:6], [layout._live_learning_gas, layout._reset_live_gas, None,
                                      layout._pcm_mode, layout._wind_brake, layout._static_feedforward_long])
    remote = _panel(self.schema, "steering", "nrdr_longitudinal")["items"]
    self.assertEqual([item["key"] for item in remote[:6]], [
      "HondaLiveLearningGas", "NrdrResetLiveGas", "NrdrLiveGasResetStatus",
      "NrdrHondaPcmMode", "NrdrHondaWindBrake", "StaticFeedforwardLong",
    ])
    mode, wind = remote[3:5]
    self.assertEqual(mode["widget"], "multiple_button")
    self.assertEqual(mode["options"], [
      {"label": "Off", "value": 0}, {"label": "ECU-Matched", "value": 1}, {"label": "Experimental", "value": 2},
    ])
    self.assertEqual([label() for label in layout._pcm_mode["buttons"]], [o["label"] for o in mode["options"]])
    for local, web in ((layout._pcm_mode, mode), (layout._wind_brake, wind)):
      self.assertEqual(local["title"](), web["title"])
      self.assertIn("Restart required.", local["description"]())
      self.assertEqual(local["description"](), web["description"])
      self.assertTrue(web["needs_onroad_cycle"])
      self.assertEqual(web["enablement"], [{"type": "offroad_only"}, {
        "type": "capability", "field": "nrdr_honda_pcm_tuning_available", "equals": True,
      }])
      self.assertEqual(web["visibility"], web["enablement"][1:])
    self.assertIn("mmmorks", layout._pcm_mode["description"]())
    self.assertIn("keeps MVL mapping", mode["details"])
    self.assertIn("ramp, coast and brake-release rules", layout._pcm_mode["description"]())
    self.assertIn("Frozen in ECU-Matched and Civic Experimental", layout._live_learning_gas["description"]())
    self.assertEqual(layout._live_learning_gas["description"](), remote[0]["description"])
    self.assertIn("Turning it off changes friction-brake demand", wind["details"])
    self.assertNotIn("NrdrHondaEcuMatchedLong", [item["key"] for item in remote])

  def test_override_threshold_labels_keep_keys_and_show_straights_before_curves(self):
    native = _native_class("override_tuning.py", "OverrideTuningLayout")(lambda: None)
    remote = _panel(self.schema, "steering", "nrdr_override")["items"]
    expected = [
      ("NrdrOverrideThresholdCenterBoost", "Driver Override Threshold (During Straights)"),
      ("NrdrDriverOverrideThreshold", "Driver Override Threshold (During Curves)"),
    ]
    for index, (key, title) in enumerate(expected):
      with self.subTest(key=key):
        local, web = native._scroller[index], remote[index]
        self.assertEqual((local["param"], local["title"]()), (key, title))
        self.assertEqual((web["key"], web["title"]), (key, title))
        self.assertEqual(local["description"](), web["description"])
        self.assertEqual(tuple(local[k] for k in ("min_value", "max_value", "value_change_step")), (100, 5000, 100))
        self.assertEqual(tuple(web[k] for k in ("min", "max", "step")), (100, 5000, 100))
        self.assertEqual(local["label_callback"](1500), "1500")

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

  def test_controller_copy_requires_the_corrected_firmware_not_the_old_placeholder(self):
    panel = _panel(self.schema, "steering", "nrdr_pidf_ground")
    selector = next(item for item in panel["items"] if item["key"] == "NrdrLateralController")
    self.assertIn("exact modified steering firmware revision", selector["description"])
    self.assertIn("04147917", selector["details"])
    self.assertIn("7ba37432", selector["details"])
    self.assertIn("same version strings", selector["details"])
    source = (ROOT / "openpilot/nrdr/ui/settings/pidf_ground.py").read_text(encoding="utf-8")
    self.assertNotIn("uses the Bosch C020 tune", source)
    # The device shows each profile's required corrected build, which the profile carries.
    self.assertIn("profile.required_rwd", source)
    from openpilot.nrdr.features.lateral.controller_selection import INSIGHT_PROFILE, TEG_PROFILE
    self.assertEqual((TEG_PROFILE.required_rwd, INSIGHT_PROFILE.required_rwd), ("04147917", "7ba37432"))


if __name__ == "__main__":
  unittest.main()
