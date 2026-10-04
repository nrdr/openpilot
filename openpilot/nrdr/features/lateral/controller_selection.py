"""Explicit controller selection, admitted only for the validated EPS family."""
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile


def yaw_controller_available(CP, CP_SP) -> bool:
  return bool(CP is not None and str(CP.brand) == "honda" and str(CP.carFingerprint) == "HONDA_CLARITY"
              and getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value
              and get_honda_vgr_profile(CP) is not None and CP.lateralTuning.which() == "pid")


def firmware_controller_selected(params, CP, CP_SP) -> bool:
  """Use the admitted selection, not a stale selector left over from another car."""
  return str(params.get("NrdrLateralController")) in ("1", "b'1'") and yaw_controller_available(CP, CP_SP)


def firmware_controller_for_model(params, CP) -> bool:
  """Resolve once per drive, without waiting on Honda-only data for other cars."""
  if CP is None or str(CP.brand) != "honda" or str(CP.carFingerprint) != "HONDA_CLARITY" or \
     str(params.get("NrdrLateralController")) not in ("1", "b'1'"):
    return False
  from openpilot.cereal import custom, messaging
  CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
  return firmware_controller_selected(params, CP, CP_SP)
