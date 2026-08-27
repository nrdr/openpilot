from collections import Counter
from importlib import import_module
import os
from pathlib import Path
import subprocess
import sys
import unittest

from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.params.profiles import (
  CLARITY_ROAD_TESTED_2026_08_21,
  HANDCRAFTED_EXTERNAL_PARAM_KEYS,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  STEER_RATIO_ENDPOINT_PROFILE_BY_FP,
  STEER_RATIO_ENDPOINT_PROFILES,
  HandcraftedLateralProfile,
  ProfileParamStore,
  ProfileValue,
  SteerRatioEndpointProfile,
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  get_steer_ratio_endpoint_profile,
)
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamFlag, ParamOwner, ParamType


EXPECTED_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

EXPECTED_REGISTRY_OVERRIDES = {
  "NrdrLatRateDamping",
  "HondaCenterScale",
  "NrdrLatStiction",
  "NrdrTuneLearner",
  "NrdrTuneLearnerStrength",
  "NrdrTuneLearnerRate",
  "NrdrDriverOverrideThreshold",
  "NrdrOverrideThresholdCenterBoost",
  "HondaDriverAssistDuringOverride",
  "HondaOverrideFadeDownSecs",
  "HondaOverrideFadeUpSecs",
  "HondaTorqueLowPassFilter",
  "HondaSteerDeltaUp",
  "HondaSteerDeltaDown",
}

BORROWED_DEFAULTS = {
  "LagdToggle": True,
  "LagdToggleDelay": 0.2,
}


def _typed_default(key: str):
  spec = PARAM_SPECS_BY_KEY[key]
  assert spec.default is not None
  if spec.param_type is ParamType.BOOL:
    return spec.default == "1"
  if spec.param_type is ParamType.INT:
    return int(spec.default)
  if spec.param_type is ParamType.FLOAT:
    return float(spec.default)
  raise AssertionError(f"unexpected profile parameter type for {key}: {spec.param_type}")


class RegistryDefaultParams:
  def __init__(self):
    self.values = {NrdrParamKey.NRDR_HANDCRAFTED_LATERAL_TUNE.value: True}
    self.writes = []

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    if key in self.values:
      return self.values[key]
    if not return_default:
      return None
    if key in BORROWED_DEFAULTS:
      return BORROWED_DEFAULTS[key]
    return _typed_default(key)

  def put_bool(self, key, value, block=False):
    self.values[key] = bool(value)
    self.writes.append(("put_bool", key, bool(value), block))

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes.append(("put", key, value, block))


class TestParamProfiles(unittest.TestCase):
  def test_profile_shape_order_types_and_ownership(self) -> None:
    self.assertEqual(HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS, EXPECTED_HANDCRAFTED_FINGERPRINTS)
    self.assertEqual(tuple(HANDCRAFTED_LATERAL_PROFILES), EXPECTED_HANDCRAFTED_FINGERPRINTS)
    self.assertEqual(len(HONDA_TORQUE_MOD_HANDCRAFTED_VALUES), 40)
    self.assertEqual(HANDCRAFTED_EXTERNAL_PARAM_KEYS, frozenset(BORROWED_DEFAULTS))

    all_values = {
      key: value
      for profile in HANDCRAFTED_LATERAL_PROFILES.values()
      for key, value in profile.values
    }
    self.assertEqual(len(all_values), 50)
    self.assertTrue(all(type(key) is str for key in all_values))
    self.assertEqual(
      Counter("bool" if isinstance(value, bool) else type(value).__name__ for value in all_values.values()),
      Counter({"bool": 13, "int": 17, "float": 20}),
    )

    owned_keys = set(all_values) - HANDCRAFTED_EXTERNAL_PARAM_KEYS
    self.assertEqual(len(owned_keys), 48)
    self.assertTrue(owned_keys <= {key.value for key in NrdrParamKey})
    self.assertTrue(all(PARAM_SPECS_BY_KEY[key].flags == (ParamFlag.PERSISTENT, ParamFlag.BACKUP)
                        for key in owned_keys))
    self.assertEqual(
      Counter(PARAM_SPECS_BY_KEY[key].owner for key in owned_keys),
      Counter({ParamOwner.LATERAL: 34, ParamOwner.HONDA: 14}),
    )

    for fingerprint, profile in HANDCRAFTED_LATERAL_PROFILES.items():
      endpoint = get_steer_ratio_endpoint_profile(fingerprint)
      self.assertIsNotNone(endpoint)
      self.assertEqual(len(profile.values), 42)
      self.assertEqual(len(dict(profile.values)), 42)
      self.assertEqual(profile.values[:2], endpoint.param_values)
      self.assertEqual(profile.values[2:], HONDA_TORQUE_MOD_HANDCRAFTED_VALUES)
      self.assertEqual(profile.version, 14)
      self.assertEqual(profile.fingerprint, fingerprint)

    self.assertIs(CLARITY_ROAD_TESTED_2026_08_21, HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"])
    self.assertIsNone(get_handcrafted_lateral_profile("HONDA_CRV_HYBRID"))
    self.assertIsNotNone(get_steer_ratio_endpoint_profile("HONDA_CRV_HYBRID"))

  def test_registry_and_profile_defaults_remain_distinct_layers(self) -> None:
    profile_values = {
      key: value
      for profile in HANDCRAFTED_LATERAL_PROFILES.values()
      for key, value in profile.values
      if key not in HANDCRAFTED_EXTERNAL_PARAM_KEYS
    }
    differing = {key for key, value in profile_values.items() if _typed_default(key) != value}
    self.assertEqual(differing, EXPECTED_REGISTRY_OVERRIDES)

  def test_reconciliation_uses_typed_ordered_blocking_writes_and_is_idempotent(self) -> None:
    params = RegistryDefaultParams()
    profile = get_handcrafted_lateral_profile("HONDA_CLARITY")
    expected_changed = [
      key for key, value in profile.values
      if (BORROWED_DEFAULTS.get(key, _typed_default(key) if key not in BORROWED_DEFAULTS else None)) != value
    ]

    changed = apply_handcrafted_lateral_profile("HONDA_CLARITY", params, block=True)
    self.assertEqual(changed, expected_changed)
    self.assertEqual(len(changed), 16)
    self.assertEqual(set(changed), EXPECTED_REGISTRY_OVERRIDES | HANDCRAFTED_EXTERNAL_PARAM_KEYS)
    self.assertEqual([write[1] for write in params.writes], changed)
    self.assertTrue(all(write[3] is True for write in params.writes))

    values = dict(profile.values)
    for method, key, value, _ in params.writes:
      self.assertEqual(method, "put_bool" if isinstance(values[key], bool) else "put")
      self.assertEqual(value, values[key])

    self.assertEqual(apply_handcrafted_lateral_profile("HONDA_CLARITY", params, block=True), [])
    self.assertEqual(len(params.writes), 16)

  def test_legacy_modules_reexport_the_canonical_objects(self) -> None:
    legacy_handcrafted = import_module("openpilot.sunnypilot.nrdr.handcrafted_lateral")
    legacy_steer_ratio = import_module("openpilot.sunnypilot.nrdr.steer_ratio_tuning")

    self.assertIs(legacy_handcrafted.HandcraftedLateralProfile, HandcraftedLateralProfile)
    self.assertIs(legacy_handcrafted.ProfileParamStore, ProfileParamStore)
    self.assertIs(legacy_handcrafted.ParamsLike, ProfileParamStore)
    self.assertIs(legacy_handcrafted.ProfileValue, ProfileValue)
    self.assertIs(legacy_handcrafted.ParamValue, ProfileValue)
    self.assertIs(legacy_handcrafted.HANDCRAFTED_LATERAL_PROFILES, HANDCRAFTED_LATERAL_PROFILES)
    self.assertIs(legacy_handcrafted.CLARITY_ROAD_TESTED_2026_08_21, CLARITY_ROAD_TESTED_2026_08_21)
    self.assertIs(legacy_handcrafted.get_handcrafted_lateral_profile, get_handcrafted_lateral_profile)
    self.assertIs(legacy_handcrafted.apply_handcrafted_lateral_profile, apply_handcrafted_lateral_profile)

    self.assertIs(legacy_steer_ratio.SteerRatioEndpointProfile, SteerRatioEndpointProfile)
    self.assertIs(legacy_steer_ratio.STEER_RATIO_ENDPOINT_PROFILES, STEER_RATIO_ENDPOINT_PROFILES)
    self.assertIs(legacy_steer_ratio.STEER_RATIO_ENDPOINT_PROFILE_BY_FP, STEER_RATIO_ENDPOINT_PROFILE_BY_FP)
    self.assertIs(legacy_steer_ratio.get_steer_ratio_endpoint_profile, get_steer_ratio_endpoint_profile)

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
