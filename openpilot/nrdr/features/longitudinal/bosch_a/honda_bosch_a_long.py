"""Honda Bosch A Long Enhancement: longitudinal behavior that is active whenever the Bosch-A radar is on.

NRDR port (verbatim logic): the BoschAStockBrakeFeel owner toggle is removed (permanently on, `stock_brake_feel` defaults
True) and active_for delegates to bosch_a/gate.py. Everything below that mentions the toggle is the SOURCE history.

Ported from openpilot-radar (ns-bosch-radar-testing @ 567495f4ad + 6db22115e8, selfdrive/controls/lib/longitudinal_planner.py).
Active only when `active_for(CP)`: a Honda on a Bosch-A platform (VERIFIED_BOSCH_A_CARS, same as
`bosch_a_radar_platform`, including alt-radar stock) with openpilot longitudinal and the radar not
disabled (`HondaBoschARadar`), which is the same gate radard uses to build BoschALeadPolicy. Each part also has its own
switch: Stock Brake Feel is the owner toggle `BoschAStockBrakeFeel` (bosch_a_toggles.py, default Off, read once when
plannerd starts and passed in as `stock_brake_feel`); STOP_EASE_ENABLED, RADAR_LEAD_RECOVERY and BIRTH_RAIL_ENABLED are
constants and stay off; NEWBORN_HOLD_ENABLED (D-080 alone) is a constant and is on. Both longitudinal planners
(StarPilot's and the upstream one) call it the same way.

Contents:
- Stock Brake Feel (D-086, D-100, D-103, D-120): stock Honda ACC's TTC depth and jerk tables, with the soft exit,
  takeover hold, lead-stop law (<= 20 s) and the emergency latch.
- Stop ease (planner side): the brake eases toward about -0.5 m/s^2 at the stop when there is room.

The planner calls `step()` once per cycle, after every other target owner and before the final clip. Every limit
here only shapes how a brake builds or lets off; the emergency latch passes the planner's target through untouched,
so the car never brakes harder than the planner would without this module. Replay and limited road evidence only.

HumanFollowing and HumanAcceleration are separate modules (human_following.py, human_acceleration.py) because they
also run with the radar off (vision-only).
"""
import numpy as np

# ---- Stock Brake Feel (D-086), comments abridged from the source; see STATUS/DECISIONS for the evidence -------------
# While a lead closes faster than STOCK_FEEL_MIN_CLOSING and the worst TTC is over STOCK_FEEL_TTC_FLOOR_S, the target may
# go no deeper than the depth table and may deepen no faster than the jerk table (fitted to stock ACC_CONTROL).
STOCK_FEEL_DEPTH_BP = [2.0, 2.25, 2.75, 3.5, 4.5, 5.5, 6.5, 7.5, 9.0, 11.0, 13.5, 17.5, 25.0]  # s
STOCK_FEEL_DEPTH_V = [-3.5, -3.2, -2.4, -2.3, -2.3, -2.1, -1.7, -1.6, -1.28, -1.09, -0.88, -0.74, -0.35]  # m/s^2
# Far entry (TTC >= 25 s): -0.6 instead of -0.35 while the nearest lead is within STOCK_FEEL_FAR_GAP_S of time gap
# (owner 2026-11-06). Route 96 32:17 (49 mph, lead then braking -3): the -0.35 cap held a plateau for ~6 s and the
# driver took over; 8f B3 slowed too late on the same plateau. An ungated -0.6 (c59ee88e4, driven on route 99) added
# far-lead brakes: vn80 -1.58 at gap 8.2 s, p78 -1.04 at gap 92 s. Only the time gap separates them: the plateau
# frames sit at 1.2-2.0 s (T4) and 3.3-3.6 s (B3), the far brakes at 9-10 s and 100+ s; lead decel, closing speed
# and a closing/distance need all overlapped (aLeadK reads -0.8..-1.2 on the far brakes). Replay (Job, open loop,
# Stock Brake Feel + Human Following + Approaching lead buffer on; limited road evidence): T4 min gap 0.54 -> 0.91 s,
# B3 2.26 -> 2.71 s, both equal to the ungated -0.6; 2.46 h pooled vs ungated: both far brakes gone, 3 marginal new
# <-1 episodes (two 1-frame -1.01/-1.03, one -1.18 at 7.8 s), all traced to closed-loop divergence.
STOCK_FEEL_FAR_DEPTH = -0.6  # m/s^2
STOCK_FEEL_FAR_GAP_S = 5.0   # s
STOCK_FEEL_JERK_BP = [2.0, 2.5, 6.0, 10.0]  # s
STOCK_FEEL_JERK_V = [3.0, 2.0, 1.0, 0.6]  # m/s^3
STOCK_FEEL_TTC_FLOOR_S = 2.0
STOCK_FEEL_MIN_CLOSING = 0.5  # m/s
# Outside the law (TTC at or under the floor, or no lead closing) the depth is kept but deepens no faster than this
# (STATUS 220: without it the target stepped -0.6..-1.65 in one frame; stock's own p98 is 2-3.4 m/s^3).
STOCK_FEEL_JERK_OUTSIDE = 5.0  # m/s^3
# D-125 (329 8:02): soft exit when the closing speed falls under STOCK_FEEL_MIN_CLOSING.
STOCK_FEEL_SOFT_EXIT = True
STOCK_FEEL_EXIT_JERK = 0.6   # m/s^3
STOCK_FEEL_EXIT_HOLD_S = 2.0  # s
# Takeover hold (owner 2026-10-08, 2f7 26:38): a brake already deeper than the cap is let off at this rate, not cut.
STOCK_FEEL_CAP_RELEASE_JERK = 0.3  # m/s^3
# Lead stopping (owner 2026-10-07, 2f2 1099/1483): a closing lead braking at STOCK_FEEL_LEAD_STOP_A or harder moves the
# cap to the decel needed to stop STOCK_FEEL_LEAD_STOP_GAP behind it. D-120 (324): leads more than
# STOCK_FEEL_LEAD_STOP_MAX_T s from stopping are left to the table (12 s delayed a real slowing lead on 324 2790).
STOCK_FEEL_LEAD_STOP = True
STOCK_FEEL_LEAD_STOP_A = -1.0  # m/s^2
STOCK_FEEL_LEAD_STOP_GAP = 4.0  # m
STOCK_FEEL_LEAD_STOP_MAX_T = 20.0  # s
# Emergency bypass (owner 2026-10-07, 2f5 ~10:01: a lead braking -6.5 was met at stock's depth and the driver had to
# brake). Latched while any lead is closing: the planner's target passes through with no cap and no jerk limit.
STOCK_FEEL_EMERGENCY = True
STOCK_FEEL_EMERGENCY_A_LEAD = -2.0  # m/s^2
STOCK_FEEL_EMERGENCY_NEED = 2.0  # m/s^2
# The aLeadK path only latches when the worst TTC is at most this (openpilot-radar STATUS 258, 6db22115e8): 3a3
# 17:28.35 aLeadK -2.09 at TTC 21.7 s latched and stayed on through a separate build 15 s later that ran to -3.03.
STOCK_FEEL_EMERGENCY_A_LEAD_MAX_TTC = 10.0  # s

# ---- Stop ease (owner 2026-10-07, 2f2: every hard stop reached standstill still braking -1.6..-1.7, the clunk) ------
STOP_EASE = True
STOP_EASE_BP = [0.0, 1.0, 3.0]  # m/s
STOP_EASE_V = [-0.5, -1.1, -2.5]  # m/s^2
STOP_EASE_JERK = 2.0  # m/s^3
STOP_EASE_MIN_GAP = 2.0  # m


# ---- Switches (owner 2026-10-20: drive James's night-star7 as shipped first, so every switch is off) -----------------
# Stock Brake Feel (the stock-ACC depth/jerk law and the emergency latch, step()) is no longer a constant here: owner
#   2026-10-22 asked for it as a toggle usable with either planner, so it is the `BoschAStockBrakeFeel` param (default
#   Off), passed to HondaBoschALongEnhancement as `stock_brake_feel`. Still gated by active_for(CP).
# STOP_EASE_ENABLED: the planner-side brake ease at the stop (step()).
# RADAR_LEAD_RECOVERY groups D-089 (far-range recovery), D-075 (newborn range publish) and D-080 (newborn aLeadK
#   bound). Only D-080 is ported (planner_radar_state()). D-089 and D-075 live in the decoder
#   (bosch_a_radar.BOSCH_A_REANCHOR_RECOVER_SIGMA_FRAC = 0, BOSCH_A_NEWBORN_RANGE_PUBLISH = False) and need radard
#   gates (RECOVERED_CAM_GATE, NEWBORN_*) plus RadarPoint fields (`measured`, `recovered`) that 7.0 does not have, so
#   this switch does NOT turn them on. Turning those decoder constants on without the gates is the rejected
#   configuration (STATUS 225; D-075 phantom brakes on 280/294/2ae/284).
# NEWBORN_HOLD_ENABLED: D-080 (newborn aLeadK bound, planner_radar_state()) on its own switch, on since 2026-11-11
#   (owner: "Port the hold alone to my branch"). It needs none of the decoder or radard parts above. Evidence, open-loop
#   replay only, not driven: route 000000bd seg10 ~621.8 s, radar track 23 became the lead with aLeadK -2.44 and
#   tripped the Stock Brake Feel emergency latch through the stopping-need path (need 2.56); with the hold the target
#   peak went -2.37 -> -2.23, worst step jerk -8.0 -> -1.4 m/s^3, latch rows 44 -> 0; the real hard stop on seg5 (5:34)
#   was identical (-3.50, 79 latch rows). Corpus (36 routes + second set, on the bob-unify-bd build f0024b0c3d, not this
#   base): 52 episodes moved, 0 harder, no REAL or PHANTOM label moved; owner reviewed the largest softenings (ep49,
#   ep417, ep2111) and accepted them. Onsets slipped by up to 0.35 s on unlabelled episodes.
STOP_EASE_ENABLED = False
RADAR_LEAD_RECOVERY = False
NEWBORN_HOLD_ENABLED = True


def active_for(CP) -> bool:
  """Same gate as radard's BoschALeadPolicy: Bosch-A Honda (classic or alt-radar), radar on, openpilot longitudinal."""
  from openpilot.nrdr.features.longitudinal.bosch_a.gate import active_for as _gate_active_for
  return _gate_active_for(CP)


def _present(lead) -> bool:
  return lead is not None and bool(getattr(lead, 'present', False))


def brake_onset_limited_target(prev: float, target: float, dt: float, jerk: float | None) -> float:
  """A brake below min(prev, 0) may deepen at most jerk * dt per step; throttle cuts, rises and jerk None pass through."""
  start = min(prev, 0.0)
  if jerk is None or target >= start:
    return float(target)
  return float(max(target, start - jerk * dt))


def brake_onset_ttc(leads, min_closing: float = 1e-3) -> float:
  """Worst time to contact (s) over the present closing leads; inf when none is closing."""
  ttc_min = float('inf')
  for lead in leads:
    if not _present(lead):
      continue
    closing = max(0.0, -float(lead.vRel))
    if closing > min_closing:
      ttc_min = min(ttc_min, float(lead.dRel) / closing)
  return ttc_min


def lead_stop_need(leads, v_ego: float, max_t: float = 0.0) -> float:
  """Decel (m/s^2, >= 0) to stop STOCK_FEEL_LEAD_STOP_GAP behind where the worst closing, braking lead will stop; 0 when
  no closing lead is braking at STOCK_FEEL_LEAD_STOP_A or harder. With max_t > 0, a lead more than max_t s from stopping
  is skipped."""
  need = 0.0
  for lead in leads:
    if not _present(lead) or not -float(lead.vRel) > STOCK_FEEL_MIN_CLOSING:
      continue
    a_lead = float(getattr(lead, 'aLeadK', 0.0))
    if not a_lead <= STOCK_FEEL_LEAD_STOP_A:
      continue
    v_lead = max(float(getattr(lead, 'vLead', v_ego + float(lead.vRel))), 0.0)
    if max_t > 0 and v_lead > max_t * -a_lead:
      continue
    room = float(lead.dRel) + v_lead * v_lead / (2.0 * -a_lead) - STOCK_FEEL_LEAD_STOP_GAP
    need = max(need, float(v_ego) ** 2 / (2.0 * max(room, 0.5)))
  return need


def stock_feel_emergency(leads, v_ego: float, active: bool) -> bool:
  """Latch: True while a lead is closing once a closing lead brakes at STOCK_FEEL_EMERGENCY_A_LEAD or harder, or stopping
  behind a braking lead needs at least STOCK_FEEL_EMERGENCY_NEED and more than the table's depth."""
  ttc = brake_onset_ttc(leads, STOCK_FEEL_MIN_CLOSING)
  if not STOCK_FEEL_EMERGENCY or ttc == float('inf'):
    return False
  if active:
    return True
  for lead in leads:
    if _present(lead) and -float(lead.vRel) > STOCK_FEEL_MIN_CLOSING and float(lead.aLeadK) <= STOCK_FEEL_EMERGENCY_A_LEAD and \
       ttc <= STOCK_FEEL_EMERGENCY_A_LEAD_MAX_TTC:
      return True
  need = lead_stop_need(leads, v_ego)
  depth = stock_feel_depth(leads, ttc, v_ego)
  return need >= STOCK_FEEL_EMERGENCY_NEED and need > -depth


def stock_feel_held_cap(prev: float, cap: float, dt: float) -> float:
  """The cap, except that a brake already deeper than it (prev) is only let off at STOCK_FEEL_CAP_RELEASE_JERK."""
  if prev < cap:
    return float(min(cap, prev + STOCK_FEEL_CAP_RELEASE_JERK * dt))
  return float(cap)


def stock_feel_law_active(leads, emergency: bool) -> bool:
  """True while stock_feel_target applies the fitted law (a lead closing, TTC over the floor, no emergency)."""
  ttc = brake_onset_ttc(leads, STOCK_FEEL_MIN_CLOSING)
  return not emergency and ttc > STOCK_FEEL_TTC_FLOOR_S and ttc != float('inf')


def stock_feel_depth(leads, ttc: float, v_ego: float) -> float:
  """Depth table at this TTC; the far entry is STOCK_FEEL_FAR_DEPTH while the nearest lead is within
  STOCK_FEEL_FAR_GAP_S of time gap."""
  depth_v = STOCK_FEEL_DEPTH_V
  d_near = min((float(lead.dRel) for lead in leads if _present(lead)), default=float('inf'))
  if d_near <= STOCK_FEEL_FAR_GAP_S * max(float(v_ego), 0.0):
    depth_v = STOCK_FEEL_DEPTH_V[:-1] + [STOCK_FEEL_FAR_DEPTH]
  return float(np.interp(ttc, STOCK_FEEL_DEPTH_BP, depth_v))


def stock_feel_target(leads, prev: float, target: float, dt: float, v_ego: float = 0.0,
                      emergency: bool = False, law_recent: bool = False) -> float:
  """D-086 stock Honda ACC brake law (see the constants above)."""
  if emergency:
    return float(target)
  ttc = brake_onset_ttc(leads, STOCK_FEEL_MIN_CLOSING)
  if ttc == float('inf') and law_recent and STOCK_FEEL_SOFT_EXIT and not any(
      _present(lead) and float(lead.aLeadK) <= STOCK_FEEL_LEAD_STOP_A for lead in leads):
    return brake_onset_limited_target(prev, target, dt, STOCK_FEEL_EXIT_JERK)
  if not ttc > STOCK_FEEL_TTC_FLOOR_S or ttc == float('inf'):
    return brake_onset_limited_target(prev, target, dt, STOCK_FEEL_JERK_OUTSIDE)
  depth = stock_feel_depth(leads, ttc, v_ego)
  if STOCK_FEEL_LEAD_STOP:
    need = lead_stop_need(leads, v_ego, STOCK_FEEL_LEAD_STOP_MAX_T)
    if need > -depth:
      return brake_onset_limited_target(prev, max(target, stock_feel_held_cap(prev, -min(need, 3.5), dt)), dt,
                                        STOCK_FEEL_JERK_OUTSIDE)
  target = max(target, stock_feel_held_cap(prev, depth, dt))
  return brake_onset_limited_target(prev, target, dt, float(np.interp(ttc, STOCK_FEEL_JERK_BP, STOCK_FEEL_JERK_V)))


def stop_ease_distance(v: float) -> float:
  """Distance (m) to stop from v under the STOP_EASE_V floor."""
  n = 20
  dv = max(float(v), 0.0) / n
  return float(sum((i + 0.5) * dv * dv / -float(np.interp((i + 0.5) * dv, STOP_EASE_BP, STOP_EASE_V)) for i in range(n)))


def stop_ease_floor(v_ego: float, d_lead: float | None) -> float | None:
  """Floor (m/s^2) at this speed, or None when off, above STOP_EASE_BP[-1], or when the eased stop would end closer
  than STOP_EASE_MIN_GAP to the lead."""
  if not STOP_EASE or not float(v_ego) < STOP_EASE_BP[-1]:
    return None
  if d_lead is not None and stop_ease_distance(v_ego) > float(d_lead) - STOP_EASE_MIN_GAP:
    return None
  return float(np.interp(max(float(v_ego), 0.0), STOP_EASE_BP, STOP_EASE_V))


def stop_eased_target(prev: float, target: float, floor: float | None, dt: float) -> float:
  """Raise a target below the floor toward it, at most STOP_EASE_JERK * dt per step above prev."""
  if floor is None or not target < floor:
    return float(target)
  return float(min(floor, max(target, prev + STOP_EASE_JERK * dt)))


class HondaBoschALongEnhancement:
  def __init__(self, CP, dt: float, stock_brake_feel: bool = True):
    """NRDR port: the BoschAStockBrakeFeel owner toggle is removed, so `stock_brake_feel` defaults to True (always on);
    active_for(CP) still decides."""
    active = active_for(CP)
    self.stock_feel = active and stock_brake_feel is True
    self.stop_ease = active and STOP_EASE_ENABLED
    self.enabled = self.stock_feel or self.stop_ease
    self.newborn_hold = NewbornLeadHold() if active and (RADAR_LEAD_RECOVERY or NEWBORN_HOLD_ENABLED) else None
    # Implausible-drop bound (D-041/D-042; owner bookmark route a2 seg 50, 2026-11-07): same gate as the other active
    # checks in this module (Bosch-A supported, radar available); default ON, no toggle.
    self.drop_bound = ImplausibleDropBound() if active else None
    self.dt = dt
    self.reset()

  def planner_radar_state(self, radar_state, a_ego: float, model_v2=None):
    """The radarState the MPC sees: D-080 bounds a newborn radar lead's aLeadK, then the implausible-drop bound
    (below) clamps a leadOne velocity-glitch brake; otherwise radar_state itself. Chained so both can apply."""
    if self.newborn_hold is not None:
      radar_state = bound_newborn_leads(radar_state, a_ego, self.newborn_hold)
    if self.drop_bound is not None:
      radar_state = bound_implausible_drop(radar_state, model_v2, self.drop_bound)
    return radar_state

  def reset(self):
    self.emergency = False
    self.law_t = 0.0

  def step(self, *, lead_one, lead_two, prev: float, target: float, v_ego: float,
           stopping: bool, standstill: bool, reset_state: bool) -> float:
    """Shape the final acceleration target. `stopping` covers should-stop, force stop and red-light stops."""
    if not self.enabled or reset_state or standstill:
      self.reset()
      return float(target)
    leads = (lead_one, lead_two)
    if stopping or not self.stock_feel:
      self.reset()
    else:
      self.emergency = stock_feel_emergency(leads, v_ego, self.emergency)
      target = stock_feel_target(leads, prev, target, self.dt, v_ego, self.emergency, self.law_t > 0.0)
      self.law_t = STOCK_FEEL_EXIT_HOLD_S if stock_feel_law_active(leads, self.emergency) else max(0.0, self.law_t - self.dt)
    if not self.stop_ease:
      return float(target)
    d_lead = float(lead_one.dRel) if _present(lead_one) else None
    return stop_eased_target(prev, target, stop_ease_floor(v_ego, d_lead), self.dt)


# ---- Newborn lead aLeadK bound (D-080), under NEWBORN_HOLD_ENABLED (or RADAR_LEAD_RECOVERY) ----------------------------
# Ported from openpilot-radar longitudinal_planner.py (567495f4ad), where it is part of the StockBrakeFeel toggle (D-086,
# default off). Replay only, not driven. STATUS 212: on 2e2 (~283 s) a radar lead first seen while its velocity estimate
# was still converging published aLeadK -3 / -2.5 when ~0.75 m/s^2 was needed, and on 2e1 a jumping track reached
# -13.7. For the first NEWBORN_LEAD_FRAMES a radar track has been a lead (or after it drops out for
# NEWBORN_LEAD_GAP_FRAMES or its range jumps NEWBORN_LEAD_JUMP_M), its aLeadK may go no lower than
# -NEWBORN_LEAD_MIN_BRAKE, or lower only as far as a quadratic fit to its own range history says it is slowing.
# MPC input only: dRel, vRel and radarState are untouched and the point is never dropped (D-041/D-042).
# D-100: removing it alone changed nothing on route 313.
NEWBORN_LEAD_FRAMES = 40        # 2.0 s as a lead
NEWBORN_LEAD_GAP_FRAMES = 10    # absent this long (0.5 s): newborn again
NEWBORN_LEAD_JUMP_M = 4.0       # range step from the last sample: newborn again
NEWBORN_LEAD_FIT_FRAMES = 16    # 0.8 s of range history before the fit may lower the floor
NEWBORN_LEAD_MIN_BRAKE = 1.0    # aLeadK floor without range confirmation
NEWBORN_LEAD_DT = 0.05          # s per planner frame (DT_MDL)


def _radar_lead(lead) -> bool:
  return _present(lead) and bool(getattr(lead, "radar", False))


class NewbornLeadHold:
  """Per radar track, (frame, dRel, aEgo) since it became a lead; bounds aLeadK while it is newborn."""
  def __init__(self):
    self.frame = 0
    self.hist: dict[int, list] = {}
    self.bound_frames = 0

  def _range_decel(self, h):
    """Lead accel from a quadratic fit to the range history plus ego accel, or None if too short."""
    if len(h) < NEWBORN_LEAD_FIT_FRAMES:
      return None
    t = np.array([f - h[-1][0] for f, _, _ in h], dtype=float) * NEWBORN_LEAD_DT
    d = np.array([x for _, x, _ in h], dtype=float)
    a_rel = 2.0 * float(np.polyfit(t, d, 2)[0])
    return a_rel + float(np.mean([a for _, _, a in h]))

  def observe(self, lead, a_ego):
    """Record `lead` this frame; its history, or None for a missing or vision-only lead. Call after tick()."""
    if lead is None or not _radar_lead(lead):
      return None
    tid = int(getattr(lead, "radarTrackId", -1))
    d_rel = float(lead.dRel)
    h = self.hist.get(tid)
    if h is None or self.frame - h[-1][0] > NEWBORN_LEAD_GAP_FRAMES or abs(d_rel - h[-1][1]) > NEWBORN_LEAD_JUMP_M:
      h = self.hist[tid] = [(self.frame, d_rel, float(a_ego))]
    elif h[-1][0] != self.frame:  # leadOne and leadTwo on one track: record it once
      h.append((self.frame, d_rel, float(a_ego)))
    return h

  def bound(self, lead, a_ego):
    """aLeadK for `lead`, or None when it is left as is. Call once per lead per frame, after tick()."""
    h = self.observe(lead, a_ego)
    if h is None or self.frame - h[0][0] >= NEWBORN_LEAD_FRAMES:
      return None
    a_lead = float(lead.aLeadK)
    a_range = self._range_decel(h)
    a_floor = -NEWBORN_LEAD_MIN_BRAKE if a_range is None else min(-NEWBORN_LEAD_MIN_BRAKE, a_range)
    if a_lead >= a_floor:
      return None
    self.bound_frames += 1
    return a_floor

  def tick(self):
    self.frame += 1
    if len(self.hist) > 64:
      self.hist = {k: h for k, h in self.hist.items() if self.frame - h[-1][0] <= NEWBORN_LEAD_GAP_FRAMES}


class _BoundedLead:
  """A lead that reads as `lead` except for aLeadK."""
  def __init__(self, lead, a_lead: float):
    self._lead = lead
    self.aLeadK = float(a_lead)

  def __getattr__(self, name):
    return getattr(self._lead, name)


class _BoundedRadarState:
  def __init__(self, radar_state, lead_one, lead_two):
    self._radar_state = radar_state
    self.leadOne = lead_one
    self.leadTwo = lead_two

  def __getattr__(self, name):
    return getattr(self._radar_state, name)


def bound_newborn_leads(radar_state, a_ego: float, hold: NewbornLeadHold):
  hold.tick()
  leads = []
  changed = False
  for lead in (radar_state.leadOne, radar_state.leadTwo):
    a_lead = hold.bound(lead, a_ego)
    leads.append(lead if a_lead is None else _BoundedLead(lead, a_lead))
    changed |= a_lead is not None
  return _BoundedRadarState(radar_state, leads[0], leads[1]) if changed else radar_state


# ---- Implausible radar-drop bound on leadOne (owner bookmark, route 000000a2--794ebefbf7 seg 50, 2026-11-07) --------
# Right after a left lane change, leadOne was radar track 24 at 18 m, matched to the camera lead (leadsV3[0] x~19-20 m,
# prob 1.0). Over 0.7 s track 24's vLead collapsed 12.5 -> 2.9 m/s (vRel +1.1 -> -6.9, an implied -13 m/s^2, physically
# impossible), aLeadK pinned at -3.0. The camera lead's v stayed 10.5-11.9 m/s and x 19-20 m the whole time. The planner
# braked at -3.5 and the car went 10.3 -> 4.2 m/s; the track then died and the next track (62) showed the car pulling
# away at 22 m. A radar velocity glitch, not a real lead. D-041/D-042: the point is never dropped or altered in
# radarState; this only bounds what leadOne publishes to the planner (MPC + this module's stock-feel law), the same
# pattern as the D-080 newborn bound above. Replay only (16-drive census + 12-episode gate rerun, 2026-11-07); no road
# evidence yet for this specific bound.
# Residual risk: a real lead braking harder than DROP_MPS/DROP_WINDOW_S (>10 m/s^2 - itself a crash-decel lead) while
# the camera model lags behind gets up to MAX_S = 1.0 s of the camera's (slower-braking) speed instead of the radar's.
DROP_WINDOW_S = 0.5          # s; a2 seg 50: the glitch collapsed vLead inside this window
DROP_MPS = 5.0               # m/s over DROP_WINDOW_S; 5.0 / 0.5 s = 10 m/s^2, beyond a real car's braking
MODEL_DROP_MAX_MPS = 1.5     # m/s the camera lead's v may drop in the window and still call the radar drop a glitch
# Range-split census, 2026-11-07, replay. Model x change over the 0.5 s before the trigger, in m: a2 seg 50 phantom
# +0.50; 84 s15 radar-noise legs +2.44 and -3.81; real slowdowns 7b s27 -5.84, 99 s1 -5.05, 7b s23 -5.81, 78 s3 -5.19,
# 7b s8 -3.69, 80 s6 -8.81, 80 s19 -1.06; adjacent-lane truck 8a s2 -2.92; 8a s11 (disengaged, lead steady) -0.09.
# 0.3 m sits between a2 (+0.50) and the closest real slowdown, 80 s19 (-1.06). A magnitude gate on radar-vs-camera
# range split was tried first and rejected: 7b s23 split -8.3 m is deeper than a2's -3.4 m. Not firing falls back to
# the old behavior (the radar drop is published unbounded), so the gate only narrows the bound.
MODEL_RANGE_SHRINK_MAX_M = 0.3  # m the camera lead's x may shrink over DROP_WINDOW_S and still call the radar drop a glitch
AGREE_M = 4.0                # m; radar dRel vs (model x - RADAR_TO_CAMERA) agreement needed at the window start
MODEL_PROB_MIN = 0.9         # camera lead confidence needed to trust it over the radar
TRIGGER_V_EGO_MIN = 5.0      # m/s; below this the radar's own near-field behavior is not glitch-like, stay off
END_CONVERGE_MPS = 2.0       # m/s; |radar vLead - model v| under this: radar has caught back up, end the bound
END_MODEL_DROP_MPS = 3.0     # m/s the camera lead's v may fall since the trigger before releasing immediately
MAX_S = 1.0                  # s; hard cap on how long the bound can run
RETRIGGER_COOLDOWN_S = 2.0   # s a track id is blocked from re-triggering after the bound ends on it
MODEL_V_MARGIN_MPS = 1.0     # m/s below the model's v that the bounded vLead may not go
IMPLAUSIBLE_DROP_DT = NEWBORN_LEAD_DT  # s per planner frame (DT_MDL), same assumption as the newborn bound above


# Lazy import, same reasoning as active_for's: this module is imported before radard's car gates are known to apply.
def _radar_to_camera() -> float:
  from openpilot.selfdrive.controls.radard import RADAR_TO_CAMERA
  return RADAR_TO_CAMERA


def _model_lead0(model_v2):
  """(prob, x[0], v[0], a[0]) of the first model lead, or None when modelV2/leadsV3[0] is unusable."""
  if model_v2 is None:
    return None
  try:
    leads = model_v2.leadsV3
    if len(leads) < 1:
      return None
    lead0 = leads[0]
    return float(lead0.prob), float(lead0.x[0]), float(lead0.v[0]), float(lead0.a[0])
  except (AttributeError, IndexError, TypeError, ValueError):
    return None


def _drop_radar_lead(lead) -> bool:
  return _present(lead) and bool(getattr(lead, 'radar', False)) and int(getattr(lead, 'radarTrackId', -1)) >= 0


class ImplausibleDropBound:
  """Per-leadOne state for the implausible-drop bound (see the constants above). `bound_implausible_drop` drives it
  once per planner frame."""

  def __init__(self):
    self.frame = 0
    self.track_id: int | None = None
    self.hist: list[tuple[int, float, float, tuple | None]] = []  # (frame, vLead, dRel, model) trimmed to the
    # trailing DROP_WINDOW_S of the current track; model is (prob, x, v, a) or None
    self.active = False
    self.trigger_frame = 0
    self.trigger_model_v = 0.0
    self.cooldown_until: dict[int, int] = {}

  def tick(self):
    self.frame += 1

  def _end(self, track_id: int):
    self.active = False
    self.cooldown_until[track_id] = self.frame + round(RETRIGGER_COOLDOWN_S / IMPLAUSIBLE_DROP_DT)

  def _reset_track(self, track_id: int | None):
    if self.active and self.track_id is not None:
      self._end(self.track_id)
    self.track_id = track_id
    self.hist = []

  def update(self, lead, model_v2):
    """`lead` is radarState.leadOne this frame. Returns (vLead, vRel, aLeadK) to publish, or None to leave it as is."""
    if not _drop_radar_lead(lead):
      self._reset_track(None)
      return None
    track_id = int(lead.radarTrackId)
    if track_id != self.track_id:
      self._reset_track(track_id)
    model = _model_lead0(model_v2)
    v_lead = float(lead.vLead)
    d_rel = float(lead.dRel)
    v_ego = v_lead - float(lead.vRel)
    self.hist.append((self.frame, v_lead, d_rel, model))
    while self.hist and (self.frame - self.hist[0][0]) * IMPLAUSIBLE_DROP_DT > DROP_WINDOW_S:
      self.hist.pop(0)

    if self.active:
      if model is None or abs(v_lead - model[2]) < END_CONVERGE_MPS or \
         (self.trigger_model_v - model[2]) > END_MODEL_DROP_MPS or \
         (self.frame - self.trigger_frame) * IMPLAUSIBLE_DROP_DT >= MAX_S:
        self._end(track_id)
        return None
      return self._bounded(lead, model, v_ego)

    if model is None or model[0] <= MODEL_PROB_MIN or v_ego <= TRIGGER_V_EGO_MIN or len(self.hist) < 2 or \
       self.cooldown_until.get(track_id, -1) > self.frame:
      return None
    start_frame, start_v_lead, start_d_rel, start_model = self.hist[0]
    if start_model is None:
      return None
    max_v_lead = max(h[1] for h in self.hist)
    if not max_v_lead - v_lead > DROP_MPS:
      return None
    if not start_model[2] - model[2] < MODEL_DROP_MAX_MPS:
      return None
    if not model[1] - start_model[1] > -MODEL_RANGE_SHRINK_MAX_M:
      return None
    if not abs(start_d_rel - (start_model[1] - _radar_to_camera())) < AGREE_M:
      return None
    self.active = True
    self.trigger_frame = self.frame
    self.trigger_model_v = model[2]
    return self._bounded(lead, model, v_ego)

  @staticmethod
  def _bounded(lead, model: tuple, v_ego: float):
    """vLead/vRel/aLeadK bounded only toward a faster, less-braking lead; dRel is untouched (D-041/D-042)."""
    model_v, model_a = model[2], model[3]
    v_lead_b = max(float(lead.vLead), model_v - MODEL_V_MARGIN_MPS)
    v_rel_b = v_lead_b - v_ego
    a_lead_k_b = max(float(lead.aLeadK), min(model_a, 0.0))
    return v_lead_b, v_rel_b, a_lead_k_b


class _FieldBoundedLead:
  """A lead that reads as `lead` except for the given field overrides."""
  def __init__(self, lead, **fields):
    self._lead = lead
    for name, value in fields.items():
      setattr(self, name, value)
    self._fields = fields

  def __getattr__(self, name):
    return getattr(self._lead, name)


def bound_implausible_drop(radar_state, model_v2, state: ImplausibleDropBound):
  state.tick()
  result = state.update(radar_state.leadOne, model_v2)
  if result is None:
    return radar_state
  v_lead_b, v_rel_b, a_lead_k_b = result
  fields = {'vLead': v_lead_b, 'vLeadK': v_lead_b, 'vRel': v_rel_b, 'aLeadK': a_lead_k_b}
  lead = radar_state.leadOne
  if hasattr(lead, 'aLead'):
    fields['aLead'] = a_lead_k_b
  bounded = _FieldBoundedLead(lead, **fields)
  return _BoundedRadarState(radar_state, bounded, radar_state.leadTwo)


# ---- Birth-rail ramps (D-077), OFF and not wired --------------------------------------------------------------------
# Ported from openpilot-radar radard.py (567495f4ad, constants and `_update_birth_rail`), where both ramps are baked on.
# Owner 2026-10-20: keep it here but off while James's fork is tested as he ships it. BIRTH_RAIL_ENABLED is False, and
# no radard code calls BirthRail yet, so this changes nothing on this branch. Wiring it needs the track's first-update
# time and the published-vRel hook in radard, and it must be re-checked against SP7's own newborn handling
# (bosch_a_radar._bosch_a_newborn_vrel) first, because both act on a track's first seconds.
# Source evidence (tools/bosch_a_birth_rail_report.py, 8 routes): born-railed moving leads overstated 128/130,
# excess 1/e ~1.2 s; born-railed stopped objects (ego < 12) genuine 61/81. Replay of the revised LOW (STATUS 207): one
# firing in ~116 engaged min (268 5:56 cut-in, -1.58 vs -1.84); stopped-object stops 2d9 8:58, 26b 29:58, 236 34:57
# unchanged. HIGH publishes less opening than the rail (more-closing direction, D-042). LOW publishes less closing than
# the rail, which narrows D-041, so it only runs with a confident model lead agreeing at the track's range and offset.
BIRTH_RAIL_ENABLED = False
BIRTH_RAIL_RAMP_HIGH = True
BIRTH_RAIL_RAMP_LOW = True
BIRTH_RAIL_WINDOW_S = 0.5
BIRTH_RAIL_RAMP_TAU_S = 1.2
BIRTH_RAIL_RAMP_MAX_AGE_S = 2.5
BIRTH_RAIL_LOW_MIN_V_EGO_MPS = 12.0
BIRTH_RAIL_LOW_MIN_LEAD_MPS = 5.0
BIRTH_RAIL_LOW_VISION_MIN_PROB = 0.5
BIRTH_RAIL_LOW_VISION_D_TOL_M = 5.0
BIRTH_RAIL_LOW_VISION_D_TOL_FRAC = 0.15
BIRTH_RAIL_LOW_VISION_Y_TOL_M = 2.0
# 2d5 9:44: without the margin the LOW ramp published less closing than the truth for 2.4 s.
BIRTH_RAIL_LOW_VISION_MARGIN_MPS = 4.0


def _u11_rails() -> tuple[float, float, float]:
  from opendbc.car.honda.bosch_a_radar import (BOSCH_A_DIRECT_VREL_CENTER_RAW, BOSCH_A_DIRECT_VREL_MAX_RAW,
                                               BOSCH_A_DIRECT_VREL_MIN_RAW, BOSCH_A_DIRECT_VREL_SCALE_MPS)
  low = (BOSCH_A_DIRECT_VREL_MIN_RAW - BOSCH_A_DIRECT_VREL_CENTER_RAW) * BOSCH_A_DIRECT_VREL_SCALE_MPS
  high = (BOSCH_A_DIRECT_VREL_MAX_RAW - BOSCH_A_DIRECT_VREL_CENTER_RAW) * BOSCH_A_DIRECT_VREL_SCALE_MPS
  return low, high, BOSCH_A_DIRECT_VREL_SCALE_MPS


def birth_rail_vision_agrees(d_rel: float, y_rel: float, vision_lead) -> bool:
  """LOW moving test: a confident model lead (dRel, yRel, vLead, prob) at the track's range and offset, moving."""
  if vision_lead is None:
    return False
  vd, vy, vv, prob = vision_lead
  if not (np.isfinite(vd) and np.isfinite(vy) and np.isfinite(vv)) or prob < BIRTH_RAIL_LOW_VISION_MIN_PROB:
    return False
  if abs(vd - d_rel) > max(BIRTH_RAIL_LOW_VISION_D_TOL_M, BIRTH_RAIL_LOW_VISION_D_TOL_FRAC * d_rel):
    return False
  return abs(vy - y_rel) <= BIRTH_RAIL_LOW_VISION_Y_TOL_M and vv >= BIRTH_RAIL_LOW_MIN_LEAD_MPS


def birth_rail_ramp_fraction(age: float) -> float:
  """Share of the rail published at track age `age`: 0 at birth, 1 at BIRTH_RAIL_RAMP_MAX_AGE_S."""
  if age >= BIRTH_RAIL_RAMP_MAX_AGE_S:
    return 1.0
  full = 1.0 - np.exp(-BIRTH_RAIL_RAMP_MAX_AGE_S / BIRTH_RAIL_RAMP_TAU_S)
  return max(0.0, float((1.0 - np.exp(-max(age, 0.0) / BIRTH_RAIL_RAMP_TAU_S)) / full))


class BirthRail:
  """Per-track D-077 state. `update()` returns the vRel to publish while a ramp is active, else None (publish as is).
  `withhold_rail_fast` is True while the LOW ramp runs (the source zeroes its RAIL_FAST correction then)."""

  def __init__(self, t_first: float, enabled: bool = BIRTH_RAIL_ENABLED):
    self.t_first = float(t_first)
    self.enabled = enabled
    self.rail = 0  # -1 born on the low rail, +1 on the high rail, 0 not (yet)
    self.done = not enabled
    self.withhold_rail_fast = False

  def update(self, t_now: float, v_rel: float, v_lead: float, d_rel: float, y_rel: float,
             range_assist_correction: float = 0.0, vision_lead=None) -> float | None:
    self.withhold_rail_fast = False
    if self.done or not (BIRTH_RAIL_RAMP_HIGH or BIRTH_RAIL_RAMP_LOW):
      return None
    low_rail, high_rail, scale = _u11_rails()
    age = float(t_now) - self.t_first
    on_low = v_rel <= low_rail + scale / 2
    on_high = v_rel >= high_rail - scale / 2
    if self.rail == 0:
      if age > BIRTH_RAIL_WINDOW_S:
        self.done = True
        return None
      self.rail = -1 if on_low else (1 if on_high else 0)
      if self.rail == 0:
        return None
    if age >= BIRTH_RAIL_RAMP_MAX_AGE_S or not (on_low if self.rail < 0 else on_high):
      self.done = True
      return None
    frac = birth_rail_ramp_fraction(age)
    if self.rail > 0:
      if not BIRTH_RAIL_RAMP_HIGH:
        self.done = True
        return None
      return min(float(v_rel) - float(range_assist_correction), high_rail * frac)
    v_ego_aligned = v_lead - v_rel
    if not BIRTH_RAIL_RAMP_LOW or v_ego_aligned < BIRTH_RAIL_LOW_MIN_V_EGO_MPS or vision_lead is None or \
       not birth_rail_vision_agrees(d_rel, y_rel, vision_lead):
      self.done = True
      return None
    vision_vrel = float(vision_lead[2]) - v_ego_aligned
    if vision_vrel < low_rail + BIRTH_RAIL_LOW_VISION_MARGIN_MPS:
      self.done = True
      return None
    self.withhold_rail_fast = True
    return max(low_rail, min(low_rail * frac, vision_vrel))
