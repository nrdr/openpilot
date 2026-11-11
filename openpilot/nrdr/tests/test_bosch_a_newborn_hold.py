"""Newborn lead aLeadK bound (D-080, NEWBORN_HOLD_ENABLED): pure python. The class and bound_newborn_leads are unchanged
on this branch; they had no unit tests (only an ad hoc fuzz), so these are new. Replay only."""
from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.longitudinal.bosch_a import honda_bosch_a_long as hb


def lead(d, a, tid=7, radar=True, v=20.0, present=True):
  return SimpleNamespace(present=present, radar=radar, radarTrackId=tid, dRel=d, vLead=v, vRel=v - 20.0, aLeadK=a)


def rs(l1, l2=None):
  return SimpleNamespace(leadOne=l1, leadTwo=l2 if l2 is not None else lead(0.0, 0.0, present=False), marker='rs')


def test_newborn_aleadk_held_at_min_brake():
  h = hb.NewbornLeadHold()
  out = hb.bound_newborn_leads(rs(lead(61.0, -2.39)), 0.0, h)
  assert out.leadOne.aLeadK == -hb.NEWBORN_LEAD_MIN_BRAKE
  assert out.leadOne.dRel == 61.0 and out.leadOne.radarTrackId == 7  # only aLeadK changes
  assert out.marker == 'rs' and h.bound_frames == 1


def test_gentle_lead_untouched_returns_same_object():
  h = hb.NewbornLeadHold()
  r = rs(lead(61.0, -0.4))
  assert hb.bound_newborn_leads(r, 0.0, h) is r


def test_bound_ends_after_newborn_frames():
  h = hb.NewbornLeadHold()
  for _ in range(hb.NEWBORN_LEAD_FRAMES):
    out = hb.bound_newborn_leads(rs(lead(61.0, -2.39)), 0.0, h)
    assert out.leadOne.aLeadK == -1.0
  r = rs(lead(61.0, -2.39))
  assert hb.bound_newborn_leads(r, 0.0, h) is r  # no longer newborn


def test_vision_and_absent_leads_untouched():
  h = hb.NewbornLeadHold()
  r = rs(lead(61.0, -2.39, radar=False))
  assert hb.bound_newborn_leads(r, 0.0, h) is r
  r = rs(lead(61.0, -2.39, present=False))
  assert hb.bound_newborn_leads(r, 0.0, h) is r


def test_range_fit_confirms_hard_braking():
  # range history that really is decelerating at -3 m/s^2 relative (d = 61 - 0.5*3*t^2 shape), ego a = 0
  h = hb.NewbornLeadHold()
  out = None
  for i in range(hb.NEWBORN_LEAD_FIT_FRAMES + 2):
    t = i * hb.NEWBORN_LEAD_DT
    out = hb.bound_newborn_leads(rs(lead(61.0 - 1.5 * t * t, -3.0)), 0.0, h)
  assert out.leadOne.aLeadK == pytest.approx(-3.0, abs=0.05)  # fit lowers the floor to its own estimate: -3 passes (<= -1)
  # and a steady range with a claimed -3 stays at -1.0
  h = hb.NewbornLeadHold()
  for _ in range(hb.NEWBORN_LEAD_FIT_FRAMES + 2):
    out = hb.bound_newborn_leads(rs(lead(61.0, -3.0)), 0.0, h)
  assert out.leadOne.aLeadK == -1.0


def test_gap_and_range_jump_make_track_newborn_again():
  h = hb.NewbornLeadHold()
  for _ in range(hb.NEWBORN_LEAD_FRAMES + 5):
    hb.bound_newborn_leads(rs(lead(61.0, -2.0)), 0.0, h)
  for _ in range(hb.NEWBORN_LEAD_GAP_FRAMES + 2):  # absent
    hb.bound_newborn_leads(rs(lead(0.0, 0.0, present=False)), 0.0, h)
  assert hb.bound_newborn_leads(rs(lead(61.0, -2.0)), 0.0, h).leadOne.aLeadK == -1.0
  h = hb.NewbornLeadHold()
  for _ in range(hb.NEWBORN_LEAD_FRAMES + 5):
    hb.bound_newborn_leads(rs(lead(61.0, -2.0)), 0.0, h)
  assert hb.bound_newborn_leads(rs(lead(61.0 + hb.NEWBORN_LEAD_JUMP_M + 0.5, -2.0)), 0.0, h).leadOne.aLeadK == -1.0


def test_wiring_follows_switch_at_construction(monkeypatch):
  monkeypatch.setattr(hb, 'active_for', lambda CP: True)
  cp = SimpleNamespace(radarUnavailable=False)
  monkeypatch.setattr(hb, 'NEWBORN_HOLD_ENABLED', False)
  off = hb.HondaBoschALongEnhancement(cp, 0.05)
  assert off.newborn_hold is None
  r = rs(lead(61.0, -2.39))
  assert off.planner_radar_state(r, 0.0) is r
  monkeypatch.setattr(hb, 'NEWBORN_HOLD_ENABLED', True)
  on = hb.HondaBoschALongEnhancement(cp, 0.05)
  assert on.newborn_hold is not None
  assert on.planner_radar_state(r, 0.0).leadOne.aLeadK == -1.0
  monkeypatch.setattr(hb, 'active_for', lambda CP: False)
  assert hb.HondaBoschALongEnhancement(cp, 0.05).newborn_hold is None
