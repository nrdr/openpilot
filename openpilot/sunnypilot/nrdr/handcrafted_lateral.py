from dataclasses import dataclass
from typing import Protocol

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import get_steer_ratio_endpoint_profile


type ParamValue = bool | int | float


class ParamsLike(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def put_bool(self, key: str, value: bool, *, block: bool = False): ...
  def put(self, key: str, value: ParamValue, *, block: bool = False): ...


@dataclass(frozen=True)
class HandcraftedLateralProfile:
  name: str
  fingerprint: str
  version: int
  values: tuple[tuple[str, ParamValue], ...]


HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

HONDA_TORQUE_MOD_HANDCRAFTED_VALUES = (
  ("NrdrStarPilotPid", False),
  ("NrdrLegacyDualBpSteerRatio", False),
  ("NrdrLaneChangeEndpointSteerRatio", True),
  ("NrdrLearnSteerRatio", False),
  ("NrdrLearnStiffness", True),
  ("NrdrLearnAngleOffset", True),
  ("LatPScaleLowSpeed", 100),
  ("LatIScaleLowSpeed", 100),
  ("LatFScaleLowSpeed", 100),
  ("LatPScaleStandard", 100),
  ("LatIScaleStandard", 100),
  ("LatFScaleStandard", 100),
  ("LatPScaleHighway", 100),
  ("LatIScaleHighway", 100),
  ("LatFScaleHighway", 100),
  ("NrdrLatRateDamping", 0),
  ("NrdrLatRateDampingFadeSpeed", 30),
  ("HondaCenterScale", 1.0),
  ("HondaCenterBoostThreshold", 3.0),
  ("HondaCenterBoostMinSpeed", 50),
  ("NrdrLatStiction", True),
  ("NrdrNnlcEnabled", False),
  ("NrdrTuneLearner", False),
  ("NrdrTuneLearnerStrength", 0),
  ("NrdrTuneLearnerRate", 10),
  ("NrdrIncreaseOverrideTolerance", False),
  ("NrdrDriverOverrideThreshold", 2000),
  ("NrdrOverrideThresholdCenterBoost", 1200),
  ("HondaDriverAssistDuringOverride", False),
  ("HondaOverrideFadeDownSecs", 0.0),
  ("HondaOverrideFadeUpSecs", 1.0),
  ("HondaOverrideTorqueScale", 0),
  ("HondaTorqueLowPassFilter", True),
  ("HondaLpfTauLowSpeed", 0.1),
  ("HondaLpfTauStandard", 0.1),
  ("HondaLpfTauHighway", 0.01),
  ("HondaSteerDeltaLimiter", False),
  ("HondaSteerDeltaUp", 4.0),
  ("HondaSteerDeltaDown", 4.0),
  ("LagdToggle", False),
  ("LagdToggleDelay", 0.5),
)


def _build_honda_profile(fingerprint: str) -> HandcraftedLateralProfile:
  steer_ratio = get_steer_ratio_endpoint_profile(fingerprint)
  if steer_ratio is None:
    raise ValueError(f"missing steer-ratio profile for {fingerprint}")
  return HandcraftedLateralProfile(
    name="Honda Clarity-Derived Road-Tested 2026-08-17",
    fingerprint=fingerprint,
    version=12,
    values=steer_ratio.param_values + HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  )


HANDCRAFTED_LATERAL_PROFILES = {
  fingerprint: _build_honda_profile(fingerprint)
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS
}

CLARITY_ROAD_TESTED_2026_08_17 = HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"]


def _params_or_default(params: ParamsLike | None) -> ParamsLike:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


def get_handcrafted_lateral_profile(fingerprint: str) -> HandcraftedLateralProfile | None:
  return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))


def is_handcrafted_lateral_enabled(fingerprint: str, params: ParamsLike | None = None) -> bool:
  return get_handcrafted_lateral_profile(fingerprint) is not None and \
    _params_or_default(params).get_bool("NrdrHandcraftedLateralTune")


def apply_handcrafted_lateral_profile(fingerprint: str, params: ParamsLike | None = None, *, block: bool = False) -> list[str]:
  params = _params_or_default(params)
  profile = get_handcrafted_lateral_profile(fingerprint)
  if profile is None or not params.get_bool("NrdrHandcraftedLateralTune"):
    return []

  changed = []
  for key, value in profile.values:
    if params.get(key, return_default=True) == value:
      continue
    if isinstance(value, bool):
      params.put_bool(key, value, block=block)
    else:
      params.put(key, value, block=block)
    changed.append(key)
  return changed


def restore_handcrafted_lateral_profile(fingerprint: str, params: ParamsLike | None = None) -> None:
  changed = apply_handcrafted_lateral_profile(fingerprint, params, block=True)
  if changed:
    from openpilot.common.swaglog import cloudlog
    cloudlog.warning({"event": "handcrafted lateral profile restored", "carFingerprint": str(fingerprint),
                      "changedParams": changed})
