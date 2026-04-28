import math
from collections import deque

import numpy as np

from cereal import log
from opendbc.car.lateral import get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt

KP = 0.4
KF = 1.0  # full feedforward; v0 torque model (LAF=2.5) is well-calibrated
KI = 0.1
KD = 0.0

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP = [250, 120, 65, 45, 18.0, 8.0, 4.5, 2.0, KP]

LP_FILTER_CUTOFF_HZ = 1.2
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0
FRICTION_THRESHOLD = 0.3
VERSION = 0


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt=0.01):
    # LatControl signature differs across forks; support both.
    try:
      super().__init__(CP, CP_SP, CI, dt)
      self.dt = dt
    except TypeError:
      super().__init__(CP, CP_SP, CI)
      self.dt = dt

    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()

    # PIDController supports scheduled gains by passing [bp, values].
    # Avoid mutating gains after construction; the controller interpolates internally.
    kf = float(getattr(self.torque_params, "kf", KF))
    self.pid = PIDController(
      [INTERP_SPEEDS, KP_INTERP],
      KI,
      k_f=kf,
      k_d=KD,
      rate=1.0 / self.dt,
    )

    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

    # Blinker-based friction fade for smoother lane changes and manual lane moves.
    self.friction_scale = FirstOrderFilter(1.0, 0.25, self.dt)

    # Comma-style latency compensation buffer.
    self.lat_accel_request_buffer_len = max(1, int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt))
    self.lat_accel_request_buffer = deque(
      [0.0] * self.lat_accel_request_buffer_len,
      maxlen=self.lat_accel_request_buffer_len
    )

    # Measurement derivative filter for stability.
    self.previous_measurement = 0.0
    self.measurement_rate_filter = FirstOrderFilter(
      0.0,
      1.0 / (2.0 * np.pi * LP_FILTER_CUTOFF_HZ),
      self.dt
    )

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction
    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(
      self.lateral_accel_from_torque(self.steer_max, self.torque_params),
      self.lateral_accel_from_torque(-self.steer_max, self.torque_params)
    )

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay=None):
    # Allow extension override of torque params.
    if self.extension.update_override_torque_params(self.torque_params):
      self.update_limits()

    pid_log = log.ControlsState.LateralTorqueState.new_message()
    pid_log.version = VERSION

    if not active:
      pid_log.active = False
      return -0.0, 0.0, pid_log

    # Measurements and deadzones.
    measured_curvature = -VM.calc_curvature(
      math.radians(CS.steeringAngleDeg - params.angleOffsetDeg),
      CS.vEgo,
      params.roll
    )
    measurement = measured_curvature * CS.vEgo ** 2

    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY

    # Latency-compensated setpoint.
    if lat_delay is None:
      lat_delay = float(getattr(params, "latDelay", self.dt))
    lat_delay = float(max(lat_delay, self.dt))

    delay_frames = int(np.clip(lat_delay / self.dt, 1, self.lat_accel_request_buffer_len))
    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]

    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.lat_accel_request_buffer.append(future_desired_lateral_accel)

    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    desired_lateral_jerk = (future_desired_lateral_accel - expected_lateral_accel) / lat_delay

    measurement_rate = float(self.measurement_rate_filter.update((measurement - self.previous_measurement) / self.dt))
    self.previous_measurement = measurement

    setpoint = lat_delay * desired_lateral_jerk + expected_lateral_accel
    error = setpoint - measurement

    # Feedforward and friction.
    ff = gravity_adjusted_future_lateral_accel
    ff -= float(self.torque_params.latAccelOffset)

    lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
    target_scale = 0.0 if lane_change else 1.0
    friction_scale = float(self.friction_scale.update(target_scale))

    friction_input = error
    friction = get_friction(friction_input, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)
    ff += friction_scale * friction

    # PID in lateral-accel space, converted to torque at the end.
    pid_log.error = float(error)

    freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
    output_lataccel = self.pid.update(
      error,
      error_rate=-measurement_rate,
      speed=CS.vEgo,
      feedforward=ff,
      freeze_integrator=freeze_integrator,
    )
    output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

    # Extension hook.
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
    pid_log.saturated = bool(self._check_saturation(
      self.steer_max - abs(output_torque) < 1e-3,
      CS,
      steer_limited_by_safety,
      curvature_limited
    ))

    return -output_torque, 0.0, pid_log
