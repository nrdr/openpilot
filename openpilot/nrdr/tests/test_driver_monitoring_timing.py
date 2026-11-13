import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import yaml

from openpilot.nrdr.hooks.driver_monitoring import apply_driver_monitoring_policy, validate_reminder_percent
from openpilot.nrdr.tools.release.clean_overlay import driver_monitoring as clean_monitoring
from openpilot.nrdr.tools.release.clean_overlay.strip_monitoring_ui import without_monitoring_panel


UPSTREAM_TIMINGS = {
  "_WHEELTOUCH_POLICY_ALERT_1_TIMEOUT": 5.,
  "_WHEELTOUCH_POLICY_ALERT_2_TIMEOUT": 15.,
  "_WHEELTOUCH_POLICY_ALERT_3_TIMEOUT": 25.,
  "_VISION_POLICY_ALERT_1_TIMEOUT": 5.,
  "_VISION_POLICY_ALERT_2_TIMEOUT": 8.,
  "_VISION_POLICY_ALERT_3_TIMEOUT": 13.,
  "_NO_RESPONSE_TIMEOUT": 5.,
  "_MAX_ALERT_3": 2,
  "_MAX_NO_RESPONSE": 1,
  "_LOCKOUT_TIMES": [1200, 6000, 18000, 36000],
  "_TIMEOUT_RECOVERY_FACTOR_MAX": 5.,
  "_TIMEOUT_RECOVERY_FACTOR_MIN": 1.25,
  "_DCAM_UNCERTAIN_ALERT_COUNT": 1200,
  "_DCAM_UNCERTAIN_RESET_COUNT": 40,
  "_HI_STD_FALLBACK_TIME": 200,
  "_DISTRACTED_FILTER_TS": 0.25,
  "_POSE_OFFSET_MIN_COUNT": 1200,
  "_POSE_OFFSET_MAX_COUNT": 7200,
  "_WHEELPOS_FILTER_MIN_COUNT": 300,
}


def settings_from_source(policy_hook, overrides=None):
  # Execute the real initializer without importing native hardware/IPC.
  path = Path(__file__).resolve().parents[2] / "selfdrive/monitoring/policy.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  settings_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DRIVER_MONITOR_SETTINGS")
  for node in ast.walk(settings_class):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
      key = node.targets[0].attr
      if overrides and key in overrides:
        node.value = ast.parse(repr(overrides[key]), mode="eval").body
  module = ast.fix_missing_locations(ast.Module(body=[settings_class], type_ignores=[]))
  namespace = {"DT_DMON": 0.05, "apply_driver_monitoring_policy": policy_hook}
  exec(compile(module, str(path), "exec"), namespace)
  return namespace["DRIVER_MONITOR_SETTINGS"]()


def upstream_settings():
  return settings_from_source(lambda settings: None)


class TestDriverMonitoringTiming(unittest.TestCase):
  def setUp(self):
    # The overlay uses the real monitor interval; keep these host tests native-free.
    realtime = patch.dict("sys.modules", {"openpilot.common.realtime": SimpleNamespace(DT_DMON=0.05)})
    realtime.start()
    self.addCleanup(realtime.stop)

  def test_default_matches_upstream_and_never_disables_monitoring(self):
    settings = upstream_settings()
    before = vars(settings).copy()
    apply_driver_monitoring_policy(settings, 100)
    self.assertEqual({key: getattr(settings, key) for key in before}, before)
    self.assertEqual(settings._NO_RESPONSE_TIMEOUT, 5.)
    self.assertEqual(settings._MAX_ALERT_3, 2)
    self.assertEqual(settings._MAX_NO_RESPONSE, 1)

  def test_first_reminder_shifts_timeline_without_stacking_multipliers(self):
    for percent in range(50, 251, 5):
      with self.subTest(percent=percent):
        settings = upstream_settings()
        before = vars(settings).copy()
        apply_driver_monitoring_policy(settings, percent)
        edited = set()
        for policy in ("VISION", "WHEELTOUCH"):
          keys = [f"_{policy}_POLICY_ALERT_{level}_TIMEOUT" for level in (1, 2, 3)]
          old = [before[key] for key in keys]
          new = [getattr(settings, key) for key in keys]
          self.assertAlmostEqual(new[0], old[0] * percent / 100)
          self.assertAlmostEqual(new[1] - new[0], old[1] - old[0])
          self.assertAlmostEqual(new[2] - new[1], old[2] - old[1])
          self.assertLess(new[2] + settings._NO_RESPONSE_TIMEOUT, 60.)
          edited.update(keys)
        for key in before.keys() - edited:
          self.assertEqual(getattr(settings, key), before[key])

  def test_250_percent_exact_schedule(self):
    settings = upstream_settings()
    apply_driver_monitoring_policy(settings, 250)
    self.assertEqual([getattr(settings, f"_VISION_POLICY_ALERT_{n}_TIMEOUT") for n in (1, 2, 3)], [12.5, 15.5, 20.5])
    self.assertEqual([getattr(settings, f"_WHEELTOUCH_POLICY_ALERT_{n}_TIMEOUT") for n in (1, 2, 3)], [12.5, 22.5, 32.5])

  def test_reapplication_never_compounds_and_100_restores_upstream(self):
    settings = upstream_settings()
    before = vars(settings).copy()
    apply_driver_monitoring_policy(settings, 250)
    tuned = copy.deepcopy(vars(settings))
    apply_driver_monitoring_policy(settings, 250)
    self.assertEqual(vars(settings), tuned)
    apply_driver_monitoring_policy(settings, 100)
    self.assertEqual({key: getattr(settings, key) for key in before}, before)

  def test_malformed_values_fall_back_to_upstream(self):
    for value in (True, False, 0, 49, 251, 55.0, "nan", "inf", "100.0", " 100", b"\xff", [], {}, 51, "1" * 5000):
      with self.subTest(value=value):
        self.assertIsNone(validate_reminder_percent(value))
        settings = upstream_settings()
        before = vars(settings).copy()
        apply_driver_monitoring_policy(settings, value)
        self.assertEqual({key: getattr(settings, key) for key in before}, before)
    for value in (50, "100", b"250"):
      self.assertEqual(validate_reminder_percent(value), int(value))

  def test_clean_build_has_no_customization(self):
    self.assertFalse(clean_monitoring.monitoring_customization_available())
    self.assertIsNone(clean_monitoring.validate_reminder_percent(250))
    for percent in (None, 50, 100, 250):
      settings = upstream_settings()
      before = vars(settings).copy()
      clean_monitoring.apply_driver_monitoring_policy(settings, percent)
      self.assertEqual(vars(settings), before)

  def test_clean_restores_upstream_timings_after_development_constant_edits(self):
    overrides = {key: [999] if isinstance(value, list) else 999 for key, value in UPSTREAM_TIMINGS.items()}
    development = settings_from_source(lambda settings: apply_driver_monitoring_policy(settings, 100), overrides)
    self.assertEqual({key: getattr(development, key) for key in overrides}, overrides)

    for percent in (None, 50, 100, 250):
      with self.subTest(percent=percent):
        clean = settings_from_source(lambda settings: clean_monitoring.apply_driver_monitoring_policy(settings, percent), overrides)
        self.assertEqual({key: getattr(clean, key) for key in UPSTREAM_TIMINGS}, UPSTREAM_TIMINGS)
        # No unrelated detection thresholds or saved-setting state is rewritten.
        baseline = upstream_settings()
        self.assertEqual({key: value for key, value in vars(clean).items() if key not in UPSTREAM_TIMINGS},
                         {key: value for key, value in vars(baseline).items() if key not in UPSTREAM_TIMINGS})

  def test_development_hook_still_applies_each_saved_timing_selection(self):
    for percent in (50, 100, 250):
      expected = upstream_settings()
      apply_driver_monitoring_policy(expected, percent)
      actual = settings_from_source(lambda settings: apply_driver_monitoring_policy(settings, percent))
      self.assertEqual(vars(actual), vars(expected))

  def test_clean_panel_removal_preserves_other_settings(self):
    document = {"sections": [{"id": "nrdr", "description": "Customize steering and driver monitoring.", "sub_panels": [
      {"id": "nrdr_driver_monitoring", "items": [{"key": "NrdrDriverMonitoringReminderPercent"}]},
      {"id": "nrdr_other", "items": [{"key": "ExistingSetting"}]},
    ]}]}
    before = copy.deepcopy(document)
    result = without_monitoring_panel(document)
    self.assertEqual(result["sections"][0]["description"], "Customize steering, cruise control, and device behavior.")
    self.assertEqual(result["sections"][0]["sub_panels"], [before["sections"][0]["sub_panels"][1]])
    self.assertEqual(document, before)
    with self.assertRaises(ValueError):
      without_monitoring_panel(result)

  def test_clean_removes_timing_controls_and_copy_from_both_real_schemas(self):
    root = Path(__file__).resolve().parents[2]
    documents = (
      yaml.safe_load((root / "nrdr/ui/sunnylink/pages/steering.yaml").read_text(encoding="utf-8")),
      json.loads((root / "sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8")),
    )
    for document in documents:
      before = copy.deepcopy(document)
      result = without_monitoring_panel(document)
      serialized = json.dumps(result)
      self.assertNotIn("NrdrDriverMonitoringReminderPercent", serialized)
      self.assertNotIn("nrdr_driver_monitoring", serialized)
      self.assertNotIn("First Reminder Timing", serialized)
      self.assertNotIn("Customize steering, cruise control, device behavior, and driver monitoring.", serialized)
      self.assertIn("Customize steering, cruise control, and device behavior.", serialized)
      self.assertEqual(document, before)
