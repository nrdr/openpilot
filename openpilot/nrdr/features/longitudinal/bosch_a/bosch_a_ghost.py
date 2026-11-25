"""Bosch-A ghost let-off (arm G4, 1.5 s no-gas hold; in the car build 2026-11-14, replay evidence only): one rule for every brake that outlives its lead.

Owner, 2026-11-13: "ideally I want to develop a universal fix for all of those situations" (turn-offs, cut-outs,
radar dropouts, camera-only leads), replacing the turn-off trigger (bosch_a_turnoff.FastLetoff) and the release coast.

When the lead we were braking for leaves leadOne (gone, or replaced by a lead that is farther or not closing), it is kept
as a ghost: its last gap, speed and accel, moved forward in time. Each cycle the ghost gives the braking it still
justifies (a_req: stop behind it, assuming it keeps braking at min(aLeadK, 0) to a stop). The brake then lets off:
  - always at least at the base rate (BRAKE_RELEASE_JERK, unchanged);
  - faster, up to FAST_JERK, but never above the ghost's a_req (no evidence it left: physics alone bounds the let-off);
  - faster up to FAST_JERK all the way to the planner's target once the ghost is CLEARED.
Cleared means evidence the obstacle left our path: its raw radar track grew to |yRel| >= CLEAR_Y_LETOFF by at least
CLEAR_DY, or the camera's lead 0 has been absent (prob < CAM_CLEAR_PROB, or farther than ghost + CAM_FAR_M) for
CAM_CLEAR_S. Gas is withheld while the ghost lives and is not GAS-cleared (|yRel| >= CLEAR_Y_GAS, or the raw track
vanished after passing CLEAR_Y_LETOFF), for at most NOGAS_MAX_S.
Arm G3: before a clear only the base let-off applies (the a_req bound above is not used; see the end of update).
The ghost dies when a lead within MERGE_M of it comes back (the planner owns it again), a closing lead inside
CLOSE_D_M appears, the ghost has been gas-cleared, or after GHOST_MAX_S.
It never adds braking (every output is min(target, ...) or a slower-than-planner rise) and never removes a radar point.
Radar dropout with the car still there: the camera still sees it and the raw track did not move out, so only a_req
applies; at short gaps a_req stays below the base let-off and nothing changes.
"""
from types import SimpleNamespace

FAST_JERK = 5.0          # m/s^3; the confirmed turn-off rate (FastLetoff A5C; A10 scored the same)
TRIGGER_PREV_TARGET = -0.5  # m/s^2; only a ghost of a lead we were actually braking for
TRIGGER_JUMP_M = 10.0    # m; a different lead this much farther counts as the old one released
TRIGGER_VREL = -0.5      # m/s; the old lead must have been closing at least this fast
STOP_GAP_M = 4.0         # m; gap a_req stops us at behind the ghost
GHOST_MAX_S = 3.0        # s
NOGAS_MAX_S = 1.5        # s; upper bound on the no-gas hold (was 2.0, the fixed FastLetoff hold; Peter 2026-11-14 chose 1.5 over 1.0)
MERGE_M = 6.0            # m; a lead this close to the ghost's predicted gap is the same obstacle back
CLOSE_D_M = 40.0         # m
CLOSE_VREL = -1.0        # m/s
CLEAR_DY = 0.3           # m; raw track |yRel| growth since it was the lead (FastLetoff CONFIRM_DY)
CLEAR_Y_LETOFF = 1.5     # m; FastLetoff CONFIRM_Y
CLEAR_Y_GAS = 3.0        # m; arm NGC
CAM_CLEAR_PROB = 0.3
CAM_FAR_M = 15.0         # m
CAM_CLEAR_S = 0.3        # s
CAM_RADAR_DX = 1.5       # m; device-frame x minus radar dRel, rough
# Arm G (2a4caf6644) failed replay: the camera clear eased the radar dropouts 84 s7 (+1.62, raw track still at |y| 1.27)
# and a2 s42 (+0.5). The camera clear now only counts for a camera ghost, or a radar ghost whose raw track was last seen
# at least this far out (FastLetoff CLEAR_Y); that keeps it for far-off-centre leads (80 s3, y0 4.33).
CAM_RADAR_Y = 1.8        # m


def ghost_a_req(d: float, v_ego: float, v_lead: float, a_lead: float) -> float:
  """Decel that stops us STOP_GAP_M behind a lead at gap d that brakes at a_lead (<= 0) to a stop. <= 0."""
  v_ego, v_lead = max(v_ego, 0.0), max(v_lead, 0.0)
  a_lead = min(a_lead, 0.0)
  lead_stop = v_lead * v_lead / (2.0 * -a_lead) if a_lead < -0.05 else 1e6
  room = d + lead_stop - STOP_GAP_M
  if room <= 0.5 or d - STOP_GAP_M <= 0.5:
    return -10.0
  if v_ego <= v_lead and a_lead >= -0.05:
    return 0.0
  if a_lead >= -0.05:  # constant-speed lead: close the speed gap within the room
    return -min(10.0, (v_ego - v_lead) ** 2 / (2.0 * max(d - STOP_GAP_M, 0.5)))
  return -min(10.0, v_ego * v_ego / (2.0 * room))


def _snap(lead):
  if lead is None or not bool(getattr(lead, 'present', False)):
    return None
  return SimpleNamespace(tid=int(getattr(lead, 'radarTrackId', -1)), dRel=float(lead.dRel), vRel=float(lead.vRel),
                         vLead=float(getattr(lead, 'vLeadK', getattr(lead, 'vLead', 0.0))),
                         aLead=float(getattr(lead, 'aLeadK', 0.0)), yRel=float(getattr(lead, 'yRel', 0.0)))


class Ghost:
  def __init__(self, src, ttl: float):
    self.tid = src.tid
    self.d = src.dRel
    self.d0 = src.dRel
    self.v_lead = max(src.vLead, 0.0)
    self.a_lead = min(src.aLead, 0.0)
    self.y0 = abs(src.yRel)
    self.y_last = self.y0
    self.age = 0.0
    self.ttl = ttl
    self.letoff_clear = False
    self.gas_clear = False
    self.cam_clear_s = 0.0
    self.raw_seen = False

  def advance(self, dt: float, v_ego: float):
    self.age += dt
    v_next = max(0.0, self.v_lead + self.a_lead * dt)
    self.d += ((self.v_lead + v_next) / 2.0 - v_ego) * dt
    self.v_lead = v_next


class GhostLetoff:
  def __init__(self, dt):
    self.dt = dt
    self.prev = None
    self.ghost = None
    self.nogas_s = 0.0
    self.fired = 0      # ghosts born
    self.cleared = 0    # ghosts cleared for the fast let-off
    self.end_reason = ''  # why the last ghost ended (back/closing/ttl/skip/reset); diagnostic only

  def reset(self):
    if self.ghost is not None:
      self.end_reason = 'reset'
    self.prev = None
    self.ghost = None
    self.nogas_s = 0.0

  @property
  def no_gas(self) -> bool:
    return self.nogas_s > 0.0

  def _cam_clear(self, g, model_lead0) -> bool:
    if model_lead0 is None:
      return False
    prob, x = model_lead0[0], model_lead0[1]
    return prob < CAM_CLEAR_PROB or (x - CAM_RADAR_DX) > g.d + CAM_FAR_M

  def update(self, lead_one, prev_target: float, v_ego: float, raw_y: dict[int, float] | None, model_lead0=None,
             skip: bool = False):
    """Returns (jerk, floor): let off at up to `jerk` but not above `floor` (None, None = base let-off only)."""
    prev, cur = self.prev, _snap(lead_one)
    self.prev = cur
    self.nogas_s = max(0.0, self.nogas_s - self.dt)
    g = self.ghost

    if g is not None:
      g.advance(self.dt, v_ego)
      back = cur is not None and abs(cur.dRel - g.d) < MERGE_M and (g.tid < 0 or cur.tid == g.tid or cur.tid < 0)
      # Arm G4: only a closing lead no farther than where the ghost was born (+ MERGE_M) takes over. A farther one is the
      # planner's (the cleared let-off never goes past the planner's target): G3 let a camera lead 25.6 m out, closing
      # 1.27 m/s, kill the 10.5 m turner's ghost on pb c1 s13 before its raw track moved out (+0.375 vs car for 0.6 s).
      closing = (cur is not None and cur.dRel < min(CLOSE_D_M, g.d0 + MERGE_M) and cur.vRel < CLOSE_VREL)
      if back or closing or g.age >= g.ttl:
        self.end_reason = 'back' if back else ('closing' if closing else 'ttl')  # diagnostic only (bosch_a_ghost log)
        self.ghost = g = None
        self.nogas_s = 0.0 if (back or closing) else self.nogas_s
    if g is not None:
      if raw_y is not None and g.tid >= 0 and g.tid in raw_y:
        g.raw_seen = True
        y = abs(raw_y[g.tid])
        g.y_last = y
        if y >= max(g.y0 + CLEAR_DY, CLEAR_Y_LETOFF):
          g.letoff_clear = True
        if y >= CLEAR_Y_GAS:
          g.gas_clear = True
      elif raw_y is not None and g.raw_seen and g.y_last >= CLEAR_Y_LETOFF:
        g.gas_clear = True  # vanished after moving out
      # A radar ghost whose track was last seen inside CAM_RADAR_Y (still there, or vanished there) is the dropout
      # signature (84 s7, a2 s42): the camera losing it does not clear it. Far-off-centre leads keep the camera path.
      cam_ok = g.tid < 0 or g.y_last >= CAM_RADAR_Y
      g.cam_clear_s = g.cam_clear_s + self.dt if (cam_ok and self._cam_clear(g, model_lead0)) else 0.0
      if g.cam_clear_s >= CAM_CLEAR_S:
        g.letoff_clear = True
      # Arm G3: a ghost extrapolated behind us is no longer a clear (84 s7 dropout "cleared" that way at 1.65 s): it only
      # shows the extrapolation was wrong, not that the car left. The ghost then runs out on GHOST_MAX_S.
      if g.letoff_clear and not getattr(g, 'counted', False):
        g.counted = True
        self.cleared += 1
      if g.gas_clear:
        self.nogas_s = 0.0

    if skip:  # lane change, blinker or gas pressed: passing a slower car also releases its lead, and we want gas there
      if g is not None:
        self.end_reason = 'skip'
      self.ghost = g = None
      self.nogas_s = 0.0
    elif (g is None and prev is not None and prev.vRel < TRIGGER_VREL and prev_target < TRIGGER_PREV_TARGET and
          (cur is None or ((cur.tid != prev.tid or cur.tid < 0) and
                           (cur.dRel > prev.dRel + TRIGGER_JUMP_M or cur.vRel >= TRIGGER_VREL)))):
      self.ghost = g = Ghost(prev, GHOST_MAX_S)
      self.nogas_s = NOGAS_MAX_S
      self.fired += 1
      if raw_y is not None and g.tid >= 0 and g.tid in raw_y:
        g.raw_seen = True

    if g is None:
      return None, None
    if g.letoff_clear:
      return FAST_JERK, 0.0
    # Arm G3: before a clear, the base let-off only. G/G2 let off faster up to ghost_a_req here; on the dropouts 84 s7 and
    # a2 s42 that eased the brake (+0.25) with no evidence the car left, and on the unfired Part A triggers it gained
    # <= 0.07. Only the no-gas hold acts on an uncleared ghost.
    return None, None
