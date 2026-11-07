"""Presentation eligibility and saved choices; never an actuation authority."""
from opendbc.car.honda.values import CAR, HONDA_BOSCH, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed, legacy_pcm_active, legacy_pcm_tuning_locked
from openpilot.nrdr.params.nidec_pcm import PCM_EXPERIMENTS
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled
from openpilot.nrdr.params.mvl_pcm_deadzone import MVL_PCM_DEADZONE_VALUES


def live_gas_available(CP, CP_SP, params) -> bool:
  present, fingerprint, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(CP, fingerprint, brand, selection_present=present)
  return bool(identity is not None and identity[1] == "honda" and identity[0] in CAR
              and getattr(CP, "openpilotLongitudinalControl", False)
              and CP_SP is not None
              and not (getattr(CP_SP, "flags", 0) & HondaFlagsSP.STOCK_LONGITUDINAL)
              and not legacy_pcm_tuning_locked(params, CP, CP_SP))


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
              and getattr(CP, "openpilotLongitudinalControl", False)
              and not getattr(CP_SP, "enableGasInterceptor", True)
              and not (getattr(CP_SP, "flags", 0) & HondaFlagsSP.STOCK_LONGITUDINAL))


def saved_pcm_mode(params) -> int:
  value = params.get("NrdrHondaPcmMode")
  # Typed Params returns an int. Reject bool and malformed/stale values as Off.
  return value if type(value) is int and value in (0, 1, 2) else 0


def pcm_experiments_available(CP, CP_SP, params) -> bool:
  return (pcm_tuning_available(CP, CP_SP, params) and CP.carFingerprint == CAR.HONDA_CIVIC
          and bool(CP.flags & HondaFlags.NIDEC) and not (CP.flags & HondaFlags.BOSCH)
          and not (getattr(CP, "passive", False) or getattr(CP, "dashcamOnly", False)))


def saved_pcm_experiment(params, key: str) -> bool:
  return key in PCM_EXPERIMENTS and params.get(key) is True


def pcm_experiment_active(CP, key: str) -> bool:
  flag = {"NrdrHondaPcmFixedCruise": HondaFlags.NIDEC_PCM_FIXED_CRUISE,
          "NrdrHondaLegacyPcm": HondaFlags.NIDEC_PCM_LEGACY}.get(key, 0)
  return bool(CP is not None and getattr(CP, "brand", "") == "honda"
              and getattr(CP, "carFingerprint", "") == CAR.HONDA_CIVIC
              and getattr(CP, "flags", 0) & HondaFlags.NIDEC and not (getattr(CP, "flags", 0) & HondaFlags.BOSCH)
              and not (getattr(CP, "passive", False) or getattr(CP, "dashcamOnly", False))
              and getattr(CP, "openpilotLongitudinalControl", False) and getattr(CP, "flags", 0) & flag)


def pcm_experiment_status(CP, CP_SP, params, key: str, *, compact: bool = False) -> str:
  if not pcm_experiments_available(CP, CP_SP, params):
    return "Unavailable"
  active, saved = pcm_experiment_active(CP, key), saved_pcm_experiment(params, key)
  running, selected = ("On" if active else "Off"), ("On" if saved else "Off")
  if compact:
    return running if active == saved else f"{running} → {selected}"
  return f"Running: {running}." if active == saved else f"Running: {running}. Saved: {selected}; restart required."


def save_pcm_experiment(state, key: str, value) -> bool:
  # These two independent choices remain available while MVL or Legacy is active.
  if (key not in PCM_EXPERIMENTS or type(value) is not bool or not state.is_offroad()
      or not pcm_experiments_available(state.CP, state.CP_SP, state.params)):
    return False
  state.params.put_bool(key, value, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True


def live_gas_status(CP, params, CP_SP=None) -> str:
  selected = params.get_bool("HondaLiveLearningGas")
  legacy_locked = legacy_pcm_tuning_locked(params, CP, CP_SP)
  legacy_selected = saved_pcm_experiment(params, "NrdrHondaLegacyPcm") and legacy_locked
  if legacy_pcm_active(CP) and legacy_locked:
    if not legacy_selected:
      return "Legacy active\nMVL pending" if selected else "Legacy active\nOFF after restart"
    return "Legacy active\nMVL saved" if selected else "Legacy active"
  if mvl_longitudinal_enabled(CP):
    if legacy_selected:
      return "MVL active\nLegacy pending"
    return "MVL active" if selected else "MVL active\nOFF after restart"
  if selected and legacy_selected:
    return "MVL saved\nLegacy pending"
  return "MVL selected\nRestart required" if selected else "MVL inactive"


def mvl_pcm_deadzone_available(CP, CP_SP, params) -> bool:
  return (pcm_tuning_available(CP, CP_SP, params) and CP.carFingerprint == CAR.HONDA_CIVIC
          and not legacy_pcm_tuning_locked(params, CP, CP_SP)
          and (mvl_longitudinal_enabled(CP) or params.get_bool("HondaLiveLearningGas")))


def saved_mvl_pcm_deadzone(params) -> int:
  value = params.get("NrdrMvlPcmDeadzone")
  return value if type(value) is int and value in MVL_PCM_DEADZONE_VALUES else 0


def save_mvl_pcm_deadzone(state, value) -> bool:
  # Deliberate MVL-only exception; custom PCM/wind/other tuning stays locked.
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
      or not tuning_write_allowed(state.params, key, CP=state.CP, CP_SP=state.CP_SP)):
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
