"""Civic Bosch low-speed crawl: a small integral "extra brake" below ~3 m/s (7 mph).

Evidence is replay only (Job, 2026-11-06, bpos + low-speed plant A, stops r99/9b/r96 + pool).
Below about 3 m/s (7 mph) behind a stopping car, the Civic Bosch delivers 0.2-0.4 m/s^2 less
decel than commanded and crawls the last metres instead of stopping cleanly. Ported from
mvl-boston opendbc sp-honda-dev-202608 @770d31735 carcontroller.py L320-326 / L1123-1137 and
tamed per replay arm K05N05R1: 9b_S0 crawl at 0.5-2 m/s cut 12.7 -> 7.2 s, pool unchanged vs
base (2 new/2 removed <-1 episodes, fidelity 0.844 vs 0.845, launch median 1.9 vs 1.8 s). The
replay plant is NOT validated for the final crawl (it cannot reproduce r99's crawl to 7 m), so
the road gain from this change is unmeasured.

This only ever adds braking, never gas: the output is never above the command it is given. The
stopping guard below only slows how fast the extra brake deepens while stopping. mvl's guard
(and the K05N05R1 replay) rate-limits the whole command, which would also hold back a sudden
deeper planner command in the stopping state; here the planner's own command always passes
(static reasoning; the replay's stopping-ramp arm S was inert, so the two should match there).
"""

import numpy as np

# 1/s. mvl uses 1.0; replay sweep K05N05R1 (Job, 2026-11-06) found 0.5 keeps ~85% of mvl's
# crawl cut while being gentler.
K_I = 0.5
# m/s^2, most extra brake the integrator may add. mvl uses -2.0. Replay: this limit had no
# effect on the stops tested; it only caps a wrong aEgo reading.
NEG_LIMIT = -0.5
# m/s, upper speed of the low-speed window (mvl).
V_MAX = 3.0
# m/s, below this the extra brake is dropped at once (R1); replay showed a jerk at the final
# snap to a stop without this reset.
V_RESET = 0.3
# m/s^2 per s, release rate once out of the window. mvl releases +0.02 per 50 Hz tick.
RELEASE_RATE = 1.0
# m/s^2 per s. mvl's stopping guard is 0.002 per 50 Hz tick: while stopping, the extra brake
# may deepen the output past its last value at most this fast. Never shallower than the command.
STOP_DEEPEN_RATE = 0.1


class LowSpeedBrakeAssist:
  """Integral-only (k_p = 0) extra brake for the Civic Bosch low-speed crawl."""

  def __init__(self, dt: float):
    self.dt = dt
    self.reset()

  def reset(self):
    self.i = 0.0
    self.last = None
    self.extra = 0.0

  def update(self, target: float, sent: float, a_ego: float, v_ego: float, active: bool, stopping: bool) -> float:
    if not active:
      self.reset()
      return sent

    if v_ego < V_RESET:
      self.i = 0.0
      out = sent
    elif target < 1e-3 and v_ego < V_MAX:
      self.i = float(np.clip(self.i + K_I * (target - a_ego) * self.dt, NEG_LIMIT, 0.0))
      out = min(sent, sent + self.i)
    else:
      self.i = min(0.0, self.i + RELEASE_RATE * self.dt)
      out = min(sent, sent + self.i)

    if stopping and self.last is not None:
      out = min(sent, max(out, self.last - STOP_DEEPEN_RATE * self.dt))

    self.last = out
    self.extra = out - sent
    return out
