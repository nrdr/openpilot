import math
import numpy as np
from collections import deque

from cereal import log
from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt


KP = 0.8
KI = 0.15

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP = [250, 120, 65, 30, 11.5, 5.5, 3.5, 2.0, KP]

LP_FILTER_CUTOFF_HZ = 1.2
JERK_LOOKAHEAD_SECONDS = 0.19
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0
VERSION = 1

FRICTION_X = [0.4, 0.6]
FRICTION_Y = [1.0, 0.25]


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()

    # Feedforward gain was removed from some builds' capnp schema and/or PID API.
    # Preserve legacy behavior by scaling the feedforward term externally.
    self.kf = float(getattr(self.torque_params, "kf", 0.5))

    self.pid = PIDController([INTERP_SPEEDS, KP_INTERP], KI, rate=1/self.dt)

    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.lat_accel_request_buffer_len = int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt)
    self.lat_accel_request_buffer = deque(
      [0.] * self.lat_accel_request_buffer_len,
      maxlen=self.lat_accel_request_buffer_len
    )

    self.lookahead_frames = int(JERK_LOOKAHEAD_SECONDS / self.dt)
    self.jerk_filter = FirstOrderFilter(0.0, 1 / (2 * np.pi * LP_FILTER_CUTOFF_HZ), self.dt)

    self.friction_scale = FirstOrderFilter(1.0, 0.25, self.dt)

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction

    self.kf = float(getattr(self.torque_params, "kf", self.kf))

    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(
      self.lateral_accel_from_torque(self.steer_max, self.torque_params),
      self.lateral_accel_from_torque(-self.steer_max, self.torque_params)
    )

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):

    if self.extension.update_override_torque_params(self.torque_params):
      self.update_limits()

    pid_log = log.ControlsState.LateralTorqueState.new_message()
    pid_log.version = VERSION

    measured_curvature = -VM.calc_curvature(
      math.radians(CS.steeringAngleDeg - params.angleOffsetDeg),
      CS.vEgo,
      params.roll
    )

    measurement = measured_curvature * CS.vEgo ** 2
    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.lat_accel_request_buffer.append(future_desired_lateral_accel)

    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY

    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    delay_frames = int(np.clip(lat_delay / self.dt + 1, 1, self.lat_accel_request_buffer_len))
    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]
    setpoint = expected_lateral_accel
    error = setpoint - measurement

    lookahead_idx = int(np.clip(-delay_frames + self.lookahead_frames,
                                -self.lat_accel_request_buffer_len + 1, -2))
    raw_lateral_jerk = (
      (self.lat_accel_request_buffer[lookahead_idx + 1] -
       self.lat_accel_request_buffer[lookahead_idx - 1]) / (2 * self.dt)
    )
    desired_lateral_jerk = self.jerk_filter.update(raw_lateral_jerk)

    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    ff = gravity_adjusted_future_lateral_accel

    ff -= self.torque_params.latAccelOffset

    lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
    target_scale = 0.0 if lane_change else 1.0
    friction_scale = float(self.friction_scale.update(target_scale))

    desired_lataccel_mag = abs(future_desired_lateral_accel)
    friction_error_scale = float(np.interp(desired_lataccel_mag, FRICTION_X, FRICTION_Y))

    friction_input = error * friction_error_scale
    friction = get_friction(friction_input, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)
    ff += friction_scale * friction

    if not active:
      output_torque = 0.0
      pid_log.active = False
    else:
      pid_log.error = float(error)

      freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5

      # Apply legacy feedforward scaling externally to preserve prior tuning behavior.
      ff_pid = ff * self.kf

      output_lataccel = self.pid.update(
        pid_log.error,
        speed=CS.vEgo,
        feedforward=ff_pid,
        freeze_integrator=freeze_integrator
      )

      output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

      pid_log, output_torque = self.extension.update(
        CS, VM, self.pid, params, ff, pid_log, setpoint, measurement, calibrated_pose, roll_compensation,
        future_desired_lateral_accel, measurement, lateral_accel_deadzone, gravity_adjusted_future_lateral_accel,
        desired_curvature, measured_curvature, steer_limited_by_safety, output_torque
      )

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque)
      pid_log.actualLateralAccel = float(measurement)
      pid_log.desiredLateralAccel = float(setpoint)
      pid_log.desiredLateralJerk = float(desired_lateral_jerk)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited
      ))

    return -output_torque, 0.0, pid_log
