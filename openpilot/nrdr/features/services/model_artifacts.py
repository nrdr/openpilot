"""Model artifact provenance and fail-closed ABI admission; no Params I/O."""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

from openpilot.common.file_chunker import open_file_chunked

TINYGRAD_RUNTIME_REF = "fe5d3169ba4f41d0947ad174925f413cbea9d056"
# The current sunnypilot catalogs publish SPTGPLN1 kernels, not tinygrad objects.
PLAIN_ARTIFACT_REFS = frozenset(("5d186bdb43c2bcc6c56b6ececf427c34bada0de9", "52e8c3e840b44de2ac9e98a0a1484fa09caf0064"))
ARTIFACT_ABI = "generic-onnx-warp-v1"
_MANIFEST = Path(__file__).resolve().parents[2] / "config" / "model_artifacts.json"

__all__ = ("ARTIFACT_ABI", "TINYGRAD_RUNTIME_REF", "ModelAdmissionError", "admit_default_artifact",
           "admit_selected_artifact", "artifact_sha256", "runtime_provenance", "write_artifact_record")


class ModelAdmissionError(RuntimeError):
  """The saved selection is retained, but cannot run without a verified migration."""


def artifact_sha256(path: str | Path) -> str:
  with open_file_chunked(str(path)) as stream:
    return hashlib.file_digest(stream, "sha256").hexdigest()


def runtime_provenance() -> dict:
  manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
  if manifest.get("abi") != ARTIFACT_ABI or manifest.get("tinygrad_ref") != TINYGRAD_RUNTIME_REF:
    raise ModelAdmissionError("Model provenance manifest and runtime disagree")
  root = Path(__file__).resolve().parents[4] / "tinygrad_repo"
  for relative, expected in manifest["tinygrad_files"].items():
    if hashlib.sha256((root / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != expected:
      raise ModelAdmissionError(f"tinygrad source does not match {TINYGRAD_RUNTIME_REF}: {relative}")
  return manifest


def _read_record(path: Path) -> dict:
  try:
    result = json.loads(path.read_text(encoding="utf-8"))
    return result if isinstance(result, dict) else {}
  except (OSError, ValueError):
    return {}


def _matching_artifact(path: Path, record: dict, *, camera: tuple[int, int] | None = None, device: str | None = None) -> bool:
  return (record.get("abi") == ARTIFACT_ABI and record.get("tinygrad_ref") == TINYGRAD_RUNTIME_REF and
          (camera is None or record.get("camera") in (None, list(camera))) and
          (device is None or str(record.get("device", "")).split(":")[0].split("+")[-1] == device.split(":")[0].split("+")[-1]) and
          record.get("artifact_sha256") == artifact_sha256(path))


def admit_default_artifact(path: str | Path, *, device: str | None = None) -> Path:
  path = Path(path)
  manifest = runtime_provenance()
  record = _read_record(Path(str(path) + ".nrdr-abi.json"))
  if record and _matching_artifact(path, record, device=device):
    source_name = {'driving_tinygrad.pkl': 'driving_supercombo.onnx', 'dmonitoring_model_tinygrad.pkl': 'dmonitoring_model.onnx'}.get(path.name)
    expected_source = manifest.get('source_models', {}).get(source_name, {}).get('sha256')
    if expected_source is None or record.get('source_sha256') == expected_source:
      return path
  expected = manifest.get("precompiled", {}).get(path.name)
  if expected and artifact_sha256(path) == expected:
    return path
  raise ModelAdmissionError(f"Rebuild required for {path.name}: no matching {ARTIFACT_ABI} provenance")


def admit_selected_artifact(path: str | Path, bundle, camera: tuple[int, int], *, device: str | None = None) -> Path:
  """Never reinterpret bundle.ref as tinygrad_ref or silently select another model."""
  manifest = runtime_provenance()
  path = Path(path)
  source_sha = str(bundle.models[0].artifact.downloadUri.sha256).lower()
  compiler_ref = str(getattr(bundle, "tinygradRef", ""))
  for trial in manifest.get("local_trials", []):
    entry = trial["catalog_bundle"]
    digest = entry["models"][0]["artifact"]["download_uri"]["sha256"]
    if bundle.ref == entry["ref"] or bundle.internalName == entry["short_name"] or source_sha == digest:
      if (bundle.ref == entry["ref"] and bundle.internalName == entry["short_name"] and
          source_sha == digest and compiler_ref == entry["tinygrad_ref"] == TINYGRAD_RUNTIME_REF and
          list(camera) == trial["camera"] and device == trial["device"] and artifact_sha256(path) == digest):
        return path
      raise ModelAdmissionError(f"Local trial {entry['short_name']} does not match its pinned artifact or hardware")
  if compiler_ref == TINYGRAD_RUNTIME_REF and artifact_sha256(path) == source_sha:
    return path
  record = _read_record(Path(str(path) + ".nrdr-migration.json"))
  if (record.get("source_artifact_sha256") == source_sha and artifact_sha256(path) == source_sha and record.get("model_ref") == bundle.ref and
      record.get("model_name") == bundle.internalName and record.get("verified") is True and
      record.get("camera") == list(camera)):
    relative = Path(record.get("artifact", ""))
    migrated = (path.parent / relative).resolve()
    if relative.parts and not relative.is_absolute() and migrated.is_relative_to(path.parent.resolve()):
      if _matching_artifact(migrated, record, camera=camera, device=device):
        return migrated
  # Prefer an already-verified local rebuild above. New downloads use upstream's
  # portable loader, which verifies their embedded reference outputs at load.
  from openpilot.sunnypilot.modeld_v2.helpers import is_plain_artifact
  if is_plain_artifact(path) and artifact_sha256(path) == source_sha:
    return path
  raise ModelAdmissionError(
    f"Selected model {bundle.displayName} retained but not admitted for tinygrad {TINYGRAD_RUNTIME_REF}; " +
    "recompile its original ONNX and validate this camera before driving. No default was substituted.")


def write_artifact_record(path: str | Path, *, source_sha256: str | None = None, camera=None) -> None:
  path = Path(path)
  runtime_provenance()
  record = {"abi": ARTIFACT_ABI, "tinygrad_ref": TINYGRAD_RUNTIME_REF, "artifact_sha256": artifact_sha256(path),
            "source_sha256": source_sha256, "camera": list(camera) if camera else None, "device": os.environ.get("DEV", "CPU:LLVM")}
  destination = Path(str(path) + ".nrdr-abi.json")
  temporary = Path(str(destination) + ".tmp")
  temporary.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
  temporary.replace(destination)


@lru_cache(maxsize=4)
def _listed_digest(path: Path, identity: tuple[int, ...]) -> str:
  # Sunnylink and the picker can poll. Rehash on replacement/change, not on every poll.
  # Selection and runtime admission independently verify contents without this cache.
  return artifact_sha256(path)


def verified_rebuild_bundles(model_root: str | Path, camera: tuple[int, int]) -> list[dict]:
  """List locally verified QCOM rebuilds; execution still requires full admission."""
  root = Path(model_root).resolve()
  bundles = []
  manifest = _read_record(_MANIFEST)
  for trial in manifest.get("local_trials", []):
    if trial["device"] != "QCOM" or trial["camera"] != list(camera):
      continue
    bundle = trial["catalog_bundle"]
    artifact = bundle["models"][0]["artifact"]
    path = root / artifact["file_name"]
    try:
      st = path.stat()
      if _listed_digest(path, (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)) == artifact["download_uri"]["sha256"]:
        bundles.append(bundle)
    except OSError:
      pass  # Optional: absent/unreadable trials are not advertised.
  for source_sha, recipe in manifest.get("legacy_rebuilds", {}).items():
    if not (bundle := recipe.get("catalog_bundle")):
      continue
    source = root / bundle["models"][0]["artifact"]["file_name"]
    record = _read_record(Path(str(source) + ".nrdr-migration.json"))
    if (record.get("verified") is not True or record.get("abi") != ARTIFACT_ABI or
        record.get("tinygrad_ref") != TINYGRAD_RUNTIME_REF or record.get("camera") != list(camera) or
        record.get("source_artifact_sha256") != source_sha or record.get("model_ref") != bundle["ref"] or
        record.get("model_name") != bundle["short_name"] or
        str(record.get("device", "")).split(":")[0].split("+")[-1] != "QCOM"):
      continue
    target = (root / record.get("artifact", "")).resolve()
    if source.is_file() and target.is_relative_to(root) and target.is_file():
      bundles.append(bundle)
  return bundles
