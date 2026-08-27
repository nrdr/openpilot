from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from openpilot.nrdr.features.services.power import AUTOMATIC_POWER_DOWN_GRACE_S, PreventAutomaticShutdownPolicy
from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.ui.settings.device_power import (
  attach_mici_automatic_shutdown_control,
  automatic_shutdown_timer_description,
  automatic_shutdown_timer_enabled,
  automatic_shutdown_toggle_item,
)


class FakeParams:
  def __init__(self, disable_power_down: bool):
    self.disable_power_down = disable_power_down

  def get_bool(self, key: str) -> bool:
    if key != NrdrParamKey.DISABLE_POWER_DOWN:
      raise AssertionError(f"unexpected key: {key}")
    return self.disable_power_down


class TestPreventAutomaticShutdownPolicy(unittest.TestCase):
  def test_boot_state_preserves_existing_behavior(self):
    self.assertTrue(PreventAutomaticShutdownPolicy(FakeParams(False)).allows_automatic_shutdown(100.0))
    self.assertFalse(PreventAutomaticShutdownPolicy(FakeParams(True)).allows_automatic_shutdown(100.0))

  def test_true_to_false_transition_has_exact_bounded_grace(self):
    params = FakeParams(True)
    policy = PreventAutomaticShutdownPolicy(params)
    params.disable_power_down = False

    self.assertFalse(policy.allows_automatic_shutdown(100.0))
    self.assertFalse(policy.allows_automatic_shutdown(100.0 + AUTOMATIC_POWER_DOWN_GRACE_S - 0.001))
    self.assertTrue(policy.allows_automatic_shutdown(100.0 + AUTOMATIC_POWER_DOWN_GRACE_S))

  def test_false_to_true_transition_never_starts_grace(self):
    params = FakeParams(False)
    policy = PreventAutomaticShutdownPolicy(params)
    self.assertTrue(policy.allows_automatic_shutdown(100.0))

    params.disable_power_down = True
    self.assertFalse(policy.allows_automatic_shutdown(101.0))
    self.assertFalse(policy.allows_automatic_shutdown(101.0 + AUTOMATIC_POWER_DOWN_GRACE_S))

  def test_reenabling_cancels_grace_and_next_disable_restarts_it(self):
    params = FakeParams(True)
    policy = PreventAutomaticShutdownPolicy(params)
    params.disable_power_down = False
    self.assertFalse(policy.allows_automatic_shutdown(100.0))

    params.disable_power_down = True
    self.assertFalse(policy.allows_automatic_shutdown(130.0))
    params.disable_power_down = False
    self.assertFalse(policy.allows_automatic_shutdown(160.0))
    self.assertFalse(policy.allows_automatic_shutdown(219.999))
    self.assertTrue(policy.allows_automatic_shutdown(220.0))


class TestPowerUiAdapters(unittest.TestCase):
  @staticmethod
  def _runtime_modules(ui_state, *, toggle_item=None, big_control=None):
    ui_state_module = ModuleType("openpilot.selfdrive.ui.ui_state")
    ui_state_module.ui_state = ui_state
    multilang_module = ModuleType("openpilot.system.ui.lib.multilang")
    multilang_module.tr = lambda text: text

    modules = {
      "openpilot.selfdrive.ui.ui_state": ui_state_module,
      "openpilot.system.ui.lib.multilang": multilang_module,
    }
    if toggle_item is not None:
      list_view_module = ModuleType("openpilot.system.ui.sunnypilot.widgets.list_view")
      list_view_module.toggle_item_sp = toggle_item
      modules["openpilot.system.ui.sunnypilot.widgets.list_view"] = list_view_module
    if big_control is not None:
      button_module = ModuleType("openpilot.selfdrive.ui.mici.widgets.button")
      button_module.BigParamControl = big_control
      modules["openpilot.selfdrive.ui.mici.widgets.button"] = button_module
    return modules

  def test_large_screen_adapter_preserves_widget_and_timer_behavior(self):
    params = FakeParams(False)
    ui_state = SimpleNamespace(is_offroad=lambda: True, params=params)
    widget = object()
    captured = {}

    def toggle_item_sp(**kwargs):
      captured.update(kwargs)
      return widget

    with mock.patch.dict(sys.modules, self._runtime_modules(ui_state, toggle_item=toggle_item_sp)):
      self.assertIs(automatic_shutdown_toggle_item(), widget)
      self.assertEqual(captured["param"], "DisablePowerDown")
      self.assertEqual(captured["title"](), "Prevent Automatic Shutdown")
      self.assertIn("60-second grace period", captured["description"]())
      self.assertTrue(captured["enabled"]())
      self.assertTrue(automatic_shutdown_timer_enabled())
      self.assertIn("30h is the default", automatic_shutdown_timer_description())

      params.disable_power_down = True
      self.assertFalse(automatic_shutdown_timer_enabled())
      ui_state.is_offroad = lambda: False
      params.disable_power_down = False
      self.assertFalse(automatic_shutdown_timer_enabled())

  def test_mici_adapter_returns_and_places_the_exact_control(self):
    ui_state = SimpleNamespace(is_offroad=lambda: True)

    class FakeControl:
      def __init__(self, text, param):
        self.text = text
        self.param = param
        self.value = None
        self.enabled = None

      def set_value(self, value):
        self.value = value

      def set_enabled(self, enabled):
        self.enabled = enabled

    class FakeScroller:
      def __init__(self):
        self.items = [object() for _ in range(6)]

      def add_widget(self, widget):
        self.items.append(widget)

    scroller = FakeScroller()
    original_items = list(scroller.items)
    with mock.patch.dict(sys.modules, self._runtime_modules(ui_state, big_control=FakeControl)):
      control = attach_mici_automatic_shutdown_control(scroller)

    self.assertIs(scroller.items[3], control)
    self.assertEqual(scroller.items[:3], original_items[:3])
    self.assertEqual(scroller.items[4:], original_items[3:])
    self.assertEqual(control.text, "prevent automatic\nshutdown")
    self.assertEqual(control.param, "DisablePowerDown")
    self.assertEqual(control.value, "battery drain risk")
    self.assertTrue(control.enabled())


class TestPowerOwnershipBoundaries(unittest.TestCase):
  @property
  def repository_root(self) -> Path:
    return Path(__file__).resolve().parents[3]

  def test_power_monitoring_retains_only_a_thin_policy_seam(self):
    path = self.repository_root / "openpilot/system/hardware/power_monitoring.py"
    source = path.read_text(encoding="utf-8")

    self.assertIn("from openpilot.nrdr.features.services.power import", source)
    self.assertIn("PreventAutomaticShutdownPolicy(self.params)", source)
    self.assertIn("self._prevent_automatic_shutdown.allows_automatic_shutdown(now)", source)
    self.assertNotIn('get_bool("DisablePowerDown")', source)
    self.assertNotIn("_automatic_power_down_grace_start", source)
    self.assertNotIn("_disable_power_down", source)
    self.assertNotIn("AUTOMATIC_POWER_DOWN_GRACE_S", source)

  def test_host_shutdown_triggers_and_manual_force_order_are_unchanged(self):
    source = (self.repository_root / "openpilot/system/hardware/power_monitoring.py").read_text(encoding="utf-8")
    expected_fragments = (
      "self.max_time_offroad_exceeded(offroad_time)",
      "low_voltage_shutdown",
      "self.car_battery_capacity_uWh <= 0",
      "should_shutdown &= not ignition",
      "should_shutdown &= in_car",
      "should_shutdown &= offroad_time > DELAY_SHUTDOWN_TIME_S",
      'should_shutdown |= self.params.get_bool("ForcePowerDown")',
      "should_shutdown &= started_seen or (now > MIN_ON_TIME_S)",
    )
    for fragment in expected_fragments:
      with self.subTest(fragment=fragment):
        self.assertIn(fragment, source)

    policy_index = source.index("allows_automatic_shutdown(now)")
    force_index = source.index('get_bool("ForcePowerDown")')
    minimum_on_time_index = source.index("started_seen or (now > MIN_ON_TIME_S)")
    self.assertLess(policy_index, force_index)
    self.assertLess(force_index, minimum_on_time_index)

    policy_source = (self.repository_root / "openpilot/nrdr/features/services/power.py").read_text(encoding="utf-8")
    self.assertNotIn("ForcePowerDown", policy_source)

  def test_framework_device_layouts_delegate_nrdr_presentation(self):
    large_source = (self.repository_root / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/device.py").read_text(encoding="utf-8")
    mici_source = (self.repository_root / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py").read_text(encoding="utf-8")

    self.assertIn("from openpilot.nrdr.ui.settings.device_power import", large_source)
    self.assertIn("automatic_shutdown_toggle_item()", large_source)
    self.assertIn("enabled=automatic_shutdown_timer_enabled", large_source)
    self.assertIn("description=automatic_shutdown_timer_description", large_source)
    self.assertNotIn("DisablePowerDown", large_source)
    self.assertNotIn("Prevent Automatic Shutdown", large_source)

    self.assertIn("from openpilot.nrdr.ui.settings.device_power import attach_mici_automatic_shutdown_control", mici_source)
    self.assertIn("attach_mici_automatic_shutdown_control(self._scroller)", mici_source)
    self.assertNotIn("DisablePowerDown", mici_source)
    self.assertNotIn("BigParamControl", mici_source)
    self.assertNotIn("prevent automatic", mici_source.lower())

  def test_sunnylink_device_fragment_has_an_explicit_deferred_integration_note(self):
    source = (self.repository_root / "openpilot/nrdr/ui/settings/device_power.py").read_text(encoding="utf-8")
    self.assertIn("settings_ui_src/pages/device.yaml", source)
    self.assertIn("separate canonical-fragment", source)


if __name__ == "__main__":
  unittest.main()
