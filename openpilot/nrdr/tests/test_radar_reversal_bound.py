"""Reversal-latch bound (static). The positive case is shaped on route 30 T1420-1425 (track 60)."""
from types import SimpleNamespace

import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_reversal_bound import LATCH_S, REVERSAL_WINDOW_S, W, ReversalBound

V_EGO = 22.0


def radar_lead(tid, d, v, a):
  return {'dRel': d, 'yRel': 0.0, 'vRel': v - V_EGO, 'vLead': v, 'vLeadK': v, 'aLeadK': a, 'aLeadTau': 0.6,
          'present': True, 'modelProb': 0.95, 'radar': True, 'radarTrackId': tid}


def vision(v=21.5, a=0.0):
  return SimpleNamespace(x=[50.0], v=[v], a=[a])


ABSENT = {'present': False}


def step(rb, lead, model=None, prob=0.95, tracks=None):
  model = model or vision()
  tracks = {lead['radarTrackId']: None} if tracks is None and lead.get('radar') else (tracks or {})
  return rb.apply([lead, ABSENT], [model, vision()], V_EGO, V_EGO, [prob, 0.0], tracks)[0]


def frames(seconds):
  return int(round(seconds / DT_MDL))


def reverse(rb, tid=60, gap_s=1.0, first=4.0, second=-3.0, d=45.0):
  step(rb, radar_lead(tid, d, 27.6, first))
  for _ in range(frames(gap_s) - 1):
    step(rb, radar_lead(tid, d, 24.0, 0.0))
  return step(rb, radar_lead(tid, d, 20.0, second))


def test_route_30_shape_is_softened_not_dropped():
  rb = ReversalBound()
  reverse(rb)
  raw = radar_lead(60, 39.0, 15.7, -3.0)
  out = step(rb, raw, vision(21.5, 0.0))
  assert out['present'] and out['radar'] and out['radarTrackId'] == 60
  assert out['dRel'] == raw['dRel']
  assert out['vLead'] == pytest.approx(15.7 + W * (21.5 - 15.7))
  assert out['vLeadK'] == pytest.approx(out['vLead'])
  assert out['vRel'] == pytest.approx(out['vLead'] - V_EGO)
  assert out['aLeadK'] == pytest.approx(-3.0 + W * 3.0)
  assert rb.weights[0] == W
  assert raw['vLead'] == 15.7  # input not mutated


def test_negative_then_positive_order_does_not_latch():
  rb = ReversalBound()
  reverse(rb, first=-3.0, second=4.0)
  raw = radar_lead(60, 45.0, 15.7, -1.5)  # still braking, but not past REVERSAL_LOW again
  assert step(rb, raw) == raw


def test_reversal_slower_than_window_does_not_latch():
  rb = ReversalBound()
  reverse(rb, gap_s=REVERSAL_WINDOW_S + 0.2)
  raw = radar_lead(60, 45.0, 15.7, -3.0)
  assert step(rb, raw) == raw


def test_urgent_range_or_ttc_keeps_full_authority():
  rb = ReversalBound()
  reverse(rb)
  close = radar_lead(60, 29.0, 15.7, -3.0)
  assert step(rb, close) == close
  short_ttc = radar_lead(60, 40.0, V_EGO - 11.0, -3.0)  # 11 m/s closing, TTC 3.6 s
  assert step(rb, short_ttc) == short_ttc


def test_only_moves_toward_less_severe():
  rb = ReversalBound()
  reverse(rb)
  raw = radar_lead(60, 45.0, 21.0, -0.5)
  out = step(rb, raw, vision(15.0, -2.5))  # vision more severe than radar: untouched
  assert out == raw
  assert rb.weights[0] == 0.0


def test_latch_expires():
  rb = ReversalBound()
  reverse(rb)
  for _ in range(frames(LATCH_S) - 2):
    out = step(rb, radar_lead(60, 45.0, 18.0, -1.0))
  assert out['vLead'] > 18.0
  for _ in range(4):
    out = step(rb, radar_lead(60, 45.0, 18.0, -1.0))
  assert out['vLead'] == 18.0


def test_retrigger_extends_latch():
  rb = ReversalBound()
  reverse(rb)
  for _ in range(frames(2.0)):
    step(rb, radar_lead(60, 45.0, 22.0, 0.0))
  reverse(rb)
  for _ in range(frames(3.0)):
    out = step(rb, radar_lead(60, 45.0, 18.0, -1.0))
  assert out['vLead'] > 18.0


def test_weak_model_lead_is_not_a_witness():
  rb = ReversalBound()
  reverse(rb)
  raw = radar_lead(60, 45.0, 15.7, -3.0)
  assert step(rb, raw, prob=0.2) == raw


def test_other_track_not_affected():
  rb = ReversalBound()
  reverse(rb, tid=60)
  raw = radar_lead(61, 45.0, 15.7, -3.0)
  assert step(rb, raw, tracks={60: None, 61: None}) == raw


def test_vision_only_and_absent_leads_pass_through():
  rb = ReversalBound()
  reverse(rb)
  vision_lead = {'present': True, 'radar': False, 'radarTrackId': -1, 'dRel': 45.0, 'vRel': -6.0,
                 'vLead': 16.0, 'vLeadK': 16.0, 'aLeadK': -3.0}
  out = rb.apply([vision_lead, ABSENT], [vision(), vision()], V_EGO, V_EGO, [0.95, 0.95], {60: None})
  assert out[0] is vision_lead and out[1] is ABSENT


def test_vanished_track_state_is_pruned():
  rb = ReversalBound()
  reverse(rb)
  rb.apply([ABSENT, ABSENT], [vision(), vision()], V_EGO, V_EGO, [0.0, 0.0], {})
  assert rb.armed_t == {} and rb.latched_until == {}
