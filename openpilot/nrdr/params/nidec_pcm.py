"""Shared copy and strict saved-value decoding for the Civic PCM experiments."""

PCM_EXPERIMENTS = {
  "NrdrHondaPcmFixedCruise": (
    "Fixed PCM Cruise Speed",
    "Holds the PCM cruise ceiling at 90 mph; openpilot sets speed, including a 0 mph attempt. "
    + "Civic PCM only. Change while parked. Applies next drive; no device reboot.",
  ),
  "NrdrHondaLegacyPcm": (
    "Legacy Kegman PCM Control",
    "Uses Kegman PCM control, bypassing MVL, saved gas tuning, wind brake and custom PCM shaping. "
    + "Civic PCM only. Change while parked. Applies next drive; no device reboot.",
  ),
}

PCM_EXPERIMENT_DETAILS = {
  "NrdrHondaPcmFixedCruise": (
    "Default Off. Exact Civic Nidec, no gas interceptor, openpilot longitudinal; excludes stock ACC. "
    + "90 mph is the PCM cruise-speed field, not the driving target. Zero is an attempt, not a guarantee the PCM accepts it. "
    + "Independent of Legacy; neither experiment guarantees equivalent hardware behavior."
  ),
  "NrdrHondaLegacyPcm": (
    "Default Off. Speed-based Kegman PCM control. Exact Civic Nidec, no gas interceptor, openpilot longitudinal; excludes stock ACC. "
    + "Saved learning and tuning choices are kept, but conflicts stay locked until the next drive with Legacy off. "
    + "Independent of Fixed PCM Cruise Speed; neither experiment guarantees equivalent hardware behavior."
  ),
}


def decode_pcm_experiment(value) -> bool | None:
  if type(value) is bool:
    return value
  if type(value) is bytes:
    return {b"0": False, b"1": True}.get(value)
  if type(value) is str:
    return {"0": False, "1": True}.get(value)
  return None
