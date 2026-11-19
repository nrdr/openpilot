"""Bosch-A: bound the braking authority of a radar lead that the camera contradicts.

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
the curve-brake bound's blend (radar_reversal_bound.ReversalBound.apply, floor_weights): only toward the less severe side, only with the
model lead as a credible witness, never when the radar lead is urgent, dRel never moved, the point always published
(D-041/D-042). Neither tell reads the radar lead's dynamics alone: the mismatch, cut-out and onset rules (PROGRESS-7.0
entry 8) did, and also fired on real slowdowns.

The weight is per lead index and rate limited so that a tell coming and going does not step the published lead
(D-042): a new radar track takes its tell's weight at once, an established one rises over RISE_S and releases over
RELEASE_S.

Job's open-loop replay of the logged radarTracks through the full radard and the 7.0 planner (rebuilt replay; its
base under-brakes the logged taps by 0.09/0.12): route 34's tap -1.82 -> -0.19 (the brake never starts; 0.6 gave
-0.75), route 37's -1.73 -> -0.64 (1.0 on the camera-passed tell gave -0.60 at more cost on the ambiguous route 37
T323, so it stays 0.6; the far ramp from 1.25 leaves T323 alone and took b1 seg14's -1.07 to +0.11, every other
event within 0.15, 2026-11-08). The 19 real brakes (the four far ones, ev19, route 37's six slowdowns and T323, three
turn-offs) keep their minimum within 0.04 and their onset. Replay evidence only, open loop; no road evidence yet.
"""
from __future__ import annotations

import math
from typing import Any

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_reversal_bound import WITNESS_PROB, urgent

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
RISE_S = 0.25
RELEASE_S = 1.0
SLEW_W = max(UNCONFIRMED_W, DISTANCE_FAR_W)  # rise and release rates are this weight per RISE_S / RELEASE_S


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


class WeakLeadBound:
  """Per lead index weight for the published Bosch-A leads. Call `update` once per radard cycle, before the bound."""
  def __init__(self, dt: float = DT_MDL):
    self.dt = dt
    self.track_ids = [-1, -1]
    self.weights = [0.0, 0.0]

  def update(self, output: list[dict[str, Any]], object_statuses, distance_ratios, lead_probs,
             contradictions=(0.0, 0.0), urgent_v_rels=(None, None)) -> list[float]:
    rise = SLEW_W * self.dt / RISE_S
    release = SLEW_W * self.dt / RELEASE_S
    for index, lead in enumerate(output):
      track_id = int(lead.get('radarTrackId', -1)) if lead.get('present', False) and lead.get('radar', False) else -1
      if track_id < 0 or float(lead_probs[index]) < WITNESS_PROB or urgent(lead, urgent_v_rels[index]):
        weight = 0.0
      else:
        target = tell_weight(object_statuses[index], distance_ratios[index], contradictions[index])
        if track_id != self.track_ids[index]:
          weight = target
        else:
          previous = self.weights[index]
          weight = min(max(target, previous - release), previous + rise)
      self.track_ids[index] = track_id
      self.weights[index] = weight
    return list(self.weights)
