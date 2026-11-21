"""Camera witness (static): the three tells (reversal latch, weak lead, camera cap), their shared veto, slew and blend, and
the STATUS carrier. Ported from test_radar_reversal_bound, test_radar_camera_cap and test_radar_lead_bound. Shapes: route 30
T1420-1425 (track 60, reversal), route 34 T479 (STATUS 9 and a contradicting camera range), 2ed T338.6 (a real truck the
camera saw late), route 37 T903 (the model lead moved on past the radar lead), b0 seg17 track 53 (cap: radar 70 m closing at
5 m/s, the camera lead at the same range holding it, closing ~0.5 m/s, a 0, range slope matching)."""
import math
import random
from collections import deque
from types import SimpleNamespace

import pytest

from openpilot.cereal import messaging
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar import radar_point_status
from openpilot.nrdr.tests.radar_replay import ReplaySubMaster, bosch_a_radard, card_publish, one_point
from openpilot.nrdr.features.radar.bosch_a_lead_policy import URGENT_LAST_DIRECT_S, urgency_v_rel
from openpilot.nrdr.features.radar.radar_camera_witness import (CAMERA_CLOSING_MAX, CAMERA_DECEL_MIN, CAMERA_SELF_TOL,
                                                               CAP_DA_RATE, CAP_DV_RATE, CAP_GAP_HOLD, CAP_GAP_MIN, CAP_HOLD_T, CAP_MIN_D, CAP_PROB,
                                                               CONTRADICTION_FULL, CONTRADICTION_START, DISTANCE_FAR_W,
                                                               DISTANCE_W, LATCH_S, RADAR_TO_CAMERA, RELEASE_S, RISE_S,
                                                               REVERSAL_WINDOW_S, SLEW_W, TREND_MIN_SAMPLES, TREND_MIN_SPAN_S,
                                                               TREND_SAMPLES, UNCONFIRMED_W, W, CameraWitness,
                                                               camera_contradiction, camera_passed_ratio, range_slope,
                                                               tell_weight, urgent)

V_EGO = 22.0
CAP_V_EGO = 25.0
TID = 53
ABSENT = {'present': False}
RISE = SLEW_W * DT_MDL / RISE_S
RELEASE = SLEW_W * DT_MDL / RELEASE_S


def radar_lead(tid, d, v, a, v_ego=V_EGO):
  return {'dRel': d, 'yRel': 0.0, 'vRel': v - v_ego, 'vLead': v, 'vLeadK': v, 'aLeadK': a, 'aLeadTau': 0.6,
          'present': True, 'modelProb': 0.95, 'radar': True, 'radarTrackId': tid}


def vision(v=21.5, a=0.0, d=50.0):
  return SimpleNamespace(x=[d], v=[v], a=[a])


def no_ranges():
  return [deque(), deque()]


def witness(cw, leads, models, v_ego=V_EGO, probs=(0.95, 0.0), tracks=None, statuses=(0, 0), ratios=(0.0, 0.0),
            contradictions=(0.0, 0.0), ranges=None, urgent_v_rels=(None, None)):
  if tracks is None:
    tracks = {lead['radarTrackId']: None for lead in leads if lead.get('radar')}
  return cw.apply(list(leads), list(models), v_ego, v_ego, list(probs), tracks, list(statuses), list(ratios),
                  list(contradictions), ranges or no_ranges(), urgent_v_rels)


def step(cw, lead, model=None, prob=0.95, tracks=None, **kw):
  return witness(cw, [lead, ABSENT], [model or vision(), vision()], probs=(prob, 0.0), tracks=tracks, **kw)[0]


def frames(seconds):
  return int(round(seconds / DT_MDL))


def reverse(cw, tid=60, gap_s=1.0, first=4.0, second=-3.0, d=45.0):
  step(cw, radar_lead(tid, d, 27.6, first))
  for _ in range(frames(gap_s) - 1):
    step(cw, radar_lead(tid, d, 24.0, 0.0))
  return step(cw, radar_lead(tid, d, 20.0, second))


def settle(cw, lead, model=None, count=None, **kw):
  """Step an established track until its weight has risen to the target (RISE_S plus a margin)."""
  out = None
  for _ in range(count or frames(RISE_S) + 2):
    out = step(cw, lead, model, **kw)
  return out


# ---- reversal tell (was test_radar_reversal_bound) ----
def test_route_30_shape_is_softened_not_dropped():
  cw = CameraWitness()
  reverse(cw)
  raw = radar_lead(60, 39.0, 15.7, -3.0)
  out = settle(cw, raw, vision(21.5, 0.0))
  assert out['present'] and out['radar'] and out['radarTrackId'] == 60
  assert out['dRel'] == raw['dRel']
  assert out['vLead'] == pytest.approx(15.7 + W * (21.5 - 15.7))
  assert out['vLeadK'] == pytest.approx(out['vLead'])
  assert out['vRel'] == pytest.approx(out['vLead'] - V_EGO)
  assert out['aLeadK'] == pytest.approx(-3.0 + W * 3.0)
  assert cw.weights[0] == pytest.approx(W)
  assert cw.tell_weights['reversal'][0] == W
  assert raw['vLead'] == 15.7  # input not mutated


def test_reversal_latch_applies_w_at_once_without_slew():
  # CHANGED (two stages): the reversal tell is not slewed; the weak tell's slew state stays 0
  cw = CameraWitness()
  reverse(cw)
  assert cw.tell_weights['reversal'][0] == W and cw.slewed[0] == 0.0 and cw.weights[0] == W
  out = step(cw, radar_lead(60, 39.0, 15.7, -3.0), vision(21.5, 0.0))
  assert out['vLead'] == pytest.approx(15.7 + W * (21.5 - 15.7))


def test_negative_then_positive_order_does_not_latch():
  cw = CameraWitness()
  reverse(cw, first=-3.0, second=4.0)
  raw = radar_lead(60, 45.0, 15.7, -1.5)  # still braking, but not past REVERSAL_LOW again
  assert step(cw, raw) == raw


def test_reversal_slower_than_window_does_not_latch():
  cw = CameraWitness()
  reverse(cw, gap_s=REVERSAL_WINDOW_S + 0.2)
  raw = radar_lead(60, 45.0, 15.7, -3.0)
  assert step(cw, raw) == raw


def test_urgent_range_or_ttc_keeps_full_authority():
  cw = CameraWitness()
  reverse(cw)
  close = radar_lead(60, 29.0, 15.7, -3.0)
  assert step(cw, close) == close
  short_ttc = radar_lead(60, 40.0, V_EGO - 11.0, -3.0)  # 11 m/s closing, TTC 3.6 s
  assert step(cw, short_ttc) == short_ttc


def test_only_moves_toward_less_severe():
  cw = CameraWitness()
  reverse(cw)
  raw = radar_lead(60, 45.0, 21.0, -0.5)
  out = step(cw, raw, vision(15.0, -2.5))  # vision more severe than radar: untouched
  assert out == raw
  assert cw.weights[0] == 0.0


def test_latch_expires():
  # CHANGED (two stages): the reversal weight drops to 0 on the frame the latch ends (no release tail)
  cw = CameraWitness()
  reverse(cw)
  for _ in range(frames(LATCH_S) - 2):
    out = step(cw, radar_lead(60, 45.0, 18.0, -1.0))
  assert out['vLead'] > 18.0
  for _ in range(4):
    previous = cw.tell_weights['reversal'][0]
    out = step(cw, radar_lead(60, 45.0, 18.0, -1.0))
    if cw.tell_weights['reversal'][0] == 0.0:
      break
  assert previous == W and cw.tell_weights['reversal'][0] == 0.0
  assert out['vLead'] == 18.0 and cw.weights[0] == 0.0


def test_retrigger_extends_latch():
  cw = CameraWitness()
  reverse(cw)
  for _ in range(frames(2.0)):
    step(cw, radar_lead(60, 45.0, 22.0, 0.0))
  reverse(cw)
  for _ in range(frames(3.0)):
    out = step(cw, radar_lead(60, 45.0, 18.0, -1.0))
  assert out['vLead'] > 18.0


def test_weak_model_lead_is_not_a_witness():
  cw = CameraWitness()
  reverse(cw)
  raw = radar_lead(60, 45.0, 15.7, -3.0)
  assert step(cw, raw, prob=0.2) == raw


def test_other_track_not_affected():
  cw = CameraWitness()
  reverse(cw, tid=60)
  raw = radar_lead(61, 45.0, 15.7, -3.0)
  assert step(cw, raw, tracks={60: None, 61: None}) == raw


def test_vision_only_and_absent_leads_pass_through():
  cw = CameraWitness()
  reverse(cw)
  vision_lead = {'present': True, 'radar': False, 'radarTrackId': -1, 'dRel': 45.0, 'vRel': -6.0,
                 'vLead': 16.0, 'vLeadK': 16.0, 'aLeadK': -3.0}
  out = witness(cw, [vision_lead, ABSENT], [vision(), vision()], probs=(0.95, 0.95), tracks={60: None})
  assert out[0] is vision_lead and out[1] is ABSENT


def test_vanished_track_state_is_pruned():
  cw = CameraWitness()
  reverse(cw)
  witness(cw, [ABSENT, ABSENT], [vision(), vision()], probs=(0.0, 0.0), tracks={})
  assert cw.armed_t == {} and cw.latched_until == {}


# ---- cap tell (was test_radar_camera_cap) ----
def cap_lead(tid=TID, d=70.0, v_rel=-5.0, a=-0.4):
  return radar_lead(tid, d, CAP_V_EGO + v_rel, a, v_ego=CAP_V_EGO)


def cap_vision(d=70.0, v_rel=-0.5, a=0.0):
  return SimpleNamespace(x=[d + RADAR_TO_CAMERA], v=[CAP_V_EGO + v_rel], a=[a])


def ranges(d=70.0, slope=-0.5):
  return deque([d + RADAR_TO_CAMERA + slope * (i - (TREND_SAMPLES - 1)) * DT_MDL for i in range(TREND_SAMPLES)],
               maxlen=TREND_SAMPLES)


CAP_TRACKS = {TID: object(), 54: object()}


def cstep(cw, lead=None, model=None, prob=0.95, camera=None, tracks=CAP_TRACKS, urgent_v_rel=None):
  return witness(cw, [lead or cap_lead(), ABSENT], [model or cap_vision(), cap_vision()], v_ego=CAP_V_EGO,
                 probs=(prob, 0.0), tracks=tracks, ranges=[camera if camera is not None else ranges(), deque()],
                 urgent_v_rels=(urgent_v_rel, None))[0]


def crun(cw, count, **kw):
  out = None
  for _ in range(count):
    out = cstep(cw, **kw)
  return out


DV_STEP = CAP_DV_RATE * DT_MDL
DA_STEP = CAP_DA_RATE * DT_MDL


def test_cap_new_track_applies_weight_one_in_the_first_cycle():
  # CHANGED (growth limit): the weight is 1 in the first cycle but the correction starts from 0 at CAP_DV_RATE * DT_MDL
  # (as the old cap did); it was vRel -0.5 in the first cycle with the weight slew alone
  cw = CameraWitness()
  out = cstep(cw)
  assert cw.tell_weights['cap'][0] == 1.0 and cw.weights[0] == 1.0
  assert out['vRel'] == pytest.approx(-5.0 + DV_STEP)
  assert out['vLead'] == pytest.approx(CAP_V_EGO - 5.0 + DV_STEP)
  assert out['vLeadK'] == pytest.approx(CAP_V_EGO - 5.0 + DV_STEP)
  assert out['dRel'] == 70.0 and out['aLeadK'] == pytest.approx(0.0)   # the 0.4 lift is under DA_STEP
  out = crun(cw, 20)
  assert out['vRel'] == pytest.approx(-0.5)


def test_cap_lifts_aleadk_never_lowers():
  # CHANGED (growth limit): the first cycle lifts CAP_DA_RATE * DT_MDL of the lift, then it grows at that rate
  out = cstep(CameraWitness(), lead=cap_lead(a=-2.0))
  assert out['aLeadK'] == pytest.approx(-2.0 + DA_STEP)
  out = crun(CameraWitness(), 20, lead=cap_lead(a=-2.0))
  assert out['aLeadK'] == pytest.approx(0.0)
  out = crun(CameraWitness(), 20, model=cap_vision(a=-0.3))
  assert out['aLeadK'] == pytest.approx(-0.3)
  out = crun(CameraWitness(), 20, lead=cap_lead(a=0.5))   # radar lead already accelerating harder: untouched
  assert out['aLeadK'] == 0.5


def test_cap_releases_slewed_when_camera_drops_and_at_once_when_vetoed():
  # CHANGED: the release is the faster of the shared RELEASE_S slew and the CAP_DV_RATE fall (2026-11-11); prob below
  # WITNESS_PROB is a veto
  cw = CameraWitness()
  crun(cw, 20)
  out = cstep(cw, prob=CAP_PROB - 0.01)
  assert out['vRel'] == pytest.approx(-5.0 + min((1.0 - RELEASE) * 4.5, 4.5 - DV_STEP))
  out = crun(cw, frames(RELEASE_S), prob=CAP_PROB - 0.01)
  assert out['vRel'] == pytest.approx(-5.0)
  crun(cw, 20)
  out = cstep(cw, prob=0.0)
  assert out['vRel'] == pytest.approx(-5.0)


def test_cap_new_track_takes_weight_at_once_but_correction_starts_from_zero():
  # CHANGED (growth limit): the weight is taken at once but the correction restarts at 0 (as test_new_track_restarts_at_zero)
  cw = CameraWitness()
  crun(cw, 20)
  out = cstep(cw, lead=cap_lead(tid=54))
  assert cw.weights[0] == 1.0 and cw.cap_dv[0] == pytest.approx(DV_STEP)
  assert out['vRel'] == pytest.approx(-5.0 + DV_STEP)
  out = crun(cw, 20, lead=cap_lead(tid=54))
  assert out['vRel'] == pytest.approx(-0.5)


def test_cap_vetoed_when_the_lead_is_urgent():
  # NEW: the urgency veto now covers the cap tell. 60 m closing 20 m/s: TTC 3 s
  cw = CameraWitness()
  lead = cap_lead(d=60.0, v_rel=-20.0)
  out = crun(cw, 10, lead=lead, model=cap_vision(d=60.0), camera=ranges(d=60.0))
  assert out == lead and cw.tell_weights['cap'][0] == 0.0 and cw.weights[0] == 0.0
  # the same lead is capped when its direct-reading vRel (the urgency vRel) says it is not closing that fast
  cw = CameraWitness()
  out = cstep(cw, lead=lead, model=cap_vision(d=60.0), camera=ranges(d=60.0), urgent_v_rel=-5.0)
  assert cw.tell_weights['cap'][0] == 1.0 and out['vRel'] == pytest.approx(-20.0 + DV_STEP)   # CHANGED: growth limit
  out = crun(cw, 60, lead=lead, model=cap_vision(d=60.0), camera=ranges(d=60.0), urgent_v_rel=-5.0)
  assert out['vRel'] == pytest.approx(-0.5)
  # and under URGENT_D never
  near = cap_lead(d=29.0)
  assert crun(CameraWitness(), 10, lead=near, model=cap_vision(d=29.0), camera=ranges(d=29.0)) == near


@pytest.mark.parametrize('kw', [
  {'lead': cap_lead(d=CAP_MIN_D - 1.0)},                          # near: radar speed stands
  {'prob': CAP_PROB - 0.01},                                      # unconfident camera
  {'model': cap_vision(d=100.0)},                                 # camera on another object (> 30 % off)
  {'model': cap_vision(a=-1.0)},                                  # camera lead slowing: no witness
  {'camera': ranges(slope=-6.0)},                                 # camera range slope disagrees with its speed
  {'camera': deque([float('nan')] * TREND_SAMPLES)},              # no camera history
  {'model': cap_vision(v_rel=-5.0 + CAP_GAP_MIN - 0.1)},          # gap not over CAP_GAP_MIN
  {'tracks': {}},                                                 # track gone
])
def test_cap_gates_leave_lead_untouched(kw):
  out = crun(CameraWitness(), 10, **kw)
  base = kw.get('lead', cap_lead())
  assert out['vRel'] == base['vRel'] and out['vLead'] == base['vLead']


def test_cap_never_more_braking_and_vision_leads_untouched():
  out = crun(CameraWitness(), 10, model=cap_vision(v_rel=-8.0))   # camera closes faster than radar: no cap
  assert out['vRel'] == -5.0
  vision_lead = dict(cap_lead(), radar=False)
  assert crun(CameraWitness(), 10, lead=vision_lead) == vision_lead


# ---- cap hold (C-012): the only mode, a limited tapered hold ----
def gap_model(gap):
  """Camera lead whose closing speed is `gap` m/s slower than the radar's -5.0 (radar v_rel = -5.0)."""
  return cap_vision(v_rel=-5.0 + gap)


def gap_cam(gap):
  return ranges(slope=-5.0 + gap)


def hstep(cw, gap, lead=None):
  return cstep(cw, lead=lead, model=gap_model(gap), camera=gap_cam(gap))


def hrun(cw, gap, count):
  out = None
  for _ in range(count):
    out = hstep(cw, gap)
  return out


def test_hold_tapers_target_when_gap_drops_5_to_2():
  cw = CameraWitness()
  assert cw.hold_t == [0.0, 0.0]
  hrun(cw, 5.0, 20)
  assert cw.tell_weights['cap'][0] == 1.0
  hrun(cw, 2.0, 20)   # tell = (2 - 1) / (3 - 1) = 0.5 on the gap: the old target gap * 0.5 = 1.0 m/s
  assert cw.tell_weights['cap'][0] == pytest.approx((2.0 - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD))
  out = hrun(CameraWitness(), 5.0, 20)      # CHANGED (growth limit): 20 cycles, the first alone gives only DV_STEP
  assert out['vRel'] == pytest.approx(-5.0 + 5.0)   # gap 5 fully applied
  assert cw.hold_t[0] == pytest.approx(20 * DT_MDL)


def test_hold_ends_after_hold_t():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  hrun(cw, 2.0, round(CAP_HOLD_T / DT_MDL))
  assert cw.tell_weights['cap'][0] == pytest.approx(0.5)
  hrun(cw, 2.0, 40)   # hold exhausted: tell 0, the correction decays at the rate
  assert cw.tell_weights['cap'][0] == 0.0 and cw.cap_dv[0] == 0.0
  assert cw.hold_t[0] == 0.0   # reset once the tell is 0


def test_no_hold_at_or_below_gap_hold():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  hrun(cw, CAP_GAP_HOLD - 0.1, 40)
  assert cw.tell_weights['cap'][0] == 0.0 and cw.cap_dv[0] == 0.0
  assert cw.hold_t[0] == 0.0


def test_hold_t_not_reset_across_recrossing_of_gap_min():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  hrun(cw, 2.0, 10)
  held = cw.hold_t[0]
  assert held == pytest.approx(10 * DT_MDL)
  hrun(cw, 5.0, 3)    # re-crossing 3 with the tell applied
  assert cw.hold_t[0] == pytest.approx(held)
  hrun(cw, 2.0, 5)
  assert cw.hold_t[0] == pytest.approx(held + 5 * DT_MDL)


def test_new_track_resets_hold_t():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  hrun(cw, 2.0, 10)
  assert cw.hold_t[0] > 0.0
  hstep(cw, 5.0, lead=cap_lead(tid=54))
  assert cw.hold_t[0] == 0.0 and cw.tell_weights['cap'][0] == 1.0


def test_new_track_does_not_inherit_a_hold():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  hstep(cw, 2.0, lead=cap_lead(tid=54))   # gap 2 on a track that was never capped: no hold
  assert cw.tell_weights['cap'][0] == 0.0


def test_hold_mode_still_lifts_aleadk_while_holding():
  cw = CameraWitness()
  hrun(cw, 5.0, 20)
  out = hrun(cw, 2.0, 5)
  assert out['aLeadK'] >= -0.4


# ---- weak tell (was test_radar_lead_bound) ----
def test_tell_weight():
  assert tell_weight(9, 0.0) == 0.0         # STATUS 9 alone: 8 % of lead time, under three real brakes
  assert tell_weight(9, 0.0, 5.84) == 0.0   # 2ed T338.6, a real truck the camera saw late, at its peak
  assert tell_weight(9, 0.0, 9.85) == UNCONFIRMED_W  # route 34 at +0.5 s
  assert tell_weight(9, 0.0, (CONTRADICTION_START + CONTRADICTION_FULL) / 2) == pytest.approx(UNCONFIRMED_W / 2)
  assert tell_weight(7, 0.0, 9.9) == 0.0    # confirmed
  assert tell_weight(0, 0.0, 9.9) == 0.0    # status not known
  assert tell_weight(3, 0.0, 9.9) == 0.0    # only 9 counts as unconfirmed
  assert tell_weight(7, 0.62) == 0.0  # the largest ratio among the four real far brakes
  assert tell_weight(0, 0.62) == 0.0
  assert tell_weight(7, 0.875) == pytest.approx(DISTANCE_W / 2)
  assert tell_weight(7, 1.02) == DISTANCE_W  # route 37 at the start of the tap
  assert tell_weight(9, 1.02, 9.9) == max(UNCONFIRMED_W, DISTANCE_W)
  assert tell_weight(7, 0.86) == pytest.approx(0.264, abs=0.01)  # route 37 T323 (ambiguous) at its peak: unchanged
  assert tell_weight(7, 1.25) == DISTANCE_W
  assert tell_weight(7, 1.375) == pytest.approx((DISTANCE_W + DISTANCE_FAR_W) / 2)
  assert tell_weight(7, 1.5) == DISTANCE_FAR_W  # b1 seg14 track 4, the model lead ~110 m past a 57-85 m radar point
  assert tell_weight(7, 1.9) == DISTANCE_FAR_W


def test_range_slope():
  assert range_slope([88.0 - 0.75 * k for k in range(31)]) == pytest.approx(-15.0)
  assert range_slope([88.0 - 0.75 * k if k % 3 else math.nan for k in range(31)]) == pytest.approx(-15.0)
  assert math.isnan(range_slope([60.0] * (TREND_MIN_SAMPLES - 1)))
  assert math.isnan(range_slope([60.0] * round(TREND_MIN_SPAN_S / DT_MDL)))  # 12 samples span 0.55 s
  assert range_slope([60.0] * (round(TREND_MIN_SPAN_S / DT_MDL) + 1)) == 0.0
  assert math.isnan(range_slope([math.nan] * 31))


def test_camera_contradiction():
  # (vRel, the track's range slope, the model lead's range slope, its closing, its a) from the logs at 20 Hz
  # route 34 at 0 s: the radar closes 10-17 m/s, the model lead's range 1.3 m/s, matching its closing of 2.9
  assert camera_contradiction(-10.08, -17.09, -1.26, 2.91, 0.04) == pytest.approx(8.82)
  # 2ed T338.6 at 0 s, a real truck the camera saw late: just under the start
  assert camera_contradiction(-8.06, -10.67, -2.22, 2.31, 0.0) == pytest.approx(5.84)
  # 313 T2330.2 (leans real): vRel -11.3, but the track's own range fell 4.0 m/s, near the camera's 3.1
  assert camera_contradiction(-11.28, -3.99, -3.07, 0.62, -0.02) == pytest.approx(0.92)
  # 368 T657.1 (real, stopped traffic): at +1 s the model lead's range rose 17.3 m/s at closing 8.3, so it had jumped
  # to a farther car and is no witness; at -0.7 s it was slowing at -1.14
  assert camera_contradiction(-9.43, -12.53, 17.28, 8.34, -0.46) == 0.0
  assert camera_contradiction(-11.43, -12.53, 10.52, 5.15, -1.14) == 0.0
  assert camera_contradiction(-10.08, -17.09, -1.26, 1.26 + CAMERA_SELF_TOL + 0.1, 0.04) == 0.0
  assert camera_contradiction(-10.08, -17.09, -1.26, 2.91, CAMERA_DECEL_MIN - 0.01) == 0.0
  assert camera_contradiction(-10.08, math.nan, -1.26, 2.91, 0.04) == 0.0  # a track too young for a slope
  assert camera_contradiction(-10.08, -17.09, math.nan, 2.91, 0.04) == 0.0
  assert camera_contradiction(-3.0, -3.0, -2.0, 2.0, 0.0) == pytest.approx(1.0)
  assert camera_contradiction(-1.0, -3.0, -2.0, 2.0, 0.0) == 0.0  # the camera closes faster than the radar


def test_camera_passed_ratio():
  # route 37 T903: SUV at 45 m, the model lead moved on to 62 m, closing 0.5 m/s, a 0
  assert camera_passed_ratio(45.0, 62.0, 0.5, 0.0) == pytest.approx(17.0 / 15.5)
  assert camera_passed_ratio(45.0, 62.0, CAMERA_CLOSING_MAX, CAMERA_DECEL_MIN) == pytest.approx(17.0 / 15.5)
  # route 37 T273: a pickup slowing to turn left at 82 m, the model lead at 109 m closing at 11.7 m/s: a real slowdown
  assert camera_passed_ratio(81.7, 108.8, 11.7, -0.3) == 0.0
  assert camera_passed_ratio(45.0, 62.0, CAMERA_CLOSING_MAX + 0.1, 0.0) == 0.0  # the model lead calls for braking
  assert camera_passed_ratio(45.0, 62.0, 0.5, CAMERA_DECEL_MIN - 0.1) == 0.0
  assert camera_passed_ratio(36.0, 27.5, 0.0, 0.0) == 0.0  # the model lead is nearer than the radar lead
  assert camera_passed_ratio(16.0, 18.0, 0.0, 0.0) == pytest.approx(0.4)  # the 5 m floor


def update(cw, lead, status=7, ratio=0.0, prob=0.95, contradiction=0.0, **kw):
  """The weak tell's weight after the shared veto, before the slew."""
  step(cw, lead, prob=prob, statuses=(status, 0), ratios=(ratio, 0.0), contradictions=(contradiction, 0.0), **kw)
  return cw.tell_weights['weak'][0]


def slewed(cw, lead, status=7, ratio=0.0, **kw):
  step(cw, lead, statuses=(status, 0), ratios=(ratio, 0.0), **kw)
  return cw.slewed[0]


def test_new_track_takes_its_tell_at_once():
  cw = CameraWitness()
  assert slewed(cw, radar_lead(55, 66.0, 15.0, -3.0), status=9, contradictions=(9.9, 0.0)) == UNCONFIRMED_W
  assert slewed(cw, radar_lead(56, 66.0, 15.0, -3.0), status=7) == 0.0  # and a new confirmed one drops it at once


def test_established_track_rises_and_releases_at_the_slew_rates():
  cw = CameraWitness()
  lead = radar_lead(32, 47.0, 28.7, 0.0)
  assert slewed(cw, lead, ratio=0.5) == 0.0
  assert slewed(cw, lead, ratio=1.1) == pytest.approx(RISE)
  for _ in range(round(RISE_S / DT_MDL)):
    weight = slewed(cw, lead, ratio=1.1)
  assert weight == pytest.approx(DISTANCE_W)
  assert slewed(cw, lead, ratio=0.5) == pytest.approx(DISTANCE_W - RELEASE)
  for _ in range(round(RELEASE_S / DT_MDL)):
    weight = slewed(cw, lead, ratio=0.5)
  assert weight == pytest.approx(0.0, abs=1e-9)


def test_urgent_unwitnessed_and_vision_leads_get_no_weight():
  cw = CameraWitness()
  assert update(cw, radar_lead(55, 29.0, 15.0, -3.0), status=9, contradiction=9.9) == 0.0          # under 30 m
  assert update(cw, radar_lead(55, 66.0, V_EGO - 17.0, -3.0), status=9, contradiction=9.9) == 0.0  # TTC 3.9 s
  assert update(cw, radar_lead(55, 66.0, 15.0, -3.0), status=9, contradiction=9.9, prob=0.2) == 0.0
  vision_lead = {'present': True, 'radar': False, 'radarTrackId': -1, 'dRel': 66.0, 'vRel': -7.0,
                 'vLead': 15.0, 'vLeadK': 15.0, 'aLeadK': -3.0}
  assert update(cw, vision_lead, status=9, contradiction=9.9) == 0.0
  assert cw.weights == [0.0, 0.0]


def test_tells_blend_once_at_the_largest_weight():
  raw = radar_lead(32, 47.0, 24.8, -2.9)  # route 37: vLead dipped to 24.8 while the model lead held 29, a 0
  model = vision(29.0, 0.0)
  weak = DISTANCE_W * 0.5                 # ratio 0.875
  cw = CameraWitness()
  out = step(cw, raw, model, ratios=(0.875, 0.0))
  assert cw.tell_weights == {'reversal': [0.0, 0.0], 'weak': [pytest.approx(weak), 0.0], 'cap': [0.0, 0.0]}
  assert out['vLead'] == pytest.approx(24.8 + weak * (29.0 - 24.8))
  assert out['vRel'] == pytest.approx(out['vLead'] - V_EGO)
  assert out['aLeadK'] == pytest.approx(-2.9 + weak * 2.9)
  assert out['dRel'] == raw['dRel'] and out['present'] and out['radar'] and cw.weights[0] == pytest.approx(weak)
  cw = CameraWitness()
  reverse(cw, tid=32, d=47.0)
  out = settle(cw, raw, model, ratios=(0.875, 0.0))
  assert cw.weights[0] == pytest.approx(W) and out['vLead'] == pytest.approx(24.8 + W * (29.0 - 24.8))  # max, not sum


class FakeSM(dict):
  def __init__(self, events):
    super().__init__({event.which(): getattr(event, event.which()) for event in events})
    self.logMonoTime = {event.which(): event.logMonoTime for event in events}


def companion(stamp, statuses, tracks_stamp=None):
  event = messaging.new_message('carStateSP', valid=True)
  event.logMonoTime = stamp
  radar_point_status.write(event.carStateSP, stamp if tracks_stamp is None else tracks_stamp, statuses)
  return event.as_reader()


def tracks(stamp):
  event = messaging.new_message('radarTracks', valid=True)
  event.logMonoTime = stamp
  return event.as_reader()


def test_point_status_round_trip_and_pairing():
  stamp = 5_000_000_000
  assert radar_point_status.read(FakeSM([tracks(stamp), companion(stamp, {60: 7, 55: 9})])) == {55: 9, 60: 7}
  late = stamp + radar_point_status.PAIR_TOLERANCE_NS + 1
  assert radar_point_status.read(FakeSM([tracks(late), companion(stamp, {55: 9})])) == {}
  assert radar_point_status.read(FakeSM([tracks(stamp), companion(stamp, {55: 9}, tracks_stamp=0)])) == {}
  assert radar_point_status.read(FakeSM([tracks(stamp)])) == {}  # no carrier: other radars, older logs


def test_card_sends_the_statuses_on_car_state_sp_stamped_with_the_tracks_they_describe():
  # nrdr merges the statuses into the one carStateSP per frame (no second carStateSP message); order is unchanged
  card = card_publish({55: 9}, one_point())
  assert [service for service, _ in card.pm.sent] == ['carOutput', 'carStateSP', 'carState', 'radarTracks']
  status_msg = dict(card.pm.sent)['carStateSP']
  tracks_msg = dict(card.pm.sent)['radarTracks']
  assert status_msg.carStateSP.radarTracksMonoTime == tracks_msg.logMonoTime > 0
  assert [(row.trackId, row.objectStatus) for row in status_msg.carStateSP.radarPointStatus] == [(55, 9)]
  assert card.radar_point_status == (tracks_msg.logMonoTime, {55: 9})


def test_card_sends_no_statuses_for_other_radars():
  card = card_publish(None, one_point())
  assert [service for service, _ in card.pm.sent] == ['carOutput', 'carStateSP', 'carState', 'radarTracks']
  status_msg = dict(card.pm.sent)['carStateSP']
  assert status_msg.carStateSP.radarTracksMonoTime == 0 and len(status_msg.carStateSP.radarPointStatus) == 0


def radard_tick(sm, tick, statuses, v_lead=5.4, d_rel=66.0, v_ego=16.0, track_id=55, model_x=None, model_v=13.5):
  stamp = 1_000_000_000 + tick * 50_000_000
  model_event = messaging.new_message('modelV2', valid=True)
  model_event.logMonoTime = stamp
  model_event.modelV2.velocity.x = [v_ego]
  for lead in model_event.modelV2.init('leadsV3', 2):
    lead.x = [d_rel + 1.52 if model_x is None else model_x]
    lead.y = [0.0]
    lead.v = [model_v]
    lead.a = [0.0]
    lead.xStd = lead.yStd = lead.vStd = [1.0]
    lead.prob = 0.99
  car_event = messaging.new_message('carState', valid=True)
  car_event.logMonoTime = stamp
  car_event.carState.vEgo = v_ego
  radar_event = messaging.new_message('radarTracks', valid=True)
  radar_event.logMonoTime = stamp
  point = radar_event.radarTracks.init('points', 1)[0]
  point.trackId = track_id
  point.dRel = d_rel
  point.vRel = v_lead - v_ego
  point.deprecated.measured = True
  events = [model_event.as_reader(), car_event.as_reader(), radar_event.as_reader()]
  if statuses is not None:
    events.append(companion(stamp, statuses))
  sm.update_msgs(stamp / 1e9, events)


def run_radard(statuses, ticks=60, shape=lambda tick: {}):
  sm = ReplaySubMaster(['modelV2', 'carState', 'radarTracks', 'carStateSP'])
  radar = bosch_a_radard()
  for tick in range(ticks):
    radard_tick(sm, tick, statuses, **shape(tick))
    radar.update(sm, sm['radarTracks'])
  return radar


def route_34_shape(camera_range_rate, model_v):
  def shape(tick):
    # track 55 sweeps in at 15 m/s reading vRel -10.6; at the end 50.8 m, TTC 4.8 s, so never urgent
    return {'d_rel': 95.0 - 0.75 * tick, 'model_x': 63.0 + 1.52 + camera_range_rate * tick * DT_MDL, 'model_v': model_v}
  return shape


def test_route_34_shape_through_radard():
  # route 34: the model lead's range holds at 63 m and it reads 13.5 m/s (closing 2.5), a 0
  shape = route_34_shape(0.0, 13.5)
  plain = run_radard(None, shape=shape).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 55
  confirmed = run_radard({55: 7}, shape=shape).radar_state.leadOne
  assert confirmed.to_dict() == plain.to_dict()  # confirmed: as before the carrier
  unconfirmed = run_radard({55: 9}, shape=shape)
  bounded = unconfirmed.radar_state.leadOne
  assert unconfirmed.tracks[55].objectStatus == 9
  assert bounded.radar and bounded.radarTrackId == 55 and bounded.dRel == plain.dRel
  assert bounded.vLead == pytest.approx(plain.vLead + UNCONFIRMED_W * (13.5 - plain.vLead), abs=0.05)


def test_unconfirmed_lead_the_camera_backs_is_not_bounded():
  # a real lead the camera sees late, like 2ed T338.6 (5.84 m/s there): its range falls 5 m/s at closing 3, so the
  # radar's vRel -10.6 runs 5.6 m/s ahead of it, under the start
  shape = route_34_shape(-5.0, 13.0)
  plain = run_radard(None, shape=shape).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 55
  assert run_radard({55: 9}, shape=shape).radar_state.leadOne.to_dict() == plain.to_dict()


def route_37_shape(model_v):
  def shape(tick):
    if tick < 30:  # the SUV ahead at 53 m, matched through the strict gate
      return {'track_id': 32, 'd_rel': 53.0, 'v_lead': 28.6, 'v_ego': 29.8, 'model_x': 53.0 + 1.52, 'model_v': 28.6}
    # it moves out: the radar reads it slowing to 25.3 at 45 m while the model lead moves on to 64 m
    return {'track_id': 32, 'd_rel': 45.0, 'v_lead': 25.3, 'v_ego': 29.8, 'model_x': 64.0 + 1.52, 'model_v': model_v}
  return shape


def test_route_37_shape_through_radard():
  # control: the model lead closing at 11.7 m/s calls for braking itself (route 37 T273's pickup): no bound
  plain = run_radard(None, shape=route_37_shape(18.1)).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 32 and plain.vLead < 26.0
  bounded = run_radard(None, shape=route_37_shape(29.3)).radar_state.leadOne  # route 37 T903: closing 0.5 m/s
  assert bounded.radar and bounded.radarTrackId == 32 and bounded.dRel == plain.dRel
  assert bounded.vLead == pytest.approx(plain.vLead + DISTANCE_W * (29.3 - plain.vLead), abs=0.05)


def test_urgency_uses_the_last_direct_reading_on_an_unmeasured_point():
  # b1 seg14 47.7 s: track 4 at 69 m, last direct reading -11.7, then the parser's floor estimate -31 (TTC 2.2 s)
  floor = radar_lead(4, 69.0, V_EGO - 31.0, -3.0)
  assert urgent(floor) and not urgent(floor, -11.7)
  assert urgent(floor, -17.5)                              # TTC 3.9 s on a fast last reading: still urgent
  assert urgent(radar_lead(4, 29.0, V_EGO - 1.0, -3.0), -1.0)  # under 30 m stays urgent whatever the speed
  hop = [90.0 - 0.75 * k for k in range(31)]               # range falling 15 m/s: a reflector hop, not used
  track = SimpleNamespace(direct=False, last_direct_vrel=-11.7, direct_age=5, range_history=hop)
  assert urgency_v_rel(track) == -11.7                     # the range slope does not override the last reading  # ty: ignore[invalid-argument-type]
  track.direct_age = round(URGENT_LAST_DIRECT_S / DT_MDL) + 1
  assert urgency_v_rel(track) is None                      # too old: the published vRel, as before  # ty: ignore[invalid-argument-type]
  track.direct_age, track.last_direct_vrel = 5, math.nan
  assert urgency_v_rel(track) is None                      # never measured: the published vRel  # ty: ignore[invalid-argument-type]
  track.direct, track.last_direct_vrel = True, -11.7
  assert urgency_v_rel(track) is None                      # a direct reading: the published vRel  # ty: ignore[invalid-argument-type]
  assert urgency_v_rel(None) is None


def test_bounds_keep_their_weight_when_only_the_floor_estimate_is_urgent():
  floor = radar_lead(4, 69.0, V_EGO - 31.0, -3.0)
  cw = CameraWitness()
  assert update(cw, floor, status=9, contradiction=9.9) == 0.0 and cw.weights == [0.0, 0.0]
  cw = CameraWitness()
  assert update(cw, floor, status=9, contradiction=9.9, urgent_v_rels=(-11.7, None)) == UNCONFIRMED_W
  model = vision(21.5, 0.0)
  cw = CameraWitness()
  assert step(cw, floor, model, ratios=(1.0, 0.0)) == floor
  cw = CameraWitness()
  out = step(cw, floor, model, ratios=(1.0, 0.0), urgent_v_rels=(-11.7, None))
  assert cw.weights[0] == pytest.approx(DISTANCE_W) and out['dRel'] == floor['dRel'] and out['present'] and out['radar']
  assert out['vLead'] == pytest.approx(floor['vLead'] + DISTANCE_W * (21.5 - floor['vLead']))


# ---- the unified rule ----
def test_dRel_never_changed_and_no_lead_dropped_over_a_random_sweep():
  rng = random.Random(20261111)
  cw = CameraWitness()
  ids = [-1, -1]
  for _ in range(4000):
    leads, models = [], []
    for index in range(2):
      kind = rng.random()
      if kind < 0.15:
        leads.append({'present': False})
      elif kind < 0.3:
        leads.append({'present': True, 'radar': False, 'radarTrackId': -1, 'dRel': rng.uniform(5, 150),
                      'vRel': rng.uniform(-20, 5), 'vLead': rng.uniform(0, 35), 'vLeadK': 10.0, 'aLeadK': rng.uniform(-3, 4)})
      else:
        if rng.random() < 0.1 or ids[index] < 0:
          ids[index] = rng.randrange(1, 6)
        v_rel = rng.uniform(-20, 5)
        lead = radar_lead(ids[index], rng.uniform(5, 150), 25.0 + v_rel, rng.uniform(-3, 4), v_ego=25.0)
        leads.append(lead)
      models.append(SimpleNamespace(x=[rng.uniform(5, 160)], v=[rng.uniform(0, 35)], a=[rng.uniform(-3, 3)]))
    tracks = {i: None for i in range(1, 6) if rng.random() < 0.9}
    cameras = [deque((rng.uniform(40, 120) if rng.random() < 0.9 else math.nan for _ in range(TREND_SAMPLES)),
                     maxlen=TREND_SAMPLES) for _ in range(2)]
    out = cw.apply([dict(lead) for lead in leads], models, 25.0, 25.0, [rng.random(), rng.random()], tracks,
                   [rng.choice((0, 7, 9)) for _ in range(2)], [rng.uniform(0, 2) for _ in range(2)],
                   [rng.uniform(0, 12) for _ in range(2)], cameras, [rng.choice((None, -rng.uniform(0, 25))) for _ in range(2)])
    assert len(out) == 2
    for before, after in zip(leads, out, strict=True):
      assert after.get('present') == before.get('present')
      if before.get('present'):
        assert after['dRel'] == before['dRel'] and after['radar'] == before['radar']
        assert after['radarTrackId'] == before['radarTrackId']
        for key in ('vLead', 'vLeadK', 'vRel', 'aLeadK'):
          assert after[key] >= before[key]   # only ever less braking
      if not before.get('radar', False):
        assert after == before
    assert all(0.0 <= w <= 1.0 for w in cw.weights)




# ---- cap growth limit (CAP_DV_RATE / CAP_DA_RATE restored 2026-11-11, scorecard ep128) ----
def gstep(cw, v_rel, a=-0.4, cam=-0.5, cam_a=0.0, tid=TID, **kw):
  """One cycle: radar vRel/aLeadK `v_rel`/`a`, a confident camera lead closing at `cam` (range slope matching)."""
  return cstep(cw, lead=cap_lead(tid=tid, v_rel=v_rel, a=a), model=cap_vision(v_rel=cam, a=cam_a),
               camera=ranges(slope=cam), tracks={tid: object()}, **kw)


def test_growth_limit_rise_on_open_gap_follows_the_rate():
  # (a1) an established track whose cap tell rises from 0 with a 4 m/s gap already open: the correction is the
  # rate-limited state, DV_STEP * n = 0.4, 0.8, 1.2 ... (no weight slew on the cap)
  cw = CameraWitness()
  gstep(cw, -0.6, cam=-0.5)                     # established, no tell (gap 0.1)
  assert cw.weights[0] == 0.0 and cw.cap_dv[0] == 0.0
  for n in range(1, 6):
    out = gstep(cw, -4.5, cam=-0.5)
    assert out['vRel'] - -4.5 == pytest.approx(DV_STEP * n)
  out = crun_g(cw, 30, -4.5)
  assert out['vRel'] == pytest.approx(-0.5)


def crun_g(cw, count, v_rel, **kw):
  out = None
  for _ in range(count):
    out = gstep(cw, v_rel, **kw)
  return out


def test_growth_limit_weight_one_gap_step_grows_at_dv_rate():
  # (a2) weight already 1, the radar vRel steps 6 m/s more closing in one frame
  cw = CameraWitness()
  crun_g(cw, 40, -4.5)
  assert cw.tell_weights['cap'][0] == 1.0 and cw.cap_dv[0] == pytest.approx(4.0)
  out = gstep(cw, -10.5)
  assert out['vRel'] == pytest.approx(-10.5 + 4.0 + DV_STEP)      # moves by the step minus all but DV_STEP of new correction
  for n in range(2, 6):
    out = gstep(cw, -10.5)
    assert out['vRel'] == pytest.approx(-10.5 + 4.0 + DV_STEP * n)
  out = crun_g(cw, 40, -10.5)
  assert out['vRel'] == pytest.approx(-0.5) and cw.cap_dv[0] == pytest.approx(10.0)


def test_growth_limit_aleadk_grows_at_da_rate():
  # (b) the aLeadK lift: radar aLeadK steps from -0.4 to -3.0 with weight 1 and the lift already applied
  cw = CameraWitness()
  crun_g(cw, 40, -4.5, a=-0.4)
  assert cw.cap_da[0] == pytest.approx(0.4)
  out = gstep(cw, -4.5, a=-3.0)
  assert out['aLeadK'] == pytest.approx(-3.0 + 0.4 + DA_STEP)
  for n in range(2, 5):
    out = gstep(cw, -4.5, a=-3.0)
    assert out['aLeadK'] == pytest.approx(-3.0 + 0.4 + DA_STEP * n)
  out = crun_g(cw, 20, -4.5, a=-3.0)
  assert out['aLeadK'] == pytest.approx(0.0)


def test_growth_limit_new_track_starts_from_zero():
  # (c)
  cw = CameraWitness()
  crun_g(cw, 40, -4.5)
  assert cw.cap_dv[0] > 0.0
  out = gstep(cw, -4.5, tid=54)
  assert cw.track_ids[0] == 54
  assert out['vRel'] == pytest.approx(-4.5 + DV_STEP) and cw.cap_dv[0] == pytest.approx(DV_STEP)
  out = gstep(cw, -4.5, tid=54)
  assert out['vRel'] == pytest.approx(-4.5 + 2 * DV_STEP)


def test_growth_limit_veto_clears_the_correction():
  cw = CameraWitness()
  crun_g(cw, 40, -4.5)
  gstep(cw, -4.5, prob=0.0)
  assert cw.cap_dv[0] == 0.0 and cw.cap_da[0] == 0.0 and cw.weights[0] == 0.0
  out = gstep(cw, -4.5)
  assert out['vRel'] == pytest.approx(-4.5 + RISE * 0 + DV_STEP)


def test_weak_tell_blends_first_then_the_cap_reads_the_blended_lead():
  # (d) the weak tell (status 9, a contradicted lead) with the cap also possible: stage 1 is the slewed blend, stage 2 the
  # rate-limited cap state on the blended lead (gap measured after the blend)
  cw = CameraWitness()
  gstep(cw, -0.6, cam=-0.5)
  dv = 0.0
  tell = 0.0
  held = 0.0
  for n in range(1, 9):
    out = witness(cw, [cap_lead(v_rel=-10.5), ABSENT], [cap_vision(v_rel=-0.5), cap_vision()], v_ego=CAP_V_EGO,
                  probs=(0.95, 0.0), tracks={TID: object()}, statuses=(9, 0), contradictions=(9.9, 0.0),
                  ranges=[ranges(slope=-0.5), deque()])[0]
    stage1 = -10.5 + min(RISE * n, 1.0) * 10.0
    gap = -0.5 - stage1
    if gap > CAP_GAP_MIN:
      tell = 1.0
    elif tell > 0.0 and gap > CAP_GAP_HOLD and held < CAP_HOLD_T:   # the tapered hold (the only mode)
      held += DT_MDL
      tell = (gap - CAP_GAP_HOLD) / (CAP_GAP_MIN - CAP_GAP_HOLD)
    else:
      tell = 0.0
    dv = min(max(tell * gap if tell > 0.0 and gap > 0.0 else 0.0, dv - DV_STEP), dv + DV_STEP)
    assert cw.slewed[0] == pytest.approx(min(RISE * n, 1.0))
    assert out['vRel'] == pytest.approx(stage1 + dv) and cw.cap_dv[0] == pytest.approx(dv)
  assert cw.tell_weights['weak'][0] == 1.0


def test_cap_gap_is_measured_on_the_blended_lead():
  # (a) raw gap 4.0 > CAP_GAP_MIN, but the weak tell (distance ratio 1.0, weight DISTANCE_W) first moves vRel by 2.4, so the
  # gap the cap sees is 1.6 < CAP_GAP_MIN: no cap (scorecard ep292: the old cap saw the post-reversal lead)
  cw = CameraWitness()
  lead, model = cap_lead(v_rel=-4.5), cap_vision(v_rel=-0.5)
  raw = witness(CameraWitness(), [lead, ABSENT], [model, cap_vision()], v_ego=CAP_V_EGO, probs=(0.95, 0.0),
                tracks={TID: object()}, ranges=[ranges(slope=-0.5), deque()])[0]
  assert raw['vRel'] > -4.5   # the raw lead alone does fire the cap
  out = witness(cw, [lead, ABSENT], [model, cap_vision()], v_ego=CAP_V_EGO, probs=(0.95, 0.0), tracks={TID: object()},
                ratios=(1.0, 0.0), ranges=[ranges(slope=-0.5), deque()])[0]
  assert cw.tell_weights['cap'][0] == 0.0 and cw.cap_dv[0] == 0.0 and cw.cap_da[0] == 0.0
  assert out['vRel'] == pytest.approx(-4.5 + DISTANCE_W * 4.0)


def test_weak_tell_still_slews():
  # (c) established track, the weak tell rises at RISE per cycle and releases at RELEASE per cycle
  cw = CameraWitness()
  lead = radar_lead(55, 66.0, 15.0, -3.0)
  step(cw, lead)
  for n in range(1, 4):
    out = step(cw, lead, vision(21.5, 0.0), statuses=(9, 0), contradictions=(9.9, 0.0))
    assert cw.slewed[0] == pytest.approx(RISE * n) and cw.weights[0] == pytest.approx(RISE * n)
    assert out['vLead'] == pytest.approx(15.0 + RISE * n * (21.5 - 15.0))
  step(cw, lead, vision(21.5, 0.0), statuses=(7, 0))
  assert cw.slewed[0] == pytest.approx(3 * RISE - RELEASE)


def test_urgency_veto_zeroes_the_cap_state():
  # (d) a lead that turns urgent loses the whole correction at once, not at the rate
  cw = CameraWitness()
  crun_g(cw, 40, -4.5, a=-3.0)
  assert cw.cap_dv[0] > 0.0 and cw.cap_da[0] > 0.0
  out = gstep(cw, -4.5, a=-3.0, urgent_v_rel=-20.0)
  assert cw.cap_dv[0] == 0.0 and cw.cap_da[0] == 0.0 and cw.weights[0] == 0.0
  assert out['vRel'] == pytest.approx(-4.5) and out['aLeadK'] == pytest.approx(-3.0)


def test_growth_limit_correction_shrinks_freely():
  # (e) CHANGED (state law, 2026-11-11): cap-only, the camera gap closes in one frame (radar vRel recovers 6 m/s): the
  # correction is the old cap's state, so it falls DV_STEP per cycle, not at once (the old cap's release; replay ep154)
  cw = CameraWitness()
  crun_g(cw, 40, -10.5)
  assert cw.cap_dv[0] == pytest.approx(10.0)
  for n in range(1, 6):
    out = gstep(cw, -4.5)                     # gap 4.0 now, target 4.0, state 10.0 - DV_STEP * n
    assert cw.cap_dv[0] == pytest.approx(10.0 - DV_STEP * n)
    assert out['vRel'] == pytest.approx(-4.5 + 10.0 - DV_STEP * n)
  # the known property: the state exceeds the current camera gap while it decays (published less closing than the camera)
  assert cw.cap_dv[0] > 4.0
  out = crun_g(cw, 30, -4.5)
  assert cw.cap_dv[0] == pytest.approx(4.0) and out['vRel'] == pytest.approx(-0.5)


def test_cap_state_falls_at_the_rate_when_the_gap_collapses():
  # the gap collapses to or below CAP_GAP_HOLD in one frame (no hold, tell lost): the correction does not fall faster than DV_STEP / DA_STEP
  cw = CameraWitness()
  crun_g(cw, 40, -4.5, a=-3.0)
  assert cw.cap_dv[0] == pytest.approx(4.0) and cw.cap_da[0] == pytest.approx(3.0)
  for n in range(1, 6):
    out = gstep(cw, -1.0, a=-3.0)             # gap 0.5 <= CAP_GAP_HOLD: tell 0, target 0
    assert cw.tell_weights['cap'][0] == 0.0
    assert cw.cap_dv[0] == pytest.approx(4.0 - DV_STEP * n)
    assert out['vRel'] == pytest.approx(-1.0 + 4.0 - DV_STEP * n)
    assert out['aLeadK'] == pytest.approx(-3.0 + 3.0 - DA_STEP * n)
  out = crun_g(cw, 12, -1.0, a=-3.0)
  assert cw.cap_dv[0] == 0.0 and cw.cap_da[0] == 0.0 and cw.weights[0] == 0.0
  assert out['vRel'] == pytest.approx(-1.0) and out['aLeadK'] == pytest.approx(-3.0)


def test_cap_state_decays_at_the_rate_when_the_tell_is_lost_by_range():
  # the tell lost because dRel < CAP_MIN_D (ep356): the state decays at the rate, never at once
  cw = CameraWitness()
  crun_g(cw, 40, -10.5)
  assert cw.cap_dv[0] == pytest.approx(10.0)
  for n in range(1, 4):
    out = cstep(cw, lead=cap_lead(d=CAP_MIN_D - 1.0, v_rel=-10.5), model=cap_vision(v_rel=-0.5),
                camera=ranges(slope=-0.5), tracks={TID: object()})
    assert cw.tell_weights['cap'][0] == 0.0
    assert cw.cap_dv[0] == pytest.approx(10.0 - DV_STEP * n)
    assert out['vRel'] == pytest.approx(-10.5 + 10.0 - DV_STEP * n)
