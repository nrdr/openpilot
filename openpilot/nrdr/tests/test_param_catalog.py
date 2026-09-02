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
  RegistryAction,
  validate_catalog,
)


REGISTRY_METADATA_SHA256 = "c2e2bfa6f3e288ce1a32d5fd602262f8b0416348626e16439f8a60899162c09b"


class TestParamCatalog(unittest.TestCase):
  def test_catalog_is_complete_and_unique(self) -> None:
    self.assertEqual(validate_catalog(), ())
    self.assertEqual(len(PARAM_SPECS), 129)
    self.assertEqual(len(ADDED_PARAM_SPECS), 128)
    self.assertEqual(len(OVERRIDDEN_PARAM_SPECS), 1)
    self.assertEqual(len(PARAM_SPECS_BY_KEY), len(PARAM_SPECS))

    metadata = "\n".join(f"{spec.action.value}|{spec.key}|{spec.cpp_attributes}" for spec in PARAM_SPECS) + "\n"
    self.assertEqual(sha256(metadata.encode()).hexdigest(), REGISTRY_METADATA_SHA256)

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
      "HondaCivicRadarTryout",
      "HondaNotchEnabled",
      "HondaNotchFreq",
      "HondaNotchQ",
      "HondaPidFriction",
        "HondaPidTuneScale",
        "NrdrLaneChangeEndpointSteerRatio",
        "NrdrLearnSteerRatio",
        "NrdrLegacyDualBpSteerRatio",
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
