from types import MappingProxyType
import unittest
from unittest.mock import patch

from openpilot.nrdr.params import snapshots
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LiveParams, ParamGroup, ParamSnapshot
from openpilot.sunnypilot.nrdr import live_params as legacy_live_params


class RecordingParams:
  def __init__(self, values=None):
    self.values = dict(values or {})
    self.fail_reads = set()
    self.fail_writes_once = set()
    self.writes = []

  def get(self, key):
    if key in self.fail_reads:
      raise OSError(key)
    return self.values.get(key)

  def put(self, key, value, *, block=False):
    self.writes.append(("put", key, value, block))
    if key in self.fail_writes_once:
      self.fail_writes_once.remove(key)
      raise OSError(key)
    self.values[key] = value

  def put_bool(self, key, value, *, block=False):
    self.writes.append(("put_bool", key, value, block))
    self.values[key] = bool(value)


class TestParamSnapshots(unittest.TestCase):
  def test_applied_settings_log_is_deferred_and_does_not_write_params(self):
    params = RecordingParams({"a": b"1"})
    reader = LiveParams((ParamGroup(("a",)),), params=params, start_worker=False)
    snapshot = reader.snapshot
    with patch.object(reader, "_log_applied_settings") as log_settings:
      reader.record_applied_settings("honda_torque_pif", snapshot.generation, friction_highway=0.3, active=True)
      log_settings.assert_not_called()
      reader._drain_applied_reports()
      report = log_settings.call_args.args[0]
      self.assertEqual(report["friction_highway"], 0.3)
      self.assertTrue(report["active"])
      self.assertEqual(report["generation"], snapshot.generation)
      self.assertIs(reader.snapshot, snapshot)
      self.assertFalse(params.writes)

  def test_logging_failure_does_not_stop_parameter_refresh(self):
    params = RecordingParams({"a": b"1"})
    reader = LiveParams((ParamGroup(("a",)),), params=params, start_worker=False)
    with patch.object(reader, "_log_applied_settings", side_effect=OSError("log unavailable")):
      reader.record_applied_settings("honda_torque_pif", 1, friction_highway=0.3)
      reader._drain_applied_reports()
    params.values["a"] = b"2"
    self.assertTrue(reader.poll_once())
    self.assertEqual(reader.get("a"), b"2")

  def test_legacy_module_reexports_canonical_snapshot_objects(self):
    for name in legacy_live_params.__all__:
      self.assertIs(getattr(legacy_live_params, name), getattr(snapshots, name))

  def test_legacy_and_canonical_access_share_singleton_registry(self):
    class Instance:
      closed = False

      def close(self):
        self.closed = True

    snapshots.reset_live_params_for_tests()
    instance = Instance()
    snapshots._instances["controlsd"] = instance
    try:
      self.assertIs(snapshots.get_live_params(), instance)
      self.assertIs(legacy_live_params.get_live_params(), instance)
      legacy_live_params.reset_live_params_for_tests()
      self.assertTrue(instance.closed)
      self.assertFalse(snapshots._instances)
    finally:
      snapshots.reset_live_params_for_tests()

  def test_steer_ratio_mode_and_manual_values_share_one_atomic_group(self):
    self.assertEqual(CONTROL_GROUPS[4].keys, (
      "NrdrSteerRatioMode",
      "NrdrSteerRatioManualCenter",
      "NrdrSteerRatioManualFinal",
    ))
    retired = {
      "NrdrLearnSteerRatio", "NrdrLaneChangeEndpointSteerRatio",
      "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
      "NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic",
      "NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord",
      "NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g",
      "NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight",
    }
    keys = [key for group in CONTROL_GROUPS for key in group.keys]
    self.assertFalse(retired & set(keys))
    self.assertEqual(len(CONTROL_GROUPS), 12)
    self.assertEqual(len(keys), len(set(keys)))
    self.assertEqual(len(keys), 56)

  def test_lane_settings_have_one_live_group_and_subsecond_cycle(self):
    self.assertIn(snapshots.LANE_CENTERING_PARAM_GROUP, CONTROL_GROUPS)
    self.assertLessEqual(snapshots.REFRESH_PERIOD, 0.5)
    params = RecordingParams({key: b"0" for key in snapshots.LANE_CENTERING_PARAM_GROUP.keys})
    reader = LiveParams(CONTROL_GROUPS, params=params, start_worker=False)
    initial = reader.snapshot
    params.values["LaneCenteringStrength"] = b"0.3"
    for _ in CONTROL_GROUPS:
      reader.poll_once()
    self.assertEqual(reader.get("LaneCenteringStrength"), b"0.3")
    self.assertEqual(initial.get("LaneCenteringStrength"), b"0")

  def test_interpolated_torque_settings_share_one_atomic_group(self):
    expected = {
      "NrdrInterpolatedTorquePifBlend",
      "NrdrInterpolatedTorqueShare",
      "NrdrInterpolatedTorqueLatAccelFactor",
      "NrdrInterpolatedTorqueFriction",
      "NrdrInterpolatedTorqueFrictionStandard",
      "NrdrInterpolatedTorqueFrictionHighway",
    }
    matching = [group for group in CONTROL_GROUPS if expected.intersection(group.keys)]
    self.assertEqual(len(matching), 1)
    self.assertEqual(set(matching[0].keys), expected)

  def test_snapshot_keeps_legacy_get_and_bool_semantics(self):
    snapshot = ParamSnapshot(4, MappingProxyType({"Bytes": b"value", "False": b" FALSE ", "True": "yes"}))
    self.assertEqual(snapshot.get("Bytes", block=True, encoding="utf-8", unused=True), "value")
    self.assertFalse(snapshot.get_bool("False"))
    self.assertTrue(snapshot.get_bool("True"))
    self.assertFalse(snapshot.get_bool("Missing"))
    with self.assertRaises(TypeError):
      snapshot.values["Bytes"] = b"changed"

  def test_refresh_and_poll_generation_semantics_remain_distinct(self):
    params = RecordingParams({"a": b"1"})
    reader = LiveParams((ParamGroup(("a",)),), params=params, start_worker=False)
    initial = reader.snapshot

    self.assertFalse(reader.poll_once())
    self.assertIs(reader.snapshot, initial)
    self.assertTrue(reader.refresh_all())
    self.assertIsNot(reader.snapshot, initial)
    self.assertEqual(reader.generation, initial.generation + 1)

  def test_failed_poll_advances_slot_without_partial_publication(self):
    params = RecordingParams({"a": b"1", "b": b"1"})
    reader = LiveParams((ParamGroup(("a",)), ParamGroup(("b",))), params=params, start_worker=False)
    initial = reader.snapshot
    params.fail_reads.add("a")
    params.values["b"] = b"2"

    self.assertFalse(reader.poll_once())
    self.assertIs(reader.snapshot, initial)
    self.assertEqual(reader._slot, 1)
    self.assertTrue(reader.poll_once())
    self.assertEqual(reader.snapshot.values, {"a": b"1", "b": b"2"})

  def test_async_writes_remain_blocking_and_retry_after_failure(self):
    params = RecordingParams({"read": b"1"})
    params.fail_writes_once.add("map")
    reader = LiveParams((ParamGroup(("read",)),), params=params, start_worker=False)
    reader.put_async("map", b"payload")
    reader.put_async("reset", False, is_bool=True)

    reader._drain_writes()
    self.assertEqual(params.writes, [("put", "map", b"payload", True)])
    reader._drain_writes()
    self.assertEqual(params.writes, [
      ("put", "map", b"payload", True),
      ("put_bool", "reset", False, True),
      ("put", "map", b"payload", True),
    ])
    self.assertIs(params.values["reset"], False)
    self.assertEqual(params.values["map"], b"payload")
