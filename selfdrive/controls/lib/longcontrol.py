import numpy as np
from cereal import car, log
from openpilot.common.realtime import DT_CTRL
from openpilot.common.pid import PIDController

LongCtrlState = car.CarControl.Actuators.LongControlState


def long_control_state_trans(CP, CP_SP, active, long_control_state, v_ego,
                             should_stop, brake_pressed, cruise_standstill):
  # Gas Interceptor
  cruise_standstill = cruise_standstill and not CP_SP.enableGasInterceptor

  stopping_condition = should_stop
  starting_condition = (not should_stop and
                        not cruise_standstill and
                        not brake_pressed)
  started_condition = v_ego > CP.vEgoStarting

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

    pos_p_limit = 0.0  # keep existing behavior
    self.pid = PIDController(
      (CP.longitudinalTuning.kpBP, CP.longitudinalTuning.kpV),
      (CP.longitudinalTuning.kiBP, CP.longitudinalTuning.kiV),
      k_f=CP.longitudinalTuning.kf,
      rate=1 / DT_CTRL,
      pos_p_limit=pos_p_limit,
    )

    self.last_output_accel = 0.0

    # --- Live personality tuning (KI only) ---
    self._last_personality = None

    # "Standard" comes from CarParams (i.e., your car interface.py).
    self._base_kiBP = list(CP.longitudinalTuning.kiBP)
    self._base_kiV = list(CP.longitudinalTuning.kiV)

  def reset(self):
    self.pid.reset()

  def _ki_scale_for_personality(self, personality) -> float:
    if personality == log.LongitudinalPersonality.relaxed:
      return 0.5
    if personality == log.LongitudinalPersonality.standard:
      return 1.0
    if personality == log.LongitudinalPersonality.aggressive:
      return 3.0
    return 1.0

  def _apply_live_personality_tune(self, personality) -> None:
    """
    Minimal-disruption tuning:
      - ONLY updates the integrator gain table (self.pid._k_i)
      - Leaves KP and k_f exactly as-is
      - Uses CP.longitudinalTuning.kiBP/kiV as the standard baseline
    """
    if personality == self._last_personality:
      return

    scale = self._ki_scale_for_personality(personality)
    kiV = [v * scale for v in self._base_kiV]

    # pid.py expects _k_i to be [bp_list, v_list]
    self.pid._k_i = [list(self._base_kiBP), list(kiV)]

    self._last_personality = personality

  def update(self, active, CS, a_target, should_stop, accel_limits,
             personality=log.LongitudinalPersonality.standard):
    """Update longitudinal control. This updates the state machine and runs a PID loop"""
    self._apply_live_personality_tune(personality)

    self.pid.neg_limit = accel_limits[0]
    self.pid.pos_limit = accel_limits[1]

    self.long_control_state = long_control_state_trans(
      self.CP, self.CP_SP, active, self.long_control_state, CS.vEgo,
      should_stop, CS.brakePressed, CS.cruiseState.standstill
    )

    if self.long_control_state == LongCtrlState.off:
      self.reset()
      output_accel = 0.0

    elif self.long_control_state == LongCtrlState.stopping:
      output_accel = self.last_output_accel
      if output_accel > self.CP.stopAccel:
        output_accel = min(output_accel, 0.0)
        output_accel -= self.CP.stoppingDecelRate * DT_CTRL
      self.reset()

    elif self.long_control_state == LongCtrlState.starting:
      output_accel = self.CP.startAccel
      self.reset()

    else:  # LongCtrlState.pid
      error = a_target - CS.aEgo
      output_accel = self.pid.update(error, speed=CS.vEgo, feedforward=a_target)

    self.last_output_accel = float(np.clip(output_accel, accel_limits[0], accel_limits[1]))
    return self.last_output_accel
