from dataclasses import dataclass
from typing import Protocol

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.sunnypilot.nrdr.honda_vgr import get_honda_vgr_profile


type ParamValue = bool | int | float

HANDCRAFTED_REQUEST_PARAM = "NrdrHandcraftedLateralTune"
HANDCRAFTED_STATUS_PARAM = "NrdrCarHandcraftedInfo"
CLARITY_FINGERPRINT = "HONDA_CLARITY"
BLEND_MASTER_PARAM = "NrdrInterpolatedTorquePifBlend"
STEER_RATIO_MODE_PARAM = "NrdrSteerRatioMode"


class ParamsLike(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def put_bool(self, key: str, value: bool, *, block: bool = False): ...
  def put(self, key: str, value: ParamValue | str, *, block: bool = False): ...


@dataclass(frozen=True)
class HandcraftedLateralProfile:
  name: str
  fingerprint: str
  version: int
  values: tuple[tuple[str, ParamValue], ...]


class HandcraftedLateralUnavailableError(RuntimeError):
  pass


class HandcraftedLateralUnsafeStateError(RuntimeError):
  """Applying failed and the controller's safe retry state could not be verified."""


HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS = (
  "HONDA_ACCORD",
  "HONDA_CIVIC",
  "HONDA_CIVIC_BOSCH",
  "HONDA_CIVIC_BOSCH_DIESEL",
  CLARITY_FINGERPRINT,
  "HONDA_CRV_5G",
  "HONDA_INSIGHT",
)

# Safe legacy v15 profile retained for the non-Clarity Honda platforms. It
# intentionally does not select a steer-ratio source or Torque/PIF blend.
HONDA_TORQUE_MOD_HANDCRAFTED_VALUES = (
  ("NrdrStarPilotPid", False),
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
  ("HondaLpfTauHighway", 0.05),
  ("HondaSteerDeltaLimiter", False),
  ("HondaSteerDeltaUp", 4.0),
  ("HondaSteerDeltaDown", 4.0),
  ("LagdToggle", False),
  ("LagdToggleDelay", 0.5),
)

# Provenance oracle: CURRENT_CLARITY_47_ORACLE.json SHA-256
# d9bea117c3ef7a30c8f67c809b386f35e89fd2ba1158dbe7cb30b1b6ded5c97a.
# Canonical oracle manifest SHA-256:
# bd8b0ebfc10342ff6405c50659eeb24645439d4f06ea4a145ca25dfa998a8e3d.
# This is exactly the user's current captured 47-key tune after the latest
# drive; global defaults and migration policy remain independent.
CLARITY_HANDCRAFTED_VALUES_V17 = (
  ("NrdrStarPilotPid", False),
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
  ("NrdrLatRateDampingFadeSpeed", 60),
  ("HondaCenterScale", 0.0),
  ("HondaCenterBoostThreshold", 5.0),
  ("HondaCenterBoostMinSpeed", 0),
  ("NrdrLatStiction", True),
  ("NrdrNnlcEnabled", False),
  ("NrdrTuneLearner", False),
  ("NrdrTuneLearnerStrength", 0),
  ("NrdrTuneLearnerRate", 10),
  ("NrdrIncreaseOverrideTolerance", False),
  ("NrdrDriverOverrideThreshold", 1200),
  ("NrdrOverrideThresholdCenterBoost", 1200),
  ("HondaDriverAssistDuringOverride", False),
  ("HondaOverrideFadeDownSecs", 0.0),
  ("HondaOverrideFadeUpSecs", 1.0),
  ("HondaOverrideTorqueScale", 0),
  ("HondaTorqueLowPassFilter", True),
  ("HondaLpfTauLowSpeed", 0.1),
  ("HondaLpfTauStandard", 0.09),
  ("HondaLpfTauHighway", 0.07),
  ("HondaSteerDeltaLimiter", False),
  ("HondaSteerDeltaUp", 4.0),
  ("HondaSteerDeltaDown", 4.0),
  ("LagdToggle", False),
  ("LagdToggleDelay", 0.05),
  (STEER_RATIO_MODE_PARAM, 3),
  ("NrdrSteerRatioManualCenter", 20.0),
  ("NrdrSteerRatioManualFinal", 13.75),
  (BLEND_MASTER_PARAM, True),
  ("NrdrInterpolatedTorqueShare", 75),
  ("NrdrInterpolatedTorqueLatAccelFactor", 10.0),
  ("NrdrInterpolatedTorqueFriction", 0.12),
  ("NrdrInterpolatedTorqueFrictionStandard", 0.10),
  ("NrdrInterpolatedTorqueFrictionHighway", 0.09),
)


def _build_honda_profile(fingerprint: str) -> HandcraftedLateralProfile:
  if fingerprint == CLARITY_FINGERPRINT:
    return HandcraftedLateralProfile(
      name="Honda Clarity Current Lateral 2026-08-28",
      fingerprint=fingerprint,
      version=17,
      values=CLARITY_HANDCRAFTED_VALUES_V17,
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

CLARITY_CURRENT_LATERAL_2026_08_28 = HANDCRAFTED_LATERAL_PROFILES[CLARITY_FINGERPRINT]
CLARITY_ROAD_TESTED_2026_08_28 = CLARITY_CURRENT_LATERAL_2026_08_28
CLARITY_ROAD_TESTED_2026_08_21 = CLARITY_CURRENT_LATERAL_2026_08_28


def _params_or_default(params: ParamsLike | None) -> ParamsLike:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


def _fingerprint(CP) -> str:
  if isinstance(CP, str):
    return CP
  return str(getattr(CP, "carFingerprint", "")) if CP is not None else ""


def get_handcrafted_lateral_profile(fingerprint: str) -> HandcraftedLateralProfile | None:
  return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))


def _supports_interpolated_controller(CP, CP_SP) -> bool:
  """Mirror the controller's support gate without importing its runtime stack."""
  if CP is None or CP_SP is None or str(getattr(CP, "brand", "")).lower() != "honda":
    return False
  if not bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value):
    return False
  try:
    tuning = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    tuning = ""
  return tuning == "pid" or (_fingerprint(CP) == CLARITY_FINGERPRINT and tuning == "torque")


def handcrafted_lateral_profile_supported(CP, CP_SP) -> bool:
  """Use one conservative support gate in runtime, native UI, and SunnyLink."""
  fingerprint = _fingerprint(CP)
  if get_handcrafted_lateral_profile(fingerprint) is None:
    return False
  if fingerprint != CLARITY_FINGERPRINT:
    return True
  if CP is None or isinstance(CP, str):
    return False
  return get_honda_vgr_profile(CP) is not None and _supports_interpolated_controller(CP, CP_SP)


def _put_typed(params: ParamsLike, key: str, value: ParamValue | str) -> None:
  if isinstance(value, bool):
    params.put_bool(key, value, block=True)
  else:
    params.put(key, value, block=True)


def _value_matches(actual, expected) -> bool:
  return type(actual) is type(expected) and actual == expected


def _verify_value(params: ParamsLike, key: str, expected) -> None:
  actual = params.get(key, return_default=True)
  if not _value_matches(actual, expected):
    raise RuntimeError(f"handcrafted lateral readback mismatch for {key}: {actual!r} != {expected!r}")


def _put_verified(params: ParamsLike, key: str, value: ParamValue | str) -> None:
  _put_typed(params, key, value)
  _verify_value(params, key, value)


def _profile_label(profile: HandcraftedLateralProfile) -> str:
  return f"{profile.name} (v{profile.version}) [{profile.fingerprint}]"


def _success_marker(profile: HandcraftedLateralProfile) -> str:
  return f"Last applied: {_profile_label(profile)}"


def _saved_success_marker(params: ParamsLike) -> str:
  saved = str(params.get(HANDCRAFTED_STATUS_PARAM) or "")
  return saved.split(" | ", 1)[0] if saved.startswith("Last applied: ") else ""


def _profile_is_exact(profile: HandcraftedLateralProfile, params: ParamsLike) -> bool:
  return all(_value_matches(params.get(key, return_default=True), value) for key, value in profile.values)


def _finalize_profile(profile: HandcraftedLateralProfile, params: ParamsLike) -> None:
  # Version first: a failed invalidation must not publish a new durable success
  # marker for a profile that callers still need to retry.
  current_version = params.get("ParamsVersion")
  if current_version is not None and type(current_version) is not int:
    raise RuntimeError(f"handcrafted lateral invalid ParamsVersion type: {type(current_version).__name__}")
  params_version = (current_version or 0) + 1
  _put_verified(params, "ParamsVersion", params_version)
  _put_verified(params, HANDCRAFTED_STATUS_PARAM, _success_marker(profile))
  _put_verified(params, HANDCRAFTED_REQUEST_PARAM, False)


def _restore_retry_state(params: ParamsLike, original: Exception, *, disable_blend: bool) -> None:
  """Best-effort durable cleanup; raise a louder error if safe state cannot verify."""
  cleanup_errors = []
  if disable_blend:
    try:
      _put_verified(params, BLEND_MASTER_PARAM, False)
    except Exception as e:
      cleanup_errors.append(f"blend OFF: {e}")
  try:
    _put_verified(params, HANDCRAFTED_REQUEST_PARAM, True)
  except Exception as e:
    cleanup_errors.append(f"request TRUE: {e}")
  if cleanup_errors:
    raise HandcraftedLateralUnsafeStateError(
      "handcrafted lateral safe-state cleanup failed: " + "; ".join(cleanup_errors)
    ) from original


def _consume_clarity_profile(profile: HandcraftedLateralProfile, params: ParamsLike) -> list[str]:
  values = dict(profile.values)
  underlying = tuple(
    (key, value) for key, value in profile.values
    if key not in (BLEND_MASTER_PARAM, STEER_RATIO_MODE_PARAM)
  )
  written = []
  try:
    # Phase 1: prove P/I/F-only state before any profile payload can change.
    _put_verified(params, BLEND_MASTER_PARAM, False)
    written.append(BLEND_MASTER_PARAM)
    for key, value in underlying:
      _put_verified(params, key, value)
      written.append(key)
    _put_verified(params, STEER_RATIO_MODE_PARAM, values[STEER_RATIO_MODE_PARAM])
    written.append(STEER_RATIO_MODE_PARAM)

    # Re-verify the complete non-blend payload, with the master still exactly
    # typed FALSE, before Torque is allowed into the final command.
    for key, value in profile.values:
      if key != BLEND_MASTER_PARAM:
        _verify_value(params, key, value)
    _verify_value(params, BLEND_MASTER_PARAM, False)

    # Phase 2: enable only the now-complete profile, then finalize its journal.
    _put_verified(params, BLEND_MASTER_PARAM, values[BLEND_MASTER_PARAM])
    written.append(BLEND_MASTER_PARAM)
    if not _profile_is_exact(profile, params):
      raise RuntimeError(f"handcrafted lateral profile v{profile.version} readback mismatch")
    _finalize_profile(profile, params)
    return written
  except Exception as original:
    # Card intentionally continues startup after this exception. Never let that
    # continuation carry a partial Torque profile or lose the durable retry.
    _restore_retry_state(params, original, disable_blend=True)
    raise


def _consume_legacy_profile(profile: HandcraftedLateralProfile, params: ParamsLike) -> list[str]:
  written = []
  try:
    for key, value in profile.values:
      _put_verified(params, key, value)
      written.append(key)
    if not _profile_is_exact(profile, params):
      raise RuntimeError(f"handcrafted lateral profile v{profile.version} readback mismatch")
    _finalize_profile(profile, params)
    return written
  except Exception as original:
    _restore_retry_state(params, original, disable_blend=False)
    raise


def consume_handcrafted_lateral_request(CP, CP_SP, params: ParamsLike | None = None, *, startup: bool = False) -> list[str]:
  """Consume one durable apply request; never enforce a profile continuously."""
  params = _params_or_default(params)
  if not params.get_bool(HANDCRAFTED_REQUEST_PARAM):
    return []
  if not startup and not params.get_bool("IsOffroad"):
    return []

  profile = get_handcrafted_lateral_profile(_fingerprint(CP))
  if profile is None or not handcrafted_lateral_profile_supported(CP, CP_SP):
    raise HandcraftedLateralUnavailableError(
      f"handcrafted lateral profile unavailable for detected car/EPS: {_fingerprint(CP) or 'unknown'}"
    )

  if profile.fingerprint == CLARITY_FINGERPRINT:
    return _consume_clarity_profile(profile, params)
  return _consume_legacy_profile(profile, params)


def handcrafted_lateral_profile_status(CP, CP_SP, params: ParamsLike | None = None) -> str:
  """Pure status derivation: it never changes profile-owned or command Params."""
  params = _params_or_default(params)
  saved_marker = _saved_success_marker(params)
  profile = get_handcrafted_lateral_profile(_fingerprint(CP))
  if profile is None:
    unavailable = "Unavailable for detected car/EPS"
    return f"{saved_marker} | {unavailable}" if saved_marker else unavailable

  if not handcrafted_lateral_profile_supported(CP, CP_SP):
    unavailable = "unavailable for detected car/EPS"
    if saved_marker and params.get_bool(HANDCRAFTED_REQUEST_PARAM):
      return f"{saved_marker} | apply requested; {unavailable}"
    return f"{saved_marker} | {unavailable}" if saved_marker else "Unavailable for detected car/EPS"

  if params.get_bool(HANDCRAFTED_REQUEST_PARAM):
    if saved_marker:
      return f"{saved_marker} | apply requested; waiting for verified completion"
    return f"Apply requested: {profile.name} (v{profile.version}) | waiting for verified completion"

  marker = _success_marker(profile)
  if saved_marker != marker:
    if saved_marker:
      return f"{saved_marker} | current profile v{profile.version} not applied"
    return f"Not applied: {profile.name} (v{profile.version})"

  exact = "exact match" if _profile_is_exact(profile, params) else "customized"
  return f"{marker} | {exact}"
