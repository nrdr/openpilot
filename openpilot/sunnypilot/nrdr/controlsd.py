from openpilot.sunnypilot.nrdr.live_params import ENGAGEMENT_LATCHED_LATERAL_GROUPS, get_live_params
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import SteerRatioResolver


def initialize_live_parameter_settings(controls) -> None:
  controls.nrdr_live_params = get_live_params()
  controls.nrdr_lateral_active = False
  controls.steer_ratio_resolver = SteerRatioResolver(controls.CP, controls.nrdr_live_params.snapshot)
  refresh_live_parameter_settings(controls, None)


def refresh_engagement_latches(controls, lateral_active: bool) -> bool:
  """Synchronously refresh the nine latched tuning Params once, only on disengagement."""
  falling_edge = controls.nrdr_lateral_active and not lateral_active
  controls.nrdr_lateral_active = lateral_active
  if not falling_edge:
    return False
  return controls.nrdr_live_params.refresh_groups_atomic(ENGAGEMENT_LATCHED_LATERAL_GROUPS)


def refresh_live_parameter_settings(controls, _params) -> None:
  snapshot = controls.nrdr_live_params.snapshot
  controls.learn_stiffness = snapshot.get_bool("NrdrLearnStiffness")
  controls.learn_angle_offset = snapshot.get_bool("NrdrLearnAngleOffset")


def vehicle_model_params(controls, live_params) -> tuple[float, float, float]:
  stiffness = live_params.stiffnessFactor if controls.learn_stiffness else 1.0
  angle_offset = live_params.angleOffsetDeg if controls.learn_angle_offset else 0.0
  return max(stiffness, 0.1), max(controls.CP.steerRatio, 0.1), angle_offset


def stopping_inputs(calibrated_pose, longitudinal_plan) -> tuple[float | None, float | None]:
  pitch = float(calibrated_pose.orientation.xyz[1]) if calibrated_pose is not None else None
  distance = None
  if longitudinal_plan.hasLead and len(longitudinal_plan.leadTrajectoryX0) > 0:
    distance = float(longitudinal_plan.leadTrajectoryX0[0])
  return pitch, distance


def apply_hud_lead(hud_control, lead) -> None:
  hud_control.leadDistance = float(lead.dRel) if lead.present else 0.0
  hud_control.leadVLead = float(lead.vLead) if lead.present else 0.0
