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


HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)


# Shared road-tested controls for the supported Honda torque-mod platforms.
# Fixed PID bases and per-rack VGR curves live in interface.py/latcontrol_pid.py;
# the profile keeps the live fine-tuning controls deterministic.
HONDA_TORQUE_MOD_HANDCRAFTED_VALUES = (
    ("NrdrStarPilotPid", False),
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
    ("HondaCenterScale", 0.5),
    ("HondaCenterBoostThreshold", 3.0),
    ("HondaCenterBoostMinSpeed", 50),
    ("HondaPidFriction", 0.5),
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
    ("HondaUnwindLookahead", False),
    ("HondaUnwindBoostSeconds", 1.0),
    ("HondaUnwindFfMultiplier", 2.0),
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
    ("HondaStoppingDecelRate", 30),
    ("NrdrMinSteerSpeed", 0),
    ("LagdToggle", False),
    ("LagdToggleDelay", 0.5),
)


def _honda_torque_mod_profile(fingerprint: str) -> HandcraftedLateralProfile:
  # The Clarity's road-tested scalar offset is rack-specific. Other supported
  # cars keep a neutral scalar anchor while using their own VGR/static SR data.
  sr_offset = -1.0 if fingerprint == "HONDA_CLARITY" else 0.0
  return HandcraftedLateralProfile(
    name="Honda Torque-Mod Road-Tested 2026-08-11",
    fingerprint=fingerprint,
    version=4,
    values=(("NrdrSteerRatioOffset", sr_offset),) + HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  )


HANDCRAFTED_LATERAL_PROFILES = {
  fingerprint: _honda_torque_mod_profile(fingerprint)
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS
}

CLARITY_ROAD_TESTED_2026_08_11 = HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"]


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
