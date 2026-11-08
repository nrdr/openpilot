"""Bosch-A: after a radar lead's accel reverses from hard positive to hard negative, bound its braking authority.

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

`apply` also takes per-lead floor weights from other tells (radar_lead_bound.WeakLeadBound); a lead is blended once,
at the larger of the two weights, under the same witness and urgency rules.
"""
from __future__ import annotations

import math
from typing import Any

from openpilot.common.realtime import DT_MDL

REVERSAL_HIGH = 2.0       # aLeadK above this arms a track (m/s^2)
REVERSAL_LOW = -2.0       # aLeadK below this within REVERSAL_WINDOW_S of an arm latches it
REVERSAL_WINDOW_S = 1.5
LATCH_S = 4.0             # route 30: the brake came ~1.5 s after the reversal and lasted ~2 s
W = 0.6                   # never all the way to the model lead (D-042)
URGENT_D = 30.0           # radar range below this: no bound
URGENT_TTC = 4.0          # radar TTC below this: no bound
WITNESS_PROB = 0.35       # filtered model lead prob for the model lead to count as a witness (= lead_detection_probability)


def urgent(lead: dict[str, Any]) -> bool:
  d_rel = float(lead['dRel'])
  closing = max(-float(lead['vRel']), 0.0)
  return d_rel < URGENT_D or (closing > 0.1 and d_rel / closing < URGENT_TTC)


class ReversalBound:
  """Per-track reversal latch over the published Bosch-A leads. Call `apply` once per radard cycle."""
  def __init__(self, dt: float = DT_MDL):
    self.dt = dt
    self.t = 0.0
    self.armed_t: dict[int, float] = {}    # last time aLeadK was above REVERSAL_HIGH, per track
    self.latched_until: dict[int, float] = {}
    self.weights = [0.0, 0.0]              # last applied weight per lead index, for replay/debug

  def _observe(self, track_id: int, a_lead: float) -> None:
    if a_lead > REVERSAL_HIGH:
      self.armed_t[track_id] = self.t
    elif a_lead < REVERSAL_LOW:
      armed = self.armed_t.get(track_id)
      if armed is not None and self.t - armed <= REVERSAL_WINDOW_S:
        self.latched_until[track_id] = self.t + LATCH_S

  def latched(self, track_id: int) -> bool:
    return self.latched_until.get(track_id, -math.inf) >= self.t

  def _bound(self, lead: dict[str, Any], vision, v_ego: float, model_v_ego: float, lead_prob: float,
             weight: float = W) -> tuple[dict[str, Any], float]:
    if weight <= 0.0 or lead_prob < WITNESS_PROB or urgent(lead):
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

  def apply(self, output: list[dict[str, Any]], model_leads, v_ego: float, model_v_ego: float, lead_probs, track_ids,
            floor_weights=(0.0, 0.0)) -> list[dict[str, Any]]:
    self.t += self.dt
    seen = set()
    for lead in output:
      if lead.get('present', False) and lead.get('radar', False):
        track_id = int(lead.get('radarTrackId', -1))
        if track_id >= 0 and track_id not in seen:
          seen.add(track_id)
          self._observe(track_id, float(lead['aLeadK']))
    for track_id in [i for i in self.armed_t if i not in track_ids]:
      del self.armed_t[track_id]
    for track_id in [i for i in self.latched_until if i not in track_ids or self.latched_until[i] < self.t]:
      del self.latched_until[track_id]

    bounded = []
    for index, lead in enumerate(output):
      self.weights[index] = 0.0
      if lead.get('present', False) and lead.get('radar', False):
        weight = max(W if self.latched(int(lead.get('radarTrackId', -1))) else 0.0, float(floor_weights[index]))
        lead, self.weights[index] = self._bound(lead, model_leads[index], v_ego, model_v_ego, float(lead_probs[index]), weight)
      bounded.append(lead)
    return bounded
