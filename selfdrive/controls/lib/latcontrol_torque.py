import math
from collections import deque

import numpy as np

from cereal import log
from opendbc.car.honda.values import CAR
from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt
from roenpilot.common.numpy_fast import interp


# -----------------------------------------------------------------------------
# Comma-style low-speed behavior (newer logic)
# -----------------------------------------------------------------------------
# Instead of a "low_speed_factor" term added into setpoint/measurement,
# Comma boosts proportional gain at low speed using a speed->KP schedule,
# and compensates actuation latency using a buffered expected lat accel and a jerk term.

KP = 1.0
KI = 0.3
KD = 0.0

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP =      [250, 120, 65,  30, 11.5, 5.5, 3.5, 2.0, KP]

LP_FILTER_CUTOFF_HZ = 1.2
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0

# -----------------------------------------------------------------------------
# Different friction on straights:
# Fade friction as desired lateral accel increases (curvier roads)
# Full friction at/under ~0.6 m/s^2, no friction at/over ~0.8 m/s^2
# -----------------------------------------------------------------------------
FRICTION_X = [0.4, 0.6]   # m/s^2 desired lateral accel magnitude
FRICTION_Y = [1.0, 0.25]   # scale applied to friction input


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt=0.01):
    # Your base LatControl signature might not take dt; keep it minimal
    super().__init__(CP, CP_SP, CI)
    self.dt = dt

    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()

    # IMPORTANT FIX:
    # PIDController supports scheduled gains by passing [bp, values].
    # DO NOT try to set self.pid.kp later; PID uses self._k_p internally.
    self.pid = PIDController(
      [INTERP_SPEEDS, KP_INTERP],   # scheduled k_p
      KI,                           # k_i (constant OK)
      k_f=self.torque_params.kf,    # keep your feedforward gain behavior
      k_d=KD,                       # 0.0
      rate=1 / self.dt
    )

    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

    # specific car fingerprint (kept in case needing per-car KP schedules later)
    self.carFingerprint = CP.carFingerprint

    # Friction fade on blinker
    self.friction_scale = FirstOrderFilter(1.0, 0.25, self.dt)

    # Comma-style latency compensation state
    self.lat_accel_request_buffer_len = max(1, int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt))
    self.lat_accel_request_buffer = deque([0.0] * self.lat_accel_request_buffer_len,
                                          maxlen=self.lat_accel_request_buffer_len)

    self.previous_measurement = 0.0
    self.measurement_rate_filter = FirstOrderFilter(
      0.0,
      1 / (2 * np.pi * LP_FILTER_CUTOFF_HZ),
      self.dt
    )

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction
    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(self.lateral_accel_from_torque(self.steer_max, self.torque_params),
                        self.lateral_accel_from_torque(-self.steer_max, self.torque_params))

  # This is NOT used to set gains anymore.
  def _kp_for_speed(self, v_ego: float) -> float:
    return float(interp(v_ego, INTERP_SPEEDS, KP_INTERP))

  def _pid_update_compat(self, error: float, measurement_rate: float, ff: float, speed: float, freeze_integrator: bool):
    """
    Your PIDController already supports error_rate, so we can call it directly.
    KD is 0.0 right now, so measurement_rate won't change output today, but it's correct.
    """
    return self.pid.update(
      error,
      error_rate=-measurement_rate,
      speed=speed,
      feedforward=ff,
      freeze_integrator=freeze_integrator
    )

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay=None):
    # Override torque params from extension
    if self.extension.update_override_torque_params(self.torque_params):
      self.update_limits()

    pid_log = log.ControlsState.LateralTorqueState.new_message()

    if not active:
      output_torque = 0.0
      pid_log.active = False
      return -output_torque, 0.0, pid_log

    # -------------------------------------------------------------------------
    # Measurements and deadzones
    # -------------------------------------------------------------------------
    measured_curvature = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg),
                                           CS.vEgo, params.roll)
    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY

    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    # -------------------------------------------------------------------------
    # Latency-compensated setpoint (Comma-style)
    # -------------------------------------------------------------------------
    # Prefer explicit lat_delay arg (Comma-style). If not provided, try params.latDelay,
    # else fall back to dt. Clamp to at least dt so division is safe.
    if lat_delay is None:
      lat_delay = float(getattr(params, "latDelay", self.dt))
    lat_delay = float(max(lat_delay, self.dt))

    delay_frames = int(np.clip(lat_delay / self.dt, 1, self.lat_accel_request_buffer_len))

    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]

    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.lat_accel_request_buffer.append(future_desired_lateral_accel)

    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    desired_lateral_jerk = (future_desired_lateral_accel - expected_lateral_accel) / lat_delay

    measurement = measured_curvature * CS.vEgo ** 2
    measurement_rate = float(self.measurement_rate_filter.update((measurement - self.previous_measurement) / self.dt))
    self.previous_measurement = measurement

    setpoint = lat_delay * desired_lateral_jerk + expected_lateral_accel
    error = setpoint - measurement

    # -------------------------------------------------------------------------
    # Feedforward + friction (kept blinker fade)
    # -------------------------------------------------------------------------
    ff = gravity_adjusted_future_lateral_accel
    # latAccelOffset corrects roll compensation bias from device roll misalignment relative to car roll
    ff -= self.torque_params.latAccelOffset

    # Disable (fade out) friction when either blinker is on to make lane changes/manual lane moves smoother
    lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
    target_scale = 0.0 if lane_change else 1.0
    friction_scale = float(self.friction_scale.update(target_scale))

    # "Different friction on straights": downscale friction input error based on desired lateral accel magnitude
    desired_lataccel_mag = abs(future_desired_lateral_accel)
    friction_error_scale = float(np.interp(desired_lataccel_mag, FRICTION_X, FRICTION_Y))
    friction_input = error * friction_error_scale

    # Comma-style: friction is a function of error (setpoint - measurement)
    friction = get_friction(friction_input, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)
    ff += friction_scale * friction

    # -------------------------------------------------------------------------
    # PID in lateral-accel space -> convert to torque at end
    # -------------------------------------------------------------------------
    pid_log.error = float(error)

    freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
    output_lataccel = self._pid_update_compat(error, measurement_rate, ff, CS.vEgo, freeze_integrator)
    output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

    # -------------------------------------------------------------------------
    # Extension hook (unchanged signature from your existing code)
    # Note: We pass "future_desired_lateral_accel" and "measurement" in place of
    # desired/actual lateral accel to match the new logic.
    # -------------------------------------------------------------------------
    pid_log, output_torque = self.extension.update(
      CS, VM, self.pid, params, ff, pid_log, setpoint, measurement, calibrated_pose, roll_compensation,
      future_desired_lateral_accel, measurement, lateral_accel_deadzone, gravity_adjusted_future_lateral_accel,
      desired_curvature, measured_curvature, steer_limited_by_safety, output_torque
    )

    # -------------------------------------------------------------------------
    # Logging (kept similar to Comma-style)
    # -------------------------------------------------------------------------
    pid_log.active = True
    pid_log.p = float(self.pid.p)
    pid_log.i = float(self.pid.i)
    pid_log.d = float(self.pid.d)
    pid_log.f = float(self.pid.f)
    pid_log.output = float(-output_torque)
    pid_log.actualLateralAccel = float(measurement)
    pid_log.desiredLateralAccel = float(setpoint)
    pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3,
                                                    CS, steer_limited_by_safety, curvature_limited))

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log