"""Presentation eligibility and saved choices; never an actuation authority."""
from opendbc.car.honda.values import CAR, HONDA_BOSCH
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity


def pcm_tuning_available(CP, CP_SP, params) -> bool:
  present, fingerprint, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(CP, fingerprint, brand, selection_present=present)
  return bool(identity is not None and identity[1] == "honda" and identity[0] in CAR
              and identity[0] not in HONDA_BOSCH
              and getattr(CP, "openpilotLongitudinalControl", False)
              and not getattr(CP_SP, "enableGasInterceptor", True)
              and not (getattr(CP_SP, "flags", 0) & HondaFlagsSP.STOCK_LONGITUDINAL))


def saved_pcm_mode(params) -> int:
  value = params.get("NrdrHondaPcmMode")
  # Typed Params returns an int. Reject bool and malformed/stale values as Off.
  return value if type(value) is int and value in (0, 1, 2) else 0


def saved_wind_brake(params) -> bool:
  value = params.get("NrdrHondaWindBrake")
  return value if type(value) is bool else True


def save_pcm_choice(state, key: str, value) -> bool:
  if not state.is_offroad() or not pcm_tuning_available(state.CP, state.CP_SP, state.params):
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
