"""Presentation eligibility and saved choices; never an actuation authority."""
from opendbc.car.honda.values import CAR, HONDA_BOSCH

from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled
from openpilot.nrdr.params.mvl_pcm_deadzone import MVL_PCM_DEADZONE_VALUES


def live_gas_available(CP, CP_SP, params) -> bool:
  # This admits saved choices, not controller operation. Persistent CP can still
  # describe the last factory-ACC drive after the user changes its saved mode.
  present, fingerprint, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(CP, fingerprint, brand, selection_present=present)
  return bool(identity is not None and identity[1] == "honda" and identity[0] in CAR
              and CP_SP is not None)


def save_live_gas_choice(state, value) -> bool:
  if (type(value) is not bool or not state.is_offroad()
      or not live_gas_available(state.CP, state.CP_SP, state.params)):
    return False
  state.params.put_bool("HondaLiveLearningGas", value, block=True)
  state.params.put_bool("OnroadCycleRequested", True)
  return True


def pcm_tuning_available(CP, CP_SP, params) -> bool:
  present, fingerprint, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(CP, fingerprint, brand, selection_present=present)
  return bool(identity is not None and identity[1] == "honda" and identity[0] in CAR
              and identity[0] not in HONDA_BOSCH
              and CP_SP is not None and not getattr(CP_SP, "enableGasInterceptor", True))


def saved_pcm_mode(params) -> int:
  value = params.get("NrdrHondaPcmMode")
  # Typed Params returns an int. Reject bool and malformed/stale values as Off.
  return value if type(value) is int and value in (0, 1, 2) else 0


def live_gas_status(CP, params, CP_SP=None, *, is_offroad: bool | None = None) -> str:
  selected = params.get_bool("HondaLiveLearningGas")
  parked = is_offroad if is_offroad is not None else params.get("IsOffroad") is not False
  if parked:
    return "MVL next drive" if selected else "MVL Off next drive"
  if mvl_longitudinal_enabled(CP):
    return "MVL active" if selected else "MVL active\nOff next drive"
  return "MVL next drive" if selected else "MVL inactive"


def mvl_pcm_deadzone_available(CP, CP_SP, params) -> bool:
  # Hardware eligibility, not whether the saved choice is currently consumed.
  return pcm_tuning_available(CP, CP_SP, params) and CP.carFingerprint == CAR.HONDA_CIVIC


def saved_mvl_pcm_deadzone(params) -> int:
  value = params.get("NrdrMvlPcmDeadzone")
  return value if type(value) is int and value in MVL_PCM_DEADZONE_VALUES else 0


def save_mvl_pcm_deadzone(state, value) -> bool:
  # May be prepared while parked; only the MVL PCM path consumes this choice.
  if (type(value) is not int or value not in MVL_PCM_DEADZONE_VALUES or not state.is_offroad()
      or not mvl_pcm_deadzone_available(state.CP, state.CP_SP, state.params)):
    return False
  state.params.put("NrdrMvlPcmDeadzone", value, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True


def saved_wind_brake(params) -> bool:
  value = params.get("NrdrHondaWindBrake")
  return value if type(value) is bool else True


def save_pcm_choice(state, key: str, value) -> bool:
  if (not pcm_tuning_available(state.CP, state.CP_SP, state.params) or not state.is_offroad()
      or not tuning_write_allowed(state.params, key, CP=state.CP, CP_SP=state.CP_SP, is_offroad=state.is_offroad())):
    return False
  if key == "NrdrHondaPcmMode" and type(value) is int and value in (0, 1, 2):
    state.params.put(key, value, block=True)
  elif key == "NrdrHondaWindBrake" and type(value) is bool:
    state.params.put_bool(key, value, block=True)
  else:
    return False
  # Saving is not evidence that the startup-latched controller has changed.
  state.params.put_bool("OnroadCycleRequested", True)
  return True
