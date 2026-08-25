from dataclasses import dataclass, field
import math
from typing import Protocol

from openpilot.nrdr.params.profiles import (
  STEER_RATIO_ENDPOINT_PROFILE_BY_FP,
  STEER_RATIO_ENDPOINT_PROFILES,
  SteerRatioEndpointProfile,
  get_steer_ratio_endpoint_profile,
)


FIRMWARE_LEGACY_BLEND_START_DEG = 70.0
FIRMWARE_LEGACY_BLEND_END_DEG = 90.0
LANE_CHANGE_SR_FADE_SECONDS = 1.5


class FirmwareVgrMap(Protocol):
  def linear_to_physical(self, angle_deg: float) -> float: ...
  def linear_to_physical_slope(self, angle_deg: float) -> float: ...
  def physical_to_linear(self, angle_deg: float) -> float: ...


@dataclass
class LaneChangeSteerRatioFade:
  dt: float
  duration: float = LANE_CHANGE_SR_FADE_SECONDS
  _was_starting: bool = field(init=False, default=False)
  _elapsed: float = field(init=False)

  def __post_init__(self) -> None:
    self.reset()

  def reset(self) -> None:
    self._was_starting = False
    self._elapsed = self.duration

  def update(self, starting: bool) -> float:
    if starting and not self._was_starting:
      self._elapsed = 0.0
    weight = max(1.0 - self._elapsed / self.duration, 0.0)
    self._elapsed = min(self._elapsed + self.dt, self.duration)
    self._was_starting = starting
    return weight


def dual_bp_ratio(angle_deg: float, center_ratio: float, outer_ratio: float, outer_angle: float) -> float:
  angle_weight = min(abs(angle_deg) / outer_angle, 1.0)
  return center_ratio + (outer_ratio - center_ratio) * angle_weight


def dual_bp_desired_angle(linear_angle_deg: float, center_ratio: float,
                          outer_ratio: float, outer_angle: float) -> float:
  """Solve y = (linear / center) * dual_bp_ratio(y) without measured-angle feedback."""
  magnitude = abs(linear_angle_deg)
  road_angle_factor = magnitude / center_ratio
  outer_candidate = road_angle_factor * outer_ratio
  if outer_candidate >= outer_angle:
    desired = outer_candidate
  else:
    denominator = 1.0 - road_angle_factor * (outer_ratio - center_ratio) / outer_angle
    desired = magnitude / denominator
  return math.copysign(desired, linear_angle_deg)


def _dual_bp_desired_slope(linear_angle_deg: float, center_ratio: float,
                           outer_ratio: float, outer_angle: float) -> float:
  road_angle_factor = abs(linear_angle_deg) / center_ratio
  if road_angle_factor * outer_ratio >= outer_angle:
    return outer_ratio / center_ratio
  denominator = 1.0 - road_angle_factor * (outer_ratio - center_ratio) / outer_angle
  return 1.0 / denominator ** 2


def _hermite_value(x: float, x0: float, x1: float, y0: float, y1: float,
                   slope0: float, slope1: float) -> float:
  interval = x1 - x0
  t = (x - x0) / interval
  t2 = t * t
  t3 = t2 * t
  return ((2.0 * t3 - 3.0 * t2 + 1.0) * y0
          + (t3 - 2.0 * t2 + t) * interval * slope0
          + (-2.0 * t3 + 3.0 * t2) * y1
          + (t3 - t2) * interval * slope1)


def _hermite_minimum_slope(x0: float, x1: float, y0: float, y1: float,
                           slope0: float, slope1: float) -> float:
  interval = x1 - x0
  cubic = 2.0 * y0 - 2.0 * y1 + interval * (slope0 + slope1)
  quadratic = -3.0 * y0 + 3.0 * y1 - interval * (2.0 * slope0 + slope1)
  linear = interval * slope0
  candidates = [linear, 3.0 * cubic + 2.0 * quadratic + linear]
  if abs(cubic) > 1e-12:
    vertex = -quadratic / (3.0 * cubic)
    if 0.0 < vertex < 1.0:
      candidates.append(3.0 * cubic * vertex ** 2 + 2.0 * quadratic * vertex + linear)
  return min(candidates) / interval


@dataclass(frozen=True)
class FirmwareLegacySteerRatioCurve:
  """Deterministic desired-angle map joining exact firmware VGR to the legacy dual-BP curve."""
  vgr: FirmwareVgrMap
  center_ratio: float
  outer_ratio: float
  outer_angle: float
  transition_start_linear: float = field(init=False, default=0.0)
  transition_end_linear: float = field(init=False, default=0.0)
  firmware_slope: float = field(init=False, default=0.0)
  legacy_slope: float = field(init=False, default=0.0)
  valid: bool = field(init=False, default=False)

  def __post_init__(self) -> None:
    values = (self.center_ratio, self.outer_ratio, self.outer_angle)
    if not all(math.isfinite(value) and value > 0.0 for value in values):
      return
    if self.outer_angle <= FIRMWARE_LEGACY_BLEND_END_DEG:
      return

    start_linear = abs(self.vgr.physical_to_linear(FIRMWARE_LEGACY_BLEND_START_DEG))
    end_ratio = dual_bp_ratio(FIRMWARE_LEGACY_BLEND_END_DEG, self.center_ratio,
                              self.outer_ratio, self.outer_angle)
    end_linear = self.center_ratio * FIRMWARE_LEGACY_BLEND_END_DEG / end_ratio
    firmware_slope = self.vgr.linear_to_physical_slope(start_linear)
    legacy_slope = _dual_bp_desired_slope(end_linear, self.center_ratio,
                                          self.outer_ratio, self.outer_angle)
    derived = (start_linear, end_linear, firmware_slope, legacy_slope)
    if not all(math.isfinite(value) and value > 0.0 for value in derived) or end_linear <= start_linear:
      return

    minimum_slope = _hermite_minimum_slope(
      start_linear, end_linear,
      FIRMWARE_LEGACY_BLEND_START_DEG, FIRMWARE_LEGACY_BLEND_END_DEG,
      firmware_slope, legacy_slope,
    )
    if not math.isfinite(minimum_slope) or minimum_slope <= 0.0:
      return

    object.__setattr__(self, "transition_start_linear", start_linear)
    object.__setattr__(self, "transition_end_linear", end_linear)
    object.__setattr__(self, "firmware_slope", firmware_slope)
    object.__setattr__(self, "legacy_slope", legacy_slope)
    object.__setattr__(self, "valid", True)

  def desired_angle(self, linear_angle_deg: float) -> float:
    if not self.valid:
      return self.vgr.linear_to_physical(linear_angle_deg)

    magnitude = abs(linear_angle_deg)
    if magnitude <= self.transition_start_linear:
      return self.vgr.linear_to_physical(linear_angle_deg)
    if magnitude >= self.transition_end_linear:
      return dual_bp_desired_angle(linear_angle_deg, self.center_ratio,
                                   self.outer_ratio, self.outer_angle)

    desired = _hermite_value(
      magnitude, self.transition_start_linear, self.transition_end_linear,
      FIRMWARE_LEGACY_BLEND_START_DEG, FIRMWARE_LEGACY_BLEND_END_DEG,
      self.firmware_slope, self.legacy_slope,
    )
    return math.copysign(desired, linear_angle_deg)


__all__ = (
  "FIRMWARE_LEGACY_BLEND_END_DEG",
  "FIRMWARE_LEGACY_BLEND_START_DEG",
  "LANE_CHANGE_SR_FADE_SECONDS",
  "STEER_RATIO_ENDPOINT_PROFILE_BY_FP",
  "STEER_RATIO_ENDPOINT_PROFILES",
  "FirmwareLegacySteerRatioCurve",
  "FirmwareVgrMap",
  "LaneChangeSteerRatioFade",
  "SteerRatioEndpointProfile",
  "dual_bp_desired_angle",
  "dual_bp_ratio",
  "get_steer_ratio_endpoint_profile",
)
