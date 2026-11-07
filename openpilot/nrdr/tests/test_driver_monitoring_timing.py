import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.nrdr.hooks.driver_monitoring import apply_driver_monitoring_policy, validate_reminder_percent
from openpilot.nrdr.tools.release.clean_overlay import driver_monitoring as clean_monitoring
from openpilot.nrdr.tools.release.clean_overlay.strip_monitoring_ui import without_monitoring_panel


def upstream_settings():
  # Read the actual upstream constants without importing native hardware/IPC.
  path = Path(__file__).resolve().parents[2] / "selfdrive/monitoring/policy.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  settings_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DRIVER_MONITOR_SETTINGS")
  values = {}
  for node in ast.walk(settings_class):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
      try:
        values[node.targets[0].attr] = ast.literal_eval(node.value)
      except (ValueError, TypeError):
        pass
  return SimpleNamespace(**values)


class TestDriverMonitoringTiming(unittest.TestCase):
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
    for percent in (50, 100, 250):
      settings = upstream_settings()
      before = vars(settings).copy()
      clean_monitoring.apply_driver_monitoring_policy(settings, percent)
      self.assertEqual(vars(settings), before)

  def test_clean_panel_removal_preserves_other_settings(self):
    document = {"sections": [{"id": "nrdr", "sub_panels": [
      {"id": "nrdr_driver_monitoring", "items": [{"key": "NrdrDriverMonitoringReminderPercent"}]},
      {"id": "nrdr_other", "items": [{"key": "ExistingSetting"}]},
    ]}]}
    before = copy.deepcopy(document)
    result = without_monitoring_panel(document)
    self.assertEqual(result["sections"][0]["sub_panels"], [before["sections"][0]["sub_panels"][1]])
    self.assertEqual(document, before)
    with self.assertRaises(ValueError):
      without_monitoring_panel(result)
