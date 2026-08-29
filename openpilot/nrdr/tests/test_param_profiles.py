from importlib import import_module
import os
from pathlib import Path
import subprocess
import sys
import unittest

from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.params.profiles import (
  CLARITY_CURRENT_LATERAL_2026_08_28,
  CLARITY_HANDCRAFTED_LATERAL_VALUES_V17,
  CLARITY_ROAD_TESTED_2026_08_21,
  HANDCRAFTED_EXTERNAL_PARAM_KEYS,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  HandcraftedLateralProfile,
  ProfileParamStore,
  ProfileValue,
  consume_handcrafted_lateral_request,
  get_handcrafted_lateral_profile,
  handcrafted_lateral_profile_supported,
)
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamFlag, ParamLifecycle


EXPECTED_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)


class TestParamProfiles(unittest.TestCase):
  def test_profile_shapes_types_and_registry_ownership(self) -> None:
    self.assertEqual(HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS, EXPECTED_HANDCRAFTED_FINGERPRINTS)
    self.assertEqual(tuple(HANDCRAFTED_LATERAL_PROFILES), EXPECTED_HANDCRAFTED_FINGERPRINTS)
    self.assertEqual(len(HONDA_TORQUE_MOD_HANDCRAFTED_VALUES), 38)
    self.assertEqual(len(CLARITY_HANDCRAFTED_LATERAL_VALUES_V17), 47)
    self.assertEqual(HANDCRAFTED_EXTERNAL_PARAM_KEYS, frozenset(("LagdToggle", "LagdToggleDelay")))

    for fingerprint, profile in HANDCRAFTED_LATERAL_PROFILES.items():
      expected = CLARITY_HANDCRAFTED_LATERAL_VALUES_V17 if fingerprint == "HONDA_CLARITY" else HONDA_TORQUE_MOD_HANDCRAFTED_VALUES
      self.assertEqual(profile.values, expected)
      self.assertEqual(len(profile.values), len(dict(profile.values)))
      self.assertTrue(all(type(key) is str for key, _ in profile.values))
      for key, value in profile.values:
        self.assertIn(type(value), (bool, int, float))
        if key in HANDCRAFTED_EXTERNAL_PARAM_KEYS:
          continue
        self.assertIn(key, {item.value for item in NrdrParamKey})
        self.assertEqual(PARAM_SPECS_BY_KEY[key].flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))

    self.assertIs(CLARITY_CURRENT_LATERAL_2026_08_28, HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"])
    self.assertIs(CLARITY_ROAD_TESTED_2026_08_21, CLARITY_CURRENT_LATERAL_2026_08_28)
    self.assertIsNone(get_handcrafted_lateral_profile("HONDA_CRV_HYBRID"))

  def test_command_and_friction_registry_contract(self) -> None:
    command = PARAM_SPECS_BY_KEY["NrdrHandcraftedLateralTune"]
    self.assertEqual(command.lifecycle, ParamLifecycle.COMMAND)
    self.assertEqual(command.flags, (ParamFlag.PERSISTENT, ParamFlag.BACKUP))
    self.assertEqual(command.default, "0")
    self.assertEqual(PARAM_SPECS_BY_KEY["NrdrInterpolatedTorqueFriction"].default, "0.12")
    self.assertEqual(PARAM_SPECS_BY_KEY["NrdrInterpolatedTorqueFrictionStandard"].default, "0.10")
    self.assertEqual(PARAM_SPECS_BY_KEY["NrdrInterpolatedTorqueFrictionHighway"].default, "0.06")

  def test_legacy_modules_reexport_the_canonical_objects(self) -> None:
    legacy = import_module("openpilot.sunnypilot.nrdr.handcrafted_lateral")
    params_api = import_module("openpilot.nrdr.params")
    self.assertIs(legacy.HandcraftedLateralProfile, HandcraftedLateralProfile)
    self.assertIs(legacy.ProfileParamStore, ProfileParamStore)
    self.assertIs(legacy.ParamsLike, ProfileParamStore)
    self.assertIs(legacy.ProfileValue, ProfileValue)
    self.assertIs(legacy.ParamValue, ProfileValue)
    self.assertIs(legacy.consume_handcrafted_lateral_request, consume_handcrafted_lateral_request)
    self.assertIs(legacy.handcrafted_lateral_profile_supported, handcrafted_lateral_profile_supported)
    self.assertIs(params_api.consume_handcrafted_lateral_request, consume_handcrafted_lateral_request)
    for module in (legacy, params_api):
      self.assertFalse(hasattr(module, "apply_handcrafted_lateral_profile"))
      self.assertFalse(hasattr(module, "restore_handcrafted_lateral_profile"))

  def test_direct_profile_import_has_no_runtime_params_dependency(self) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(repository_root), environment.get("PYTHONPATH"))))
    script = """
import sys
sys.modules["openpilot.common.params"] = None
sys.modules["openpilot.common.swaglog"] = None
sys.modules["zmq"] = None
from openpilot.nrdr.params.profiles import HANDCRAFTED_LATERAL_PROFILES
assert len(HANDCRAFTED_LATERAL_PROFILES) == 7
assert "openpilot.common.params" not in sys.modules or sys.modules["openpilot.common.params"] is None
"""
    subprocess.run([sys.executable, "-c", script], cwd=repository_root, env=environment, check=True)


if __name__ == "__main__":
  unittest.main()
