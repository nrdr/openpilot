import math
from collections import deque

import numpy as np

from cereal import log
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.car.interfaces import FRICTION_THRESHOLD
from openpilot.selfdrive.controls.lib.drive_helpers import get_friction
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.pid import PIDController
from openpilot.selfdrive.controls.lib.vehicle_model import ACCELERATION_DUE_TO_GRAVITY


KP = 1.0
KI = 0.3
KD = 0.0

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP =      [250, 120, 65,  30, 11.5, 5.5, 3.5, 2.0, KP]

LP_FILTER_CUTOFF_HZ = 1.2
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0


# -----------------------------------------------------------------------------
# Dynamic friction shaping:
# Fade friction as desired lateral accel increases (curvier roads).
# Full friction at/under ~0.4-0.6 m/s^2, reduced friction above.
# -----------------------------------------------------------------------------
FRICTION_X = [0.4, 0.6]    # m/s^2 desired lateral accel magnitude
FRICTION_Y = [1.0, 0.25]   # scale applied to friction input


class LatControlTorque(LatControl):
  def __init__(self, CP, CI, dt):
    super().__init__(CP, CI, dt)

    self.torque_params = CP.lateralTuning.torque
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()

    # PIDController supports scheduled gains via [breakpoints, values] and "speed=" in update().
    self.pid = PIDController([INTERP_SPEEDS, KP_INTERP], KI, k_d=KD, rate=1 / self.dt)

    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.LATACCEL_REQUEST_BUFFER_NUM_FRAMES = max(1, int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt))
    self.requested_lateral_accel_buffer = deque(
      [0.0] * self.LATACCEL_REQUEST_BUFFER_NUM_FRAMES,
      maxlen=self.LATACCEL_REQUEST_BUFFER_NUM_FRAMES
    )

    self.previous_measurement = 0.0
    self.measurement_rate_filter = FirstOrderFilter(
      0.0,
      1 / (2 * np.pi * LP_FILTER_CUTOFF_HZ),
      self.dt
    )

    # Smoothly fade friction out during lane changes to reduce steering “stickiness”.
    self.friction_scale = FirstOrderFilter(1.0, 0.25, self.dt)

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
             curvature_limited, lat_delay, llk, model_data, frogpilot_toggles):
    pid_log = log.ControlsState.LateralTorqueState.new_message()

    output_torque = 0.0

    if not active:
      pid_log.active = False
      return -output_torque, 0.0, pid_log

    # -------------------------------------------------------------------------
    # Measurements and deadzones
    # -------------------------------------------------------------------------
    measured_curvature = -VM.calc_curvature(
      math.radians(CS.steeringAngleDeg - params.angleOffsetDeg),
      CS.vEgo,
      params.roll
    )

    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY

    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    # -------------------------------------------------------------------------
    # Latency-compensated setpoint (Comma-style)
    # -------------------------------------------------------------------------
    lat_delay = float(max(lat_delay, self.dt))
    delay_frames = int(np.clip(lat_delay / self.dt, 1, self.LATACCEL_REQUEST_BUFFER_NUM_FRAMES))

    expected_lateral_accel = self.requested_lateral_accel_buffer[-delay_frames]

    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.requested_lateral_accel_buffer.append(future_desired_lateral_accel)

    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    desired_lateral_jerk = (future_desired_lateral_accel - expected_lateral_accel) / lat_delay

    measurement = measured_curvature * CS.vEgo ** 2
    measurement_rate = float(self.measurement_rate_filter.update((measurement - self.previous_measurement) / self.dt))
    self.previous_measurement = measurement

    setpoint = lat_delay * desired_lateral_jerk + expected_lateral_accel
    error = setpoint - measurement

    # -------------------------------------------------------------------------
    # Feedforward + friction shaping
    # -------------------------------------------------------------------------
    ff = gravity_adjusted_future_lateral_accel
    ff -= self.torque_params.latAccelOffset

    # Fade friction out when either blinker is on.
    left_blinker = bool(getattr(CS, "leftBlinker", False))
    right_blinker = bool(getattr(CS, "rightBlinker", False))
    lane_change = left_blinker or right_blinker

    target_scale = 0.0 if lane_change else 1.0
    friction_scale = float(self.friction_scale.update(target_scale))

    # Reduce friction contribution as desired lateral accel increases (curvier roads).
    desired_lataccel_mag = abs(future_desired_lateral_accel)
    friction_error_scale = float(np.interp(desired_lataccel_mag, FRICTION_X, FRICTION_Y))
    friction_input = error * friction_error_scale

    ff += friction_scale * get_friction(friction_input, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)

    # -------------------------------------------------------------------------
    # PID in lateral-accel space -> torque at end
    # -------------------------------------------------------------------------
    pid_log.error = float(error)

    freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5.0
    output_lataccel = self.pid.update(
      pid_log.error,
      -measurement_rate,
      feedforward=ff,
      speed=CS.vEgo,
      freeze_integrator=freeze_integrator
    )

    output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    pid_log.active = True
    pid_log.p = float(self.pid.p)
    pid_log.i = float(self.pid.i)
    pid_log.d = float(self.pid.d)
    pid_log.f = float(self.pid.f)
    pid_log.output = float(-output_torque)
    pid_log.actualLateralAccel = float(measurement)
    pid_log.desiredLateralAccel = float(setpoint)
    pid_log.saturated = bool(
      self._check_saturation(
        self.steer_max - abs(output_torque) < 1e-3,
        CS,
        steer_limited_by_safety,
        curvature_limited
      )
    )

    # Left is positive in this convention.
    return -output_torque, 0.0, pid_log
