"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections import deque
import math
import numpy as np

from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from opendbc.sunnypilot.car.interfaces import LatControlInputs
from opendbc.sunnypilot.car.lateral_ext import get_friction as get_friction_in_torque_space
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_base import LatControlTorqueExtBase, sign
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import MOCK_MODEL_PATH
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.model import NNTorqueModel

LP_FILTER_CUTOFF_HZ = 1.2
JERK_LOOKAHEAD_SECONDS = 0.19
JERK_GAIN = 0.3
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0
DT_NNLC = 0.01


# At a given roll, if pitch magnitude increases, the
# gravitational acceleration component starts pointing
# in the longitudinal direction, decreasing the lateral
# acceleration component. Here we do the same thing
# to the roll value itself, then pass it to nnff.
def roll_pitch_adjust(roll, pitch):
  return roll * math.cos(pitch)


class NeuralNetworkLateralControl(LatControlTorqueExtBase):
  def __init__(self, lac_torque, CP, CP_SP, CI):
    super().__init__(lac_torque, CP, CP_SP, CI)
    self.params = Params()
    self.enabled = self.params.get_bool("NeuralNetworkLateralControl")
    self.has_nn_model = CP_SP.neuralNetworkLateralControl.model.path != MOCK_MODEL_PATH

    # NN model takes current v_ego, lateral_accel, lat accel/jerk error, roll, and past/future/planned data
    # of lat accel and roll.
    # Past value is computed using previous desired lat accel and observed roll.
    self.model = NNTorqueModel(CP_SP.neuralNetworkLateralControl.model.path)

    self.pitch = FirstOrderFilter(0.0, 0.5, DT_NNLC)
    self.pitch_last = 0.0

    # Future time offsets used by the NN feature builder.
    self.future_times = [0.3, 0.6, 1.0, 1.5]
    self.nn_future_times = [i + self.desired_lat_jerk_time for i in self.future_times]

    # Past time offsets used by the NN feature builder.
    self.past_times = [-0.3, -0.2, -0.1]
    history_check_frames = [int(abs(i) * 100) for i in self.past_times]
    self.history_frame_offsets = [history_check_frames[0] - i for i in history_check_frames]
    self.lateral_accel_desired_deque = deque(maxlen=history_check_frames[0])
    self.roll_deque = deque(maxlen=history_check_frames[0])
    self.error_deque = deque(maxlen=history_check_frames[0])
    self.past_future_len = len(self.past_times) + len(self.nn_future_times)

    # Match the newer upstream torque controller by buffering desired lateral acceleration,
    # estimating a delayed setpoint, and deriving jerk from a lookahead window.
    self.lat_accel_request_buffer_len = max(1, int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / DT_NNLC))
    self.lat_accel_request_buffer = deque(
      [0.0] * self.lat_accel_request_buffer_len,
      maxlen=self.lat_accel_request_buffer_len,
    )
    self.lookahead_frames = int(JERK_LOOKAHEAD_SECONDS / DT_NNLC)
    self.jerk_filter = FirstOrderFilter(
      0.0,
      1.0 / (2.0 * np.pi * LP_FILTER_CUTOFF_HZ),
      DT_NNLC,
    )

  @property
  def _nnlc_enabled(self):
    return self.enabled and self.model_valid and self.has_nn_model

  def update_limits(self):
    if not self._nnlc_enabled:
      return

    self._pid.set_limits(self.lac_torque.steer_max, -self.lac_torque.steer_max)

  def update_lateral_lag(self, lag):
    super().update_lateral_lag(lag)
    self.nn_future_times = [t + self.desired_lat_jerk_time for t in self.future_times]

  def update_feedforward_torque_space(self, CS):
    torque_from_setpoint = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(self._setpoint, self._roll_compensation, CS.vEgo, CS.aEgo),
      self.lac_torque.torque_params,
      gravity_adjusted=False,
    )
    torque_from_measurement = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(self._measurement, self._roll_compensation, CS.vEgo, CS.aEgo),
      self.lac_torque.torque_params,
      gravity_adjusted=False,
    )
    self._pid_log.error = float(torque_from_setpoint - torque_from_measurement)
    self._ff = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(self._gravity_adjusted_lateral_accel, self._roll_compensation, CS.vEgo, CS.aEgo),
      self.lac_torque.torque_params,
      gravity_adjusted=True,
    )
    self._ff += get_friction_in_torque_space(
      self._desired_lateral_accel - self._actual_lateral_accel,
      self._lateral_accel_deadzone,
      FRICTION_THRESHOLD,
      self.lac_torque.torque_params,
    )

  def update_output_torque(self, CS):
    freeze_integrator = self._steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
    self._output_torque = self._pid.update(
      self._pid_log.error,
      feedforward=self._ff,
      speed=CS.vEgo,
      freeze_integrator=freeze_integrator,
    )

  def update_neural_network_feedforward(self, CS, params, calibrated_pose) -> None:
    if not self._nnlc_enabled:
      return

    # Match the newer torque controller's delayed lateral-accel setpoint behavior.
    # desired_lat_jerk_time is the closest existing lag term available in this NNLC path.
    lat_delay = max(float(self.desired_lat_jerk_time), DT_NNLC)
    self.lat_accel_request_buffer.append(self._desired_lateral_accel)

    delay_frames = int(np.clip(lat_delay / DT_NNLC + 1, 1, self.lat_accel_request_buffer_len))
    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]

    lookahead_idx = int(np.clip(
      -delay_frames + self.lookahead_frames,
      -self.lat_accel_request_buffer_len + 1,
      -2,
    ))
    raw_lateral_jerk = (
      self.lat_accel_request_buffer[lookahead_idx + 1] -
      self.lat_accel_request_buffer[lookahead_idx - 1]
    ) / (2 * DT_NNLC)
    desired_lateral_jerk = float(self.jerk_filter.update(raw_lateral_jerk))

    # Replace the old squared low-speed curvature helper with the newer torque-controller
    # convention: setpoint is delayed desired lateral acceleration, measurement is actual
    # lateral acceleration.
    self._setpoint = expected_lateral_accel
    self._measurement = self._actual_lateral_accel

    # Update past data.
    roll = params.roll
    if calibrated_pose is not None:
      pitch = self.pitch.update(calibrated_pose.orientation.pitch)
      roll = roll_pitch_adjust(roll, pitch)
      self.pitch_last = pitch
    self.roll_deque.append(roll)
    self.lateral_accel_desired_deque.append(self._desired_lateral_accel)

    # Prepare past and future values.
    # Adjust future times to account for longitudinal acceleration.
    adjusted_future_times = [t + 0.5 * CS.aEgo * (t / max(CS.vEgo, 1.0)) for t in self.nn_future_times]
    past_rolls = [self.roll_deque[min(len(self.roll_deque) - 1, i)] for i in self.history_frame_offsets]
    future_rolls = [
      roll_pitch_adjust(
        np.interp(t, ModelConstants.T_IDXS, self.model_v2.orientation.x) + roll,
        np.interp(t, ModelConstants.T_IDXS, self.model_v2.orientation.y) + self.pitch_last,
      ) for t in adjusted_future_times
    ]
    past_lateral_accels_desired = [
      self.lateral_accel_desired_deque[min(len(self.lateral_accel_desired_deque) - 1, i)]
      for i in self.history_frame_offsets
    ]
    future_planned_lateral_accels = [
      np.interp(t, ModelConstants.T_IDXS, self.model_v2.acceleration.y)
      for t in adjusted_future_times
    ]

    # Compute NN-based torque-space error response using the updated setpoint/measurement
    # conventions while preserving the model's original feature layout.
    nnff_setpoint_input = [CS.vEgo, self._setpoint, desired_lateral_jerk, roll] \
                          + [self._setpoint] * self.past_future_len \
                          + past_rolls + future_rolls
    nnff_measurement_input = [CS.vEgo, self._measurement, self.lateral_jerk_measurement, roll] \
                             + [self._measurement] * self.past_future_len \
                             + past_rolls + future_rolls
    torque_from_setpoint = self.model.evaluate(nnff_setpoint_input)
    torque_from_measurement = self.model.evaluate(nnff_measurement_input)
    self._pid_log.error = torque_from_setpoint - torque_from_measurement

    # The "pure" NNLC error response can be too weak for cars whose models were trained
    # with a lack of high-magnitude lateral acceleration data, for which the NNLC model
    # torque response flattens out at high lateral accelerations.
    # This workaround blends in a guaranteed stronger error response only when the
    # desired lateral acceleration is high enough to warrant it, by using the lateral
    # acceleration error as the input to the NNLC model.
    error_blend_factor = float(np.interp(abs(self._desired_lateral_accel), [1.0, 2.0], [0.0, 1.0]))
    if error_blend_factor > 0.0:
      nnff_error_input = [
        CS.vEgo,
        self._setpoint - self._measurement,
        desired_lateral_jerk - self.lateral_jerk_measurement,
        0.0,
      ]
      torque_from_error = self.model.evaluate(nnff_error_input)
      if sign(self._pid_log.error) == sign(torque_from_error) and abs(self._pid_log.error) < abs(torque_from_error):
        self._pid_log.error = self._pid_log.error * (1.0 - error_blend_factor) + torque_from_error * error_blend_factor

    # Match current torque-controller friction behavior more closely:
    # friction input is error plus a jerk assist term rather than the older
    # low-speed curvature-based helper path.
    friction_input = self._pid_log.error + JERK_GAIN * desired_lateral_jerk

    # Compute feedforward using the existing NN feature structure. Keep the model inputs
    # stable, but feed it the updated friction term and current desired lateral accel.
    nn_input = [CS.vEgo, self._desired_lateral_accel, friction_input, roll] \
               + past_lateral_accels_desired + future_planned_lateral_accels \
               + past_rolls + future_rolls
    self._ff = self.model.evaluate(nn_input)

    # Apply friction override for cars whose NN friction response is too weak.
    if self.model.friction_override:
      self._pid_log.error += get_friction(
        friction_input,
        self._lateral_accel_deadzone,
        FRICTION_THRESHOLD,
        self.lac_torque.torque_params,
      )

    self.update_output_torque(CS)