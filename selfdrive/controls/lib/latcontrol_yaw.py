from collections import deque
import math

import numpy as np

from cereal import log
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl


# Experimental yaw-feedback controller for the modified-EPS 10th-generation
# Nidec Civic.  It deliberately does not read steering angle, steer ratio, the
# vehicle model, or the firmware VGR map.  The only closed-loop measurement is
# calibrated road-frame yaw rate from livePose.
YAW_CONTROL_FINGERPRINTS = frozenset({"HONDA_CIVIC"})

# Initial tune translated from the known-good Civic PID tune and the historical
# nrdr torque-controller setup.  Keep these constants together so the first
# road-test baseline is unambiguous.
KP = 0.30
KI = 0.10
KD = 0.0
LAT_ACCEL_FACTOR = 3.5
FRICTION = 0.5
FRICTION_THRESHOLD = 0.3

# Historical low-speed curvature augmentation requested for this controller.
# Values are speeds in m/s and equivalent low-speed factors in m/s.
LOW_SPEED_X = [0.0, 10.0, 20.0, 30.0]
LOW_SPEED_Y = [15.0, 13.0, 10.0, 5.0]

YAW_FEEDBACK_MIN_SPEED = 0.5
MAX_YAW_RATE = 1.0
MAX_YAW_RATE_STD = 1.0
REQUEST_BUFFER_SECONDS = 2.0
VERSION = 1


def use_yaw_controller(car_fingerprint: str) -> bool:
  return str(car_fingerprint) in YAW_CONTROL_FINGERPRINTS


def low_speed_factor(v_ego: float) -> float:
  return float(np.interp(v_ego, LOW_SPEED_X, LOW_SPEED_Y) ** 2)


def friction_compensation(lateral_accel_error: float) -> float:
  return float(np.interp(lateral_accel_error,
                         [-FRICTION_THRESHOLD, FRICTION_THRESHOLD],
                         [-FRICTION, FRICTION]))


class LatControlYaw(LatControl):
  """Civic torque control closed around measured yaw instead of steering angle."""

  is_yaw_control = True

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    self.pid = PIDController(KP, KI, KD, k_f=1.0,
                             pos_limit=self.steer_max, neg_limit=-self.steer_max,
                             rate=1.0 / self.dt)
    buffer_len = max(2, int(REQUEST_BUFFER_SECONDS / self.dt))
    self.curvature_request_buffer = deque([0.0] * buffer_len, maxlen=buffer_len)

  def reset(self):
    super().reset()
    self.pid.reset()
    self.curvature_request_buffer.clear()
    self.curvature_request_buffer.extend([0.0] * self.curvature_request_buffer.maxlen)

  # controlsd calls this for controllers backed by a PID CarParams tune.  Yaw
  # control intentionally has no model-dependent unwind/lookahead extension.
  def update_model_v2(self, model_v2):
    pass

  @staticmethod
  def _read_yaw_rate(calibrated_pose) -> tuple[float, bool]:
    if calibrated_pose is None:
      return 0.0, False

    yaw_rate = float(calibrated_pose.angular_velocity.yaw)
    yaw_rate_std = float(calibrated_pose.angular_velocity.yaw_std)
    valid = math.isfinite(yaw_rate) and math.isfinite(yaw_rate_std)
    valid = valid and abs(yaw_rate) < MAX_YAW_RATE and 0.0 <= yaw_rate_std < MAX_YAW_RATE_STD
    return (yaw_rate if valid else 0.0), valid

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    del VM  # This controller must remain independent of steer ratio and VGR.

    pid_log = log.ControlsState.LateralTorqueState.new_message()
    pid_log.version = VERSION

    v_ego = max(float(CS.vEgo), 0.0)
    desired_curvature = float(desired_curvature)
    self.curvature_request_buffer.append(desired_curvature)

    finite_delay = float(lat_delay) if math.isfinite(float(lat_delay)) else 0.0
    delay_frames = int(np.clip(finite_delay / self.dt + 1,
                               1, len(self.curvature_request_buffer)))
    expected_curvature = self.curvature_request_buffer[-delay_frames]

    yaw_rate, yaw_valid = self._read_yaw_rate(calibrated_pose)
    actual_lateral_accel = yaw_rate * v_ego
    desired_lateral_accel = desired_curvature * v_ego ** 2
    expected_lateral_accel = expected_curvature * v_ego ** 2

    # At nonzero speed, close the loop on both lateral acceleration and
    # curvature.  Below the useful yaw-observation floor, retain the same
    # controller and its requested-curvature pre-positioning term, but freeze I.
    if yaw_valid and v_ego >= YAW_FEEDBACK_MIN_SPEED:
      actual_curvature = yaw_rate / v_ego
      curvature_error = expected_curvature - actual_curvature
      lateral_accel_error = expected_lateral_accel - actual_lateral_accel
    elif yaw_valid:
      curvature_error = expected_curvature
      lateral_accel_error = expected_lateral_accel - actual_lateral_accel
    else:
      # Missing pose data must not create a fictitious feedback error.  Leave
      # only feedforward active until calibrated yaw returns.
      curvature_error = 0.0
      lateral_accel_error = 0.0

    augmented_error = lateral_accel_error + low_speed_factor(v_ego) * curvature_error
    torque_equivalent_error = augmented_error / LAT_ACCEL_FACTOR

    roll_compensation = float(params.roll) * ACCELERATION_DUE_TO_GRAVITY
    feedforward = (desired_lateral_accel - roll_compensation) / LAT_ACCEL_FACTOR
    if yaw_valid:
      # Match the historical high-friction tune: friction reacts to raw lateral
      # acceleration error, never to the low-speed amplified curvature term.
      raw_lateral_accel_error = desired_lateral_accel - actual_lateral_accel
      feedforward += friction_compensation(raw_lateral_accel_error)

    if not active:
      output_torque = 0.0
      pid_log.active = False
    else:
      freeze_integrator = steer_limited_by_safety or CS.steeringPressed or \
                          not yaw_valid or v_ego < YAW_FEEDBACK_MIN_SPEED
      output_torque = self.pid.update(torque_equivalent_error,
                                      feedforward=feedforward,
                                      freeze_integrator=freeze_integrator)

      pid_log.active = True
      pid_log.error = float(torque_equivalent_error)
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque)
      pid_log.actualLateralAccel = float(actual_lateral_accel)
      pid_log.desiredLateralAccel = float(expected_lateral_accel)
      pid_log.desiredLateralJerk = 0.0
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output_torque) < 1e-3,
        CS, steer_limited_by_safety, curvature_limited,
      ))

    # Honda torque convention is opposite the controller's lateral convention.
    return -output_torque, 0.0, pid_log
