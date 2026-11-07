from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

PARAMS_DIR = Path(__file__).resolve().parents[1] / "params"
sys.path.insert(0, str(PARAMS_DIR))

from generate import CPP_INCLUDE, generated_targets, repository_errors, write_generated
from specs import (
  ADDED_PARAM_SPECS,
  OVERRIDDEN_PARAM_SPECS,
  PARAM_SPECS,
  PARAM_SPECS_BY_KEY,
  ParamFlag,
  ParamLifecycle,
  ParamOwner,
  ParamType,
  RegistryAction,
  validate_catalog,
)


REGISTRY_METADATA_SHA256 = "c4433c55bdfe7c6216a6db1f14d5f447d8645d981ef098f8d834c366dec9efd2"


class TestParamCatalog(unittest.TestCase):
  def test_catalog_is_complete_and_unique(self) -> None:
    self.assertEqual(validate_catalog(), ())
    self.assertEqual(len(PARAM_SPECS), 160)
    self.assertEqual(len(ADDED_PARAM_SPECS), 159)
    self.assertEqual(len(OVERRIDDEN_PARAM_SPECS), 1)
    self.assertEqual(len(PARAM_SPECS_BY_KEY), len(PARAM_SPECS))
    from openpilot.nrdr.params.generated import ALL_KEYS, ADDED_KEYS, OVERRIDDEN_KEYS
    self.assertEqual(set(ALL_KEYS), set(PARAM_SPECS_BY_KEY))
    self.assertEqual(set(ADDED_KEYS), {spec.key for spec in ADDED_PARAM_SPECS})
    self.assertEqual(set(OVERRIDDEN_KEYS), {spec.key for spec in OVERRIDDEN_PARAM_SPECS})
    self.assertFalse({"NrdrExperimentalEngineBraking", "NrdrCruiseOverspeedAllowance"} & set(ALL_KEYS))

    # Adding the optional deadzone must not change any existing registry/default.
    metadata = "\n".join(f"{spec.action.value}|{spec.key}|{spec.cpp_attributes}" for spec in PARAM_SPECS
                         if spec.key != "NrdrMvlPcmDeadzone") + "\n"
    self.assertEqual(sha256(metadata.encode()).hexdigest(), REGISTRY_METADATA_SHA256)
    receipt = PARAM_SPECS_BY_KEY["NrdrRdxRouteAConfirmation"]
    self.assertEqual(receipt.flags, (ParamFlag.PERSISTENT, ParamFlag.DONT_LOG))
    self.assertIsNone(receipt.default)
    self.assertIs(receipt.lifecycle, ParamLifecycle.STATE)

  def test_device_yaw_switch_defaults_on_without_reviving_retired_sliders(self) -> None:
    spec = PARAM_SPECS_BY_KEY["NrdrDeviceYawCorrection"]
    self.assertIs(spec.param_type, ParamType.BOOL)
    self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
    self.assertEqual(spec.default, "1")
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertIs(PARAM_SPECS_BY_KEY["NrdrInterpolatedTorquePifBlend"].lifecycle, ParamLifecycle.TOMBSTONE)

  def test_pcm_mode_defaults_off_and_wind_on_without_migrating_legacy_bool(self) -> None:
    for key, kind, default in (("NrdrHondaPcmMode", ParamType.INT, "0"), ("NrdrHondaWindBrake", ParamType.BOOL, "1"),
                               ("NrdrMvlPcmDeadzone", ParamType.INT, "0")):
      spec = PARAM_SPECS_BY_KEY[key]
      self.assertEqual((spec.param_type, spec.default), (kind, default))
      self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
      self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
      self.assertIs(spec.owner, ParamOwner.HONDA)
    self.assertIs(PARAM_SPECS_BY_KEY["NrdrHondaEcuMatchedLong"].lifecycle, ParamLifecycle.TOMBSTONE)

  def test_handcrafted_request_context_is_typed_and_not_restored_from_backups(self) -> None:
    spec = PARAM_SPECS_BY_KEY["NrdrHandcraftedLateralRequest"]
    self.assertIs(spec.param_type, ParamType.JSON)
    self.assertIs(spec.lifecycle, ParamLifecycle.COMMAND)
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT,))
    self.assertIsNone(spec.default)

  def test_personality_accel_profile_param_is_a_persistent_ignored_tombstone(self) -> None:
    spec = PARAM_SPECS_BY_KEY["NrdrPersonalityAccelProfiles"]
    self.assertIs(spec.param_type, ParamType.BOOL)
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertEqual(spec.default, "0")
    self.assertIs(spec.lifecycle, ParamLifecycle.TOMBSTONE)
    self.assertIs(spec.owner, ParamOwner.LONGITUDINAL)

  def test_lane_centering_min_speed_is_canonical_mph_setting(self) -> None:
    spec = PARAM_SPECS_BY_KEY["LaneCenteringMinSpeed"]
    self.assertIs(spec.param_type, ParamType.INT)
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertEqual(spec.default, "12")
    self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
    self.assertIs(spec.owner, ParamOwner.LATERAL)

  def test_lane_guidance_defaults_to_sunny_for_unset_params(self) -> None:
    spec = PARAM_SPECS_BY_KEY["LaneGuidanceMode"]
    self.assertIs(spec.param_type, ParamType.INT)
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertEqual(spec.default, "2")
    self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
    self.assertIs(spec.owner, ParamOwner.LATERAL)

  def test_lane_centering_strength_uses_suggested_default(self) -> None:
    spec = PARAM_SPECS_BY_KEY["LaneCenteringStrength"]
    self.assertIs(spec.param_type, ParamType.FLOAT)
    self.assertEqual(spec.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertEqual(spec.default, "0.95")
    self.assertIs(spec.lifecycle, ParamLifecycle.SETTING)
    self.assertIs(spec.owner, ParamOwner.LATERAL)

  def test_existing_key_override_is_not_generated_as_an_addition(self) -> None:
    override = OVERRIDDEN_PARAM_SPECS[0]
    self.assertEqual(override.key, "DisablePowerDown")
    self.assertIs(override.action, RegistryAction.OVERRIDE)
    self.assertEqual(override.cpp_attributes, 'PERSISTENT | BACKUP, BOOL, "1"')
    self.assertNotIn(override, ADDED_PARAM_SPECS)

  def test_sensitive_and_retired_metadata_is_explicit(self) -> None:
    self.assertIn(ParamFlag.DONT_LOG, PARAM_SPECS_BY_KEY["RemoteAccessPinSalt"].flags)
    self.assertIn(ParamFlag.DONT_LOG, PARAM_SPECS_BY_KEY["RemoteAccessPinHash"].flags)
    self.assertIn(ParamFlag.DONT_LOG, PARAM_SPECS_BY_KEY["NrdrTuneLearnerMap"].flags)

    tombstones = {spec.key for spec in PARAM_SPECS if spec.lifecycle is ParamLifecycle.TOMBSTONE}
    self.assertEqual(tombstones, {
      "NrdrHondaEcuMatchedLong",
      "NrdrYawDelaySchedule",
      "NrdrInterpolatedTorquePifBlend", "NrdrInterpolatedTorqueShare", "NrdrInterpolatedTorqueLatAccelFactor",
      "NrdrInterpolatedTorqueFriction", "NrdrInterpolatedTorqueFrictionStandard", "NrdrInterpolatedTorqueFrictionHighway",
      "NrdrLaneChangeMinTime", "NrdrLaneChangeEntrySrReduction", "NrdrLaneChangeEntryReturnTime",
      "NrdrLaneChangeTorqueFactor", "NrdrLaneChangeFrictionPercent", "NrdrIncreaseOverrideTolerance",
      "NrdrStarPilotPid", "NrdrNnlcEnabled", "NrdrNnlcActivationSpeed", "NrdrNnlcKpGain", "NrdrNnlcKfGain",
      "NrdrNnlcKiGain", "NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed",
      "HondaCivicRadarTryout",
      "HondaNotchEnabled",
      "HondaNotchFreq",
      "HondaNotchQ",
      "HondaPidFriction",
        "HondaPidTuneScale",
        "NrdrLaneChangeEndpointSteerRatio",
        "NrdrLearnSteerRatio",
        "NrdrLegacyDualBpSteerRatio",
        "NrdrPersonalityAccelProfiles",
        "NrdrSteerRatioCenterAccord",
        "NrdrSteerRatioCenterCivic",
        "NrdrSteerRatioCenterClarity",
        "NrdrSteerRatioCenterCrv5g",
        "NrdrSteerRatioCenterInsight",
        "NrdrSteerRatioMax",
        "NrdrSteerRatioMin",
        "NrdrSteerRatioOffset",
        "NrdrSteerRatioOuterAccord",
        "NrdrSteerRatioOuterCivic",
        "NrdrSteerRatioOuterClarity",
        "NrdrSteerRatioOuterCrv5g",
        "NrdrSteerRatioOuterInsight",
      })

  def test_committed_generated_files_and_header_are_current(self) -> None:
    self.assertEqual(repository_errors(), ())
    result = subprocess.run(
      [sys.executable, str(PARAMS_DIR / "generate.py"), "--check"],
      check=False,
      capture_output=True,
      text=True,
    )
    self.assertEqual(result.returncode, 0, result.stderr)

  def test_repository_check_detects_stale_output_and_header_drift(self) -> None:
    with TemporaryDirectory() as temporary_directory:
      root = Path(temporary_directory)
      header_path = root / "openpilot" / "common" / "params_keys.h"
      header_path.parent.mkdir(parents=True)
      header_path.write_text("\n".join((
        "inline static int keys[] = {",
        '  {"DisablePowerDown", {PERSISTENT | BACKUP, BOOL, "1"}},',
        CPP_INCLUDE,
        "};",
        "",
      )), encoding="utf-8")
      write_generated(root)
      self.assertEqual(repository_errors(root), ())

      keys_path = next(path for path in generated_targets(root) if path.name == "keys.py")
      keys_path.write_text(keys_path.read_text(encoding="utf-8") + "# stale\n", encoding="utf-8")
      self.assertTrue(any("stale generated file" in error for error in repository_errors(root)))

      write_generated(root)
      header_path.write_text(
        header_path.read_text(encoding="utf-8").replace(
          'PERSISTENT | BACKUP, BOOL, "1"',
          "PERSISTENT | BACKUP, BOOL",
        ),
        encoding="utf-8",
      )
      self.assertTrue(any("DisablePowerDown: registry metadata mismatch" in error
                          for error in repository_errors(root)))

  def test_repository_check_rejects_duplicate_direct_generated_key(self) -> None:
    with TemporaryDirectory() as temporary_directory:
      root = Path(temporary_directory)
      header_path = root / "openpilot" / "common" / "params_keys.h"
      header_path.parent.mkdir(parents=True)
      header_path.write_text("\n".join((
        "inline static int keys[] = {",
        '  {"DisablePowerDown", {PERSISTENT | BACKUP, BOOL, "1"}},',
        '  {"HondaBoschARadar", {PERSISTENT, BOOL, "1"}},',
        CPP_INCLUDE,
        "};",
        "",
      )), encoding="utf-8")
      write_generated(root)
      self.assertTrue(any("HondaBoschARadar: generated key must not also be declared directly" in error
                          for error in repository_errors(root)))


if __name__ == "__main__":
  unittest.main()
