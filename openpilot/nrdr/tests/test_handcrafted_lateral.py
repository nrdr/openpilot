import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.params import (
  CLARITY_HANDCRAFTED_LATERAL_VALUES_V17,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HandcraftedLateralUnsafeStateError,
  confirmed_vehicle_identity,
  consume_handcrafted_lateral_request,
  get_handcrafted_lateral_profile,
  get_selected_car_identity,
  handcrafted_lateral_profile_status,
  handcrafted_lateral_profile_supported,
  handcrafted_lateral_success_marker,
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

EXPECTED_CLARITY_V17 = {
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
  def __init__(self, values=None, *, fail_on_call=None, fail_on_calls=(), fail_after_call=None, corrupt_reads=None,
               readback_overrides=None, silent_puts=(), silent_writes=()):
    self.values = dict(values or {})
    self.calls = []
    self.fail_on_call = fail_on_call
    self.fail_on_calls = set(fail_on_calls)
    self.fail_after_call = fail_after_call
    self.corrupt_reads = dict(corrupt_reads or {})
    self.readback_overrides = dict(readback_overrides or {})
    self.silent_puts = set(silent_puts)
    self.silent_writes = set(silent_writes)
    self.write_counts = {}

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    if key in self.corrupt_reads:
      return self.corrupt_reads[key]
    token = (key, self.write_counts.get(key, 0))
    if token in self.readback_overrides:
      return self.readback_overrides.pop(token)
    return self.values.get(key)

  def _write(self, method, key, value, block):
    call_index = len(self.calls)
    self.calls.append((method, key, value, block))
    if call_index == self.fail_on_call or call_index in self.fail_on_calls:
      raise OSError("injected interruption")
    self.write_counts[key] = self.write_counts.get(key, 0) + 1
    write_token = (key, self.write_counts[key])
    if key not in self.silent_puts and write_token not in self.silent_writes:
      self.values[key] = value
    if call_index == self.fail_after_call:
      raise OSError("injected post-write interruption")

  def put_bool(self, key, value, block=False):
    self._write("put_bool", key, bool(value), block)

  def put(self, key, value, block=False):
    self._write("put", key, value, block)


def clarity_cp(*, firmware=True, lateral="pid"):
  fw = [SimpleNamespace(ecu="eps", fwVersion=b"39990-TRW-A020\x00")] if firmware else []
  return SimpleNamespace(
    brand="honda",
    carFingerprint="HONDA_CLARITY",
    carFw=fw,
    lateralTuning=SimpleNamespace(which=lambda: lateral),
  )


def clarity_cp_sp(*, modified=True):
  return SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0)


def vehicle_cp(fingerprint, *, brand="toyota"):
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint)


def pending_params(values=None, **kwargs):
  return FakeParams({
    "NrdrHandcraftedLateralTune": True,
    "IsOffroad": True,
    "ParamsVersion": 5,
    **(values or {}),
  }, **kwargs)


def test_profiles_are_fingerprint_scoped_and_clarity_only_is_v17():
  assert HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS == EXPECTED_FINGERPRINTS
  assert tuple(HANDCRAFTED_LATERAL_PROFILES) == EXPECTED_FINGERPRINTS
  assert get_handcrafted_lateral_profile("HONDA_CLARITY").version == 17
  for fingerprint in EXPECTED_FINGERPRINTS:
    profile = get_handcrafted_lateral_profile(fingerprint)
    assert profile.fingerprint == fingerprint
    assert profile.version == (17 if fingerprint == "HONDA_CLARITY" else 15)
    assert len(profile.values) == len(dict(profile.values))
  assert get_handcrafted_lateral_profile("HONDA_CIVIC_2022") is None


def test_clarity_v17_is_exact_47_key_reviewed_oracle():
  profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
  assert profile.values == CLARITY_HANDCRAFTED_LATERAL_VALUES_V17
  assert len(profile.values) == 47
  assert dict(profile.values) == EXPECTED_CLARITY_V17
  source = Path(__file__).parents[1] / "params" / "profiles.py"
  provenance = source.read_text(encoding="utf-8")
  assert "d9bea117c3ef7a30c8f67c809b386f35e89fd2ba1158dbe7cb30b1b6ded5c97a" in provenance
  assert "bd8b0ebfc10342ff6405c50659eeb24645439d4f06ea4a145ca25dfa998a8e3d" in provenance


def test_legacy_profiles_never_receive_clarity_firmware_or_blend_values():
  clarity_only = {
    "NrdrSteerRatioMode", "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal",
    "NrdrInterpolatedTorquePifBlend", "NrdrInterpolatedTorqueShare",
    "NrdrInterpolatedTorqueLatAccelFactor", "NrdrInterpolatedTorqueFriction",
    "NrdrInterpolatedTorqueFrictionStandard", "NrdrInterpolatedTorqueFrictionHighway",
  }
  for fingerprint in EXPECTED_FINGERPRINTS:
    if fingerprint == "HONDA_CLARITY":
      continue
    assert not clarity_only & dict(get_handcrafted_lateral_profile(fingerprint).values).keys()


def test_shared_support_predicate_requires_exact_clarity_eps_and_modified_flag():
  assert handcrafted_lateral_profile_supported(clarity_cp(), clarity_cp_sp())
  assert not handcrafted_lateral_profile_supported(clarity_cp(firmware=False), clarity_cp_sp())
  assert not handcrafted_lateral_profile_supported(clarity_cp(), clarity_cp_sp(modified=False))
  assert not handcrafted_lateral_profile_supported(None, None, "HONDA_CLARITY")
  assert not handcrafted_lateral_profile_supported(None, None, "HONDA_CIVIC")
  assert handcrafted_lateral_profile_supported(vehicle_cp("HONDA_CIVIC", brand="honda"), None)
  assert not handcrafted_lateral_profile_supported(None, None, "HONDA_CIVIC_2022")
  assert not handcrafted_lateral_profile_supported(
    vehicle_cp("HONDA_CIVIC", brand="honda"), None, "LEXUS_ES_TSS2", "toyota",
  )
  assert not handcrafted_lateral_profile_supported(
    vehicle_cp("HONDA_CIVIC", brand="honda"), None, "HONDA_CIVIC", "toyota",
  )


def test_confirmed_vehicle_identity_requires_live_cp_and_exact_selection_match():
  honda = vehicle_cp("HONDA_CIVIC", brand="honda")
  assert confirmed_vehicle_identity(honda) == ("HONDA_CIVIC", "honda")
  assert confirmed_vehicle_identity(honda, "HONDA_CIVIC", "honda") == ("HONDA_CIVIC", "honda")
  assert confirmed_vehicle_identity(None, "HONDA_CIVIC", "honda") is None
  assert confirmed_vehicle_identity(honda, "LEXUS_ES_TSS2", "toyota") is None
  assert confirmed_vehicle_identity(honda, "HONDA_CIVIC", "toyota") is None
  assert confirmed_vehicle_identity(honda, "", "", selection_present=True) is None
  assert confirmed_vehicle_identity(honda, "", "", selection_present=False) == ("HONDA_CIVIC", "honda")
  assert confirmed_vehicle_identity(vehicle_cp("", brand="honda")) is None
  assert confirmed_vehicle_identity(vehicle_cp("HONDA_CIVIC", brand="")) is None
  assert confirmed_vehicle_identity(vehicle_cp("HYUNDAI_SONATA", brand="hyundai")) == ("HYUNDAI_SONATA", "hyundai")


def test_success_is_blocking_ordered_verified_versioned_and_auto_clears():
  params = pending_params()
  written = consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert dict(get_handcrafted_lateral_profile("HONDA_CLARITY").values).items() <= params.values.items()
  assert params.values["NrdrHandcraftedLateralTune"] is False
  assert params.values["ParamsVersion"] == 6
  marker = handcrafted_lateral_success_marker(get_handcrafted_lateral_profile("HONDA_CLARITY"))
  assert params.values["NrdrCarHandcraftedInfo"] == marker
  assert written[0] == "NrdrInterpolatedTorquePifBlend"
  assert written[-2:] == ["NrdrSteerRatioMode", "NrdrInterpolatedTorquePifBlend"]
  assert params.calls[0][:3] == ("put_bool", "NrdrInterpolatedTorquePifBlend", False)
  assert params.calls[-3][:3] == ("put", "ParamsVersion", 6)
  assert params.calls[-2][:3] == ("put", "NrdrCarHandcraftedInfo", marker)
  assert params.calls[-1][:3] == ("put_bool", "NrdrHandcraftedLateralTune", False)
  assert all(call[3] is True for call in params.calls)


def test_request_is_never_consumed_onroad():
  params = pending_params({"IsOffroad": False})
  assert consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params) == []
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.calls == []


@pytest.mark.parametrize(("fingerprint", "startup", "offroad"), (
  ("LEXUS_ES_TSS2", False, True),
  ("LEXUS_ES_TSS2", True, False),
  ("TOYOTA_CAMRY_TSS2", False, True),
))
def test_confirmed_unsupported_vehicle_terminally_clears_only_request(fingerprint, startup, offroad):
  protected = {
    "HondaCenterScale": 0.37,
    "NrdrStarPilotPid": True,
    "NrdrCarHandcraftedInfo": "Last applied: preserved marker",
    "ParamsVersion": 41,
  }
  params = pending_params({
    **protected,
    "IsOffroad": offroad,
    "CarPlatformBundle": {"brand": "toyota", "platform": fingerprint},
  })

  assert consume_handcrafted_lateral_request(
    vehicle_cp(fingerprint), None, params, startup=startup,
  ) == []

  assert params.values["NrdrHandcraftedLateralTune"] is False
  assert {key: params.values[key] for key in protected} == protected
  assert params.calls == [("put_bool", "NrdrHandcraftedLateralTune", False, True)]


def test_confirmed_unsupported_cp_is_sufficient_without_a_selection_bundle():
  params = pending_params({"HondaCenterScale": 0.37})

  assert consume_handcrafted_lateral_request(vehicle_cp("LEXUS_ES_TSS2"), None, params) == []

  assert params.values["NrdrHandcraftedLateralTune"] is False
  assert params.values["HondaCenterScale"] == 0.37
  assert params.calls == [("put_bool", "NrdrHandcraftedLateralTune", False, True)]


@pytest.mark.parametrize(("CP", "bundle"), (
  (None, {"brand": "toyota", "platform": "LEXUS_ES_TSS2"}),
  (vehicle_cp("LEXUS_ES_TSS2"), {"brand": "honda", "platform": "HONDA_CLARITY"}),
  (clarity_cp(), {"brand": "toyota", "platform": "LEXUS_ES_TSS2"}),
  (clarity_cp(), {"brand": "toyota", "platform": "HONDA_CLARITY"}),
  (vehicle_cp("LEXUS_ES_TSS2"), {}),
  (vehicle_cp("LEXUS_ES_TSS2"), {"brand": "toyota"}),
  (vehicle_cp("LEXUS_ES_TSS2"), {"platform": "LEXUS_ES_TSS2"}),
  (vehicle_cp("LEXUS_ES_TSS2"), ["toyota", "LEXUS_ES_TSS2"]),
))
def test_unknown_or_mismatched_identity_preserves_pending_intent_without_writes(CP, bundle):
  params = pending_params({
    "CarPlatformBundle": bundle,
    "HondaCenterScale": 0.37,
    "NrdrCarHandcraftedInfo": "Last applied: preserved marker",
  })

  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []

  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["NrdrCarHandcraftedInfo"] == "Last applied: preserved marker"
  assert params.values["ParamsVersion"] == 5
  assert params.calls == []


def test_physically_present_null_selection_is_invalid_not_cp_fallback(tmp_path):
  bundle_path = tmp_path / "CarPlatformBundle"
  bundle_path.write_text("null", encoding="utf-8")

  class NullBundleParams(FakeParams):
    def get_param_path(self, key=""):
      assert key == "CarPlatformBundle"
      return str(bundle_path)

  params = NullBundleParams({
    "NrdrHandcraftedLateralTune": True,
    "IsOffroad": True,
    "ParamsVersion": 5,
    "CarPlatformBundle": None,
  })

  assert get_selected_car_identity(params) == (True, "", "")
  assert consume_handcrafted_lateral_request(vehicle_cp("LEXUS_ES_TSS2"), None, params) == []
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.calls == []


def test_unreviewed_honda_and_transient_clarity_capability_remain_pending_silently():
  cases = (
    (vehicle_cp("HONDA_CIVIC_2022", brand="honda"), None),
    (clarity_cp(firmware=False), clarity_cp_sp()),
    (clarity_cp(), None),
  )
  for CP, CP_SP in cases:
    params = pending_params()
    assert consume_handcrafted_lateral_request(CP, CP_SP, params, startup=True) == []
    assert params.values["NrdrHandcraftedLateralTune"] is True
    assert params.calls == []


def test_repeated_unsupported_toyota_boot_is_a_single_terminal_clear_without_retry():
  params = pending_params({"HondaCenterScale": 0.37})
  CP = vehicle_cp("LEXUS_ES_TSS2")

  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []
  assert consume_handcrafted_lateral_request(CP, None, params, startup=True) == []

  assert params.calls == [("put_bool", "NrdrHandcraftedLateralTune", False, True)]
  assert params.values["HondaCenterScale"] == 0.37


@pytest.mark.parametrize("failure", ("write", "readback"))
def test_terminal_clear_failure_never_falls_through_to_tune_writes(failure):
  kwargs = {"fail_on_call": 0} if failure == "write" else {
    "silent_puts": {"NrdrHandcraftedLateralTune"},
  }
  params = pending_params({"HondaCenterScale": 0.37}, **kwargs)

  with pytest.raises((OSError, RuntimeError)):
    consume_handcrafted_lateral_request(vehicle_cp("LEXUS_ES_TSS2"), None, params)

  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["HondaCenterScale"] == 0.37
  assert params.values["ParamsVersion"] == 5
  assert params.calls == [("put_bool", "NrdrHandcraftedLateralTune", False, True)]


@pytest.mark.parametrize("failure_index", (0, 1, 12, 37, 46, 48, 49, 50))
def test_interruption_retains_request_and_full_retry_converges(failure_index):
  params = pending_params(fail_on_call=failure_index)
  with pytest.raises(OSError, match="injected interruption"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False

  params.fail_on_call = None
  params.calls.clear()
  consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)
  assert params.values["NrdrHandcraftedLateralTune"] is False
  assert dict(get_handcrafted_lateral_profile("HONDA_CLARITY").values).items() <= params.values.items()


def test_silent_payload_write_keeps_card_startup_safe_and_retry_pending():
  params = pending_params(silent_puts={"HondaCenterScale"})
  card_continued = False

  try:
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params, startup=True)
  except RuntimeError as error:
    assert "HondaCenterScale" in str(error)
    # Mirrors Card's guarded startup finisher: it logs and continues rather
    # than creating an ignition boot loop.
    card_continued = True

  assert card_continued
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False
  assert [call[1] for call in params.calls[-2:]] == [
    "NrdrInterpolatedTorquePifBlend", "NrdrHandcraftedLateralTune",
  ]
  assert "NrdrCarHandcraftedInfo" not in params.values
  assert params.values["ParamsVersion"] == 5


def test_post_write_request_clear_failure_rejournals_true_and_disables_blend():
  params = pending_params(fail_after_call=50)

  with pytest.raises(OSError, match="post-write interruption"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False
  assert [call[1] for call in params.calls[-2:]] == [
    "NrdrInterpolatedTorquePifBlend", "NrdrHandcraftedLateralTune",
  ]


def test_unverifiable_blend_off_cleanup_is_fatal_and_keeps_card_from_starting():
  # ParamsVersion fails after the blend has verified ON. The cleanup blend-OFF
  # write is then silently lost, so Card must not continue into controller
  # construction with the blend still enabled.
  params = pending_params(
    fail_on_call=48,
    silent_writes={("NrdrInterpolatedTorquePifBlend", 3)},
  )

  with pytest.raises(HandcraftedLateralUnsafeStateError, match="safe pending state"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params, startup=True)

  assert params.values["NrdrInterpolatedTorquePifBlend"] is True
  assert params.values["NrdrHandcraftedLateralTune"] is True


@pytest.mark.parametrize("failure", ("write", "readback"))
def test_blend_cleanup_write_or_readback_failure_is_fatal(failure):
  kwargs = {"fail_on_calls": {48, 49}} if failure == "write" else {
    "fail_on_call": 48,
    "readback_overrides": {("NrdrInterpolatedTorquePifBlend", 3): True},
  }
  params = pending_params(**kwargs)

  with pytest.raises(HandcraftedLateralUnsafeStateError, match="safe pending state"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params, startup=True)

  assert params.values["NrdrHandcraftedLateralTune"] is True


def test_unverifiable_request_restore_after_post_write_clear_is_fatal():
  # The final clear is durable before it throws. If the cleanup re-journal is
  # also silently lost, neither Card nor remoted may treat the apply as safely
  # retryable even though the blend itself was forced OFF.
  params = pending_params(
    fail_after_call=50,
    silent_writes={("NrdrHandcraftedLateralTune", 2)},
  )

  with pytest.raises(HandcraftedLateralUnsafeStateError, match="safe pending state"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params, startup=True)

  assert params.values["NrdrInterpolatedTorquePifBlend"] is False
  assert params.values["NrdrHandcraftedLateralTune"] is False


@pytest.mark.parametrize(("key", "write_number", "coerced_readback"), (
  ("NrdrInterpolatedTorquePifBlend", 1, 0),
  ("NrdrInterpolatedTorquePifBlend", 2, 1),
  ("NrdrHandcraftedLateralTune", 1, 0),
))
def test_bool_as_int_readback_is_rejected_and_cleanup_is_exact(key, write_number, coerced_readback):
  params = pending_params(readback_overrides={(key, write_number): coerced_readback})

  with pytest.raises(RuntimeError, match="readback mismatch"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert type(params.values["NrdrHandcraftedLateralTune"]) is bool
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False
  assert type(params.values["NrdrInterpolatedTorquePifBlend"]) is bool


def test_params_version_bool_readback_is_rejected_before_success_marker():
  old_marker = "Last applied: old profile (v15) [HONDA_CLARITY]"
  params = pending_params(
    {"ParamsVersion": 0, "NrdrCarHandcraftedInfo": old_marker},
    readback_overrides={("ParamsVersion", 1): True},
  )

  with pytest.raises(RuntimeError, match="ParamsVersion readback mismatch"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert params.values["NrdrCarHandcraftedInfo"] == old_marker
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False


def test_existing_bool_params_version_is_not_coerced_to_an_integer():
  params = pending_params({"ParamsVersion": True})

  with pytest.raises(RuntimeError, match="invalid ParamsVersion type: bool"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert params.values["ParamsVersion"] is True
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False


@pytest.mark.parametrize(("failure_index", "expected_version"), ((48, 5), (49, 6)))
def test_version_or_marker_failure_preserves_prior_success_marker(failure_index, expected_version):
  old_marker = "Last applied: old profile (v15) [HONDA_CLARITY]"
  params = pending_params({"NrdrCarHandcraftedInfo": old_marker}, fail_on_call=failure_index)

  with pytest.raises(OSError, match="injected interruption"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)

  assert params.values["NrdrCarHandcraftedInfo"] == old_marker
  assert params.values["ParamsVersion"] == expected_version
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False


def test_readback_mismatch_retains_request_and_does_not_publish_success():
  old_marker = "Last applied: old profile (v15) [HONDA_CLARITY]"
  params = pending_params(
    {"NrdrCarHandcraftedInfo": old_marker},
    corrupt_reads={"HondaCenterScale": 9.9},
  )
  with pytest.raises(RuntimeError, match="HondaCenterScale"):
    consume_handcrafted_lateral_request(clarity_cp(), clarity_cp_sp(), params)
  assert params.values["NrdrHandcraftedLateralTune"] is True
  assert params.values["NrdrInterpolatedTorquePifBlend"] is False
  assert params.values["NrdrCarHandcraftedInfo"] == old_marker
  assert params.values["ParamsVersion"] == 5


def test_post_apply_manual_edits_are_reported_customized_and_never_restored():
  params = pending_params()
  CP, CP_SP = clarity_cp(), clarity_cp_sp()
  consume_handcrafted_lateral_request(CP, CP_SP, params)
  assert handcrafted_lateral_profile_status(CP, CP_SP, params).endswith("exact match")

  params.values["HondaCenterScale"] = 1.23
  params.calls.clear()
  assert handcrafted_lateral_profile_status(CP, CP_SP, params).endswith("customized")
  assert consume_handcrafted_lateral_request(CP, CP_SP, params) == []
  assert params.values["HondaCenterScale"] == 1.23
  assert params.calls == []


def test_pending_or_unavailable_status_preserves_any_prior_success_marker():
  old_marker = "Last applied: old profile (v15) [HONDA_CLARITY]"
  params = pending_params({"NrdrCarHandcraftedInfo": old_marker})
  assert handcrafted_lateral_profile_status(clarity_cp(), clarity_cp_sp(), params).startswith(old_marker)
  assert handcrafted_lateral_profile_status(clarity_cp(firmware=False), clarity_cp_sp(), params).startswith(old_marker)


def test_v16_success_marker_is_preserved_until_v17_is_applied():
  old_marker = "Last applied: Honda Clarity Current Lateral 2026-08-28 (v16) [HONDA_CLARITY]"
  params = pending_params({
    "NrdrHandcraftedLateralTune": False,
    "NrdrCarHandcraftedInfo": old_marker,
  })

  assert handcrafted_lateral_profile_status(clarity_cp(), clarity_cp_sp(), params) == \
    f"{old_marker} | current profile v17 not applied"


def test_native_apply_callback_is_a_durable_blocking_command():
  source = Path(__file__).parents[1] / "ui" / "settings" / "lateral_tuning.py"
  text = source.read_text(encoding="utf-8")
  assert 'tr("Apply Handcrafted Lateral Profile")' in text
  assert 'put_bool("NrdrHandcraftedLateralTune", True, block=True)' in text
  assert 'self._handcrafted_tune.set_visible(False)' in text
  assert "get_selected_car_identity(ui_state.params)" in text
  assert "selection_present=selection_present" in text
  assert 'put_bool("NrdrHandcraftedLateralTune", False' not in text


def test_reporter_card_and_settings_have_no_persistent_restore_or_lock_path():
  root = Path(__file__).parents[2]
  reporter_path = root / "nrdr" / "features" / "services" / "car_tune_report.py"
  tree = ast.parse(reporter_path.read_text(encoding="utf-8"))
  build = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "_build")
  build_calls = {node.func.id for node in ast.walk(build) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
  assert "consume_handcrafted_lateral_request" not in build_calls
  consume = next(node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef) and node.name == "consume_handcrafted_request")
  assert any(
    isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get_bool" and
    len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and node.args[0].value == "IsOffroad"
    for node in ast.walk(consume)
  )

  card = (root / "selfdrive" / "car" / "card.py").read_text(encoding="utf-8")
  assert "restore_handcrafted_lateral_profile" not in card
  assert "consume_handcrafted_lateral_request(self.CP, self.CP_SP, self.params, startup=True)" in card
  assert "handcrafted lateral apply failed; request retained" in card
  card_tree = ast.parse(card)
  startup_try = next(
    node for node in ast.walk(card_tree)
    if isinstance(node, ast.Try) and any(
      isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and
      call.func.id == "consume_handcrafted_lateral_request"
      for statement in node.body for call in ast.walk(statement)
    )
  )
  assert isinstance(startup_try.handlers[0].type, ast.Name)
  assert startup_try.handlers[0].type.id == "HandcraftedLateralUnsafeStateError"
  assert any(isinstance(node, ast.Raise) for node in ast.walk(startup_try.handlers[0]))
  assert isinstance(startup_try.handlers[1].type, ast.Name)
  assert startup_try.handlers[1].type.id == "Exception"

  for relative in (
    "nrdr/ui/settings/vehicle_model_learning.py",
    "nrdr/ui/settings/pidf_ground.py",
    "nrdr/ui/settings/override_tuning.py",
    "nrdr/ui/settings/steer_filters.py",
    "selfdrive/ui/sunnypilot/layouts/settings/models.py",
  ):
    source = (root / relative).read_text(encoding="utf-8")
    assert "NrdrHandcraftedLateralTune" not in source


def test_native_ui_fail_closed_hides_honda_only_groups_and_special_page():
  root = Path(__file__).parents[2]
  lateral = (root / "nrdr" / "ui" / "settings" / "lateral_tuning.py").read_text(encoding="utf-8")
  layout = (root / "nrdr" / "ui" / "settings" / "layout.py").read_text(encoding="utf-8")

  assert "get_selected_car_identity(ui_state.params)" in lateral
  assert "selection_present=selection_present" in lateral
  assert 'identity is not None and identity[1] == "honda"' in lateral
  assert "HONDA_ONLY_LATERAL_PANELS" in lateral
  for panel in ("PIDF", "STEER_RATIO", "OVERRIDE", "STEER_FILTERS"):
    assert f"LateralPanel.{panel}" in lateral
  assert "for item in self._honda_only_items:" in lateral
  assert "if self._current_panel in HONDA_ONLY_LATERAL_PANELS and not honda_available:" in lateral
  lateral_tree = ast.parse(lateral)
  honda_items = next(
    node for node in ast.walk(lateral_tree)
    if isinstance(node, ast.Assign) and any(
      isinstance(target, ast.Attribute) and target.attr == "_honda_only_items"
      for target in node.targets
    )
  )
  honda_buttons = {
    node.attr for node in honda_items.value.elts
    if isinstance(node, ast.Attribute)
  }
  assert honda_buttons == {"_pidf_button", "_override_button", "_steer_filters_button"}
  assert "_vehicle_model_button" not in honda_buttons
  assert "self._honda_only_items = (self._party_tricks_separator, self._party_tricks_button)" in layout
  assert layout.count("for item in self._honda_only_items:") == 2
  assert "panel == PanelType.PARTY_TRICKS and not honda_tuning_available()" in layout
