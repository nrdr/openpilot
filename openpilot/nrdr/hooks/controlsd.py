import math

from openpilot.nrdr.params import get_live_params
from openpilot.nrdr.params.snapshots import _bool_value
from openpilot.nrdr.features.lateral.live_tuning import LiveTorqueTransition
from openpilot.nrdr.features.lateral.torque_output_filter import HondaTorqueOutputFilter, torque_lpf_tau
from openpilot.nrdr.features.lateral.lane_change_tuning import LaneChangeEntry, shape_lane_change_curvature
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  SteerRatioModeLatch,
  resolve_steer_ratio_selection,
)


def initialize_live_parameter_settings(controls) -> None:
  controls.nrdr_live_params = get_live_params()
  controls.steer_ratio_latch = SteerRatioModeLatch(
    resolve_steer_ratio_selection(controls.CP, controls.nrdr_live_params.snapshot),
  )
  controls.nrdr_lateral_settings_active = False
  controls.nrdr_live_torque_transition = LiveTorqueTransition()
  controls.nrdr_torque_output_filter = HondaTorqueOutputFilter()
  controls.nrdr_lane_change_entry = LaneChangeEntry()
  controls.nrdr_last_valid_comma_ratio = max(float(controls.CP.steerRatio), 0.1)
  refresh_live_parameter_settings(controls, None)


def refresh_live_parameter_settings(controls, snapshot=None) -> None:
  snapshot = controls.nrdr_live_params.snapshot if snapshot is None else snapshot
  controls.learn_stiffness = _bool_value(snapshot.get("NrdrLearnStiffness"))
  controls.learn_angle_offset = _bool_value(snapshot.get("NrdrLearnAngleOffset"))


def finalize_lateral_torque(controls, torque: float, CS, active: bool, dt: float) -> float:
  torque = controls.nrdr_live_torque_transition.update(
    torque, controls.nrdr_lateral_snapshot, active, bool(CS.steeringPressed), dt,
  )
  if controls.CP.brand == "honda":
    # Reuse the typed, background-refreshed Honda settings and their existing
    # defaults; no Params reads or second set of LPF controls in this loop.
    live = controls.CI.interface_config.honda.provider.get_live_tuning(refresh_if_uninitialized=False)
    unfiltered = torque
    torque = controls.nrdr_torque_output_filter.update(torque, active, CS.vEgo, live, dt)
    signature = (bool(live.torque_lpf_enabled), live.lpf_tau_low, live.lpf_tau_standard, live.lpf_tau_highway)
    if signature != getattr(controls, "nrdr_lpf_report_signature", None):
      controls.nrdr_lpf_report_signature = signature
      # Report the exact Honda snapshot consumed here, not requested UI values.
      # Configuration changes only; the worker performs all logging off-thread.
      reporter = getattr(controls, "nrdr_live_params", None)
      if reporter is not None:
        reporter.record_applied_settings(
          "honda_torque_lpf", live.generation, enabled=signature[0],
          tau_low=signature[1], tau_standard=signature[2], tau_highway=signature[3],
          selected_tau=torque_lpf_tau(CS.vEgo, *signature[1:]) if signature[0] else 0.0,
          active=bool(active), speed_ms=float(CS.vEgo), input_torque=float(unfiltered), output_torque=float(torque),
        )
  return torque


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
  """Capture a single live snapshot for geometry, PID/blend and lane centering."""
  snapshot = controls.nrdr_live_params.snapshot
  controls.nrdr_lateral_snapshot = snapshot
  refresh_live_parameter_settings(controls, snapshot)
  if hasattr(controls, "update_lane_centering_params"):
    controls.update_lane_centering_params(snapshot)
  if hasattr(controls.LaC, "set_live_tuning_snapshot"):
    controls.LaC.set_live_tuning_snapshot(snapshot)
  candidate = resolve_steer_ratio_selection(controls.CP, snapshot, _held_comma_ratio(controls, live_params))
  selection = controls.steer_ratio_latch.update(candidate, lat_active)
  # Record requested vs actually accepted geometry outside the realtime loop.
  # Unlike the ratio itself this signature does not change with wheel angle.
  signature = (candidate.requested_label, selection.effective_label, controls.steer_ratio_latch.rejected_reason,
               snapshot.get("NrdrSteerRatioMode"), snapshot.get("NrdrSteerRatioHybrid"),
               snapshot.get("NrdrSteerRatioSourceB"), snapshot.get("NrdrSteerRatioBlendStart"), bool(lat_active),
               snapshot.get("NrdrSteerRatioManualCenter"), snapshot.get("NrdrSteerRatioManualFinal"))
  if signature != getattr(controls, "nrdr_geometry_report_signature", None):
    controls.nrdr_geometry_report_signature = signature
    if hasattr(controls.nrdr_live_params, "record_applied_settings"):
      controls.nrdr_live_params.record_applied_settings(
        "steer_ratio_geometry", getattr(snapshot, "generation", 0), active=signature[7],
        requested=signature[0], effective=signature[1], rejected_reason=signature[2],
        source_a=signature[3], hybrid=signature[4], source_b=signature[5], blend_start=signature[6],
        requested_manual_center=signature[8], requested_manual_final=signature[9],
        effective_manual_center=selection.manual_center, effective_manual_final=selection.manual_final,
      )
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


def lane_change_request(controls, CS, model, live_params, desired_curvature: float, active: bool, dt: float) -> float:
  """Command-only entry shaping before the existing curvature safety limiter."""
  enabled = controls.CP.brand == "honda" and controls.steer_ratio_latch.selection.available
  reduction = controls.nrdr_lane_change_entry.update(
    active=active and enabled and not controls.sm.valid['lateralManeuverPlan'],
    valid=bool(controls.sm.all_checks(['modelV2'])),
    state=model.meta.laneChangeState.raw, direction=model.meta.laneChangeDirection.raw,
    driver_override=bool(CS.steeringPressed), settings=controls.nrdr_lateral_snapshot, dt=dt,
  )
  shaped_curvature = shape_lane_change_curvature(
    controls.steer_ratio_latch.selection, controls.VM, CS.steeringAngleDeg, CS.vEgo, live_params.roll,
    desired_curvature, reduction,
  )
  # Queue consumed settings and command telemetry, never disk I/O in the control loop.
  entry = controls.nrdr_lane_change_entry
  signature = (entry.was_starting, entry.reduction, entry.return_seconds, entry.direction, enabled, reduction > 0.0)
  report_age = getattr(controls, "nrdr_lane_change_report_age", 0.0) + dt
  if signature != getattr(controls, "nrdr_lane_change_report_signature", None) or (reduction > 0.0 and report_age >= 0.1):
    controls.nrdr_lane_change_report_signature = signature
    report_age = 0.0
    controls.nrdr_live_params.record_applied_settings(
      "lane_change_entry", getattr(controls.nrdr_lateral_snapshot, "generation", 0),
      starting=entry.was_starting, captured_reduction=entry.reduction, return_seconds=entry.return_seconds,
      direction=entry.direction, supported=enabled, envelope_reduction=reduction,
      requested_curvature=desired_curvature, shaped_curvature=shaped_curvature,
      geometry=controls.steer_ratio_latch.selection.effective_label,
    )
  controls.nrdr_lane_change_report_age = report_age
  return shaped_curvature


def apply_hud_lead(hud_control, lead) -> None:
  hud_control.leadDistance = float(lead.dRel) if lead.present else 0.0
  hud_control.leadVLead = float(lead.vLead) if lead.present else 0.0
