from dataclasses import dataclass


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
