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


class LatStiction:
  E_HI_BP = (8.0, 30.0)
  E_HI_V = (0.9, 0.4)
  E_LO_BP = (8.0, 30.0)
  E_LO_V = (0.35, 0.20)
  DES_RATE_MOVE = 2.0
  DES_RATE_QUIET = 0.8
  WHEEL_RATE_QUIET = 3.0
  DRIFT_BUDGET_DEGS = 0.35
  DWELL_S = 0.15
  MIN_MOVE_S = 0.25
  MIN_HOLD_S = 0.20
  XFADE_S = 0.08
  KI_HOLD = 0.10
  HOLD_CAPTURE_TAU = 0.30
  MIN_SPEED = 3.0

  def __init__(self, dt: float, steer_max: float):
    self.dt = dt
    self.steer_max = steer_max
    self.holding = False
    self.hold_torque = 0.0
    self._lpf = 0.0
    self._dwell_s = 0.0
    self._state_s = 1e9
    self._drift = 0.0
    self._xfade_s = 1e9
    self._xfade_from = 0.0

  def reset(self) -> None:
    self.holding = False
    self.hold_torque = 0.0
    self._lpf = 0.0
    self._dwell_s = 0.0
    self._state_s = 1e9
    self._drift = 0.0
    self._xfade_s = 1e9
    self._xfade_from = 0.0

  def _transition(self, to_hold: bool, current_out: float) -> None:
    self.holding = to_hold
    self._state_s = 0.0
    self._dwell_s = 0.0
    self._drift = 0.0
    self._xfade_s = 0.0
    self._xfade_from = current_out

  def _blend(self, target: float) -> float:
    if self._xfade_s >= self.XFADE_S:
      return target
    weight = self._xfade_s / self.XFADE_S
    return self._xfade_from + weight * (target - self._xfade_from)

  def update(self, active: bool, v_ego: float, error_deg: float, des_rate_degs: float,
             wheel_rate_degs: float, live_torque: float,
             steering_pressed: bool, lane_changing: bool, saturated: bool) -> float:
    self._lpf += (live_torque - self._lpf) * (self.dt / self.HOLD_CAPTURE_TAU)
    self._state_s += self.dt
    self._xfade_s += self.dt

    bypass = (not active or steering_pressed or lane_changing or saturated
              or v_ego < self.MIN_SPEED)
    if bypass:
      if self.holding:
        self._transition(False, self.hold_torque)
      self._dwell_s = 0.0
      return self._blend(live_torque)

    e_hi = _interp(v_ego, self.E_HI_BP, self.E_HI_V)

    if self.holding:
      self.hold_torque = _clip(self.hold_torque + self.KI_HOLD * error_deg * self.dt,
                               -self.steer_max, self.steer_max)
      self._drift += error_deg * self.dt
      breakaway = (abs(error_deg) > e_hi or abs(des_rate_degs) > self.DES_RATE_MOVE
                   or abs(self._drift) > self.DRIFT_BUDGET_DEGS)
      urgent = abs(error_deg) > 2.0 * e_hi
      if (breakaway and self._state_s >= self.MIN_HOLD_S) or urgent:
        self._transition(False, self.hold_torque)
        return self._blend(live_torque)
      return self._blend(self.hold_torque)

    e_lo = _interp(v_ego, self.E_LO_BP, self.E_LO_V)
    settled = (abs(error_deg) < e_lo and abs(des_rate_degs) < self.DES_RATE_QUIET
               and abs(wheel_rate_degs) < self.WHEEL_RATE_QUIET)
    self._dwell_s = self._dwell_s + self.dt if settled else 0.0
    if settled and self._dwell_s >= self.DWELL_S and self._state_s >= self.MIN_MOVE_S:
      out = self._blend(live_torque)
      self.hold_torque = self._lpf
      self._transition(True, out)
      return self._blend(self.hold_torque)
    return self._blend(live_torque)
