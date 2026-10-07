"""Drive-latched firmware control, with exact EPS-family admission.

Firmware version strings identify the family, not the contents of a modified image.
The owner must still confirm the flashed build. TEG-A010 is an explicit, unvalidated
owner-requested C020 calibration fallback, never a generic Honda fallback.
"""
from dataclasses import dataclass

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile, normalize_honda_eps_firmware


@dataclass(frozen=True)
class FirmwareControllerProfile:
  name: str
  calibration: str
  prediction_schedule: bool = False
  provisional: bool = False


CLARITY_PROFILE = FirmwareControllerProfile("Clarity A020", "clarity_a020", prediction_schedule=True)
CIVIC_PROFILE = FirmwareControllerProfile("Civic Bosch C020", "civic_bosch_c020")
TEG_PLACEHOLDER_PROFILE = FirmwareControllerProfile(
  "Civic TEG-A010 / Bosch C020 placeholder (not road-validated)", "civic_bosch_c020", provisional=True,
)
_PROFILES = {
  ("HONDA_CLARITY", "39990-TRW-A020"): CLARITY_PROFILE,
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C020"): CIVIC_PROFILE,
  ("HONDA_CIVIC", "39990-TEG-A010"): TEG_PLACEHOLDER_PROFILE,
}


def _firmware_family(CP) -> FirmwareControllerProfile | None:
  if CP is None or str(getattr(CP, "brand", "")) != "honda":
    return None
  for firmware in getattr(CP, "carFw", ()):
    if firmware.ecu == "eps":
      profile = _PROFILES.get((str(CP.carFingerprint), normalize_honda_eps_firmware(firmware.fwVersion)))
      if profile is not None:
        return profile
  return None


def firmware_controller_profile(CP, CP_SP) -> FirmwareControllerProfile | None:
  profile = _firmware_family(CP)
  if profile is not None and getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value and \
     get_honda_vgr_profile(CP) is not None and CP.lateralTuning.which() == "pid":
    return profile
  return None


def yaw_controller_available(CP, CP_SP) -> bool:
  # Keep the legacy wire/call-site name; this controller is not a live yaw loop.
  return firmware_controller_profile(CP, CP_SP) is not None


def firmware_controller_selected(params, CP, CP_SP) -> bool:
  """Use the admitted selection, not a stale selector left over from another car."""
  return str(params.get("NrdrLateralController")) in ("1", "b'1'") and yaw_controller_available(CP, CP_SP)


def firmware_controller_profile_for_model(params, CP) -> FirmwareControllerProfile | None:
  """Resolve once per drive, without waiting on Honda-only data for other cars."""
  if _firmware_family(CP) is None or \
     str(params.get("NrdrLateralController")) not in ("1", "b'1'"):
    return None
  from openpilot.cereal import custom, messaging
  CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
  return firmware_controller_profile(CP, CP_SP)


def firmware_controller_for_model(params, CP) -> bool:
  return firmware_controller_profile_for_model(params, CP) is not None
