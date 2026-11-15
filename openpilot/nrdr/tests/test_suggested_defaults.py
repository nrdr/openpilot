"""Fresh defaults stay separate from an owner's explicit one-shot preset."""
import json
import os
import time

import pytest

from openpilot.nrdr.features.services.model_manager import select_default_model
from openpilot.nrdr.params.profiles import (
  FIRMWARE_DEFAULTS_KEY, FIRMWARE_HANDCRAFTED_VALUES,
  consume_handcrafted_lateral_request, get_handcrafted_lateral_profile, seed_firmware_defaults,
)
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.tests.test_handcrafted_preset_v18 import FakeParams, cp_sp, vehicle_cp
from openpilot.nrdr.tests.test_model_manager import FakeParams as ModelParams, bundle
from openpilot.nrdr.tests.test_param_defaults import FakeParams as DefaultParams, _apply, _load_defaults


class FileParams(FakeParams):
  def __init__(self, root, values=None):
    super().__init__(values)
    self.root = root
    self.clock = time.time_ns()
    for key in self.values:
      self._save(key)

  def get_param_path(self, key=""):
    return str(self.root / key)

  def _save(self, key):
    path = self.root / key
    path.write_text(json.dumps(self.values[key]), encoding="utf-8")
    self.clock += 1_000_000
    os.utime(path, ns=(self.clock, self.clock))

  def _write(self, method, key, value, block):
    super()._write(method, key, value, block)
    self._save(key)


def test_new_selector_waits_for_live_admission_without_locking_settings(tmp_path):
  params = FileParams(tmp_path)
  seed_firmware_defaults(params)
  assert params.get("NrdrLateralController") == 0
  assert params.get("NrdrSteerRatioMode") == 0
  assert params.get(FIRMWARE_DEFAULTS_KEY)
  assert not params.get_bool("NrdrSuggestedSettings")
  assert tuning_write_allowed(params, "NrdrLateralController")

  cp = vehicle_cp()
  assert consume_handcrafted_lateral_request(cp, cp_sp(), params) == []  # not a startup
  written = consume_handcrafted_lateral_request(cp, cp_sp(), params, startup=True)
  assert written == [key for key, _ in FIRMWARE_HANDCRAFTED_VALUES]
  assert params.get("NrdrLateralController") == 1
  assert params.get("NrdrSteerRatioMode") == 3
  assert params.get("NrdrSteerRatioHybrid") is False
  assert params.get(FIRMWARE_DEFAULTS_KEY) == {}
  assert not params.get_bool("NrdrSuggestedSettings")
  assert not params.get_bool("NrdrHandcraftedLateralTune")
  assert tuning_write_allowed(params, "NrdrLateralController")


@pytest.mark.parametrize("change", ["unmodified", "unknown-rack", "wrong-car", "wrong-controller"])
def test_family_string_alone_never_enables_firmware_control(tmp_path, change):
  cp = vehicle_cp()
  sp = cp_sp(modified=change != "unmodified")
  if change == "unknown-rack":
    cp = vehicle_cp(firmware=b"39990-TEG-A999")
  elif change == "wrong-car":
    cp = vehicle_cp("HONDA_ACCORD")
  elif change == "wrong-controller":
    cp = vehicle_cp(controller="torque")
  params = FileParams(tmp_path)
  seed_firmware_defaults(params)
  assert consume_handcrafted_lateral_request(cp, sp, params, startup=True) == []
  assert params.get("NrdrLateralController") == 0
  assert params.get("NrdrSteerRatioMode") == 0
  assert params.get(FIRMWARE_DEFAULTS_KEY) == {}


@pytest.mark.parametrize("existing", [
  {"NrdrLateralController": 0}, {"NrdrSteerRatioMode": 2}, {"NrdrSteerRatioHybrid": False},
  {"NrdrSuggestedSettings": False}, {"NrdrLearnSteerRatio": False}, {"NrdrFirstRunSetupDone": False},
  {FIRMWARE_DEFAULTS_KEY: {}},
])
def test_existing_choices_and_legacy_devices_never_receive_an_auto_preset(tmp_path, existing):
  params = FileParams(tmp_path, existing)
  seed_firmware_defaults(params)
  assert params.values == existing
  assert not params.calls


@pytest.mark.parametrize("key,value", [
  ("NrdrLateralController", 0), ("NrdrSteerRatioMode", 0), ("NrdrSteerRatioHybrid", False),
  ("NrdrLateralController", 1), ("NrdrSteerRatioMode", 2),
])
def test_even_same_value_owner_rewrite_cancels_auto_selection(tmp_path, key, value):
  params = FileParams(tmp_path)
  seed_firmware_defaults(params)
  params.put(key, value, block=True)
  before = {k: params.get(k) for k, _ in FIRMWARE_HANDCRAFTED_VALUES}
  assert consume_handcrafted_lateral_request(vehicle_cp(), cp_sp(), params, startup=True) == []
  assert {k: params.get(k) for k in before} == before
  assert params.get(FIRMWARE_DEFAULTS_KEY) == {}


def test_unknown_identity_defers_but_completed_defaults_never_reapply(tmp_path):
  params = FileParams(tmp_path)
  seed_firmware_defaults(params)
  assert consume_handcrafted_lateral_request(None, None, params, startup=True) == []
  assert params.get(FIRMWARE_DEFAULTS_KEY)
  cp = vehicle_cp()
  consume_handcrafted_lateral_request(cp, cp_sp(), params, startup=True)
  params.put("NrdrLateralController", 0)
  params.put("NrdrSteerRatioMode", 2)
  params.calls.clear()
  seed_firmware_defaults(params)
  assert consume_handcrafted_lateral_request(cp, cp_sp(), params, startup=True) == []
  assert params.get("NrdrLateralController") == 0
  assert params.get("NrdrSteerRatioMode") == 2
  assert not params.calls


def test_default_write_failure_keeps_controller_off_and_does_not_rearm(tmp_path):
  params = FileParams(tmp_path)
  seed_firmware_defaults(params)
  params.fail_once_keys.add("NrdrSteerRatioMode")
  with pytest.raises(OSError, match="injected"):
    consume_handcrafted_lateral_request(vehicle_cp(), cp_sp(), params, startup=True)
  assert params.get("NrdrLateralController") == 0
  assert params.get(FIRMWARE_DEFAULTS_KEY) == {}


def test_preset_does_not_copy_manual_geometry_or_longitudinal_values():
  for cp in (vehicle_cp(), vehicle_cp("HONDA_CLARITY", firmware=b"39990-TRW-A020"), vehicle_cp("HONDA_ACCORD")):
    profile = get_handcrafted_lateral_profile(cp.carFingerprint, cp, cp_sp())
    keys = dict(profile.values)
    assert not any(key.startswith(("Long", "HondaLive", "NrdrCruise")) or "Manual" in key or "Calibration" in key for key in keys)
    assert not {"NrdrLearnSteerRatio", "NrdrLearnAngleOffset", "NrdrLearnStiffness"} & keys.keys()
    if cp.carFingerprint == "HONDA_ACCORD":
      assert "NrdrLateralController" not in keys
      assert "NrdrSteerRatioMode" not in keys


def test_fresh_baseline_is_unlocked_and_pop_request_is_compatible_only():
  defaults, _ = _load_defaults()
  params = DefaultParams()
  _apply(defaults, params)
  assert params.get("LaneGuidanceMode") == 2
  assert params.get("LagdToggle") is False
  assert params.get("NrdrOptimizedLaneChanges") is False
  assert params.get("NrdrSuggestedSettings") is None
  assert params.get("NrdrAutoSelectModel") is True
  assert params.get("ExperimentalMode") is False
  assert tuning_write_allowed(params, "LaneGuidanceMode")


@pytest.mark.parametrize("existing", [
  {"NrdrAutoSelectModel": False}, {"NrdrFirstRunSetupDone": False}, {"NrdrFirstRunSetupDone": True},
  {"ModelManager_ActiveBundle": {}}, {"ModelManager_ActiveBundleChestnut": b""}, {"ModelManager_DownloadRef": ""},
])
def test_model_default_preserves_opt_out_saved_and_pending_choices(existing):
  defaults, _ = _load_defaults()
  params = DefaultParams(existing)
  _apply(defaults, params)
  assert params.get("NrdrAutoSelectModel") is not True
  assert all(params.get(key) == value for key, value in existing.items())


def test_pop_default_uses_exact_identity_and_persists_completed_flag():
  params = ModelParams()
  impostor = bundle(999, "Pop Model v2", "not-pop")
  impostor.internalName = "other"
  select_default_model(params, [impostor])
  assert params.get("ModelManager_DownloadRef") is None
  select_default_model(params, [bundle(59, "Pop Model v2", "real-pop"), impostor])
  assert params.get("ModelManager_DownloadRef") == "real-pop"
  assert params.values["NrdrAutoSelectModel"] is False
