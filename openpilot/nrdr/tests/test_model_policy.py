from types import SimpleNamespace
import unittest

from openpilot.nrdr.features.lateral.model_policy import (
  LEGACY_DUAL_BP_ARTIFACT_SHA256S,
  PURE_FIRMWARE_VGR_ARTIFACT_SHA256S,
  REVIEWED_MODEL_ARTIFACTS,
  SteerRatioModelPolicy,
  classify_steer_ratio_model,
  model_artifact_sha256,
  resolve_steer_ratio_model,
)


def mapping_bundle(artifact_sha256, *, internal_name="TEST", display_name="Test Model", **metadata):
  return {
    "internalName": internal_name,
    "displayName": display_name,
    "models": [{"artifact": {"downloadUri": {"sha256": artifact_sha256}}}],
    **metadata,
  }


class TestSteerRatioModelPolicy(unittest.TestCase):
  def test_exact_legacy_registry(self):
    self.assertEqual(len(LEGACY_DUAL_BP_ARTIFACT_SHA256S), 7)
    for artifact_sha256 in LEGACY_DUAL_BP_ARTIFACT_SHA256S:
      with self.subTest(artifact_sha256=artifact_sha256):
        self.assertIs(classify_steer_ratio_model(mapping_bundle(artifact_sha256)),
                      SteerRatioModelPolicy.LEGACY_DUAL_BP)

  def test_exact_pure_firmware_registry(self):
    self.assertEqual(len(PURE_FIRMWARE_VGR_ARTIFACT_SHA256S), 6)
    for artifact_sha256 in PURE_FIRMWARE_VGR_ARTIFACT_SHA256S:
      with self.subTest(artifact_sha256=artifact_sha256):
        self.assertIs(classify_steer_ratio_model(mapping_bundle(artifact_sha256)),
                      SteerRatioModelPolicy.PURE_FIRMWARE_VGR)

  def test_registries_are_disjoint_valid_sha256s(self):
    self.assertEqual(len(REVIEWED_MODEL_ARTIFACTS), 13)
    self.assertEqual(len({artifact.artifact_sha256 for artifact in REVIEWED_MODEL_ARTIFACTS}), 13)
    self.assertTrue(all(artifact.name and len(artifact.source_ref) == 40 for artifact in REVIEWED_MODEL_ARTIFACTS))
    self.assertTrue(LEGACY_DUAL_BP_ARTIFACT_SHA256S.isdisjoint(PURE_FIRMWARE_VGR_ARTIFACT_SHA256S))
    for artifact_sha256 in LEGACY_DUAL_BP_ARTIFACT_SHA256S | PURE_FIRMWARE_VGR_ARTIFACT_SHA256S:
      self.assertEqual(len(artifact_sha256), 64)
      self.assertEqual(int(artifact_sha256, 16) >= 0, True)

  def test_classifier_accepts_capnp_shaped_objects_and_normalizes_case(self):
    artifact_sha256 = next(iter(PURE_FIRMWARE_VGR_ARTIFACT_SHA256S))
    bundle = SimpleNamespace(
      internalName="TSFM",
      displayName="Terrible Super Fantastic Model",
      models=[SimpleNamespace(artifact=SimpleNamespace(
        downloadUri=SimpleNamespace(sha256=f"  {artifact_sha256.upper()}  "),
      ))],
    )
    resolution = resolve_steer_ratio_model(bundle)
    self.assertIs(resolution.policy, SteerRatioModelPolicy.PURE_FIRMWARE_VGR)
    self.assertEqual(resolution.artifact_sha256, artifact_sha256)
    self.assertEqual(resolution.internal_name, "TSFM")
    self.assertEqual(resolution.display_name, "Terrible Super Fantastic Model")

  def test_names_refs_and_folders_never_enroll_an_unknown_artifact(self):
    bundle = mapping_bundle(
      "0" * 64,
      internal_name="PMV2",
      display_name="Pop Model v2",
      ref="62bf6fb072880905a4c490f0f4f4a6b3c23346ec",
      overrides=[{"key": "folder", "value": "2026 World Models"}],
    )
    self.assertIs(classify_steer_ratio_model(bundle), SteerRatioModelPolicy.UNKNOWN)

  def test_only_first_models_aggregate_artifact_sha_is_authoritative(self):
    known = next(iter(LEGACY_DUAL_BP_ARTIFACT_SHA256S))
    bundle = mapping_bundle("0" * 64)
    bundle["models"].append({"artifact": {"downloadUri": {"sha256": known}}})
    bundle["models"][0]["artifact"]["chunks"] = [{"sha256": known}]
    self.assertEqual(model_artifact_sha256(bundle), "0" * 64)
    self.assertIs(classify_steer_ratio_model(bundle), SteerRatioModelPolicy.UNKNOWN)

  def test_missing_malformed_and_unregistered_hashes_are_unknown(self):
    malformed = (
      None,
      {},
      {"models": []},
      {"models": [{}]},
      mapping_bundle(None),
      mapping_bundle(123),
      mapping_bundle("short"),
      mapping_bundle("z" * 64),
    )
    for bundle in malformed:
      with self.subTest(bundle=bundle):
        self.assertIsNone(model_artifact_sha256(bundle))
        self.assertIs(classify_steer_ratio_model(bundle), SteerRatioModelPolicy.UNKNOWN)

    unregistered = mapping_bundle("0" * 64)
    self.assertEqual(model_artifact_sha256(unregistered), "0" * 64)
    self.assertIs(classify_steer_ratio_model(unregistered), SteerRatioModelPolicy.UNKNOWN)


if __name__ == "__main__":
  unittest.main()
