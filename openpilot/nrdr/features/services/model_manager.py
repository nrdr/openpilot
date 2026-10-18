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
  if params.get("ModelManager_ActiveBundle") or params.get("ModelManager_ActiveBundleChestnut"):
    return
  candidates = [model for model in available_models if model.ref and "pop" in model.displayName.lower() and
                "v2" in model.displayName.lower() and _compatible_automatic_download(model)]
  if candidates:
    params.put("ModelManager_DownloadRef", max(candidates, key=lambda model: model.index).ref)
    params.remove("NrdrAutoSelectModel")


__all__ = ("select_default_model",)
