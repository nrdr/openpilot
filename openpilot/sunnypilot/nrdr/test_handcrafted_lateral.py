from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  BLEND_MASTER_PARAM,
  CLARITY_HANDCRAFTED_VALUES_V17,
  CLARITY_ROAD_TESTED_2026_08_28,
  HANDCRAFTED_LATERAL_PROFILES,
  HANDCRAFTED_REQUEST_PARAM,
  HANDCRAFTED_STATUS_PARAM,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HandcraftedLateralUnsafeStateError,
  STEER_RATIO_MODE_PARAM,
  confirmed_vehicle_identity,
  consume_handcrafted_lateral_request,
  get_handcrafted_lateral_profile,
  get_selected_car_identity,
  handcrafted_lateral_profile_status,
  handcrafted_lateral_profile_supported,
)


EXPECTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

# Independent source oracle: CURRENT_CLARITY_47_ORACLE.json SHA-256
# d9bea117c3ef7a30c8f67c809b386f35e89fd2ba1158dbe7cb30b1b6ded5c97a.
# Canonical oracle manifest SHA-256:
# bd8b0ebfc10342ff6405c50659eeb24645439d4f06ea4a145ca25dfa998a8e3d.
EXPECTED_CLARITY_V17_VALUES = {
  "NrdrStarPilotPid": False,
  "NrdrLearnStiffness": True,
  "NrdrLearnAngleOffset": True,
  "LatPScaleLowSpeed": 100,
  "LatIScaleLowSpeed": 100,
  "LatFScaleLowSpeed": 100,
  "LatPScaleStandard": 100,
  "LatIScaleStandard": 100,
  "LatFScaleStandard": 100,
  "LatPScaleHighway": 100,
  "LatIScaleHighway": 100,
  "LatFScaleHighway": 100,
  "NrdrLatRateDamping": 0,
  "NrdrLatRateDampingFadeSpeed": 60,
  "HondaCenterScale": 0.0,
  "HondaCenterBoostThreshold": 5.0,
  "HondaCenterBoostMinSpeed": 0,
  "NrdrLatStiction": True,
  "NrdrNnlcEnabled": False,
  "NrdrTuneLearner": False,
  "NrdrTuneLearnerStrength": 0,
  "NrdrTuneLearnerRate": 10,
  "NrdrIncreaseOverrideTolerance": False,
  "NrdrDriverOverrideThreshold": 1200,
  "NrdrOverrideThresholdCenterBoost": 1200,
  "HondaDriverAssistDuringOverride": False,
  "HondaOverrideFadeDownSecs": 0.0,
  "HondaOverrideFadeUpSecs": 1.0,
  "HondaOverrideTorqueScale": 0,
  "HondaTorqueLowPassFilter": True,
  "HondaLpfTauLowSpeed": 0.1,
  "HondaLpfTauStandard": 0.09,
  "HondaLpfTauHighway": 0.07,
  "HondaSteerDeltaLimiter": False,
  "HondaSteerDeltaUp": 4.0,
  "HondaSteerDeltaDown": 4.0,
  "LagdToggle": False,
  "LagdToggleDelay": 0.05,
  "NrdrSteerRatioMode": 3,
  "NrdrSteerRatioManualCenter": 20.0,
  "NrdrSteerRatioManualFinal": 13.75,
  "NrdrInterpolatedTorquePifBlend": True,
  "NrdrInterpolatedTorqueShare": 75,
  "NrdrInterpolatedTorqueLatAccelFactor": 10.0,
  "NrdrInterpolatedTorqueFriction": 0.12,
  "NrdrInterpolatedTorqueFrictionStandard": 0.10,
  "NrdrInterpolatedTorqueFrictionHighway": 0.09,
}


class FakeParams:
  def __init__(self, values=None, *, fail_key=None, fail_occurrence=1):
    self.values = dict(values or {})
    self.writes = []
    self.fail_key = fail_key
    self.fail_occurrence = fail_occurrence
    self._key_attempts = {}
    self.failed = False

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    del return_default
    return self.values.get(key)

  def _write(self, kind, key, value, block):
    assert block
    self._key_attempts[key] = self._key_attempts.get(key, 0) + 1
    if key == self.fail_key and self._key_attempts[key] == self.fail_occurrence and not self.failed:
      self.failed = True
      raise RuntimeError(f"interrupted {key}")
    typed = bool(value) if kind == "bool" else value
    self.values[key] = typed
    self.writes.append((key, typed, kind, block))

  def put_bool(self, key, value, block=False):
    self._write("bool", key, value, block)

  def put(self, key, value, block=False):
    self._write("put", key, value, block)


class BoolAsIntReadbackParams(FakeParams):
  def get(self, key, return_default=False):
    value = super().get(key, return_default=return_default)
    return int(value) if key == "NrdrStarPilotPid" and isinstance(value, bool) else value


class SilentWriteOnceParams(FakeParams):
  def __init__(self, values=None, *, silent_key, silent_occurrence=1):
    super().__init__(values)
    self.silent_key = silent_key
    self.silent_occurrence = silent_occurrence
    self.silenced = False

  def _write(self, kind, key, value, block):
    assert block
    self._key_attempts[key] = self._key_attempts.get(key, 0) + 1
    if key == self.silent_key and self._key_attempts[key] == self.silent_occurrence and not self.silenced:
      self.silenced = True
      return
    typed = bool(value) if kind == "bool" else value
    self.values[key] = typed
    self.writes.append((key, typed, kind, block))


class FailAfterWriteOnceParams(FakeParams):
  def __init__(self, values=None, *, fail_key, fail_occurrence=1):
    super().__init__(values)
    self.post_fail_key = fail_key
    self.post_fail_occurrence = fail_occurrence
    self.post_failed = False

  def _write(self, kind, key, value, block):
    super()._write(kind, key, value, block)
    if key == self.post_fail_key and self._key_attempts[key] == self.post_fail_occurrence and not self.post_failed:
      self.post_failed = True
      raise RuntimeError(f"post-write interruption {key}")


class WrongTypeReadbackOnceParams(FakeParams):
  def __init__(self, values=None, *, corrupt_key, replacement, corrupt_occurrence=1):
    super().__init__(values)
    self.corrupt_key = corrupt_key
    self.replacement = replacement
    self.corrupt_occurrence = corrupt_occurrence
    self.corrupted = False

  def get(self, key, return_default=False):
    value = super().get(key, return_default=return_default)
    if key == self.corrupt_key and self._key_attempts.get(key, 0) >= self.corrupt_occurrence and not self.corrupted:
      self.corrupted = True
      return self.replacement
    return value


class ApplyAndCleanupFailureParams(FakeParams):
  def __init__(self, values=None, *, cleanup_key, cleanup_occurrence):
    super().__init__(values)
    self.cleanup_key = cleanup_key
    self.cleanup_occurrence = cleanup_occurrence

  def _write(self, kind, key, value, block):
    assert block
    self._key_attempts[key] = self._key_attempts.get(key, 0) + 1
    if key == HANDCRAFTED_STATUS_PARAM and self._key_attempts[key] == 1:
      raise RuntimeError("interrupted success marker")
    if key == self.cleanup_key and self._key_attempts[key] == self.cleanup_occurrence:
      raise RuntimeError(f"interrupted cleanup {key}")
    typed = bool(value) if kind == "bool" else value
    self.values[key] = typed
    self.writes.append((key, typed, kind, block))


def clarity_context(*, firmware=b"39990-TRW-A020", modified=True, tuning="torque"):
  CP = SimpleNamespace(
    brand="honda",
    carFingerprint="HONDA_CLARITY",
    carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
    lateralTuning=SimpleNamespace(which=lambda: tuning),
  )
  flags = HondaFlagsSP.EPS_MODIFIED.value if modified else 0
  return CP, SimpleNamespace(flags=flags)


def legacy_context(fingerprint="HONDA_ACCORD"):
  return SimpleNamespace(brand="honda", carFingerprint=fingerprint), None


def vehicle_context(fingerprint, *, brand="toyota"):
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint)


def requested_params(cls=FakeParams, **kwargs):
  return cls({HANDCRAFTED_REQUEST_PARAM: True, "IsOffroad": True, "ParamsVersion": 7}, **kwargs)


def test_profiles_are_versioned_and_clarity_v17_matches_exact_47_key_oracle():
  assert HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS == EXPECTED_FINGERPRINTS
  assert tuple(HANDCRAFTED_LATERAL_PROFILES) == EXPECTED_FINGERPRINTS
  clarity = get_handcrafted_lateral_profile("HONDA_CLARITY")
  assert clarity is CLARITY_ROAD_TESTED_2026_08_28
  assert clarity.name == "Honda Clarity Current Lateral 2026-08-28"
  assert clarity.version == 17
  assert clarity.values == CLARITY_HANDCRAFTED_VALUES_V17
  assert tuple(key for key, _ in clarity.values) == tuple(EXPECTED_CLARITY_V17_VALUES)
  assert dict(clarity.values) == EXPECTED_CLARITY_V17_VALUES
  assert len(clarity.values) == len(dict(clarity.values)) == 47


def test_non_clarity_profiles_remain_safe_legacy_v15_without_blend_or_steer_ratio_ownership():
  clarity_values = dict(CLARITY_ROAD_TESTED_2026_08_28.values)
  for fingerprint in EXPECTED_FINGERPRINTS:
    profile = get_handcrafted_lateral_profile(fingerprint)
    assert profile.fingerprint == fingerprint
    if fingerprint == "HONDA_CLARITY":
      continue
    values = dict(profile.values)
    assert profile.version == 15
    assert len(values) == 38
    assert BLEND_MASTER_PARAM not in values
    assert STEER_RATIO_MODE_PARAM not in values
    assert not any(key.startswith("NrdrInterpolatedTorque") for key in values)
    assert values["HondaCenterScale"] == 1.0
    assert values["LatFScaleLowSpeed"] == 100
    assert values != clarity_values
  assert get_handcrafted_lateral_profile("HONDA_CIVIC_2022") is None


def test_clarity_support_requires_exact_firmware_map_modified_eps_and_supported_controller():
  CP, CP_SP = clarity_context()
  assert handcrafted_lateral_profile_supported(CP, CP_SP)
  assert not handcrafted_lateral_profile_supported(*clarity_context(firmware=b"39990-TRW-A021"))
  assert not handcrafted_lateral_profile_supported(*clarity_context(modified=False))
  assert not handcrafted_lateral_profile_supported(*clarity_context(tuning="indi"))
  assert not handcrafted_lateral_profile_supported("HONDA_CLARITY", None)
  assert handcrafted_lateral_profile_supported(vehicle_context("HONDA_ACCORD", brand="honda"), None)
  assert not handcrafted_lateral_profile_supported("HONDA_CIVIC_2022", None)
  assert not handcrafted_lateral_profile_supported(
    vehicle_context("HONDA_ACCORD", brand="honda"), None, "LEXUS_ES_TSS2", "toyota",
  )
  assert not handcrafted_lateral_profile_supported(
    vehicle_context("HONDA_ACCORD", brand="honda"), None, "HONDA_ACCORD", "toyota",
  )


def test_confirmed_vehicle_identity_requires_live_cp_and_exact_selection_match():
  honda = vehicle_context("HONDA_ACCORD", brand="honda")
  assert confirmed_vehicle_identity(honda) == ("HONDA_ACCORD", "honda")
  assert confirmed_vehicle_identity(honda, "HONDA_ACCORD", "honda") == ("HONDA_ACCORD", "honda")
  assert confirmed_vehicle_identity(None, "HONDA_ACCORD", "honda") is None
  assert confirmed_vehicle_identity(honda, "LEXUS_ES_TSS2", "toyota") is None
  assert confirmed_vehicle_identity(honda, "HONDA_ACCORD", "toyota") is None
  assert confirmed_vehicle_identity(honda, "", "", selection_present=True) is None
  assert confirmed_vehicle_identity(honda, "", "", selection_present=False) == ("HONDA_ACCORD", "honda")
  assert confirmed_vehicle_identity(vehicle_context("", brand="honda")) is None
  assert confirmed_vehicle_identity(vehicle_context("HONDA_ACCORD", brand="")) is None
  assert confirmed_vehicle_identity(vehicle_context("HYUNDAI_SONATA", brand="hyundai")) == ("HYUNDAI_SONATA", "hyundai")


def test_no_request_or_onroad_request_never_writes():
  CP, CP_SP = clarity_context()
  absent = FakeParams({"IsOffroad": True})
  assert not consume_handcrafted_lateral_request(CP, CP_SP, absent)
  assert absent.writes == []

  onroad = FakeParams({HANDCRAFTED_REQUEST_PARAM: True, "IsOffroad": False})
  assert consume_handcrafted_lateral_request(CP, CP_SP, onroad) == []
  assert onroad.get_bool(HANDCRAFTED_REQUEST_PARAM)
  assert onroad.writes == []


@pytest.mark.parametrize(("fingerprint", "startup", "offroad"), (
  ("LEXUS_ES_TSS2", False, True),
  ("LEXUS_ES_TSS2", True, False),
  ("TOYOTA_CAMRY_TSS2", False, True),
))
def test_confirmed_unsupported_vehicle_terminally_clears_only_request(fingerprint, startup, offroad):
  protected = {
    "HondaCenterScale": 0.37,
    "NrdrStarPilotPid": True,
    HANDCRAFTED_STATUS_PARAM: "Last applied: preserved marker",
    "ParamsVersion": 41,
  }
  params = FakeParams({
    **protected,
    HANDCRAFTED_REQUEST_PARAM: True,
    "IsOffroad": offroad,
    "CarPlatformBundle": {"brand": "toyota", "platform": fingerprint},
  })

  assert consume_handcrafted_lateral_request(
    vehicle_context(fingerprint), None, params, startup=startup,
  ) == []

  assert params.values[HANDCRAFTED_REQUEST_PARAM] is False
  assert {key: params.values[key] for key in protected} == protected
  assert params.writes == [(HANDCRAFTED_REQUEST_PARAM, False, "bool", True)]


def test_confirmed_unsupported_cp_is_sufficient_without_a_selection_bundle():
  params = requested_params()
  params.values["HondaCenterScale"] = 0.37

  assert consume_handcrafted_lateral_request(vehicle_context("LEXUS_ES_TSS2"), None, params) == []

  assert params.values[HANDCRAFTED_REQUEST_PARAM] is False
  assert params.values["HondaCenterScale"] == 0.37
  assert params.writes == [(HANDCRAFTED_REQUEST_PARAM, False, "bool", True)]


@pytest.mark.parametrize(("CP", "bundle"), (
  (None, {"brand": "toyota", "platform": "LEXUS_ES_TSS2"}),
  (vehicle_context("LEXUS_ES_TSS2"), {"brand": "honda", "platform": "HONDA_CLARITY"}),
  (clarity_context()[0], {"brand": "toyota", "platform": "LEXUS_ES_TSS2"}),
  (clarity_context()[0], {"brand": "toyota", "platform": "HONDA_CLARITY"}),
  (vehicle_context("LEXUS_ES_TSS2"), {}),
  (vehicle_context("LEXUS_ES_TSS2"), {"brand": "toyota"}),
  (vehicle_context("LEXUS_ES_TSS2"), {"platform": "LEXUS_ES_TSS2"}),
  (vehicle_context("LEXUS_ES_TSS2"), ["toyota", "LEXUS_ES_TSS2"]),
))
def test_unknown_or_mismatched_identity_preserves_pending_intent_without_writes(CP, bundle):
  params = requested_params()
  params.values.update({
    "CarPlatformBundle": bundle,
    "HondaCenterScale": 0.37,
    HANDCRAFTED_STATUS_PARAM: "Last applied: preserved marker",
  })

  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []

  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values[HANDCRAFTED_STATUS_PARAM] == "Last applied: preserved marker"
  assert params.values["ParamsVersion"] == 7
  assert params.writes == []


def test_physically_present_null_selection_is_invalid_not_cp_fallback(tmp_path):
  bundle_path = tmp_path / "CarPlatformBundle"
  bundle_path.write_text("null", encoding="utf-8")

  class NullBundleParams(FakeParams):
    def get_param_path(self, key=""):
      assert key == "CarPlatformBundle"
      return str(bundle_path)

  params = NullBundleParams({
    HANDCRAFTED_REQUEST_PARAM: True,
    "IsOffroad": True,
    "ParamsVersion": 7,
    "CarPlatformBundle": None,
  })

  assert get_selected_car_identity(params) == (True, "", "")
  assert consume_handcrafted_lateral_request(vehicle_context("LEXUS_ES_TSS2"), None, params) == []
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert params.writes == []


def test_unreviewed_honda_and_transient_clarity_capability_remain_pending_silently():
  cases = (
    (vehicle_context("HONDA_CIVIC_2022", brand="honda"), None),
    (clarity_context(firmware=b"39990-TRW-A021")[0], clarity_context()[1]),
    (clarity_context()[0], None),
  )
  for CP, CP_SP in cases:
    params = requested_params()
    assert consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True) == []
    assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
    assert params.writes == []


def test_repeated_unsupported_toyota_boot_is_a_single_terminal_clear_without_retry():
  params = requested_params()
  params.values["HondaCenterScale"] = 0.37
  CP = vehicle_context("LEXUS_ES_TSS2")

  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []
  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []

  assert params.writes == [(HANDCRAFTED_REQUEST_PARAM, False, "bool", True)]
  assert params.values["HondaCenterScale"] == 0.37


def test_terminal_clear_write_failure_never_falls_through_to_tune_writes():
  params = requested_params(fail_key=HANDCRAFTED_REQUEST_PARAM)
  params.values["HondaCenterScale"] = 0.37

  with pytest.raises(RuntimeError, match="interrupted"):
    consume_handcrafted_lateral_request(vehicle_context("LEXUS_ES_TSS2"), None, params)

  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["ParamsVersion"] == 7
  assert params.writes == []


def test_terminal_clear_readback_failure_never_falls_through_to_tune_writes():
  params = SilentWriteOnceParams(
    {HANDCRAFTED_REQUEST_PARAM: True, "IsOffroad": True, "ParamsVersion": 7, "HondaCenterScale": 0.37},
    silent_key=HANDCRAFTED_REQUEST_PARAM,
  )

  with pytest.raises(RuntimeError, match="readback mismatch"):
    consume_handcrafted_lateral_request(vehicle_context("LEXUS_ES_TSS2"), None, params)

  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["ParamsVersion"] == 7
  assert params.writes == []


def test_clarity_one_shot_uses_fail_safe_blocking_order_and_verified_finalization():
  CP, CP_SP = clarity_context()
  params = requested_params()

  written = consume_handcrafted_lateral_request(CP, CP_SP, params)

  profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
  expected_underlying = [key for key, _ in profile.values if key not in (BLEND_MASTER_PARAM, STEER_RATIO_MODE_PARAM)]
  expected_order = [
    BLEND_MASTER_PARAM,
    *expected_underlying,
    STEER_RATIO_MODE_PARAM,
    BLEND_MASTER_PARAM,
    "ParamsVersion",
    HANDCRAFTED_STATUS_PARAM,
    HANDCRAFTED_REQUEST_PARAM,
  ]
  assert written == expected_order[:-3]
  assert [key for key, *_ in params.writes] == expected_order
  assert params.writes[0][1] is False
  assert params.writes[-4][1] is True
  assert all(block is True for *_, block in params.writes)
  assert all(type(params.values[key]) is type(value) and params.values[key] == value for key, value in profile.values)
  assert params.values[HANDCRAFTED_STATUS_PARAM].startswith("Last applied: ")
  assert params.values["ParamsVersion"] == 8
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is False


@pytest.mark.parametrize(("fail_key", "occurrence"), (
  (BLEND_MASTER_PARAM, 1),
  ("HondaCenterScale", 1),
  (STEER_RATIO_MODE_PARAM, 1),
  (BLEND_MASTER_PARAM, 2),
  (HANDCRAFTED_STATUS_PARAM, 1),
  ("ParamsVersion", 1),
  (HANDCRAFTED_REQUEST_PARAM, 1),
))
def test_interrupted_apply_retains_request_and_retry_completes(fail_key, occurrence):
  CP, CP_SP = clarity_context()
  params = requested_params(fail_key=fail_key, fail_occurrence=occurrence)

  with pytest.raises(RuntimeError, match="interrupted"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)
  assert params.get_bool(HANDCRAFTED_REQUEST_PARAM)
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert params.values[BLEND_MASTER_PARAM] is False

  assert consume_handcrafted_lateral_request(CP, CP_SP, params)
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is False
  assert dict(get_handcrafted_lateral_profile("HONDA_CLARITY").values).items() <= params.values.items()
  assert params.writes[-4][0:2] == (BLEND_MASTER_PARAM, True)


def test_silent_payload_write_is_detected_while_blend_is_verified_off():
  CP, CP_SP = clarity_context()
  params = requested_params(
    SilentWriteOnceParams,
    silent_key="HondaCenterScale",
  )

  with pytest.raises(RuntimeError, match="HondaCenterScale"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  assert all(value is False for key, value, *_ in params.writes if key == BLEND_MASTER_PARAM)


def test_card_style_catch_continues_startup_only_with_partial_profile_disabled():
  CP, CP_SP = clarity_context()
  params = requested_params(
    SilentWriteOnceParams,
    silent_key="HondaCenterScale",
  )
  firmware_query_done = False

  try:
    consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True)
  except Exception:
    firmware_query_done = True

  assert firmware_query_done
  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True


@pytest.mark.parametrize(("cleanup_key", "cleanup_occurrence"), (
  (BLEND_MASTER_PARAM, 3),
  (HANDCRAFTED_REQUEST_PARAM, 1),
))
def test_unverified_safe_state_raises_dedicated_fatal_error(cleanup_key, cleanup_occurrence):
  CP, CP_SP = clarity_context()
  params = requested_params(
    ApplyAndCleanupFailureParams,
    cleanup_key=cleanup_key,
    cleanup_occurrence=cleanup_occurrence,
  )

  with pytest.raises(HandcraftedLateralUnsafeStateError, match="safe-state cleanup failed") as exc_info:
    consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True)

  assert isinstance(exc_info.value.__cause__, RuntimeError)
  assert "interrupted success marker" in str(exc_info.value.__cause__)


@pytest.mark.parametrize("fail_key", (
  "ParamsVersion",
  HANDCRAFTED_STATUS_PARAM,
  HANDCRAFTED_REQUEST_PARAM,
))
def test_every_finalization_failure_rolls_back_blend_and_retains_request(fail_key):
  CP, CP_SP = clarity_context()
  params = requested_params(fail_key=fail_key)

  with pytest.raises(RuntimeError, match="interrupted"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True


def test_post_write_request_clear_exception_rejournals_true_and_fails_closed():
  CP, CP_SP = clarity_context()
  params = requested_params(
    FailAfterWriteOnceParams,
    fail_key=HANDCRAFTED_REQUEST_PARAM,
  )

  with pytest.raises(RuntimeError, match="post-write interruption"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True
  request_writes = [value for key, value, *_ in params.writes if key == HANDCRAFTED_REQUEST_PARAM]
  assert request_writes[-2:] == [False, True]


def test_params_version_failure_preserves_prior_success_marker():
  CP, CP_SP = clarity_context()
  prior = "Last applied: prior profile (v15) [HONDA_CLARITY]"
  params = requested_params(fail_key="ParamsVersion")
  params.values[HANDCRAFTED_STATUS_PARAM] = prior

  with pytest.raises(RuntimeError, match="ParamsVersion"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert params.values[HANDCRAFTED_STATUS_PARAM] == prior
  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True


@pytest.mark.parametrize(("key", "replacement", "occurrence"), (
  (BLEND_MASTER_PARAM, 0, 1),
  (BLEND_MASTER_PARAM, 1, 2),
  (HANDCRAFTED_REQUEST_PARAM, 0, 1),
))
def test_bool_readbacks_reject_int_aliases_and_cleanup_exactly(key, replacement, occurrence):
  CP, CP_SP = clarity_context()
  params = requested_params(
    WrongTypeReadbackOnceParams,
    corrupt_key=key,
    replacement=replacement,
    corrupt_occurrence=occurrence,
  )

  with pytest.raises(RuntimeError, match="readback mismatch"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert type(params.values[BLEND_MASTER_PARAM]) is bool
  assert params.values[BLEND_MASTER_PARAM] is False
  assert type(params.values[HANDCRAFTED_REQUEST_PARAM]) is bool
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True


def test_params_version_readback_rejects_bool_alias_before_marker():
  CP, CP_SP = clarity_context()
  params = requested_params(
    WrongTypeReadbackOnceParams,
    corrupt_key="ParamsVersion",
    replacement=True,
  )
  params.values.pop("ParamsVersion")

  with pytest.raises(RuntimeError, match="ParamsVersion"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)

  assert HANDCRAFTED_STATUS_PARAM not in params.values
  assert params.values[BLEND_MASTER_PARAM] is False
  assert params.values[HANDCRAFTED_REQUEST_PARAM] is True


def test_type_strict_readback_rejects_bool_int_alias_and_retains_request():
  CP, CP_SP = clarity_context()
  params = requested_params(BoolAsIntReadbackParams)

  with pytest.raises(RuntimeError, match="readback mismatch"):
    consume_handcrafted_lateral_request(CP, CP_SP, params)
  assert params.get_bool(HANDCRAFTED_REQUEST_PARAM)
  assert HANDCRAFTED_STATUS_PARAM not in params.values


def test_legacy_true_is_one_pending_apply_and_manual_edits_are_never_reapplied():
  CP, CP_SP = clarity_context()
  params = requested_params()
  assert consume_handcrafted_lateral_request(CP, CP_SP, params)
  applied_writes = len(params.writes)

  params.values["HondaCenterScale"] = 2.22
  assert not consume_handcrafted_lateral_request(CP, CP_SP, params)
  assert len(params.writes) == applied_writes
  assert params.values["HondaCenterScale"] == 2.22
  status = handcrafted_lateral_profile_status(CP, CP_SP, params)
  assert status.startswith("Last applied: ")
  assert status.endswith(" | customized")


def test_status_is_pure_and_preserves_last_success_across_pending_failure_version_and_support_changes():
  CP, CP_SP = clarity_context()
  old_marker = "Last applied: prior profile (v15) [HONDA_CLARITY]"
  params = FakeParams({
    HANDCRAFTED_REQUEST_PARAM: True,
    HANDCRAFTED_STATUS_PARAM: old_marker + " | exact match",
  })

  pending = handcrafted_lateral_profile_status(CP, CP_SP, params)
  assert pending == old_marker + " | apply requested; waiting for verified completion"
  assert params.writes == []

  params.values[HANDCRAFTED_REQUEST_PARAM] = False
  version_changed = handcrafted_lateral_profile_status(CP, CP_SP, params)
  assert version_changed == old_marker + " | current profile v17 not applied"

  unsupported = handcrafted_lateral_profile_status(*clarity_context(modified=False), params)
  assert unsupported == old_marker + " | unavailable for detected car/EPS"
  assert params.writes == []


def test_unsupported_request_remains_durable_and_legacy_profiles_apply_without_clarity_extensions():
  CP, CP_SP = clarity_context(modified=False)
  unsupported = requested_params()
  assert consume_handcrafted_lateral_request(CP, CP_SP, unsupported) == []
  assert unsupported.get_bool(HANDCRAFTED_REQUEST_PARAM)
  assert unsupported.writes == []

  legacy_CP, legacy_CP_SP = legacy_context()
  legacy = requested_params()
  assert consume_handcrafted_lateral_request(legacy_CP, legacy_CP_SP, legacy)
  keys = [key for key, *_ in legacy.writes]
  assert BLEND_MASTER_PARAM not in keys
  assert STEER_RATIO_MODE_PARAM not in keys
  assert legacy.values[HANDCRAFTED_REQUEST_PARAM] is False


def test_card_startup_is_the_only_explicit_non_offroad_consumer_exception():
  card = Path("openpilot/selfdrive/car/card.py").read_text(encoding="utf-8")
  remoted = Path("openpilot/sunnypilot/nrdr/remoted.py").read_text(encoding="utf-8")
  reporter = Path("openpilot/sunnypilot/nrdr/car_tune_report.py").read_text(encoding="utf-8")
  assert "consume_handcrafted_lateral_request(self.CP, self.CP_SP, self.params, startup=True)" in card
  assert card.index("consume_handcrafted_lateral_request") < card.index('self.params.put_bool("FirmwareQueryDone"')
  fatal_handler = "except HandcraftedLateralUnsafeStateError:"
  ordinary_handler = "except Exception:"
  consume_call = card.index("consume_handcrafted_lateral_request(self.CP, self.CP_SP, self.params, startup=True)")
  fatal_index = card.index(fatal_handler, consume_call)
  ordinary_index = card.index(ordinary_handler, fatal_index)
  firmware_done_index = card.index('self.params.put_bool("FirmwareQueryDone"', ordinary_index)
  assert consume_call < fatal_index < ordinary_index < firmware_done_index
  fatal_body = card[fatal_index:ordinary_index]
  assert "raise" in fatal_body
  assert "aborting startup" in fatal_body
  assert "consume_handcrafted_lateral_request(CP, CP_SP, params)" in remoted
  assert "startup=True" not in remoted
  assert 'not params.get_bool("IsOffroad")' in remoted
  assert "request retained" in remoted
  assert "handcrafted_lateral_profile_status(CP, CP_SP, self.params)" in reporter
  assert "consume_handcrafted_lateral_request" not in reporter


def test_native_ui_fail_closed_hides_honda_only_groups_and_special_page():
  root = Path("openpilot")
  lateral = (root / "selfdrive" / "ui" / "sunnypilot" / "layouts" / "settings" /
             "nrdr_sub_layouts" / "lateral_tuning.py").read_text(encoding="utf-8")
  layout = (root / "selfdrive" / "ui" / "sunnypilot" / "layouts" / "settings" /
            "nrdr.py").read_text(encoding="utf-8")

  assert "get_selected_car_identity(ui_state.params)" in lateral
  assert "selection_present=selection_present" in lateral
  assert 'identity is not None and identity[1] == "honda"' in lateral
  assert "HONDA_ONLY_LATERAL_PANELS" in lateral
  for panel in ("PIDF", "OVERRIDE", "STEER_FILTERS"):
    assert f"LateralPanel.{panel}" in lateral
  assert "for item in self._honda_only_items:" in lateral
  assert "if self._current_panel in HONDA_ONLY_LATERAL_PANELS and not honda_available:" in lateral
  assert "self._handcrafted_apply.set_visible(False)" in lateral
  assert "self._honda_only_items = (self._party_tricks_separator, self._party_tricks_button)" in layout
  assert layout.count("for item in self._honda_only_items:") == 2
  assert "panel == PanelType.PARTY_TRICKS and not honda_tuning_available()" in layout
