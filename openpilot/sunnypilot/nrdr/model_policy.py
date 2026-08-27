from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from string import hexdigits
from typing import Any


class SteerRatioModelPolicy(Enum):
  UNKNOWN = "unknown"
  LEGACY_DUAL_BP = "legacy_dual_bp"
  PURE_FIRMWARE_VGR = "pure_firmware_vgr"


@dataclass(frozen=True)
class SteerRatioModelResolution:
  policy: SteerRatioModelPolicy
  artifact_sha256: str | None
  internal_name: str
  display_name: str


@dataclass(frozen=True)
class ReviewedModelArtifact:
  name: str
  source_ref: str
  artifact_sha256: str
  policy: SteerRatioModelPolicy


# This is an immutable review ledger, not a manifest matcher. Names and source refs
# identify what humans reviewed; only artifact_sha256 is consulted at runtime.
REVIEWED_MODEL_ARTIFACTS = (
  ReviewedModelArtifact(
    "Off Policy Model", "d90758cfaecb2cf13d9098c6aade37e68d6034d2",
    "f5e8c7938c5b49615ca69a63db8ca1562fab3021fdd33f640bef7f8df9572b35", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Off-policy Model v2", "ae34a24c59d85df7efad5fde2b760fb6d0b9dd6e",
    "0324ca61f072a3bbeecb4f6f42226e11a37896197d7f3c4199167b9c15ade14e", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Off Policy Model v3", "7e548dd765873bed301c0a19cfe10c3ca6be2bbe",
    "80287f5fedbd6634aef0551e5b49b5a9658a76bfe72f875129521ae52862e49a", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Off-Policy Model v4", "25abcc49fce2f6268d8cabf759e31c626edbf584",
    "f3d35e379de64280881fc76031704cf904ae014474fbef8133c7358b02c939c2", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Off-Policy Model v5", "b390b98c5a359c293fdc2501af79b19867fcdac4",
    "1b699f20c6db0522577a58c35c87060c1abff658abe6e2e12380411f36d529be", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Pop Model", "6f71783a8a8faa07ddaeef5bbb6809b4f4f44a15",
    "c838d552e96386ab3dca5129b64639b279034b0b826d06498477c813a3834c30", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Pop Model v2", "62bf6fb072880905a4c490f0f4f4a6b3c23346ec",
    "c48899574c1303e47ca2a6f80113876ca5eb749c4a75c89b53cc8029bb3bb710", SteerRatioModelPolicy.LEGACY_DUAL_BP,
  ),
  ReviewedModelArtifact(
    "Michael RL v2", "37b38bf738edfb1daa6875255f581e5fc9b0a258",
    "50321da6563febf862e3d795b6fb54b362ac95a64db62caf3b3a7de64692708d", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
  ReviewedModelArtifact(
    "Get Your Hopes Up", "574735edc6e1aafdc2a69395f9a32e7f5cc4b62b",
    "bb7b02e0dfa4345b5ab559b2690ccce9d7fd5cd649ec743cc8eec5f685fcb8d8", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
  ReviewedModelArtifact(
    "RDF Model", "a95e2c25cae5fbf1afba7628bfb7acc4af59e0cc",
    "1ebb2ae974612a66a086570ef0876692464e0fbfdbbc211339d87f0b691cc2b9", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
  ReviewedModelArtifact(
    "RDF Model v2", "35703097905a122c9f3ddf0d12889b4873d7e2a2",
    "46521c8aef817e9b16beb5fb4ce4c323ca280493a7cd70ab62eecd8f85968223", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
  ReviewedModelArtifact(
    "Terrible Super Fantastic", "4d911346cde4e0d2978a625f31679808284cc19d",
    "f858afb2a46a696da21d888960f288b54c53ed015c1e74a5b8742b8483885739", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
  ReviewedModelArtifact(
    "Terrible Super Fantastic Do Over", "0394d7284cfc229f772ee4fa73ff724ba8245110",
    "92d06467e4de97c40ffdc366e385a4f5897f36fc8ea632bd9bed113a3083fea8", SteerRatioModelPolicy.PURE_FIRMWARE_VGR,
  ),
)

_POLICY_BY_ARTIFACT_SHA256 = {artifact.artifact_sha256: artifact.policy for artifact in REVIEWED_MODEL_ARTIFACTS}
LEGACY_DUAL_BP_ARTIFACT_SHA256S = frozenset(
  artifact.artifact_sha256 for artifact in REVIEWED_MODEL_ARTIFACTS
  if artifact.policy is SteerRatioModelPolicy.LEGACY_DUAL_BP
)
PURE_FIRMWARE_VGR_ARTIFACT_SHA256S = frozenset(
  artifact.artifact_sha256 for artifact in REVIEWED_MODEL_ARTIFACTS
  if artifact.policy is SteerRatioModelPolicy.PURE_FIRMWARE_VGR
)


def _member(value: Any, name: str) -> Any:
  return value.get(name) if isinstance(value, Mapping) else getattr(value, name)


def model_artifact_sha256(bundle: Any) -> str | None:
  """Return models[0]'s aggregate artifact SHA, or None for malformed bundles."""
  try:
    model = _member(bundle, "models")[0]
    artifact = _member(model, "artifact")
    download_uri = _member(artifact, "downloadUri")
    value = _member(download_uri, "sha256")
  except (AttributeError, IndexError, KeyError, TypeError):
    return None

  if isinstance(value, bytes):
    try:
      value = value.decode("ascii")
    except UnicodeDecodeError:
      return None
  if not isinstance(value, str):
    return None

  value = value.strip().lower()
  if len(value) != 64 or any(character not in hexdigits for character in value):
    return None
  return value


def _text_member(bundle: Any, name: str) -> str:
  try:
    value = _member(bundle, name)
  except (AttributeError, KeyError, TypeError):
    return ""
  return value.strip() if isinstance(value, str) else ""


def resolve_steer_ratio_model(bundle: Any) -> SteerRatioModelResolution:
  artifact_sha256 = model_artifact_sha256(bundle)
  policy = _POLICY_BY_ARTIFACT_SHA256.get(artifact_sha256, SteerRatioModelPolicy.UNKNOWN)
  return SteerRatioModelResolution(
    policy=policy,
    artifact_sha256=artifact_sha256,
    internal_name=_text_member(bundle, "internalName"),
    display_name=_text_member(bundle, "displayName"),
  )


def classify_steer_ratio_model(bundle: Any) -> SteerRatioModelPolicy:
  return resolve_steer_ratio_model(bundle).policy
