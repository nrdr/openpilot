"""Drive-latched firmware control, with exact EPS-family admission.

Firmware version strings identify the family, not the contents of a modified image.
The owner must still confirm the flashed build. TEG-A010 runs its own calibration for the corrected PTM
build (command row 3; rows 2 and 3 make the same command there), with R6 and load measured on one
car's telemetry, and driven on that build (owner's route 0000013d, 2026-10-17). It is never a
generic Honda fallback. Insight TXM-A040 runs its corrected PTM build's calibration, which has been driven.
The corrected builds of the C120, TGG-A120, A030 and both CR-V images have provisional starting calibrations.
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
  # The corrected PTM build the calibration models (RWD SHA-256 prefix). Older builds report the same EPS version,
  # so admission cannot check it; it is shown and logged so the owner can.
  required_rwd: str = ""


CLARITY_PROFILE = FirmwareControllerProfile("Clarity A020", "clarity_a020", prediction_schedule=True)
CIVIC_PROFILE = FirmwareControllerProfile("Civic Bosch C020", "civic_bosch_c020", prediction_schedule=True)
TEG_PROFILE = FirmwareControllerProfile(
  "Civic TEG-A010 corrected PTM, row 3", "civic_teg_a010", prediction_schedule=True, required_rwd="04147917",
)
INSIGHT_PROFILE = FirmwareControllerProfile(
  "Insight TXM-A040 corrected PTM", "insight_txm_a040", prediction_schedule=True, required_rwd="7ba37432",
)
# Corrected-PTM (revision b) starting calibrations: firmware read from each image, the vehicle side carried from
# the nearest measured car until its owner's drives measure it. The Civics take that car's delay schedule too (the
# A030 the TEG's, the C120 and TGG the C020's); the CR-Vs keep live/manual delay until a CR-V drive is measured.
C120_PROFILE = FirmwareControllerProfile(
  "Civic Bosch TBA-C120 corrected PTM (starting calibration)", "civic_tba_c120", prediction_schedule=True, provisional=True, required_rwd="9261b8db",
)
TGG_PROFILE = FirmwareControllerProfile(
  "Civic TGG-A120 corrected PTM (starting calibration)", "civic_tgg_a120", prediction_schedule=True, provisional=True, required_rwd="6640806d",
)
A030_PROFILE = FirmwareControllerProfile(
  "Civic TBA-A030 corrected PTM (starting calibration)", "civic_tba_a030", prediction_schedule=True, provisional=True, required_rwd="55c37266",
)
CRV_A040_PROFILE = FirmwareControllerProfile(
  "CR-V TLA-A040 corrected PTM (starting calibration)", "crv_tla_a040", provisional=True, required_rwd="2e6a8802",
)
CRV_A220_PROFILE = FirmwareControllerProfile(
  "CR-V TLA-A220 corrected PTM (starting calibration)", "crv_tla_a220", provisional=True, required_rwd="2c992997",
)
_PROFILES = {
  ("HONDA_CLARITY", "39990-TRW-A020"): CLARITY_PROFILE,
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C020"): CIVIC_PROFILE,
  ("HONDA_CIVIC", "39990-TEG-A010"): TEG_PROFILE,
  ("HONDA_INSIGHT", "39990-TXM-A040"): INSIGHT_PROFILE,
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C120"): C120_PROFILE,
  ("HONDA_CIVIC_BOSCH", "39990-TGG-A120"): TGG_PROFILE,
  ("HONDA_CIVIC", "39990-TBA-A030"): A030_PROFILE,
  ("HONDA_CRV_5G", "39990-TLA-A040"): CRV_A040_PROFILE,
  ("HONDA_CRV_5G", "39990-TLA-A220"): CRV_A220_PROFILE,
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
