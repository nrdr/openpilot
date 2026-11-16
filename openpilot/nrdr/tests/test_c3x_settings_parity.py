"""Exercise C3X control registration without importing native graphics or Params."""

import ast
import time
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.nrdr.hooks.driver_monitoring import monitoring_customization_available, validate_reminder_percent
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY
from openpilot.nrdr.tests.test_settings_navigation import _method, _tree
from openpilot.nrdr.tests.test_ui_settings_contract import _items
from openpilot.nrdr.tools.release.clean_overlay import driver_monitoring as clean_monitoring
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema


ROOT = Path(__file__).resolve().parents[3]
SETTINGS = "openpilot/selfdrive/ui/sunnypilot/layouts/settings/"
REMINDER = "NrdrDriverMonitoringReminderPercent"


class Control:
  def __init__(self, *args, **kwargs):
    self.config = kwargs
    self.visible = True

  def set_visible(self, visible):
    self.visible = visible


def load_method(path, class_name, method_name, namespace):
  node = _method(_tree(ROOT / path), class_name, method_name)
  module = ast.Module(body=[node], type_ignores=[])
  exec(compile(module, str(ROOT / path), "exec"), namespace)
  return namespace[method_name]


def registered_items(path, class_name, state, availability=monitoring_customization_available, **dependencies):
  namespace = {"tr": lambda text: text, "ui_state": state, "monitoring_customization_available": availability}
  namespace.update(dependencies)
  namespace.update(dict.fromkeys(("simple_button_item_sp", "option_item_sp", "toggle_item_sp", "LineSeparatorSP"), Control))
  layout = SimpleNamespace(_on_icbm_toggle=lambda _: None, _on_custom_acc_toggle=lambda _: None)
  initialize = load_method(path, class_name, "_initialize_items", namespace)
  return layout, initialize(layout)


class TestC3xSettingsParity(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.items = {item["key"]: item for item in _items(compile_schema(DEFAULT_SRC))}

  def setUp(self):
    self.state = SimpleNamespace(offroad=True, params=SimpleNamespace(get_bool=lambda _: False))
    self.state.is_offroad = lambda: self.state.offroad

  def test_reminder_is_registered_with_matching_range_and_no_vehicle_gate(self):
    layout, items = registered_items("openpilot/nrdr/ui/settings/layout.py", "NrdrLayout", self.state)
    control = layout._monitoring_reminder
    self.assertIn(control, items)
    self.assertIn(layout._monitoring_separator, items)
    self.assertEqual(control.config["param"], REMINDER)
    self.assertEqual([control.config[key] for key in ("min_value", "max_value", "value_change_step")],
                     [self.items[REMINDER][key] for key in ("min", "max", "step")])
    self.assertEqual(control.config["label_callback"](100), "100%")
    self.assertTrue(control.visible())
    self.assertTrue(control.config["enabled"]())  # No CP, vehicle, advanced-controls or model dependency.
    self.state.offroad = False
    self.assertTrue(control.visible())
    self.assertFalse(control.config["enabled"]())
    for value in range(50, 251, 5):
      self.assertEqual(validate_reminder_percent(value), value)

  def test_clean_build_hides_and_disables_reminder(self):
    layout, _ = registered_items("openpilot/nrdr/ui/settings/layout.py", "NrdrLayout", self.state,
                                 clean_monitoring.monitoring_customization_available)
    self.assertFalse(layout._monitoring_reminder.visible())
    self.assertFalse(layout._monitoring_separator.visible())
    self.assertFalse(layout._monitoring_reminder.config["enabled"]())

  def test_reminder_uses_shared_default_persistence_and_remote_refresh(self):
    default = int(PARAM_SPECS_BY_KEY[REMINDER].default)
    self.assertEqual(default, 100)
    stored = {}
    params = SimpleNamespace(get=lambda key, **_: stored.get(key, default), put=lambda key, value: stored.update({key: value}))
    action = SimpleNamespace(params=params, param_key=REMINDER, min_value=50, max_value=250, value_change_step=5,
                             current_value=50, value_map=None, use_float_scaling=False, on_value_changed=None)
    namespace = {"time": time, "tuning_write_allowed": lambda *_: True}
    path = "openpilot/system/ui/sunnypilot/widgets/option_control.py"
    refresh = load_method(path, "OptionControlSP", "_refresh_from_params", namespace)
    save = load_method(path, "OptionControlSP", "set_value", namespace)
    refresh(action, force=True)
    self.assertEqual(action.current_value, 100)
    self.assertEqual(stored, {})  # Opening the page must not seed or overwrite a saved preference.
    save(action, 125)
    self.assertEqual(stored, {REMINDER: 125})
    stored[REMINDER] = 175  # A later Sunnylink edit.
    refresh(action, force=True)
    self.assertEqual(action.current_value, 175)
    self.assertEqual(stored, {REMINDER: 175})
    for invalid in (0, 45, 255):
      save(action, invalid)
      self.assertEqual(stored, {REMINDER: 175})

  def test_post_blinker_delay_is_reachable_without_exposing_torque_controls(self):
    layout, items = registered_items(SETTINGS + "steering.py", "SteeringLayout", self.state)
    self.assertIn(layout._blinker_reengage_delay, items)
    self.assertNotIn(layout._torque_control_toggle, items)
    self.assertNotIn(layout._torque_customization_button, items)
    config = layout._blinker_reengage_delay.config
    self.assertEqual(config["param"], "BlinkerLateralReengageDelay")
    self.assertEqual([config[key] for key in ("min_value", "max_value", "value_change_step")],
                     [self.items[config["param"]][key] for key in ("min", "max", "step")])
    update = ast.unparse(_method(_tree(ROOT / (SETTINGS + "steering.py")), "SteeringLayout", "_update_state"))
    self.assertIn("self._blinker_reengage_delay.set_visible(self._blinker_control_toggle.action_item.get_state())", update)

  def test_long_press_supports_every_remote_increment_without_index_mapping(self):
    layout, items = registered_items(SETTINGS + "cruise.py", "CruiseLayout", self.state)
    self.assertIn(layout.custom_acc_long_increment, items)
    config = layout.custom_acc_long_increment.config
    self.assertEqual(config["param"], "CustomAccLongPressIncrement")
    self.assertNotIn("value_map", config)
    remote = self.items[config["param"]]
    self.assertEqual(list(range(config["min_value"], config["max_value"] + 1, config["value_change_step"])),
                     list(range(remote["min"], remote["max"] + 1, remote["step"])))

  def test_brightness_delay_options_match_native_runtime_values(self):
    path = ROOT / "openpilot/sunnypilot/system/params_migration.py"
    assignment = next(node for node in _tree(path).body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "ONROAD_BRIGHTNESS_TIMER_VALUES" for target in node.targets))
    namespace = {}
    exec(compile(ast.Module(body=[assignment], type_ignores=[]), str(path), "exec"), namespace)
    values = list(namespace["ONROAD_BRIGHTNESS_TIMER_VALUES"].values())
    self.assertEqual([option["value"] for option in self.items["OnroadScreenOffTimer"]["options"]], values)
    self.assertNotIn(0, values)  # An expired timer is not an "Always On" mode.
    layout, items = registered_items(SETTINGS + "display.py", "DisplayLayout", self.state, **namespace)
    self.assertIn(layout._onroad_brightness_timer, items)

  def test_always_on_monitoring_remains_in_existing_toggles_panel(self):
    tree = _tree(ROOT / "openpilot/selfdrive/ui/layouts/settings/toggles.py")
    init = _method(tree, "TogglesLayout", "__init__")
    definitions = next(node.value for node in ast.walk(init) if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Attribute) and target.attr == "_toggle_defs" for target in node.targets))
    self.assertIn("AlwaysOnDM", [key.value for key in definitions.keys])
    self.assertIn("Scroller(list(self._toggles.values())", ast.unparse(init))
    self.assertIn("self._toggles[param] = toggle", ast.unparse(init))
