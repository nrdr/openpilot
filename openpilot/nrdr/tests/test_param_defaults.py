from importlib import util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock


DEFAULTS_PATH = Path(__file__).resolve().parents[1] / "params" / "defaults.py"
LEGACY_PATH = Path(__file__).resolve().parents[2] / "sunnypilot" / "nrdr" / "manager.py"

EXPECTED_BOOL_DEFAULTS = {
  "QuietMode": True,
  "GsmMetered": False,
  "ExperimentalMode": True,
  "RecordFront": True,
  "RecordAudio": True,
  "LaneTurnDesire": True,
  "DynamicExperimentalControl": True,
  "SmartCruiseControlVision": True,
  "CustomAccIncrementsEnabled": True,
  "MadsMainCruiseAllowed": False,
  "HondaTorqueLowPassFilter": True,
  "NrdrNnlcEnabled": False,
  "RocketFuel": True,
  "BlindSpot": True,
  "TorqueBar": True,
  "RainbowMode": False,
  "StandstillTimer": True,
  "RoadNameToggle": True,
  "GreenLightAlert": True,
  "LeadDepartAlert": True,
  "TrueVEgoUI": False,
  "HideVEgoUI": False,
  "ShowTurnSignals": True,
  "SshEnabled": True,
  "ShowAdvancedControls": True,
  "LagdToggle": True,
  "EnableCopyparty": True,
}

EXPECTED_VALUE_DEFAULTS = {
  "LaneTurnValue": 20.0,
  "AutoLaneChangeTimer": 1,
  "NrdrNnlcActivationSpeed": 30,
  "NrdrNnlcKpGain": 100,
  "NrdrNnlcKfGain": 50,
  "NrdrNnlcKiGain": 10,
  "LongitudinalPersonality": 3,
  "SpeedLimitMode": 3,
  "SpeedLimitOffsetType": 1,
  "SpeedLimitValueOffset": 5,
  "CustomAccShortPressIncrement": 5,
  "CustomAccLongPressIncrement": 1,
  "NrdrDriverOverrideThreshold": 1400,
  "NrdrOverrideThresholdCenterBoost": 1000,
  "HondaOverrideFadeDownSecs": 0.1,
  "HondaOverrideFadeUpSecs": 0.1,
  "ChevronInfo": 4,
  "DevUIInfo": 3,
  "OnroadScreenOffBrightness": 1,
  "InteractivityTimeout": 120,
}

VERSION_VALUES = {
  "terms_version": "terms-test",
  "terms_version_sp": "terms-sp-test",
  "training_version": "training-test",
  "sunnylink_consent_version": "sunnylink-test",
}


class FakeCloudlog:
  def __init__(self):
    self.exceptions = []

  def exception(self, message, *args):
    self.exceptions.append((message, args))


class FakeParams:
  def __init__(self, values=None, *, get_errors=(), put_errors=()):
    self.values = dict(values or {})
    self.get_errors = set(get_errors)
    self.put_errors = set(put_errors)
    self.calls = []

  def get(self, key):
    if key in self.get_errors:
      raise RuntimeError(f"get failed: {key}")
    return self.values.get(key)

  def put(self, key, value, *args, **kwargs):
    self._write("put", key, value, args, kwargs)

  def put_bool(self, key, value, *args, **kwargs):
    self._write("put_bool", key, bool(value), args, kwargs)

  def _write(self, setter, key, value, args, kwargs):
    self.calls.append((setter, key, value, args, kwargs))
    if key in self.put_errors:
      raise RuntimeError(f"put failed: {key}")
    self.values[key] = value


def _module(name, **attributes):
  module = ModuleType(name)
  for key, value in attributes.items():
    setattr(module, key, value)
  return module


def _load_defaults():
  cloudlog = FakeCloudlog()
  stubs = {
    "openpilot.common.params": _module("openpilot.common.params", Params=object),
    "openpilot.common.swaglog": _module("openpilot.common.swaglog", cloudlog=cloudlog),
    "openpilot.common.hardware": _module(
      "openpilot.common.hardware",
      HARDWARE=SimpleNamespace(get_device_type=lambda: "pc"),
    ),
  }
  spec = util.spec_from_file_location("_nrdr_param_defaults_under_test", DEFAULTS_PATH)
  module = util.module_from_spec(spec)
  with mock.patch.dict(sys.modules, stubs):
    spec.loader.exec_module(module)
  return module, cloudlog


def _apply(module, params):
  version = _module("openpilot.common.version", **VERSION_VALUES)
  with mock.patch.dict(sys.modules, {"openpilot.common.version": version}):
    module.apply_defaults(params)


class TestParamDefaults(unittest.TestCase):
  def setUp(self):
    self.defaults, self.cloudlog = _load_defaults()

  def test_default_catalog_is_an_exact_compatibility_snapshot(self):
    self.assertEqual(self.defaults.BOOL_DEFAULTS, EXPECTED_BOOL_DEFAULTS)
    self.assertEqual(self.defaults.VALUE_DEFAULTS, EXPECTED_VALUE_DEFAULTS)

  def test_missing_values_are_seeded_in_order_and_existing_values_are_preserved(self):
    existing = {
      "QuietMode": False,
      "LaneTurnValue": 99.0,
      "EnforceTorqueControl": True,
      "NeuralNetworkLateralControl": True,
      "HasAcceptedTerms": "old-terms",
      "HasAcceptedTermsSP": "old-sp-terms",
      "CompletedTrainingVersion": "old-training",
      "CompletedSunnylinkConsentVersion": "old-consent",
      "SunnylinkEnabled": False,
    }
    params = FakeParams(existing)

    _apply(self.defaults, params)

    self.assertIs(params.values["QuietMode"], False)
    self.assertEqual(params.values["LaneTurnValue"], 99.0)
    for key, value in EXPECTED_BOOL_DEFAULTS.items():
      if key != "QuietMode":
        self.assertEqual(params.values[key], value)
    for key, value in EXPECTED_VALUE_DEFAULTS.items():
      if key != "LaneTurnValue":
        self.assertEqual(params.values[key], value)
    self.assertEqual(params.values["NrdrSteerRatioMode"], 0)
    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 15.38)
    self.assertEqual(params.values["NrdrSteerRatioManualFinal"], 10.93)

    forced = {
      "EnforceTorqueControl": False,
      "NeuralNetworkLateralControl": False,
      "HasAcceptedTerms": VERSION_VALUES["terms_version"],
      "HasAcceptedTermsSP": VERSION_VALUES["terms_version_sp"],
      "CompletedTrainingVersion": VERSION_VALUES["training_version"],
      "CompletedSunnylinkConsentVersion": VERSION_VALUES["sunnylink_consent_version"],
      "SunnylinkEnabled": True,
    }
    for key, value in forced.items():
      self.assertEqual(params.values[key], value)

    expected_keys = (
      ["NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal", "NrdrSteerRatioMode"]
      + [key for key in EXPECTED_BOOL_DEFAULTS if key != "QuietMode"]
      + [key for key in EXPECTED_VALUE_DEFAULTS if key != "LaneTurnValue"]
      + list(forced)
    )
    self.assertEqual([call[1] for call in params.calls], expected_keys)
    self.assertTrue(all(call[4] == {"block": True} for call in params.calls[:3]))
    self.assertTrue(all(call[3:] == ((), {}) for call in params.calls[3:]), "ordinary startup defaults must remain nonblocking")
    bool_start = 3
    bool_end = bool_start + len(EXPECTED_BOOL_DEFAULTS) - 1
    self.assertTrue(all(call[0] == "put_bool" for call in params.calls[bool_start:bool_end]))
    value_start = bool_end
    value_end = value_start + sum(key not in existing for key in EXPECTED_VALUE_DEFAULTS)
    self.assertTrue(all(call[0] == "put" for call in params.calls[value_start:value_end]))

  def test_legacy_true_migrates_to_comma_and_current_car_endpoints(self):
    params = FakeParams({
      "CarPlatformBundle": {"platform": "HONDA_CLARITY"},
      "NrdrLearnSteerRatio": True,
      "NrdrSteerRatioCenterClarity": 19.25,
      "NrdrSteerRatioOuterClarity": 13.10,
    })

    self.defaults._migrate_steer_ratio_settings(params)

    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 19.25)
    self.assertEqual(params.values["NrdrSteerRatioManualFinal"], 13.10)
    self.assertEqual(params.values["NrdrSteerRatioMode"], 1)
    self.assertEqual([call[1] for call in params.calls], [
      "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal", "NrdrSteerRatioMode",
    ])
    self.assertTrue(all(call[4] == {"block": True} for call in params.calls))

  def test_partial_migration_retries_only_missing_values_and_writes_mode_last(self):
    params = FakeParams(
      {
        "CarPlatformBundle": {"platform": "HONDA_CIVIC"},
        "NrdrLearnSteerRatio": True,
        "NrdrSteerRatioCenterCivic": 17.24,
        "NrdrSteerRatioOuterCivic": 10.93,
      },
      put_errors={"NrdrSteerRatioManualFinal"},
    )

    self.defaults._migrate_steer_ratio_settings(params)

    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 17.24)
    self.assertNotIn("NrdrSteerRatioManualFinal", params.values)
    self.assertNotIn("NrdrSteerRatioMode", params.values)
    self.assertEqual([call[1] for call in params.calls], [
      "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal",
    ])

    params.put_errors.clear()
    params.calls.clear()
    self.defaults._migrate_steer_ratio_settings(params)

    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 17.24)
    self.assertEqual(params.values["NrdrSteerRatioManualFinal"], 10.93)
    self.assertEqual(params.values["NrdrSteerRatioMode"], 1)
    self.assertEqual([call[1] for call in params.calls], [
      "NrdrSteerRatioManualFinal", "NrdrSteerRatioMode",
    ])
    self.assertTrue(all(call[4] == {"block": True} for call in params.calls))

  def test_fresh_clarity_uses_requested_global_manual_defaults(self):
    params = FakeParams({"CarPlatformBundle": {"platform": "HONDA_CLARITY"}})

    self.defaults._migrate_steer_ratio_settings(params)

    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 15.38)
    self.assertEqual(params.values["NrdrSteerRatioManualFinal"], 10.93)
    self.assertEqual(params.values["NrdrSteerRatioMode"], 0)

  def test_existing_new_values_are_never_overwritten_by_migration(self):
    params = FakeParams({
      "NrdrSteerRatioMode": 3,
      "NrdrSteerRatioManualCenter": 16.2,
      "NrdrSteerRatioManualFinal": 11.1,
      "NrdrLearnSteerRatio": True,
    })

    self.defaults._migrate_steer_ratio_settings(params)

    self.assertEqual(params.values["NrdrSteerRatioMode"], 3)
    self.assertEqual(params.values["NrdrSteerRatioManualCenter"], 16.2)
    self.assertEqual(params.values["NrdrSteerRatioManualFinal"], 11.1)
    self.assertEqual(params.calls, [])

  def test_mici_omits_quiet_mode_seed(self):
    self.defaults.HARDWARE = SimpleNamespace(get_device_type=lambda: "mici")
    params = FakeParams()

    _apply(self.defaults, params)

    self.assertNotIn("QuietMode", params.values)
    self.assertNotIn("QuietMode", [call[1] for call in params.calls])
    self.assertEqual(params.values["GsmMetered"], False)

  def test_one_parameter_failure_does_not_stop_later_defaults(self):
    params = FakeParams(get_errors={"GsmMetered"}, put_errors={"RecordFront"})

    _apply(self.defaults, params)

    self.assertNotIn("GsmMetered", params.values)
    self.assertNotIn("RecordFront", params.values)
    self.assertIs(params.values["RecordAudio"], True)
    self.assertEqual(params.values["InteractivityTimeout"], 120)
    self.assertEqual(len(self.cloudlog.exceptions), 2)
    self.assertTrue(all(message == "failed to initialize nrdr param %s"
                        for message, _args in self.cloudlog.exceptions))

  def test_legacy_module_forwards_the_canonical_objects(self):
    spec = util.spec_from_file_location("_legacy_nrdr_manager_under_test", LEGACY_PATH)
    legacy = util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {"openpilot.nrdr.params.defaults": self.defaults}):
      spec.loader.exec_module(legacy)

    self.assertIs(legacy.BOOL_DEFAULTS, self.defaults.BOOL_DEFAULTS)
    self.assertIs(legacy.VALUE_DEFAULTS, self.defaults.VALUE_DEFAULTS)
    self.assertIs(legacy.apply_defaults, self.defaults.apply_defaults)
    self.assertEqual(legacy.__all__, ("BOOL_DEFAULTS", "VALUE_DEFAULTS", "apply_defaults"))


if __name__ == "__main__":
  unittest.main()
