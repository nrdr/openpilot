from types import MappingProxyType
import unittest

from openpilot.nrdr.params import snapshots
from openpilot.nrdr.params.profiles import STEER_RATIO_ENDPOINT_PROFILES
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

  def test_control_groups_follow_canonical_endpoint_profile_order(self):
    expected = tuple((profile.center_param, profile.outer_param) for profile in STEER_RATIO_ENDPOINT_PROFILES)
    actual = tuple(group.keys for group in CONTROL_GROUPS[4:4 + len(expected)])
    self.assertEqual(actual, expected)
    self.assertEqual(len(CONTROL_GROUPS), 8 + len(expected))
    keys = [key for group in CONTROL_GROUPS for key in group.keys]
    self.assertEqual(len(keys), len(set(keys)))
    self.assertEqual(len(keys), 52)

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
