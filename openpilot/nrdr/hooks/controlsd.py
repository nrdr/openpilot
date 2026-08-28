import math

from openpilot.nrdr.params import get_live_params
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  SteerRatioModeLatch,
  resolve_steer_ratio_selection,
)


def initialize_live_parameter_settings(controls) -> None:
  controls.nrdr_live_params = get_live_params()
  controls.steer_ratio_latch = SteerRatioModeLatch(
    resolve_steer_ratio_selection(controls.CP, controls.nrdr_live_params.snapshot),
  )
  controls.nrdr_last_valid_comma_ratio = max(float(controls.CP.steerRatio), 0.1)
  refresh_live_parameter_settings(controls, None)


def refresh_live_parameter_settings(controls, _params) -> None:
  snapshot = controls.nrdr_live_params.snapshot
  controls.learn_stiffness = snapshot.get_bool("NrdrLearnStiffness")
  controls.learn_angle_offset = snapshot.get_bool("NrdrLearnAngleOffset")


def _valid_comma_ratio(controls, live_params) -> float | None:
  valid = bool(getattr(live_params, "steerRatioValid", False))
  try:
    valid = valid and bool(controls.sm.valid["vehicleParameters"])
  except (AttributeError, KeyError, TypeError):
    pass
  try:
    ratio = float(live_params.steerRatio)
  except (AttributeError, TypeError, ValueError):
    return None
  cp_ratio = max(float(controls.CP.steerRatio), 0.1)
  plausible = 0.5 * cp_ratio <= ratio <= 2.0 * cp_ratio
  return ratio if valid and math.isfinite(ratio) and plausible else None


def _held_comma_ratio(controls, live_params) -> float:
  if not hasattr(controls, "nrdr_last_valid_comma_ratio"):
    controls.nrdr_last_valid_comma_ratio = max(float(controls.CP.steerRatio), 0.1)
  if (ratio := _valid_comma_ratio(controls, live_params)) is not None:
    controls.nrdr_last_valid_comma_ratio = ratio
  return controls.nrdr_last_valid_comma_ratio


def vehicle_model_params(controls, live_params) -> tuple[float, float, float]:
  stiffness = live_params.stiffnessFactor if controls.learn_stiffness else 1.0
  selection = controls.steer_ratio_latch.selection
  steer_ratio = selection.ratio_at(0.0, _held_comma_ratio(controls, live_params))
  angle_offset = live_params.angleOffsetDeg if controls.learn_angle_offset else 0.0
  return max(stiffness, 0.1), max(steer_ratio, 0.1), angle_offset


def vehicle_model_state(controls, live_params, CS, lat_active: bool) -> tuple[float, float, float, float]:
  """Return one latched geometry view for both measured and desired curvature paths."""
  candidate = resolve_steer_ratio_selection(controls.CP, controls.nrdr_live_params.snapshot)
  selection = controls.steer_ratio_latch.update(candidate, lat_active)
  if hasattr(controls.LaC, "set_steer_ratio_selection"):
    controls.LaC.set_steer_ratio_selection(selection)

  stiffness = live_params.stiffnessFactor if controls.learn_stiffness else 1.0
  angle_offset = live_params.angleOffsetDeg if controls.learn_angle_offset else 0.0
  steer_ratio = selection.ratio_at(CS.steeringAngleDeg, _held_comma_ratio(controls, live_params))
  measured_angle = selection.linearize_measured_angle(CS.steeringAngleDeg - angle_offset)
  return max(stiffness, 0.1), max(steer_ratio, 0.1), angle_offset, measured_angle


def stopping_inputs(calibrated_pose, longitudinal_plan) -> tuple[float | None, float | None]:
  pitch = float(calibrated_pose.orientation.xyz[1]) if calibrated_pose is not None else None
  distance = None
  if longitudinal_plan.hasLead and len(longitudinal_plan.leadTrajectoryX0) > 0:
    distance = float(longitudinal_plan.leadTrajectoryX0[0])
  return pitch, distance


def apply_hud_lead(hud_control, lead) -> None:
  hud_control.leadDistance = float(lead.dRel) if lead.present else 0.0
  hud_control.leadVLead = float(lead.vLead) if lead.present else 0.0
