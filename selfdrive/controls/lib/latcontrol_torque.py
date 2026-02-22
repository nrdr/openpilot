import math
from collections import deque

import numpy as np

from cereal import log
from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt

KP = 1.0
KI = 0.1
KD = 0.0

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5.0, 7.5, 10, 15, 18, 22, 30]
KP_INTERP     = [250, 225, 100, 40, 30, 10, 5, 3.2, 2.7, 1.8, KP]

LP_FILTER_CUTOFF_HZ = 1.2
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0

# Friction scaling on straights & turns:
# Scale applied to friction input error as a function of desired lateral accel magnitude.
FRICTION_X = [0.4, 0.6]  # m/s^2 desired lateral accel magnitude

FRICTION_Y_LOW_SPEED = [2.0, 1.0]    # stronger friction comp at low speed
FRICTION_Y_HIGH_SPEED = [0.6, 0.4]  # weaker friction comp at high speed

FRICTION_BLEND_START_MPH = 25.0
FRICTION_BLEND_END_MPH = 30.0
MPH_TO_MS = 0.44704
FRICTION_BLEND_START_MS = FRICTION_BLEND_START_MPH * MPH_TO_MS
FRICTION_BLEND_END_MS = FRICTION_BLEND_END_MPH * MPH_TO_MS

VERSION = 2


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()

    # Restore feedforward gain behavior when available.
    kf = float(getattr(self.torque_params, "kf", 0.5))

    self.pid = PIDController(
      [INTERP_SPEEDS, KP_INTERP],
      KI,
      k_d=KD,
      k_f=kf,
      rate=1.0 / self.dt,
    )

    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

    # Blinker-based friction fade (smooth lane changes / manual lane moves).
    self.friction_scale = FirstOrderFilter(1.0, 0.25, self.dt)

    # Latency compensation buffer (stores desired lateral accel history).
    self.lat_accel_request_buffer_len = max(1, int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt))
    self.lat_accel_request_buffer = deque([0.0] * self.lat_accel_request_buffer_len,
                                          maxlen=self.lat_accel_request_buffer_len)

    # Measurement rate filter (for error_rate / damping / stability).
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
      self.lateral_accel_from_torque(-self.steer_max, self.torque_params),
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

    # Measurement in lateral-accel space.
    measured_curvature = -VM.calc_curvature(
      math.radians(CS.steeringAngleDeg - params.angleOffsetDeg),
      CS.vEgo,
      params.roll
    )
    measurement = measured_curvature * CS.vEgo ** 2

    # Deadzone conversion to lateral-accel space.
    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY

    # Latency compensation: use provided lat_delay if available, otherwise fall back.
    if lat_delay is None:
      lat_delay = float(getattr(params, "latDelay", self.dt))
    lat_delay = float(max(lat_delay, self.dt))

    # Buffer expected desired lateral accel based on actuation delay.
    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.lat_accel_request_buffer.append(future_desired_lateral_accel)

    delay_frames = int(np.clip(lat_delay / self.dt, 1, self.lat_accel_request_buffer_len))
    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]

    # Jerk term computed against expected accel (setpoint-side compensation).
    desired_lateral_jerk = (future_desired_lateral_accel - expected_lateral_accel) / lat_delay

    # Measurement rate for optional D usage (KD currently 0.0, but behavior remains correct).
    measurement_rate = float(self.measurement_rate_filter.update((measurement - self.previous_measurement) / self.dt))
    self.previous_measurement = measurement

    # Latency-compensated setpoint.
    setpoint = lat_delay * desired_lateral_jerk + expected_lateral_accel
    error = setpoint - measurement

    # Feedforward in lateral-accel space (gravity-adjusted, with latAccelOffset bias correction).
    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    ff = gravity_adjusted_future_lateral_accel
    ff -= float(self.torque_params.latAccelOffset)

    # Fade friction out during lane changes for smoother transitions.
    lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
    target_scale = 0.0 if lane_change else 1.0
    friction_scale = float(self.friction_scale.update(target_scale))

    # Reduce friction compensation on curves (keep it strongest on straights).
    desired_lataccel_mag = abs(future_desired_lateral_accel)

    # Blend friction scaling across a speed band to avoid a hard mode switch.
    blend = float(np.interp(CS.vEgo, [FRICTION_BLEND_START_MS, FRICTION_BLEND_END_MS], [0.0, 1.0]))
    friction_y = (1.0 - blend) * np.array(FRICTION_Y_LOW_SPEED) + blend * np.array(FRICTION_Y_HIGH_SPEED)

    friction_error_scale = float(np.interp(desired_lataccel_mag, FRICTION_X, friction_y))
    friction_input = error * friction_error_scale

    friction = get_friction(friction_input, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)
    ff += friction_scale * friction

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

    # Extension hook (kept compatible with your earlier signature expectations).
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
