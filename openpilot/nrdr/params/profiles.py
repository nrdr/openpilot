"""Versioned NRDR parameter profiles and their one-shot application contract.

This module is intentionally safe to import before the native Params library is
built. Runtime Params and lateral-feature dependencies are loaded only by the
functions that need them.
"""

from dataclasses import dataclass
from typing import Protocol

from openpilot.nrdr.params.generated.keys import NrdrParamKey


type ProfileValue = bool | int | float


class ProfileParamStore(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def put_bool(self, key: str, value: bool, *, block: bool = False): ...
  def put(self, key: str, value, *, block: bool = False): ...


@dataclass(frozen=True)
class HandcraftedLateralProfile:
  name: str
  fingerprint: str
  version: int
  values: tuple[tuple[str, ProfileValue], ...]


class HandcraftedLateralUnavailableError(RuntimeError):
  pass


class HandcraftedLateralUnsafeStateError(RuntimeError):
  """Applying failed and the controller's safe pending state could not be verified."""


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

# The safe legacy profile remains available as a one-shot action for the other
# reviewed modified-EPS Honda fingerprints. Clarity has its own v17 snapshot.
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

# Exact 47-key local-date 2026-08-28 Clarity snapshot. Sealed oracle:
# CURRENT_CLARITY_47_ORACLE.json SHA-256
# d9bea117c3ef7a30c8f67c809b386f35e89fd2ba1158dbe7cb30b1b6ded5c97a.
# Canonical manifest SHA-256
# bd8b0ebfc10342ff6405c50659eeb24645439d4f06ea4a145ca25dfa998a8e3d.
# Values are copied exactly from the current device snapshot. The registry's
# fresh-install friction defaults intentionally remain .12 / .10 / .06.
CLARITY_HANDCRAFTED_LATERAL_VALUES_V17 = (
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
  (NrdrParamKey.NRDR_LAT_RATE_DAMPING_FADE_SPEED.value, 60),
  (NrdrParamKey.HONDA_CENTER_SCALE.value, 0.0),
  (NrdrParamKey.HONDA_CENTER_BOOST_THRESHOLD.value, 5.0),
  (NrdrParamKey.HONDA_CENTER_BOOST_MIN_SPEED.value, 0),
  (NrdrParamKey.NRDR_LAT_STICTION.value, True),
  (NrdrParamKey.NRDR_NNLC_ENABLED.value, False),
  (NrdrParamKey.NRDR_TUNE_LEARNER.value, False),
  (NrdrParamKey.NRDR_TUNE_LEARNER_STRENGTH.value, 0),
  (NrdrParamKey.NRDR_TUNE_LEARNER_RATE.value, 10),
  (NrdrParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE.value, False),
  (NrdrParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD.value, 1200),
  (NrdrParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST.value, 1200),
  (NrdrParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE.value, False),
  (NrdrParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS.value, 0.0),
  (NrdrParamKey.HONDA_OVERRIDE_FADE_UP_SECS.value, 1.0),
  (NrdrParamKey.HONDA_OVERRIDE_TORQUE_SCALE.value, 0),
  (NrdrParamKey.HONDA_TORQUE_LOW_PASS_FILTER.value, True),
  (NrdrParamKey.HONDA_LPF_TAU_LOW_SPEED.value, 0.1),
  (NrdrParamKey.HONDA_LPF_TAU_STANDARD.value, 0.09),
  (NrdrParamKey.HONDA_LPF_TAU_HIGHWAY.value, 0.07),
  (NrdrParamKey.HONDA_STEER_DELTA_LIMITER.value, False),
  (NrdrParamKey.HONDA_STEER_DELTA_UP.value, 4.0),
  (NrdrParamKey.HONDA_STEER_DELTA_DOWN.value, 4.0),
  ("LagdToggle", False),
  ("LagdToggleDelay", 0.05),
  (NrdrParamKey.NRDR_STEER_RATIO_MODE.value, 3),
  (NrdrParamKey.NRDR_STEER_RATIO_MANUAL_CENTER.value, 20.0),
  (NrdrParamKey.NRDR_STEER_RATIO_MANUAL_FINAL.value, 13.75),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_PIF_BLEND.value, True),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_SHARE.value, 75),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_LAT_ACCEL_FACTOR.value, 10.0),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION.value, 0.12),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD.value, 0.10),
  (NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY.value, 0.09),
)


def _build_honda_profile(fingerprint: str) -> HandcraftedLateralProfile:
  if fingerprint not in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS:
    raise ValueError(f"unsupported handcrafted-lateral fingerprint: {fingerprint}")
  if fingerprint == "HONDA_CLARITY":
    return HandcraftedLateralProfile(
      name="Honda Clarity Current Lateral 2026-08-28",
      fingerprint=fingerprint,
      version=17,
      values=CLARITY_HANDCRAFTED_LATERAL_VALUES_V17,
    )
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

CLARITY_CURRENT_LATERAL_2026_08_28 = HANDCRAFTED_LATERAL_PROFILES["HONDA_CLARITY"]
# Import compatibility for the previous public name; the object itself is v17.
CLARITY_ROAD_TESTED_2026_08_21 = CLARITY_CURRENT_LATERAL_2026_08_28

_REQUEST_KEY = NrdrParamKey.NRDR_HANDCRAFTED_LATERAL_TUNE.value
_STATUS_KEY = NrdrParamKey.NRDR_CAR_HANDCRAFTED_INFO.value
_BLEND_KEY = NrdrParamKey.NRDR_INTERPOLATED_TORQUE_PIF_BLEND.value
_STEER_RATIO_MODE_KEY = NrdrParamKey.NRDR_STEER_RATIO_MODE.value


def _params_or_default(params: ProfileParamStore | None) -> ProfileParamStore:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


def get_handcrafted_lateral_profile(fingerprint: str) -> HandcraftedLateralProfile | None:
  return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))


def handcrafted_lateral_profile_supported(CP, CP_SP, fingerprint: str | None = None) -> bool:
  """Return whether the detected car can safely consume its reviewed profile."""
  fingerprint = str(fingerprint or getattr(CP, "carFingerprint", ""))
  if get_handcrafted_lateral_profile(fingerprint) is None:
    return False
  if fingerprint != "HONDA_CLARITY":
    return True

  from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
  from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
  if CP is None or CP_SP is None or get_honda_vgr_profile(CP) is None:
    return False
  if str(getattr(CP, "brand", "")).lower() != "honda" or \
      not bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value):
    return False
  try:
    lateral_kind = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    lateral_kind = ""
  return lateral_kind in ("pid", "torque")


def _value_matches(actual, expected: ProfileValue) -> bool:
  return type(actual) is type(expected) and actual == expected


def handcrafted_lateral_profile_matches(profile: HandcraftedLateralProfile,
                                         params: ProfileParamStore | None = None) -> bool:
  params = _params_or_default(params)
  return all(_value_matches(params.get(key, return_default=True), value) for key, value in profile.values)


def handcrafted_lateral_success_marker(profile: HandcraftedLateralProfile) -> str:
  return f"Last applied: {profile.name} (v{profile.version}) [{profile.fingerprint}]"


def _stored_success_marker(stored) -> str | None:
  if isinstance(stored, str) and stored.startswith("Last applied:"):
    return stored.split(" | ", 1)[0]
  return None


def handcrafted_lateral_profile_status(CP, CP_SP, params: ProfileParamStore | None = None) -> str:
  """Describe last apply state without writing or reconciling any tune value."""
  params = _params_or_default(params)
  profile = get_handcrafted_lateral_profile(str(getattr(CP, "carFingerprint", "")))
  stored = params.get(_STATUS_KEY)
  stored_marker = _stored_success_marker(stored)
  if profile is None:
    if stored_marker is not None:
      return f"{stored_marker} | unavailable for detected car/EPS"
    return "Unavailable for detected car/EPS"
  marker = handcrafted_lateral_success_marker(profile)
  if not handcrafted_lateral_profile_supported(CP, CP_SP):
    if stored_marker is not None:
      pending = " | apply requested; unavailable for detected car/EPS" if params.get_bool(_REQUEST_KEY) else \
        " | unavailable for detected car/EPS"
      return stored_marker + pending
    return "Unavailable for detected car/EPS"
  if params.get_bool(_REQUEST_KEY):
    if stored_marker is not None:
      return f"{stored_marker} | apply requested; waiting for verified completion"
    return f"Apply requested: {profile.name} (v{profile.version}) | waiting for verified completion"

  if stored_marker != marker:
    if stored_marker is not None:
      return f"{stored_marker} | current profile v{profile.version} not applied"
    return f"Not applied: {profile.name} (v{profile.version})"
  state = "exact match" if handcrafted_lateral_profile_matches(profile, params) else "customized"
  return f"{marker} | {state}"


def _put_typed(params: ProfileParamStore, key: str, value: ProfileValue) -> None:
  if isinstance(value, bool):
    params.put_bool(key, value, block=True)
  else:
    params.put(key, value, block=True)


def _verify_typed(params: ProfileParamStore, key: str, value: ProfileValue) -> None:
  actual = params.get(key, return_default=True)
  if not _value_matches(actual, value):
    raise RuntimeError(f"handcrafted lateral readback mismatch for {key}: {actual!r} != {value!r}")


def _put_verified(params: ProfileParamStore, key: str, value: ProfileValue) -> None:
  _put_typed(params, key, value)
  _verify_typed(params, key, value)


def _ordered_profile_writes(profile: HandcraftedLateralProfile) -> tuple[tuple[str, ProfileValue], ...]:
  if profile.fingerprint != "HONDA_CLARITY":
    return profile.values

  values = dict(profile.values)
  underlying = tuple(
    (key, value) for key, value in profile.values
    if key not in (_BLEND_KEY, _STEER_RATIO_MODE_KEY)
  )
  return (
    (_BLEND_KEY, False),
    *underlying,
    (_STEER_RATIO_MODE_KEY, values[_STEER_RATIO_MODE_KEY]),
    (_BLEND_KEY, values[_BLEND_KEY]),
  )


def _restore_safe_pending_state(params: ProfileParamStore, profile: HandcraftedLateralProfile) -> None:
  """Leave an interrupted command retryable, with Clarity's blend verified off."""
  errors: list[Exception] = []
  if profile.fingerprint == "HONDA_CLARITY":
    try:
      _put_verified(params, _BLEND_KEY, False)
    except Exception as error:
      errors.append(error)
  try:
    params.put_bool(_REQUEST_KEY, True, block=True)
    if not _value_matches(params.get(_REQUEST_KEY, return_default=True), True):
      raise RuntimeError("handcrafted lateral request restore readback mismatch")
  except Exception as error:
    errors.append(error)
  if errors:
    details = "; ".join(f"{type(error).__name__}: {error}" for error in errors)
    raise HandcraftedLateralUnsafeStateError(
      f"handcrafted lateral could not restore its verified safe pending state ({details})"
    ) from errors[0]


def consume_handcrafted_lateral_request(CP, CP_SP, params: ProfileParamStore | None = None,
                                        *, startup: bool = False) -> list[str]:
  """Consume one pending apply request only after every value verifies exactly.

  The durable BOOL remains true after any interruption or validation failure, so
  the next offroad poll or car startup can safely retry the deterministic write
  sequence. A false request is a strict no-op: this function never reconciles a
  completed profile.
  """
  params = _params_or_default(params)
  if not params.get_bool(_REQUEST_KEY):
    return []
  if not startup and not params.get_bool("IsOffroad"):
    return []

  fingerprint = str(getattr(CP, "carFingerprint", ""))
  profile = get_handcrafted_lateral_profile(fingerprint)
  if profile is None or not handcrafted_lateral_profile_supported(CP, CP_SP):
    raise HandcraftedLateralUnavailableError(
      f"handcrafted lateral profile unavailable for detected car/EPS: {fingerprint or 'unknown'}"
    )

  try:
    ordered = _ordered_profile_writes(profile)
    written: list[str] = []
    if profile.fingerprint == "HONDA_CLARITY":
      # Phase one keeps the master durably OFF while every payload value and
      # mode-last steering source is written and verified. Recheck the entire
      # non-blend snapshot before the only write which can enable the blend.
      for key, value in ordered[:-1]:
        _put_verified(params, key, value)
        written.append(key)
      for key, value in profile.values:
        if key != _BLEND_KEY:
          _verify_typed(params, key, value)
      key, value = ordered[-1]
      _put_verified(params, key, value)
      written.append(key)
    else:
      for key, value in ordered:
        _put_verified(params, key, value)
        written.append(key)

    for key, value in profile.values:
      _verify_typed(params, key, value)

    current_version = params.get("ParamsVersion")
    if current_version is not None and type(current_version) is not int:
      raise RuntimeError(f"handcrafted lateral invalid ParamsVersion type: {type(current_version).__name__}")
    version = (current_version or 0) + 1
    params.put("ParamsVersion", version, block=True)
    if not _value_matches(params.get("ParamsVersion"), version):
      raise RuntimeError("handcrafted lateral ParamsVersion readback mismatch")

    marker = handcrafted_lateral_success_marker(profile)
    params.put(_STATUS_KEY, marker, block=True)
    if params.get(_STATUS_KEY) != marker:
      raise RuntimeError("handcrafted lateral status readback mismatch")

    params.put_bool(_REQUEST_KEY, False, block=True)
    if not _value_matches(params.get(_REQUEST_KEY, return_default=True), False):
      raise RuntimeError("handcrafted lateral command clear readback mismatch")
    return written
  except Exception as apply_error:
    try:
      _restore_safe_pending_state(params, profile)
    except HandcraftedLateralUnsafeStateError as cleanup_error:
      raise cleanup_error from apply_error
    raise


__all__ = (
  "CLARITY_CURRENT_LATERAL_2026_08_28",
  "CLARITY_HANDCRAFTED_LATERAL_VALUES_V17",
  "CLARITY_ROAD_TESTED_2026_08_21",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS",
  "HANDCRAFTED_LATERAL_PROFILES",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES",
  "HandcraftedLateralProfile",
  "HandcraftedLateralUnavailableError",
  "HandcraftedLateralUnsafeStateError",
  "ProfileParamStore",
  "ProfileValue",
  "consume_handcrafted_lateral_request",
  "get_handcrafted_lateral_profile",
  "handcrafted_lateral_profile_matches",
  "handcrafted_lateral_profile_status",
  "handcrafted_lateral_profile_supported",
  "handcrafted_lateral_success_marker",
)
