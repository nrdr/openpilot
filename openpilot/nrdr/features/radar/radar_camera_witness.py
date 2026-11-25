"""Bosch-A camera witness: one rule that moves a published radar lead toward the camera (model) lead.

Two stages per lead index. Stage 1 (blend): the reversal and weak tells give a weight and `_blend` moves the raw lead
toward the camera lead. Stage 2 (cap): the cap tell reads the stage-1 lead and adds a rate-limited correction on top of it.
dRel is never moved and the point is always published (D-041/D-042). Replaces radar_lead_bound (WeakLeadBound),
radar_reversal_bound (ReversalBound) and radar_camera_cap (CameraCap), in their old order; their evidence is kept below, one
block per tell, in the words of its owner. The shared veto and the order against CameraSlowBound are static; not replayed
beyond the scorecard traces: every replay number below was measured on the separate modules.

Why the cap reads the stage-1 lead, and why the reversal tell is not slewed (scorecard ep292, a4 seg16, labeled REAL by
Peter; replay trace): the first unification ran the cap on the raw lead and slewed all tells together. The raw-lead gap was
3.2-4.4 m/s and fired the cap where the post-reversal gap (the lead the old cap saw) was 1.3-1.8, and the slewed release
left a 0.3 s tail after the reversal latch ended and hid a -2.9 aLeadK frame. So the cap measures its gap on the lead the
reversal and weak tells already moved, and the reversal weight drops at once when its latch ends. The weak tell still slews.

=== Tell `weak`: unconfirmed and contradicted, or passed (was radar_lead_bound) ===
Two far false brake taps behind a lead that was not slowing (2026-10-26 drive), each with its own tell:

Route 34 (11c8fa231c0499ed/00000034--010fbd6343) T479, 16 m/s: radar track 55 swept in from 88 m to 52 m in 3 s
(range falling 15-17 m/s around the tap) while its vRel read -8 to -10.6, and became lead0 through the strict gate at
62-76 m with aLeadK already at the -3 clamp; the plan went to -1.91. The model lead held 61-66 m at 13-14 m/s with
a ~ 0, and its own range fell only 1-2 m/s. The track's F0 STATUS nibble read 9 (not confirmed) until +1.48 s.

STATUS 9 alone is not a tell: Job's census over the post-rebase routes found it on 8 % of engaged lead0 time and under
39 of 747 brakes, and on his stills 3 of the 14 STATUS-9 brakes on routes 0c-368 were real (2ed T338.6 a truck,
368 T657.1 stopped traffic, 0c T342.7) and 2 more lean real. A STATUS-only weight would have softened all five. What
route 34 has and they don't is the camera's range contradicting the radar's closing: from 0 to +0.7 s, over the last
1.5 s, the model lead's range fell 8.8-9.9 m/s slower than the radar lead's vRel said and slower than the track's own
range fell, while the model lead's range slope stayed within 3 m/s of its own closing speed. In 2ed T338.6 the camera
saw the truck late and the gap peaked at 5.8 m/s; in the other four it stayed under 1, and in the four real far
brakes (2f T736, 10 T188, 32 T1248, 0f T2190) at 0 even with STATUS taken as 9. A model lead whose range slope and
closing speed disagree by more than CAMERA_SELF_TOL (it jumped to another car: 25.6 m/s in 368 T657.1) is no witness.

Route 37 (00000037--34e868f7ba) T903, 30 m/s: an SUV 45-50 m ahead moving out to the right. Radar track 32 (STATUS 7,
old) dipped vLead 28.7 -> 24.8 (aLeadK -2.9) and went back to 31; the model lead held v 29, a 0 and moved on to the
next car at 61-71 m. Track 32 kept lead0 only through the relaxed gate: from +0.03 s, the start of the tap (plan
-0.29 -> -1.84), its range was more than the strict window (0.25 x range, at least 5 m) short of the model lead's.

That range gap alone is not a tell. On the same drive (T273-278) a pickup slowing to turn left held lead0 at 82 m
while the model lead had moved on to 110 m: the gap reached the window's edge and the plan went to -2.21 for a
real slowdown. There the model lead was itself closing at 11.7 m/s. In the four real far brakes it closed at 4.5 m/s
or more (median 9-13) and the gap stayed under 0.65 of the window; at route 37 T903 it closed at -0.2 to +1.5 m/s. So
the gap counts only while the model lead is past the radar lead and calls for no braking (camera_passed_ratio). On
route 37 none of the six real slowdowns on the stills then gets any weight at its brake; T323, an SUV turning right at
an intersection (ambiguous on the stills), gets at most 0.27 around its -1.12 (log emulation, not a replay).

So while a published radar lead is unconfirmed and its closing contradicted as above, its vLead/vLeadK/vRel and
aLeadK are moved all the way to the model lead's, and while the model lead has moved on past it, 0.6 of the way
(all the way once it is 1.5 windows past: b1 seg14, see DISTANCE_FAR_START), by
the shared blend (see "Shared veto, slew and blend" below; before the unification it was the curve-brake bound's blend,
radar_reversal_bound.ReversalBound.apply, floor_weights): only toward the less severe side, only with the
model lead as a credible witness, never when the radar lead is urgent, dRel never moved, the point always published
(D-041/D-042). Neither tell reads the radar lead's dynamics alone: the mismatch, cut-out and onset rules (PROGRESS-7.0
entry 8) did, and also fired on real slowdowns.

The weight is per lead index and rate limited so that a tell coming and going does not step the published lead
(D-042): a new radar track takes its tell's weight at once, an established one rises over RISE_S and releases over
RELEASE_S. (That slew is now the shared one, applied to every tell.)

Job's open-loop replay of the logged radarTracks through the full radard and the 7.0 planner (rebuilt replay; its
base under-brakes the logged taps by 0.09/0.12): route 34's tap -1.82 -> -0.19 (the brake never starts; 0.6 gave
-0.75), route 37's -1.73 -> -0.64 (1.0 on the camera-passed tell gave -0.60 at more cost on the ambiguous route 37
T323, so it stays 0.6; the far ramp from 1.25 leaves T323 alone and took b1 seg14's -1.07 to +0.11, every other
event within 0.15, 2026-11-08). The 19 real brakes (the four far ones, ev19, route 37's six slowdowns and T323, three
turn-offs) keep their minimum within 0.04 and their onset. Replay evidence only, open loop; no road evidence yet.

=== Tell `reversal`: accel reversal latch (was radar_reversal_bound) ===
Route 30 (11c8fa231c0499ed/00000030--70508f00bd) T1420-1425, a two-lane S-curve with guardrails both sides and the
lead 4-6 m off-centre: radar track 60 kept its ID while its range swung 45 -> 54 -> 39 m and vLead 22 -> 27.6 -> 15.7
in about 4 s. The model lead held 47-52 m at 21-22 m/s with a ~ 0, and on the stills the lead does not close.
Published aLeadK went +4.0 to -3.0 (the clamp) in 1 s; the negative half took the plan (lead0) to aTarget -2.87.

A real car does not go from accelerating above +2 m/s^2 to braking below -2 m/s^2 inside 1.5 s. Under that rule the
model lead had 0 hits on 18 radar routes (0d-20, 25, 27, 2a, 2b, 2c, 2e, 2f, 30, 31, 32), while radar leads had 18.
Only route 30's hit had lead0 braking the plan below -1.0 in the next 4 s. Of the 58 engaged lead0 brakes below
-1.5 on those routes, none had a same-track reversal in the 4 s before it (log level, limited road evidence; one
positive event, on one road).

So for LATCH_S after such a reversal the published lead's vLead/vLeadK/vRel and aLeadK are moved W of the way
toward the model lead, only when the model lead is the less severe, and only while the model lead is a credible
witness. dRel is never moved and the point is always published (D-041/D-042). The radar's own geometry bypasses the
bound when it is urgent (range or TTC short), so a real close-in brake keeps full authority. A false trigger costs
nothing unless the radar lead is braking the plan inside the latch.
Estimated effect on route 30 (regression on that route's lead0 rows, not a planner replay): -2.87 -> about -1.3.

A lead is blended once, at the largest weight among the tells (see below), under the same witness and urgency rules.
The latch itself is unchanged by the unification; its weight W now rises over RISE_S on an established track instead of
stepping in and out (static; not replayed yet).

=== Tell `cap`: far lead closing faster than a confident camera lead (was radar_camera_cap) ===
Far phantom brakes left after the weak-lead and reversal bounds (2026-11-08, Bob, replay at 93b5b5c9d7, Peter's stills):
  000000b0 seg17 ~17:05-17:13: radar track 53 at 60-80 m read vRel well below the model lead, which held its range
    (range slope within CAMERA_SELF_TOL of its own closing speed, a > -0.5). Phantom on the stills. The radar's own
    range slope agreed with its doppler at onset (-4.4..-5.4 vs -4.9), so no radar-only tell separates it: the
    contradiction bound (the weak tell above) needs STATUS 9 and the camera-passed tell needs the camera past the radar.
  0000008a seg2 and 00000071 seg12: the same shape; Peter: no car cutting in, phantoms.
Gating on where the camera lead sits against the radar's (at or past it, or no more than 5 m past) was tried in
replay and dropped: route 71 (gap/dRel 0.15-0.32) and b0 17:13 (up to 0.17) overlap, and either gate lost one of them.

So while a radar lead is at least CAP_MIN_D away, a camera lead with filtered prob >= CAP_PROB sits within
CAP_RANGE_FRAC of its range, its range slope matches its own closing speed within CAMERA_SELF_TOL, it slows no harder
than CAMERA_DECEL_MIN, and it closes more than CAP_GAP_MIN slower than the radar's vRel, the published vLead/vLeadK/vRel
are raised to the camera's closing speed. Only ever less braking, toward a camera that calls for none; never past the
camera. While the cap is active, aLeadK is also lifted toward the camera lead's a (floored at CAMERA_DECEL_MIN), never
lowered. dRel and the point are untouched (D-041/D-042). The cap is stage 2: its gap, its target and the aLeadK lift are
computed on the stage-1 lead, and its correction is the old cap's rate-limited state (restored 2026-11-11 after scorecard
replays: ep128 softer/later under weight * gap forms, ep154 and ep356 harder while the cap's release was still running; replay).
Its target is the tell times the camera gap (m/s); it follows that target at +-CAP_DV_RATE (8 m/s per second) for
vLead/vLeadK/vRel and +-CAP_DA_RATE (10 m/s^2 per second) for the aLeadK lift, in and out, so it never falls faster than
the rate. Known property, kept as baseline behavior (not replayed as a change): while it decays the correction can exceed
the current camera gap (ep154 +1.57..+1.9 s: published up to ~1.3 m/s less closing than the camera). The replay numbers
below are with these rates. The urgency veto on this tell (a lead under URGENT_D or inside URGENT_TTC is never moved) is
static; it is the one intended difference from the old CameraCap (ep64). Before the unification this ran after
CameraSlowBound; CameraSlowBound (which only ever makes a lead slower) now runs after the witness.

Replay (open loop, logged radarTracks through radard and the planner, 3b3d + StockBrakeFeel + HumanFollowing, plan
min accel, before -> after): b0 17:13 -1.38 -> -0.59, 8a seg2 -1.81 -> -0.82, 71 seg12 -1.74 -> -1.35; 84 seg7 t0
(a queue at a signal 60-100 m out, leans real on the stills) -1.31 -> -1.13; 82 seg13 -0.91 -> -0.85, 99 seg15
-0.68 -> -0.62, 80 seg10 -0.53 -> -0.45; 80 seg19 -2.15 -> -2.27. The other groups of the 93b pool are unchanged, and
replay fidelity moved by at most 0.004 in correlation. Route a2 (60 segs): seg22 -1.34 -> -1.21, seg23 -0.96 -> -0.90,
seg43 -0.59 -> -0.39, seg45 -0.85 -> -0.64, seg50 -0.69 -> -0.74; a3 unchanged.
The cost case is 80 seg19: track 25 is a real slowdown the camera read late (vRel -8 against a camera calling for
much less), so the cap softened the first pulse (-1.70 -> -1.22, logged -1.80) and the second came 0.12 harder.
aLeadK lift (variant A, same replay, cap alone -> cap + lift): 71 seg12 -1.35 -> -0.93, 8a seg2 -0.82 -> -0.72,
b0 17:05 -0.59 -> -0.11; b0 t51.6 stays -3.40 (track 53's range-fit vRel, not the camera's case). No row anywhere
braked harder than the cap alone except 80 seg19's second pulse (+0.20); full-route fidelity moved <= 0.006.
Replay evidence only; no road evidence yet.

Hold (C-012, the only mode; the BoschACameraCapHold toggle and the plain VA branch are gone, static only): the cap above
has a limited, tapered hold: there is no gap floor, and while the cap tell was applied last cycle and the gap is at or below
CAP_GAP_MIN but above CAP_GAP_HOLD, the cap tell is (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD) (as a weight on the
gap; the old D+E target was gap * (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD) in m/s), for at most CAP_HOLD_T
seconds in total per engagement (hold_t is reset on a new track and whenever the cap tell returns to 0, deliberately not
when the gap re-crosses CAP_GAP_MIN).

=== Shared veto and the two stages (static; ep292 and the scorecard traces are replay) ===
One veto for every tell: the weight and the cap state are 0 unless the lead is present, radar, has a track id, its filtered
model lead prob is at least WITNESS_PROB, and the lead is not urgent (urgent(): range under URGENT_D or TTC under
URGENT_TTC, the TTC using radar.urgency_v_rel when the parser has no direct reading; b1 seg14 47.7 s).
Stage 1: weight = max(reversal tell, slewed weak tell). The reversal tell is W while its latch is on and 0 the frame it ends
(not slewed). The weak tell is slewed: a new track id takes its target at once; otherwise weight = min(max(target, previous -
release), previous + rise), rise = SLEW_W * dt / RISE_S, release = SLEW_W * dt / RELEASE_S. Then one blend: vLead/vLeadK/vRel
move weight * (camera speed - vLead) and aLeadK weight * (model a - aLeadK), each only toward the less severe side.
Stage 2: the cap tell, gap and lift are evaluated on the stage-1 lead; `cap_dv`/`cap_da` are added onto it and a new track
or a veto zeroes them. `weights` is the applied weight per lead index (the blend weight, or 1.0 when the cap applied
anything; 0 when nothing changed); `tell_weights` holds each tell's value after the veto, before any slew, for replay/debug.
"""
from __future__ import annotations

import math
from typing import Any

from openpilot.common.realtime import DT_MDL

# ---- weak tell (was radar_lead_bound) ----
UNCONFIRMED_STATUSES = frozenset({9})  # route 34's phantom; 7 = confirmed, 0 = not provided (other radars, old logs)
UNCONFIRMED_W = 1.0          # replay: 0.6 left route 34 at -0.75 (the 40 % left of the phantom's closing); 1.0 at -0.19
CONTRADICTION_START = 6.0    # m/s; 2ed T338.6 (a real truck the camera saw late) peaked at 5.8, the other real ones < 2
CONTRADICTION_FULL = 9.0     # route 34: 6.2 at its lead0 start (-0.40 s), 8.8-9.9 from 0 to +0.7 s
CAMERA_SELF_TOL = 4.0        # m/s; the model lead's range slope must match its closing speed this well (route 34: 3.0)
TREND_S = 1.5                # range slopes are least-squares fits over this window
TREND_MIN_SPAN_S = 0.6
TREND_MIN_SAMPLES = 8
TREND_SAMPLES = round(TREND_S / DT_MDL) + 1
CAMERA_PROB_MIN = 0.5        # model lead ranges below this prob are left out of its slope
DISTANCE_RATIO_START = 0.75  # real far brakes stayed under 0.65; route 37 crossed 0.77 -> 1.02 at the tap's start
DISTANCE_RATIO_FULL = 1.0    # the strict gate's edge
DISTANCE_W = 0.6
# Clearly past: b1 seg14 47.0-48.4 s (night, our lane empty to the far tail lights on the stills), radar track 4 in our
# path closing 12 m/s from 85 to 57 m while the model lead held ~110 m at our speed: ratio 1.5-1.9, and 0.6 left -1.06.
# Route 37 T323 (ambiguous, the reason 1.0 was turned down) peaks at ~0.86 (0.27 weight), so it never reaches this ramp.
DISTANCE_FAR_START = 1.25
DISTANCE_FAR_FULL = 1.5
DISTANCE_FAR_W = 1.0
CAMERA_CLOSING_MAX = 2.0     # m/s; route 37 T903 -0.2 to +1.5, real far brakes 4.5 or more, the turning pickup 11.7
CAMERA_DECEL_MIN = -0.5      # m/s^2; a model lead slowing harder than this calls for braking itself

# ---- reversal tell (was radar_reversal_bound) ----
REVERSAL_HIGH = 2.0       # aLeadK above this arms a track (m/s^2)
REVERSAL_LOW = -2.0       # aLeadK below this within REVERSAL_WINDOW_S of an arm latches it
REVERSAL_WINDOW_S = 1.5
LATCH_S = 4.0             # route 30: the brake came ~1.5 s after the reversal and lasted ~2 s
W = 0.6                   # never all the way to the model lead (D-042)

# ---- cap tell (was radar_camera_cap) ----
RADAR_TO_CAMERA = 1.52
CAP_MIN_D = 50.0       # m; far leads only (b0 track 53 at 60-80 m). Nearer, the radar's speed stands.
CAP_PROB = 0.9         # filtered model lead prob (CameraSlowBound's witness level)
CAP_RANGE_FRAC = 0.3   # camera range within this fraction of dRel (b0 17:05: 70 vs 79 m)
CAP_GAP_MIN = 3.0      # m/s; the camera must close this much slower than the radar's vRel
CAP_GAP_HOLD = 1.0     # m/s; no hold at or below this gap, and the taper reaches 0 here
CAP_HOLD_T = 1.0       # s; total hold time per engagement
CAP_DV_RATE = 8.0      # m/s per second; the cap-only vRel/vLead correction follows its target at this rate, up and down
                       # (the replay in the cap tell's block above ran at 8)
CAP_DA_RATE = 10.0     # m/s^2 per second; the same for the aLeadK lift (variant A replay ran at 10)
# 2026-11-11: the cap correction is the old cap's rate-limited state (radar_camera_cap.py), restored after scorecard
# ep128 (80 seg19, REAL) came out up to 0.24 m/s^2 softer/later (the 0.25 s weight rise on an already-open gap grew the
# correction at 16-20 m/s per second) and ep154/ep356 harder (the weight * gap forms let the correction fall with the gap,
# faster than the old release) (replay). The shared weight slew applies to the weak and reversal tells only.
# Known property, baseline behavior, kept and not replayed as a change: while the state decays it can exceed the current
# camera gap (ep154 +1.57..+1.9 s: published up to ~1.3 m/s less closing than the camera).

# ---- shared veto and slew ----
URGENT_D = 30.0           # radar range below this: no bound
URGENT_TTC = 4.0          # radar TTC below this: no bound
WITNESS_PROB = 0.35       # filtered model lead prob for the model lead to count as a witness (= lead_detection_probability)
RISE_S = 0.25
RELEASE_S = 1.0
SLEW_W = max(UNCONFIRMED_W, DISTANCE_FAR_W)  # rise and release rates are this weight per RISE_S / RELEASE_S


def closing_ttc(d_rel: float, closing: float, min_closing: float) -> float:
  """Time to contact (s) d_rel / closing when the closing speed (m/s, positive = closing) is above min_closing, else inf.
  The one shared TTC expression for the radar and planner code (this module imports nothing from either)."""
  return d_rel / closing if closing > min_closing else math.inf


def urgent(lead: dict[str, Any], v_rel: float | None = None) -> bool:
  """Range or TTC short. `v_rel` replaces the lead's vRel in the TTC when the parser has no direct speed reading for
  the track (radar.urgency_v_rel): b1 seg14 47.7 s, see there."""
  d_rel = float(lead['dRel'])
  closing = max(-float(lead['vRel'] if v_rel is None else v_rel), 0.0)
  return d_rel < URGENT_D or closing_ttc(d_rel, closing, 0.1) < URGENT_TTC


def camera_passed_ratio(d_rel: float, camera_d_rel: float, camera_closing: float, camera_a: float) -> float:
  """How far the model lead is past the radar lead, as a fraction of radard's strict distance window (0.25 x range, at
  least 5 m; 1.0 = its edge). 0 unless the model lead is past it and calls for no braking: closing at most
  CAMERA_CLOSING_MAX and slowing no harder than CAMERA_DECEL_MIN. camera_d_rel is from the radar, like d_rel."""
  if camera_d_rel <= d_rel or camera_closing > CAMERA_CLOSING_MAX or camera_a < CAMERA_DECEL_MIN:
    return 0.0
  return (camera_d_rel - d_rel) / max(abs(camera_d_rel) * 0.25, 5.0)


def range_slope(samples) -> float:
  """Least-squares slope (m/s) of ranges sampled every DT_MDL, oldest first; NaN entries (no sample) are skipped.
  NaN unless at least TREND_MIN_SAMPLES samples span at least TREND_MIN_SPAN_S."""
  points = [(index * DT_MDL, float(value)) for index, value in enumerate(samples) if not math.isnan(value)]
  if len(points) < TREND_MIN_SAMPLES or points[-1][0] - points[0][0] < TREND_MIN_SPAN_S - 1e-9:
    return math.nan
  mean_t = sum(t for t, _ in points) / len(points)
  mean_x = sum(x for _, x in points) / len(points)
  return sum((t - mean_t) * (x - mean_x) for t, x in points) / sum((t - mean_t) ** 2 for t, _ in points)


def camera_contradiction(v_rel: float, radar_slope: float, camera_slope: float, camera_closing: float,
                         camera_a: float) -> float:
  """How much faster (m/s) the radar lead closes than the model lead's range does: the smaller of what its vRel and
  its own range slope claim beyond the camera's range slope. 0 unless the model lead is a credible witness that calls
  for no braking: its range slope matches its own closing speed within CAMERA_SELF_TOL and it slows no harder than
  CAMERA_DECEL_MIN. NaN slopes (too little history) give 0."""
  if math.isnan(radar_slope) or math.isnan(camera_slope) or camera_a < CAMERA_DECEL_MIN:
    return 0.0
  if abs(camera_slope + camera_closing) > CAMERA_SELF_TOL:
    return 0.0
  return max(min(camera_slope - v_rel, camera_slope - radar_slope), 0.0)


def _ramp(value: float, start: float, full: float) -> float:
  return min(max((float(value) - start) / (full - start), 0.0), 1.0)


def tell_weight(object_status: int, distance_ratio: float, contradiction: float = 0.0) -> float:
  unconfirmed = int(object_status) in UNCONFIRMED_STATUSES
  contradicted = UNCONFIRMED_W * _ramp(contradiction, CONTRADICTION_START, CONTRADICTION_FULL) if unconfirmed else 0.0
  passed = DISTANCE_W * _ramp(distance_ratio, DISTANCE_RATIO_START, DISTANCE_RATIO_FULL)
  passed += (DISTANCE_FAR_W - DISTANCE_W) * _ramp(distance_ratio, DISTANCE_FAR_START, DISTANCE_FAR_FULL)
  return max(contradicted, passed)


def cap_gap(lead: dict[str, Any], model_lead, camera_ranges, model_v_ego: float, lead_prob: float) -> float:
  """The cap tell's conditions: camera closing speed minus the radar lead's vRel (m/s) when every condition holds
  (filtered prob >= CAP_PROB, dRel >= CAP_MIN_D, camera range within CAP_RANGE_FRAC of dRel, a range slope within
  CAMERA_SELF_TOL of the camera's own closing speed, a >= CAMERA_DECEL_MIN), else -inf."""
  d_rel = float(lead['dRel'])
  if lead_prob < CAP_PROB or d_rel < CAP_MIN_D:
    return -math.inf
  if abs(d_rel - (float(model_lead.x[0]) - RADAR_TO_CAMERA)) > CAP_RANGE_FRAC * d_rel:
    return -math.inf
  camera_v_rel = float(model_lead.v[0]) - model_v_ego
  camera_slope = range_slope(camera_ranges)
  if math.isnan(camera_slope) or abs(camera_slope - camera_v_rel) > CAMERA_SELF_TOL or float(model_lead.a[0]) < CAMERA_DECEL_MIN:
    return -math.inf
  return camera_v_rel - float(lead['vRel'])


class CameraWitness:
  """Per lead index camera witness over the published Bosch-A leads. Call `apply` once per radard cycle."""
  def __init__(self, dt: float = DT_MDL):
    self.dt = dt
    self.t = 0.0
    self.armed_t: dict[int, float] = {}    # last time aLeadK was above REVERSAL_HIGH, per track
    self.latched_until: dict[int, float] = {}
    self.hold_t = [0.0, 0.0]
    self.track_ids = [-1, -1]
    self.cap_dv = [0.0, 0.0]               # stage 2: the speed correction applied last cycle, per lead index
    self.cap_da = [0.0, 0.0]               # stage 2: the aLeadK lift applied last cycle
    self.slewed = [0.0, 0.0]               # the weak tell's slewed weight, the slew's state
    self.weights = [0.0, 0.0]              # applied weight per lead index (0 when nothing changed), for replay/debug
    self.tell_weights: dict[str, list[float]] = {'reversal': [0.0, 0.0], 'weak': [0.0, 0.0], 'cap': [0.0, 0.0]}

  def _observe(self, track_id: int, a_lead: float) -> None:
    if a_lead > REVERSAL_HIGH:
      self.armed_t[track_id] = self.t
    elif a_lead < REVERSAL_LOW:
      armed = self.armed_t.get(track_id)
      if armed is not None and self.t - armed <= REVERSAL_WINDOW_S:
        self.latched_until[track_id] = self.t + LATCH_S

  def latched(self, track_id: int) -> bool:
    return self.latched_until.get(track_id, -math.inf) >= self.t

  def _cap_tell(self, index: int, lead: dict[str, Any], model_lead, camera_ranges, model_v_ego: float, lead_prob: float,
                track_id: int, tracks) -> float:
    gap = cap_gap(lead, model_lead, camera_ranges, model_v_ego, lead_prob) if track_id in tracks else -math.inf
    if gap > CAP_GAP_MIN:
      return 1.0
    if self.tell_weights['cap'][index] > 0.0 and gap > CAP_GAP_HOLD and self.hold_t[index] < CAP_HOLD_T:
      self.hold_t[index] += self.dt
      return (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD)
    return 0.0

  @staticmethod
  def _blend(lead: dict[str, Any], vision, v_ego: float, model_v_ego: float,
             weight: float) -> tuple[dict[str, Any], float]:
    """Stage 1. Returns (lead, applied weight)."""
    if weight <= 0.0:
      return lead, 0.0
    vision_v = v_ego + (float(vision.v[0]) - model_v_ego)
    dv = weight * max(vision_v - float(lead['vLead']), 0.0)
    da = weight * max(float(vision.a[0]) - float(lead['aLeadK']), 0.0)
    if dv <= 0.0 and da <= 0.0:
      return lead, 0.0
    out = dict(lead)
    out['vLead'] = float(lead['vLead']) + dv
    out['vLeadK'] = float(lead['vLeadK']) + dv
    out['vRel'] = float(lead['vRel']) + dv
    out['aLeadK'] = float(lead['aLeadK']) + da
    return out, weight

  def apply(self, output: list[dict[str, Any]], model_leads, v_ego: float, model_v_ego: float, lead_probs, tracks,
            object_statuses, distance_ratios, contradictions, camera_ranges,
            urgent_v_rels=(None, None)) -> list[dict[str, Any]]:
    self.t += self.dt
    seen = set()
    for lead in output:
      if lead.get('present', False) and lead.get('radar', False):
        track_id = int(lead.get('radarTrackId', -1))
        if track_id >= 0 and track_id not in seen:
          seen.add(track_id)
          self._observe(track_id, float(lead['aLeadK']))
    for track_id in [i for i in self.armed_t if i not in tracks]:
      del self.armed_t[track_id]
    for track_id in [i for i in self.latched_until if i not in tracks or self.latched_until[i] < self.t]:
      del self.latched_until[track_id]

    rise = SLEW_W * self.dt / RISE_S
    release = SLEW_W * self.dt / RELEASE_S
    step, step_a = CAP_DV_RATE * self.dt, CAP_DA_RATE * self.dt
    published = []
    for index, lead in enumerate(output):
      radar_lead = lead.get('present', False) and lead.get('radar', False)
      track_id = int(lead.get('radarTrackId', -1)) if radar_lead else -1
      new_track = track_id != self.track_ids[index]
      if new_track:
        self.hold_t[index] = 0.0
        self.cap_dv[index] = self.cap_da[index] = 0.0
        self.tell_weights['cap'][index] = 0.0   # a hold never carries over to another track
      self.track_ids[index] = track_id
      vetoed = track_id < 0 or float(lead_probs[index]) < WITNESS_PROB or urgent(lead, urgent_v_rels[index])
      reversal = weak = 0.0
      if not vetoed:
        reversal = W if self.latched(track_id) else 0.0
        weak = tell_weight(object_statuses[index], distance_ratios[index], contradictions[index])
      # stage 1: the reversal tell steps, the weak tell slews
      if vetoed:
        self.slewed[index] = 0.0
      elif new_track:
        self.slewed[index] = weak
      else:
        self.slewed[index] = min(max(weak, self.slewed[index] - release), self.slewed[index] + rise)
      lead, self.weights[index] = self._blend(lead, model_leads[index], v_ego, model_v_ego, max(reversal, self.slewed[index]))
      # stage 2: the cap on the stage-1 lead
      cap = 0.0 if vetoed else self._cap_tell(index, lead, model_leads[index], camera_ranges[index], model_v_ego,
                                              float(lead_probs[index]), track_id, tracks)
      if cap <= 0.0:
        self.hold_t[index] = 0.0
      self.tell_weights['reversal'][index], self.tell_weights['weak'][index], self.tell_weights['cap'][index] = reversal, weak, cap
      if vetoed:
        self.cap_dv[index] = self.cap_da[index] = 0.0
        published.append(lead)
        continue
      gap = cap_gap(lead, model_leads[index], camera_ranges[index], model_v_ego, float(lead_probs[index])) \
        if track_id in tracks else -math.inf
      target_dv = cap * gap if cap > 0.0 and gap > 0.0 else 0.0
      target_da = max(0.0, max(float(model_leads[index].a[0]), CAMERA_DECEL_MIN) - float(lead['aLeadK'])) if target_dv > 0.0 else 0.0
      dv = min(max(target_dv, self.cap_dv[index] - step), self.cap_dv[index] + step)
      da = min(max(target_da, self.cap_da[index] - step_a), self.cap_da[index] + step_a)
      self.cap_dv[index], self.cap_da[index] = dv, da
      if dv > 0.0 or da > 0.0:
        self.weights[index] = 1.0
        lead = dict(lead)
        for key in ('vLead', 'vLeadK', 'vRel'):
          lead[key] = float(lead[key]) + dv
        lead['aLeadK'] = float(lead['aLeadK']) + da
      published.append(lead)
    return published
