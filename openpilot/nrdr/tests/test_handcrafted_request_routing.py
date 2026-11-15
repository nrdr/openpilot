"""Exercise real Sunnylink request routing without importing native runtime modules."""

import ast
import base64
import gzip
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch


ROOT = Path(__file__).resolve().parents[2]
COMMAND_KEY = "NrdrHandcraftedLateralTune"
CONTEXT_KEY = "NrdrHandcraftedLateralRequest"


def _load_definitions(relative_path, names, namespace):
  path = ROOT / relative_path
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  selected = []
  found = set()
  for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in names:
      node.decorator_list = []
      selected.append(node)
      found.add(node.name)
    elif isinstance(node, ast.Assign):
      assigned = {target.id for target in node.targets if isinstance(target, ast.Name)}
      if assigned & names:
        selected.append(node)
        found.update(assigned & names)
  if found != names:
    raise AssertionError(f"Missing production definitions in {relative_path}: {names - found}")
  exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


class TestHandcraftedRequestRouting(unittest.TestCase):
  def setUp(self):
    self.params = SimpleNamespace(
      get_bool=Mock(return_value=True),
      get=Mock(return_value="0"),
      put=Mock(),
      put_bool=Mock(),
    )
    self.request = Mock(return_value=True)
    self.generic_write = Mock()
    self.namespace = {
      "base64": base64,
      "gzip": gzip,
      "params": self.params,
      "cloudlog": SimpleNamespace(warning=Mock(), error=Mock()),
      "_vehicle_tuning_capabilities": Mock(return_value={"has_handcrafted_lateral_profile": True}),
      "request_stored_handcrafted_lateral_profile": self.request,
      "save_param_from_base64_encoded_string": self.generic_write,
    }
    _load_definitions("nrdr/features/services/sunnylink.py", {
      "ONROAD_WRITE_BLOCKLIST", "HONDA_TUNING_WRITE_KEYS", "allow_param_write",
    }, self.namespace)
    _load_definitions("sunnypilot/sunnylink/athena/sunnylinkd.py", {
      "BLOCKED_PARAMS", "_remote_bool_value", "_remote_int_value", "saveParams",
    }, self.namespace)
    self.save_params = self.namespace["saveParams"]

  @staticmethod
  def _encode(raw, compression=False):
    return base64.b64encode(gzip.compress(raw) if compression else raw).decode("ascii")

  def test_true_routes_only_through_bound_request(self):
    for compression in (False, True):
      with self.subTest(compression=compression):
        self.request.reset_mock()
        self.save_params({COMMAND_KEY: self._encode(b"1", compression)}, compression)
        self.request.assert_called_once_with(self.params)
        self.generic_write.assert_not_called()

  def test_rejected_bound_request_never_falls_through_to_generic_write(self):
    self.request.return_value = False
    self.save_params({COMMAND_KEY: self._encode(b"true")})
    self.request.assert_called_once_with(self.params)
    self.generic_write.assert_not_called()

  def test_false_preserves_generic_cancellation(self):
    for compression in (False, True):
      with self.subTest(compression=compression):
        self.generic_write.reset_mock()
        value = self._encode(b"0", compression)
        self.save_params({COMMAND_KEY: value}, compression)
        self.generic_write.assert_called_once_with(COMMAND_KEY, value, compression)
        self.request.assert_not_called()

  def test_onroad_true_is_not_routed_or_written(self):
    self.params.get_bool.return_value = False
    self.save_params({COMMAND_KEY: self._encode(b"1")})
    self.request.assert_not_called()
    self.generic_write.assert_not_called()

  def test_remote_context_is_blocked_before_policy_or_routing(self):
    for offroad in (False, True):
      with self.subTest(offroad=offroad):
        self.params.get_bool.return_value = offroad
        # Even an overly permissive admission policy cannot bypass the RPC blocklist.
        policy = Mock(return_value=True)
        self.namespace["allow_param_write"] = policy
        self.save_params({CONTEXT_KEY: self._encode(b'{"version":18}')})
        policy.assert_not_called()
        self.request.assert_not_called()
        self.generic_write.assert_not_called()

  def test_policy_independently_rejects_context_in_both_road_states(self):
    for onroad in (False, True):
      with self.subTest(onroad=onroad):
        self.assertFalse(self.namespace["allow_param_write"](
          CONTEXT_KEY, onroad, handcrafted_profile_available=True,
          honda_tuning_available=True, requested_bool=True,
        ))

  def test_device_yaw_switch_requires_device_owned_support_and_preserves_controller_choice(self):
    key = "NrdrDeviceYawCorrection"
    for honda, supported, expected in ((True, True, True), (True, False, False), (True, None, False), (False, True, False)):
      for onroad in (False, True):
        with self.subTest(honda=honda, supported=supported, onroad=onroad):
          self.generic_write.reset_mock()
          self.params.put.reset_mock()
          self.params.get_bool.return_value = not onroad
          self.namespace["_vehicle_tuning_capabilities"].return_value = {
            "nrdr_honda_tuning_available": honda,
            "nrdr_interpolated_torque_pif_blend_available": supported,
          }
          self.save_params({key: self._encode(b"0")})
          self.assertEqual(self.generic_write.called, expected)
          if expected:
            self.generic_write.assert_called_once_with(key, self._encode(b"0"), False)
          self.assertNotIn("NrdrLateralController", [call.args[0] for call in self.params.put.call_args_list])

  def test_device_yaw_switch_respects_suggested_and_full_yaw_locks_on_server(self):
    key = "NrdrDeviceYawCorrection"
    self.namespace["_vehicle_tuning_capabilities"].return_value = {
      "nrdr_honda_tuning_available": True,
      "nrdr_interpolated_torque_pif_blend_available": True,
    }
    for locked in ({"NrdrSuggestedSettings": True}, {"NrdrHandcraftedLateralTune": True}, {"NrdrLateralController": 1}):
      with self.subTest(locked=locked):
        self.generic_write.reset_mock()
        self.params.get.side_effect = lambda name, locked=locked, **_: locked.get(name, "0")
        self.save_params({key: self._encode(b"0")})
        self.generic_write.assert_not_called()

  def test_geometry_is_shared_and_only_scheduled_firmware_delay_is_locked(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {
      "nrdr_honda_tuning_available": True,
    }
    for scheduled in (False, True):
      self.namespace["_vehicle_tuning_capabilities"].return_value["nrdr_firmware_prediction_schedule"] = scheduled
      for suggested in (False, True):
        values = {"NrdrLateralController": 1, "NrdrSuggestedSettings": suggested}
        self.params.get.side_effect = lambda name, values=values, **_: values.get(name, "0")
        for key, raw in (("NrdrSteerRatioMode", b"2"), ("LagdToggle", b"0"), ("LagdToggleDelay", b"0.3")):
          with self.subTest(scheduled=scheduled, suggested=suggested, key=key):
            self.generic_write.reset_mock()
            value = self._encode(raw)
            self.save_params({key: value})
            if suggested or (scheduled and key in ("LagdToggle", "LagdToggleDelay")):
              self.generic_write.assert_not_called()
            else:
              self.generic_write.assert_called_once_with(key, value, False)

  def test_controller_change_onroad_is_rpc_error_and_never_saves_or_updates_version(self):
    self.params.get_bool.return_value = False
    with self.assertRaisesRegex(ValueError, "offroad"):
      self.save_params({"NrdrLateralController": self._encode(b"1")})
    self.params.put.assert_not_called()
    self.generic_write.assert_not_called()

  def test_controller_choice_validates_support_and_reports_invalid_values(self):
    for available, value in ((False, b"1"), (True, b"2"), (True, b"garbage"), (True, b"1.0")):
      with self.subTest(available=available, value=value):
        self.namespace["_vehicle_tuning_capabilities"].return_value = {
          "nrdr_honda_tuning_available": True, "nrdr_yaw_controller_available": available,
        }
        with self.assertRaises(ValueError):
          self.save_params({"NrdrLateralController": self._encode(value)})
        self.params.put.assert_not_called()

  def test_controller_choice_is_saved_and_read_back_offroad(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {
      "nrdr_honda_tuning_available": True, "nrdr_yaw_controller_available": True,
    }
    for value in (0, 1):
      for compression in (False, True):
        with self.subTest(value=value, compression=compression):
          stored = {"NrdrLateralController": 1 - value}
          self.params.get.side_effect = lambda key, stored=stored, **_: stored.get(key, 0)
          self.params.put.side_effect = lambda key, value, stored=stored, **_: stored.update({key: value})
          self.save_params({"NrdrLateralController": self._encode(str(value).encode(), compression)}, compression)
          self.assertEqual(stored["NrdrLateralController"], value)
          self.assertNotIn("NrdrDeviceYawCorrection", stored)

  def test_controller_choice_readback_failure_propagates_error(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {
      "nrdr_honda_tuning_available": True, "nrdr_yaw_controller_available": True,
    }
    with self.assertRaisesRegex(ValueError, "could not be saved"):
      self.save_params({"NrdrLateralController": self._encode(b"1")})

  def test_controller_write_rechecks_road_state_after_validation(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {
      "nrdr_honda_tuning_available": True, "nrdr_yaw_controller_available": True,
    }
    self.params.get_bool.side_effect = [True, False]
    with self.assertRaisesRegex(ValueError, "could not be saved"):
      self.save_params({"NrdrLateralController": self._encode(b"1")})
    self.params.put.assert_not_called()

  def test_monitoring_timing_validates_and_reads_back_offroad(self):
    key = "NrdrDriverMonitoringReminderPercent"
    for percent in (50, 100, 250):
      for compression in (False, True):
        with self.subTest(percent=percent, compression=compression):
          stored = {}
          self.params.get.side_effect = lambda key, _stored=stored, **_: _stored.get(key, 0)
          self.params.put.side_effect = lambda key, value, _stored=stored, **_: _stored.update({key: value})
          self.save_params({key: self._encode(str(percent).encode(), compression)}, compression)
          self.assertEqual(stored[key], percent)
          self.generic_write.assert_not_called()

  def test_monitoring_timing_rejects_disable_and_malformed_requests(self):
    key = "NrdrDriverMonitoringReminderPercent"
    for value in (b"0", b"49", b"251", b"99", b"100.0", b" 100", b"nan", b"\xff"):
      with self.subTest(value=value), self.assertRaises(ValueError):
        self.save_params({key: self._encode(value)})
    self.params.put.assert_not_called()
    self.generic_write.assert_not_called()

  def test_monitoring_timing_rejects_onroad_clean_and_racing_transitions(self):
    key = "NrdrDriverMonitoringReminderPercent"
    request = {key: self._encode(b"250")}
    self.params.get_bool.return_value = False
    with self.assertRaisesRegex(ValueError, "offroad"):
      self.save_params(request)
    self.params.get_bool.return_value = True
    with patch("openpilot.nrdr.hooks.driver_monitoring.monitoring_customization_available", return_value=False):
      with self.assertRaisesRegex(ValueError, "non-clean"):
        self.save_params(request)
    self.params.get_bool.side_effect = [True, False]
    with self.assertRaisesRegex(ValueError, "could not be saved"):
      self.save_params(request)
    self.params.put.assert_not_called()
    self.generic_write.assert_not_called()

  def test_monitoring_timing_readback_failure_is_reported(self):
    with self.assertRaisesRegex(ValueError, "could not be saved"):
      self.save_params({"NrdrDriverMonitoringReminderPercent": self._encode(b"250")})

  def test_remote_road_state_cannot_unlock_monitoring_timing(self):
    stored = {"IsOffroad": False}
    self.params.get_bool.side_effect = lambda key: bool(stored.get(key, False))
    self.params.get.side_effect = lambda key, **_: stored.get(key, 0)
    self.params.put.side_effect = lambda key, value, **_: stored.update({key: value})
    self.generic_write.side_effect = lambda key, value, compression: stored.update({key: base64.b64decode(value) == b"1"})
    self.save_params({"IsOffroad": self._encode(b"1")})
    self.generic_write.assert_not_called()
    self.assertFalse(stored["IsOffroad"])
    with self.assertRaisesRegex(ValueError, "offroad"):
      self.save_params({"NrdrDriverMonitoringReminderPercent": self._encode(b"250")})
    self.assertNotIn("NrdrDriverMonitoringReminderPercent", stored)

  def test_remote_requests_cannot_reset_or_poison_monitoring_lockout(self):
    for key in ("DriverLockoutCount", "DriverTooDistracted"):
      for raw in (b"0", b"-100", b"999999"):
        with self.subTest(key=key, raw=raw):
          self.save_params({key: self._encode(raw)})
          self.generic_write.assert_not_called()
          self.assertFalse(any(call.args[0] == key for call in self.params.put.call_args_list))

  def test_lane_guidance_mode_is_validated_and_mirrors_the_legacy_bool(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {"custom_model_active": True}
    for mode in (0, 1, 2):
      for compression in (False, True):
        with self.subTest(mode=mode, compression=compression):
          self.params.put.reset_mock()
          self.params.put_bool.reset_mock()
          self.generic_write.reset_mock()
          self.save_params({"LaneGuidanceMode": self._encode(str(mode).encode(), compression)}, compression)
          mode_writes = [call for call in self.params.put.call_args_list if call.args[0] == "LaneGuidanceMode"]
          self.assertEqual(mode_writes, [call("LaneGuidanceMode", mode, block=True)])
          self.params.put_bool.assert_called_once_with("LaneCentering", mode == 1, block=True)
          self.generic_write.assert_not_called()

  def test_lane_guidance_rejects_invalid_values_and_blendful_without_a_custom_model(self):
    self.namespace["_vehicle_tuning_capabilities"].return_value = {"custom_model_active": True}
    for value in (b"-1", b"3", b"1.0", b" 1", b"+1", b"garbage"):
      with self.subTest(value=value):
        self.params.put.reset_mock()
        self.params.put_bool.reset_mock()
        with self.assertRaisesRegex(ValueError, "Invalid Lane Centering Method"):
          self.save_params({"LaneGuidanceMode": self._encode(value)})
        self.params.put.assert_not_called()
        self.params.put_bool.assert_not_called()

    self.namespace["_vehicle_tuning_capabilities"].return_value = {"custom_model_active": False}
    with self.assertRaisesRegex(ValueError, "custom model"):
      self.save_params({"LaneGuidanceMode": self._encode(b"2")})
    self.params.put.assert_not_called()
    self.params.put_bool.assert_not_called()


if __name__ == "__main__":
  unittest.main()
