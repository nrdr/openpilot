"""SunnyPilot shell for VFN's f837ca86 Clarity EPS controller.

Uses the source controller's fixed gains, yaw-calibrated rack map, delay schedule
and output filter. NRDR's other lateral tuning does not change this controller.
Optimized lane changes are the explicit owner-requested exception.
"""
import math
import numpy as np

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.nrdr.features.lateral.controller_selection import yaw_controller_available
from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsLateralCore
from openpilot.nrdr.features.lateral.yaw_control_timing import clarity_lateral_delay
from openpilot.nrdr.features.lateral.vfn_geometry import NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_VGR_ANGLE_BP
from openpilot.nrdr.features.lateral.vfn_rack_map import ClarityRackMap
from openpilot.nrdr.features.lateral.latcontrol_pid import _eps_modified_steering_pressed
from openpilot.nrdr.features.lateral.lane_change_tuning import optimized_lane_change_active

VFN_SOURCE_COMMIT = "f837ca86a639b1c20a0ce23bb8acf0ebbc6a05d4"
GAIN_BP = [0.0, 11.175, 11.176, 22.352]
KP = [0.018, 0.024, 0.048, 0.060]
KI = [0.006, 0.008, 0.016, 0.020]
ANGLE_RATE_LIMIT = 300.0


class LatControlVfnEps(LatControl):
  owns_output_filter = True

  def __init__(self, CP, CP_SP, CI, dt):
    if not yaw_controller_available(CP, CP_SP) or CP.lateralTuning.which() != "pid":
      raise ValueError("VFN EPS control requires modified Clarity A020 with PID CarParams")
    super().__init__(CP, CP_SP, CI, dt)
    self.core = HondaEpsLateralCore(GAIN_BP, KP, GAIN_BP, KI, dt)
    self.rack_map = ClarityRackMap(CP.wheelbase, (NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_VGR_ANGLE_BP))
    self.model_v2 = None
    self.prev_angle = 0.0
    self.pressed_duration = 0.0
    self.pressed_prev = False

  def update_model_v2(self, model_v2):
    self.model_v2 = model_v2

  def lateral_delay(self, speed):
    return clarity_lateral_delay(speed)

  def measured_curvature(self, angle, speed, roll):
    return self.rack_map.curvature_from_angle(angle, speed, roll)

  def shape_lane_change_request(self, angle, speed, roll, curvature, reduction):
    # Same command-only reduction as PIF, evaluated in this controller's own
    # rack coordinates, before controlsd's unchanged curvature safety limits.
    if reduction <= 0.0 or not all(math.isfinite(v) for v in (angle, speed, roll, curvature, reduction)):
      return curvature
    zero = self.rack_map.angle_from_curvature(0.0, speed, roll)
    target = self.rack_map.angle_from_curvature(curvature, speed, roll)
    reference = max(abs(angle), 0.01)
    ref_curve = abs(self.rack_map.curvature_from_angle(reference, 0.0, 0.0))
    ratio = math.radians(reference) / max(ref_curve * self.rack_map.wheelbase, 1e-9)
    scale = 1.0 - min(reduction, 5.0, max(0.0, ratio - 1.0)) / ratio
    result = self.rack_map.curvature_from_angle(zero + scale * (target - zero), speed, roll)
    return float(np.clip(result, min(0.0, curvature), max(0.0, curvature)))

  def reset(self):
    super().reset()
    self.core.reset()
    self.pressed_duration = 0.0
    self.pressed_prev = False

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)
    desired = self.rack_map.angle_from_curvature(desired_curvature, CS.vEgo, params.roll)
    if active:
      step = ANGLE_RATE_LIMIT * self.dt
      desired = float(np.clip(desired, self.prev_angle - step, self.prev_angle + step))
    self.prev_angle = desired
    angle = desired + params.angleOffsetDeg
    pid_log.steeringAngleDesiredDeg = angle
    pid_log.angleError = angle - CS.steeringAngleDeg
    if not active:
      self.reset()
      output = 0.0
    else:
      self.pressed_duration, pressed = _eps_modified_steering_pressed(
        bool(CS.steeringPressed), float(CS.steeringTorque), self.core.output,
        self.pressed_duration, self.pressed_prev)
      self.pressed_prev = pressed
      state = 0 if self.model_v2 is None else self.model_v2.meta.laneChangeState.raw
      optimized = optimized_lane_change_active(self.live_tuning_snapshot, state)
      output = self.core.update(desired, params.angleOffsetDeg, CS.steeringAngleDeg, CS.vEgo, params.roll,
                                pressed, steer_limited_by_safety, optimized_lane_change=optimized)
      output = float(np.clip(output, -self.steer_max, self.steer_max))
      pid_log.p = float(self.core.pid.p)
      pid_log.i = float(self.core.pid.i)
      pid_log.f = float(self.core.pid.f)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
    pid_log.active = bool(active)
    pid_log.output = output
    return output, angle, pid_log
