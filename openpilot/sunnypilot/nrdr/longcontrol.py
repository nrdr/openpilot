import math
from collections import deque

import numpy as np

from opendbc.car.honda.values import HondaFlags
from opendbc.car.structs import car
from openpilot.common.pid import PIDController
from openpilot.common.realtime import DT_CTRL
from openpilot.sunnypilot.nrdr.live_params import get_live_params
from openpilot.sunnypilot.nrdr.long_tune import LongTune
from openpilot.sunnypilot.nrdr.longitudinal_stopping import compute_stopping_accel
from openpilot.sunnypilot.nrdr.params import read_bool, read_float


LongCtrlState = car.CarControl.Actuators.LongControlState
DREL_FILTER_FRAMES = 10
DREL_FILTER_ALPHA = 0.3
ROEN_ACCEL_BP = (0.0, 5.0, 20.0)
ROEN_NIDEC_ACCEL_MAX = (4.0, 4.0, 3.0)
LONG_PID_SCALE_KEYS = (
  "LongPidTuneScaleAggressive",
  "LongPidTuneScaleStandard",
  "LongPidTuneScaleRelaxed",
  "LongPidTuneScaleEcon",
)
LONG_PID_SCALE_DEFAULTS = (2.0, 1.0, 0.8, 0.5)
LONG_PID_SCALE_SLEW_PER_SECOND = 2.0
LONG_PID_SCALE_EPSILON = 1e-6


def _personality_index(personality) -> int | None:
  raw = getattr(personality, "raw", personality)
  if isinstance(raw, bool):
    return None
  try:
    index = int(raw)
    if float(raw) != index:
      return None
  except (TypeError, ValueError):
    return None
  return index if 0 <= index < len(LONG_PID_SCALE_DEFAULTS) else None


def effective_long_pid_scale(scales, personality, gas_interceptor: bool, live_learning_gas: bool) -> float:
  if live_learning_gas or not gas_interceptor:
    return 1.0

  index = _personality_index(personality)
  if index is None or index >= len(scales):
    return 1.0
  try:
    scale = float(scales[index])
  except (TypeError, ValueError):
    return 1.0
  return float(np.clip(scale, 0.0, 5.0)) if math.isfinite(scale) else 1.0


def scaled_pid_limits(neg_limit: float, pos_limit: float, feedforward: float,
                      scale: float, static_feedforward: bool) -> tuple[float, float]:
  # Preserve the existing reduced-authority behavior at or below 100%; above
  # 100%, tighten the PID's own limits so its anti-windup sees the outer clamp.
  if scale <= 1.0:
    return neg_limit, pos_limit
  if static_feedforward:
    return (
      feedforward + (neg_limit - feedforward) / scale,
      feedforward + (pos_limit - feedforward) / scale,
    )
  return neg_limit / scale, pos_limit / scale


def longitudinal_pid_gains(CP):
  tuning = CP.longitudinalTuning
  return (
    (tuning.deprecated.kpBP, tuning.deprecated.kpV),
    (tuning.kiBP, tuning.kiV),
  )


def _state_transition(CP, CP_SP, active, state, should_stop, brake_pressed,
                      cruise_standstill, v_ego, v_ego_starting):
  cruise_standstill = cruise_standstill and not CP_SP.enableGasInterceptor
  starting = not should_stop and not cruise_standstill and not brake_pressed
  started = v_ego > v_ego_starting

  if not active:
    return LongCtrlState.off
  if state == LongCtrlState.off:
    if not starting:
      return LongCtrlState.stopping
    return LongCtrlState.starting if CP.deprecated.startingState else LongCtrlState.pid
  if state == LongCtrlState.stopping:
    if starting:
      return LongCtrlState.starting if CP.deprecated.startingState else LongCtrlState.pid
    return state
  if should_stop:
    return LongCtrlState.stopping
  if started:
    return LongCtrlState.pid
  return state


class NrdrLongControl:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.long_control_state = LongCtrlState.off
    self.pid = PIDController(*longitudinal_pid_gains(CP), rate=1 / DT_CTRL)
    self.params = get_live_params()
    self.settings_generation = -1
    self.tune = LongTune()
    self.last_output_accel = 0.0
    self.frame = 0
    self.pid_scale = 1.0
    self.pid_scales = LONG_PID_SCALE_DEFAULTS
    self.live_learning_gas = not CP_SP.enableGasInterceptor
    self.static_feedforward = True
    self.stop_accel = CP.stopAccel
    self.stopping_decel_rate = CP.deprecated.stoppingDecelRate
    self.v_ego_starting = CP.deprecated.vEgoStarting
    self.v_ego_stopping = CP.deprecated.vEgoStopping
    self.roen_acceleration_limits = True
    self.drel_window = deque(maxlen=DREL_FILTER_FRAMES)
    self.drel_filtered = math.inf
    self._refresh_params()

  def reset(self) -> None:
    self.pid.reset()

  def _refresh_params(self) -> None:
    snapshot = self.params.snapshot
    self.pid_scales = tuple(
      read_float(snapshot, key, default, 0.0, 5.0, scale=100.0)
      for key, default in zip(LONG_PID_SCALE_KEYS, LONG_PID_SCALE_DEFAULTS, strict=True)
    )
    self.live_learning_gas = read_bool(snapshot, "HondaLiveLearningGas", not self.CP_SP.enableGasInterceptor)
    self.static_feedforward = read_bool(snapshot, "StaticFeedforwardLong", True)
    self.stop_accel = read_float(snapshot, "HondaStopAccel", self.CP.stopAccel, -10.0, 0.0)
    self.stopping_decel_rate = read_float(
      snapshot, "HondaStoppingDecelRateLong", self.CP.deprecated.stoppingDecelRate, 0.0, 5.0,
    )
    self.v_ego_starting = read_float(snapshot, "HondaVEgoStarting", self.CP.deprecated.vEgoStarting, 0.0, 5.0)
    self.v_ego_stopping = read_float(snapshot, "HondaVEgoStopping", self.CP.deprecated.vEgoStopping, 0.0, 5.0)
    self.roen_acceleration_limits = read_bool(snapshot, "NrdrRoenAccelerationLimits", True)
    self.settings_generation = snapshot.generation

  def _accel_limits(self, accel_limits, v_ego: float):
    if (self.roen_acceleration_limits and self.CP.brand == "honda" and self.CP.flags & HondaFlags.NIDEC and
        self.CP_SP.enableGasInterceptor):
      roen_max = float(np.interp(v_ego, ROEN_ACCEL_BP, ROEN_NIDEC_ACCEL_MAX))
      return accel_limits[0], max(accel_limits[1], roen_max)
    return accel_limits

  def _filter_drel(self, drel) -> float:
    if drel is None or not math.isfinite(drel):
      self.drel_window.clear()
      self.drel_filtered = math.inf
      return self.drel_filtered

    self.drel_window.append(float(drel))
    rolling_minimum = min(self.drel_window)
    if not math.isfinite(self.drel_filtered):
      self.drel_filtered = rolling_minimum
    else:
      self.drel_filtered += DREL_FILTER_ALPHA * (rolling_minimum - self.drel_filtered)
    return self.drel_filtered

  def _stock_stopping_accel(self) -> float:
    if self.last_output_accel <= self.stop_accel:
      return self.last_output_accel
    return min(self.last_output_accel, 0.0) - self.stopping_decel_rate * DT_CTRL

  def _stopping_accel(self, CS, pitch, drel_filtered) -> float:
    if self.tune.stopping["l2_enable"] < 0.5:
      return self._stock_stopping_accel()
    return compute_stopping_accel(
      self.last_output_accel,
      self.stop_accel,
      self.stopping_decel_rate,
      CS.vEgo,
      self.v_ego_stopping,
      self.tune.stopping["hold_accel"],
      self.tune.stopping["phase_switch_v"],
      self.tune.stopping["proximity_scale_m"],
      self.tune.stopping["pitch_margin"],
      drel_filtered,
      pitch if pitch is not None else math.nan,
    )

  def _pid_accel(self, CS, a_target) -> float:
    zero_scale = self.pid_scale <= LONG_PID_SCALE_EPSILON
    if zero_scale:
      self.pid.i = 0.0
    self.pid.neg_limit, self.pid.pos_limit = scaled_pid_limits(
      self.pid.neg_limit, self.pid.pos_limit, a_target, self.pid_scale, self.static_feedforward,
    )
    output = self.pid.update(
      a_target - CS.aEgo,
      speed=CS.vEgo,
      feedforward=a_target,
      freeze_integrator=zero_scale,
    )
    if self.static_feedforward:
      return (output - self.pid.f) * self.pid_scale + self.pid.f
    return output * self.pid_scale

  def _update_pid_scale(self, personality, was_pid: bool) -> None:
    target = effective_long_pid_scale(
      self.pid_scales, personality, self.CP_SP.enableGasInterceptor, self.live_learning_gas,
    )
    forced_default = self.live_learning_gas or not self.CP_SP.enableGasInterceptor or _personality_index(personality) is None
    if forced_default or not was_pid or self.long_control_state != LongCtrlState.pid:
      self.pid_scale = target
      return

    max_delta = LONG_PID_SCALE_SLEW_PER_SECOND * DT_CTRL
    self.pid_scale += float(np.clip(target - self.pid_scale, -max_delta, max_delta))

  def update(self, active, CS, a_target, should_stop, accel_limits, pitch=None, drel=None, personality=None):
    if self.settings_generation != self.params.generation:
      self._refresh_params()
    self.tune.refresh()
    self.frame += 1
    accel_limits = self._accel_limits(accel_limits, CS.vEgo)

    self.pid.neg_limit, self.pid.pos_limit = accel_limits
    was_pid = self.long_control_state == LongCtrlState.pid
    self.long_control_state = _state_transition(
      self.CP,
      self.CP_SP,
      active,
      self.long_control_state,
      should_stop,
      CS.brakePressed,
      CS.cruiseState.standstill,
      CS.vEgo,
      self.v_ego_starting,
    )
    self._update_pid_scale(personality, was_pid)
    drel_filtered = self._filter_drel(drel)

    if self.long_control_state == LongCtrlState.off:
      self.reset()
      output_accel = 0.0
    elif self.long_control_state == LongCtrlState.stopping:
      output_accel = self._stopping_accel(CS, pitch, drel_filtered)
      self.reset()
    elif self.long_control_state == LongCtrlState.starting:
      output_accel = self.CP.deprecated.startAccel
      self.reset()
    else:
      output_accel = self._pid_accel(CS, a_target)

    self.last_output_accel = float(np.clip(output_accel, *accel_limits))
    return self.last_output_accel
