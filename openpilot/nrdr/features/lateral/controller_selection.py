"""Exact family + explicit image acknowledgement, latched before a bare drive.

Modified EPS firmware reports a family string, not a build hash. A comma marker
alone must never select a calibration. NrdrFirmwareImage records the owner's
separate confirmation, not an automatic image verification or a firmware flasher.
"""
from dataclasses import dataclass

from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile, normalize_honda_eps_firmware


@dataclass(frozen=True)
class FirmwareControllerProfile:
  name: str
  calibration: str
  firmware_image: str
  prediction_schedule: bool = False
  provisional: bool = False


CLARITY_PROFILE = FirmwareControllerProfile(
  "Clarity A020", "clarity_a020", "clarity-a020-pminus5-tracker3200-norm1650", True)
CIVIC_PROFILE = FirmwareControllerProfile(
  "Civic Bosch C020", "civic_bosch_c020", "civic-c020-targetmapd-tracker4500-norm1650")
TEG_PROFILE = FirmwareControllerProfile(
  "Civic TEG-A010 corrected PTM (provisional)", "civic_teg_a010", "civic-teg-20261016b-04147917", provisional=True)
INSIGHT_PROFILE = FirmwareControllerProfile(
  "Insight TXM-A040 corrected PTM", "insight_txm_a040", "insight-txm-20261016b-7ba37432", True)
PROFILES = {
  ("HONDA_CLARITY", "39990-TRW-A020"): CLARITY_PROFILE,
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C020"): CIVIC_PROFILE,
  ("HONDA_CIVIC", "39990-TEG-A010"): TEG_PROFILE,
  ("HONDA_INSIGHT", "39990-TXM-A040"): INSIGHT_PROFILE,
}


def _text(value) -> str:
  return value.decode("ascii", errors="replace") if isinstance(value, bytes) else str(value)


def firmware_controller_profile(CP, settings) -> FirmwareControllerProfile | None:
  if CP is None or str(CP.brand) != "honda" or CP.lateralTuning.which() != "pid" or \
     str(getattr(CP, "steerControlType", "torque")) != "torque" or \
     _text(settings.get("NrdrLateralController")) != "1" or get_honda_vgr_profile(CP) is None:
    return None
  # Reject inconsistent duplicate EPS entries rather than admitting the first match.
  eps_versions = {_text(fw.fwVersion).rstrip("\0") for fw in CP.carFw if fw.ecu == "eps"}
  if len(eps_versions) != 1:
    return None
  version = next(iter(eps_versions))
  if "," not in version:
    return None
  profile = PROFILES.get((str(CP.carFingerprint), normalize_honda_eps_firmware(version)))
  return profile if profile is not None and _text(settings.get("NrdrFirmwareImage")) == profile.firmware_image else None
