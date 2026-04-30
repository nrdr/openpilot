import inspect
import math
from typing import NamedTuple

import numpy as np

from cereal import log
from openpilot.common.params import Params
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl

try:
  from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
except ImportError:
  from openpilot.selfdrive.controls.lib.vehicle_model import ACCELERATION_DUE_TO_GRAVITY

# Speed based KP
KP = 1.0
KF = 1.0
KI = 0.1
KD = 0.0

LOW_SPEED_X = [0.0, 10.0, 20.0, 30.0]
LOW_SPEED_Y = [15.0, 13.0, 10.0, 5.0]

FRICTION_THRESHOLD = 0.3

VERSION = 2
PARAM_UPDATE_FRAMES = 30


class LatControlInputs(NamedTuple):
  lateral_acceleration: float
  roll_compensation: float
  v_ego: float
  a_ego: float


class ClassicTorqueExtension:
  def update_model_v2(self, model_v2):
    pass

  def update_lateral_lag(self, lag):
    pass

  def update_override_torque_params(self, torque_params):
    return False


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt=0.01):
    try:
      super().__init__(CP, CP_SP, CI, dt)
    except TypeError:
      try:
        super().__init__(CP, CP_SP, CI)
      except TypeError:
        super().__init__(CP, CI)

    self.dt = dt

    torque_tuning = CP.lateralTuning.torque
    self.torque_params = torque_tuning.as_builder() if hasattr(torque_tuning, "as_builder") else torque_tuning

    if not hasattr(CI, "torque_from_lateral_accel_in_torque_space"):
      raise RuntimeError("Classic torque controller requires CI.torque_from_lateral_accel_in_torque_space()")

    # Use the classic torque-space callback so PID and feedforward stay in steering torque space.
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel_in_torque_space()

    try:
      self.torque_callback_arg_count = len(inspect.signature(self.torque_from_lateral_accel).parameters)
    except (TypeError, ValueError):
      self.torque_callback_arg_count = 3

    self.pid = PIDController(
      KP,
      KI,
      k_d=KD,
      k_f=KF,
      pos_limit=self.steer_max,
      neg_limit=-self.steer_max,
      rate=1.0 / self.dt,
    )

    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    # controlsd expects torque controllers to expose an extension object.
    # This shim preserves that interface without enabling NNLC/NNFF/jerk extension behavior.
    self.extension = ClassicTorqueExtension()

    self.params = Params()
    self.frame = -1
    self.enforce_torque_control_toggle = self.params.get_bool("EnforceTorqueControl")
    self.torque_override_enabled = self.params.get_bool("TorqueParamsOverrideEnabled")

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction

  def _read_float_param(self, key, default):
    value = self.params.get(key, return_default=True)

    if value is None:
      return default

    try:
      if isinstance(value, bytes):
        value = value.decode("utf8")
      return float(value)
    except (TypeError, ValueError):
      return default

  def update_live_tune(self):
    self.frame += 1

    if self.frame % PARAM_UPDATE_FRAMES != 0:
      return

    self.enforce_torque_control_toggle = self.params.get_bool("EnforceTorqueControl")
    if not self.enforce_torque_control_toggle:
      return

    self.torque_override_enabled = self.params.get_bool("TorqueParamsOverrideEnabled")
    if not self.torque_override_enabled:
      return

    self.torque_params.latAccelFactor = self._read_float_param(
      "TorqueParamsOverrideLatAccelFactor",
      self.torque_params.latAccelFactor,
    )
    self.torque_params.friction = self._read_float_param(
      "TorqueParamsOverrideFriction",
      self.torque_params.friction,
    )

  @staticmethod
  def _apply_deadzone(error, deadzone):
    if error > deadzone:
      return error - deadzone
    if error < -deadzone:
      return error + deadzone
    return 0.0

  def _classic_friction(self, friction_input, lateral_accel_deadzone):
    friction = float(getattr(self.torque_params, "friction", 0.0))
    lat_accel_factor = float(getattr(self.torque_params, "latAccelFactor", 1.0))

    return float(np.interp(
      self._apply_deadzone(friction_input, lateral_accel_deadzone),
      [-FRICTION_THRESHOLD, FRICTION_THRESHOLD],
      [-friction, friction],
    )) * lat_accel_factor

  def _torque_from_lateral_accel(self, lateral_accel, roll_compensation, v_ego, a_ego, gravity_adjusted=False):
    lat_control_inputs = LatControlInputs(lateral_accel, roll_compensation, v_ego, a_ego)

    if self.torque_callback_arg_count >= 3:
      return self.torque_from_lateral_accel(
        lat_control_inputs,
        self.torque_params,
        gravity_adjusted,
      )

    return self.torque_from_lateral_accel(
      lat_control_inputs,
      self.torque_params,
    )

  def _check_saturation_compat(self, saturated, CS, steer_limited_by_safety, curvature_limited):
    try:
      return self._check_saturation(saturated, CS, steer_limited_by_safety, curvature_limited)
    except TypeError:
      return self._check_saturation(saturated, CS, steer_limited_by_safety)

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited=False, lat_delay=None):
    self.update_live_tune()

    pid_log = log.ControlsState.LateralTorqueState.new_message()

    try:
      pid_log.version = VERSION
    except AttributeError:
      pass

    if not active:
      pid_log.active = False
      return -0.0, 0.0, pid_log

    v_ego = float(CS.vEgo)
    a_ego = float(getattr(CS, "aEgo", 0.0))
    roll = float(getattr(params, "roll", 0.0))
    angle_offset_deg = float(getattr(params, "angleOffsetDeg", 0.0))

    actual_curvature = -VM.calc_curvature(
      math.radians(CS.steeringAngleDeg - angle_offset_deg),
      v_ego,
      roll,
    )

    curvature_deadzone = abs(VM.calc_curvature(
      math.radians(self.steering_angle_deadzone_deg),
      v_ego,
      0.0,
    ))
    lateral_accel_deadzone = curvature_deadzone * v_ego ** 2

    roll_compensation = roll * ACCELERATION_DUE_TO_GRAVITY

    desired_lateral_accel = desired_curvature * v_ego ** 2
    actual_lateral_accel = actual_curvature * v_ego ** 2

    # Classic torque-controller low-speed correction.
    low_speed_factor = np.interp(v_ego, LOW_SPEED_X, LOW_SPEED_Y) ** 2
    setpoint = desired_lateral_accel + low_speed_factor * desired_curvature
    measurement = actual_lateral_accel + low_speed_factor * actual_curvature

    # PID error is intentionally computed in torque space.
    torque_from_setpoint = self._torque_from_lateral_accel(
      setpoint,
      roll_compensation,
      v_ego,
      a_ego,
      gravity_adjusted=False,
    )

    torque_from_measurement = self._torque_from_lateral_accel(
      measurement,
      roll_compensation,
      v_ego,
      a_ego,
      gravity_adjusted=False,
    )

    pid_error = torque_from_setpoint - torque_from_measurement

    # Classic friction behavior: base torque feedforward plus direct torque-space friction.
    friction_input = desired_lateral_accel - actual_lateral_accel
    gravity_adjusted_lateral_accel = desired_lateral_accel - roll_compensation

    ff = self._torque_from_lateral_accel(
      gravity_adjusted_lateral_accel,
      roll_compensation,
      v_ego,
      a_ego,
      gravity_adjusted=True,
    )
    ff += self._classic_friction(friction_input, lateral_accel_deadzone)

    freeze_integrator = steer_limited_by_safety or CS.steeringPressed or v_ego < 5.0

    output_torque = self.pid.update(
      pid_error,
      speed=v_ego,
      feedforward=ff,
      freeze_integrator=freeze_integrator,
    )

    pid_log.active = True
    pid_log.error = float(pid_error)
    pid_log.p = float(self.pid.p)
    pid_log.i = float(self.pid.i)
    pid_log.d = float(self.pid.d)
    pid_log.f = float(self.pid.f)
    pid_log.output = float(-output_torque)
    pid_log.actualLateralAccel = float(actual_lateral_accel)
    pid_log.desiredLateralAccel = float(desired_lateral_accel)
    pid_log.saturated = bool(self._check_saturation_compat(
      self.steer_max - abs(output_torque) < 1e-3,
      CS,
      steer_limited_by_safety,
      curvature_limited,
    ))

    return -output_torque, 0.0, pid_log