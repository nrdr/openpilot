from pathlib import Path

from openpilot.common.params import Params, UnknownKeyName
from openpilot.common.hardware.hw import Paths


UNREGISTERED = "UnregisteredDevice"
ONROAD_WRITE_BLOCKLIST = frozenset((
  "LaneCentering",
  "LaneCenteringE2EAuthority",
  "LaneCenteringMinSpeed",
  "LaneCenteringPauseOnSignal",
  "LaneCenteringStrength",
  "LaneCenterOffset",
  "LongitudinalPersonality",
  "NrdrHandcraftedLateralTune",
))

# These controls are surfaced only for an exact, confirmed Honda CP. Keeping
# the server-side set co-located with the admission policy prevents a stale or
# custom remote client from bypassing the vehicle-aware UI.
HONDA_TUNING_WRITE_KEYS = frozenset((
  # Controller Tuning Dungeon.
  "NrdrInterpolatedTorquePifBlend",
  "NrdrInterpolatedTorqueShare",
  "NrdrInterpolatedTorqueLatAccelFactor",
  "NrdrInterpolatedTorqueFriction",
  "NrdrInterpolatedTorqueFrictionStandard",
  "NrdrInterpolatedTorqueFrictionHighway",
  "NrdrStarPilotPid",
  "LatPScaleLowSpeed",
  "LatIScaleLowSpeed",
  "LatFScaleLowSpeed",
  "LatPScaleStandard",
  "LatIScaleStandard",
  "LatFScaleStandard",
  "LatPScaleHighway",
  "LatIScaleHighway",
  "LatFScaleHighway",
  "NrdrLatRateDamping",
  "NrdrLatRateDampingFadeSpeed",
  "HondaCenterScale",
  "HondaCenterBoostThreshold",
  "HondaCenterBoostMinSpeed",
  "NrdrLatStiction",
  "NrdrNnlcEnabled",
  "NrdrNnlcActivationSpeed",
  "NrdrNnlcKpGain",
  "NrdrNnlcKfGain",
  "NrdrNnlcKiGain",
  # Steer ratio, override, and steering filters.
  "NrdrSteerRatioMode",
  "NrdrSteerRatioManualCenter",
  "NrdrSteerRatioManualFinal",
  "NrdrIncreaseOverrideTolerance",
  "NrdrDriverOverrideThreshold",
  "NrdrOverrideThresholdCenterBoost",
  "HondaDriverAssistDuringOverride",
  "HondaOverrideFadeDownSecs",
  "HondaOverrideFadeUpSecs",
  "HondaOverrideTorqueScale",
  "HondaTorqueLowPassFilter",
  "HondaLpfTauLowSpeed",
  "HondaLpfTauStandard",
  "HondaLpfTauHighway",
  "HondaSteerDeltaLimiter",
  "HondaSteerDeltaUp",
  "HondaSteerDeltaDown",
  # Special.
  "HondaInjectionTest",
  "HondaAltDashboardSpeed",
  "HondaAltDashboardDistance",
  "NrdrClearDashFaults",
  "HondaSpoofCameraMessages",
  "NrdrCruiseButtonSubMode",
  "NrdrCruiseButtonSubModeSecs",
))


def _identity_path() -> Path:
  return Path(Paths.persist_root()) / "comma" / "sunnylink_dongle_id"


def restore_dongle_id(params, dongle_id):
  if dongle_id not in (None, UNREGISTERED):
    return dongle_id
  try:
    restored = _identity_path().read_text().strip()
    if restored:
      params.put("SunnylinkDongleId", restored, block=True)
      return restored
  except Exception:
    pass
  return dongle_id


def persist_dongle_id(dongle_id) -> None:
  if not dongle_id or dongle_id == UNREGISTERED:
    return
  try:
    path = _identity_path()
    if not path.exists():
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(dongle_id)
  except Exception:
    pass


def allow_param_write(key: str, onroad: bool, *, handcrafted_profile_available: bool | None = None,
                      honda_tuning_available: bool | None = None,
                      requested_bool: bool | None = None) -> bool:
  if key == "NrdrHandcraftedLateralRequest":
    return False
  if onroad and key in ONROAD_WRITE_BLOCKLIST:
    return False
  if key == "NrdrHandcraftedLateralTune":
    # A false write lets the user cancel an existing command. Enabling is
    # admitted only when current CP/CP_SP and any selected platform agree that
    # this exact vehicle can consume the preset. None is fail-closed. The
    # caller must bind an admitted True request through the profile API.
    return requested_bool is False or (
      requested_bool is True and handcrafted_profile_available is True
    )
  if key in HONDA_TUNING_WRITE_KEYS:
    return honda_tuning_available is True
  return True


def request_stored_handcrafted_lateral_profile(params) -> bool:
  """Bind a remote opt-in to device-owned vehicle data, never client payloads."""
  from opendbc.car.structs import car
  from openpilot.cereal import custom, messaging
  from openpilot.nrdr.params import request_handcrafted_lateral_profile

  cp_bytes = params.get("CarParamsPersistent")
  if not cp_bytes:
    return False
  CP = messaging.log_from_bytes(cp_bytes, car.CarParams)
  cp_sp_bytes = params.get("CarParamsSPPersistent")
  CP_SP = messaging.log_from_bytes(cp_sp_bytes, custom.CarParamsSP) if cp_sp_bytes else None
  return request_handcrafted_lateral_profile(CP, CP_SP, params)


def inject_car_tune_details(schema: dict, walk) -> None:
  try:
    details = Params().get("NrdrCarTuneDetails")
  except UnknownKeyName:
    return
  if isinstance(details, bytes):
    details = details.decode("utf-8", "replace")
  if not details:
    return

  def visitor(item: dict) -> None:
    if item.get("key") == "NrdrCarTuneInfo":
      item["details"] = str(details)

  walk(schema, visitor)


__all__ = (
  "HONDA_TUNING_WRITE_KEYS",
  "ONROAD_WRITE_BLOCKLIST",
  "UNREGISTERED",
  "_identity_path",
  "allow_param_write",
  "inject_car_tune_details",
  "persist_dongle_id",
  "request_stored_handcrafted_lateral_profile",
  "restore_dongle_id",
)
