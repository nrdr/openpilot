"""Shared native/remote tuning admission rules. No vehicle actuation or I/O."""

SUGGESTED_DESCRIPTION = (
  "Last Road Tested: October 1, 2026, with PopV2 Model. Your mileage may vary. "
  "Turning back to OFF will preserve these settings and unlock tuning menus."
)
PIF_KEYS = frozenset(
  f"Lat{term}Scale{band}" for term in "PIF" for band in ("LowSpeed", "Standard", "Highway")
) | frozenset(("HondaCenterScale", "HondaCenterBoostThreshold", "HondaCenterBoostMinSpeed",
               "NrdrLatStiction", "NrdrDeviceYawCorrection", "NrdrTuneLearner", "NrdrTuneLearnerStrength", "NrdrTuneLearnerRate"))
LONG_SCALE_KEYS = frozenset(("LongPidTuneScale", "LongPidTuneScaleAggressive", "LongPidTuneScaleStandard",
                            "LongPidTuneScaleRelaxed", "LongPidTuneScaleEcon"))
YAW_FIXED_KEYS = PIF_KEYS | frozenset((
  "HondaTorqueLowPassFilter",
  "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
))
RETIRED_TUNING_KEYS = frozenset((
  "NrdrYawDelaySchedule",
  "NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed",
  "NrdrStarPilotPid", "NrdrIncreaseOverrideTolerance", "NeuralNetworkLateralControl",
  "NrdrInterpolatedTorquePifBlend", "NrdrInterpolatedTorqueShare", "NrdrInterpolatedTorqueLatAccelFactor",
  "NrdrInterpolatedTorqueFriction", "NrdrInterpolatedTorqueFrictionStandard", "NrdrInterpolatedTorqueFrictionHighway",
  "NrdrLaneChangeMinTime", "NrdrLaneChangeEntrySrReduction", "NrdrLaneChangeEntryReturnTime",
  "NrdrLaneChangeTorqueFactor", "NrdrLaneChangeFrictionPercent",
))
SUGGESTED_LOCK_KEYS = PIF_KEYS | frozenset((
  "NrdrOptimizedLaneChanges", "LagdToggle", "LagdToggleDelay",
  "NrdrDriverOverrideThreshold", "NrdrOverrideThresholdCenterBoost", "HondaDriverAssistDuringOverride",
  "HondaOverrideFadeUpSecs", "HondaOverrideFadeDownSecs", "HondaOverrideTorqueScale",
  "HondaTorqueLowPassFilter", "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
  "HondaSteerDeltaLimiter", "HondaSteerDeltaUp", "HondaSteerDeltaDown",
))


def _enabled(params, key: str) -> bool:
  value = params.get(key)
  return str(value).strip().lower() in ("true", "1", "b'1'", "b'true'")


def tuning_write_allowed(params, key: str | None) -> bool:
  if not key:
    return True
  if key in RETIRED_TUNING_KEYS or key.startswith("NrdrNnlc"):
    return False
  if key in LONG_SCALE_KEYS and _enabled(params, "HondaLiveLearningGas"):
    return False
  if _enabled(params, "NrdrSuggestedSettings") or _enabled(params, "NrdrHandcraftedLateralTune"):
    if key in SUGGESTED_LOCK_KEYS or key.startswith(("NrdrSteerRatio", "LaneCenter", "NrdrLatRateDamping")):
      return False
  if str(params.get("NrdrLateralController")) in ("1", "b'1'"):
    if key in YAW_FIXED_KEYS or key.startswith("NrdrLatRateDamping"):
      return False
  return True


def reset_learning_scales(params) -> None:
  """Called by both settings writers; runtime independently forces unity too."""
  if _enabled(params, "HondaLiveLearningGas"):
    for key in sorted(LONG_SCALE_KEYS):
      params.put(key, 100, block=True)
