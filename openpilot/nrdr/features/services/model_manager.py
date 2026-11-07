from pathlib import PurePosixPath
from urllib.parse import urlparse

from openpilot.nrdr.features.services import TINYGRAD_RUNTIME_REF


def _compatible_automatic_download(model) -> bool:
  # Catalog provenance can admit a new download only for this exact runtime.
  # A model source ref or the existence of a legacy rebuild recipe is not proof
  # that a fresh install has a compatible compiled artifact.
  if getattr(model, "tinygradRef", "") != TINYGRAD_RUNTIME_REF or str(getattr(model, "runner", "")) != "tinygrad":
    return False
  models = getattr(model, "models", ())
  if not models:
    return False
  artifact = getattr(models[0], "artifact", None)
  download = getattr(artifact, "downloadUri", None)
  digest = str(getattr(download, "sha256", "")).lower()
  return bool(str(getattr(artifact, "fileName", "")).lower().endswith(".pkl") and getattr(download, "uri", "") and
              len(digest) == 64 and all(char in "0123456789abcdef" for char in digest))


def select_default_model(params, available_models) -> None:
  if not params.get_bool("NrdrAutoSelectModel") or params.get("ModelManager_DownloadRef") is not None:
    return
  # A first-run request is not permission to replace an existing preference,
  # including a legacy selection waiting for a compatible rebuild.
  if any(params.get(key) is not None for key in ("ModelManager_ActiveBundle", "ModelManager_ActiveBundleChestnut")):
    return
  candidates = [model for model in available_models if model.ref and getattr(model, "internalName", "") == "PMV2" and
                _compatible_automatic_download(model)]
  if candidates:
    params.put("ModelManager_DownloadRef", max(candidates, key=lambda model: model.index).ref)
    # Keep a completed/opt-out value: deleting it looks like an unset preference
    # after a reboot or a later model removal.
    params.put_bool("NrdrAutoSelectModel", False)


def _artifact_identity(bundle) -> tuple:
  # Local content-addressed filenames differ from catalog names after repair.
  return tuple((str(model.type), model.artifact.downloadUri.sha256.lower(),
                tuple(chunk.sha256.lower() for chunk in model.artifact.chunks)) for model in bundle.models)


def get_model_repair_candidate(saved, available_models):
  """Upgrade a saved selection's compiler artifacts, never its model identity."""
  if not saved or not saved.ref or not saved.internalName or str(saved.runner) != "tinygrad":
    return None
  matches = [model for model in available_models if model.ref == saved.ref and model.internalName == saved.internalName and
             model.generation == saved.generation and str(model.runner) == "tinygrad"]
  if len(matches) != 1:
    return None
  target = matches[0]
  if not _compatible_automatic_download(target):
    return None
  for model in target.models:
    artifact = model.artifact
    name = artifact.fileName
    uri = urlparse(artifact.downloadUri.uri)
    if (not name or PurePosixPath(name).name != name or "\\" in name or not name.endswith(".pkl") or
        uri.scheme != "https" or not uri.hostname):
      return None
    hashes = [artifact.downloadUri.sha256, *(chunk.sha256 for chunk in artifact.chunks)]
    if any(len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()) for digest in hashes):
      return None
  if saved.tinygradRef == TINYGRAD_RUNTIME_REF and _artifact_identity(saved) == _artifact_identity(target):
    return None
  return target


__all__ = ("get_model_repair_candidate", "select_default_model")
