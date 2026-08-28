"""Versioned NRDR parameter profiles and fingerprint-specific parameter metadata.

This module is intentionally safe to import before the native Params library is
built. Runtime Params and logging dependencies are loaded only by the functions
that need them.
"""

from dataclasses import dataclass
from typing import Protocol

from openpilot.nrdr.params.generated.keys import NrdrParamKey


type ProfileValue = bool | int | float


class ProfileParamStore(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def put_bool(self, key: str, value: bool, *, block: bool = False): ...
  def put(self, key: str, value: ProfileValue, *, block: bool = False): ...


@dataclass(frozen=True)
class HandcraftedLateralProfile:
  name: str
  fingerprint: str
  version: int
  values: tuple[tuple[str, ProfileValue], ...]


HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  "HONDA_CLARITY",
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

# These two settings are owned by SunnyPilot's live-delay subsystem rather than
# the NRDR registry. Keeping the exception explicit prevents borrowed settings
# from silently expanding the profile boundary.
HANDCRAFTED_EXTERNAL_PARAM_KEYS = frozenset(("LagdToggle", "LagdToggleDelay"))

HONDA_TORQUE_MOD_HANDCRAFTED_VALUES = (
  (NrdrParamKey.NRDR_STAR_PILOT_PID.value, False),
  (NrdrParamKey.NRDR_LEARN_STIFFNESS.value, True),
  (NrdrParamKey.NRDR_LEARN_ANGLE_OFFSET.value, True),
  (NrdrParamKey.LAT_P_SCALE_LOW_SPEED.value, 100),
  (NrdrParamKey.LAT_I_SCALE_LOW_SPEED.value, 100),
  (NrdrParamKey.LAT_F_SCALE_LOW_SPEED.value, 100),
  (NrdrParamKey.LAT_P_SCALE_STANDARD.value, 100),
  (NrdrParamKey.LAT_I_SCALE_STANDARD.value, 100),
  (NrdrParamKey.LAT_F_SCALE_STANDARD.value, 100),
  (NrdrParamKey.LAT_P_SCALE_HIGHWAY.value, 100),
  (NrdrParamKey.LAT_I_SCALE_HIGHWAY.value, 100),
  (NrdrParamKey.LAT_F_SCALE_HIGHWAY.value, 100),
  (NrdrParamKey.NRDR_LAT_RATE_DAMPING.value, 0),
  (NrdrParamKey.NRDR_LAT_RATE_DAMPING_FADE_SPEED.value, 30),
  (NrdrParamKey.HONDA_CENTER_SCALE.value, 1.0),
  (NrdrParamKey.HONDA_CENTER_BOOST_THRESHOLD.value, 3.0),
  (NrdrParamKey.HONDA_CENTER_BOOST_MIN_SPEED.value, 50),
  (NrdrParamKey.NRDR_LAT_STICTION.value, True),
  (NrdrParamKey.NRDR_NNLC_ENABLED.value, False),
  (NrdrParamKey.NRDR_TUNE_LEARNER.value, False),
  (NrdrParamKey.NRDR_TUNE_LEARNER_STRENGTH.value, 0),
  (NrdrParamKey.NRDR_TUNE_LEARNER_RATE.value, 10),
  (NrdrParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE.value, False),
  (NrdrParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD.value, 2000),
  (NrdrParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST.value, 1200),
  (NrdrParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE.value, False),
  (NrdrParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS.value, 0.0),
  (NrdrParamKey.HONDA_OVERRIDE_FADE_UP_SECS.value, 1.0),
  (NrdrParamKey.HONDA_OVERRIDE_TORQUE_SCALE.value, 0),
  (NrdrParamKey.HONDA_TORQUE_LOW_PASS_FILTER.value, True),
  (NrdrParamKey.HONDA_LPF_TAU_LOW_SPEED.value, 0.1),
  (NrdrParamKey.HONDA_LPF_TAU_STANDARD.value, 0.1),
  (NrdrParamKey.HONDA_LPF_TAU_HIGHWAY.value, 0.05),
  (NrdrParamKey.HONDA_STEER_DELTA_LIMITER.value, False),
  (NrdrParamKey.HONDA_STEER_DELTA_UP.value, 4.0),
  (NrdrParamKey.HONDA_STEER_DELTA_DOWN.value, 4.0),
  ("LagdToggle", False),
  ("LagdToggleDelay", 0.5),
)


def _build_honda_profile(fingerprint: str) -> HandcraftedLateralProfile:
  if fingerprint not in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    raise ValueError(f"unsupported handcrafted-lateral fingerprint: {fingerprint}")
  return HandcraftedLateralProfile(
    name="Honda Clarity-Derived Road-Tested 2026-08-28 (steer ratio independent)",
    fingerprint=fingerprint,
    version=15,
    values=HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  )


HANDCRAFTED_LATERAL_PROFILES = {
  fingerprint: _build_honda_profile(fingerprint)
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS
}

CLARITY_ROAD_TESTED_2026_08_21 = HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"]


def _params_or_default(params: ProfileParamStore | None) -> ProfileParamStore:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


def get_handcrafted_lateral_profile(fingerprint: str) -> HandcraftedLateralProfile | None:
  return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))


def is_handcrafted_lateral_enabled(fingerprint: str, params: ProfileParamStore | None = None) -> bool:
  return get_handcrafted_lateral_profile(fingerprint) is not None and \
    _params_or_default(params).get_bool(NrdrParamKey.NRDR_HANDCRAFTED_LATERAL_TUNE.value)


def apply_handcrafted_lateral_profile(fingerprint: str, params: ProfileParamStore | None = None,
                                      *, block: bool = False) -> list[str]:
  params = _params_or_default(params)
  profile = get_handcrafted_lateral_profile(fingerprint)
  if profile is None or not params.get_bool(NrdrParamKey.NRDR_HANDCRAFTED_LATERAL_TUNE.value):
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


def restore_handcrafted_lateral_profile(fingerprint: str, params: ProfileParamStore | None = None) -> None:
  changed = apply_handcrafted_lateral_profile(fingerprint, params, block=True)
  if changed:
    from openpilot.common.swaglog import cloudlog
    cloudlog.warning({"event": "handcrafted lateral profile restored", "carFingerprint": str(fingerprint),
                      "changedParams": changed})


__all__ = (
  "CLARITY_ROAD_TESTED_2026_08_21",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS",
  "HANDCRAFTED_LATERAL_PROFILES",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES",
  "HandcraftedLateralProfile",
  "ProfileParamStore",
  "ProfileValue",
  "apply_handcrafted_lateral_profile",
  "get_handcrafted_lateral_profile",
  "is_handcrafted_lateral_enabled",
  "restore_handcrafted_lateral_profile",
)
