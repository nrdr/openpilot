#!/usr/bin/env python3
"""Focused real-Params verification; never opens the device's default Params.

Run from the candidate checkout with its built native library:
  python -m openpilot.nrdr.tools.check_lane_guidance_native

Every case uses a TemporaryDirectory AND a unique OPENPILOT_PREFIX. Production
migration/backup function bodies are loaded without constructing services. The
backup utility's Params factory is explicitly bound to that same isolated store.
No manager, messaging, network, CAN, reboot or model process is started.
"""

import ast
import base64
from enum import IntEnum
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import uuid


ROOT = Path(__file__).resolve().parents[2]
LANE_MODULE = "openpilot.nrdr.features.lateral.lane_guidance"
BAD_MODES = (b"", b"garbage", b"\xff", b" 2", b"+2", b"02", b"2\n", b"-1", b"3", b"true", b"1.0")


def load_definitions(relative, names, namespace):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
  if {node.name for node in nodes} != set(names):
    raise AssertionError(f"Missing production definitions: {relative}")
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)


class LaneGuidanceFailsafeChecks(unittest.TestCase):
  @staticmethod
  def make_params(root):
    from openpilot.common.params import Params
    return Params(root)  # Explicit root: never Params().

  def setUp(self):
    self.directory = TemporaryDirectory(prefix="nrdr-sunny-guard-")
    self.addCleanup(self.directory.cleanup)
    prefix = patch.dict(os.environ, {"OPENPILOT_PREFIX": "nrdr-sunny-guard-" + uuid.uuid4().hex})
    prefix.start()
    self.addCleanup(prefix.stop)
    self.params = self.make_params(self.directory.name)
    assert Path(self.params.get_param_path()).resolve().is_relative_to(Path(self.directory.name).resolve())

    spec = importlib.util.spec_from_file_location(LANE_MODULE, ROOT / "nrdr/features/lateral/lane_guidance.py")
    self.lane = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(self.lane)
    modules = patch.dict(sys.modules, {LANE_MODULE: self.lane})
    modules.start()
    self.addCleanup(modules.stop)
    self.ns = {"cloudlog": Mock(), "IntEnum": IntEnum, "base64": base64, "gzip": gzip, "json": json,
               "Params": lambda: self.params, "ParamKeyFlag": SimpleNamespace(BACKUP=0x100)}
    load_definitions("common/params.py", {"ParamKeyType"}, self.ns)
    load_definitions("sunnypilot/sunnylink/utils.py", {"_convert_param_to_type", "save_param_from_base64_encoded_string"}, self.ns)
    load_definitions("sunnypilot/system/params_migration.py", {"_migrate_lane_guidance_mode"}, self.ns)
    load_definitions("sunnypilot/sunnylink/backups/manager.py", {"_apply_config"}, self.ns)
    self.migrate = lambda: self.ns["_migrate_lane_guidance_mode"](self.params)
    self.restore = lambda data: self.ns["_apply_config"](SimpleNamespace(params=self.params), data)

  def raw(self, key, value):
    path = Path(self.params.get_param_path(key))
    assert path.resolve().is_relative_to(Path(self.directory.name).resolve())
    if value is None:
      path.unlink(missing_ok=True)
    else:
      path.write_bytes(value)

  def pair(self, mode, legacy):
    self.raw("LaneGuidanceMode", mode)
    self.raw("LaneCentering", legacy)

  def assert_mode(self, mode):
    self.assertEqual(self.params.get_raw("LaneGuidanceMode"), str(mode).encode())
    self.assertEqual(self.params.get_raw("LaneCentering"), b"1" if mode == 1 else b"0")
    self.assertEqual(int(self.lane.lane_guidance_mode_from_params(self.params)), mode)

  @staticmethod
  def encoded(raw):
    return base64.b64encode(raw).decode("ascii")

  def test_raw_missing_empty_and_registry_validation(self):
    self.assertIsNone(self.params.get_raw("LaneGuidanceMode"))
    self.raw("LaneGuidanceMode", b"")
    self.assertEqual(self.params.get_raw("LaneGuidanceMode"), b"")
    with patch.object(self.params, "check_key", side_effect=ValueError("unknown key")), \
         patch.object(self.params, "get_param_path") as path:
      with self.assertRaises(ValueError):
        self.params.get_raw("../not-a-registered-key")
      path.assert_not_called()

  def test_fresh_sunny_and_repeat_startup(self):
    self.assertEqual(self.params.get_default_value("LaneGuidanceMode"), 2)
    self.migrate()
    self.assert_mode(2)
    with patch.object(self.params, "put") as put, patch.object(self.params, "put_bool") as put_bool:
      self.migrate()
      put.assert_not_called()
      put_bool.assert_not_called()

  def test_saved_choices_win_and_legacy_only_is_preserved(self):
    for mode in (0, 1, 2):
      for legacy in (None, b"0", b"1"):
        with self.subTest(mode=mode, legacy=legacy):
          self.pair(str(mode).encode(), legacy)
          self.migrate()
          self.assert_mode(mode)
    for legacy, expected in ((b"0", 0), (b"1", 1), (b"", 0), (b"garbage", 0)):
      with self.subTest(legacy=legacy):
        self.pair(None, legacy)
        self.migrate()
        self.assert_mode(expected)

  def test_malformed_canonical_never_uses_defaults_or_legacy(self):
    for raw in BAD_MODES:
      for legacy in (None, b"0", b"1"):
        with self.subTest(raw=raw, legacy=legacy):
          self.pair(raw, legacy)
          self.assertEqual(int(self.lane.lane_guidance_mode_from_params(self.params)), 0)
          self.migrate()
          self.assert_mode(0)

  def test_native_default_conversion_cannot_enable_runtime(self):
    self.pair(b"garbage", b"0")
    self.assertEqual(self.params.get("LaneGuidanceMode", return_default=True), 2)
    self.assertIsNone(self.params.get("LaneGuidanceMode"))
    self.assertEqual(int(self.lane.lane_guidance_mode_from_params(self.params)), 0)
    self.pair(None, b"1")
    self.assertEqual(int(self.lane.lane_guidance_mode_from_params(self.params)), 0)

  def test_io_errors_fail_closed_and_abort_startup_before_default_seeding(self):
    with patch.object(self.params, "get_raw", side_effect=OSError("unreadable")), \
         patch.object(self.params, "put") as put, patch.object(self.params, "put_bool") as put_bool:
      self.assertEqual(int(self.lane.lane_guidance_mode_from_params(self.params)), 0)
      with self.assertRaises(OSError):
        self.migrate()
      put.assert_not_called()
      put_bool.assert_not_called()

  def test_startup_checks_both_writes_and_readback(self):
    for method in ("put", "put_bool"):
      for failure in (None, OSError("write failed")):
        with self.subTest(method=method, failure=failure):
          self.pair(None, None)
          with patch.object(self.params, method, side_effect=failure):
            with self.assertRaises(OSError):
              self.migrate()

  def test_legacy_only_backup_overrides_destination_and_preserves_other_state(self):
    self.params.put("HondaWindFactorParams", 1.23, block=True)
    for destination in (0, 1, 2):
      for legacy, expected in ((b"0", 0), (b"False", 0), (b"1", 1), (b"True", 1)):
        with self.subTest(destination=destination, legacy=legacy):
          self.pair(str(destination).encode(), b"1" if destination == 1 else b"0")
          self.restore({"lanecentering": self.encoded(legacy)})
          self.assert_mode(expected)
          self.migrate()
          self.assert_mode(expected)
          self.assertEqual(self.params.get("HondaWindFactorParams"), 1.23)

  def test_canonical_backup_wins_in_either_order_and_bad_canonical_is_off(self):
    for raw in (b"0", b"1", b"2", *BAD_MODES):
      for reverse in (False, True):
        with self.subTest(raw=raw, reverse=reverse):
          self.pair(b"2", b"0")
          items = [("LANEGUIDANCEMODE", self.encoded(raw)), ("LaneCentering", self.encoded(b"True"))]
          self.restore(dict(reversed(items) if reverse else items))
          self.assert_mode(int(raw) if raw in (b"0", b"1", b"2") else 0)

  def test_no_lane_choice_does_not_reset_selection_and_generic_writer_is_isolated(self):
    self.pair(b"2", b"0")
    self.restore({"IsMetric": self.encoded(b"True")})
    self.assert_mode(2)
    self.assertIs(self.params.get("IsMetric"), True)

  def test_invalid_encoding_and_duplicate_aliases_reject_before_any_write(self):
    for config in ({"LaneCentering": "%%%"}, {"LaneCentering": self.encoded(b"garbage")},
                   {"LaneGuidanceMode": "%%%"}, {"LaneCentering": self.encoded(b"1"), "lanecentering": self.encoded(b"0")}):
      with self.subTest(config=config):
        self.pair(b"2", b"0")
        with patch.object(self.params, "put") as put, patch.object(self.params, "put_bool") as put_bool:
          with self.assertRaises(ValueError):
            self.restore({"IsMetric": self.encoded(b"True"), **config})
          put.assert_not_called()
          put_bool.assert_not_called()

  def test_partial_restore_or_failed_readback_is_not_success(self):
    for method in ("put", "put_bool"):
      for failure in (None, OSError("write failed")):
        with self.subTest(method=method, failure=failure):
          self.pair(b"2", b"0")
          with patch.object(self.params, method, side_effect=failure):
            with self.assertRaises(OSError):
              self.restore({"LaneCentering": self.encoded(b"True"), "IsMetric": self.encoded(b"True")})
          self.assertIsNone(self.params.get("IsMetric"))

  def test_both_model_runners_use_nondefaulting_raw_helper(self):
    for relative in ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"):
      with self.subTest(runner=relative):
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        reads = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "lane_guidance_mode_from_params"]
        self.assertEqual(len(reads), 1)
        self.assertEqual(ast.unparse(reads[0]), "lane_guidance_mode_from_params(params)")
        self.assertNotIn('params.get("LaneGuidanceMode", return_default=True)', (ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
  unittest.main(verbosity=2)
