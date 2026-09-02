def select_default_model(params, available_models) -> None:
  if not params.get_bool("NrdrAutoSelectModel") or params.get("ModelManager_DownloadRef") is not None:
    return
  candidates = [model for model in available_models if model.ref and "pop" in model.displayName.lower() and "v2" in model.displayName.lower()]
  if candidates:
    params.put("ModelManager_DownloadRef", max(candidates, key=lambda model: model.index).ref)
    params.remove("NrdrAutoSelectModel")
