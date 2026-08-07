from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  CLARITY_ROAD_TESTED_2026_08_07,
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


def test_clarity_profile_is_versioned_and_fingerprint_scoped():
  profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
  assert profile is CLARITY_ROAD_TESTED_2026_08_07
  assert profile.version == 2
  assert "2026-08-07" in profile.name
  assert get_handcrafted_lateral_profile("HONDA_CIVIC") is None


def test_profile_restores_complete_clarity_snapshot():
  params = FakeParams({"NrdrHandcraftedLateralTune": True})
  changed = apply_handcrafted_lateral_profile("HONDA_CLARITY", params)

  expected = dict(CLARITY_ROAD_TESTED_2026_08_07.values)
  assert changed == list(expected)
  assert all(params.values[key] == value for key, value in expected.items())
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", params) == []


def test_profile_can_be_disabled_and_never_affects_other_fingerprints():
  disabled = FakeParams({"NrdrHandcraftedLateralTune": False, "LatPScaleLowSpeed": 42})
  assert not is_handcrafted_lateral_enabled("HONDA_CLARITY", disabled)
  assert apply_handcrafted_lateral_profile("HONDA_CLARITY", disabled) == []
  assert disabled.values["LatPScaleLowSpeed"] == 42

  unsupported = FakeParams({"NrdrHandcraftedLateralTune": True, "LatPScaleLowSpeed": 42})
  assert not is_handcrafted_lateral_enabled("HONDA_CIVIC", unsupported)
  assert apply_handcrafted_lateral_profile("HONDA_CIVIC", unsupported) == []
  assert unsupported.values["LatPScaleLowSpeed"] == 42


def test_profile_preserves_the_current_road_tested_clarity_choices():
  values = dict(CLARITY_ROAD_TESTED_2026_08_07.values)
  assert values["NrdrSteerRatioOffset"] == -1.0
  assert values["HondaCenterScale"] == 0.0
  assert values["NrdrLatStiction"] is False
  assert values["HondaLpfTauHighway"] == 0.01
  assert values["NrdrNnlcEnabled"] is False
  assert values["HondaTorqueLowPassFilter"] is True
  assert values["HondaLpfTauLowSpeed"] == values["HondaLpfTauStandard"] == 0.1
  assert values["LagdToggle"] is False
  assert values["LagdToggleDelay"] == 0.5
