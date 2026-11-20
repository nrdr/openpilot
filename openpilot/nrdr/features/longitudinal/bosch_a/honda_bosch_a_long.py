"""Honda Bosch A Long Enhancement: longitudinal behavior that is active whenever the Bosch-A radar is on.

Ported from openpilot-radar (ns-bosch-radar-testing @ 567495f4ad + 6db22115e8, selfdrive/controls/lib/longitudinal_planner.py).
Active only when `active_for(CP)`: a Honda in VERIFIED_BOSCH_A_CARS with openpilot longitudinal and the radar not
disabled (`HondaBoschARadar`), which is the same gate radard uses to build BoschALeadPolicy. Each part also has its own
switch: Stock Brake Feel is permanent (owner 2026-11-11: "Make Stock Brake Feel permanent"; the BoschAStockBrakeFeel
toggle and its settings row are removed). HumanFollowing and HumanAcceleration are always on too (owner 2026-11-13: no
toggle, default for all Bosch-A cars; the HumanFollowing owner toggle is removed). Everything in this class needs the radar on
(owner 2026-11-13; bosch_a_toggles.long_tuning_active); HumanFollowing and HumanAcceleration still run vision-only. Both longitudinal planners
(StarPilot's and the upstream one) call it the
same way. The D-077 birth-rail ramps (off, never wired to radard here) were removed 2026-11-11; the code and its
evidence comment are in git at 3f26fb513c and in openpilot-radar radard.py @ 567495f4ad.

Contents:
- Stock Brake Feel (D-086, D-100, D-103, D-120): stock Honda ACC's TTC depth and jerk tables, with the soft exit,
  takeover hold, lead-stop law (<= 20 s) and the emergency latch.
  Split 2026-11-15 (option 2): the depth half (stock_feel_cap: depth table, lead-stop need, held-cap let-off) runs in
  lead() on the lead candidate; the build-rate half (stock_feel_jerk) runs in step() on the final target, every brake.
- Brake onset ramp (2026-11-05, step() since 2026-11-11): a brake that starts with every lead far away deepens at
  most ONSET_JERK per second; it only binds inside the emergency pass-through, where the law's rate stands down.
- Coast first (depth floor; folded in from bosch_a_coast_first.py 2026-11-11): for a distant lead tapping its brakes, the
  final target is floored at COAST_ACCEL and the floor descends at COAST_RAMP_JERK. It runs in step() after the onset
  ramp when the caller passes `follow_s`, so model (e2e) and cruise braking get the gentle start too.
- Need floor (2026-11-11, NEED_FLOOR_ENABLED, on; replay only): need_floor() raises a braking target to -max(need, 0.8)
  for a steady closing moving lead; the last stage of lead(), longitudinal_planner.py only.

- Newborn lead aLeadK bound (D-080, restored 2026-11-11 as NEWBORN_HOLD_ENABLED, on): planner_radar_state() holds a
  newborn radar lead's aLeadK at -1.0 unless its own range history confirms the braking (MPC and law input only).

Placement (d2 t1297.6 red-light let-off, 2026-11-15): the planner calls `lead()` once per cycle on the lead MPC candidate
only, before min(candidates): the law's depth cap and the need floor. A depth cap on the final target let a calm far camera
lead lift e2e's red-light brake (-2.6 -> -0.6); e2e and cruise braking are never capped or let off by it. `step()` shapes
the final target, after the other target owners and before release coast, smooth and stop gap: the law's build rate (or
the onset ramp in an emergency) on every brake, then
coast first (it only stages a new brake from COAST_ACCEL, so it cannot let off one that is built). Every limit here
only shapes how a brake builds or lets off; the emergency latch passes the target through untouched, so the car never
brakes harder than the planner would without this module. Replay and limited road evidence only.

HumanFollowing and HumanAcceleration are separate modules (human_following.py, human_acceleration.py) because they
also run with the radar off (vision-only).
"""
import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_camera_witness import closing_ttc
from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_release as release
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_release import let_off_limited_target
from openpilot.nrdr.features.longitudinal.bosch_a.gate import long_tuning_active, vehicle_supported

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
# Soft exit (D-125: STOCK_FEEL_EXIT_JERK, STOCK_FEEL_EXIT_HOLD_S) and takeover hold (STOCK_FEEL_CAP_RELEASE_JERK) live
# in the let-off rate table in bosch_a_release.py, with their evidence. Read through the module so a replay harness can
# patch them there.
# Lead stopping (owner 2026-10-07, 2f2 1099/1483): a closing lead braking at STOCK_FEEL_LEAD_STOP_A or harder moves the
# cap to the decel needed to stop STOCK_FEEL_LEAD_STOP_GAP behind it. D-120 (324): leads more than
# STOCK_FEEL_LEAD_STOP_MAX_T s from stopping are left to the table (12 s delayed a real slowing lead on 324 2790).
STOCK_FEEL_LEAD_STOP_A = -1.0  # m/s^2
STOCK_FEEL_LEAD_STOP_GAP = 4.0  # m
STOCK_FEEL_LEAD_STOP_MAX_T = 20.0  # s
# Emergency bypass (owner 2026-10-07, 2f5 ~10:01: a lead braking -6.5 was met at stock's depth and the driver had to
# brake). Latched while any lead is closing: the planner's target passes through with no cap and no jerk limit.
STOCK_FEEL_EMERGENCY_A_LEAD = -2.0  # m/s^2
STOCK_FEEL_EMERGENCY_NEED = 2.0  # m/s^2
# The aLeadK path only latches when the worst TTC is at most this (openpilot-radar STATUS 258, 6db22115e8): 3a3
# 17:28.35 aLeadK -2.09 at TTC 21.7 s latched and stayed on through a separate build 15 s later that ran to -3.03.
STOCK_FEEL_EMERGENCY_A_LEAD_MAX_TTC = 10.0  # s


# ---- Switch: newborn lead aLeadK bound (D-080) -------------------------------------------------------------------------
# NEWBORN_HOLD_ENABLED turns on the D-080 newborn-lead aLeadK bound (NewbornLeadHold, planner_radar_state()). It was
# RADAR_LEAD_RECOVERY = False, a group switch for D-089 (far-range recovery), D-075 (newborn range publish) and D-080;
# only D-080 was ever ported. D-089 and D-075 live in the decoder (bosch_a_radar.BOSCH_A_REANCHOR_RECOVER_SIGMA_FRAC = 0,
# BOSCH_A_NEWBORN_RANGE_PUBLISH) and need radard gates (RECOVERED_CAM_GATE, NEWBORN_*) plus RadarPoint fields
# (`measured`, `recovered`) that 7.0 does not have, so this switch does NOT turn them on (D-089/D-075 are not ported
# here, so the group name RADAR_LEAD_RECOVERY no longer fits). Turning those decoder constants on without the gates is
# the rejected configuration (STATUS 225; D-075 phantom brakes on 280/294/2ae/284).
# Turned on 2026-11-11 for scoring on bob-unify-bd: route 000000bd seg 10 ~621.8 s (Jason/Job, open-loop replay at
# a1ac1afdba, single route): new radar track born at 61 m with aLeadK -2.39 (decayed to -0.29 within 1.1 s) tripped the
# emergency latch for 79 frames; with the hold the peak went -2.44 -> -2.23, worst decel jerk -9.3 -> -7.2, latch 0
# frames, onset 0.2 s later. Risk to score: the hold delays braking for a genuinely hard-braking newborn lead by up to 40
# frames unless the range fit confirms it. Replay only; not driven.
# Scored 2026-11-11 (Job, replay only, vs replay_unify4, 36 routes + second set): 52 episodes move, 0 harder, no REAL or
# PHANTOM label moves; route bd seg 10 -2.37 -> -2.23, step jerk -8.0 -> -1.4, latch rows 44 -> 0; seg 5 hard stop
# identical. Owner 2026-11-11: "Port the hold alone to my branch" (car branch bd-newborn-hold fd05f917d8).
# Read when HondaBoschALongEnhancement is constructed, so a replay harness can set the constant before building the planner.
NEWBORN_HOLD_ENABLED = True


def active_for(CP) -> bool:
  """Same gate as radard's BoschALeadPolicy: verified Bosch-A Honda, radar on, openpilot longitudinal
  (bosch_a_toggles.long_tuning_active, the one gate for every Bosch-A longitudinal part)."""
  return long_tuning_active(CP)


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
    ttc_min = min(ttc_min, closing_ttc(float(lead.dRel), closing, min_closing))
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
  if ttc == float('inf'):
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
  """The cap, except that a brake already deeper than it (prev) is only let off at STOCK_FEEL_CAP_RELEASE_JERK.
  Caps are always braking (cap < 0), so this is let_off_limited_target at that rate."""
  return let_off_limited_target(prev, cap, dt, release.STOCK_FEEL_CAP_RELEASE_JERK)


def stock_feel_law_active(leads, emergency: bool) -> bool:
  """True while the fitted law applies (a lead closing, TTC over the floor, no emergency)."""
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


def stock_feel_cap(leads, prev: float, target: float, dt: float, v_ego: float = 0.0) -> float:
  """The law's depth half: no deeper than the depth table (or the lead-stop need), a brake already deeper than that let
  off at the held-cap rate. Applied to the lead MPC candidate only (lead()), never to e2e or cruise braking."""
  ttc = brake_onset_ttc(leads, STOCK_FEEL_MIN_CLOSING)
  if not ttc > STOCK_FEEL_TTC_FLOOR_S or ttc == float('inf'):
    return float(target)
  depth = stock_feel_depth(leads, ttc, v_ego)
  need = lead_stop_need(leads, v_ego, STOCK_FEEL_LEAD_STOP_MAX_T)
  cap = -min(need, 3.5) if need > -depth else depth
  return float(max(target, stock_feel_held_cap(prev, cap, dt)))


def stock_feel_jerk(leads, v_ego: float = 0.0, law_recent: bool = False) -> float:
  """The law's build-rate half (m/s^3): how fast a brake may deepen, from the jerk table while a lead closes over the
  TTC floor, else STOCK_FEEL_JERK_OUTSIDE (or EXIT_JERK just after the law). Applied to the final target (step())."""
  ttc = brake_onset_ttc(leads, STOCK_FEEL_MIN_CLOSING)
  if ttc == float('inf') and law_recent and not any(
      _present(lead) and float(lead.aLeadK) <= STOCK_FEEL_LEAD_STOP_A for lead in leads):
    return release.STOCK_FEEL_EXIT_JERK
  if not ttc > STOCK_FEEL_TTC_FLOOR_S or ttc == float('inf'):
    return STOCK_FEEL_JERK_OUTSIDE
  if lead_stop_need(leads, v_ego, STOCK_FEEL_LEAD_STOP_MAX_T) > -stock_feel_depth(leads, ttc, v_ego):
    return STOCK_FEEL_JERK_OUTSIDE
  return float(np.interp(ttc, STOCK_FEEL_JERK_BP, STOCK_FEEL_JERK_V))


def stock_feel_target(leads, prev: float, target: float, dt: float, v_ego: float = 0.0,
                      emergency: bool = False, law_recent: bool = False) -> float:
  """D-086 stock Honda ACC brake law (see the constants above): the depth cap, then the build rate, both from prev.
  The planner splits them (2026-11-15, option 2): cap in lead(), rate in step()."""
  if emergency:
    return float(target)
  return brake_onset_limited_target(prev, stock_feel_cap(leads, prev, target, dt, v_ego), dt,
                                    stock_feel_jerk(leads, v_ego, law_recent))


# ---- Brake onset ramp --------------------------------------------------------------------------------------------
# Brake onset ramp: a brake that starts with every lead far away builds at ONSET_JERK instead of in one frame.
#
# Owner 2026-11-05: "Why can we just mimic stock brake for those situations? Instead of just slamming the brake".
# Stock ACC on route 299 (STATUS 214) brings a brake in at -1.4..-3.4 m/s^3 per step; ours stepped at -36..-52 m/s^3
# on the route 84 far brakes (E1, E4), e2ae and e2f8. The old D-083 ramp (6f1a05b37) would not have changed them: its
# lead-braking and need gates stand it down on every one, because the lead is already braking hard at onset.
#
# Replay (Job, base dad6bbbb6, open loop, arm R4b; limited road evidence, not driven):
#   - first-jolt jerk 44-52 -> 8 m/s^3 on 84 E1/E4/vn84_3/vn84_11, 34 -> 8 on e2ae, 43 -> 8 on e2f8; peak decel unchanged
#     (-3.5 stays -3.5), onset at -2 at most 0.15 s later.
#   - min gap 0.4-0.9 m smaller on those events (e2ae: -0.62 m, ending at 4.8 m); min TTC within 0.08 s.
#   - the 2f5 close stop (onset dRel 38.1 m) is exempt and equals today's output; pooled 0.85 h: same brake episode
#     counts, no episode closer by more than 2 m.
#   - nothing at onset (need, closing speed) separates e2ae/2f5 from the 84 far brakes; only the onset distance does.
#     EXEMPT_D_M = 40 sits between 2f5 (38.1 m) and e2f8 (43.9 m); 30 m capped 2f5 and cost it 0.36 m.
#   - an in-brake close-gap stand-down (R5) changed nothing: the ramp finishes in ~0.4 s, before the gap gets close.
#
# Channels: reads radarState leadOne/leadTwo (present, dRel, vRel) as published; a railed vRel (U11 low rail -12) only
# makes TTC smaller, which stands the ramp down, never extends it. Only the fall rate of the target is capped; the peak is
# never reduced, rises pass through, and dRel/vLead/radar points are untouched (D-041/D-042).
#
# With the law always on (owner 2026-11-11), the ramp only binds inside the emergency pass-through, where the law
# hands the planner's target through untouched; on the scorecard baseline (44f382face, 36 routes) that was 10 frames in
# 7 episodes (replay). The episode-end rule below (the law's output and last cycle's published target both back at
# or above END_ACCEL) replaces the old ramp's own post-smooth input test: static; not replayed yet.
ONSET_JERK = 8.0         # m/s^3, the fastest a non-exempt brake may deepen
ONSET_START_ACCEL = -0.3       # m/s^2: the law's output below this starts a brake episode
ONSET_END_ACCEL = -0.1         # m/s^2: the output and last cycle's target both back at or above this end it
ONSET_EXEMPT_D_M = 40.0        # any lead closer than this as the episode starts: no ramp for the whole episode
ONSET_TTC_STAND_DOWN_S = 2.0   # any lead at or below this TTC: no ramp for the rest of the episode


def lead_close(leads) -> bool:
  return any(float(lead.dRel) < ONSET_EXEMPT_D_M for lead in leads if _present(lead))


def lead_ttc_low(leads) -> bool:
  for lead in leads:
    if not _present(lead):
      continue
    closing = -float(lead.vRel)
    if closing_ttc(float(lead.dRel), closing, 1e-3) <= ONSET_TTC_STAND_DOWN_S:
      return True
  return False


# ---- Coast first (depth floor) ------------------------------------------------------------------------------------
# Bosch-A coast first: for a distant lead tapping its brakes, lift off the gas before braking.
#
# Owner 2026-11-01, route 71 (00000071--37216af48f) 12:03: at 70 mph a pickup 51-66 m ahead (1.6-2.0 s) braked for
# about 2 s (aLeadK to -3.0, vLead 32.5 -> 25.4) and was back on the gas 1.5 s later. The planner went 0 -> -2.25 in
# 0.75 s. The closest gap was 50.9 m / 1.64 s. A coast at -0.5 from the same onset reaches about 49.5 m / 1.65 s
# (open-loop kinematics on the logged lead, Long Sim), so the brake bought about 1.4 m. "I wouldn't mind if the car lets
# go off the gas instead, then ramping up brake if needed" (owner 2026-10-20, 3a3 17:44).
#
# While the gap is well clear, the brake is staged instead of cut: the target is floored at COAST_ACCEL when braking
# starts and the floor descends at COAST_RAMP_JERK, so a lead that keeps braking still gets the full brake 1-2 s later.
# Every tick re-checks a projection: the lead keeps its current decel (aLeadK, no recovery assumed) and we follow the
# staged floor for COAST_HORIZON_S; if the projected gap ever drops under COAST_FLOOR_GAP_S * v + COAST_FLOOR_GAP_M, or
# the time gap is under follow + COAST_GAP_MARGIN_S, or TTC, lead decel or FCW trip, the floor is dropped at once and the
# planner's target passes untouched until it stops braking. It only raises a braking target (never adds gas above
# COAST_ACCEL, never touches the radar points: D-041/D-042). Static and open-loop replay evidence only.
#
# Owner 2026-11-05, route 0000008f bookmark 1 (4445.2): a car 37-40 m ahead (2.7 s, TTC 14.5 s) tapped its brakes at
# about -3 for 1 s at 32 mph and we braked to -1.8. Coast first stood down on speed (14.1 < 15) and on the projection,
# which held the lead's -3 for the full 3 s. "The car was still a distance away". So COAST_MIN_V_EGO is 13.5 and the
# projection holds the lead's decel for COAST_LEAD_DECEL_HOLD_S, then holds the lead's speed. Replay (Long Sim, V-ASM
# 3b3d20056 with Stock Brake Feel and Human Following on, open loop on the logged lead): bookmark 1 coasts 1.75 s, peak
# -1.81 -> -1.58, min gap unchanged (26.9 m); bookmark 2 (1.43 s gap) unchanged; 2f5 one frame later, e2ae and route 84
# E1/E4 identical, 19 route-84 far brakes keep min gap and TTC; route 71 12:03 identical. Pooled 2.16 h: 14 new coasts
# (37.1 -> 43.5/h), none lost, counts below -1 and -2 identical, max target change 0.18 m/s^2, closest new coast 2.29 s
# gap / 9.9 s TTC. Replay only, not driven.
COAST_MIN_V_EGO = 13.5       # m/s (~30 mph); distant taps at road speed (was 15; 8f B1 at 14.1). The stop gap owns the stop.
COAST_ACCEL = -0.5           # m/s^2; lift-off plus a little (Civic gas-off at 70 mph ~ -0.4)
COAST_RAMP_JERK = 1.0        # m/s^3; staged floor: -0.5 -> -2.5 in 2 s
COAST_GAP_MARGIN_S = 0.35    # time gap must be at least follow + this (aggressive 1.25 -> 1.6; 71 12:03 bottomed at 1.64)
COAST_HORIZON_S = 3.0
COAST_LEAD_DECEL_HOLD_S = 1.5  # s; the projected lead brakes this long, then holds its speed (was the whole horizon)
COAST_FLOOR_GAP_S = 0.8      # projected gap floor: 0.8 s * v + 6 m (long_mpc STOP_DISTANCE)
COAST_FLOOR_GAP_M = 6.0
COAST_MIN_TTC_S = 5.0        # 71 12:03 at the low point: 51 m / 5.8 m/s = 8.8 s
COAST_MAX_LEAD_DECEL = -4.0  # m/s^2; harder than this is not a tap


def projected_gap_ok(d_rel: float, v_lead: float, a_lead: float, v_ego: float, floor_a: float) -> bool:
  a_lead = min(a_lead, 0.0)
  d, vl, ve, fa = d_rel, v_lead, v_ego, floor_a
  t = 0.0
  while t < COAST_HORIZON_S:
    d += (vl - ve) * DT_MDL
    if t < COAST_LEAD_DECEL_HOLD_S:
      vl = max(0.0, vl + a_lead * DT_MDL)
    ve = max(0.0, ve + fa * DT_MDL)
    fa -= COAST_RAMP_JERK * DT_MDL
    if d < COAST_FLOOR_GAP_S * ve + COAST_FLOOR_GAP_M:
      return False
    t += DT_MDL
  return True


# ---- Need floor ("arm 13" / arm D; Bosch-A, replay only) ---------------------------------------------------------------
# Owner 2026-11-11, route 11c8fa231c0499ed/000000bd--3279f521f1 seg 10 (10:20): a radar lead born at 61 m closing at 10.5
# m/s never stopped (vLead 8.5-9 m/s, then 13), min gap 41 m; -2.23 with the newborn hold 'still feels too hard', owner
# wants a -1.3 to -1.5 peak. Cause: the MPC asks -2.3..-2.4 to restore time-gap headway, and the Stock Brake Feel depth
# table is TTC-only (TTC 4.7-5.9 s allows -2.1..-2.25). Replay (Job, open loop at a1ac1afdba + anchored kinematic closed
# loop, 0.3 s lag, MPC not reacting; one route, three events), against the newborn hold alone: seg 10 peak -2.23 -> -1.52,
# worst decel jerk -7.2 -> -3.7, closed-loop min gap 38.3 -> 30.7 m, min TTC 4.72 -> 4.63 s; seg 5 (5:34) and seg 18
# (18:30), both stopped leads: 0 frames differ, the gate never opened (highest vLead while closing 3.9 m/s). Earlier
# variants without the vLead/aLeadK gate (arms 10-12) softened stops behind a late-born stopped lead (closed-loop stop gap
# 0.9 m vs 2.5 m at 18:30; seg 5 min gap 4.7 m vs 11.3 m) and must not be used. Multiplier 1.3 gave -1.91, 0.9 gave
# -1.39. Open: at 630 s the simulated ego is still 2-2.6 m/s faster than the lead, so a late second brake is expected in
# the car and is not modeled. The gate is tuned on three events; replay only, not driven, not yet scored on the corpus.
# Frame counts are planner frames at 20 Hz.
NEED_FLOOR_ENABLED = True       # switch; read at construction so a replay harness can set it before building the planner
# floor = -max(MULT * need, MIN); 1.3 gave -1.91, 0.9 gave -1.39 on seg 10. 1.15 (Peter 2026-11-11, replay only): seg 10 -1.75 (hold-only
# -2.23, 1.0 -1.52); seg 5 / seg 18 stops unchanged; ep1046 REAL -2.30 -> -2.72; 15 of 1141 episodes >0.05 deeper, onsets unchanged
NEED_FLOOR_MULT = 1.15
NEED_FLOOR_MIN = 0.8            # m/s^2; the shallowest the floor may be
NEED_FLOOR_HEADWAY_S = 1.0      # s; need's gap target = vLead * this + STOP_M
NEED_FLOOR_STOP_M = 6.0         # m
NEED_FLOOR_MIN_ROOM_M = 5.0     # m; need's room is never smaller than this
NEED_FLOOR_RELEASE_TTC_S = 3.0  # s; closing at or under this TTC: floor off and sticky
NEED_FLOOR_RELEASE_NEED = 2.0   # m/s^2; need at or over this: floor off and sticky
NEED_FLOOR_MIN_V_EGO = 5.0      # m/s
NEED_FLOOR_MIN_D = 15.0         # m
NEED_FLOOR_GATE_V_LEAD = 5.0    # m/s; lead must be moving (stopped leads at 5:34 and 18:30 never opened the gate)
NEED_FLOOR_GATE_A_LEAD = -1.0   # m/s^2; lead's aLeadK must be above this (not itself braking hard)
NEED_FLOOR_GATE_FRAMES = 10     # consecutive frames of the gate on one (track id, radar flag): 0.5 s
NEED_FLOOR_QUIET_FRAMES = 20    # frames with no lead closing before the sticky-off clears: 1.0 s
# Owner 2026-11-11 (via Bob), scorecard ep645, route 000000ae seg 81: gap 22 m at 16.0 m/s (1.37 s), closing 2.2 m/s; floor -0.80
# vs hold -1.19, owner wants the floor not to soften a lead this close. Always on (the car's setting; no toggle); replay only.
NEED_FLOOR_MIN_GAP_ENABLED = True  # read by NeedFloor at construction (module attribute), so a replay harness can set it first
NEED_FLOOR_MIN_GAP_S = 1.5      # s; the floor applies only at d >= v_ego * this (evaluated every frame, not sticky)
# Owner 2026-11-14 (fix B), route 000000d2 seg 21 t1298.8 (static + log math): e2e braked -1.89 for a red light; the
# nearest lead was the camera lead (tid -1, no radar) at 73.7 m closing 5.3 m/s with vLead 8.3, which opened the moving-lead
# gate; need 0.24 -> floor -0.80 lifted the target -1.89 -> -0.80 in one cycle and the driver braked at -4.0 1.5 s later.
# B: the floor applies to radar leads only (a camera-only lead still runs the gate / sticky state, it just never lifts).
# (Fix A, a cap/stopping special case, was deleted 2026-11-15: the floor now acts on the lead candidate only, see lead().)
NEED_FLOOR_RADAR_ONLY = True


class NeedFloor:
  """Raises a braking target to at least -max(NEED_FLOOR_MULT * need, NEED_FLOOR_MIN) for a steady closing moving lead.

  need = closing^2 / (2 * max(d - (max(vLead, 0) * HEADWAY_S + STOP_M), MIN_ROOM_M)), the decel that closes the speed
  difference in the room left before the headway gap. The floor only RAISES a braking target (never adds braking) and
  never touches should_stop. It applies to the nearer present planner lead (leadOne or leadTwo, vision or radar) only
  when the lead is a radar lead (NEED_FLOOR_RADAR_ONLY), the lead is closing, v_ego >= MIN_V_EGO, d >= MIN_D, ttc > RELEASE_TTC_S, need <
  RELEASE_NEED, the floor is not
  sticky-off and the gate (vLead >= GATE_V_LEAD and aLeadK > GATE_A_LEAD for GATE_FRAMES consecutive frames on the same
  (track id, radar flag)) is open. Sticky-off: once the release fires (closing and (ttc <= RELEASE_TTC_S or need >=
  RELEASE_NEED)) or the Stock Brake Feel emergency latch is on, the floor stays off until QUIET_FRAMES frames with no
  lead closing, or the lead identity changes to one farther away than the previous frame's gap. No lead: quiet + 1, gate
  count 0, sticky clears at QUIET_FRAMES. It acts on the lead MPC candidate only (HondaBoschALongEnhancement.lead(),
  d2 t1297.6 red-light let-off, 2026-11-15), so e2e or cruise braking deeper than the lead is never lifted; that is why
  there is no cap / stopping special case. longitudinal_planner.py only; not in the upstream planner. Parity target: the ARM 'D'
  block of replay_bd.py (Job's scorecard
  harness), including its rounding of the lead fields (d and vRel to 0.01, aLeadK to 0.001). Replay only."""
  def __init__(self):
    """Reads NEED_FLOOR_MIN_GAP_ENABLED (module constant, on) at construction: when on, also require d >= v_ego *
    NEED_FLOOR_MIN_GAP_S, re-evaluated every frame; it never touches gate_count, off or quiet."""
    self.min_gap = NEED_FLOOR_MIN_GAP_ENABLED is True
    self.reset()

  def reset(self):
    self.off = False
    self.quiet = 0
    self.last_id = None
    self.last_d = None
    self.gate_id = None
    self.gate_count = 0

  @staticmethod
  def _view(lead):
    return (int(getattr(lead, 'radarTrackId', -1)), int(bool(getattr(lead, 'radar', False))),
            round(float(lead.dRel), 2), round(float(lead.vRel), 2), round(float(getattr(lead, 'aLeadK', 0.0)), 3))

  def step(self, leads, v_ego: float, emergency: bool, target: float) -> float:
    views = [self._view(lead) for lead in leads if _present(lead)]
    a = float(target)
    if not views:
      self.quiet += 1
      self.gate_count = 0
      if self.off and self.quiet >= NEED_FLOOR_QUIET_FRAMES:
        self.off = False
      return a
    track_id, radar, d, v_rel, a_lead = min(views, key=lambda x: x[2])
    v_ego = float(v_ego)
    v_lead = v_ego + v_rel
    need = (v_rel * v_rel if v_rel < 0 else 0.0) / (2.0 * max(d - (max(v_lead, 0.0) * NEED_FLOOR_HEADWAY_S + NEED_FLOOR_STOP_M),
                                                               NEED_FLOOR_MIN_ROOM_M))
    ttc = closing_ttc(d, -v_rel, 0.1)
    closing = v_rel < 0
    lid = (track_id, radar)
    if closing:
      self.quiet = 0
    else:
      self.quiet += 1
    if self.off and (self.quiet >= NEED_FLOOR_QUIET_FRAMES or
                     (self.last_id is not None and lid != self.last_id and self.last_d is not None and d > self.last_d)):
      self.off = False
    self.last_id = lid
    self.last_d = d
    if (closing and (ttc <= NEED_FLOOR_RELEASE_TTC_S or need >= NEED_FLOOR_RELEASE_NEED)) or bool(emergency):
      self.off = True
    if self.gate_id != lid or not (v_lead >= NEED_FLOOR_GATE_V_LEAD and a_lead > NEED_FLOOR_GATE_A_LEAD):
      self.gate_count = 0
    else:
      self.gate_count += 1
    self.gate_id = lid
    if (self.gate_count >= NEED_FLOOR_GATE_FRAMES and closing and not self.off and v_ego >= NEED_FLOOR_MIN_V_EGO and
        d >= NEED_FLOOR_MIN_D and ttc > NEED_FLOOR_RELEASE_TTC_S and need < NEED_FLOOR_RELEASE_NEED and
        (not self.min_gap or d >= v_ego * NEED_FLOOR_MIN_GAP_S) and
        (radar or not NEED_FLOOR_RADAR_ONLY)):
      a = max(a, -max(NEED_FLOOR_MULT * need, NEED_FLOOR_MIN))
    return a


class HondaBoschALongEnhancement:
  """lead() shapes the lead MPC candidate (law depth cap, need floor); step() is the build rate and coast first on the
  final target.
  Placement: d2 t1297.6 red-light let-off (2026-11-15)."""
  def __init__(self, CP, dt: float):
    """Stock Brake Feel is permanent (owner 2026-11-11); active_for(CP) is the only gate. NeedFloor's min-gap gate is
    always on (NEED_FLOOR_MIN_GAP_ENABLED)."""
    active = active_for(CP)
    self.stock_feel = active
    # Implausible-drop bound (D-041/D-042; owner bookmark route a2 seg 50, 2026-11-07): same gate as the other active
    # checks in this module (Bosch-A supported, radar available); default ON, no toggle.
    self.drop_bound = ImplausibleDropBound() if active else None
    self.newborn_hold = NewbornLeadHold() if active and NEWBORN_HOLD_ENABLED else None
    self._need_floor = NeedFloor() if self.stock_feel and NEED_FLOOR_ENABLED else None
    self.dt = dt
    # Coast first: the same gate as everything else here.
    self.coast_enabled = vehicle_supported(CP) and not bool(getattr(CP, 'radarUnavailable', True))  # == long_tuning_active(CP)
    self.coast_floor = None      # staged floor while coasting first; None when not active (replay/debug)
    self.coast_bypassed = False  # latched for the rest of this braking event
    self.reset()

  def planner_radar_state(self, radar_state, a_ego: float, model_v2=None):
    """The radarState the MPC sees: D-080 bounds a newborn radar lead's aLeadK (with confident matching model_v2
    corroboration so filter-convergence range curves cannot force a false emergency stop), then the implausible-drop
    bound (below) clamps a leadOne velocity-glitch brake; otherwise radar_state itself. Chained so both can apply."""
    if self.newborn_hold is not None:
      radar_state = bound_newborn_leads(radar_state, a_ego, self.newborn_hold, model_v2=model_v2)
    if self.drop_bound is not None:
      radar_state = bound_implausible_drop(radar_state, model_v2, self.drop_bound)
    return radar_state

  def reset(self):
    self.reset_onset()
    self.reset_lead()
    self.reset_coast()

  def reset_onset(self):
    self.onset_episode = False
    self.onset_free = False  # this episode passes through (close lead at its start, low TTC, FCW or stopping)

  def reset_lead(self):
    """Lead-candidate path state: the law and its own previous output (NeedFloor resets in need_floor)."""
    self._reset_law()
    self.lead_prev = None

  def _reset_law(self):
    self.emergency = False
    self.law_t = 0.0
    self.law_recent = False

  def reset_coast(self):
    self.coast_floor = None
    self.coast_bypassed = False

  @property
  def coast_active(self) -> bool:
    return self.coast_floor is not None

  def need_floor(self, *, lead_one, lead_two, target: float, v_ego: float, reset_state: bool) -> float:
    """Need floor (NeedFloor, above): raise a braking lead-candidate `target` for a steady closing moving lead. Called
    from lead() (longitudinal_planner.py only, not upstream/planner.py), so it only ever sees the lead MPC candidate.
    Not active (Stock Brake Feel off, or NEED_FLOOR_ENABLED False at construction) or reset_state: state is cleared and
    the target passes through."""
    if self._need_floor is None or reset_state:
      if self._need_floor is not None:
        self._need_floor.reset()
      return float(target)
    return self._need_floor.step((lead_one, lead_two), v_ego, self.emergency, target)

  def lead(self, *, lead_one, lead_two, target: float, v_ego: float, stopping: bool, standstill: bool,
           reset_state: bool, fcw: bool, floor: bool = True) -> float:
    """Shape the lead MPC candidate only (before min(candidates)): the Stock Brake Feel law from this method's own previous
    output (`lead_prev`, not the published target), then the need floor when `floor`. e2e and cruise braking never pass
    through it (d2 t1297.6 red-light let-off, 2026-11-15). `stopping` covers should-stop and force stop;
    upstream/planner.py passes floor=False (it never ran the need floor)."""
    target = float(target)
    if reset_state or standstill:
      self.reset_lead()
      if floor:
        self.need_floor(lead_one=lead_one, lead_two=lead_two, target=target, v_ego=v_ego, reset_state=True)
      return target
    leads = (lead_one, lead_two)
    out = target
    if not self.stock_feel:  # the law is Stock Brake Feel's
      self.lead_prev = None
    elif stopping:
      self._reset_law()
    else:
      law_prev = target if self.lead_prev is None else self.lead_prev
      self.emergency = stock_feel_emergency(leads, v_ego, self.emergency)
      if not self.emergency:
        out = stock_feel_cap(leads, law_prev, target, self.dt, v_ego)
      self.law_recent = self.law_t > 0.0  # read by step() for the build rate this cycle
      self.law_t = release.STOCK_FEEL_EXIT_HOLD_S if stock_feel_law_active(leads, self.emergency) else max(0.0, self.law_t - self.dt)
    if floor:
      out = self.need_floor(lead_one=lead_one, lead_two=lead_two, target=out, v_ego=v_ego, reset_state=reset_state)
    self.lead_prev = float(out)
    return self.lead_prev

  def step(self, *, lead_one, lead_two, prev: float, target: float, v_ego: float,
           stopping: bool, standstill: bool, reset_state: bool, fcw: bool, follow_s: float | None = None) -> float:
    """The FINAL target (after min(candidates)): the brake onset ramp, then coast first when `follow_s` is given, so a
    model or cruise brake gets the same gentle start as a lead brake (2026-11-15). The lead-based law is lead()."""
    out = self._onset(lead_one=lead_one, lead_two=lead_two, prev=prev, target=target, v_ego=v_ego, stopping=stopping,
                      standstill=standstill, reset_state=reset_state, fcw=fcw)
    if follow_s is None:
      return out
    if standstill:
      self.reset_coast()
      return out
    return self._coast_first(lead_one=lead_one, lead_two=lead_two, target=out, v_ego=v_ego, follow_s=follow_s, fcw=fcw,
                             reset_state=reset_state)

  def _onset(self, *, lead_one, lead_two, prev: float, target: float, v_ego: float, stopping: bool, standstill: bool,
             reset_state: bool, fcw: bool) -> float:
    """Build rate on the final target (prev = last published target): the law's stock jerk, or the onset ramp in an
    emergency. Never lets off and never limits a rise."""
    out = float(target)
    if not self.stock_feel or reset_state or standstill:
      self.reset_onset()
      return out
    leads = (lead_one, lead_two)
    if self.onset_episode and out >= ONSET_END_ACCEL and prev >= ONSET_END_ACCEL:
      self.onset_episode = False
      self.onset_free = False
    if not self.onset_episode and out < ONSET_START_ACCEL:
      self.onset_episode = True
      self.onset_free = lead_close(leads)
    if self.onset_episode and (fcw or stopping or lead_ttc_low(leads)):
      self.onset_free = True
    if stopping:  # the law stands down while stopping (lead() resets it); so does the ramp (onset_free above)
      return float(out)
    if self.emergency:  # the law passes an emergency through; only the onset ramp may bind
      jerk = ONSET_JERK if self.onset_episode and not self.onset_free else None
    else:  # the law's build rate, on every brake (option 2, 2026-11-15); its depth cap is lead()'s
      jerk = stock_feel_jerk(leads, v_ego, self.law_recent)
    return brake_onset_limited_target(prev, out, self.dt, jerk)

  def _coast_first(self, *, lead_one, lead_two, target: float, v_ego: float, follow_s: float, fcw: bool,
                   reset_state: bool) -> float:
    """Coast first on the final target: a new brake past COAST_ACCEL starts at COAST_ACCEL and deepens at
    COAST_RAMP_JERK while a radar lead is clear; it never lets off a brake that is already built."""
    target = float(target)
    if not self.coast_enabled or reset_state:
      self.reset_coast()
      return target
    if target >= COAST_ACCEL:
      self.reset_coast()  # not braking past a lift-off: the event is over
      return target
    if self.coast_bypassed:
      return target
    from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_stop_gap import closest_radar_lead
    lead = closest_radar_lead((lead_one, lead_two))
    floor = COAST_ACCEL if self.coast_floor is None else self.coast_floor - COAST_RAMP_JERK * self.dt
    if lead is None or fcw or v_ego < COAST_MIN_V_EGO or not self._clear(lead, v_ego, follow_s, floor):
      self.coast_floor = None
      self.coast_bypassed = True
      return target
    self.coast_floor = floor
    return max(target, floor)

  @staticmethod
  def _clear(lead, v_ego: float, follow_s: float, floor: float) -> bool:
    d_rel, v_lead, a_lead = float(lead.dRel), float(lead.vLead), float(getattr(lead, 'aLeadK', 0.0))
    closing = v_ego - v_lead
    return (d_rel >= (follow_s + COAST_GAP_MARGIN_S) * v_ego and
            (closing <= 0.0 or d_rel / closing >= COAST_MIN_TTC_S) and
            a_lead >= COAST_MAX_LEAD_DECEL and
            projected_gap_ok(d_rel, v_lead, a_lead, v_ego, floor))


# ---- Newborn lead aLeadK bound (D-080), under NEWBORN_HOLD_ENABLED --------------------------------------------------
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
# Camera-corroborated newborn range-fit cap (000000ed--fc469136cd seg 6, 384.8..387.1 s; closed-loop replay only, no
# XCP dependency): track 6 converged 65.2 -> 50.0 m over 1.4 s with fake quadratic curvature (_range_decel) while
# matching modelV2 (prob ~0.98) stayed calm (a ~ -0.2..-0.4 m/s^2). Without camera corroboration, the converging fit
# lowered aLeadK to -2.75 at 50-44 m (TTC > 4.1 s) and -1.00 still tripped STOCK_FEEL_LEAD_STOP_A (-1.0) emergency.
NEWBORN_MODEL_MIN_D = 40.0        # m; urgent close leads (< 40 m) bypass camera floor immediately
NEWBORN_MODEL_MIN_TTC = 4.0       # s; urgent short-TTC leads (<= 4 s) bypass camera floor immediately
NEWBORN_MODEL_PROB_MIN = 0.9      # modelV2 confidence required to constrain newborn range fit
NEWBORN_MODEL_RANGE_M = 8.0       # m minimum camera/radar range match window
NEWBORN_MODEL_RANGE_FRAC = 0.25   # fraction of dRel match window
NEWBORN_MODEL_MIN_BRAKE = 0.95    # m/s^2 soft floor (> STOCK_FEEL_LEAD_STOP_A = -1.0 cliff) while camera is calm
NEWBORN_MODEL_ACCEL_MARGIN = 0.35 # m/s^2 below smoothed model.a before floor drops
NEWBORN_MODEL_A_ALPHA = 0.25      # EMA alpha per 50 ms frame to suppress single-frame model.a spikes
NEWBORN_RELEASE_RATE = 0.5        # m/s^2 per s D-042 slew-out when a camera-held newborn window expires
# Camera-floor limits, REPLAY ONLY (nb_census, routes e3 e5 e6 d1..d6 ed; not road-validated).
# (1) The floor may move at most NEWBORN_FLOOR_SLEW per frame toward MORE braking, and at NEWBORN_RELEASE_RATE toward
#     less, so a match loss, an urgent bypass or the range fit crossing the floor cannot step aLeadK (e5 seg1 tid5
#     +57.53 s: urgent flip, e6 seg14 tid59 +28.75 s: match lost then re-armed, steps of 1.8 to 1.9 m/s^2 in the patch).
# (2) A far fast closer keeps radar authority: e3 seg12 tid52 (107 m, vRel -9.85, TTC 10.9 s) was a real braking lead
#     (hindsight -3.2) that the -0.95 floor hid (aT -1.62 base, -1.24 patch). ed seg6 tid6 (TTC 6.5 s at birth, the
#     case the floor exists for) is under 8 s and stays lifted. e3/ed are the only two data points for the 8 s cut.
NEWBORN_FLOOR_SLEW = 0.25         # m/s^2 per 50 ms frame, toward more braking
NEWBORN_CAMERA_MAX_TTC = 8.0      # s; the camera lift applies only below this time to collision


def _radar_lead(lead) -> bool:
  return _present(lead) and bool(getattr(lead, "radar", False))


def _matched_model_lead(d_rel: float, model_v2, prob_min: float, range_m: float, range_frac: float):
  """Best matching confident modelV2.leadsV3 entry near d_rel, returning (prob, x, v, a) or None."""
  if model_v2 is None:
    return None
  try:
    leads = model_v2.leadsV3
  except (AttributeError, TypeError):
    return None
  tol = max(range_m, range_frac * d_rel)
  cam_offset = _radar_to_camera()
  best = None
  best_err = float('inf')
  for i in range(min(2, len(leads))):
    try:
      lead = leads[i]
      prob = float(lead.prob)
      mx = float(lead.x[0])
      mv = float(lead.v[0])
      ma = float(lead.a[0])
    except (AttributeError, IndexError, TypeError, ValueError):
      continue
    if prob < prob_min:
      continue
    err = abs(d_rel - (mx - cam_offset))
    if err <= tol and err < best_err:
      best_err = err
      best = (prob, mx, mv, ma)
  return best


class NewbornLeadHold:
  """Per radar track, (frame, dRel, aEgo) since it became a lead; bounds aLeadK while it is newborn."""
  def __init__(self):
    self.frame = 0
    self.hist: dict[int, list] = {}
    self.bound_frames = 0
    self._model_a_ema: dict[int, tuple[int, float]] = {}
    self._cam_floor_state: dict[int, tuple[int, float]] = {}
    self._floor_slew: dict[int, tuple[int, float, bool]] = {}

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
      self._cam_floor_state.pop(tid, None)
      self._floor_slew.pop(tid, None)
    elif h[-1][0] != self.frame:  # leadOne and leadTwo on one track: record it once
      h.append((self.frame, d_rel, float(a_ego)))
    return h

  def _update_model_a(self, tid: int, d_rel: float, model_v2) -> float | None:
    if model_v2 is None:
      return None
    prev = self._model_a_ema.get(tid)
    if prev is not None and prev[0] == self.frame:
      return prev[1]
    ml = _matched_model_lead(d_rel, model_v2, NEWBORN_MODEL_PROB_MIN, NEWBORN_MODEL_RANGE_M, NEWBORN_MODEL_RANGE_FRAC)
    if ml is None:
      self._model_a_ema.pop(tid, None)
      return None
    if prev is None or self.frame - prev[0] > NEWBORN_LEAD_GAP_FRAMES:
      ema = ml[3]
    else:
      ema = (1.0 - NEWBORN_MODEL_A_ALPHA) * prev[1] + NEWBORN_MODEL_A_ALPHA * ml[3]
    self._model_a_ema[tid] = (self.frame, ema)
    return ema

  def bound(self, lead, a_ego, model_v2=None):
    """aLeadK for `lead`, or None when it is left as is. Call once per lead per frame, after tick()."""
    h = self.observe(lead, a_ego)
    if h is None:
      return None
    tid = int(getattr(lead, "radarTrackId", -1))
    d_rel = float(lead.dRel)
    v_rel = float(getattr(lead, "vRel", 0.0))
    non_urgent = d_rel >= NEWBORN_MODEL_MIN_D and (v_rel >= 0.0 or d_rel / -v_rel > NEWBORN_MODEL_MIN_TTC)
    a_lead = float(lead.aLeadK)

    if self.frame - h[0][0] < NEWBORN_LEAD_FRAMES:
      a_range = self._range_decel(h)
      a_base = -NEWBORN_LEAD_MIN_BRAKE if a_range is None else min(-NEWBORN_LEAD_MIN_BRAKE, a_range)
      cam_a_ema = self._update_model_a(tid, d_rel, model_v2) if model_v2 is not None else None
      # camera lift: calm matching camera, not urgent, and not a far fast closer (TTC above NEWBORN_CAMERA_MAX_TTC)
      lift = non_urgent and cam_a_ema is not None and (v_rel >= -0.5 or d_rel / -v_rel <= NEWBORN_CAMERA_MAX_TTC)
      cam_floor = min(-NEWBORN_MODEL_MIN_BRAKE, cam_a_ema - NEWBORN_MODEL_ACCEL_MARGIN) if lift else a_base
      a_floor = max(a_base, cam_floor)
      slew = self._floor_slew.get(tid)  # (frame, floor, lifted); leadOne and leadTwo on one track share the frame's floor
      if slew is not None and slew[0] == self.frame:
        a_floor, lifted = slew[1], slew[2]
      else:
        if slew is not None and self.frame - slew[0] <= 1 and (a_floor > a_base or slew[2]):
          if a_floor < slew[1]:
            a_floor = max(a_floor, slew[1] - NEWBORN_FLOOR_SLEW)
          else:
            a_floor = min(a_floor, slew[1] + NEWBORN_RELEASE_RATE * NEWBORN_LEAD_DT)
        a_floor = max(a_floor, a_base)
        lifted = a_floor > a_base + 1e-9
        self._floor_slew[tid] = (self.frame, a_floor, lifted)
      if a_lead >= a_floor:
        return None
      if lifted:
        self._cam_floor_state[tid] = (self.frame, a_floor)
      self.bound_frames += 1
      return a_floor

    prev = self._cam_floor_state.get(tid)
    if prev is None or (self.frame - prev[0]) > 1:
      self._cam_floor_state.pop(tid, None)
      return None
    # slew out at the D-042 rate while the camera still corroborates, at NEWBORN_FLOOR_SLEW when it does not (no step)
    rate = NEWBORN_RELEASE_RATE * NEWBORN_LEAD_DT if (model_v2 is not None and non_urgent) else NEWBORN_FLOOR_SLEW
    a_floor = prev[1] if prev[0] == self.frame else prev[1] - rate
    if a_lead >= a_floor:
      if prev[0] != self.frame:
        self._cam_floor_state.pop(tid, None)
      return None
    self._cam_floor_state[tid] = (self.frame, a_floor)
    self.bound_frames += 1
    return a_floor

  def tick(self):
    self.frame += 1
    if len(self.hist) > 64:
      self.hist = {k: h for k, h in self.hist.items() if self.frame - h[-1][0] <= NEWBORN_LEAD_GAP_FRAMES}
      self._model_a_ema = {k: v for k, v in self._model_a_ema.items() if k in self.hist}
      self._cam_floor_state = {k: v for k, v in self._cam_floor_state.items() if k in self.hist}
      self._floor_slew = {k: v for k, v in self._floor_slew.items() if k in self.hist}


class _BoundedLead:
  """A lead that reads as `lead` except for the given field overrides. Wrapping an already wrapped lead merges the
  overrides (the new ones win) onto the original lead instead of nesting proxies."""
  def __init__(self, lead, **fields):
    if isinstance(lead, _BoundedLead):
      fields = {**lead._fields, **fields}
      lead = lead._lead
    self._lead = lead
    self._fields = fields
    for name, value in fields.items():
      setattr(self, name, value)

  def __getattr__(self, name):
    return getattr(self._lead, name)


class _BoundedRadarState:
  def __init__(self, radar_state, lead_one, lead_two):
    self._radar_state = radar_state
    self.leadOne = lead_one
    self.leadTwo = lead_two

  def __getattr__(self, name):
    return getattr(self._radar_state, name)


def bound_newborn_leads(radar_state, a_ego: float, hold: NewbornLeadHold, model_v2=None):
  hold.tick()
  leads = []
  changed = False
  for lead in (radar_state.leadOne, radar_state.leadTwo):
    a_lead = hold.bound(lead, a_ego, model_v2=model_v2)
    leads.append(lead if a_lead is None else _BoundedLead(lead, aLeadK=float(a_lead)))
    changed |= a_lead is not None
  return _BoundedRadarState(radar_state, leads[0], leads[1]) if changed else radar_state


# ---- Implausible radar-drop bound on leadOne (owner bookmark, route 000000a2--794ebefbf7 seg 50, 2026-11-07) --------
# Right after a left lane change, leadOne was radar track 24 at 18 m, matched to the camera lead (leadsV3[0] x~19-20 m,
# prob 1.0). Over 0.7 s track 24's vLead collapsed 12.5 -> 2.9 m/s (vRel +1.1 -> -6.9, an implied -13 m/s^2, physically
# impossible), aLeadK pinned at -3.0. The camera lead's v stayed 10.5-11.9 m/s and x 19-20 m the whole time. The planner
# braked at -3.5 and the car went 10.3 -> 4.2 m/s; the track then died and the next track (62) showed the car pulling
# away at 22 m. A radar velocity glitch, not a real lead. D-041/D-042: the point is never dropped or altered in
# radarState; this only bounds what leadOne publishes to the planner (MPC + this module's stock-feel law). Replay only
# (16-drive census + 12-episode gate rerun, 2026-11-07); no road evidence yet for this specific bound.
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
IMPLAUSIBLE_DROP_DT = 0.05   # s per planner frame (DT_MDL)


# Lazy import, same reasoning as active_for's: this module is imported before radard's car gates are known to apply.
# The single definition lives in radar_camera_witness.
def _radar_to_camera() -> float:
  from openpilot.nrdr.features.radar.radar_camera_witness import RADAR_TO_CAMERA
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
  bounded = _BoundedLead(lead, **fields)
  return _BoundedRadarState(radar_state, bounded, radar_state.leadTwo)
