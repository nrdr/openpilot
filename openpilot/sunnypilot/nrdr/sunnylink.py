from pathlib import Path

UNREGISTERED = "UnregisteredDevice"
ONROAD_BLOCKED_PARAMS = {
  "LaneCentering",
  "LaneCenteringE2EAuthority",
  "LaneCenteringMinSpeed",
  "LaneCenteringPauseOnSignal",
  "LaneCenterOffset",
  "LongitudinalPersonality",
  "NrdrHandcraftedLateralTune",
}

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
  from openpilot.common.hardware.hw import Paths
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
  if onroad and key in ONROAD_BLOCKED_PARAMS:
    return False
  if key == "NrdrHandcraftedLateralTune":
    # A false write lets the user cancel an existing command. Enabling is
    # admitted only when current CP/CP_SP and any selected platform agree that
    # this exact vehicle has a reviewed profile. None is fail-closed.
    return requested_bool is False or (
      requested_bool is True and handcrafted_profile_available is True
    )
  if key in HONDA_TUNING_WRITE_KEYS:
    return honda_tuning_available is True
  return True


def inject_car_tune_details(schema: dict, walk) -> None:
  from openpilot.common.params import Params, UnknownKeyName
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
