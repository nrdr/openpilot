"""Bosch-A turn-off let-off: once a braking radar lead has been seen leaving our lane on the raw radar track, let the
brake off at FAST_JERK instead of BRAKE_RELEASE_JERK, and ask for no gas for NOGAS_S.

Owner report, route 000000cc 15:25 (2026-11-13): "my car was slowing down for a car turning right, and as the car
already turned to the right, my car slammed on the brake". The car ahead (radar track 22) slowed 13 -> 6 m/s while still
fused as leadOne, the command reached -3.43 as the radar released it, and the brake then let off at 2.5 m/s^3, so aEgo
peaked at -4.15 after the lead was gone.

Replay evidence (Job, open loop, bob-turnoff-arms3 @ 816b95048f arm A5C, scored per dir 2026-11-13):
  cc event: min target unchanged (-3.49); the brake reaches 0 by 926.8 s where the base is still at -1.37.
  main 1141 / second 99 episodes: score.py changed 0, harder 0, real_softer 0; fires on the real exits 9e s24, 7b s5,
  82 s6; does not fire on the radar dropouts 84 s7 and a2 s42 (lead still closing at about 1.25 m off centre);
  leaves the REAL brake 00000080 s19 untouched. No-gas cap binds 10.6 s over 8 main episodes (worst b3 s10 withholds
  +0.95 for 1.45 s). Fidelity 0.9489 vs 0.9494.
Rejected: the same let-off without the raw-track confirm (eased both dropouts) and a lateral aLeadK bound (softened the
REAL brake 80 s19 and acted on a2 s42 while the lead was under 1 m off centre and closing).

Trigger: the previous planner cycle's leadOne was a present radar lead closing faster than REL_VREL_MAX inside REL_D_MAX
with the target braking below REL_PREV_TARGET_MAX, and now leadOne is gone or a different, farther or non-closing lead.
Confirm: within CONFIRM_S the released track must still be in the raw radar tracks (radarTracks) and its |yRel| must have
grown by CONFIRM_DY to at least CONFIRM_Y. A track that vanishes or does not move out falls back to the base let-off.
While fast: a closing radar lead inside REL_D_MAX, or the watched track vanishing inside CLEAR_Y, ends it at once.
It only lets an existing brake off sooner and withholds gas; it never adds braking and never removes a radar point.
No raw tracks (radar fault, not subscribed) means nothing confirms, so it stays on the base let-off.
"""
from types import SimpleNamespace

FAST_JERK = 5.0            # m/s^3 let-off while fast (arm A5; A10 scored the same)
FAST_S = 1.0               # s
NOGAS_S = 2.0              # s from the confirm: no positive target (owner route 9e: "I'd rather it lift")
REL_VREL_MAX = -2.0        # m/s; previous radar lead was closing at least this fast
REL_D_MAX = 40.0           # m
REL_PREV_TARGET_MAX = -0.5  # m/s^2; only after a real brake
REL_JUMP_M = 10.0          # m; a different lead this much farther counts as released
CANCEL_VREL = -1.0         # m/s; a closing radar lead inside REL_D_MAX cancels the fast let-off

# Job's traces of the 5 biggest unconfirmed let-offs: real exits (9e s24, 7b s5, 82 s6, cc track 22) stay in the raw
# tracks after the release with |yRel| growing (cc: -1.07 as lead, then -1.51, -2.03, -2.65 ...); dropouts (84 s7: 12.5 m
# closing 8 m/s; a2 s42) vanish at about 1.25 m off centre with |yRel| grown 0.03-0.12 m.
CONFIRM_S = 0.6            # s after the trigger to see the track move out
CONFIRM_DY = 0.3           # m; |yRel| growth since it was the lead
CONFIRM_Y = 1.5            # m; and at least this far off centre
CLEAR_Y = 1.8              # m; a watched track that vanishes inside this cancels the fast let-off


def raw_track_y_or_none(sm) -> dict[int, float] | None:
  """nrdr: valid raw tracks, or None when unavailable (not subscribed, invalid or not alive). A valid empty frame is {}
  (no tracks remain), which is different from None (no data): the ghost must not read missing data as a clear."""
  try:
    rt = sm['radarTracks']
  except (KeyError, AttributeError):
    return None
  valid = getattr(sm, 'valid', {})
  alive = getattr(sm, 'alive', {})
  if not valid.get('radarTracks', True) or not alive.get('radarTracks', True):
    return None
  return {int(p.trackId): float(p.yRel) for p in rt.points}


def raw_track_y(sm) -> dict[int, float]:
  """{trackId: yRel} from the latest radarTracks; empty when not subscribed, invalid or not alive (PTM semantics)."""
  return raw_track_y_or_none(sm) or {}


def _snap(lead):
  if lead is None:
    return None
  return SimpleNamespace(present=bool(getattr(lead, 'present', False)), tid=int(getattr(lead, 'radarTrackId', -1)),
                         dRel=float(lead.dRel), vRel=float(lead.vRel), yRel=float(getattr(lead, 'yRel', 0.0)))


class FastLetoff:
  def __init__(self, dt):
    self.dt = dt
    self.fast_s = 0.0
    self.nogas_s = 0.0
    self.prev = None
    self.pend = None           # (tid, |y0|, seconds left) while waiting for confirmation
    self.watch = None          # (tid, last |y|) while letting off fast on a confirmed exit
    self.fired = 0
    self.aborted = 0

  def reset(self):
    self.fast_s = 0.0
    self.nogas_s = 0.0
    self.prev = None
    self.pend = None
    self.watch = None

  @property
  def no_gas(self) -> bool:
    return self.nogas_s > 0.0

  def update(self, lead_one, prev_target: float, raw_y: dict[int, float]) -> float | None:
    """Returns the let-off jerk to use this cycle, or None for the base rate."""
    prev, cur = self.prev, _snap(lead_one)
    self.prev = cur
    self.nogas_s = max(0.0, self.nogas_s - self.dt)
    if self.fast_s > 0.0 and self.watch is not None:
      tid, last_y = self.watch
      if tid in raw_y:
        self.watch = (tid, abs(raw_y[tid]))
      elif last_y < CLEAR_Y:
        self.fast_s = self.nogas_s = 0.0
        self.watch = None
        self.aborted += 1
    if self.pend is not None:
      tid, y0, left = self.pend
      if tid not in raw_y:
        self.pend = None
        self.aborted += 1
      elif abs(raw_y[tid]) >= max(y0 + CONFIRM_DY, CONFIRM_Y):
        self.pend = None
        self.fast_s, self.nogas_s = FAST_S, NOGAS_S
        self.watch = (tid, abs(raw_y[tid]))
        self.fired += 1
      elif left - self.dt <= 0.0:
        self.pend = None
        self.aborted += 1
      else:
        self.pend = (tid, y0, left - self.dt)
    if self.fast_s > 0.0:
      if cur is not None and cur.present and cur.tid >= 0 and cur.dRel < REL_D_MAX and cur.vRel < CANCEL_VREL:
        self.fast_s = 0.0
        self.nogas_s = 0.0
      else:
        self.fast_s = max(0.0, self.fast_s - self.dt)
    if (self.fast_s <= 0.0 and self.pend is None and prev is not None and prev.present and prev.tid >= 0 and
        prev.vRel < REL_VREL_MAX and prev.dRel < REL_D_MAX and prev_target < REL_PREV_TARGET_MAX):
      gone = cur is None or not cur.present
      switched = (not gone and cur.tid != prev.tid and
                  (cur.dRel > prev.dRel + REL_JUMP_M or cur.vRel >= -0.5))
      if gone or switched:
        self.pend = (prev.tid, abs(prev.yRel), CONFIRM_S)
    return FAST_JERK if self.fast_s > 0.0 else None
