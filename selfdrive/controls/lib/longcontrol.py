class LongControl:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.long_control_state = LongCtrlState.off

    pos_p_limit = 0.0  # if params("NoPositivePResponse") else None

    # --- Profile gain sets ---
    # Standard uses CP.longitudinalTuning
    std_kp = (CP.longitudinalTuning.kpBP, CP.longitudinalTuning.kpV)
    std_ki = (CP.longitudinalTuning.kiBP, CP.longitudinalTuning.kiV)
    std_kf = CP.longitudinalTuning.kf

    # NOTE: Fill these with YOUR known-good, road-tested values.
    # Keep BP arrays identical across profiles to avoid weirdness.
    rel_kp = std_kp
    rel_ki = (CP.longitudinalTuning.kiBP, [v / 2.0 for v in CP.longitudinalTuning.kiV])
    rel_kf = std_kf

    agg_kp = std_kp
    agg_ki = (CP.longitudinalTuning.kiBP, [v * 3.0 for v in CP.longitudinalTuning.kiV])
    agg_kf = std_kf

    self.pid_relaxed = PIDController(rel_kp, rel_ki, k_f=rel_kf, rate=1 / DT_CTRL, pos_p_limit=pos_p_limit)
    self.pid_standard = PIDController(std_kp, std_ki, k_f=std_kf, rate=1 / DT_CTRL, pos_p_limit=pos_p_limit)
    self.pid_aggressive = PIDController(agg_kp, agg_ki, k_f=agg_kf, rate=1 / DT_CTRL, pos_p_limit=pos_p_limit)

    self.pid = self.pid_standard
    self._last_personality = None

    # Output smoothing after profile switch (prevents “slam gas/brake”)
    self._switch_timer_s = 0.0
    self._switch_ramp_s = 2.0          # 1.0–3.0 is a good range
    self._switch_max_delta = 0.25      # m/s^2 per update during ramp (tune)

    self.last_output_accel = 0.0

  def reset(self):
    self.pid_relaxed.reset()
    self.pid_standard.reset()
    self.pid_aggressive.reset()
    self._switch_timer_s = 0.0

  def _select_pid(self, personality):
    # Personality enum comes from cereal/log in most forks.
    # We compare by int to avoid import issues.
    if personality is None:
      return self.pid_standard

    p = int(personality)
    # These numeric values are typically: relaxed=0, standard=1, aggressive=2
    if p == 0:
      return self.pid_relaxed
    elif p == 2:
      return self.pid_aggressive
    else:
      return self.pid_standard

  def update(self, active, CS, a_target, should_stop, accel_limits, personality=None):
    """Update longitudinal control. This updates the state machine and runs a PID loop"""

    # --- live personality PID switching ---
    if personality is not None and personality != self._last_personality:
      new_pid = self._select_pid(personality)
      if new_pid is not self.pid:
        # Reset integrator on switch to avoid surprise stored error
        new_pid.reset()
        self.pid = new_pid

        # Start output ramp window so accel doesn't jump
        self._switch_timer_s = self._switch_ramp_s

      self._last_personality = personality

    # Limits always apply to whichever PID is active
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
      self.pid.reset()

    elif self.long_control_state == LongCtrlState.starting:
      output_accel = self.CP.startAccel
      self.pid.reset()

    else:  # LongCtrlState.pid
      error = a_target - CS.aEgo
      output_accel = self.pid.update(error, speed=CS.vEgo, feedforward=a_target)

    # --- ramp output accel right after profile switch ---
    output_accel = float(np.clip(output_accel, accel_limits[0], accel_limits[1]))

    if self._switch_timer_s > 0.0:
      self._switch_timer_s = max(0.0, self._switch_timer_s - DT_CTRL)
      lo = self.last_output_accel - self._switch_max_delta
      hi = self.last_output_accel + self._switch_max_delta
      output_accel = float(np.clip(output_accel, lo, hi))

    self.last_output_accel = output_accel
    return self.last_output_accel