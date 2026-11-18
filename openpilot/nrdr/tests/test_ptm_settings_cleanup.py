"""Focused defaults, controller ownership and model-specific geometry contracts."""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.nrdr.params import profiles
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed, RETIRED_TUNING_KEYS
from openpilot.nrdr.features.lateral import steer_ratio_tuning as sr
from openpilot.nrdr.features.lateral import lane_change_tuning
from openpilot.nrdr.tests.test_handcrafted_preset_v18 import FakeParams, vehicle_cp, cp_sp
from openpilot.nrdr.tests.test_param_defaults import _load_defaults, _apply, FakeParams as DefaultParams
from openpilot.nrdr.tests.test_honda_rack_map import cp as ratio_cp
from openpilot.nrdr.tests.test_model_manager import bundle, FakeParams as ModelParams
from openpilot.nrdr.features.services.model_manager import select_default_model
from openpilot.nrdr.tests.test_mvl_settings import rpc as rpc, encoded
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("recipe", [
  "SHARED_RECOMMENDED_VALUES", "HONDA_LONGITUDINAL_RECOMMENDED_VALUES", "COMMON_HANDCRAFTED_VALUES",
  "HONDA_FILTER_HANDCRAFTED_VALUES", "HONDA_PID_HANDCRAFTED_VALUES", "FIRMWARE_HANDCRAFTED_VALUES",
  "TORQUE_HANDCRAFTED_VALUES",
])
def test_recommended_keys_exist_in_native_registry(recipe):
  from openpilot.nrdr.params.generate import HEADER_ENTRY_RE
  from openpilot.nrdr.params.specs import ADDED_PARAM_SPECS
  header = (ROOT / "openpilot/common/params_keys.h").read_text(encoding="utf-8")
  registered = {match.group("key") for match in HEADER_ENTRY_RE.finditer(header)} | {spec.key for spec in ADDED_PARAM_SPECS}
  assert {str(key) for key, _ in getattr(profiles, recipe)} <= registered


def vehicle(pedal=True, brand="honda", firmware=b"39990-TRW-A020"):
  CP = vehicle_cp("HONDA_CLARITY", controller="pid", brand=brand, firmware=firmware)
  CP.flags = HondaFlags.NIDEC
  CP_SP = cp_sp()
  CP_SP.enableGasInterceptor = pedal
  return CP, CP_SP


@pytest.mark.parametrize("pedal,brand,expected", [(True, "honda", 3), (False, "honda", 1), (True, "toyota", None)])
def test_detected_hardware_controller_default(pedal, brand, expected):
  CP, CP_SP = vehicle(pedal, brand)
  assert profiles.recommended_longitudinal_controller(CP, CP_SP) == expected
  CP.flags = 0
  assert profiles.recommended_longitudinal_controller(CP, CP_SP) == (None if brand != "honda" else 1)


@pytest.mark.parametrize("clean", [False, True])
def test_shared_migration_once_and_exclusions(monkeypatch, clean):
  from openpilot.nrdr.hooks import driver_monitoring
  monkeypatch.setattr(driver_monitoring, "monitoring_customization_available", lambda: not clean)
  preserved = {"HondaSpoofCameraMessages": True, "HondaEnforceStockLongitudinal": True,
               "RecordFront": False, "RecordAudio": False, "SshEnabled": False,
               "EnableCopyparty": False, "ModelManager_ActiveBundle": {"ref": "Cheddar"},
               "CalibrationParams": b"calibration", "NrdrDriverMonitoringReminderPercent": 100}
  params = DefaultParams({**preserved, "QuietMode": True, "LongitudinalPersonality": 0})
  module, _ = _load_defaults()
  _apply(module, params)
  assert params.get("QuietMode") is False and params.get("LongitudinalPersonality") == 3
  assert params.get("NrdrDriverMonitoringReminderPercent") == (100 if clean else 250)
  for key, value in preserved.items():
    if key != "NrdrDriverMonitoringReminderPercent":
      assert params.get(key) == value
  params.values.update(QuietMode=True, LongitudinalPersonality=1, NrdrDriverMonitoringReminderPercent=150)
  _apply(module, params)
  assert params.get("QuietMode") is True and params.get("LongitudinalPersonality") == 1
  assert params.get("NrdrDriverMonitoringReminderPercent") == 150


def test_vehicle_migration_once_preserves_model_privacy_and_learned_state():
  CP, CP_SP = vehicle()
  untouched = {"ModelManager_ActiveBundle": {"ref": "Cheddar"}, "CalibrationParams": b"cal",
               "HondaGasFactorParams": "1.25", "HondaSpoofCameraMessages": True,
               "RecordFront": False, "SshEnabled": False, "QuietMode": True}
  params = FakeParams(untouched)
  written = profiles.consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True)
  assert "NrdrLongitudinalController" in written
  assert params.get("NrdrLongitudinalController") == 3
  assert params.get("NrdrHondaWindBrake") is False
  assert params.get("NrdrSteerRatioMode") == 3
  assert params.get("NrdrSteerRatioModelBlend") is True
  assert params.get("NrdrDriverOverrideThreshold") == params.get("NrdrOverrideThresholdCenterBoost") == 1200
  assert params.get("HondaOverrideFadeDownSecs") == .1 and params.get("HondaOverrideFadeUpSecs") == 1.
  for key, value in untouched.items():
    assert params.get(key) == value
  params.values.update(NrdrLongitudinalController=0, NrdrDriverOverrideThreshold=1700)
  before = copy.deepcopy(params.values)
  assert profiles.consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True) == []
  assert params.values == before


def test_failed_vehicle_migration_stays_pending_and_disables_partial_control():
  CP, CP_SP = vehicle()
  params = FakeParams()
  params.fail_once_keys.add("NrdrSteerRatioMode")
  with pytest.raises(OSError):
    profiles.consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True)
  assert profiles.vehicle_defaults_pending(params, CP.carFingerprint)
  assert params.get("NrdrLateralController") == 0
  profiles.consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True)
  assert not profiles.vehicle_defaults_pending(params, CP.carFingerprint)
  assert params.get("NrdrLateralController") == 1


def test_unknown_eps_uses_comma_not_an_unverified_ptm_profile():
  CP, CP_SP = vehicle(firmware=b"39990-TRW-A030")
  profile = dict(profiles.get_handcrafted_lateral_profile(CP.carFingerprint, CP, CP_SP).values)
  assert profile["NrdrSteerRatioMode"] == 1 and "NrdrLateralController" not in profile


@pytest.mark.parametrize("controller", range(5))
def test_tuning_locks_do_not_rewrite_saved_values(controller):
  params = FakeParams({"NrdrLongitudinalController": controller, "IsOffroad": True,
                       "NrdrHondaWindBrake": True, "StaticFeedforwardLong": True})
  before = copy.deepcopy(params.values)
  for key in ("LongPidTuneScaleEcon", "NrdrHondaFullBrakeAuthority"):
    assert tuning_write_allowed(params, key) is (controller == 0)
  for key in ("NrdrHondaWindBrake", "StaticFeedforwardLong"):
    assert tuning_write_allowed(params, key) is (controller != 3)
  params.values["NrdrLateralController"] = 1
  assert not tuning_write_allowed(params, "HondaSteerDeltaLimiter")
  for key, value in before.items():
    assert params.values[key] == value


@pytest.mark.parametrize("fingerprint,firmware", sr._MODEL_BLEND_ENDPOINTS)
@pytest.mark.parametrize("ptm_baseline", [False, True])
def test_blend_endpoints_monotonicity_and_inverse(monkeypatch, fingerprint, firmware, ptm_baseline):
  monkeypatch.setattr(lane_change_tuning, "active_model_supports_steer_ratio_blend", lambda: True)
  CP = ratio_cp(fingerprint, firmware.encode())
  selection = sr.resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": 3, "NrdrSteerRatioModelBlend": True}, ptm_baseline=ptm_baseline)
  blend = selection.model_blend
  assert blend is not None
  final, lock = sr.model_blend_endpoint(CP)
  center = selection.cp_ratio * .01 / selection.firmware_profile.physical_to_linear(.01)
  for fraction in (.001, .25, .5, .75, 1.):
    angle = lock * fraction
    assert selection.cp_ratio * angle / selection.linearize_measured_angle(angle) == pytest.approx(center + fraction * (final - center))
  angles = np.linspace(-lock * 1.1, lock * 1.1, 101)
  linear = [selection.linearize_measured_angle(a) for a in angles]
  assert all(b > a for a, b in zip(linear, linear[1:]))
  for angle, value in zip(angles, linear, strict=True):
    assert selection.physicalize_desired_angle(value) == pytest.approx(angle, abs=1e-7)
    for speed, roll in ((0., 0.), (25., .03)):
      vm = NS(sR=0.)
      curvature = selection.measured_curvature(vm, angle, speed, roll)
      assert selection.desired_angle_no_offset(vm, 0., speed, roll, curvature) == pytest.approx(angle, abs=1e-6)


@pytest.mark.parametrize("eligible,mode,toggle", [(False, 3, True), (True, 1, True), (True, 3, False)])
def test_blend_isolation(monkeypatch, eligible, mode, toggle):
  monkeypatch.setattr(lane_change_tuning, "active_model_supports_steer_ratio_blend", lambda: eligible)
  CP = ratio_cp("HONDA_CLARITY", b"39990-TRW-A020")
  selection = sr.resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": mode, "NrdrSteerRatioModelBlend": toggle})
  baseline = sr.resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": mode})
  assert selection.model_blend is None
  for angle in np.linspace(-500., 500., 101):
    assert selection.linearize_measured_angle(angle) == baseline.linearize_measured_angle(angle)


def test_model_default_c3x_only_and_existing_selection_untouched():
  opm = bundle(100, "OP Model 10 V3", "opm")
  opm.internalName = "OPM10V3"
  pop = bundle(80, "Pop Model v2", "pop")
  for device, expected in (("tizi", "opm"), ("mici", "pop")):
    params = ModelParams()
    select_default_model(params, (opm, pop), device_type=device)
    assert params.get("ModelManager_DownloadRef") == expected
    params = ModelParams()
    params.values["ModelManager_ActiveBundle"] = {"ref": "Cheddar"}
    select_default_model(params, (opm, pop), device_type=device)
    assert params.get("ModelManager_DownloadRef") is None


def test_lane_change_shaping_uses_the_blended_mapping_in_both_directions(monkeypatch):
  monkeypatch.setattr(lane_change_tuning, "active_model_supports_steer_ratio_blend", lambda: True)
  CP = ratio_cp("HONDA_CLARITY", b"39990-TRW-A020")
  selection = sr.resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": 3, "NrdrSteerRatioModelBlend": True})
  for request in (-.03, -.003, .003, .03):
    vm = NS(sR=16.5)
    angle, speed, roll, reduction = 70., 20., .02, 3.
    ratio = selection.cp_ratio * angle / selection.linearize_measured_angle(angle)
    zero = selection.desired_angle_no_offset(vm, angle, speed, roll, 0.)
    desired = selection.desired_angle_no_offset(vm, angle, speed, roll, request)
    expected_angle = zero + (desired - zero) * (1. - reduction / ratio)
    result = lane_change_tuning.shape_lane_change_curvature(selection, vm, angle, speed, roll, request, reduction)
    assert result == pytest.approx(selection.measured_curvature(vm, expected_angle, speed, roll))
    assert abs(result) < abs(request)


def test_ui_retired_keys_and_help_only_descriptions():
  def items(node):
    if isinstance(node, dict):
      if "widget" in node and "key" in node:
        yield node
      for child in node.values():
        yield from items(child)
    elif isinstance(node, list):
      for child in node:
        yield from items(child)
  controls = {item["key"]: item for item in items(compile_schema(DEFAULT_SRC))}
  assert not controls.keys() & RETIRED_TUNING_KEYS
  assert [option["value"] for option in controls["NrdrLongitudinalController"]["options"]] == [0, 1, 2, 4, 3]
  assert [option["value"] for option in controls["NrdrSteerRatioMode"]["options"]] == [3, 1]
  for key in ("NrdrSuggestedSettings", "NrdrRemoteForceUpdate", "DisablePowerDown"):
    assert not controls[key]["description"] and controls[key]["details"]


def test_hardware_default_hook_runs_before_interface_construction():
  path = ROOT / "opendbc_repo/opendbc/car/car_helpers.py"
  tree = ast.parse(path.read_text())
  get_car = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_car")
  calls = {ast.unparse(n.func): n.lineno for n in ast.walk(get_car) if isinstance(n, ast.Call)}
  assert calls["CarInterface.get_params_sp"] < calls["configure_detected_car"] < calls["sunnypilot_interfaces"]


@pytest.mark.parametrize("pedal", [False, True])
def test_detected_controller_rebuild_precedes_actuator_startup(monkeypatch, tmp_path, pedal):
  from openpilot.sunnypilot.selfdrive.car import opendbc_config as boundary
  CP, CP_SP = vehicle(pedal)
  params = FakeParams({"NrdrLongitudinalController": 0, "HondaEnforceStockLongitudinal": True,
                       "HondaGasFactorParams": "1.25", "RecordFront": False})
  real_builder = boundary.build_sunnypilot_car_config
  monkeypatch.setattr(boundary, "build_sunnypilot_car_config", lambda p: real_builder(p, start_worker=False, metadata_path=tmp_path / "meta"))
  original = boundary.build_sunnypilot_car_config(params)
  updated = boundary.configure_detected_car_defaults(CP, CP_SP, original, params)
  try:
    assert updated.honda.personal_pedal is pedal
    assert updated.honda.mvl_longitudinal is (not pedal)
    assert updated.honda.enforce_stock_longitudinal is True  # no automatic switch away from stock ACC
    assert updated.honda.nidec_pcm_mode == 0
    assert params.get("HondaGasFactorParams") == "1.25" and params.get("RecordFront") is False
    params.values["NrdrVehicleDefaultsApplied"] = {CP.carFingerprint: 1}
    writes = list(params.calls)
    assert boundary.configure_detected_car_defaults(CP, CP_SP, updated, params) is updated
    assert params.calls == writes
  finally:
    updated.honda.provider.close()


@pytest.mark.parametrize("mode,learning,personal,pcm", [(0, False, False, 0), (1, True, False, 0), (2, False, False, 0),
                                                      (3, False, True, 0), (4, True, False, 2)])
def test_controller_config_has_one_explicit_experimental_choice(tmp_path, mode, learning, personal, pcm):
  from openpilot.nrdr.car.opendbc import build_nrdr_honda_config
  params = FakeParams({"NrdrLongitudinalController": mode, "NrdrHondaPcmMode": 2, "NrdrPcmSpeedDeadzone": .2})
  config = build_nrdr_honda_config(params, start_worker=False, metadata_path=tmp_path / "meta")
  try:
    assert (config.mvl_longitudinal, config.personal_pedal, config.nidec_pcm_mode) == (learning, personal, pcm)
    assert config.civic_pcm_speed_deadzone == 0.
    assert not params.calls
  finally:
    config.provider.close()


def test_remote_experimental_selection_uses_existing_gate_and_legacy_fields(rpc, monkeypatch):
  from openpilot.nrdr.car import live_gas_reset
  monkeypatch.setattr(live_gas_reset, "stored_cp", lambda p: None)
  save, params, caps = rpc
  caps.update(nrdr_mvl_pcm_deadzone_available=True, nrdr_personal_pedal_available=False)
  save({"NrdrLongitudinalController": encoded(4)})
  assert params.get("NrdrLongitudinalController") == 4 and params.get("NrdrHondaPcmMode") == 2
  assert params.get_bool("HondaLiveLearningGas")
  save({"NrdrLongitudinalController": encoded(0)})
  assert params.get("NrdrHondaPcmMode") == 0
  caps["nrdr_mvl_pcm_deadzone_available"] = False
  with pytest.raises(ValueError):
    save({"NrdrLongitudinalController": encoded(4)})


def test_remote_ptm_pedal_cannot_change_its_fixed_wind_or_pid_policy(rpc):
  save, params, caps = rpc
  caps["nrdr_personal_pedal_available"] = True
  params.values.update(NrdrLongitudinalController=3, NrdrHondaWindBrake=False, LongPidTuneScaleEcon=100)
  save({"NrdrHondaWindBrake": encoded(1), "LongPidTuneScaleEcon": encoded(200)})
  assert params.get("NrdrHondaWindBrake") is False
  assert params.get("LongPidTuneScaleEcon") == 100
