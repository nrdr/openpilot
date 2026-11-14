"""Presentation eligibility and saved choices; never an actuation authority."""
from opendbc.car.honda.values import CAR, HONDA_BOSCH, HONDA_BOSCH_A

from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled
from openpilot.nrdr.params.pcm_speed_deadzone import PCM_SPEED_DEADZONE_KEY, decode_speed_deadzone, read_speed_deadzone
from openpilot.nrdr.params.longitudinal_controller import (
  CONTROLLER_KEY, CONTROLLER_LABELS, CONTROLLER_DESCRIPTION, LongitudinalController, decode_controller, saved_controller,
)


def longitudinal_controller_choices(CP, CP_SP, params):
  if not live_gas_available(CP, CP_SP, params):
    return ()
  choices = [LongitudinalController.STANDARD, LongitudinalController.MVL]
  if CP.carFingerprint in HONDA_BOSCH_A:
    choices.append(LongitudinalController.BOSCH_RADAR)
  if CP.carFingerprint not in HONDA_BOSCH and CP_SP.enableGasInterceptor:
    choices.append(LongitudinalController.PERSONAL_PEDAL)
  return tuple(choices)


def longitudinal_controller_selection(CP, CP_SP, params):
  choices = longitudinal_controller_choices(CP, CP_SP, params)
  return saved_controller(params, bosch_radar_available=LongitudinalController.BOSCH_RADAR in choices)


def store_controller_choice(params, value, choices, CP=None):
  if type(value) not in (int, LongitudinalController) or value not in choices or not params.get_bool("IsOffroad"):
    return False
  previous = saved_controller(params, bosch_radar_available=LongitudinalController.BOSCH_RADAR in choices)
  if value == LongitudinalController.PERSONAL_PEDAL and previous != value:
    from openpilot.nrdr.car.live_gas_reset import request_reset
    request_reset(params, CP)
  # Keep old readers/downgrades consistent, but never rewrite tuning values.
  params.put_bool("HondaLiveLearningGas", value == LongitudinalController.MVL, block=True)
  if LongitudinalController.BOSCH_RADAR in choices and value in (0, 2):
    params.put_bool("HondaBoschARadar", value == LongitudinalController.BOSCH_RADAR, block=True)
  params.put(CONTROLLER_KEY, int(value), block=True)
  params.put_bool("OnroadCycleRequested", True, block=True)
  return True


def save_longitudinal_controller(state, value):
  return state.is_offroad() and store_controller_choice(
    state.params, value, longitudinal_controller_choices(state.CP, state.CP_SP, state.params), state.CP,
  )


def longitudinal_controller_label(state):
  return CONTROLLER_LABELS[longitudinal_controller_selection(state.CP, state.CP_SP, state.params)]


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
  if decode_controller(state.params.get(CONTROLLER_KEY)) is not None:
    state.params.put(CONTROLLER_KEY, -1, block=True)
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


def saved_pcm_speed_deadzone(params) -> float:
  return read_speed_deadzone(params.get(PCM_SPEED_DEADZONE_KEY))


def save_pcm_speed_deadzone(state, value) -> bool:
  selected = decode_speed_deadzone(value) if type(value) in (int, float) else None
  if selected is None or not state.is_offroad() or not mvl_pcm_deadzone_available(state.CP, state.CP_SP, state.params):
    return False
  state.params.put(PCM_SPEED_DEADZONE_KEY, selected, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True


def saved_wind_brake(params) -> bool:
  value = params.get("NrdrHondaWindBrake")
  return value if type(value) is bool else True


def wind_brake_editable(CP, CP_SP, params, *, is_offroad: bool) -> bool:
  return (LongitudinalController.PERSONAL_PEDAL in longitudinal_controller_choices(CP, CP_SP, params)
          or (is_offroad and pcm_tuning_available(CP, CP_SP, params)))


def save_pcm_choice(state, key: str, value) -> bool:
  if key == "NrdrHondaWindBrake":
    if type(value) is not bool or not wind_brake_editable(state.CP, state.CP_SP, state.params, is_offroad=state.is_offroad()):
      return False
    state.params.put_bool(key, value, block=True)
    if pcm_tuning_available(state.CP, state.CP_SP, state.params):
      state.params.put_bool("OnroadCycleRequested", True)
    return True
  if (not pcm_tuning_available(state.CP, state.CP_SP, state.params) or not state.is_offroad()
      or not tuning_write_allowed(state.params, key, CP=state.CP, CP_SP=state.CP_SP, is_offroad=state.is_offroad())):
    return False
  if key == "NrdrHondaPcmMode" and type(value) is int and value in (0, 1, 2):
    state.params.put(key, value, block=True)
  else:
    return False
  # Saving is not evidence that the startup-latched controller has changed.
  state.params.put_bool("OnroadCycleRequested", True)
  return True
