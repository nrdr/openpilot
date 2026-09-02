"""Authoritative registry metadata for parameters introduced or overridden by NRDR.

This module deliberately depends only on the Python standard library.  It is
the source for generated Python key names and the C++ registry include; it is
not a Params client and is safe to use from build and validation tooling.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ParamType(StrEnum):
  BOOL = "BOOL"
  BYTES = "BYTES"
  FLOAT = "FLOAT"
  INT = "INT"
  JSON = "JSON"
  STRING = "STRING"


class ParamFlag(StrEnum):
  PERSISTENT = "PERSISTENT"
  CLEAR_ON_MANAGER_START = "CLEAR_ON_MANAGER_START"
  CLEAR_ON_OFFROAD_TRANSITION = "CLEAR_ON_OFFROAD_TRANSITION"
  BACKUP = "BACKUP"
  DONT_LOG = "DONT_LOG"


class RegistryAction(StrEnum):
  ADDED = "added"
  OVERRIDE = "override"


class ParamLifecycle(StrEnum):
  SETTING = "setting"
  STATE = "state"
  TRANSIENT = "transient"
  COMMAND = "command"
  STATUS = "status"
  TOMBSTONE = "tombstone"


class ParamOwner(StrEnum):
  SYSTEM = "system"
  DEVICE = "device"
  REMOTE = "remote"
  MODEL = "model"
  LATERAL = "lateral"
  LONGITUDINAL = "longitudinal"
  HONDA = "honda"
  DIAGNOSTICS = "diagnostics"


@dataclass(frozen=True, slots=True)
class ParamSpec:
  key: str
  param_type: ParamType
  flags: tuple[ParamFlag, ...]
  default: str | None = None
  lifecycle: ParamLifecycle = ParamLifecycle.SETTING
  owner: ParamOwner = ParamOwner.SYSTEM
  action: RegistryAction = RegistryAction.ADDED

  @property
  def cpp_attributes(self) -> str:
    flags = " | ".join(flag.value for flag in self.flags)
    attributes = f"{flags}, {self.param_type.value}"
    if self.default is not None:
      attributes += f', "{self.default}"'
    return attributes


P = ParamFlag.PERSISTENT
B = ParamFlag.BACKUP
M = ParamFlag.CLEAR_ON_MANAGER_START
O = ParamFlag.CLEAR_ON_OFFROAD_TRANSITION
D = ParamFlag.DONT_LOG
PB = (P, B)


def _added(key: str, param_type: ParamType, flags: tuple[ParamFlag, ...], default: str | None = None,
           lifecycle: ParamLifecycle = ParamLifecycle.SETTING,
           owner: ParamOwner = ParamOwner.SYSTEM) -> ParamSpec:
  return ParamSpec(key, param_type, flags, default, lifecycle, owner)


# Order is stable and intentionally follows the original registry delta.  C++
# map order is not semantically relevant, but keeping it stable makes generated
# changes reviewable and preserves every default lexeme exactly (for example,
# "18.50" must not be normalized to "18.5").
PARAM_SPECS: tuple[ParamSpec, ...] = (
  ParamSpec("DisablePowerDown", ParamType.BOOL, PB, "1", ParamLifecycle.SETTING,
            ParamOwner.SYSTEM, RegistryAction.OVERRIDE),

  _added("HondaBoschARadar", ParamType.BOOL, (P,), "1", owner=ParamOwner.HONDA),
  _added("Offroad_NeosUpdate", ParamType.JSON, (M,), lifecycle=ParamLifecycle.STATUS),
  _added("RecordAudioFeedback", ParamType.BOOL, PB, "0", owner=ParamOwner.DEVICE),
  _added("RemoteAccessPinEnabled", ParamType.BOOL, (P,), lifecycle=ParamLifecycle.STATE, owner=ParamOwner.REMOTE),
  _added("RemoteAccessPinSalt", ParamType.BYTES, (P, D), lifecycle=ParamLifecycle.STATE, owner=ParamOwner.REMOTE),
  _added("RemoteAccessPinHash", ParamType.BYTES, (P, D), lifecycle=ParamLifecycle.STATE, owner=ParamOwner.REMOTE),
  _added("RemoteAccessPinIterations", ParamType.INT, (P,), "150000", ParamLifecycle.STATE, ParamOwner.REMOTE),
  _added("LiveViewEnabled", ParamType.BOOL, PB, "1", owner=ParamOwner.REMOTE),
  _added("LiveView", ParamType.BOOL, (M, O), lifecycle=ParamLifecycle.TRANSIENT, owner=ParamOwner.REMOTE),
  _added("LatPScaleLowSpeed", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatPScaleStandard", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatPScaleHighway", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatIScaleLowSpeed", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatIScaleStandard", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatIScaleHighway", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatFScaleLowSpeed", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatFScaleStandard", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LatFScaleHighway", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("LongPidTuneScale", ParamType.INT, PB, "100", owner=ParamOwner.LONGITUDINAL),
  _added("LongPidTuneScaleAggressive", ParamType.INT, PB, "200", owner=ParamOwner.LONGITUDINAL),
  _added("LongPidTuneScaleStandard", ParamType.INT, PB, "100", owner=ParamOwner.LONGITUDINAL),
  _added("LongPidTuneScaleRelaxed", ParamType.INT, PB, "80", owner=ParamOwner.LONGITUDINAL),
  _added("LongPidTuneScaleEcon", ParamType.INT, PB, "50", owner=ParamOwner.LONGITUDINAL),
  _added("NrdrCruiseMismatchCorrection", ParamType.FLOAT, PB, "100", owner=ParamOwner.LONGITUDINAL),
  _added("NrdrCruiseOverspeedAllowance", ParamType.INT, PB, "0", owner=ParamOwner.LONGITUDINAL),
  _added("HondaCenterScale", ParamType.FLOAT, PB, "0.5", owner=ParamOwner.HONDA),
  _added("HondaPidFriction", ParamType.FLOAT, PB, "0.0", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
  _added("NrdrInterpolatedTorquePifBlend", ParamType.BOOL, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrInterpolatedTorqueShare", ParamType.INT, PB, "50", owner=ParamOwner.LATERAL),
  _added("NrdrInterpolatedTorqueLatAccelFactor", ParamType.FLOAT, PB, "5.0", owner=ParamOwner.LATERAL),
  _added("NrdrInterpolatedTorqueFriction", ParamType.FLOAT, PB, "0.12", owner=ParamOwner.LATERAL),
  _added("NrdrInterpolatedTorqueFrictionStandard", ParamType.FLOAT, PB, "0.10", owner=ParamOwner.LATERAL),
  _added("NrdrInterpolatedTorqueFrictionHighway", ParamType.FLOAT, PB, "0.06", owner=ParamOwner.LATERAL),
  _added("HondaNotchEnabled", ParamType.BOOL, PB, "0", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
  _added("HondaNotchFreq", ParamType.FLOAT, PB, "7.5", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
  _added("HondaNotchQ", ParamType.FLOAT, PB, "1.5", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
  _added("NrdrSteerRatioMode", ParamType.INT, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrSteerRatioManualCenter", ParamType.FLOAT, PB, "15.38", owner=ParamOwner.LATERAL),
  _added("NrdrSteerRatioManualFinal", ParamType.FLOAT, PB, "10.93", owner=ParamOwner.LATERAL),
  # Retained so startup can perform a one-time migration and older builds can
  # still boot after a downgrade. Runtime and UI code must not consume these.
  _added("NrdrLearnSteerRatio", ParamType.BOOL, PB, "0", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioCenterClarity", ParamType.FLOAT, PB, "18.50", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOuterClarity", ParamType.FLOAT, PB, "12.72", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioCenterCivic", ParamType.FLOAT, PB, "17.24", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOuterCivic", ParamType.FLOAT, PB, "10.93", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioCenterAccord", ParamType.FLOAT, PB, "18.31", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOuterAccord", ParamType.FLOAT, PB, "11.82", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioCenterCrv5g", ParamType.FLOAT, PB, "17.94", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOuterCrv5g", ParamType.FLOAT, PB, "12.30", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioCenterInsight", ParamType.FLOAT, PB, "16.82", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOuterInsight", ParamType.FLOAT, PB, "12.58", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  # Retained with its exact registry metadata/default for downgrade compatibility;
  # model-artifact policy replaced this manual setting in profile v14.
  _added("NrdrLegacyDualBpSteerRatio", ParamType.BOOL, PB, "1", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrLaneChangeEndpointSteerRatio", ParamType.BOOL, PB, "1", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioOffset", ParamType.FLOAT, PB, "0.0", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioMin", ParamType.FLOAT, PB, "16.84", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrSteerRatioMax", ParamType.FLOAT, PB, "12.74", ParamLifecycle.TOMBSTONE, ParamOwner.LATERAL),
  _added("NrdrLearnStiffness", ParamType.BOOL, PB, "1", owner=ParamOwner.LATERAL),
  _added("NrdrLearnAngleOffset", ParamType.BOOL, PB, "1", owner=ParamOwner.LATERAL),
  _added("HondaStoppingDecelRate", ParamType.INT, PB, "30", owner=ParamOwner.HONDA),
  _added("NrdrIncreaseOverrideTolerance", ParamType.BOOL, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrDriverOverrideThreshold", ParamType.INT, PB, "1400", owner=ParamOwner.LATERAL),
  _added("NrdrOverrideThresholdCenterBoost", ParamType.INT, PB, "1000", owner=ParamOwner.LATERAL),
  _added("HondaOverrideFadeDownSecs", ParamType.FLOAT, PB, "0.1", owner=ParamOwner.HONDA),
  _added("HondaOverrideFadeUpSecs", ParamType.FLOAT, PB, "0.1", owner=ParamOwner.HONDA),
  _added("HondaOverrideTorqueScale", ParamType.INT, PB, "0", owner=ParamOwner.HONDA),
  _added("HondaDriverAssistDuringOverride", ParamType.BOOL, PB, "1", owner=ParamOwner.HONDA),
  _added("HondaLiveLearningGas", ParamType.BOOL, PB, owner=ParamOwner.HONDA),
  _added("HondaTorqueLowPassFilter", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("HondaLpfTauLowSpeed", ParamType.FLOAT, PB, "0.1", owner=ParamOwner.HONDA),
  _added("HondaLpfTauStandard", ParamType.FLOAT, PB, "0.1", owner=ParamOwner.HONDA),
  _added("HondaLpfTauHighway", ParamType.FLOAT, PB, "0.05", owner=ParamOwner.HONDA),
  _added("NrdrFirstRunSetupDone", ParamType.BOOL, PB, "0", ParamLifecycle.STATE, ParamOwner.SYSTEM),
  _added("NrdrAutoSelectModel", ParamType.BOOL, PB, "0", owner=ParamOwner.MODEL),
  _added("StaticFeedforwardLong", ParamType.BOOL, PB, "1", owner=ParamOwner.LONGITUDINAL),
  _added("NrdrHondaEcuMatchedLong", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("NrdrHondaFullBrakeAuthority", ParamType.BOOL, PB, "1", owner=ParamOwner.HONDA),
  _added("NrdrRoenAccelerationLimits", ParamType.BOOL, PB, "1", owner=ParamOwner.HONDA),
  _added("HondaInjectionTest", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("HondaAltDashboardSpeed", ParamType.INT, PB, "0", owner=ParamOwner.HONDA),
  _added("HondaAltDashboardDistance", ParamType.INT, PB, "0", owner=ParamOwner.HONDA),
  _added("NrdrHondaDashVariantB", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("NrdrClearDashFaults", ParamType.BOOL, PB, "1", owner=ParamOwner.HONDA),
  _added("HondaSpoofCameraMessages", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("NrdrCruiseButtonSubMode", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("NrdrCruiseButtonSubModeSecs", ParamType.INT, PB, "15", owner=ParamOwner.HONDA),
  _added("NrdrHudSubModeUntil", ParamType.FLOAT, (M,), "0", ParamLifecycle.TRANSIENT, ParamOwner.HONDA),
  _added("NrdrRemoteForceUpdate", ParamType.BOOL, (M,), "0", ParamLifecycle.COMMAND, ParamOwner.REMOTE),
  _added("NrdrRemoteTuneScan", ParamType.BOOL, (M,), "0", ParamLifecycle.COMMAND, ParamOwner.REMOTE),
  _added("NrdrRemoteStatus", ParamType.STRING, (M,), "idle", ParamLifecycle.STATUS, ParamOwner.REMOTE),
  _added("NrdrTuneReportSummary", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarTuneInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarTuneDetails", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarControllerInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarHandcraftedInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarPidLowInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarPidMidInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarPidHighInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarDampingInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarCenterInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarNnlcInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarSteerRatioInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarLearningInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrCarHelpersInfo", ParamType.STRING, (P,), lifecycle=ParamLifecycle.STATUS, owner=ParamOwner.DIAGNOSTICS),
  _added("NrdrStarPilotPid", ParamType.BOOL, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrHandcraftedLateralTune", ParamType.BOOL, PB, "0", ParamLifecycle.COMMAND, ParamOwner.LATERAL),
  _added("NrdrNnlcEnabled", ParamType.BOOL, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrNnlcActivationSpeed", ParamType.INT, PB, "30", owner=ParamOwner.LATERAL),
  _added("NrdrNnlcKpGain", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("NrdrNnlcKfGain", ParamType.INT, PB, "50", owner=ParamOwner.LATERAL),
  _added("NrdrNnlcKiGain", ParamType.INT, PB, "10", owner=ParamOwner.LATERAL),
  _added("NrdrTuneLearner", ParamType.BOOL, PB, "1", owner=ParamOwner.LATERAL),
  _added("NrdrLatStiction", ParamType.BOOL, PB, "0", owner=ParamOwner.LATERAL),
  _added("NrdrTuneLearnerReset", ParamType.BOOL, (P,), "0", ParamLifecycle.COMMAND, ParamOwner.LATERAL),
  _added("NrdrTuneLearnerStrength", ParamType.INT, PB, "100", owner=ParamOwner.LATERAL),
  _added("NrdrTuneLearnerRate", ParamType.INT, PB, "50", owner=ParamOwner.LATERAL),
  _added("NrdrTuneLearnerMap", ParamType.BYTES, (P, B, D), lifecycle=ParamLifecycle.STATE, owner=ParamOwner.LATERAL),
  _added("HondaCenterBoostThreshold", ParamType.FLOAT, PB, "3", owner=ParamOwner.HONDA),
  _added("HondaCenterBoostMinSpeed", ParamType.INT, PB, "50", owner=ParamOwner.HONDA),
  _added("NrdrLatRateDamping", ParamType.INT, PB, "30", owner=ParamOwner.LATERAL),
  _added("NrdrLatRateDampingFadeSpeed", ParamType.INT, PB, "30", owner=ParamOwner.LATERAL),
  _added("HondaSteerDeltaLimiter", ParamType.BOOL, PB, "0", owner=ParamOwner.HONDA),
  _added("HondaSteerDeltaUp", ParamType.FLOAT, PB, "3", owner=ParamOwner.HONDA),
  _added("HondaSteerDeltaDown", ParamType.FLOAT, PB, "3", owner=ParamOwner.HONDA),
  _added("HondaPidTuneScale", ParamType.INT, PB, "100", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
  _added("HondaStopAccel", ParamType.FLOAT, PB, "-2", owner=ParamOwner.HONDA),
  _added("HondaStoppingDecelRateLong", ParamType.FLOAT, PB, "0.3", owner=ParamOwner.HONDA),
  _added("HondaVEgoStopping", ParamType.FLOAT, PB, "0.5", owner=ParamOwner.HONDA),
  _added("HondaVEgoStarting", ParamType.FLOAT, PB, "0.5", owner=ParamOwner.HONDA),
  _added("HondaCivicRadarTryout", ParamType.BOOL, PB, "0", ParamLifecycle.TOMBSTONE, ParamOwner.HONDA),
)


def validate_catalog(specs: tuple[ParamSpec, ...] = PARAM_SPECS) -> tuple[str, ...]:
  errors: list[str] = []
  seen_keys: set[str] = set()
  for spec in specs:
    if not spec.key or spec.key in seen_keys:
      errors.append(f"duplicate or empty key: {spec.key!r}")
    seen_keys.add(spec.key)
    if not spec.flags:
      errors.append(f"{spec.key}: at least one registry flag is required")
    if len(set(spec.flags)) != len(spec.flags):
      errors.append(f"{spec.key}: duplicate registry flag")
    if spec.default is not None:
      try:
        if spec.param_type is ParamType.BOOL and spec.default not in ("0", "1"):
          raise ValueError("BOOL defaults must be 0 or 1")
        if spec.param_type is ParamType.INT:
          int(spec.default)
        if spec.param_type is ParamType.FLOAT:
          float(spec.default)
      except ValueError as exc:
        errors.append(f"{spec.key}: invalid {spec.param_type.value} default {spec.default!r}: {exc}")

  overrides = [spec for spec in specs if spec.action is RegistryAction.OVERRIDE]
  if [spec.key for spec in overrides] != ["DisablePowerDown"]:
    errors.append("DisablePowerDown must be the sole existing-key override")
  return tuple(errors)


ADDED_PARAM_SPECS = tuple(spec for spec in PARAM_SPECS if spec.action is RegistryAction.ADDED)
OVERRIDDEN_PARAM_SPECS = tuple(spec for spec in PARAM_SPECS if spec.action is RegistryAction.OVERRIDE)
PARAM_SPECS_BY_KEY = {spec.key: spec for spec in PARAM_SPECS}
