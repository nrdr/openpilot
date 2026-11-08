"""Shared native/remote tuning admission rules. Never an actuation authority."""

from functools import lru_cache

MVL_DESCRIPTION = (
  "Selects MVL longitudinal control on Honda Nidec PCM, Bosch and gas-interceptor paths. " +
  "MVL owns gas, braking and the complete Aggressive, Standard and Relaxed profiles, including following distances. " +
  "Experimental Mode remains manually selectable: OFF uses ACC, ON uses end-to-end longitudinal planning. " +
  "Only Econ retains nrdr's longer-following and gentler acceleration/jerk defaults. " +
  "Speed-limit assistance, curve-speed control and custom cruise-button increments keep their own settings. " +
  "Custom controller tuning can be saved while parked; MVL ignores it. " +
  "Legacy Kegman PCM takes precedence on supported Civics; the saved learning choice is kept. " +
  "Change while parked. Applies next drive; no device reboot."
)

SUGGESTED_DESCRIPTION = (
  "Use the November 5 lateral setup: Sunny and matched Firmware Controller/steer ratio where supported. " +
  "Tested with PopV2; your model stays unchanged. Confirm the exact modified EPS build before using firmware control. " +
  "You can adjust the applied settings while parked. Turning this off keeps your saved tuning."
)
PIF_KEYS = frozenset(
  f"Lat{term}Scale{band}" for term in "PIF" for band in ("LowSpeed", "Standard", "Highway")
) | frozenset(("HondaCenterScale", "HondaCenterBoostThreshold", "HondaCenterBoostMinSpeed",
               "NrdrLatStiction", "NrdrDeviceYawCorrection", "NrdrTuneLearner", "NrdrTuneLearnerStrength", "NrdrTuneLearnerRate"))
LONG_SCALE_KEYS = frozenset(("LongPidTuneScale", "LongPidTuneScaleAggressive", "LongPidTuneScaleStandard",
                            "LongPidTuneScaleRelaxed", "LongPidTuneScaleEcon"))
# Target selection is independent of the controller's tune/learning ownership.
CRUISE_PREFERENCE_KEYS = frozenset((
  "SmartCruiseControlVision", "SmartCruiseControlMap", "SpeedLimitMode", "SpeedLimitPolicy",
  "SpeedLimitOffsetType", "SpeedLimitValueOffset", "CustomAccIncrementsEnabled",
  "CustomAccShortPressIncrement", "CustomAccLongPressIncrement",
))
# Manual ExperimentalMode remains authoritative; automatic DEC is a conflict.
MVL_LOCK_KEYS = LONG_SCALE_KEYS | frozenset((
  "NrdrHondaPcmMode", "NrdrHondaWindBrake", "StaticFeedforwardLong", "NrdrRoenAccelerationLimits",
  "NrdrHondaFullBrakeAuthority", "HondaStoppingDecelRate", "HondaStopAccel", "HondaStoppingDecelRateLong",
  "HondaVEgoStarting", "HondaVEgoStopping", "NrdrStandstillGapExtra", "NrdrCruiseMismatchCorrection",
  "AccelBoostSP", "DynamicExperimentalControl",
))
YAW_FIXED_KEYS = PIF_KEYS | frozenset((
  "HondaTorqueLowPassFilter",
  "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
))
# The separate Legacy experiment still bypasses target extensions; this change
# only restores ordinary cruise preferences alongside MVL control.
LEGACY_PCM_LOCK_KEYS = MVL_LOCK_KEYS | CRUISE_PREFERENCE_KEYS | frozenset(("HondaLiveLearningGas", "NrdrMvlPcmDeadzone"))
RETIRED_TUNING_KEYS = frozenset((
  "NrdrExperimentalEngineBraking", "NrdrCruiseOverspeedAllowance",
  "NrdrYawDelaySchedule",
  "NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed",
  "NrdrStarPilotPid", "NrdrIncreaseOverrideTolerance", "NeuralNetworkLateralControl",
  "NrdrInterpolatedTorquePifBlend", "NrdrInterpolatedTorqueShare", "NrdrInterpolatedTorqueLatAccelFactor",
  "NrdrInterpolatedTorqueFriction", "NrdrInterpolatedTorqueFrictionStandard", "NrdrInterpolatedTorqueFrictionHighway",
  "NrdrLaneChangeMinTime", "NrdrLaneChangeEntrySrReduction", "NrdrLaneChangeEntryReturnTime",
  "NrdrLaneChangeTorqueFactor", "NrdrLaneChangeFrictionPercent",
))
SUGGESTED_LOCK_KEYS = PIF_KEYS | frozenset((
  "LaneGuidanceMode", "NrdrLateralController",
  "NrdrOptimizedLaneChanges", "LagdToggle", "LagdToggleDelay",
  "NrdrDriverOverrideThreshold", "NrdrOverrideThresholdCenterBoost", "HondaDriverAssistDuringOverride",
  "HondaOverrideFadeUpSecs", "HondaOverrideFadeDownSecs", "HondaOverrideTorqueScale",
  "HondaTorqueLowPassFilter", "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
  "HondaSteerDeltaLimiter", "HondaSteerDeltaUp", "HondaSteerDeltaDown",
))


def _enabled(params, key: str) -> bool:
  value = params.get(key)
  return str(value).strip().lower() in ("true", "1", "b'1'", "b'true'")


@lru_cache(maxsize=4)
def _stored_mvl_context(raw: bytes) -> tuple[bool, bool]:
  from opendbc.car.structs import car
  from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled

  with car.CarParams.from_bytes(raw) as cp:
    return mvl_longitudinal_enabled(cp), mvl_tuning_exempt(cp)


def mvl_tuning_exempt(CP) -> bool:
  """A known other vehicle/stock ACC must not inherit a saved Honda-mode lock."""
  brand = str(getattr(CP, "brand", "")).lower()
  return bool(brand and (brand != "honda" or not getattr(CP, "openpilotLongitudinalControl", False)))


def mvl_tuning_locked(params, CP=None) -> bool:
  """Saved ON or the startup mode owns custom tuning while driving.

  Param-only widget callers use current CarParams, then its offroad persistent
  copy. A corrupt existing CP fails closed; no CP yet does not invent a mode.
  This reports mode ownership, not whether parked preconfiguration is allowed.
  """
  from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled

  saved = _enabled(params, "HondaLiveLearningGas")
  if CP is not None and getattr(CP, "brand", ""):
    return mvl_longitudinal_enabled(CP) or (saved and not mvl_tuning_exempt(CP))
  try:
    raw = params.get("CarParams") or params.get("CarParamsPersistent")
    if raw:
      active, exempt = _stored_mvl_context(raw)
      return active or (saved and not exempt)
    return saved
  except Exception:
    return True


def tuning_write_allowed(params, key: str | None, *, firmware_prediction_schedule: bool = False,
                         CP=None, CP_SP=None, is_offroad: bool | None = None) -> bool:
  if not key:
    return True
  if key in RETIRED_TUNING_KEYS or key.startswith("NrdrNnlc"):
    return False
  # A controller's ownership of its running tune does not prevent preparing
  # another tune while parked. Persistent CP describes the previous drive.
  # Unknown road state retains the onroad guards; no saved choice is rewritten.
  parked = _enabled(params, "IsOffroad") if is_offroad is None else is_offroad is True
  if not parked:
    if key in LEGACY_PCM_LOCK_KEYS and legacy_pcm_tuning_locked(params, CP, CP_SP):
      return False
    if key in MVL_LOCK_KEYS and mvl_tuning_locked(params, CP):
      return False
  # A completed preset is a starting point, not a permanent edit lock. Keep
  # the short pending-application guard so edits cannot race the preset write.
  if (not parked and _enabled(params, "NrdrSuggestedSettings")) or _enabled(params, "NrdrHandcraftedLateralTune"):
    if key in SUGGESTED_LOCK_KEYS or key.startswith(("NrdrSteerRatio", "LaneCenter", "NrdrLatRateDamping")):
      return False
  if str(params.get("NrdrLateralController")) in ("1", "b'1'"):
    if firmware_prediction_schedule and key in ("LagdToggle", "LagdToggleDelay"):
      return False
    if key in YAW_FIXED_KEYS or key.startswith("NrdrLatRateDamping"):
      return False
  return True


def legacy_pcm_active(CP) -> bool:
  from opendbc.car.honda.values import CAR, HondaFlags

  return bool(CP is not None and getattr(CP, "brand", "") == "honda"
              and getattr(CP, "carFingerprint", "") == CAR.HONDA_CIVIC
              and getattr(CP, "flags", 0) & HondaFlags.NIDEC and not (getattr(CP, "flags", 0) & HondaFlags.BOSCH)
              and getattr(CP, "openpilotLongitudinalControl", False)
              and not (getattr(CP, "passive", False) or getattr(CP, "dashcamOnly", False))
              and getattr(CP, "flags", 0) & HondaFlags.NIDEC_PCM_LEGACY)


@lru_cache(maxsize=4)
def _stored_legacy_context(raw: bytes) -> tuple[bool, bool]:
  from opendbc.car.structs import car

  with car.CarParams.from_bytes(raw) as cp:
    return legacy_pcm_active(cp), _legacy_pcm_exempt(cp)


def _legacy_pcm_exempt(CP) -> bool:
  from opendbc.car.honda.values import CAR, HondaFlags

  return bool(getattr(CP, "brand", "") and (
    CP.brand != "honda" or getattr(CP, "carFingerprint", "") != CAR.HONDA_CIVIC
    or not (getattr(CP, "flags", 0) & HondaFlags.NIDEC) or getattr(CP, "flags", 0) & HondaFlags.BOSCH
    or not getattr(CP, "openpilotLongitudinalControl", False)
    or getattr(CP, "passive", False) or getattr(CP, "dashcamOnly", False)))


def _legacy_sp_exempt(CP_SP) -> bool:
  from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

  return bool(getattr(CP_SP, "enableGasInterceptor", False) or getattr(CP_SP, "flags", 0) & HondaFlagsSP.STOCK_LONGITUDINAL)


@lru_cache(maxsize=4)
def _stored_legacy_sp_exempt(raw: bytes) -> bool:
  from openpilot.cereal import custom

  with custom.CarParamsSP.from_bytes(raw) as cp_sp:
    return _legacy_sp_exempt(cp_sp)


def legacy_pcm_tuning_locked(params, CP=None, CP_SP=None) -> bool:
  """Saved or startup-latched Legacy ownership, separate from parked editing."""
  from openpilot.nrdr.params.nidec_pcm import decode_pcm_experiment

  saved = decode_pcm_experiment(params.get("NrdrHondaLegacyPcm")) is True
  try:
    if CP_SP is not None:
      if _legacy_sp_exempt(CP_SP):
        return False
    elif (raw_sp := params.get("CarParamsSPPersistent")) and _stored_legacy_sp_exempt(raw_sp):
      return False
    if CP is not None and getattr(CP, "brand", ""):
      return legacy_pcm_active(CP) or (saved and not _legacy_pcm_exempt(CP))
    raw = params.get("CarParams") or params.get("CarParamsPersistent")
    if raw:
      active, exempt = _stored_legacy_context(raw)
      return active or (saved and not exempt)
    return saved
  except Exception:
    return True


def reset_learning_scales(params) -> None:
  """Compatibility hook: full MVL ignores custom scales without erasing them.

  Older generic UI/defaults callers still invoke this hook. Runtime ownership
  replaces the old learner-only unity reset; returning to custom mode restores
  the user's existing saved tune after restart.
  """
