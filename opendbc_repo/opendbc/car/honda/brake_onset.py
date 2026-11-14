"""Civic Bosch brake-onset overshoot compensation.

The Civic's ACC ECU decelerates past the ACCEL_COMMAND while a brake request is
deepening, then settles back near the command. Evidence (log analysis, limited
road evidence), dongle 11c8fa231c0499ed routes 0d/0e/0f/10/13/1a, 2026-10-24:
  - 45 brake steps (command falling faster than 2 m/s^3): peak aEgo / peak command
    median 1.19 (p25 1.11, p75 1.27), about 0.35 m/s^2 deeper, at every speed band.
  - Steady braking after the 0.2 s lag is near 1.0-1.1, inside pitch uncertainty,
    so this is a transient, not a gain error.
  - Ten flagged brake events at 20 Hz: aEgo(t+0.25 s) ~= u + C*(u_f - LP(u_f)) when
    deepening, u_f = min(u, 0), LP first order. Best fit C 0.4..0.5, tau 1.0..1.5 s.
    RMSE 0.37 -> 0.27 m/s^2, better on every event (e.g. 0f t=774: 0.63 -> 0.44).

The compensation inverts that model, so the predicted decel equals the planner's
command: it only reduces a deepening brake command, never adds braking, and never
touches a release. C is set below the fit so an over-predicted overshoot costs at
most the cap. The relief fades out for commands approaching full braking so a
maximum brake request is always sent as asked.
"""

# Fit C 0.4..0.5; 0.35 keeps a margin toward under-compensation.
OVERSHOOT_GAIN = 0.35
# Fit tau 1.0..1.5 s; the shorter end limits how long a release-then-rebrake keeps relief.
OVERSHOOT_TAU_S = 1.0
# Largest command reduction. The measured step excess median is 0.35 m/s^2.
MAX_RELIEF_MPS2 = 0.5
# Relief is full at or above FADE_START and zero at or below FADE_END (BOSCH_ACCEL_MIN is -3.5).
FADE_START_MPS2 = -3.0
FADE_END_MPS2 = -3.5


class BrakeOnsetCompensation:
  def __init__(self, dt: float):
    self.alpha = dt / (OVERSHOOT_TAU_S + dt)
    self.reset()

  def reset(self):
    self.state = None
    self.relief = 0.0

  def update(self, accel: float, active: bool) -> float:
    braking = min(accel, 0.0)
    if not active or self.state is None:
      self.state = braking
      self.relief = 0.0
      return accel

    out = accel
    if braking < self.state:
      k = OVERSHOOT_GAIN * (1.0 - self.alpha)
      inverse = (braking + k * self.state) / (1.0 + k)
      relief = min(inverse - braking, MAX_RELIEF_MPS2)
      if accel <= FADE_END_MPS2:
        relief = 0.0
      elif accel < FADE_START_MPS2:
        relief *= (accel - FADE_END_MPS2) / (FADE_START_MPS2 - FADE_END_MPS2)
      out = accel + max(relief, 0.0)
    self.relief = out - accel
    # The filter follows what the ECU was actually asked for.
    self.state += self.alpha * (min(out, 0.0) - self.state)
    return out
