"""Static tests for Stock Brake Feel's gap-gated far depth entry (owner 2026-11-06, route 96 32:17). Not road evidence."""
from types import SimpleNamespace

from openpilot.nrdr.features.longitudinal.bosch_a import honda_bosch_a_long as hbl

DT = 0.05


def lead(d, v_rel, a_lead=0.0):
  return SimpleNamespace(present=True, dRel=d, vRel=v_rel, aLeadK=a_lead)


def test_far_lead_within_gap_gets_minus_0_6():
  # 96 T4-like: 40 m at 20 m/s is a 2 s gap; closing 1 m/s -> TTC 40 s
  assert hbl.stock_feel_target((lead(40.0, -1.0),), -0.6, -1.0, DT, v_ego=20.0) == -0.6


def test_far_lead_beyond_gap_keeps_minus_0_35():
  # vn80-like: 110 m at 12.7 m/s is an 8.7 s gap
  assert hbl.stock_feel_target((lead(110.0, -0.8),), -0.35, -1.0, DT, v_ego=12.7) == -0.35
  # p78-like: crawling, the gap is huge
  assert hbl.stock_feel_target((lead(150.0, -0.6),), -0.35, -1.0, DT, v_ego=1.7) == -0.35


def test_gap_uses_the_nearest_lead():
  leads = (lead(150.0, -5.0), lead(30.0, 0.6))
  assert hbl.stock_feel_depth(leads, 30.0, 20.0) == -0.6


def test_gate_changes_only_the_far_entry():
  near, far = (lead(40.0, -1.0),), (lead(140.0, -1.0),)
  for ttc in (2.0, 5.0, 11.0, 17.5):
    assert hbl.stock_feel_depth(near, ttc, 20.0) == hbl.stock_feel_depth(far, ttc, 20.0)
  assert hbl.stock_feel_depth(far, 25.0, 20.0) == -0.35


def test_far_cap_never_adds_braking():
  assert hbl.stock_feel_target((lead(40.0, -1.0),), -0.2, -0.2, DT, v_ego=20.0) == -0.2
