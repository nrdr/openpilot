import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.params import (
  consume_handcrafted_lateral_request,
  get_handcrafted_lateral_profile,
  request_handcrafted_lateral_profile,
)


REQUEST_KEY = "NrdrHandcraftedLateralTune"
CONTEXT_KEY = "NrdrHandcraftedLateralRequest"
BLEND_KEY = "NrdrInterpolatedTorquePifBlend"

COMMON_VALUES = (
  ("LaneCentering", True),
  ("LaneCenteringStrength", 1.0),
  ("LaneCenteringMinSpeed", 50),
  ("LaneCenteringE2EAuthority", 0.0),
  ("LaneCenteringPauseOnSignal", True),
  ("LaneCenterOffset", 0.0),
  ("LagdToggle", True),
  ("LagdToggleDelay", 0.4),
)

HONDA_FILTER_VALUES = (
  ("HondaCenterScale", 0.0),
  ("HondaCenterBoostThreshold", 5.0),
  ("HondaCenterBoostMinSpeed", 0),
  ("NrdrIncreaseOverrideTolerance", False),
  ("NrdrDriverOverrideThreshold", 1200),
  ("NrdrOverrideThresholdCenterBoost", 1200),
  ("HondaDriverAssistDuringOverride", False),
  ("HondaOverrideFadeDownSecs", 0.0),
  ("HondaOverrideFadeUpSecs", 1.0),
  ("HondaOverrideTorqueScale", 0),
  ("HondaTorqueLowPassFilter", True),
  ("HondaLpfTauLowSpeed", 0.1),
  ("HondaLpfTauStandard", 0.05),
  ("HondaLpfTauHighway", 0.02),
  ("HondaSteerDeltaLimiter", False),
  ("HondaSteerDeltaUp", 4.0),
  ("HondaSteerDeltaDown", 4.0),
)

HONDA_PID_VALUES = (
  ("NrdrStarPilotPid", False),
  ("LatPScaleLowSpeed", 100),
  ("LatIScaleLowSpeed", 100),
  ("LatFScaleLowSpeed", 100),
  ("LatPScaleStandard", 100),
  ("LatIScaleStandard", 100),
  ("LatFScaleStandard", 100),
  ("LatPScaleHighway", 100),
  ("LatIScaleHighway", 100),
  ("LatFScaleHighway", 100),
  ("NrdrLatRateDamping", 0),
  ("NrdrLatRateDampingFadeSpeed", 60),
  ("NrdrLatStiction", False),
  ("NrdrTuneLearner", False),
  ("NrdrTuneLearnerStrength", 0),
  ("NrdrTuneLearnerRate", 10),
)

HYBRID_VALUES = (
  (BLEND_KEY, True),
  ("NrdrInterpolatedTorqueShare", 10),
  ("NrdrInterpolatedTorqueLatAccelFactor", 10.0),
  ("NrdrInterpolatedTorqueFriction", 1.0),
  ("NrdrInterpolatedTorqueFrictionStandard", 1.0),
  ("NrdrInterpolatedTorqueFrictionHighway", 1.0),
)

TORQUE_VALUES = (
  ("TorqueParamsOverrideEnabled", False),
  ("TorqueParamsOverrideLatAccelFactor", 2.5),
  ("TorqueParamsOverrideFriction", 0.1),
  ("TorqueControlTune", 0.0),
  ("LateralJerkTorqueController", False),
  ("NrdrNnlcEnabled", False),
  ("NrdrNnlcActivationSpeed", 0),
  ("NrdrNnlcKpGain", 300),
  ("NrdrNnlcKiGain", 10),
  ("NrdrNnlcKfGain", 0),
)

PRESERVED_VALUES = {
  "NrdrSteerRatioMode": 2,
  "NrdrSteerRatioManualCenter": 18.75,
  "NrdrSteerRatioManualFinal": 13.25,
  "CalibrationParams": b"calibration-sentinel",
  "LiveParametersV2": b"live-parameters-sentinel",
  "NrdrTuneLearnerMap": b"learned-map-sentinel",
  "NrdrTuneLearnerReset": True,
  "NrdrLearnStiffness": False,
  "NrdrLearnAngleOffset": False,
}


class FakeParams:
  """Typed in-memory Params double with ordered calls and one-shot failures."""

  def __init__(self, values=None):
    self.values = copy.deepcopy(values or {})
    self.calls = []
    self.operations = []
    self.fail_once_keys = set()

  def get_bool(self, key):
    self.operations.append(("get_bool", key))
    return self.values.get(key, False) is True

  def get(self, key, return_default=False):
    self.operations.append(("get", key))
    return copy.deepcopy(self.values.get(key))

  def get_param_path(self, key=""):
    return ""

  def _write(self, method, key, value, block):
    stored = copy.deepcopy(value)
    self.calls.append((method, key, stored, block))
    self.operations.append((method, key))
    if key in self.fail_once_keys:
      self.fail_once_keys.remove(key)
      raise OSError(f"injected write failure for {key}")
    self.values[key] = stored

  def put_bool(self, key, value, block=False):
    self._write("put_bool", key, bool(value), block)

  def put(self, key, value, block=False):
    self._write("put", key, value, block)


def vehicle_cp(fingerprint="HONDA_CIVIC", *, brand="honda", controller="pid",
               steer_control_type="torque", firmware=b"39990-TEG-A010\x00", not_car=False):
  return SimpleNamespace(
    brand=brand,
    carFingerprint=fingerprint,
    carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
    lateralTuning=SimpleNamespace(which=lambda: controller),
    steerControlType=steer_control_type,
    notCar=not_car,
  )


def cp_sp(*, modified=True):
  return SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0)


def selected_params(CP, values=None):
  return FakeParams({
    "IsOffroad": True,
    "ParamsVersion": 5,
    "CarPlatformBundle": {"brand": CP.brand, "platform": CP.carFingerprint},
    **(values or {}),
  })


def canonical(value):
  return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def context_digest(value):
  return hashlib.sha256(canonical(value).encode()).hexdigest()


def assert_every_write_is_blocking_and_immediately_read_back(params):
  assert params.calls
  assert all(call[3] is True for call in params.calls)
  for index, operation in enumerate(params.operations):
    if operation[0] not in ("put", "put_bool"):
      continue
    assert params.operations[index + 1] == ("get", operation[1])


def request_profile(CP, CP_SP, params):
  assert request_handcrafted_lateral_profile(CP, CP_SP, params)
  context = copy.deepcopy(params.values[CONTEXT_KEY])
  params.calls.clear()
  params.operations.clear()
  return context


def test_v18_static_lookup_and_honda_hybrid_profiles_are_exact():
  static_civic = get_handcrafted_lateral_profile("HONDA_CIVIC")
  assert static_civic is not None
  assert static_civic.version == 18
  assert static_civic.values == COMMON_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES + HYBRID_VALUES

  static_clarity = get_handcrafted_lateral_profile("HONDA_CLARITY")
  assert static_clarity is not None
  assert static_clarity.version == 18
  assert static_clarity.values == COMMON_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES + HYBRID_VALUES + TORQUE_VALUES

  civic = vehicle_cp()
  runtime_civic = get_handcrafted_lateral_profile(civic.carFingerprint, civic, cp_sp())
  assert runtime_civic is not None
  assert runtime_civic.version == 18
  assert runtime_civic.values == COMMON_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES + HYBRID_VALUES

  clarity = vehicle_cp("HONDA_CLARITY", controller="torque", firmware=b"39990-TRW-A020\x00")
  runtime_clarity = get_handcrafted_lateral_profile(clarity.carFingerprint, clarity, cp_sp())
  assert runtime_clarity is not None
  assert runtime_clarity.version == 18
  assert runtime_clarity.values == COMMON_VALUES + TORQUE_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES + HYBRID_VALUES


def test_v18_capability_subsets_exclude_inapplicable_groups():
  honda_stock = vehicle_cp()
  honda_stock_profile = get_handcrafted_lateral_profile(honda_stock.carFingerprint, honda_stock, cp_sp(modified=False))
  assert honda_stock_profile is not None
  assert honda_stock_profile.values == COMMON_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES

  honda_angle = vehicle_cp(steer_control_type="angle")
  honda_angle_profile = get_handcrafted_lateral_profile(honda_angle.carFingerprint, honda_angle, cp_sp())
  assert honda_angle_profile is not None
  assert honda_angle_profile.values == COMMON_VALUES

  toyota_angle = vehicle_cp("LEXUS_ES_TSS2", brand="toyota", controller="lqr", steer_control_type="angle")
  toyota_angle_profile = get_handcrafted_lateral_profile(toyota_angle.carFingerprint, toyota_angle, None)
  assert toyota_angle_profile is not None
  assert toyota_angle_profile.values == COMMON_VALUES

  toyota_torque = vehicle_cp("TOYOTA_CAMRY_TSS2", brand="toyota", controller="torque")
  toyota_torque_profile = get_handcrafted_lateral_profile(toyota_torque.carFingerprint, toyota_torque, None)
  assert toyota_torque_profile is not None
  assert toyota_torque_profile.values == COMMON_VALUES + TORQUE_VALUES

  civic_torque = vehicle_cp(controller="torque")
  civic_torque_profile = get_handcrafted_lateral_profile(civic_torque.carFingerprint, civic_torque, cp_sp())
  assert civic_torque_profile is not None
  assert civic_torque_profile.values == COMMON_VALUES + TORQUE_VALUES + HONDA_FILTER_VALUES

  hybrid_keys = dict(HYBRID_VALUES).keys()
  assert hybrid_keys.isdisjoint(dict(honda_stock_profile.values))
  assert hybrid_keys.isdisjoint(dict(civic_torque_profile.values))
  assert (set(dict(HONDA_FILTER_VALUES)) | set(dict(HONDA_PID_VALUES)) | set(hybrid_keys)).isdisjoint(
    dict(toyota_angle_profile.values)
  )


def test_stock_clarity_torque_keeps_its_pid_leg_settings_without_enabling_modified_eps_blend():
  clarity = vehicle_cp("HONDA_CLARITY", controller="torque", firmware=b"stock-clarity-eps")
  profile = get_handcrafted_lateral_profile(clarity.carFingerprint, clarity, cp_sp(modified=False))
  assert profile is not None
  assert profile.values == COMMON_VALUES + TORQUE_VALUES + HONDA_FILTER_VALUES + HONDA_PID_VALUES
  assert dict(HYBRID_VALUES).keys().isdisjoint(dict(profile.values))


def test_runtime_lookup_rejects_unusable_or_mismatched_cp():
  civic = vehicle_cp()
  assert get_handcrafted_lateral_profile("HONDA_CLARITY", civic, cp_sp()) is None
  assert get_handcrafted_lateral_profile(civic.carFingerprint, vehicle_cp(not_car=True), cp_sp()) is None
  assert get_handcrafted_lateral_profile(
    civic.carFingerprint, vehicle_cp(brand="mock"), cp_sp(),
  ) is None
  assert get_handcrafted_lateral_profile(
    civic.carFingerprint, vehicle_cp(controller="unknown"), cp_sp(),
  ) is None


def test_request_requires_offroad_and_matching_selected_identity():
  civic = vehicle_cp()

  onroad = selected_params(civic, {"IsOffroad": False})
  assert not request_handcrafted_lateral_profile(civic, cp_sp(), onroad)
  assert onroad.calls == []

  mismatch = selected_params(civic)
  mismatch.values["CarPlatformBundle"] = {"brand": "toyota", "platform": "LEXUS_ES_TSS2"}
  assert not request_handcrafted_lateral_profile(civic, cp_sp(), mismatch)
  assert mismatch.calls == []

  malformed = selected_params(civic)
  malformed.values["CarPlatformBundle"] = {"brand": "honda"}
  assert not request_handcrafted_lateral_profile(civic, cp_sp(), malformed)
  assert malformed.calls == []


def test_request_writes_exact_json_context_before_legacy_boolean():
  civic = vehicle_cp()
  params = selected_params(civic)
  assert request_handcrafted_lateral_profile(civic, cp_sp(), params)

  profile = get_handcrafted_lateral_profile(civic.carFingerprint, civic, cp_sp())
  assert profile is not None
  firmware = sorted((str(fw.ecu), bytes(fw.fwVersion).hex()) for fw in civic.carFw)
  assert params.values[CONTEXT_KEY] == {
    "version": 18,
    "fingerprint": "HONDA_CIVIC",
    "brand": "honda",
    "controller": "pid",
    "steer_control_type": "torque",
    "flags_sp": HondaFlagsSP.EPS_MODIFIED.value,
    "firmware_sha256": context_digest(firmware),
    "payload_sha256": context_digest(dict(profile.values)),
  }
  assert json.loads(json.dumps(params.values[CONTEXT_KEY])) == params.values[CONTEXT_KEY]
  assert [(call[0], call[1]) for call in params.calls] == [
    ("put", CONTEXT_KEY), ("put_bool", REQUEST_KEY),
  ]
  assert params.values[REQUEST_KEY] is True
  assert_every_write_is_blocking_and_immediately_read_back(params)


@pytest.mark.parametrize(("field", "replacement"), (
  ("version", 17),
  ("fingerprint", "HONDA_CLARITY"),
  ("payload_sha256", "0" * 64),
))
def test_stale_or_changed_request_context_is_cleared_without_tune_writes(field, replacement):
  civic = vehicle_cp()
  params = selected_params(civic, {"HondaCenterScale": 0.37})
  request_profile(civic, cp_sp(), params)
  params.values[CONTEXT_KEY][field] = replacement

  assert consume_handcrafted_lateral_request(civic, cp_sp(), params) == []

  assert params.values[REQUEST_KEY] is False
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["ParamsVersion"] == 5
  assert params.calls == [("put_bool", REQUEST_KEY, False, True)]


def test_changed_capability_or_firmware_clears_bound_request_without_applying():
  civic = vehicle_cp()
  params = selected_params(civic, {"HondaCenterScale": 0.37})
  request_profile(civic, cp_sp(), params)

  assert consume_handcrafted_lateral_request(civic, cp_sp(modified=False), params) == []
  assert params.values[REQUEST_KEY] is False
  assert params.values["HondaCenterScale"] == 0.37
  assert params.calls == [("put_bool", REQUEST_KEY, False, True)]

  params = selected_params(civic, {"HondaCenterScale": 0.37})
  request_profile(civic, cp_sp(), params)
  changed_firmware = vehicle_cp(firmware=b"changed-firmware\x00")
  assert consume_handcrafted_lateral_request(changed_firmware, cp_sp(), params) == []
  assert params.values[REQUEST_KEY] is False
  assert params.values["HondaCenterScale"] == 0.37
  assert params.calls == [("put_bool", REQUEST_KEY, False, True)]


def test_old_unbound_boolean_is_terminally_cleared_without_tune_writes():
  civic = vehicle_cp()
  params = selected_params(civic, {
    REQUEST_KEY: True,
    "HondaCenterScale": 0.37,
    "LaneCenteringStrength": 0.22,
  })

  assert consume_handcrafted_lateral_request(civic, cp_sp(), params) == []

  assert params.values[REQUEST_KEY] is False
  assert CONTEXT_KEY not in params.values
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["LaneCenteringStrength"] == 0.22
  assert params.calls == [("put_bool", REQUEST_KEY, False, True)]


def test_fresh_apply_is_blocking_verified_and_enables_compound_features_last():
  civic = vehicle_cp()
  params = selected_params(civic, {**PRESERVED_VALUES, "LaneCentering": True, BLEND_KEY: True})
  request_profile(civic, cp_sp(), params)

  profile = get_handcrafted_lateral_profile(civic.carFingerprint, civic, cp_sp())
  assert profile is not None
  written = consume_handcrafted_lateral_request(civic, cp_sp(), params)

  assert dict(profile.values).items() <= params.values.items()
  assert written[:2] == [BLEND_KEY, "LaneCentering"]
  assert written[-2:] == [BLEND_KEY, "LaneCentering"]
  assert params.calls[0][:3] == ("put_bool", BLEND_KEY, False)
  assert params.calls[1][:3] == ("put_bool", "LaneCentering", False)
  payload_calls = [call for call in params.calls if call[1] in dict(profile.values)]
  assert payload_calls[-2][:3] == ("put_bool", BLEND_KEY, True)
  assert payload_calls[-1][:3] == ("put_bool", "LaneCentering", True)
  assert [call[1] for call in payload_calls] == written
  assert params.calls[-2] == ("put", CONTEXT_KEY, {}, True)
  assert params.calls[-1] == ("put_bool", REQUEST_KEY, False, True)
  assert params.values[CONTEXT_KEY] == {}
  assert params.values[REQUEST_KEY] is False
  assert params.values["ParamsVersion"] == 6
  assert_every_write_is_blocking_and_immediately_read_back(params)


def test_apply_preserves_steer_ratio_calibration_state_and_learning_policy():
  civic = vehicle_cp()
  params = selected_params(civic, PRESERVED_VALUES)
  request_profile(civic, cp_sp(), params)
  expected = copy.deepcopy(PRESERVED_VALUES)

  profile = get_handcrafted_lateral_profile(civic.carFingerprint, civic, cp_sp())
  assert profile is not None
  assert set(expected).isdisjoint(dict(profile.values))
  consume_handcrafted_lateral_request(civic, cp_sp(), params)

  assert {key: params.values[key] for key in expected} == expected


def test_interrupted_apply_restores_bound_request_with_blend_and_lane_centering_off_then_retries():
  civic = vehicle_cp()
  params = selected_params(civic, {"LaneCentering": True, BLEND_KEY: True})
  original_context = request_profile(civic, cp_sp(), params)
  params.fail_once_keys.add("HondaCenterScale")

  with pytest.raises(OSError, match="HondaCenterScale"):
    consume_handcrafted_lateral_request(civic, cp_sp(), params)

  assert params.values[BLEND_KEY] is False
  assert params.values["LaneCentering"] is False
  assert params.values[CONTEXT_KEY] == original_context
  assert params.values[REQUEST_KEY] is True
  assert params.values["ParamsVersion"] == 5
  assert [call[1] for call in params.calls[-4:]] == [
    BLEND_KEY, "LaneCentering", CONTEXT_KEY, REQUEST_KEY,
  ]

  params.calls.clear()
  params.operations.clear()
  consume_handcrafted_lateral_request(civic, cp_sp(), params)
  assert params.values[REQUEST_KEY] is False
  assert params.values[CONTEXT_KEY] == {}
  assert params.values[BLEND_KEY] is True
  assert params.values["LaneCentering"] is True


def test_completed_request_never_auto_reapplies_after_customization():
  civic = vehicle_cp()
  params = selected_params(civic)
  request_profile(civic, cp_sp(), params)
  consume_handcrafted_lateral_request(civic, cp_sp(), params)
  params.values["HondaCenterScale"] = 0.37
  params.values["LaneCenteringStrength"] = 0.22
  params.calls.clear()
  params.operations.clear()

  assert consume_handcrafted_lateral_request(civic, cp_sp(), params) == []
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["LaneCenteringStrength"] == 0.22
  assert params.values[CONTEXT_KEY] == {}
  assert params.values[REQUEST_KEY] is False
  assert params.calls == []


def test_fingerprint_only_profile_import_is_safe_before_native_dependencies_exist():
  repo_root = Path(__file__).parents[3]
  environment = os.environ.copy()
  environment["PYTHONPATH"] = os.pathsep.join((str(repo_root), str(repo_root / "opendbc_repo")))
  script = """
import sys
for name in ('capnp', 'numpy', 'pyray', 'zmq', 'openpilot.common.params'):
  sys.modules[name] = None
from openpilot.nrdr.params import get_handcrafted_lateral_profile
profile = get_handcrafted_lateral_profile('HONDA_CIVIC')
assert profile is not None and profile.version == 18
"""
  subprocess.run(
    [sys.executable, "-c", script], cwd=repo_root, env=environment,
    check=True, capture_output=True, text=True,
  )
