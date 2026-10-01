from dataclasses import replace
from pathlib import Path
import unittest

import yaml

from openpilot.nrdr.params import (
  HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  NRDR_UI_METADATA,
  NRDR_UI_METADATA_BY_KEY,
  NrdrParamKey,
  UiDescriptionSource,
  UiRemoteWritePolicy,
  get_ui_metadata,
  validate_ui_metadata,
)
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamLifecycle, ParamType
from openpilot.nrdr.params.ui_metadata import LANE_CHANGE_UI_METADATA
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
from openpilot.nrdr.ui.sunnylink_schema import SunnylinkMetadataConflict, apply_sunnylink_metadata, sunnylink_fields_for_key
from openpilot.selfdrive.ui.translations.potools import extract_strings


EXPECTED_KEYS = (
  NrdrParamKey.LAT_P_SCALE_LOW_SPEED,
  NrdrParamKey.LAT_I_SCALE_LOW_SPEED,
  NrdrParamKey.LAT_P_SCALE_STANDARD,
  NrdrParamKey.LAT_I_SCALE_STANDARD,
  NrdrParamKey.LAT_P_SCALE_HIGHWAY,
  NrdrParamKey.LAT_I_SCALE_HIGHWAY,
)

FRICTION_KEYS = (
  NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION,
  NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD,
  NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY,
)
INTERPOLATED_KEYS = (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_LAT_ACCEL_FACTOR, *FRICTION_KEYS)
ALL_EXPECTED_KEYS = EXPECTED_KEYS

EXPECTED_NATIVE = {
  "LatPScaleLowSpeed": (
    "[0-25MPH] Proportional (Default: 100%)",
    "Corrects steering error as it occurs.",
  ),
  "LatIScaleLowSpeed": (
    "[0-25MPH] Integral (Default: 100%)",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
  ),
  "LatPScaleStandard": (
    "[25-50MPH] Proportional (Default: 100%)",
    "Corrects steering error as it occurs.",
  ),
  "LatIScaleStandard": (
    "[25-50MPH] Integral (Default: 100%)",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
  ),
  "LatPScaleHighway": (
    "[50+MPH] Proportional (Default: 100%)",
    "Corrects steering error as it occurs.",
  ),
  "LatIScaleHighway": (
    "[50+MPH] Integral (Default: 100%)",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
  ),
}

EXPECTED_SUNNYLINK_COPY = {
  "LatPScaleLowSpeed": (
    "[0-25MPH] Proportional",
    "Corrects steering error as it occurs.",
    "Corrects steering error as it occurs.",
  ),
  "LatIScaleLowSpeed": (
    "[0-25MPH] Integral",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
  ),
  "LatPScaleStandard": (
    "[25-50MPH] Proportional",
    "Corrects steering error as it occurs.",
    None,
  ),
  "LatIScaleStandard": (
    "[25-50MPH] Integral",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
    None,
  ),
  "LatPScaleHighway": (
    "[50+MPH] Proportional",
    "Corrects steering error as it occurs.",
    None,
  ),
  "LatIScaleHighway": (
    "[50+MPH] Integral",
    "Builds correction over time for persistent steering error, such as an alignment bias.",
    None,
  ),
}


class TestParamUiMetadata(unittest.TestCase):
  def test_first_slice_is_exact_and_valid(self):
    self.assertEqual(tuple(metadata.key for metadata in NRDR_UI_METADATA), ALL_EXPECTED_KEYS)
    self.assertEqual(tuple(NRDR_UI_METADATA_BY_KEY), tuple(key.value for key in ALL_EXPECTED_KEYS))
    self.assertEqual(validate_ui_metadata(), ())
    self.assertFalse(any("LatFScale" in key for key in NRDR_UI_METADATA_BY_KEY))

  def test_catalog_defaults_and_profile_values_are_characterized(self):
    profile = dict(HONDA_TORQUE_MOD_HANDCRAFTED_VALUES)
    for key in EXPECTED_KEYS:
      with self.subTest(key=key.value):
        spec = PARAM_SPECS_BY_KEY[key.value]
        self.assertIs(spec.param_type, ParamType.INT)
        self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
        self.assertEqual(spec.default, "100")
        self.assertEqual(profile[key.value], 100)
        self.assertIs(get_ui_metadata(key), NRDR_UI_METADATA_BY_KEY[key.value])

  def test_retired_blend_metadata_is_not_exposed(self):
    for key in INTERPOLATED_KEYS:
      self.assertNotIn(key.value, NRDR_UI_METADATA_BY_KEY)
      with self.assertRaises(KeyError):
        get_native_option_spec(key)
    self.assertEqual(LANE_CHANGE_UI_METADATA, ())

  def test_native_adapter_reproduces_exact_option_specs(self):
    for key in EXPECTED_KEYS:
      with self.subTest(key=key.value):
        title, description = EXPECTED_NATIVE[key.value]
        native = get_native_option_spec(key.value)
        self.assertEqual(native.param, key.value)
        self.assertEqual(native.title, title)
        self.assertEqual(native.description, description)
        self.assertEqual((native.min_value, native.max_value, native.value_change_step), (0, 500, 5))
        self.assertFalse(native.use_float_scaling)
        self.assertEqual(native.format_label(0), "0%")
        self.assertEqual(native.format_label(100), "100%")
        self.assertEqual(native.format_label(500), "500%")

  def test_sunnylink_adapter_reproduces_exact_fields(self):
    for key in EXPECTED_KEYS:
      with self.subTest(key=key.value):
        title, description, details = EXPECTED_SUNNYLINK_COPY[key.value]
        expected = {
          "widget": "option",
          "title": title,
          "description": description,
          "min": 0,
          "max": 500,
          "step": 5,
          "unit": "%",
        }
        if details is not None:
          expected["details"] = details
        self.assertEqual(sunnylink_fields_for_key(key.value), expected)
        merged = apply_sunnylink_metadata({"key": key.value, "widget": "option"})
        self.assertEqual({k: v for k, v in merged.items() if k != "enablement"}, {"key": key.value, **expected})
        self.assertEqual({c["condition"]["key"] for c in merged["enablement"]},
                         {"NrdrSuggestedSettings", "NrdrHandcraftedLateralTune", "NrdrLateralController"})

  def test_sunnylink_explicit_metadata_drift_is_rejected(self):
    with self.assertRaisesRegex(SunnylinkMetadataConflict, "LatPScaleLowSpeed.*'max'"):
      apply_sunnylink_metadata({"key": "LatPScaleLowSpeed", "widget": "option", "max": 501})

  def test_invalid_step_is_reported_without_crashing(self):
    metadata = get_ui_metadata(NrdrParamKey.LAT_P_SCALE_LOW_SPEED)
    invalid = replace(metadata, numeric=replace(metadata.numeric, step=0))
    self.assertIn("LatPScaleLowSpeed: step must be positive", validate_ui_metadata((invalid,)))

  def test_policies_are_explicit_and_separate(self):
    for key in EXPECTED_KEYS:
      with self.subTest(key=key.value):
        metadata = get_ui_metadata(key)
        self.assertEqual(metadata.edit_policies, ())
        self.assertIs(metadata.remote_write_policy, UiRemoteWritePolicy.ANY_ROAD_STATE)
    self.assertIs(get_ui_metadata("LatPScaleLowSpeed").native_description_source, UiDescriptionSource.DETAILS)
    self.assertIs(get_ui_metadata("LatPScaleStandard").native_description_source, UiDescriptionSource.DESCRIPTION)

  def test_native_runtime_strings_remain_translation_extractable(self):
    repository_root = Path(__file__).resolve().parents[3]
    relative_path = "openpilot/nrdr/params/ui_metadata.py"
    extracted = {entry.msgid for entry in extract_strings([relative_path], str(repository_root))}
    expected = {text for pair in EXPECTED_NATIVE.values() for text in pair}
    expected.update(text for item in LANE_CHANGE_UI_METADATA for text in (item.native_title, item.description, item.details))
    self.assertLessEqual(expected, extracted)

  def test_consumers_do_not_redeclare_managed_metadata(self):
    repository_root = Path(__file__).resolve().parents[3]
    native_path = repository_root / "openpilot/nrdr/ui/settings/pidf_ground.py"
    native_source = native_path.read_text(encoding="utf-8")
    self.assertIn('get_native_option_spec(key) if term in ("P", "I") else None', native_source)
    self.assertIn("spec.min_value", native_source)
    self.assertIn("spec.max_value", native_source)
    self.assertIn("spec.value_change_step", native_source)
    lane_source = (repository_root / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/steering_sub_layouts/lane_change_settings.py").read_text(encoding="utf-8")
    self.assertNotIn("NrdrLaneChangeEntrySrReduction", lane_source)
    self.assertNotIn('title=tr("Interpolated Torque/PIF Blend")', native_source)
    self.assertIn('NrdrOptimizedLaneChanges', native_source)
    for key in EXPECTED_KEYS:
      with self.subTest(surface="native", key=key.value):
        self.assertNotIn(f'param="{key.value}"', native_source)
        for text in EXPECTED_NATIVE[key.value]:
          self.assertNotIn(text, native_source)

    yaml_path = repository_root / "openpilot/nrdr/ui/sunnylink/pages/steering.yaml"
    source = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    items: dict[str, dict] = {}

    def collect(node):
      if isinstance(node, dict):
        if isinstance(node.get("key"), str):
          items[node["key"]] = node
        for name, value in node.items():
          if name not in ("visibility", "enablement", "options"):
            collect(value)
      elif isinstance(node, list):
        for value in node:
          collect(value)

    collect(source)
    for key in EXPECTED_KEYS:
      with self.subTest(surface="sunnylink", key=key.value):
        self.assertEqual(items[key.value], {"key": key.value, "widget": "option"})

    for key in INTERPOLATED_KEYS:
      with self.subTest(surface="sunnylink", key=key.value):
        self.assertNotIn(key.value, items)


if __name__ == "__main__":
  unittest.main()
