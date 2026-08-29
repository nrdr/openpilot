from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY, CV
from openpilot.sunnypilot.nrdr.params import read_bool, read_float


PARAM_BLEND = "NrdrInterpolatedTorquePifBlend"
PARAM_TORQUE_SHARE = "NrdrInterpolatedTorqueShare"
PARAM_LAT_ACCEL_FACTOR = "NrdrInterpolatedTorqueLatAccelFactor"
PARAM_FRICTION = "NrdrInterpolatedTorqueFriction"
PARAM_FRICTION_STANDARD = "NrdrInterpolatedTorqueFrictionStandard"
PARAM_FRICTION_HIGHWAY = "NrdrInterpolatedTorqueFrictionHighway"
PARAM_KEYS = (
  PARAM_BLEND,
  PARAM_TORQUE_SHARE,
  PARAM_LAT_ACCEL_FACTOR,
  PARAM_FRICTION,
  PARAM_FRICTION_STANDARD,
  PARAM_FRICTION_HIGHWAY,
)

TORQUE_SHARE_DEFAULT = 50.0
LAT_ACCEL_FACTOR_DEFAULT = 5.0
FRICTION_LOW_DEFAULT = 0.12
FRICTION_STANDARD_DEFAULT = 0.10
FRICTION_HIGHWAY_DEFAULT = 0.06
# Compatibility name for callers which still mean the legacy/low band.
FRICTION_DEFAULT = FRICTION_LOW_DEFAULT
FRICTION_LOW_STANDARD_TRANSITION_MPH = 25.0
FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH = 50.0
FRICTION_TRANSITION_HALF_WIDTH_MPH = 1.0

# The normal, non-neural controller at f13de17baffd152c321fd179dcc764af3eb1433f.
KP = 0.5
KI = 0.1
KF = 1.0
LOW_SPEED_X = (0.0, 10.0, 20.0, 30.0)
LOW_SPEED_Y = (30.0, 17.0, 10.0, 5.0)
FRICTION_THRESHOLD = 0.3


@dataclass(frozen=True)
class InterpolatedTorqueSettings:
  enabled: bool = False
  torque_share: float = TORQUE_SHARE_DEFAULT / 100.0
  lat_accel_factor: float = LAT_ACCEL_FACTOR_DEFAULT
  friction_low: float = FRICTION_LOW_DEFAULT
  friction_standard: float = FRICTION_STANDARD_DEFAULT
  friction_highway: float = FRICTION_HIGHWAY_DEFAULT

  @property
  def friction(self) -> float:
    """Compatibility alias for callers that still mean the legacy low band."""
    return self.friction_low


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class ClassicTorqueMeasurement:
  actual_curvature: float
  source: str
  yaw_feedback_weight: float
  yaw_feedback_valid: bool
  fallback_reason: str = ""


class LegacyPIDController:
  """The f13de17 PID state update, kept local so later PID changes cannot alter it."""

  def __init__(self, k_p: float, k_i: float, k_f: float = 0.0, k_d: float = 0.0,
               pos_limit: float = 1e308, neg_limit: float = -1e308, rate: float = 100.0):
    self.k_p = float(k_p)
    self.k_i = float(k_i)
    self.k_f = float(k_f)
    self.k_d = float(k_d)
    self.pos_limit = float(pos_limit)
    self.neg_limit = float(neg_limit)
    self.i_unwind_rate = 0.3 / float(rate)
    self.i_rate = 1.0 / float(rate)
    self.reset()

  def reset(self) -> None:
    self.p = 0.0
    self.i = 0.0
    self.d = 0.0
    self.f = 0.0
    self.control = 0.0

  def update(self, error: float, error_rate: float = 0.0, speed: float = 0.0,
             override: bool = False, feedforward: float = 0.0,
             freeze_integrator: bool = False) -> float:
    del speed
    error = float(error)
    self.p = error * self.k_p
    self.f = float(feedforward) * self.k_f
    self.d = float(error_rate) * self.k_d

    if override:
      self.i -= self.i_unwind_rate * float(np.sign(self.i))
    else:
      candidate_i = self.i + error * self.k_i * self.i_rate
      candidate_control = self.p + candidate_i + self.d + self.f
      unwinds_from_positive_limit = error >= 0.0 and (candidate_control <= self.pos_limit or candidate_i < 0.0)
      unwinds_from_negative_limit = error <= 0.0 and (candidate_control >= self.neg_limit or candidate_i > 0.0)
      if (unwinds_from_positive_limit or unwinds_from_negative_limit) and not freeze_integrator:
        self.i = candidate_i

    self.control = float(np.clip(self.p + self.i + self.d + self.f, self.neg_limit, self.pos_limit))
    return self.control


def settings_from_params(params) -> InterpolatedTorqueSettings:
  return InterpolatedTorqueSettings(
    enabled=read_bool(params, PARAM_BLEND),
    torque_share=read_float(params, PARAM_TORQUE_SHARE, TORQUE_SHARE_DEFAULT, 0.0, 100.0) / 100.0,
    lat_accel_factor=read_float(params, PARAM_LAT_ACCEL_FACTOR, LAT_ACCEL_FACTOR_DEFAULT, 0.1, 10.0),
    friction_low=read_float(params, PARAM_FRICTION, FRICTION_LOW_DEFAULT, 0.0, 1.0),
    friction_standard=read_float(params, PARAM_FRICTION_STANDARD, FRICTION_STANDARD_DEFAULT, 0.0, 1.0),
    friction_highway=read_float(params, PARAM_FRICTION_HIGHWAY, FRICTION_HIGHWAY_DEFAULT, 0.0, 1.0),
  )


def resolve_interpolated_torque_pif_settings(params, supported: bool) -> InterpolatedTorqueSettings:
  settings = settings_from_params(params)
  return InterpolatedTorqueSettings(
    enabled=bool(supported and settings.enabled),
    torque_share=settings.torque_share,
    lat_accel_factor=settings.lat_accel_factor,
    friction_low=settings.friction_low,
    friction_standard=settings.friction_standard,
    friction_highway=settings.friction_highway,
  )


def speed_banded_friction(v_ego: float, low: float, standard: float, highway: float) -> float:
  """Select friction by speed with continuous two-mph handoffs around 25 and 50 mph."""
  low = float(low)
  standard = float(standard)
  highway = float(highway)
  if low == standard == highway:
    return low

  v_ego = float(v_ego)
  if not np.isfinite(v_ego):
    return low

  low_blend_start = (FRICTION_LOW_STANDARD_TRANSITION_MPH - FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  low_blend_end = (FRICTION_LOW_STANDARD_TRANSITION_MPH + FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  highway_blend_start = (FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH - FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  highway_blend_end = (FRICTION_STANDARD_HIGHWAY_TRANSITION_MPH + FRICTION_TRANSITION_HALF_WIDTH_MPH) * CV.MPH_TO_MS
  if v_ego <= low_blend_start:
    return low
  if v_ego < low_blend_end:
    return float(np.interp(v_ego, (low_blend_start, low_blend_end), (low, standard)))
  if v_ego <= highway_blend_start:
    return standard
  if v_ego < highway_blend_end:
    return float(np.interp(v_ego, (highway_blend_start, highway_blend_end), (standard, highway)))
  return highway


def is_interpolated_torque_pif_supported(CP, CP_SP) -> bool:
  if CP is None or CP_SP is None or str(getattr(CP, "brand", "")).lower() != "honda":
    return False
  if not bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value):
    return False

  try:
    tuning = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    tuning = ""
  is_pid = tuning == "pid"
  is_clarity_hybrid = str(getattr(CP, "carFingerprint", "")) == "HONDA_CLARITY" and tuning == "torque"
  return is_pid or is_clarity_hybrid


def blend_commands(pif_command: float, torque_command: float, torque_share: float,
                   steer_max: float = 1.0) -> float:
  share = float(np.clip(torque_share, 0.0, 1.0))
  if share <= 0.0:
    blended = float(pif_command)
  elif share >= 1.0:
    blended = float(torque_command)
  else:
    blended = (1.0 - share) * float(pif_command) + share * float(torque_command)
  return float(np.clip(blended, -abs(steer_max), abs(steer_max)))


def maybe_blend_interpolated_torque_pif(
  pif_output: float,
  settings: InterpolatedTorqueSettings,
  classic_candidate: Callable[[], ClassicTorqueCandidateResult],
  steer_max: float = 1.0,
) -> tuple[float, ClassicTorqueCandidateResult | None]:
  """Evaluate Torque only while enabled, and use exact P/I/F when yaw is unusable."""
  if not settings.enabled:
    return pif_output, None

  classic_result = classic_candidate()
  if not classic_result.yaw_feedback_valid:
    return pif_output, classic_result
  return (
    blend_commands(pif_output, classic_result.output, settings.torque_share, steer_max),
    classic_result,
  )


def select_classic_torque_measurement(angle_curvature: Callable[[], float], v_ego: float,
                                      calibrated_pose) -> ClassicTorqueMeasurement:
  """Reproduce f13's 2-5 m/s angle-to-yaw measurement transition safely."""
  v_ego = float(v_ego)
  requested_yaw_weight = float(np.interp(v_ego, (2.0, 5.0), (0.0, 1.0)))
  if requested_yaw_weight <= 0.0:
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
    (2.0, 5.0),
    (float(angle_curvature()), yaw_curvature),
  ))
  return ClassicTorqueMeasurement(actual_curvature, "angle_yaw_blend", requested_yaw_weight, True)


class LegacyTorqueController:
  """Isolated f13de17 normal torque path with its linear conversion frozen in place."""

  def __init__(self, dt: float, steer_max: float = 1.0):
    self.dt = float(dt)
    self.steer_max = abs(float(steer_max))
    self.pid = LegacyPIDController(
      KP,
      KI,
      k_f=KF,
      pos_limit=self.steer_max,
      neg_limit=-self.steer_max,
      rate=1.0 / self.dt,
    )

  def reset(self) -> None:
    self.pid.reset()

  @staticmethod
  def _apply_deadzone(error: float, deadzone: float) -> float:
    if error > deadzone:
      return error - deadzone
    if error < -deadzone:
      return error + deadzone
    return 0.0

  @staticmethod
  def _direct_friction(error: float, deadzone: float, friction: float) -> float:
    return float(np.interp(
      LegacyTorqueController._apply_deadzone(error, deadzone),
      (-FRICTION_THRESHOLD, FRICTION_THRESHOLD),
      (-friction, friction),
    ))

  def update(self, CS, VM, params, steer_limited_by_safety: bool, desired_curvature: float,
             calibrated_pose, steer_ratio_resolver,
             settings: InterpolatedTorqueSettings) -> ClassicTorqueCandidateResult:
    v_ego = float(CS.vEgo)
    roll = float(getattr(params, "roll", 0.0))
    curvature_measurement = select_classic_torque_measurement(
      lambda: float(steer_ratio_resolver.calc_curvature(
        VM,
        CS.steeringAngleDeg,
        float(getattr(params, "angleOffsetDeg", 0.0)),
        v_ego,
        roll,
      )),
      v_ego,
      calibrated_pose,
    )
    actual_curvature = curvature_measurement.actual_curvature
    if not curvature_measurement.yaw_feedback_valid:
      # Once the f13 path asks for yaw, substituting angle would duplicate the
      # P/I/F sensor path. Preserve every classic PID term and surface an
      # unavailable diagnostic; the wrapper returns exact P/I/F for this frame.
      unavailable = float("nan")
      return ClassicTorqueCandidateResult(
        output=unavailable,
        error=unavailable,
        p=self.pid.p,
        i=self.pid.i,
        d=self.pid.d,
        f=self.pid.f,
        actual_curvature=unavailable,
        actual_lateral_accel=unavailable,
        desired_lateral_accel=float(desired_curvature) * v_ego ** 2,
        measurement_source=curvature_measurement.source,
        yaw_feedback_weight=curvature_measurement.yaw_feedback_weight,
        yaw_feedback_valid=False,
        yaw_feedback_fallback_reason=curvature_measurement.fallback_reason,
      )

    roll_compensation = roll * ACCELERATION_DUE_TO_GRAVITY
    desired_lateral_accel = float(desired_curvature) * v_ego ** 2
    actual_lateral_accel = actual_curvature * v_ego ** 2

    low_speed_factor = float(np.interp(v_ego, LOW_SPEED_X, LOW_SPEED_Y)) ** 2
    setpoint = desired_lateral_accel + low_speed_factor * float(desired_curvature)
    measurement = actual_lateral_accel + low_speed_factor * actual_curvature

    torque_error = (setpoint / settings.lat_accel_factor) - (measurement / settings.lat_accel_factor)

    gravity_adjusted_lateral_accel = desired_lateral_accel - roll_compensation
    feedforward = gravity_adjusted_lateral_accel / settings.lat_accel_factor
    feedforward += self._direct_friction(
      desired_lateral_accel - actual_lateral_accel,
      0.0,
      speed_banded_friction(
        v_ego,
        settings.friction_low,
        settings.friction_standard,
        settings.friction_highway,
      ),
    )

    freeze_integrator = (
      steer_limited_by_safety
      or bool(CS.steeringPressed)
      or v_ego < 5.0
    )
    internal_output = self.pid.update(
      torque_error,
      speed=v_ego,
      feedforward=feedforward,
      freeze_integrator=freeze_integrator,
    )
    return ClassicTorqueCandidateResult(
      output=float(-internal_output),
      error=torque_error,
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


# Keep the feature API parallel with the architecture branch while this branch
# retains the older NRDR module layout.
InterpolatedTorquePifSettings = InterpolatedTorqueSettings
supports_interpolated_torque_pif = is_interpolated_torque_pif_supported
convex_torque_pif_blend = blend_commands
ClassicTorqueCandidate = LegacyTorqueController
