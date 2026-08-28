"""Engagement-latched NRDR interpolation between Honda torque and P/I/F control."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY, CV
from openpilot.nrdr.params import NrdrParamKey, read_bool, read_float


LEGACY_TORQUE_KP = 0.5
LEGACY_TORQUE_KI = 0.1
LEGACY_TORQUE_KF = 1.0
LEGACY_TORQUE_KD = 0.0
LEGACY_TORQUE_LOW_SPEED_X = (0.0, 10.0, 20.0, 30.0)
LEGACY_TORQUE_LOW_SPEED_Y = (30.0, 17.0, 10.0, 5.0)
LEGACY_TORQUE_FRICTION_THRESHOLD = 0.3
LEGACY_TORQUE_YAW_BLEND_X = (2.0, 5.0)

DEFAULT_TORQUE_SHARE_PERCENT = 50.0
DEFAULT_LAT_ACCEL_FACTOR = 5.0
DEFAULT_FRICTION = 0.5
FRICTION_LOW_STANDARD_TRANSITION_MPH = 25.0
FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH = 50.0
FRICTION_TRANSITION_HALF_WIDTH_MPH = 1.0


@dataclass(frozen=True, slots=True)
class InterpolatedTorquePifSettings:
  enabled: bool = False
  torque_share: float = DEFAULT_TORQUE_SHARE_PERCENT / 100.0
  lat_accel_factor: float = DEFAULT_LAT_ACCEL_FACTOR
  friction_low: float = DEFAULT_FRICTION
  friction_standard: float = DEFAULT_FRICTION
  friction_highway: float = DEFAULT_FRICTION

  @property
  def friction(self) -> float:
    """Compatibility name for the original low-speed setting."""
    return self.friction_low

  @property
  def torque_share_percent(self) -> int:
    return int(round(self.torque_share * 100.0))


@dataclass(frozen=True, slots=True)
class ClassicTorqueCandidateResult:
  output: float
  error: float
  p: float
  i: float
  d: float
  f: float
  actual_curvature: float
  actual_lateral_accel: float
  desired_lateral_accel: float
  measurement_source: str
  yaw_feedback_weight: float
  yaw_feedback_valid: bool
  yaw_feedback_fallback_reason: str


@dataclass(frozen=True, slots=True)
class ClassicTorqueMeasurement:
  actual_curvature: float
  source: str
  yaw_feedback_weight: float
  yaw_feedback_valid: bool
  fallback_reason: str = ""


@dataclass(slots=True)
class InterpolatedTorquePifSettingsLatch:
  settings: InterpolatedTorquePifSettings

  def update(self, settings, supported: bool, active: bool) -> InterpolatedTorquePifSettings:
    if not active:
      self.settings = resolve_interpolated_torque_pif_settings(settings, supported)
    return self.settings


def supports_interpolated_torque_pif(CP, CP_SP) -> bool:
  """Limit the experiment to modified-EPS Honda PID and Clarity-hybrid paths."""
  if str(getattr(CP, "brand", "")).lower() != "honda":
    return False
  if not bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value):
    return False

  fingerprint = str(getattr(CP, "carFingerprint", ""))
  try:
    lateral_kind = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    lateral_kind = ""
  return lateral_kind == "pid" or (fingerprint == "HONDA_CLARITY" and lateral_kind == "torque")


def resolve_interpolated_torque_pif_settings(settings, supported: bool) -> InterpolatedTorquePifSettings:
  share_percent = read_float(
    settings,
    NrdrParamKey.NRDR_INTERPOLATED_TORQUE_SHARE,
    DEFAULT_TORQUE_SHARE_PERCENT,
    0.0,
    100.0,
  )
  return InterpolatedTorquePifSettings(
    enabled=supported and read_bool(settings, NrdrParamKey.NRDR_INTERPOLATED_TORQUE_PIF_BLEND),
    torque_share=share_percent / 100.0,
    lat_accel_factor=read_float(
      settings,
      NrdrParamKey.NRDR_INTERPOLATED_TORQUE_LAT_ACCEL_FACTOR,
      DEFAULT_LAT_ACCEL_FACTOR,
      0.1,
      10.0,
    ),
    friction_low=read_float(
      settings,
      NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION,
      DEFAULT_FRICTION,
      0.0,
      1.0,
    ),
    friction_standard=read_float(
      settings,
      NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD,
      DEFAULT_FRICTION,
      0.0,
      1.0,
    ),
    friction_highway=read_float(
      settings,
      NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY,
      DEFAULT_FRICTION,
      0.0,
      1.0,
    ),
  )


def speed_banded_friction(v_ego: float, low: float, standard: float, highway: float) -> float:
  """Select friction by speed with continuous two-mph handoffs around 25 and 50 mph."""
  low = float(low)
  standard = float(standard)
  highway = float(highway)
  if low == standard == highway:
    # Preserve the original single-setting arithmetic exactly after migration.
    return low

  v_ego = float(v_ego)
  if not np.isfinite(v_ego):
    return low

  low_start = (FRICTION_LOW_STANDARD_TRANSITION_MPH - FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  low_end = (FRICTION_LOW_STANDARD_TRANSITION_MPH + FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  highway_start = (FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH - FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  highway_end = (FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH + FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS

  if v_ego <= low_start:
    return low
  if v_ego < low_end:
    return float(np.interp(v_ego, (low_start, low_end), (low, standard)))
  if v_ego <= highway_start:
    return standard
  if v_ego < highway_end:
    return float(np.interp(v_ego, (highway_start, highway_end), (standard, highway)))
  return highway


def convex_torque_pif_blend(pif_output: float, torque_output: float, torque_share: float,
                            steer_max: float = 1.0) -> float:
  share = float(np.clip(torque_share, 0.0, 1.0))
  if share <= 0.0:
    blended = float(pif_output)
  elif share >= 1.0:
    blended = float(torque_output)
  else:
    blended = (1.0 - share) * float(pif_output) + share * float(torque_output)
  return float(np.clip(blended, -steer_max, steer_max))


def maybe_blend_interpolated_torque_pif(
  pif_output: float,
  settings: InterpolatedTorquePifSettings,
  classic_candidate: Callable[[], ClassicTorqueCandidateResult],
  steer_max: float = 1.0,
) -> tuple[float, ClassicTorqueCandidateResult | None]:
  """Return P/I/F verbatim while off; only evaluate the torque half while on."""
  if not settings.enabled:
    return pif_output, None

  classic_result = classic_candidate()
  # Once the historical path calls for yaw, reusing angle feedback would make
  # both halves respond to the same sensor. An unavailable torque candidate is
  # diagnostic-only, so return the complete P/I/F command bit-for-bit.
  if not classic_result.yaw_feedback_valid:
    return pif_output, classic_result
  return (
    convex_torque_pif_blend(pif_output, classic_result.output, settings.torque_share, steer_max),
    classic_result,
  )


def should_run_pif_tune_learner(is_eps_modified: bool, settings: InterpolatedTorquePifSettings) -> bool:
  """Allow sample accumulation only off-blend; caller still runs learner maintenance."""
  return bool(is_eps_modified and not settings.enabled)


def select_classic_torque_measurement(angle_curvature: Callable[[], float], v_ego: float,
                                      calibrated_pose) -> ClassicTorqueMeasurement:
  """Reproduce f13's 2-5 m/s angle-to-yaw measurement transition safely."""
  v_ego = float(v_ego)
  requested_yaw_weight = float(np.interp(v_ego, LEGACY_TORQUE_YAW_BLEND_X, (0.0, 1.0)))
  if requested_yaw_weight <= 0.0:
    # Yaw is deliberately not required below the historical transition.
    return ClassicTorqueMeasurement(float(angle_curvature()), "angle_low_speed", 0.0, True)

  if calibrated_pose is None:
    return ClassicTorqueMeasurement(float("nan"), "yaw_unavailable", requested_yaw_weight, False, "pose_unavailable")
  if not bool(getattr(calibrated_pose, "angular_velocity_valid", False)):
    return ClassicTorqueMeasurement(float("nan"), "yaw_unavailable", requested_yaw_weight, False, "pose_invalid_or_stale")

  try:
    yaw_rate = float(calibrated_pose.angular_velocity.z)
  except (AttributeError, TypeError, ValueError):
    return ClassicTorqueMeasurement(float("nan"), "yaw_unavailable", requested_yaw_weight, False, "yaw_unavailable")
  if not np.isfinite(yaw_rate):
    return ClassicTorqueMeasurement(float("nan"), "yaw_unavailable", requested_yaw_weight, False, "yaw_nonfinite")

  yaw_curvature = yaw_rate / v_ego
  if requested_yaw_weight >= 1.0:
    return ClassicTorqueMeasurement(yaw_curvature, "yaw", 1.0, True)

  actual_curvature = float(np.interp(
    v_ego,
    LEGACY_TORQUE_YAW_BLEND_X,
    (float(angle_curvature()), yaw_curvature),
  ))
  return ClassicTorqueMeasurement(actual_curvature, "angle_yaw_blend", requested_yaw_weight, True)


class LegacyTorquePid:
  """The f13de17 normal-path PID, kept separate from the current P/I/F state."""

  def __init__(self, dt: float, steer_max: float):
    self.dt = float(dt)
    self.steer_max = float(steer_max)
    self.reset()

  def reset(self) -> None:
    self.p = 0.0
    self.i = 0.0
    self.d = 0.0
    self.f = 0.0
    self.control = 0.0

  def update(self, error: float, feedforward: float, freeze_integrator: bool) -> float:
    error = float(error)
    self.p = error * LEGACY_TORQUE_KP
    self.f = float(feedforward) * LEGACY_TORQUE_KF
    self.d = 0.0

    candidate_i = self.i + error * LEGACY_TORQUE_KI * self.dt
    candidate_control = self.p + candidate_i + self.d + self.f
    moves_away_from_positive_limit = error >= 0.0 and (candidate_control <= self.steer_max or candidate_i < 0.0)
    moves_away_from_negative_limit = error <= 0.0 and (candidate_control >= -self.steer_max or candidate_i > 0.0)
    if (moves_away_from_positive_limit or moves_away_from_negative_limit) and not freeze_integrator:
      self.i = candidate_i

    self.control = float(np.clip(self.p + self.i + self.d + self.f, -self.steer_max, self.steer_max))
    return self.control


class ClassicTorqueCandidate:
  """f13de17's normal yaw-feedback torque controller without NN/jerk extensions."""

  def __init__(self, dt: float, steer_max: float = 1.0):
    self.pid = LegacyTorquePid(dt, steer_max)

  def reset(self) -> None:
    # Deliberate safety adaptation: do not retain f13de17's stale integral over a disengagement.
    self.pid.reset()

  @staticmethod
  def _apply_center_deadzone(error: float, deadzone: float) -> float:
    if error > deadzone:
      return error - deadzone
    if error < -deadzone:
      return error + deadzone
    return 0.0

  @classmethod
  def _friction(cls, lateral_accel_error: float, lateral_accel_deadzone: float, friction: float) -> float:
    return float(np.interp(
      cls._apply_center_deadzone(lateral_accel_error, lateral_accel_deadzone),
      (-LEGACY_TORQUE_FRICTION_THRESHOLD, LEGACY_TORQUE_FRICTION_THRESHOLD),
      (-friction, friction),
    ))

  def update(self, CS, VM, vehicle_params, steer_limited_by_safety: bool, desired_curvature: float,
             calibrated_pose, steer_ratio_selection,
             settings: InterpolatedTorquePifSettings) -> ClassicTorqueCandidateResult:
    v_ego = float(CS.vEgo)
    desired_lateral_accel = float(desired_curvature) * v_ego ** 2
    curvature_measurement = select_classic_torque_measurement(
      lambda: steer_ratio_selection.measured_curvature(
        VM,
        float(CS.steeringAngleDeg),
        v_ego,
        float(vehicle_params.roll),
        float(vehicle_params.angleOffsetDeg),
      ),
      v_ego,
      calibrated_pose,
    )
    actual_curvature = curvature_measurement.actual_curvature
    if not curvature_measurement.yaw_feedback_valid:
      # The requested yaw measurement is unavailable. Hold every classic PID
      # term exactly as-is; maybe_blend_interpolated_torque_pif returns P/I/F.
      return ClassicTorqueCandidateResult(
        output=float("nan"),
        error=float("nan"),
        p=self.pid.p,
        i=self.pid.i,
        d=self.pid.d,
        f=self.pid.f,
        actual_curvature=float("nan"),
        actual_lateral_accel=float("nan"),
        desired_lateral_accel=desired_lateral_accel,
        measurement_source=curvature_measurement.source,
        yaw_feedback_weight=curvature_measurement.yaw_feedback_weight,
        yaw_feedback_valid=False,
        yaw_feedback_fallback_reason=curvature_measurement.fallback_reason,
      )
    actual_lateral_accel = actual_curvature * v_ego ** 2

    # f13's useSteeringAngle=False path explicitly sets curvature deadzone to 0.
    lateral_accel_deadzone = 0.0
    low_speed_factor = float(np.interp(v_ego, LEGACY_TORQUE_LOW_SPEED_X, LEGACY_TORQUE_LOW_SPEED_Y)) ** 2
    setpoint = desired_lateral_accel + low_speed_factor * float(desired_curvature)
    measurement = actual_lateral_accel + low_speed_factor * actual_curvature

    lat_accel_factor = settings.lat_accel_factor
    error = (setpoint / lat_accel_factor) - (measurement / lat_accel_factor)
    roll_compensation = float(vehicle_params.roll) * ACCELERATION_DUE_TO_GRAVITY
    friction_input = desired_lateral_accel - actual_lateral_accel
    feedforward = (desired_lateral_accel - roll_compensation) / lat_accel_factor
    friction = speed_banded_friction(
      v_ego,
      settings.friction_low,
      settings.friction_standard,
      settings.friction_highway,
    )
    feedforward += self._friction(friction_input, lateral_accel_deadzone, friction)

    freeze_integrator = bool(steer_limited_by_safety or CS.steeringPressed or v_ego < 5.0)
    internal_output = self.pid.update(error, feedforward, freeze_integrator)
    return ClassicTorqueCandidateResult(
      output=-internal_output,
      error=error,
      p=self.pid.p,
      i=self.pid.i,
      d=self.pid.d,
      f=self.pid.f,
      actual_curvature=actual_curvature,
      actual_lateral_accel=actual_lateral_accel,
      desired_lateral_accel=desired_lateral_accel,
      measurement_source=curvature_measurement.source,
      yaw_feedback_weight=curvature_measurement.yaw_feedback_weight,
      yaw_feedback_valid=curvature_measurement.yaw_feedback_valid,
      yaw_feedback_fallback_reason=curvature_measurement.fallback_reason,
    )


__all__ = (
  "ClassicTorqueCandidate",
  "ClassicTorqueCandidateResult",
  "ClassicTorqueMeasurement",
  "DEFAULT_FRICTION",
  "DEFAULT_LAT_ACCEL_FACTOR",
  "DEFAULT_TORQUE_SHARE_PERCENT",
  "FRICTION_LOW_STANDARD_TRANSITION_MPH",
  "FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH",
  "FRICTION_TRANSITION_HALF_WIDTH_MPH",
  "InterpolatedTorquePifSettings",
  "InterpolatedTorquePifSettingsLatch",
  "LEGACY_TORQUE_FRICTION_THRESHOLD",
  "LEGACY_TORQUE_KF",
  "LEGACY_TORQUE_KI",
  "LEGACY_TORQUE_KP",
  "LEGACY_TORQUE_LOW_SPEED_X",
  "LEGACY_TORQUE_LOW_SPEED_Y",
  "LEGACY_TORQUE_YAW_BLEND_X",
  "LegacyTorquePid",
  "convex_torque_pif_blend",
  "maybe_blend_interpolated_torque_pif",
  "resolve_interpolated_torque_pif_settings",
  "select_classic_torque_measurement",
  "should_run_pif_tune_learner",
  "speed_banded_friction",
  "supports_interpolated_torque_pif",
)
