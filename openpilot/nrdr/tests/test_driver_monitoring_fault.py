"""Focused DM fail-closed checks using production code without native IPC/hardware."""

import ast
from collections import defaultdict
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[2]
DM_SERVICE = "driverMonitoringState"


def source_tree(relative_path):
  return ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))


def execute_nodes(nodes, namespace):
  # Preserve annotations without needing the native types they refer to.
  future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
  module = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
  exec(compile(module, "<production DM definitions>", "exec"), namespace)


def production_class(relative_path, name):
  return next(node for node in source_tree(relative_path).body if isinstance(node, ast.ClassDef) and node.name == name)


class Names:
  def __getattr__(self, name):
    return name


class TestDriverMonitoringFault(unittest.TestCase):
  def setUp(self):
    self.namespace = {
      "SIMULATION": False, "REPLAY": False,
      "EventName": Names(), "AlertLevel": Names(), "MonitoringPolicy": Names(),
      "ButtonType": Names(), "time": SimpleNamespace(monotonic=lambda: 100.),
      "custom": SimpleNamespace(OnroadEventSP=SimpleNamespace(EventName=Names())),
      "set_offroad_alert": Mock(),
    }
    method = next(node for node in production_class("selfdrive/selfdrived/selfdrived.py", "SelfdriveD").body
                  if isinstance(node, ast.FunctionDef) and node.name == "update_events")
    # Execute the real prefix, including startup/passive returns and model loading,
    # through the top-level DM block; no imitation of the admission logic.
    dm_index = next(index for index, node in enumerate(method.body)
                    if isinstance(node, ast.If) and ast.unparse(node.test) == "not self.CP.notCar")
    method.body = method.body[:dm_index + 1]
    execute_nodes([method], self.namespace)

    submaster = production_class("cereal/messaging/__init__.py", "SubMaster")
    submaster.body = [node for node in submaster.body if isinstance(node, ast.FunctionDef) and node.name in
                     ("__getitem__", "_check_avg_freq", "all_alive", "all_freq_ok", "all_valid", "all_checks")]
    messaging_namespace = {"SERVICE_LIST": {DM_SERVICE: SimpleNamespace(frequency=20.)}}
    execute_nodes([submaster], messaging_namespace)
    self.sm = messaging_namespace["SubMaster"]()
    self.sm.services = [DM_SERVICE, "modelV2", "cabinCameraState"]
    self.sm.alive = dict.fromkeys(self.sm.services, True)
    self.sm.valid = dict(self.sm.alive)
    self.sm.freq_ok = dict(self.sm.alive)
    self.sm.seen = dict(self.sm.alive)
    self.sm.ignore_alive = []
    self.sm.ignore_average_freq = []
    self.sm.ignore_valid = []
    self.sm.recv_frame = {"lateralManeuverPlan": 0, "alertDebug": 0}
    self.sm.updated = {"userBookmark": False}
    self.sm.data = {
      DM_SERVICE: SimpleNamespace(lockout=False, alwaysOnLockout=False, activePolicy="vision", alertLevel="none",
                                  visionPolicyState=SimpleNamespace(uncertainOffroadAlertPercent=0)),
      "longitudinalPlanSP": SimpleNamespace(events=[]),
      "controlsState": SimpleNamespace(lateralControlState=SimpleNamespace(which=lambda: "pidState")),
      "deviceState": SimpleNamespace(chestnutPresent=True),
    }
    self.sm.all_checks = Mock(wraps=self.sm.all_checks)
    self.events = set()
    self.selfdrive = SimpleNamespace(
      CP=SimpleNamespace(notCar=False, passive=False, pcmCruise=True), sm=self.sm,
      events=self.events, events_sp=Mock(), params=SimpleNamespace(get_bool=lambda key: False, get=lambda key: None),
      initialized=True, enabled=False, startup_event=None, dm_lockout_set=False, dm_uncertain_alerted=False,
      big_model_loading=False, big_model_active=False, big_model_failed=False, big_model_ready_t=0.,
    )
    self.car_state = SimpleNamespace(buttonEvents=[], vCruise=100.)

  def update(self):
    self.namespace["update_events"](self.selfdrive, self.car_state)

  def test_stale_invalid_and_low_frequency_fail_independently(self):
    for attribute in ("alive", "valid", "freq_ok"):
      with self.subTest(attribute=attribute):
        getattr(self.sm, attribute)[DM_SERVICE] = False
        self.update()
        self.assertIn("driverMonitoringFault", self.events)
        getattr(self.sm, attribute)[DM_SERVICE] = True
        self.update()
        self.assertNotIn("driverMonitoringFault", self.events)
    self.assertTrue(all(call.args == ([DM_SERVICE],) for call in self.sm.all_checks.call_args_list))

  def test_never_received_monitoring_fails_after_initialization(self):
    self.sm.seen[DM_SERVICE] = self.sm.alive[DM_SERVICE] = self.sm.valid[DM_SERVICE] = False
    self.update()
    self.assertIn("driverMonitoringFault", self.events)

  def test_driving_model_loading_or_settling_cannot_suppress_dm_fault(self):
    self.sm.valid[DM_SERVICE] = False
    for loading in (False, True):
      with self.subTest(loading=loading):
        self.selfdrive.big_model_loading = loading
        self.selfdrive.big_model_ready_t = 100.
        self.selfdrive.params.get_bool = Mock(return_value=loading)
        self.update()
        self.assertIn("driverMonitoringFault", self.events)

  def test_unrelated_camera_or_model_fault_does_not_raise_dm_fault(self):
    for service in ("modelV2", "cabinCameraState"):
      self.sm.alive[service] = self.sm.valid[service] = self.sm.freq_ok[service] = False
    self.update()
    self.assertNotIn("driverMonitoringFault", self.events)

  def test_simulation_notcar_startup_and_passive_exemptions(self):
    self.sm.valid[DM_SERVICE] = False
    for target, attribute in ((self.selfdrive.CP, "notCar"), (self.selfdrive.CP, "passive")):
      with self.subTest(attribute=attribute):
        setattr(target, attribute, True)
        self.update()
        self.assertNotIn("driverMonitoringFault", self.events)
        setattr(target, attribute, False)
    self.selfdrive.initialized = False
    self.update()
    self.assertEqual(self.events, {"selfdriveInitializing"})
    self.selfdrive.initialized = True
    self.namespace["SIMULATION"] = True
    self.update()
    self.assertNotIn("driverMonitoringFault", self.events)
    self.sm.all_checks.assert_not_called()

  def test_replay_retains_submaster_health_and_ignore_semantics(self):
    self.namespace.update(SIMULATION=True, REPLAY=True)
    self.update()
    self.assertNotIn("driverMonitoringFault", self.events)
    self.sm.valid[DM_SERVICE] = False
    self.update()
    self.assertIn("driverMonitoringFault", self.events)
    self.sm.alive[DM_SERVICE] = self.sm.freq_ok[DM_SERVICE] = False
    self.sm.ignore_alive = self.sm.ignore_average_freq = self.sm.ignore_valid = [DM_SERVICE]
    self.update()
    self.assertNotIn("driverMonitoringFault", self.events)

  def test_existing_warning_and_lockout_events_remain_active(self):
    dm = self.sm.data[DM_SERVICE]
    self.selfdrive.params.put_bool = Mock()
    for policy, prefix in (("vision", "driverDistracted"), ("wheeltouch", "driverUnresponsive")):
      for number, level in enumerate(("one", "two", "three"), 1):
        dm.activePolicy, dm.alertLevel, dm.lockout = policy, level, True
        self.update()
        self.assertEqual(self.events, {f"{prefix}{number}", "tooDistracted"})

  def test_dedicated_event_blocks_entry_and_soft_disables_without_generic_events(self):
    namespace = {"State": Names(), "DT_CTRL": .01}
    execute_nodes([production_class("sunnypilot/selfdrive/selfdrived/events_base.py", "ET")], namespace)
    et = namespace["ET"]
    events_tree = source_tree("selfdrive/selfdrived/events.py")
    mapping = next(node.value for node in events_tree.body if isinstance(node, ast.AnnAssign)
                   and isinstance(node.target, ast.Name) and node.target.id == "EVENTS")
    handlers = next(value for key, value in zip(mapping.keys, mapping.values, strict=True)
                    if isinstance(key, ast.Attribute) and key.attr == "driverMonitoringFault")
    handler_namespace = {"ET": et, "NoEntryAlert": lambda text: text, "soft_disable_alert": lambda text: text}
    handler_map = eval(compile(ast.Expression(handlers), "<DM event handlers>", "eval"), handler_namespace)
    self.assertEqual(set(handler_map), {et.NO_ENTRY, et.SOFT_DISABLE})
    self.assertIn("Driver Monitoring Unavailable", handler_map[et.SOFT_DISABLE])
    execute_nodes([node for node in source_tree("selfdrive/selfdrived/state.py").body
                   if not isinstance(node, (ast.Import, ast.ImportFrom)) and not
                   (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "State" for t in node.targets))], namespace)
    event_types = set(handler_map) | {et.ENABLE}
    events = SimpleNamespace(contains=lambda event_type: event_type in event_types)
    machine = namespace["StateMachine"]()
    machine.update(events)
    self.assertEqual(machine.state, "disabled")
    self.assertIn(et.NO_ENTRY, machine.current_alert_types)
    event_types.discard(et.ENABLE)
    machine.state = "enabled"
    machine.update(events)
    self.assertEqual(machine.state, "softDisabling")
    # A recovered stream clears the dedicated event and cancels the countdown.
    event_types.clear()
    machine.update(events)
    self.assertEqual(machine.state, "enabled")
    event_types.update(handler_map)
    machine.update(events)
    for _ in range(int(namespace["SOFT_DISABLE_TIME"] / namespace["DT_CTRL"])):
      machine.update(events)
    self.assertEqual(machine.state, "disabled")

  def test_schema_appends_event_105_without_duplicate_ordinals(self):
    schema = (ROOT / "cereal/log.capnp").read_text(encoding="utf-8")
    enum = re.search(r"enum EventName\s+@[^\{]+\{(.*?)\n  \}", schema, re.DOTALL).group(1)
    values = re.findall(r"(\w+)\s+@(\d+);", enum)
    self.assertEqual(dict(values)["driverMonitoringFault"], "105")
    self.assertEqual(len(values), len({ordinal for _, ordinal in values}))
    self.assertEqual({int(ordinal) for _, ordinal in values}, set(range(106)))

  def test_mads_cannot_bypass_fault_for_lateral_only_engagement(self):
    namespace = {"State": Names(), "EventName": Names(), "EventNameSP": Names(), "DT_CTRL": .01, "SOFT_DISABLE_TIME": 3}
    execute_nodes([production_class("sunnypilot/selfdrive/selfdrived/events_base.py", "ET")], namespace)
    hook_nodes = [node for node in source_tree("nrdr/hooks/events.py").body
                  if (isinstance(node, ast.FunctionDef) and node.name == "keep_lateral_active") or
                  (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_LATERAL_ONLY_CAR_EVENTS"
                                                       for t in node.targets))]
    execute_nodes(hook_nodes, namespace)
    self.assertFalse(namespace["keep_lateral_active"]("driverMonitoringFault"))
    execute_nodes([node for node in source_tree("sunnypilot/mads/state.py").body
                   if not isinstance(node, (ast.Import, ast.ImportFrom)) and not
                   (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("State", "EventName", "EventNameSP")
                                                        for t in node.targets))], namespace)
    et = namespace["ET"]
    events_tree = source_tree("selfdrive/selfdrived/events.py")
    mapping = next(node.value for node in events_tree.body if isinstance(node, ast.AnnAssign)
                   and isinstance(node.target, ast.Name) and node.target.id == "EVENTS")
    handlers = next(value for key, value in zip(mapping.keys, mapping.values, strict=True)
                    if isinstance(key, ast.Attribute) and key.attr == "driverMonitoringFault")
    fault_types = {getattr(et, key.attr): None for key in handlers.keys}
    event_map = {"driverMonitoringFault": fault_types, "pcmEnable": {et.ENABLE: None}}
    self.selfdrive.events = SimpleNamespace(names=list(event_map), get_events_mapping=lambda: event_map)
    self.selfdrive.events_sp = SimpleNamespace(contains=lambda event_type: False, has=lambda event: False,
                                              contains_in_list=lambda events: False)
    self.selfdrive.state_machine = SimpleNamespace(soft_disable_timer=0, current_alert_types=[])
    machine = namespace["StateMachine"](SimpleNamespace(selfdrive=self.selfdrive))
    self.assertEqual(machine.update(), (False, False))
    self.assertIn(et.NO_ENTRY, self.selfdrive.state_machine.current_alert_types)
    machine.state = "enabled"
    machine.update()
    self.assertEqual(machine.state, "softDisabling")
    self.assertEqual(self.selfdrive.state_machine.soft_disable_timer, 300)
    self.selfdrive.state_machine.soft_disable_timer = 0
    self.assertEqual(machine.update(), (False, False))


class TestDriverMonitoringLockoutCount(unittest.TestCase):
  def test_negative_count_is_clamped_before_any_lockout_transition(self):
    namespace = {
      "DT_DMON": .05, "defaultdict": defaultdict, "AlertLevel": Names(), "MonitoringPolicy": Names(),
      "apply_driver_monitoring_policy": lambda settings: None,
      "RunningStatFilter": lambda **kwargs: None, "DriverPose": lambda **kwargs: None, "DriverBlink": lambda: None,
      "FirstOrderFilter": lambda *args: None,
    }
    execute_nodes([production_class("selfdrive/monitoring/policy.py", "DRIVER_MONITOR_SETTINGS"),
                   production_class("selfdrive/monitoring/policy.py", "DriverMonitoring")], namespace)
    for count in (None, -100, -1, 0, 1, 2, 3, 100):
      for cause in ("alert_3_cnt", "no_response_cnt"):
        with self.subTest(count=count, cause=cause):
          params = SimpleNamespace(get=Mock(return_value=count), get_bool=lambda key: False, put=Mock())
          namespace["Params"] = Mock(return_value=params)
          dm = namespace["DriverMonitoring"]()
          expected_count = max(0, count or 0)
          self.assertEqual(dm.lockout_count, expected_count)
          setattr(dm, cause, 2 if cause == "alert_3_cnt" else 1)
          dm._update_events(False, False, False, False)
          self.assertTrue(dm.lockout_active)
          self.assertEqual(dm.lockout_count, expected_count + 1)
          self.assertEqual(dm.lockout_duration, dm.settings._LOCKOUT_TIMES[min(expected_count, 3)])
          params.put.assert_called_once_with("DriverLockoutCount", expected_count + 1)


if __name__ == "__main__":
  unittest.main()
