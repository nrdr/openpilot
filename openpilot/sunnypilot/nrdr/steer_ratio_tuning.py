from dataclasses import dataclass, field


LANE_CHANGE_SR_FADE_SECONDS = 1.5


@dataclass(frozen=True)
class SteerRatioEndpointProfile:
  family: str
  fingerprints: tuple[str, ...]
  center_param: str
  outer_param: str
  center_default: float
  outer_default: float
  outer_angle: float

  @property
  def breakpoints(self) -> tuple[float, float]:
    return 0.0, self.outer_angle

  @property
  def default_values(self) -> tuple[float, float]:
    return self.center_default, self.outer_default

  @property
  def param_values(self) -> tuple[tuple[str, float], tuple[str, float]]:
    return (
      (self.center_param, self.center_default),
      (self.outer_param, self.outer_default),
    )


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


STEER_RATIO_ENDPOINT_PROFILES = (
  SteerRatioEndpointProfile(
    family="Clarity",
    fingerprints=("HONDA_CLARITY",),
    center_param="NrdrSteerRatioCenterClarity",
    outer_param="NrdrSteerRatioOuterClarity",
    center_default=18.50,
    outer_default=12.72,
    outer_angle=250.0,
  ),
  SteerRatioEndpointProfile(
    family="10th-gen Civic",
    fingerprints=("HONDA_CIVIC", "HONDA_CIVIC_BOSCH", "HONDA_CIVIC_BOSCH_DIESEL"),
    center_param="NrdrSteerRatioCenterCivic",
    outer_param="NrdrSteerRatioOuterCivic",
    center_default=17.24,
    outer_default=10.93,
    outer_angle=2.22 * 250.0 / 2.41,
  ),
  SteerRatioEndpointProfile(
    family="10th-gen Accord",
    fingerprints=("HONDA_ACCORD",),
    center_param="NrdrSteerRatioCenterAccord",
    outer_param="NrdrSteerRatioOuterAccord",
    center_default=18.31,
    outer_default=11.82,
    outer_angle=2.30 * 250.0 / 2.41,
  ),
  SteerRatioEndpointProfile(
    family="5th-gen CR-V",
    fingerprints=("HONDA_CRV_5G", "HONDA_CRV_HYBRID"),
    center_param="NrdrSteerRatioCenterCrv5g",
    outer_param="NrdrSteerRatioOuterCrv5g",
    center_default=17.94,
    outer_default=12.30,
    outer_angle=2.30 * 250.0 / 2.41,
  ),
  SteerRatioEndpointProfile(
    family="3rd-gen Insight",
    fingerprints=("HONDA_INSIGHT",),
    center_param="NrdrSteerRatioCenterInsight",
    outer_param="NrdrSteerRatioOuterInsight",
    center_default=16.82,
    outer_default=12.58,
    outer_angle=2.54 * 250.0 / 2.41,
  ),
)

STEER_RATIO_ENDPOINT_PROFILE_BY_FP = {
  fingerprint: profile
  for profile in STEER_RATIO_ENDPOINT_PROFILES
  for fingerprint in profile.fingerprints
}


def get_steer_ratio_endpoint_profile(fingerprint: str) -> SteerRatioEndpointProfile | None:
  return STEER_RATIO_ENDPOINT_PROFILE_BY_FP.get(str(fingerprint))
