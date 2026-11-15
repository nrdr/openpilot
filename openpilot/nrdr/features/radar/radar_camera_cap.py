"""Bosch-A: a far radar lead may close no faster than a confident, self-consistent camera lead at its range says.

Far phantom brakes left after the weak-lead and reversal bounds (2026-11-08, Bob, replay at 93b5b5c9d7, Peter's stills):
  000000b0 seg17 ~17:05-17:13: radar track 53 at 60-80 m read vRel well below the model lead, which held its range
    (range slope within CAMERA_SELF_TOL of its own closing speed, a > -0.5). Phantom on the stills. The radar's own
    range slope agreed with its doppler at onset (-4.4..-5.4 vs -4.9), so no radar-only tell separates it: the
    contradiction bound (radar_lead_bound) needs STATUS 9 and the camera-passed tell needs the camera past the radar.
  0000008a seg2 and 00000071 seg12: the same shape; Peter: no car cutting in, phantoms.
Gating on where the camera lead sits against the radar's (at or past it, or no more than 5 m past) was tried in
replay and dropped: route 71 (gap/dRel 0.15-0.32) and b0 17:13 (up to 0.17) overlap, and either gate lost one of them.

So while a radar lead is at least CAP_MIN_D away, a camera lead with filtered prob >= CAP_PROB sits within
CAP_RANGE_FRAC of its range, its range slope matches its own closing speed within CAMERA_SELF_TOL, it slows no harder
than CAMERA_DECEL_MIN, and it closes more than CAP_GAP_MIN slower than the radar's vRel, the published vLead/vLeadK/vRel
are raised to the camera's closing speed. Only ever less braking, toward a camera that calls for none; never past the
camera. While the cap is active, aLeadK is also lifted toward the camera lead's a (floored at CAMERA_DECEL_MIN), never
lowered. dRel and the point are untouched (D-041/D-042). The added dv slews at CAP_DV_RATE and the aLeadK lift at
CAP_DA_RATE, in and out (no step); both restart at 0 on a new track. Runs after CameraSlowBound, which only ever makes
a lead slower.

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

Mode (C-012): VA (above) or D+E (`hold=True`). Testing latches it from its BoschACameraCapHold toggle (default on); nrdr has no
Bosch-A toggles, so BoschALeadPolicy always constructs it with hold=True and VA is reachable only by constructing CameraCap directly
(the tests do). D+E adds a
limited, tapered hold: the gap floor is dropped, and while the gap is at or below CAP_GAP_MIN but above CAP_GAP_HOLD with
dv > 0, a target of gap * (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD) holds for at most CAP_HOLD_T seconds in total
per engagement (hold_t is reset on a new track and whenever dv <= 0, deliberately not when the gap re-crosses CAP_GAP_MIN).
"""
from __future__ import annotations

import math
from typing import Any

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_lead_bound import CAMERA_DECEL_MIN, CAMERA_SELF_TOL, range_slope

RADAR_TO_CAMERA = 1.52
CAP_MIN_D = 50.0       # m; far leads only (b0 track 53 at 60-80 m). Nearer, the radar's speed stands.
CAP_PROB = 0.9         # filtered model lead prob (CameraSlowBound's witness level)
CAP_RANGE_FRAC = 0.3   # camera range within this fraction of dRel (b0 17:05: 70 vs 79 m)
CAP_GAP_MIN = 3.0      # m/s; the camera must close this much slower than the radar's vRel
CAP_DV_RATE = 8.0      # m/s per second, in and out (the replay above ran at 8)
CAP_GAP_HOLD = 1.0     # m/s; D+E: no hold at or below this gap, and the taper reaches 0 here
CAP_HOLD_T = 1.0       # s; D+E: total hold time per engagement
CAP_DA_RATE = 10.0     # m/s^2 per second for the aLeadK lift, in and out (variant A replay ran at 10)


class CameraCap:
  """Per lead index camera cap over the published Bosch-A leads. Call `apply` once per radard cycle."""
  def __init__(self, dt: float = DT_MDL, hold: bool = False):
    self.dt = dt
    self.hold = bool(hold)
    self.hold_t = [0.0, 0.0]
    self.dv = [0.0, 0.0]
    self.da = [0.0, 0.0]
    self.track_ids = [-1, -1]

  @staticmethod
  def _target(lead: dict[str, Any], model_lead, camera_ranges, model_v_ego: float, lead_prob: float,
              gap_min: float = CAP_GAP_MIN) -> float:
    d_rel = float(lead['dRel'])
    if lead_prob < CAP_PROB or d_rel < CAP_MIN_D:
      return 0.0
    if abs(d_rel - (float(model_lead.x[0]) - RADAR_TO_CAMERA)) > CAP_RANGE_FRAC * d_rel:
      return 0.0
    camera_v_rel = float(model_lead.v[0]) - model_v_ego
    camera_slope = range_slope(camera_ranges)
    if math.isnan(camera_slope) or abs(camera_slope - camera_v_rel) > CAMERA_SELF_TOL or float(model_lead.a[0]) < CAMERA_DECEL_MIN:
      return 0.0
    gap = camera_v_rel - float(lead['vRel'])
    return gap if gap > gap_min else 0.0

  def apply(self, output: list[dict[str, Any]], model_leads, model_v_ego: float, lead_probs, tracks,
            camera_ranges) -> list[dict[str, Any]]:
    step = CAP_DV_RATE * self.dt
    step_a = CAP_DA_RATE * self.dt
    capped = []
    for index, lead in enumerate(output):
      radar_lead = lead.get('present', False) and lead.get('radar', False)
      track_id = int(lead.get('radarTrackId', -1)) if radar_lead else -1
      if track_id != self.track_ids[index]:
        self.track_ids[index] = track_id
        self.dv[index] = 0.0
        self.da[index] = 0.0
        self.hold_t[index] = 0.0
      target = 0.0
      if radar_lead and track_id in tracks:
        if not self.hold:
          target = self._target(lead, model_leads[index], camera_ranges[index], model_v_ego, float(lead_probs[index]))
        else:
          gap = self._target(lead, model_leads[index], camera_ranges[index], model_v_ego, float(lead_probs[index]),
                             gap_min=-math.inf)
          if gap > CAP_GAP_MIN:
            target = gap
          elif self.dv[index] > 0.0 and gap > CAP_GAP_HOLD and self.hold_t[index] < CAP_HOLD_T:
            self.hold_t[index] += self.dt
            target = gap * (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD)
      self.dv[index] = min(max(target, self.dv[index] - step), self.dv[index] + step)
      if self.dv[index] <= 0.0:
        self.hold_t[index] = 0.0
      a_target = 0.0
      if target > 0.0:
        a_target = max(0.0, max(float(model_leads[index].a[0]), CAMERA_DECEL_MIN) - float(lead['aLeadK']))
      self.da[index] = min(max(a_target, self.da[index] - step_a), self.da[index] + step_a)
      if radar_lead and (self.dv[index] > 0.0 or self.da[index] > 0.0):
        lead = dict(lead)
        for key in ('vLead', 'vLeadK', 'vRel'):
          lead[key] = float(lead[key]) + self.dv[index]
        lead['aLeadK'] = float(lead['aLeadK']) + self.da[index]
      capped.append(lead)
    return capped
