"""Clarity angle mode on the openpilot side: the 39990+TRW+A020 ID resolves like 39990-TRW,A020, and an angle-mode
Clarity is never handed to the PTM torque controllers (it steers through LatControlAngle)."""
from types import SimpleNamespace
import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.controller_selection import angle_controller_available, firmware_controller_profile
from openpilot.nrdr.features.lateral.yaw_control_timing import prediction_delay_schedule
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile, normalize_honda_eps_firmware


def _cp(fw):
  return SimpleNamespace(brand="honda", carFingerprint="HONDA_CLARITY", steerRatio=16.5,
                         carFw=[SimpleNamespace(ecu="eps", fwVersion=fw)],
                         lateralTuning=SimpleNamespace(which=lambda: "pid"))


def test_ptm2_id_normalizes_and_gets_the_same_vgr_profile():
  assert normalize_honda_eps_firmware(b"39990+TRW+A020\x00\x00") == normalize_honda_eps_firmware(b"39990-TRW,A020\x00\x00")
  assert get_honda_vgr_profile(_cp(b"39990+TRW+A020\x00\x00")) == get_honda_vgr_profile(_cp(b"39990-TRW,A020\x00\x00")) is not None


def test_angle_mode_is_excluded_from_the_ptm_controller():
  cp = _cp(b"39990-TRW,A020\x00\x00")
  torque = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED))
  angle = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.CLARITY_ANGLE_MODE))
  assert firmware_controller_profile(cp, torque) is not None
  assert firmware_controller_profile(cp, angle) is None


@pytest.mark.parametrize("saved", [None, 0, 1, 2, 3])
@pytest.mark.parametrize("firmware,expected", [
  ([b"39990+TRW+A020\0\0"], True), ([b"39990-TRW-A020"], False), ([b"39990-TRW,A020"], False),
  ([b"39990+TRW+A021"], False), ([], False), ([b"39990+TRW+A020", b"39990-TRW-A020"], False),
])
def test_detected_config_selects_exact_rack_on_first_start(tmp_path, monkeypatch, saved, firmware, expected):
  from opendbc.car.structs import car
  from opendbc.sunnypilot.car.honda.clarity_eps import apply_angle_mode, EpsCalStatus
  from openpilot.cereal import custom
  from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
  from openpilot.sunnypilot.selfdrive.car import opendbc_config as boundary

  params = FakeParams({} if saved is None else {"NrdrLateralController": saved})
  builder = boundary.build_sunnypilot_car_config
  monkeypatch.setattr(boundary, "build_sunnypilot_car_config", lambda p: builder(p, start_worker=False, metadata_path=tmp_path / "meta"))
  # Keep the capability flags identical: punctuation alone or a stale flag must not cause a match.
  sp = custom.CarParamsSP.new_message(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.EPS_ANGLE_PTM))
  cp = car.CarParams.new_message(brand="honda", carFingerprint="HONDA_CLARITY", carFw=[{"ecu": "eps", "fwVersion": fw} for fw in firmware])
  config = boundary.configure_detected_car_defaults(cp, sp, boundary.build_sunnypilot_car_config(params), params)
  try:
    assert config.honda.clarity_angle_mode is expected
    apply_angle_mode(cp, sp, config.honda.clarity_angle_mode)
    assert (cp.steerControlType == "angle") is expected
    assert not EpsCalStatus(cp, sp).angle_ready  # Selection alone never authorizes output.
    assert params.get("NrdrLateralController") == saved
  finally:
    config.honda.provider.close()


def test_angle_mode_uses_lagd_not_the_ptm_delay_schedule():
  # modeld and controlsd take the PTM prediction-delay schedule only from the PTM controller profile; angle mode gets
  # none, so both use lagd's learned delay (get_lat_delay with delay_schedule=None)
  cp = _cp(b"39990-TRW,A020\x00\x00")
  torque = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED))
  angle = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.CLARITY_ANGLE_MODE))
  assert prediction_delay_schedule(firmware_controller_profile(cp, torque)) is not None
  assert prediction_delay_schedule(firmware_controller_profile(cp, angle)) is None


def test_angle_picker_checks_firmware_independently_of_the_last_drive():
  cp = _cp(b"39990+TRW+A020\x00\x00")
  flags = HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.EPS_ANGLE_PTM
  for mode in (0, HondaFlagsSP.CLARITY_ANGLE_MODE):
    sp = SimpleNamespace(flags=int(flags | mode))
    assert angle_controller_available(cp, sp)
    assert firmware_controller_profile(cp, sp, for_picker=True) is not None
    assert (firmware_controller_profile(cp, sp) is None) == bool(mode)
  assert not angle_controller_available(cp, None)
  assert not angle_controller_available(cp, SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED)))
  assert not angle_controller_available(_cp(b"39990-TRW,A020"), sp)
  cp.carFingerprint = "HONDA_CIVIC"
  assert not angle_controller_available(cp, sp)


def test_only_angle_knobs_unlock_and_saved_torque_tune_survives_switches():
  from openpilot.nrdr.params.tuning_policy import ANGLE_LOCKED_KEYS, ANGLE_TUNING_KEYS, tuning_write_allowed
  p = {"IsOffroad": True, "LatPScaleStandard": 113, "HondaEpsAngleRateLimit": 60}
  for controller in (0, 1, 2, 3, 0):
    p["NrdrLateralController"] = controller
    assert all(tuning_write_allowed(p, k) == (controller == 3) for k in ANGLE_TUNING_KEYS)
    if controller == 3:
      assert not any(tuning_write_allowed(p, k) for k in ANGLE_LOCKED_KEYS)
    assert tuning_write_allowed(p, "NrdrLateralController")
  assert tuning_write_allowed(p, "LatPScaleStandard")
  assert (p["LatPScaleStandard"], p["HondaEpsAngleRateLimit"]) == (113, 60)


@pytest.mark.parametrize("detected,expected", [(True, b"3"), (False, b"2")])
def test_sunnylink_reads_effective_controller_without_writing_preferences(detected, expected):
  import base64
  import json
  from openpilot.nrdr.tests.test_sunnylink_model_catalog import load_function, MemoryParams, ParamType
  key = "NrdrLateralController"
  params = MemoryParams({key: 2})
  read = load_function("openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py", "getParams", {
    "Params": lambda: params, "ParamKeyType": ParamType, "json": json, "base64": base64,
    "_vehicle_tuning_capabilities": lambda: {"nrdr_angle_controller_available": detected},
    "get_param_as_byte": lambda k: str(params.get(k)).encode(),
  })
  assert base64.b64decode(read([key])[key]) == expected
  assert params.get(key) == 2


def test_migration_never_copies_a_firmware_choice_into_another_cars_preference():
  from opendbc.car.structs import car
  from openpilot.cereal import custom
  from openpilot.nrdr.tests.test_param_defaults import FakeParams, _load_defaults
  defaults, _ = _load_defaults()
  cp = car.CarParams.new_message(brand="honda", carFingerprint="HONDA_CLARITY",
                                 carFw=[{"ecu": "eps", "fwVersion": b"39990+TRW+A020"}])
  sp = custom.CarParamsSP.new_message(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.EPS_ANGLE_PTM))
  cp_raw, sp_raw = cp.to_bytes(), sp.to_bytes()
  for old, raw, flags, expected in ((True, cp_raw, sp_raw, 2), (False, cp_raw, sp_raw, 2),
                                    (True, None, None, 2), (True, b"bad", sp_raw, 2),
                                    (True, cp_raw, custom.CarParamsSP.new_message().to_bytes(), 2)):
    p = FakeParams({"HondaClarityAngleMode": old, "CarParamsPersistent": raw, "CarParamsSPPersistent": flags,
                    "NrdrLateralController": 2, "HondaClarityAngleCap3": True, "HondaEpsAngleRateLimit": 80})
    defaults._migrate_angle_controller(p)
    assert p.get("NrdrLateralController") == expected
    assert not p.get("HondaClarityAngleMode")
    assert p.get("HondaClarityAngleCap3") and p.get("HondaEpsAngleRateLimit") == 80
    p.put("NrdrLateralController", 1)
    defaults._migrate_angle_controller(p)
    assert p.get("NrdrLateralController") == 1
