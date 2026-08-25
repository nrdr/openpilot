import pytest

from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  CLARITY_ROAD_TESTED_2026_08_21,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  is_handcrafted_lateral_enabled,
)
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import get_steer_ratio_endpoint_profile


EXPECTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

EXPECTED_GEOMETRY = (
  ("HONDA_ACCORD", "NrdrSteerRatioCenterAccord", 18.31, "NrdrSteerRatioOuterAccord", 11.82, 2.30 * 250.0 / 2.41),
  ("HONDA_CIVIC", "NrdrSteerRatioCenterCivic", 17.24, "NrdrSteerRatioOuterCivic", 10.93, 2.22 * 250.0 / 2.41),
  ("HONDA_CIVIC_BOSCH", "NrdrSteerRatioCenterCivic", 17.24, "NrdrSteerRatioOuterCivic", 10.93, 2.22 * 250.0 / 2.41),
  ("HONDA_CIVIC_BOSCH_DIESEL", "NrdrSteerRatioCenterCivic", 17.24, "NrdrSteerRatioOuterCivic", 10.93, 2.22 * 250.0 / 2.41),
  ("HONDA_CLARITY", "NrdrSteerRatioCenterClarity", 18.50, "NrdrSteerRatioOuterClarity", 12.72, 250.0),
  ("HONDA_CRV_5G", "NrdrSteerRatioCenterCrv5g", 17.94, "NrdrSteerRatioOuterCrv5g", 12.30, 2.30 * 250.0 / 2.41),
  ("HONDA_INSIGHT", "NrdrSteerRatioCenterInsight", 16.82, "NrdrSteerRatioOuterInsight", 12.58, 2.54 * 250.0 / 2.41),
)

EXPECTED_C4_SHARED_VALUES = {
  "NrdrStarPilotPid": False,
  "NrdrLegacyDualBpSteerRatio": False,
  "NrdrLaneChangeEndpointSteerRatio": True,
  "NrdrLearnSteerRatio": False,
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
  "NrdrLatRateDampingFadeSpeed": 30,
  "HondaCenterScale": 1.0,
  "HondaCenterBoostThreshold": 3.0,
  "HondaCenterBoostMinSpeed": 50,
  "NrdrLatStiction": True,
  "NrdrNnlcEnabled": False,
  "NrdrTuneLearner": False,
  "NrdrTuneLearnerStrength": 0,
  "NrdrTuneLearnerRate": 10,
  "NrdrIncreaseOverrideTolerance": False,
  "NrdrDriverOverrideThreshold": 2000,
  "NrdrOverrideThresholdCenterBoost": 1200,
  "HondaDriverAssistDuringOverride": False,
  "HondaOverrideFadeDownSecs": 0.0,
  "HondaOverrideFadeUpSecs": 1.0,
  "HondaOverrideTorqueScale": 0,
  "HondaTorqueLowPassFilter": True,
  "HondaLpfTauLowSpeed": 0.1,
  "HondaLpfTauStandard": 0.1,
  "HondaLpfTauHighway": 0.05,
  "HondaSteerDeltaLimiter": False,
  "HondaSteerDeltaUp": 4.0,
  "HondaSteerDeltaDown": 4.0,
  "LagdToggle": False,
  "LagdToggleDelay": 0.5,
}


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    return self.values.get(key)

  def put_bool(self, key, value, block=False):
    self.values[key] = bool(value)

  def put(self, key, value, block=False):
    self.values[key] = value


def test_torque_mod_profiles_are_versioned_and_fingerprint_scoped():
  assert HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS == EXPECTED_FINGERPRINTS
  assert tuple(HANDCRAFTED_LATERAL_PROFILES) == EXPECTED_FINGERPRINTS
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    profile = get_handcrafted_lateral_profile(fingerprint)
    assert profile is HANDCRAFTED_LATERAL_PROFILES[fingerprint]
    assert profile.fingerprint == fingerprint
    assert profile.version == 13
    assert "2026-08-21" in profile.name
  assert get_handcrafted_lateral_profile("HONDA_CIVIC_2022") is None
  assert get_handcrafted_lateral_profile("HONDA_CRV_HYBRID") is None


@pytest.mark.parametrize(
  ("fingerprint", "center_param", "center", "outer_param", "outer", "outer_angle"),
  EXPECTED_GEOMETRY,
)
def test_profile_keeps_each_cars_mechanical_steer_ratio_geometry(
  fingerprint, center_param, center, outer_param, outer, outer_angle,
):
  profile = get_handcrafted_lateral_profile(fingerprint)
  steer_ratio = get_steer_ratio_endpoint_profile(fingerprint)
  values = dict(profile.values)

  assert steer_ratio.center_param == center_param
  assert steer_ratio.outer_param == outer_param
  assert steer_ratio.center_default == center
  assert steer_ratio.outer_default == outer
  assert steer_ratio.outer_angle == pytest.approx(outer_angle)
  assert values[center_param] == center
  assert values[outer_param] == outer

  endpoint_keys = {
    endpoint_key
    for configured in EXPECTED_GEOMETRY
    for endpoint_key in (configured[1], configured[3])
  }
  assert set(values) & endpoint_keys == {center_param, outer_param}


def test_all_profiles_share_the_exact_winning_c4_live_tune():
  for fingerprint in EXPECTED_FINGERPRINTS:
    profile = get_handcrafted_lateral_profile(fingerprint)
    steer_ratio = get_steer_ratio_endpoint_profile(fingerprint)
    values = dict(profile.values)
    values.pop(steer_ratio.center_param)
    values.pop(steer_ratio.outer_param)

    assert values == EXPECTED_C4_SHARED_VALUES
    assert "HondaStoppingDecelRate" not in values
    assert {key for key in values if key.startswith("NrdrNnlc")} == {"NrdrNnlcEnabled"}
    assert len(profile.values) == len(dict(profile.values)), "profile contains duplicate Param keys"


def test_profile_restores_complete_torque_mod_snapshot():
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    params = FakeParams({"NrdrHandcraftedLateralTune": True})
    changed = apply_handcrafted_lateral_profile(fingerprint, params)

    expected = dict(HANDCRAFTED_LATERAL_PROFILES[fingerprint].values)
    assert changed == list(expected)
    assert all(params.values[key] == value for key, value in expected.items())
    assert apply_handcrafted_lateral_profile(fingerprint, params) == []


def test_v11_profile_state_migrates_once_then_is_idempotent():
  profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
  old_values = dict(profile.values)
  old_values.update({
    "NrdrLegacyDualBpSteerRatio": True,
    "HondaCenterScale": 0.5,
    "NrdrLatStiction": False,
    "NrdrDriverOverrideThreshold": 1400,
    "NrdrOverrideThresholdCenterBoost": 1000,
    "HondaOverrideFadeDownSecs": 0.1,
    "HondaOverrideFadeUpSecs": 0.1,
  })
  params = FakeParams({"NrdrHandcraftedLateralTune": True, **old_values})

  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", params) == [
    "NrdrLegacyDualBpSteerRatio",
    "HondaCenterScale",
    "NrdrLatStiction",
    "NrdrDriverOverrideThreshold",
    "NrdrOverrideThresholdCenterBoost",
    "HondaOverrideFadeDownSecs",
    "HondaOverrideFadeUpSecs",
  ]
  assert all(params.values[key] == value for key, value in profile.values)
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", params) == []


def test_v12_profile_state_updates_highway_lpf_once_then_is_idempotent():
  profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
  old_values = dict(profile.values)
  old_values["HondaLpfTauHighway"] = 0.01
  params = FakeParams({"NrdrHandcraftedLateralTune": True, **old_values})

  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", params) == ["HondaLpfTauHighway"]
  assert params.values["HondaLpfTauHighway"] == 0.05
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", params) == []


def test_profile_can_be_disabled_and_never_affects_other_fingerprints():
  disabled = FakeParams({
    "NrdrHandcraftedLateralTune": False,
    "LatPScaleLowSpeed": 42,
    "NrdrLegacyDualBpSteerRatio": True,
    "NrdrLatStiction": False,
    "NrdrNnlcEnabled": True,
  })
  assert not is_handcrafted_lateral_enabled("HONDA_CLARITY", disabled)
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", disabled) == []
  assert disabled.values["LatPScaleLowSpeed"] == 42
  assert disabled.values["NrdrLegacyDualBpSteerRatio"] is True
  assert disabled.values["NrdrLatStiction"] is False
  assert disabled.values["NrdrNnlcEnabled"] is True

  disabled.values["NrdrHandcraftedLateralTune"] = True
  assert is_handcrafted_lateral_enabled("HONDA_CLARITY", disabled)
  apply_handcrafted_lateral_profile("HONDA_CLARITY", disabled)
  assert disabled.values["LatPScaleLowSpeed"] == 100
  assert disabled.values["NrdrLegacyDualBpSteerRatio"] is False
  assert disabled.values["NrdrLatStiction"] is True
  assert disabled.values["NrdrNnlcEnabled"] is False

  for fingerprint in ("HONDA_CIVIC_2022", "HONDA_CRV_HYBRID"):
    unsupported = FakeParams({"NrdrHandcraftedLateralTune": True, "LatPScaleLowSpeed": 42})
    assert not is_handcrafted_lateral_enabled(fingerprint, unsupported)
    assert apply_handcrafted_lateral_profile(fingerprint, unsupported) == []
    assert unsupported.values["LatPScaleLowSpeed"] == 42


def test_profile_preserves_the_current_road_tested_choices():
  values = dict(CLARITY_ROAD_TESTED_2026_08_21.values)
  clarity_sr = get_steer_ratio_endpoint_profile("HONDA_CLARITY")
  assert values[clarity_sr.center_param] == 18.50
  assert values[clarity_sr.outer_param] == 12.72
  assert values["NrdrLegacyDualBpSteerRatio"] is False
  assert values["NrdrLaneChangeEndpointSteerRatio"] is True
  assert "NrdrSteerRatioOffset" not in values
  assert values["HondaCenterScale"] == 1.0
  assert values["HondaCenterBoostThreshold"] == 3.0
  assert values["HondaCenterBoostMinSpeed"] == 50
  assert values["NrdrLatStiction"] is True
  assert values["HondaLpfTauHighway"] == 0.05
  assert values["NrdrNnlcEnabled"] is False
  assert not any(key.startswith("NrdrNnlc") and key != "NrdrNnlcEnabled" for key in values)
  assert values["HondaTorqueLowPassFilter"] is True
  assert values["HondaLpfTauLowSpeed"] == values["HondaLpfTauStandard"] == 0.1
  assert "HondaPidFriction" not in values
  assert values["NrdrDriverOverrideThreshold"] == 2000
  assert values["NrdrOverrideThresholdCenterBoost"] == 1200
  assert values["HondaOverrideFadeDownSecs"] == 0.0
  assert values["HondaOverrideFadeUpSecs"] == 1.0
  assert values["HondaOverrideTorqueScale"] == 0
  assert values["HondaSteerDeltaUp"] == values["HondaSteerDeltaDown"] == 4.0
  assert "HondaStoppingDecelRate" not in values
  assert values["LagdToggle"] is False
  assert values["LagdToggleDelay"] == 0.5

  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    sr_profile = get_steer_ratio_endpoint_profile(fingerprint)
    profile_values = dict(HANDCRAFTED_LATERAL_PROFILES[fingerprint].values)
    assert profile_values[sr_profile.center_param] == sr_profile.center_default
    assert profile_values[sr_profile.outer_param] == sr_profile.outer_default
