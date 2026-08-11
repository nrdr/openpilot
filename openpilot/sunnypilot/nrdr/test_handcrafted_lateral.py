from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  CLARITY_ROAD_TESTED_2026_08_11,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  is_handcrafted_lateral_enabled,
)


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
  assert tuple(HANDCRAFTED_LATERAL_PROFILES) == HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    profile = get_handcrafted_lateral_profile(fingerprint)
    assert profile is HANDCRAFTED_LATERAL_PROFILES[fingerprint]
    assert profile.fingerprint == fingerprint
    assert profile.version == 4
    assert "2026-08-11" in profile.name
  assert get_handcrafted_lateral_profile("HONDA_CIVIC_2022") is None


def test_profile_restores_complete_torque_mod_snapshot():
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    params = FakeParams({"NrdrHandcraftedLateralTune": True})
    changed = apply_handcrafted_lateral_profile(fingerprint, params)

    expected = dict(HANDCRAFTED_LATERAL_PROFILES[fingerprint].values)
    assert changed == list(expected)
    assert all(params.values[key] == value for key, value in expected.items())
    assert apply_handcrafted_lateral_profile(fingerprint, params) == []


def test_profile_can_be_disabled_and_never_affects_other_fingerprints():
  disabled = FakeParams({"NrdrHandcraftedLateralTune": False, "LatPScaleLowSpeed": 42})
  assert not is_handcrafted_lateral_enabled("HONDA_CLARITY", disabled)
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", disabled) == []
  assert disabled.values["LatPScaleLowSpeed"] == 42

  unsupported = FakeParams({"NrdrHandcraftedLateralTune": True, "LatPScaleLowSpeed": 42})
  assert not is_handcrafted_lateral_enabled("HONDA_CIVIC_2022", unsupported)
  assert apply_handcrafted_lateral_profile("HONDA_CIVIC_2022", unsupported) == []
  assert unsupported.values["LatPScaleLowSpeed"] == 42


def test_profile_preserves_the_current_road_tested_choices():
  values = dict(CLARITY_ROAD_TESTED_2026_08_11.values)
  assert values["NrdrSteerRatioOffset"] == -1.0
  assert values["HondaCenterScale"] == 0.5
  assert values["HondaCenterBoostThreshold"] == 3.0
  assert values["HondaCenterBoostMinSpeed"] == 50
  assert values["HondaPidFriction"] == 0.5
  assert values["NrdrLatStiction"] is False
  assert values["HondaLpfTauHighway"] == 0.01
  assert values["NrdrNnlcEnabled"] is False
  assert values["HondaTorqueLowPassFilter"] is True
  assert values["HondaLpfTauLowSpeed"] == values["HondaLpfTauStandard"] == 0.1
  assert values["HondaUnwindLookahead"] is False
  assert values["HondaOverrideFadeUpSecs"] == 1.0
  assert values["HondaSteerDeltaUp"] == values["HondaSteerDeltaDown"] == 4.0
  assert values["HondaStoppingDecelRate"] == 30
  assert values["LagdToggle"] is False
  assert values["LagdToggleDelay"] == 0.5

  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    if fingerprint != "HONDA_CLARITY":
      assert dict(HANDCRAFTED_LATERAL_PROFILES[fingerprint].values)["NrdrSteerRatioOffset"] == 0.0
