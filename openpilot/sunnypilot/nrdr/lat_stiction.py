from enum import Enum, auto


def _interp(x, xp, fp):
  if x <= xp[0]:
    return fp[0]
  if x >= xp[-1]:
    return fp[-1]
  for i in range(len(xp) - 1):
    if x < xp[i + 1]:
      f = (x - xp[i]) / (xp[i + 1] - xp[i])
      return fp[i] + f * (fp[i + 1] - fp[i])
  return fp[-1]


def _clip(x, lo, hi):
  return lo if x < lo else (hi if x > hi else x)


def _sign(x):
  return 1.0 if x > 0.0 else (-1.0 if x < 0.0 else 0.0)


class LatStictionState(Enum):
  TRACK = auto()
  CAPTURE = auto()
  HOLD = auto()
  REACQUIRE = auto()


class LatStiction:
  E_HI_BP = (8.0, 30.0)
  E_HI_V = (0.9, 0.4)
  E_LO_BP = (8.0, 30.0)
  E_LO_V = (0.35, 0.20)

  LOOKAHEAD_S = 0.12
  MAX_LOOKAHEAD_DEG = 5.0
  MIN_CLOSING_RATE = 1.0
  RELATIVE_RATE_TAU = 0.05
  CAPTURE_DAMPING = 0.008
  MAX_TORQUE_REMOVAL = 0.25
  CAPTURE_TIMEOUT_S = 0.75
  CAPTURE_RAMP_S = 0.08
  DIRECTION_CHANGE_TORQUE = 0.03

  DES_RATE_DISCONTINUITY = 100.0
  RELATIVE_RATE_QUIET = 3.0
  RELATIVE_RATE_RELEASE = 6.0
  DRIFT_BUDGET_DEGS = 0.35
  DWELL_S = 0.15
  MIN_TRACK_S = 0.12
  MIN_HOLD_S = 0.20
  XFADE_S = 0.08

  def __init__(self, dt: float, steer_max: float):
    self.dt = dt
    self.steer_max = steer_max
    self.state = LatStictionState.TRACK
    self.hold_torque = 0.0
    self.output = 0.0
    self.capture_scale = 1.0
    self.relative_motion = 0.0
    self.reason = "tracking"
    self._dwell_s = 0.0
    self._state_s = self.MIN_TRACK_S
    self._drift = 0.0
    self._reacquire_from = 0.0

  @property
  def holding(self) -> bool:
    return self.state is LatStictionState.HOLD

  @property
  def freeze_integrator(self) -> bool:
    return self.state is not LatStictionState.TRACK

  def reset(self) -> None:
    self.state = LatStictionState.TRACK
    self.hold_torque = 0.0
    self.output = 0.0
    self.capture_scale = 1.0
    self.relative_motion = 0.0
    self.reason = "reset"
    self._dwell_s = 0.0
    self._state_s = self.MIN_TRACK_S
    self._drift = 0.0
    self._reacquire_from = 0.0

  def _enter(self, state: LatStictionState, current_out: float, reason: str = "transition") -> None:
    self.state = state
    self.reason = reason
    self._state_s = 0.0
    self._dwell_s = 0.0
    self._drift = 0.0
    if state is LatStictionState.CAPTURE:
      self.capture_scale = 1.0
    elif state is LatStictionState.HOLD:
      self.hold_torque = _clip(current_out, -self.steer_max, self.steer_max)
    elif state is LatStictionState.REACQUIRE:
      self._reacquire_from = current_out
    elif state is LatStictionState.TRACK:
      self.capture_scale = 1.0

  def _passthrough(self, live_torque: float, reason: str) -> float:
    self._enter(LatStictionState.TRACK, live_torque, reason)
    self.output = live_torque
    return live_torque

  def _reacquire(self, live_torque: float) -> float:
    if self._reacquire_from * live_torque <= 0.0:
      self._enter(LatStictionState.TRACK, live_torque, "direction_change")
      self.output = live_torque
      return live_torque
    weight = _clip(self._state_s / self.XFADE_S, 0.0, 1.0)
    output = self._reacquire_from + weight * (live_torque - self._reacquire_from)
    if weight >= 1.0:
      self._enter(LatStictionState.TRACK, live_torque, "reacquired")
      output = live_torque
    self.output = output
    return output

  def _capture(self, live_torque: float, relative_motion: float) -> float:
    output = live_torque
    if live_torque * relative_motion > 0.0:
      removal = min(abs(live_torque), self.CAPTURE_DAMPING * abs(relative_motion),
                    self.MAX_TORQUE_REMOVAL)
      authority = _clip(self._state_s / self.CAPTURE_RAMP_S, 0.0, 1.0)
      output -= _sign(live_torque) * removal * authority
    self.capture_scale = abs(output / live_torque) if live_torque != 0.0 else 1.0
    return output

  def update(self, active: bool, v_ego: float, error_deg: float, des_rate_degs: float,
             wheel_rate_degs: float, live_torque: float,
             steering_pressed: bool, lane_changing: bool, saturated: bool) -> float:
    self._state_s += self.dt

    raw_relative_motion = wheel_rate_degs - des_rate_degs
    if not active:
      self.relative_motion = raw_relative_motion
      return self._passthrough(live_torque, "inactive")
    if steering_pressed:
      self.relative_motion = raw_relative_motion
      return self._passthrough(live_torque, "driver_override")
    if lane_changing:
      self.relative_motion = raw_relative_motion
      return self._passthrough(live_torque, "lane_change")
    if saturated:
      self.relative_motion = raw_relative_motion
      return self._passthrough(live_torque, "limited")

    alpha = _clip(self.dt / self.RELATIVE_RATE_TAU, 0.0, 1.0)
    self.relative_motion += alpha * (raw_relative_motion - self.relative_motion)

    e_hi = _interp(v_ego, self.E_HI_BP, self.E_HI_V)
    e_lo = _interp(v_ego, self.E_LO_BP, self.E_LO_V)
    relative_motion = self.relative_motion
    closing_rate = _sign(error_deg) * relative_motion

    if self.state is LatStictionState.TRACK:
      settled = (abs(error_deg) <= e_lo
                 and abs(relative_motion) <= self.RELATIVE_RATE_QUIET)
      self._dwell_s = self._dwell_s + self.dt if settled else 0.0
      capture_error = e_lo + min(self.LOOKAHEAD_S * max(closing_rate, 0.0), self.MAX_LOOKAHEAD_DEG)
      should_capture = (self._state_s >= self.MIN_TRACK_S
                        and abs(des_rate_degs) < self.DES_RATE_DISCONTINUITY
                        and closing_rate > self.MIN_CLOSING_RATE
                        and abs(error_deg) <= capture_error)
      if should_capture:
        self._enter(LatStictionState.CAPTURE, live_torque, "predictive_capture")
      elif settled and self._dwell_s >= self.DWELL_S:
        self._enter(LatStictionState.HOLD, live_torque, "quiet_settle")
        self.output = self.hold_torque
        return self.output
      else:
        self.output = live_torque
        return live_torque

    if self.state is LatStictionState.CAPTURE:
      output = self._capture(live_torque, relative_motion)
      settled = (abs(error_deg) <= e_lo
                 and abs(relative_motion) <= self.RELATIVE_RATE_QUIET)
      self._dwell_s = self._dwell_s + self.dt if settled else 0.0

      moving_away = closing_rate <= 0.0 and abs(error_deg) >= e_hi
      abort = (abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY
               or moving_away
               or self._state_s >= self.CAPTURE_TIMEOUT_S)
      if settled and self._dwell_s >= self.DWELL_S:
        self._enter(LatStictionState.HOLD, output, "capture_settled")
        self.output = self.hold_torque
        return self.output
      if abort:
        if abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY:
          reason = "target_discontinuity"
        elif moving_away:
          reason = "outer_error"
        else:
          reason = "capture_timeout"
        if reason == "target_discontinuity":
          return self._passthrough(live_torque, reason)
        self._enter(LatStictionState.REACQUIRE, output, reason)
        return self._reacquire(live_torque)
      self.output = output
      return output

    if self.state is LatStictionState.HOLD:
      if abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY:
        return self._passthrough(live_torque, "target_discontinuity")
      if self.hold_torque * live_torque < 0.0 and abs(live_torque) >= self.DIRECTION_CHANGE_TORQUE:
        return self._passthrough(live_torque, "direction_change")
      self._drift += error_deg * self.dt
      breakaway = (abs(error_deg) >= e_hi
                   or abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY
                   or abs(relative_motion) >= self.RELATIVE_RATE_RELEASE
                   or abs(self._drift) >= self.DRIFT_BUDGET_DEGS)
      urgent = (abs(error_deg) >= 2.0 * e_hi
                or abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY
                or abs(relative_motion) >= 2.0 * self.RELATIVE_RATE_RELEASE)
      if urgent or (breakaway and self._state_s >= self.MIN_HOLD_S):
        if abs(des_rate_degs) >= self.DES_RATE_DISCONTINUITY:
          reason = "target_discontinuity"
        elif abs(relative_motion) >= self.RELATIVE_RATE_RELEASE:
          reason = "wheel_motion"
        elif abs(self._drift) >= self.DRIFT_BUDGET_DEGS:
          reason = "accumulated_error"
        else:
          reason = "outer_error"
        if urgent:
          return self._passthrough(live_torque, reason)
        self._enter(LatStictionState.REACQUIRE, self.hold_torque, reason)
        return self._reacquire(live_torque)
      self.output = self.hold_torque
      return self.output

    return self._reacquire(live_torque)
