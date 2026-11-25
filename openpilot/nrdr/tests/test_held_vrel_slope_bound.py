"""Held-vRel range-slope bound (replay-shaped, scratch candidate, not road tested).

Shaped on scorecard episode 26 (route 00000071--37216af48f seg 9): track 58 at 82-85 m, the parser marks the point not
measured and holds vRel -9.51 while the track's own range rises about 2 m/s. Driven through BoschALeadPolicy.update_tracks
and leads() with a minimal fake SubMaster/radard. The model lead is given a filtered prob of 0.5 (above the witness's 0.35,
below the cap's and the slow bound's 0.9) so only the held-vRel bound can move the lead.
"""
from types import SimpleNamespace

import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar import bosch_a_lead_policy as radar_mod
from openpilot.nrdr.features.radar.bosch_a_lead_policy import (HELD_VREL_MARGIN, HELD_VREL_MIN_S, BoschALeadPolicy)

V_EGO = 30.0


class KalmanParams:
  # stand-in for radard.KalmanParams(DT_MDL = 0.05) (A, C and the K table entries for dt 0.05), so the test does not import radard
  # (which loads the aarch64-only params library)
  def __init__(self, dt):
    assert abs(dt - 0.05) < 1e-9
    self.A = [[1.0, dt], [0.0, 1.0]]
    self.C = [1.0, 0.0]
    self.K = [[0.1988689], [0.28555364]]


HELD_V_REL = -9.51
CYCLES_MIN = round(HELD_VREL_MIN_S / DT_MDL)
WARMUP = 20  # cycles with a measured point first, so the range slope is available the cycle `direct` drops


def model_lead(x, v):
  return SimpleNamespace(x=[x], y=[0.0], v=[v], a=[0.0], xStd=[1.0], yStd=[0.5], vStd=[1.0], prob=0.99)


class FakeSM:
  def __init__(self):
    self.recv_frame = {'radarTracks': 0}
    self.logMonoTime = {'radarTracks': 0}
    self.msgs = {}

  def __getitem__(self, key):
    return self.msgs[key]


class Rig:
  def __init__(self, d0=82.0, slope=2.0, v_rel=HELD_V_REL, track_id=58):
    self.policy = BoschALeadPolicy()
    self.radar = SimpleNamespace(ready=True, v_ego=V_EGO, tracks={}, kalman_params=KalmanParams(DT_MDL), v_ego_hist=[V_EGO],
                                 lead_prob_filters=[SimpleNamespace(x=0.5), SimpleNamespace(x=0.0)])
    self.sm = FakeSM()
    self.d, self.slope, self.v_rel, self.track_id = d0, slope, v_rel, track_id

  def step(self, direct=False, d_rel=None, v_rel=None, a_slope=None):
    self.d = self.d + (self.slope if a_slope is None else a_slope) * DT_MDL if d_rel is None else d_rel
    v_rel = self.v_rel if v_rel is None else v_rel
    point = SimpleNamespace(trackId=self.track_id, dRel=self.d, yRel=0.0, vRel=v_rel, deprecated=SimpleNamespace(measured=direct))
    self.sm.recv_frame['radarTracks'] += 1
    lead0 = model_lead(self.d + radar_mod.RADAR_TO_CAMERA, V_EGO + v_rel)
    self.sm.msgs = {'carState': SimpleNamespace(standstill=False), 'modelV2': SimpleNamespace(leadsV3=[lead0, model_lead(300.0, V_EGO)])}
    self.policy.update_tracks(self.sm, SimpleNamespace(points=[point]), self.radar)
    return self.policy.leads(self.sm, self.radar, V_EGO)[0]

  def warmup(self, n=WARMUP, **kw):
    out = None
    for _ in range(n):
      out = self.step(direct=True, **kw)
    return out


def test_fires_only_after_min_s_and_gives_minus_one():
  rig = Rig()
  rig.warmup()
  outs = [rig.step(direct=False) for _ in range(CYCLES_MIN + 2)]
  for out in outs[:CYCLES_MIN - 1]:
    assert out['vRel'] == pytest.approx(HELD_V_REL)
  for out in outs[CYCLES_MIN - 1:]:
    assert out['vRel'] == pytest.approx(-HELD_VREL_MARGIN, abs=1e-6)
    assert out['radar'] and out['present'] and out['radarTrackId'] == 58
    assert out['vLead'] == pytest.approx(V_EGO - HELD_VREL_MARGIN, abs=1e-6)
    assert V_EGO + HELD_V_REL < out['vLeadK'] <= V_EGO


def test_direct_true_does_not_fire():
  rig = Rig()
  rig.warmup()
  for _ in range(CYCLES_MIN + 4):
    assert rig.step(direct=True)['vRel'] == pytest.approx(HELD_V_REL)


def test_near_lead_does_not_fire():
  rig = Rig(d0=45.0)
  rig.warmup()
  for _ in range(CYCLES_MIN + 4):
    assert rig.step(direct=False)['vRel'] == pytest.approx(HELD_V_REL)


def test_agreeing_slope_does_not_fire():
  rig = Rig(slope=-2.0, v_rel=-9.51)
  rig.warmup()
  for _ in range(CYCLES_MIN + 4):
    assert rig.step(direct=False)['vRel'] == pytest.approx(HELD_V_REL)


def test_urgency_does_not_fire():
  # last direct reading (within URGENT_LAST_DIRECT_S) puts the TTC under 4 s: 82 m / 25 m/s = 3.3 s; the held vRel alone would not
  rig = Rig()
  rig.warmup(v_rel=-25.0)
  for _ in range(CYCLES_MIN + 4):
    out = rig.step(direct=False)
    assert out['vRel'] == pytest.approx(HELD_V_REL)
  # and with urgency it is the published value that stays
  assert rig.policy.tracks[58].held_vrel_cycles == 0


def test_resets_the_cycle_direct_returns():
  rig = Rig()
  rig.warmup()
  for _ in range(CYCLES_MIN + 2):
    rig.step(direct=False)
  assert rig.policy.tracks[58].held_vrel_cycles >= CYCLES_MIN
  out = rig.step(direct=True)
  assert rig.policy.tracks[58].held_vrel_cycles == 0
  assert out['vRel'] == pytest.approx(HELD_V_REL)   # the radar's own measurement, no release slew
  out = rig.step(direct=False)                      # needs the full min time again
  assert out['vRel'] == pytest.approx(HELD_V_REL)


def test_never_lowers_vrel():
  # published vRel already above the bound (-0.5 > -1.0): nothing to raise; closing gate also false at -0.5
  rig = Rig(v_rel=-0.5)
  rig.warmup()
  for _ in range(CYCLES_MIN + 4):
    assert rig.step(direct=False)['vRel'] == pytest.approx(-0.5)
  # unit level: bound below current vRel never lowers
  lead = {'dRel': 80.0, 'vRel': -0.2, 'vLead': 29.8, 'vLeadK': 29.8, 'aLeadK': 0.0}
  track = SimpleNamespace(range_history=[80.0 + 2.0 * DT_MDL * i for i in range(20)])
  assert radar_mod.held_vrel_bound(lead, track) is lead  # ty: ignore[invalid-argument-type]


def test_distance_accel_track_untouched():
  rig = Rig()
  rig.warmup()
  rig_off = Rig()
  rig_off.warmup()
  old = radar_mod.HELD_VREL_SLOPE_BOUND_ENABLED
  try:
    for _ in range(CYCLES_MIN + 4):
      on = rig.step(direct=False)
      radar_mod.HELD_VREL_SLOPE_BOUND_ENABLED = False  # ty: ignore[invalid-assignment]
      try:
        off = rig_off.step(direct=False)
      finally:
        radar_mod.HELD_VREL_SLOPE_BOUND_ENABLED = old
      for key in ('dRel', 'yRel', 'aLeadK', 'aLeadTau', 'radarTrackId', 'radar', 'present', 'modelProb'):
        assert on[key] == off[key]
  finally:
    radar_mod.HELD_VREL_SLOPE_BOUND_ENABLED = old
  assert on['vRel'] != off['vRel']


def test_switch_off_is_no_change(monkeypatch):
  monkeypatch.setattr(radar_mod, 'HELD_VREL_SLOPE_BOUND_ENABLED', False)
  rig = Rig()
  rig.warmup()
  for _ in range(CYCLES_MIN + 6):
    out = rig.step(direct=False)
    assert out['vRel'] == pytest.approx(HELD_V_REL)
    assert out['vLead'] == pytest.approx(V_EGO + HELD_V_REL)
