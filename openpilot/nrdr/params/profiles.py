"""Versioned NRDR parameter profiles and their one-shot application contract.

This module is intentionally safe to import before the native Params library is
built. Runtime Params and lateral-feature dependencies are loaded only by the
functions that need them.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Protocol

from openpilot.nrdr.params.generated.keys import NrdrParamKey


type ProfileValue = bool | int | float


class ProfileParamStore(Protocol):
  def get_bool(self, key: str) -> bool: ...
  def get(self, key: str, *, return_default: bool = False): ...
  def get_param_path(self, key: str = "") -> str: ...
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

# These settings are owned by the base/SunnyPilot registry. Keep borrowed keys
# explicit so the preset cannot silently expand its write boundary.
HANDCRAFTED_EXTERNAL_PARAM_KEYS = frozenset((
  "LagdToggle", "LagdToggleDelay", "TorqueControlTune", "LateralJerkTorqueController",
  "TorqueParamsOverrideEnabled", "TorqueParamsOverrideFriction", "TorqueParamsOverrideLatAccelFactor",
  "LaneCentering", "LaneCenteringE2EAuthority", "LaneCenteringPauseOnSignal", "LaneCenterOffset",
))

# Immutable historical values retained for provenance and import compatibility;
# the active capability-scoped recipe below is v18.
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


def _build_legacy_honda_profile(fingerprint: str) -> HandcraftedLateralProfile:
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


# Historical exports remain immutable records, not the active apply recipe.
CLARITY_CURRENT_LATERAL_2026_08_28 = _build_legacy_honda_profile("HONDA_CLARITY")
CLARITY_ROAD_TESTED_2026_08_21 = CLARITY_CURRENT_LATERAL_2026_08_28

HANDCRAFTED_LATERAL_VERSION = 19
# Captured from the owner's Civic on 2026-09-12. This records provenance, not
# validation on other vehicles. Never translate the hybrid's 1.0 friction into
# the unrelated native torque-controller override.
# v19: owner-requested 2026-09-14 lane strength reduction to 0.30. Keep the
# original snapshot hash/provenance and the already-zero model break-in.
CIVIC_DIALED_SETTINGS_SHA256 = "c1faf2291527061621c7bdbb2679fd8f90cfa00f0b8acd08fdd27e5ee9770074"
COMMON_HANDCRAFTED_VALUES = (
  ("LaneCentering", True), ("LaneCenteringStrength", 0.30),
  ("LaneCenteringMinSpeed", 50), ("LaneCenteringE2EAuthority", 0.0),
  ("LaneCenteringPauseOnSignal", True), ("LaneCenterOffset", 0.0),
  ("LagdToggle", True), ("LagdToggleDelay", 0.4),
)
_SNAPSHOT_UPDATES = {
  "NrdrLatStiction": False,
  "HondaLpfTauStandard": 0.05,
  "HondaLpfTauHighway": 0.02,
  "NrdrInterpolatedTorqueShare": 10,
  "NrdrInterpolatedTorqueFriction": 1.0,
  "NrdrInterpolatedTorqueFrictionStandard": 1.0,
  "NrdrInterpolatedTorqueFrictionHighway": 1.0,
}
_PID_KEYS = frozenset((
  "NrdrStarPilotPid", "NrdrLatStiction", "NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed",
  "NrdrTuneLearner", "NrdrTuneLearnerStrength", "NrdrTuneLearnerRate",
))
_HONDA_KEYS = frozenset((
  "NrdrIncreaseOverrideTolerance", "NrdrDriverOverrideThreshold", "NrdrOverrideThresholdCenterBoost",
))


def _snapshot_group(predicate) -> tuple[tuple[str, ProfileValue], ...]:
  return tuple((key, _SNAPSHOT_UPDATES.get(key, value)) for key, value in CLARITY_HANDCRAFTED_LATERAL_VALUES_V17 if predicate(key))


HONDA_PID_HANDCRAFTED_VALUES = _snapshot_group(lambda key: key in _PID_KEYS or key.startswith(("LatPScale", "LatIScale", "LatFScale")))
HONDA_FILTER_HANDCRAFTED_VALUES = _snapshot_group(lambda key: key.startswith("Honda") or key in _HONDA_KEYS)
HYBRID_HANDCRAFTED_VALUES = _snapshot_group(lambda key: key.startswith("NrdrInterpolatedTorque"))
TORQUE_HANDCRAFTED_VALUES = (
  ("TorqueParamsOverrideEnabled", False), ("TorqueParamsOverrideLatAccelFactor", 2.5),
  ("TorqueParamsOverrideFriction", 0.1), ("TorqueControlTune", 0.0),
  ("LateralJerkTorqueController", False),
  ("NrdrNnlcEnabled", False), ("NrdrNnlcActivationSpeed", 0),
  ("NrdrNnlcKpGain", 300), ("NrdrNnlcKiGain", 10), ("NrdrNnlcKfGain", 0),
)


def _make_profile(fingerprint: str, values: tuple[tuple[str, ProfileValue], ...], scope: str) -> HandcraftedLateralProfile:
  # These checks apply to every future recipe, not just this captured snapshot.
  if len(values) != len(dict(values)):
    raise ValueError("duplicate handcrafted-lateral setting")
  if any("SteerRatio" in key or "Calibration" in key or key in ("NrdrLearnStiffness", "NrdrLearnAngleOffset") for key, _ in values):
    raise ValueError("handcrafted preset must preserve vehicle geometry and calibration")
  return HandcraftedLateralProfile(f"Civic-derived 2026-09-12 ({scope}; steer ratio preserved)", fingerprint,
                                  HANDCRAFTED_LATERAL_VERSION, values)


HANDCRAFTED_LATERAL_PROFILES = {
  fingerprint: _make_profile(
    fingerprint, COMMON_HANDCRAFTED_VALUES + HONDA_FILTER_HANDCRAFTED_VALUES + HONDA_PID_HANDCRAFTED_VALUES +
    HYBRID_HANDCRAFTED_VALUES + (TORQUE_HANDCRAFTED_VALUES if fingerprint == "HONDA_CLARITY" else ()),
    "Honda hybrid",
  )
  for fingerprint in HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS
}

_REQUEST_KEY = NrdrParamKey.NRDR_HANDCRAFTED_LATERAL_TUNE.value
_CONTEXT_KEY = "NrdrHandcraftedLateralRequest"
_STATUS_KEY = NrdrParamKey.NRDR_CAR_HANDCRAFTED_INFO.value
_BLEND_KEY = NrdrParamKey.NRDR_INTERPOLATED_TORQUE_PIF_BLEND.value
_ENABLE_LAST_KEYS = (_BLEND_KEY, "LaneCentering")


def _params_or_default(params: ProfileParamStore | None) -> ProfileParamStore:
  if params is not None:
    return params
  from openpilot.common.params import Params
  return Params()


def get_handcrafted_lateral_profile(fingerprint: str, CP=None, CP_SP=None) -> HandcraftedLateralProfile | None:
  """Resolve consumed settings only; a fingerprint-only lookup is informational.

  All application paths pass authoritative CP/CP_SP. The historical Honda map
  remains available to callers describing the full hybrid preset before boot.
  """
  if CP is None:
    return HANDCRAFTED_LATERAL_PROFILES.get(str(fingerprint))
  identity = confirmed_vehicle_identity(CP)
  if identity is None or identity[0] != str(fingerprint) or identity[1] == "mock" or getattr(CP, "notCar", False):
    return None
  brand = identity[1]
  mode = str(getattr(CP, "steerControlType", ""))
  try:
    lateral_kind = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    return None
  if mode not in ("torque", "angle", "curvature") or lateral_kind not in ("pid", "torque", "indi", "lqr"):
    return None

  values = COMMON_HANDCRAFTED_VALUES
  scopes = ["lane centering / live delay"]
  if mode == "torque" and lateral_kind == "torque":
    values += TORQUE_HANDCRAFTED_VALUES
    scopes.append("native torque options")
  if brand == "honda" and mode == "torque":
    from openpilot.nrdr.features.lateral.capabilities import supports_interpolated_torque_pif
    from openpilot.nrdr.features.lateral.steer_ratio_tuning import get_steer_ratio_metadata
    hybrid = supports_interpolated_torque_pif(CP, CP_SP)
    values += HONDA_FILTER_HANDCRAFTED_VALUES
    pid_path = lateral_kind == "pid" or (fingerprint == "HONDA_CLARITY" and lateral_kind == "torque")
    if pid_path and (hybrid or get_steer_ratio_metadata(fingerprint) is not None):
      values += HONDA_PID_HANDCRAFTED_VALUES
      scopes.append("Honda PID")
    if hybrid:
      values += HYBRID_HANDCRAFTED_VALUES
      scopes.append("10% torque / 90% PIF")
  return _make_profile(str(fingerprint), values, ", ".join(scopes))


def confirmed_vehicle_identity(CP, fingerprint: str | None = None,
                               brand: str | None = None, *,
                               selection_present: bool | None = None) -> tuple[str, str] | None:
  """Resolve authoritative CP identity only when any selected car agrees."""
  if CP is None:
    return None
  detected_fingerprint = str(getattr(CP, "carFingerprint", "") or "")
  detected_brand = str(getattr(CP, "brand", "") or "").lower()
  selected_fingerprint = str(fingerprint or "")
  selected_brand = str(brand or "").lower()
  if selection_present is None:
    selection_present = fingerprint is not None or brand is not None
  if not detected_fingerprint or not detected_brand:
    return None
  if selection_present:
    if not selected_fingerprint or not selected_brand:
      return None
    if selected_fingerprint != detected_fingerprint or selected_brand != detected_brand:
      return None
  return detected_fingerprint, detected_brand


def handcrafted_lateral_profile_supported(CP, CP_SP, fingerprint: str | None = None,
                                           brand: str | None = None, *,
                                           selection_present: bool | None = None) -> bool:
  """Return whether confirmed vehicle identity has a compatible preset subset."""
  identity = confirmed_vehicle_identity(
    CP, fingerprint, brand, selection_present=selection_present,
  )
  if identity is None:
    return False
  return get_handcrafted_lateral_profile(identity[0], CP, CP_SP) is not None


def _canonical(value) -> str:
  return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _request_context(CP, CP_SP, profile: HandcraftedLateralProfile) -> dict:
  firmware = sorted((str(getattr(fw, "ecu", "")), bytes(getattr(fw, "fwVersion", b"")).hex())
                    for fw in getattr(CP, "carFw", ()))
  return {
    "version": profile.version, "fingerprint": profile.fingerprint, "brand": str(CP.brand).lower(),
    "controller": str(CP.lateralTuning.which()), "steer_control_type": str(CP.steerControlType),
    "flags_sp": int(getattr(CP_SP, "flags", 0)),
    "firmware_sha256": hashlib.sha256(_canonical(firmware).encode()).hexdigest(),
    "payload_sha256": hashlib.sha256(_canonical(dict(profile.values)).encode()).hexdigest(),
  }


def _put_context(params: ProfileParamStore, context: dict) -> None:
  params.put(_CONTEXT_KEY, context, block=True)
  if _canonical(params.get(_CONTEXT_KEY)) != _canonical(context):
    raise RuntimeError("handcrafted lateral request context readback mismatch")


def request_handcrafted_lateral_profile(CP, CP_SP, params: ProfileParamStore | None = None) -> bool:
  """Bind a fresh offroad request to this vehicle, controller and exact recipe."""
  params = _params_or_default(params)
  if not params.get_bool("IsOffroad") or params.get_bool(_REQUEST_KEY):
    return False
  present, fingerprint, brand = get_selected_car_identity(params)
  if not handcrafted_lateral_profile_supported(CP, CP_SP, fingerprint, brand, selection_present=present):
    return False
  profile = get_handcrafted_lateral_profile(str(CP.carFingerprint), CP, CP_SP)
  assert profile is not None
  _put_context(params, _request_context(CP, CP_SP, profile))
  _put_verified(params, _REQUEST_KEY, True)
  return True


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
  profile = get_handcrafted_lateral_profile(str(getattr(CP, "carFingerprint", "")), CP, CP_SP)
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


def get_selected_car_identity(params: ProfileParamStore) -> tuple[bool, str, str]:
  """Return physical selection presence plus a complete parsed identity.

  A malformed JSON value can decode to None just like a missing Param. In that
  case the physical file decides whether CP-only fallback is permitted.
  """
  bundle = params.get("CarPlatformBundle")
  present = bundle is not None
  if bundle is None:
    try:
      present = Path(params.get_param_path("CarPlatformBundle")).is_file()
    except (AttributeError, OSError, TypeError, ValueError):
      present = False
  if isinstance(bundle, dict):
    return present, str(bundle.get("platform") or ""), str(bundle.get("brand") or "")
  return present, "", ""


def _ordered_profile_writes(profile: HandcraftedLateralProfile) -> tuple[tuple[str, ProfileValue], ...]:
  values = dict(profile.values)
  enabled_keys = tuple(key for key in _ENABLE_LAST_KEYS if values.get(key) is True)
  underlying = tuple(
    (key, value) for key, value in profile.values
    if key not in enabled_keys
  )
  return (
    *((key, False) for key in enabled_keys),
    *underlying,
    *((key, values[key]) for key in enabled_keys),
  )


def _restore_safe_pending_state(params: ProfileParamStore, profile: HandcraftedLateralProfile, context: dict) -> None:
  """Leave an interrupted command retryable with partial compound features off."""
  errors: list[Exception] = []
  for key in _ENABLE_LAST_KEYS:
    if key not in dict(profile.values):
      continue
    try:
      _put_verified(params, key, False)
    except Exception as error:
      errors.append(error)
  try:
    _put_context(params, context)
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

  Legacy or mismatched requests are cleared without tune writes. In particular,
  an old unsupported Toyota request cannot become permission for the new recipe.
  Unknown vehicle identity and transient I/O failures remain pending. A false
  request is a strict no-op: completed profiles are never reconciled.
  """
  params = _params_or_default(params)
  if not params.get_bool(_REQUEST_KEY):
    return []
  if not startup and not params.get_bool("IsOffroad"):
    return []

  selection_present, selected_fingerprint, selected_brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(
    CP, selected_fingerprint, selected_brand, selection_present=selection_present,
  )
  if identity is None:
    return []
  fingerprint, _detected_brand = identity
  profile = get_handcrafted_lateral_profile(fingerprint, CP, CP_SP)
  if profile is None:
    _put_verified(params, _REQUEST_KEY, False)
    return []
  context = _request_context(CP, CP_SP, profile)
  try:
    context_matches = _canonical(params.get(_CONTEXT_KEY)) == _canonical(context)
  except (TypeError, ValueError):
    context_matches = False
  if not context_matches:
    _put_verified(params, _REQUEST_KEY, False)
    return []

  try:
    ordered = _ordered_profile_writes(profile)
    written: list[str] = []
    enabling = tuple(key for key in _ENABLE_LAST_KEYS if dict(profile.values).get(key) is True)
    payload_end = len(ordered) - len(enabling)
    for key, value in ordered[:payload_end]:
      _put_verified(params, key, value)
      written.append(key)
    # Verify the whole payload before enabling either lane centering or hybrid.
    for key, value in profile.values:
      if key not in enabling:
        _verify_typed(params, key, value)
    for key, value in ordered[payload_end:]:
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

    _put_context(params, {})
    params.put_bool(_REQUEST_KEY, False, block=True)
    if not _value_matches(params.get(_REQUEST_KEY, return_default=True), False):
      raise RuntimeError("handcrafted lateral command clear readback mismatch")
    return written
  except Exception as apply_error:
    try:
      _restore_safe_pending_state(params, profile, context)
    except HandcraftedLateralUnsafeStateError as cleanup_error:
      raise cleanup_error from apply_error
    raise


__all__ = (
  "CLARITY_CURRENT_LATERAL_2026_08_28",
  "CLARITY_HANDCRAFTED_LATERAL_VALUES_V17",
  "CLARITY_ROAD_TESTED_2026_08_21",
  "CIVIC_DIALED_SETTINGS_SHA256",
  "COMMON_HANDCRAFTED_VALUES",
  "HANDCRAFTED_LATERAL_VERSION",
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
  "confirmed_vehicle_identity",
  "get_selected_car_identity",
  "get_handcrafted_lateral_profile",
  "handcrafted_lateral_profile_matches",
  "handcrafted_lateral_profile_status",
  "handcrafted_lateral_profile_supported",
  "handcrafted_lateral_success_marker",
  "request_handcrafted_lateral_profile",
)
