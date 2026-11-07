"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import base64
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from openpilot.common.params import Params, ParamKeyFlag
from openpilot.sunnypilot.sunnylink import utils as sunnylink_utils
from openpilot.sunnypilot.sunnylink.backups.manager import BackupManagerSP


class TestBackupManagerSP(unittest.TestCase):
  def setUp(self) -> None:
    self.params_directory = TemporaryDirectory()
    self.params = Params(self.params_directory.name)
    self.manager = BackupManagerSP.__new__(BackupManagerSP)
    self.manager.params = self.params

  def tearDown(self) -> None:
    self.manager = None
    self.params = None
    self.params_directory.cleanup()

  def test_backup_key_enumeration_is_valid_unique_and_registered(self) -> None:
    registered_keys = set(self.params.all_keys())
    backup_keys = self.params.all_keys(ParamKeyFlag.BACKUP)

    self.assertGreater(len(backup_keys), 20)
    self.assertEqual(len(backup_keys), len(set(backup_keys)))
    self.assertIn(b"IsMetric", backup_keys)
    self.assertNotIn(b"DongleId", backup_keys)

    for key in backup_keys:
      with self.subTest(key=repr(key)):
        self.assertIsInstance(key, bytes)
        decoded_key = key.decode("utf-8")
        self.assertTrue(decoded_key)
        self.assertNotIn("\0", decoded_key)
        self.assertIn(key, registered_keys)
        self.assertEqual(self.params.check_key(key), key)

  def test_collect_config_only_includes_backup_keys(self) -> None:
    self.params.put("IsMetric", True, block=True)
    self.params.put("DongleId", "must-not-be-backed-up", block=True)

    with patch.object(sunnylink_utils, "Params", return_value=self.params):
      config_data = self.manager._collect_config_data()

    self.assertEqual(set(config_data), {"IsMetric"})
    self.assertEqual(base64.b64decode(config_data["IsMetric"]), b"True")
    self.assertNotIn("DongleId", config_data)

  def test_apply_config_only_restores_backup_keys(self) -> None:
    self.params.put("IsMetric", False, block=True)
    self.params.put("DongleId", "original-device-id", block=True)
    config_data = {
      "ismetric": base64.b64encode(b"True").decode("utf-8"),
      "DongleId": base64.b64encode(b"replacement-device-id").decode("utf-8"),
    }

    with patch.object(sunnylink_utils, "Params", return_value=self.params):
      self.manager._apply_config(config_data)

    self.assertIs(self.params.get("IsMetric"), True)
    self.assertEqual(self.params.get("DongleId"), "original-device-id")


if __name__ == "__main__":
  unittest.main()
