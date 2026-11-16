"""Bosch-A: start braking earlier, and gentler, when a confident camera sees the radar lead slower than the radar does.

Peter's labels on seven hard brakes (2026-10-28, qcamera video): six were real cars that braked late, then hard. On the
car's own logs (Job, radarState / modelV2 / longitudinalPlan) the camera lead saw the slowdown first every time:
  2f8 T1365.04: radar had the lead from 129 m, but vRel read -2..-3 while the model lead's speed fell 19.5 -> 11.9 m/s
    at 88 m; radar vRel only reached -7.8 at T-1 (64 m). Plan -3.50.
  309 T446.66: the lead moved right and revealed a stopped car; radar track 45 read vRel -3.0 at 60 m while the model
    lead read 3-6.5 m/s; vRel reached -10 only at T+0.5. Plan -3.45.
  2f8 T266.33/268.64: a car merging in and stopping; the model lead's speed fell 18 -> 2.8 m/s before radar vRel did.
    Plan -3.28.
  The planner follows the radar lead, so its brake starts when the radar's speed catches up, 1.5-3 s late.

So while a confident camera lead sits at the radar lead's range and reads it at least CAM_SLOW_DV slower for
CAM_SLOW_HOLD_S, the published vLead/vLeadK/vRel move a weight w toward the camera speed, by at most CAM_SLOW_DV_MAX.
w ramps in at CAM_SLOW_RAMP_IN per second and out at CAM_SLOW_RAMP_OUT, so the change itself is no step.
It only ever makes the lead slower (more braking, sooner), never faster. dRel, aLeadK and the point are untouched
(D-041/D-042). Under CAM_SLOW_MIN_D the radar's own speed is trusted as is.

The opposite direction (radar slower than the camera, D-048 gate item 1) was shelved: far young radar tracks read
slower than the camera on 22.8 % of frames. This side's false-trigger cost, a camera speed that reads a steady lead
too slow, is an early gentle slowdown; how often that happens is measured in replay before this ships.
"""
from __future__ import annotations

from typing import Any

from openpilot.common.realtime import DT_MDL

RADAR_TO_CAMERA = 1.52
CAM_SLOW_PROB = 0.9          # filtered model lead prob (D-105 CamABound uses the same confidence)
CAM_SLOW_RANGE_FRAC = 0.1    # same object: |dRel - camera range| <= max(CAM_SLOW_RANGE_M, frac * dRel) (D-105)
CAM_SLOW_RANGE_M = 8.0       # was max(10 m, 20 %). Census 2026-10-30 (Job, open loop, 16 CSB movers): 2f8 T1365 matched
                             # within 0.9 m and is kept; 30a T424 (-2.16 -> -2.75, the camera lead a different car
                             # 10.4 m past the radar's) and 311 T2873 (2.3 s early, nothing close in lane) are dropped.
                             # Also dropped: two real ones (09 T355 cut-in, 31 T317), which go back to the radar-only
                             # brake. Kept: 237 T1186 (cones, 9.5 m apart at 95 m).
CAM_SLOW_DV = 2.0            # camera speed at least this far below radar vLead (m/s)
CAM_SLOW_HOLD_S = 0.5        # for this long before w starts to rise
CAM_SLOW_W_MAX = 0.8         # never all the way to the camera speed (0.5 gave 2f8 T1365.04 min -2.86, 0.8 -2.73, replay)
CAM_SLOW_DV_MAX = 4.0        # never more than this off the radar vLead (m/s)
CAM_SLOW_RAMP_IN = 2.0       # w per second (0.4 s to W_MAX; the dv itself is still capped at CAM_SLOW_DV_MAX)
CAM_SLOW_RAMP_OUT = 1.0
CAM_SLOW_MIN_D = 20.0        # radar range below this: radar speed as is
CAM_SLOW_MIN_V_EGO = 5.0     # stop-and-go is left to the stop laws


class CameraSlowBound:
  """Per-lead-index camera-slower weight over the published Bosch-A leads. Call `apply` once per radard cycle."""
  def __init__(self, dt: float = DT_MDL):
    self.dt = dt
    self.slow_s = [0.0, 0.0]     # how long the camera has read this lead slower
    self.weights = [0.0, 0.0]    # current weight per lead index, for replay/debug
    self.track_ids = [-1, -1]
    self.last_gap = [0.0, 0.0]   # held while w ramps out after the camera drops, so the release is no step

  def _witness_v(self, lead: dict[str, Any], vision, v_ego: float, model_v_ego: float, lead_prob: float) -> float | None:
    d_rel = float(lead['dRel'])
    if lead_prob < CAM_SLOW_PROB or v_ego < CAM_SLOW_MIN_V_EGO or d_rel < CAM_SLOW_MIN_D:
      return None
    camera_d = float(vision.x[0]) - RADAR_TO_CAMERA
    if abs(d_rel - camera_d) > max(CAM_SLOW_RANGE_M, CAM_SLOW_RANGE_FRAC * d_rel):
      return None
    return v_ego + (float(vision.v[0]) - model_v_ego)

  def apply(self, output: list[dict[str, Any]], model_leads, v_ego: float, model_v_ego: float,
            lead_probs) -> list[dict[str, Any]]:
    bounded = []
    for index, lead in enumerate(output):
      radar_lead = lead.get('present', False) and lead.get('radar', False)
      track_id = int(lead.get('radarTrackId', -1)) if radar_lead else -1
      if track_id != self.track_ids[index]:
        self.track_ids[index] = track_id
        self.slow_s[index] = 0.0
        self.weights[index] = 0.0
        self.last_gap[index] = 0.0
      vision_v = self._witness_v(lead, model_leads[index], v_ego, model_v_ego, float(lead_probs[index])) if radar_lead else None
      gap = float(lead['vLead']) - vision_v if vision_v is not None else 0.0
      # leaky: a one-frame dip under CAM_SLOW_DV (2f8 T1365.04 flickered 2.3 -> 1.9 -> 6.7) costs one frame, not the hold
      if gap >= CAM_SLOW_DV:
        self.slow_s[index] = min(self.slow_s[index] + self.dt, CAM_SLOW_HOLD_S)   # capped: a lost camera releases at once
      else:
        self.slow_s[index] = max(self.slow_s[index] - self.dt, 0.0)
      if vision_v is not None:
        self.last_gap[index] = max(gap, 0.0)
      gap = self.last_gap[index]
      if self.slow_s[index] >= CAM_SLOW_HOLD_S:
        self.weights[index] = min(self.weights[index] + CAM_SLOW_RAMP_IN * self.dt, CAM_SLOW_W_MAX)
      else:
        self.weights[index] = max(self.weights[index] - CAM_SLOW_RAMP_OUT * self.dt, 0.0)
      if radar_lead and self.weights[index] > 0.0 and gap > 0.0:
        dv = min(self.weights[index] * gap, CAM_SLOW_DV_MAX)
        lead = dict(lead)
        lead['vLead'] = float(lead['vLead']) - dv
        lead['vLeadK'] = float(lead['vLeadK']) - dv
        lead['vRel'] = float(lead['vRel']) - dv
      bounded.append(lead)
    return bounded
