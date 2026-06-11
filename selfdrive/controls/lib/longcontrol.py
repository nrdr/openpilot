import numpy as np

from cereal import car
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.common.pid import PIDController
from openpilot.selfdrive.modeld.constants import ModelConstants

CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]

LongCtrlState = car.CarControl.Actuators.LongControlState


def get_param_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  value = params.get(key)
  if value is None:
    ret = default
  else:
    try:
      # sunnypilot Params.get() auto-casts by declared key type, so an INT param
      # comes back as a python int (not bytes). Handle bytes/str/number uniformly.
      if isinstance(value, bytes):
        value = value.decode("utf-8")
      ret = float(value) / scale
    except (AttributeError, TypeError, ValueError):
      ret = default

  if min_value is not None:
    ret = max(min_value, ret)
  if max_value is not None:
    ret = min(max_value, ret)
  return ret


def long_control_state_trans(CP, CP_SP, active, long_control_state, v_ego,
                             should_stop, brake_pressed, cruise_standstill, v_ego_starting=None):
  # Gas Interceptor
  cruise_standstill = cruise_standstill and not CP_SP.enableGasInterceptor

  stopping_condition = should_stop
  starting_condition = (not should_stop and
                        not cruise_standstill and
                        not brake_pressed)
  started_condition = v_ego > (CP.vEgoStarting if v_ego_starting is None else v_ego_starting)

  if not active:
    long_control_state = LongCtrlState.off

  else:
    if long_control_state == LongCtrlState.off:
      if not starting_condition:
        long_control_state = LongCtrlState.stopping
      else:
        if starting_condition and CP.startingState:
          long_control_state = LongCtrlState.starting
        else:
          long_control_state = LongCtrlState.pid

    elif long_control_state == LongCtrlState.stopping:
      if starting_condition and CP.startingState:
        long_control_state = LongCtrlState.starting
      elif starting_condition:
        long_control_state = LongCtrlState.pid

    elif long_control_state in [LongCtrlState.starting, LongCtrlState.pid]:
      if stopping_condition:
        long_control_state = LongCtrlState.stopping
      elif started_condition:
        long_control_state = LongCtrlState.pid
  return long_control_state


class LongControl:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.long_control_state = LongCtrlState.off
    self.pid = PIDController((CP.longitudinalTuning.kpBP, CP.longitudinalTuning.kpV),
                             (CP.longitudinalTuning.kiBP, CP.longitudinalTuning.kiV),
                             rate=1 / DT_CTRL)
    self.params = Params()
    self.last_output_accel = 0.0
    self.frame = 0

    # Live-tunable longitudinal params; default to the car's configured values so
    # an unset param means "no change from stock".
    self.long_pid_tune_scale = 1.0
    self.scale_excludes_kf = False  # when True, PID scale multiplies P+I only, not feedforward
    self.stop_accel = CP.stopAccel
    self.stopping_decel_rate = CP.stoppingDecelRate
    self.v_ego_starting = CP.vEgoStarting

  def reset(self):
    self.pid.reset()

  def _read_live_params(self):
    self.long_pid_tune_scale = get_param_float(self.params, "LongPidTuneScale", 1.0, 0.0, 5.0, scale=100.0)
    self.scale_excludes_kf = self.params.get_bool("NrdrPidScaleExcludeKf")
    self.stop_accel = get_param_float(self.params, "HondaStopAccel", self.CP.stopAccel, -10.0, 0.0)
    self.stopping_decel_rate = get_param_float(self.params, "HondaStoppingDecelRateLong", self.CP.stoppingDecelRate, 0.0, 5.0)
    self.v_ego_starting = get_param_float(self.params, "HondaVEgoStarting", self.CP.vEgoStarting, 0.0, 5.0)

  def update(self, active, CS, a_target, should_stop, accel_limits):
    """Update longitudinal control. This updates the state machine and runs a PID loop"""
    if self.frame % 300 == 0:
      self._read_live_params()
    self.frame += 1

    self.pid.neg_limit = accel_limits[0]
    self.pid.pos_limit = accel_limits[1]

    self.long_control_state = long_control_state_trans(self.CP, self.CP_SP, active, self.long_control_state, CS.vEgo,
                                                       should_stop, CS.brakePressed,
                                                       CS.cruiseState.standstill, v_ego_starting=self.v_ego_starting)
    if self.long_control_state == LongCtrlState.off:
      self.reset()
      output_accel = 0.0

    elif self.long_control_state == LongCtrlState.stopping:
      output_accel = self.last_output_accel
      if output_accel > self.stop_accel:
        output_accel = min(output_accel, 0.0)
        output_accel -= self.stopping_decel_rate * DT_CTRL
      self.reset()

    elif self.long_control_state == LongCtrlState.starting:
      output_accel = self.CP.startAccel
      self.reset()

    else:  # LongCtrlState.pid
      error = a_target - CS.aEgo

      output_accel = self.pid.update(
        error,
        speed=CS.vEgo,
        feedforward=a_target,
      )

      if self.scale_excludes_kf:
        # Live PID scale multiplies only the feedback (P+I); feedforward keeps its tuned value.
        output_accel = (output_accel - self.pid.f) * self.long_pid_tune_scale + self.pid.f
      else:
        output_accel *= self.long_pid_tune_scale

    self.last_output_accel = np.clip(output_accel, accel_limits[0], accel_limits[1])
    return self.last_output_accel
