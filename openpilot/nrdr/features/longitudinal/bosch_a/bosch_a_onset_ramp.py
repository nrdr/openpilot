"""Bosch-A brake onset ramp: a brake that starts with every lead far away builds at ONSET_JERK instead of in one frame.

Owner 2026-11-05: "Why can we just mimic stock brake for those situations? Instead of just slamming the brake".
Stock ACC on route 299 (STATUS 214) brings a brake in at -1.4..-3.4 m/s^3 per step; ours stepped at -36..-52 m/s^3
on the route 84 far brakes (E1, E4), e2ae and e2f8. The old D-083 ramp (6f1a05b37) would not have changed them: its
lead-braking and need gates stand it down on every one, because the lead is already braking hard at onset.

Replay (Job, base dad6bbbb6, open loop, arm R4b; limited road evidence, not driven):
  - first-jolt jerk 44-52 -> 8 m/s^3 on 84 E1/E4/vn84_3/vn84_11, 34 -> 8 on e2ae, 43 -> 8 on e2f8; peak decel unchanged
    (-3.5 stays -3.5), onset at -2 at most 0.15 s later.
  - min gap 0.4-0.9 m smaller on those events (e2ae: -0.62 m, ending at 4.8 m); min TTC within 0.08 s.
  - the 2f5 close stop (onset dRel 38.1 m) is exempt and equals today's output; pooled 0.85 h: same brake episode
    counts, no episode closer by more than 2 m.
  - nothing at onset (need, closing speed) separates e2ae/2f5 from the 84 far brakes; only the onset distance does.
    EXEMPT_D_M = 40 sits between 2f5 (38.1 m) and e2f8 (43.9 m); 30 m capped 2f5 and cost it 0.36 m.
  - an in-brake close-gap stand-down (R5) changed nothing: the ramp finishes in ~0.4 s, before the gap gets close.

Channels: reads radarState leadOne/leadTwo (present, dRel, vRel) as published; a railed vRel (U11 low rail -12) only
makes TTC smaller, which stands the ramp down, never extends it. Only the fall rate of the target is capped; the peak is
never reduced, rises pass through, and dRel/vLead/radar points are untouched (D-041/D-042).
"""
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a.gate import vehicle_supported

ONSET_JERK = 8.0         # m/s^3, the fastest a non-exempt brake may deepen
START_ACCEL = -0.3       # m/s^2: the target below this starts a brake episode
END_ACCEL = -0.1         # m/s^2: the target back at or above this ends it
EXEMPT_D_M = 40.0        # any lead closer than this as the episode starts: no ramp for the whole episode
TTC_STAND_DOWN_S = 2.0   # any lead at or below this TTC: no ramp for the rest of the episode


def active_leads(leads):
  return [lead for lead in leads if lead is not None and bool(getattr(lead, 'present', False))]


def lead_close(leads) -> bool:
  return any(float(lead.dRel) < EXEMPT_D_M for lead in active_leads(leads))


def lead_ttc_low(leads) -> bool:
  for lead in active_leads(leads):
    closing = -float(lead.vRel)
    if closing > 1e-3 and float(lead.dRel) / closing <= TTC_STAND_DOWN_S:
      return True
  return False


def ramp_limited_target(prev: float, target: float, dt: float) -> float:
  """A brake below min(prev, 0) deepens at most ONSET_JERK * dt per step; throttle cuts and rises pass through."""
  start = min(prev, 0.0)
  if target >= start:
    return float(target)
  return float(max(target, start - ONSET_JERK * dt))


class BoschAOnsetRamp:
  def __init__(self, CP, dt: float = DT_MDL):
    self.enabled = vehicle_supported(CP)
    self.dt = dt
    self.reset()

  def reset(self):
    self.in_episode = False
    self.free = False  # this episode passes through (close lead at its start, low TTC, FCW or stopping)

  def step(self, *, lead_one, lead_two, prev: float, target: float, fcw: bool, stopping: bool, reset: bool) -> float:
    """`prev` is last cycle's published target, `target` this cycle's before the ramp. Only ever less braking, briefly."""
    if not self.enabled or reset:
      self.reset()
      return float(target)
    leads = (lead_one, lead_two)
    if self.in_episode and target >= END_ACCEL:
      self.reset()
    if not self.in_episode:
      if target >= START_ACCEL:
        return float(target)
      self.in_episode = True
      self.free = lead_close(leads)
    if fcw or stopping or lead_ttc_low(leads):
      self.free = True
    if self.free:
      return float(target)
    return ramp_limited_target(prev, target, self.dt)
