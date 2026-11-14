import datetime
import os
from pathlib import Path
import re
import threading
import time
import uuid

from openpilot.common.test import OpenpilotTestCase
from openpilot.common.params import (
  Params,
  ParamKeyFlag,
  UnknownKeyName,
  _copy_string,
  params_key_at,
  params_key_has_flag_at,
  params_keys_size,
)


_FLAG_VALUES = {
  "PERSISTENT": int(ParamKeyFlag.PERSISTENT),
  "CLEAR_ON_MANAGER_START": int(ParamKeyFlag.CLEAR_ON_MANAGER_START),
  "CLEAR_ON_ONROAD_TRANSITION": int(ParamKeyFlag.CLEAR_ON_ONROAD_TRANSITION),
  "CLEAR_ON_OFFROAD_TRANSITION": int(ParamKeyFlag.CLEAR_ON_OFFROAD_TRANSITION),
  "DONT_LOG": int(ParamKeyFlag.DONT_LOG),
  "DEVELOPMENT_ONLY": int(ParamKeyFlag.DEVELOPMENT_ONLY),
  "CLEAR_ON_IGNITION_ON": int(ParamKeyFlag.CLEAR_ON_IGNITION_ON),
  "BACKUP": int(ParamKeyFlag.BACKUP),
}
_REGISTRY_ENTRY_RE = re.compile(r'^\s*\{"([^"]+)", \{([^,]+),')


def _registry_key_flags():
  common_dir = Path(__file__).resolve().parents[1]
  registry_paths = (
    common_dir / "params_keys.h",
    common_dir.parent / "nrdr" / "params" / "generated" / "params_keys.inc",
  )
  key_flags = {}
  for path in registry_paths:
    for line in path.read_text(encoding="utf-8").splitlines():
      match = _REGISTRY_ENTRY_RE.match(line)
      if match is None:
        continue
      key, flag_expression = match.groups()
      assert key not in key_flags
      flags = 0
      for name in flag_expression.split("|"):
        flags |= _FLAG_VALUES[name.strip()]
      key_flags[key.encode()] = flags
  return key_flags


_REGISTRY_KEY_FLAGS = _registry_key_flags()


class TestParams(OpenpilotTestCase):
  def setup_method(self):
    self.params = Params()

  def test_params_put_and_get(self):
    self.params.put("DongleId", "cb38263377b873ee", block=True)
    assert self.params.get("DongleId") == "cb38263377b873ee"

  def test_params_non_ascii(self):
    st = b"\xe1\x90\xff"
    self.params.put("CarParams", st, block=True)
    assert self.params.get("CarParams") == st

  def test_params_get_cleared_manager_start(self):
    self.params.put("CarParams", b"test", block=True)
    self.params.put("DongleId", "cb38263377b873ee", block=True)
    assert self.params.get("CarParams") == b"test"

    undefined_param = self.params.get_param_path(uuid.uuid4().hex)
    with open(undefined_param, "w") as f:
      f.write("test")
    assert os.path.isfile(undefined_param)

    self.params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)
    assert self.params.get("CarParams") is None
    assert self.params.get("DongleId") is not None
    assert not os.path.isfile(undefined_param)

  def test_params_two_things(self):
    self.params.put("DongleId", "bob", block=True)
    self.params.put("AthenadPid", 123, block=True)
    assert self.params.get("DongleId") == "bob"
    assert self.params.get("AthenadPid") == 123

  def test_params_get_block(self):
    def _delayed_writer():
      time.sleep(0.1)
      self.params.put("CarParams", b"test", block=True)
    threading.Thread(target=_delayed_writer).start()
    assert self.params.get("CarParams") is None
    assert self.params.get("CarParams", block=True) == b"test"

  def test_params_unknown_key_fails(self):
    with self.assertRaises(UnknownKeyName):
      self.params.get("swag")

    with self.assertRaises(UnknownKeyName):
      self.params.get_bool("swag")

    with self.assertRaises(UnknownKeyName):
      self.params.put("swag", "abc", block=True)

    with self.assertRaises(UnknownKeyName):
      self.params.put_bool("swag", True, block=True)

    with self.assertRaises(UnknownKeyName):
      self.params.put(b"DongleId\0suffix", "abc", block=True)

    assert self.params.get_param_path(b"key\0suffix").endswith("/key\0suffix")

  def test_remove_not_there(self):
    assert self.params.get("CarParams") is None
    self.params.remove("CarParams")
    assert self.params.get("CarParams") is None

  def test_get_bool(self):
    self.params.remove("IsMetric")
    assert not self.params.get_bool("IsMetric")

    self.params.put_bool("IsMetric", True, block=True)
    assert self.params.get_bool("IsMetric")

    self.params.put_bool("IsMetric", False, block=True)
    assert not self.params.get_bool("IsMetric")

    self.params.put("IsMetric", True, block=True)
    assert self.params.get_bool("IsMetric")

    self.params.put("IsMetric", False, block=True)
    assert not self.params.get_bool("IsMetric")

  def test_put_non_blocking_with_get_block(self):
    q = Params()
    def _delayed_writer():
      time.sleep(0.1)
      Params().put("CarParams", b"test")
    threading.Thread(target=_delayed_writer).start()
    assert q.get("CarParams") is None
    assert q.get("CarParams", True) == b"test"

  def test_put_bool_non_blocking_with_get_block(self):
    q = Params()
    def _delayed_writer():
      time.sleep(0.1)
      Params().put_bool("CarParams", True)
    threading.Thread(target=_delayed_writer).start()
    assert q.get("CarParams") is None
    assert q.get("CarParams", True) == b"1"

  def test_params_all_keys(self):
    keys = self.params.all_keys()

    assert set(keys) == set(_REGISTRY_KEY_FLAGS)
    assert len(keys) == len(_REGISTRY_KEY_FLAGS)
    assert len(keys) == len(set(keys))
    assert b"CarParams" in keys

  def test_params_all_keys_by_flag(self):
    all_keys = self.params.all_keys()
    flags = (
      *_FLAG_VALUES.values(),
      int(ParamKeyFlag.PERSISTENT | ParamKeyFlag.CLEAR_ON_MANAGER_START),
      int(ParamKeyFlag.CLEAR_ON_ONROAD_TRANSITION | ParamKeyFlag.CLEAR_ON_IGNITION_ON),
      int(ParamKeyFlag.ALL),
    )

    for flag in flags:
      expected = all_keys if flag == int(ParamKeyFlag.ALL) else [
        key for key in all_keys if _REGISTRY_KEY_FLAGS[key] & flag
      ]
      actual = self.params.all_keys(flag)
      assert actual == expected
      assert len(actual) == len(set(actual))
      assert all(b"\0" not in key and key.decode("utf-8") for key in actual)

    combined_flag = ParamKeyFlag.BACKUP | ParamKeyFlag.CLEAR_ON_MANAGER_START
    any_match = self.params.all_keys(combined_flag)
    assert set(any_match) == set(self.params.all_keys(ParamKeyFlag.BACKUP)) | set(
      self.params.all_keys(ParamKeyFlag.CLEAR_ON_MANAGER_START)
    )
    assert b"IsMetric" in any_match
    assert b"DoReboot" in any_match
    assert b"DongleId" not in any_match
    assert self.params.all_keys(0) == []
    assert self.params.all_keys(ParamKeyFlag.ALL) == all_keys

    backup_keys = self.params.all_keys(ParamKeyFlag.BACKUP)
    assert b"Mads" in backup_keys
    assert b"TorqueParamsOverrideLatAccelFactor" in backup_keys
    assert b"AccessToken" not in backup_keys

    dont_log_keys = self.params.all_keys(ParamKeyFlag.DONT_LOG)
    assert b"AccessToken" in dont_log_keys
    assert b"RemoteAccessPinSalt" in dont_log_keys
    assert b"NrdrTuneLearnerMap" in dont_log_keys
    assert b"DongleId" not in dont_log_keys

  def test_params_all_keys_repeat_stability(self):
    expected = self.params.all_keys(ParamKeyFlag.BACKUP)

    self.params.get_default_value("LanguageSetting")
    self.params.get_param_path("CarParams")
    assert self.params.all_keys(ParamKeyFlag.BACKUP) == expected

    self.params.get_default_value("DisablePowerDown")
    assert self.params.all_keys(ParamKeyFlag.BACKUP) == expected

  def test_params_key_flag_scalar_abi(self):
    key_count = params_keys_size(self.params.p)
    assert key_count == len(_REGISTRY_KEY_FLAGS)
    assert not params_key_has_flag_at(self.params.p, key_count, int(ParamKeyFlag.ALL))

    for index in range(key_count):
      assert params_key_has_flag_at(self.params.p, index, int(ParamKeyFlag.ALL))
      assert not params_key_has_flag_at(self.params.p, index, 0)
      key = _copy_string(params_key_at(self.params.p, index))
      for flag in _FLAG_VALUES.values():
        assert params_key_has_flag_at(self.params.p, index, flag) == bool(_REGISTRY_KEY_FLAGS[key] & flag)

  def test_params_default_value(self):
    self.params.remove("LanguageSetting")
    self.params.remove("LongitudinalPersonality")
    self.params.remove("LiveParametersV2")

    assert self.params.get("LanguageSetting") is None
    assert self.params.get("LanguageSetting", return_default=False) is None
    assert isinstance(self.params.get("LanguageSetting", return_default=True), str)
    assert isinstance(self.params.get("LongitudinalPersonality", return_default=True), int)
    assert self.params.get("LiveParametersV2") is None
    assert self.params.get("LiveParametersV2", return_default=True) is None
    assert self.params.get_default_value("DisablePowerDown") is True
    assert self.params.get_default_value("HondaBoschARadar") is True
    assert self.params.get_default_value("NrdrHandcraftedLateralTune") is False

  def test_params_get_type(self):
    # json
    self.params.put("ApiCache_FirehoseStats", {"a": 0}, block=True)
    assert self.params.get("ApiCache_FirehoseStats") == {"a": 0}

    # int
    self.params.put("BootCount", 1441, block=True)
    assert self.params.get("BootCount") == 1441

    # bool
    self.params.put("AdbEnabled", True, block=True)
    assert self.params.get("AdbEnabled")
    assert isinstance(self.params.get("AdbEnabled"), bool)

    # time
    now = datetime.datetime.now(datetime.UTC)
    self.params.put("InstallDate", now, block=True)
    assert self.params.get("InstallDate") == now
