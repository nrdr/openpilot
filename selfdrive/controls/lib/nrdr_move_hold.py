# nrdr stiction

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


class MoveHold:
  # Constants below the ES350 line are calibrated against measured Lexus ES350 city
  # driving (8-15 m/s, 63 s engaged, hands-off): hold fraction 53% of drive time,
  # hold durations p50 0.76 s, wheel span tolerated within a hold p50 0.51 / p90 1.16 deg,
  # move durations p50 0.33 s, step amplitudes p50 0.54 / p75 1.78 deg, peak move rate
  # p50 6.5 deg/s. Commanded curvature is flat to 4 decimals during holds (plan steady).
  # Highway-end values remain physics estimates until a highway route is measured.
  E_HI_BP = (8.0, 30.0)       # m/s
  E_HI_V = (0.9, 0.4)         # deg; breakaway into MOVE (ES350 measured span p75-p90 at city)
  E_LO_BP = (8.0, 30.0)       # m/s
  E_LO_V = (0.35, 0.20)       # deg; error small enough to allow HOLD (ES350 holds begin
                              # with ~0.3-0.5 deg wander; 0.15 was tighter than the real car
                              # and risked never parking on a jittery Honda error signal)
  DES_RATE_MOVE = 2.0         # deg/s; plan actively turning -> MOVE (FF leads, never waits)
  DES_RATE_QUIET = 0.8        # deg/s; plan quiet enough to allow HOLD
  WHEEL_RATE_QUIET = 3.0      # deg/s; wheel actually settled before parking it
  DRIFT_BUDGET_DEGS = 0.35    # deg*s of accumulated held error -> MOVE (slow-creep guard)
  DWELL_S = 0.15              # HOLD-entry conditions must persist this long
  MIN_MOVE_S = 0.25           # once moving, commit (anti-chatter)
  MIN_HOLD_S = 0.20           # once holding, commit (unless error doubles E_HI)
  XFADE_S = 0.08              # output crossfade on every transition (no torque steps)
  KI_HOLD = 0.10              # torque/(deg*s); micro-integrator while holding
  HOLD_CAPTURE_TAU = 0.30     # s; low-pass that defines the captured hold torque
  MIN_SPEED = 3.0             # m/s; below this the stage is bypassed (parking)

  def __init__(self, dt: float, steer_max: float):
    self.dt = dt
    self.steer_max = steer_max
    self.holding = False
    self.hold_torque = 0.0
    self._lpf = 0.0           # running capture filter of the live output
    self._dwell_s = 0.0
    self._state_s = 1e9       # time in current state; starts saturated
    self._drift = 0.0
    self._xfade_s = 1e9       # time since last transition; starts saturated
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
    f = self._xfade_s / self.XFADE_S
    return self._xfade_from + f * (target - self._xfade_from)

  def update(self, active: bool, v_ego: float, error_deg: float, des_rate_degs: float,
             wheel_rate_degs: float, live_torque: float,
             steering_pressed: bool, lane_changing: bool, saturated: bool) -> float:
    """Returns the torque to send. live_torque is the fully computed PID+FF output."""
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
      # winding against stiction: only the micro-integrator runs
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

    # MOVE state
    e_lo = _interp(v_ego, self.E_LO_BP, self.E_LO_V)
    settled = (abs(error_deg) < e_lo and abs(des_rate_degs) < self.DES_RATE_QUIET
               and abs(wheel_rate_degs) < self.WHEEL_RATE_QUIET)
    self._dwell_s = self._dwell_s + self.dt if settled else 0.0
    if settled and self._dwell_s >= self.DWELL_S and self._state_s >= self.MIN_MOVE_S:
      out = self._blend(live_torque)
      self.hold_torque = self._lpf  # park on the smoothed recent output, not one noisy frame
      self._transition(True, out)
      return self._blend(self.hold_torque)
    return self._blend(live_torque)
