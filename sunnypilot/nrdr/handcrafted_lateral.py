"""Fingerprint-scoped, road-tested lateral tuning profiles.

These profiles are deliberately versioned snapshots.  They preserve the full
set of live Params that shaped a known-good drive, including helpers and model
delay settings that are easy to overlook when copying only PID gains.
"""
from dataclasses import dataclass
from typing import Protocol

type ParamValue = bool | int | float


class ParamsLike(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def put_bool(self, key: str, value: bool, *, block: bool = False): ...
  def put(self, key: str, value: ParamValue, *, block: bool = False): ...


def _params_or_default(params: ParamsLike | None) -> ParamsLike:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


@dataclass(frozen=True)
class HandcraftedLateralProfile:
  name: str
  fingerprint: str
  version: int
  values: tuple[tuple[str, ParamValue], ...]


# Captured from Brett's Clarity/Comma Four on 2026-08-07 after the August 5
# road-test refinements. The fixed PID base, VGR curve, and Clarity hybrid
# wiring are separately regression-tested in test_latcontrol.py and
# test_load_model.py.
CLARITY_ROAD_TESTED_2026_08_07 = HandcraftedLateralProfile(
  name="Clarity Road-Tested 2026-08-07",
  fingerprint="HONDA_CLARITY",
  version=2,
  values=(
    ("NrdrStarPilotPid", False),
    ("NrdrLearnSteerRatio", False),
    ("NrdrSteerRatioOffset", -1.0),
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
    ("HondaCenterScale", 0.0),
    ("HondaCenterBoostThreshold", 5.0),
    ("HondaCenterBoostMinSpeed", 15),
    ("NrdrLatStiction", False),
    ("NrdrNnlcEnabled", False),
    ("NrdrNnlcActivationSpeed", 15),
    ("NrdrNnlcKpGain", 50),
    ("NrdrNnlcKfGain", 20),
    ("NrdrNnlcKiGain", 10),
    ("NrdrTuneLearner", False),
    ("NrdrTuneLearnerStrength", 0),
    ("NrdrTuneLearnerRate", 10),
    ("HondaUnwindFreeze", False),
    ("HondaUnwindLookahead", True),
    ("HondaUnwindBoostSeconds", 1.0),
    ("HondaUnwindFfMultiplier", 2.0),
    ("NrdrIncreaseOverrideTolerance", False),
    ("NrdrDriverOverrideThreshold", 2000),
    ("NrdrOverrideThresholdCenterBoost", 1200),
    ("HondaDriverAssistDuringOverride", False),
    ("HondaOverrideFadeDownSecs", 0.0),
    ("HondaOverrideFadeUpSecs", 2.5),
    ("HondaOverrideTorqueScale", 0),
    ("HondaTorqueLowPassFilter", True),
    ("HondaLpfTauLowSpeed", 0.1),
    ("HondaLpfTauStandard", 0.1),
    ("HondaLpfTauHighway", 0.01),
    ("HondaSteerDeltaLimiter", False),
    ("HondaSteerDeltaUp", 3.0),
    ("HondaSteerDeltaDown", 3.0),
    ("NrdrMinSteerSpeed", 0),
    # Clarity CP.steerActuatorDelay is 0.1 s, so this fixed software component
    # produces the road-tested 0.6 s effective lateral delay.
    ("LagdToggle", False),
    ("LagdToggleDelay", 0.5),
  ),
)


HANDCRAFTED_LATERAL_PROFILES = {
  CLARITY_ROAD_TESTED_2026_08_07.fingerprint: CLARITY_ROAD_TESTED_2026_08_07,
}


def get_handcrafted_lateral_profile(fingerprint: str) -> HandcraftedLateralProfile | None:
  return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))


def is_handcrafted_lateral_enabled(fingerprint: str, params: ParamsLike | None = None) -> bool:
  profile = get_handcrafted_lateral_profile(fingerprint)
  return profile is not None and _params_or_default(params).get_bool("NrdrHandcraftedLateralTune")


def apply_handcrafted_lateral_profile(fingerprint: str, params: ParamsLike | None = None, *, block: bool = False) -> list[str]:
  """Restore the selected fingerprint's profile, returning changed Param keys."""
  params = _params_or_default(params)
  profile = get_handcrafted_lateral_profile(fingerprint)
  if profile is None or not params.get_bool("NrdrHandcraftedLateralTune"):
    return []

  changed: list[str] = []
  for key, value in profile.values:
    if params.get(key, return_default=True) == value:
      continue
    if isinstance(value, bool):
      params.put_bool(key, value, block=block)
    else:
      params.put(key, value, block=block)
    changed.append(key)
  return changed
