from dataclasses import dataclass, field

from openpilot.nrdr.params.profiles import (
  STEER_RATIO_ENDPOINT_PROFILE_BY_FP,
  STEER_RATIO_ENDPOINT_PROFILES,
  SteerRatioEndpointProfile,
  get_steer_ratio_endpoint_profile,
)


LANE_CHANGE_SR_FADE_SECONDS = 1.5


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


__all__ = (
  "LANE_CHANGE_SR_FADE_SECONDS",
  "STEER_RATIO_ENDPOINT_PROFILE_BY_FP",
  "STEER_RATIO_ENDPOINT_PROFILES",
  "LaneChangeSteerRatioFade",
  "SteerRatioEndpointProfile",
  "get_steer_ratio_endpoint_profile",
)
