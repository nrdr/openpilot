from types import SimpleNamespace

from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_turnoff as T
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_release import BRAKE_RELEASE_JERK, BoschARelease

DT = 0.05


def lead(tid=22, d=20.0, v=-5.0, y=-0.8, present=True):
  return SimpleNamespace(present=present, radarTrackId=tid, dRel=d, vRel=v, yRel=y)


GONE = lead(present=False, tid=-1, d=0.0, v=0.0, y=0.0)


def run_release(fl, raw_seq, prev_target=-3.0):
  """One braking cycle with the lead, then the lead is gone; raw_seq gives the raw tracks per cycle after that."""
  assert fl.update(lead(), prev_target, {22: -0.8}) is None
  return [fl.update(GONE, prev_target, raw) for raw in raw_seq]


def test_confirmed_exit_lets_off_fast_and_withholds_gas():
  fl = T.FastLetoff(DT)
  out = run_release(fl, [{22: -1.0}, {22: -1.6}, {22: -2.0}, {}])  # gone at 2.0 m: past CLEAR_Y, keeps going
  assert out[0] is None and out[1] == T.FAST_JERK
  assert fl.fired == 1 and fl.no_gas


def test_track_vanishing_without_moving_out_keeps_base_letoff():
  # 84 s7 / a2 s42 shape: the track disappears near 1.25 m with little lateral growth
  fl = T.FastLetoff(DT)
  out = run_release(fl, [{22: -0.85}, {}, {}, {}])
  assert all(o is None for o in out)
  assert fl.fired == 0 and fl.aborted == 1 and not fl.no_gas


def test_track_staying_in_lane_times_out():
  fl = T.FastLetoff(DT)
  n = int(T.CONFIRM_S / DT) + 4
  out = run_release(fl, [{22: -0.9}] * n)
  assert all(o is None for o in out) and fl.aborted == 1


def test_no_raw_tracks_never_fires():
  fl = T.FastLetoff(DT)
  out = run_release(fl, [{}] * 20)
  assert all(o is None for o in out) and fl.fired == 0


def test_closing_lead_cancels_fast():
  fl = T.FastLetoff(DT)
  run_release(fl, [{22: -1.0, 30: 0.0}, {22: -1.6, 30: 0.0}])
  assert fl.fast_s > 0.0
  assert fl.update(lead(tid=30, d=25.0, v=-3.0, y=0.0), -2.0, {22: -2.0, 30: 0.0}) is None
  assert not fl.no_gas


def test_watched_track_vanishing_close_cancels():
  fl = T.FastLetoff(DT)
  run_release(fl, [{22: -1.0}, {22: -1.6}])
  assert fl.fast_s > 0.0
  assert fl.update(GONE, -2.0, {}) is None and not fl.no_gas


def test_no_trigger_without_a_real_brake():
  fl = T.FastLetoff(DT)
  out = run_release(fl, [{22: -2.0}] * 5, prev_target=-0.2)
  assert all(o is None for o in out) and fl.pend is None


def test_raw_track_y():
  pts = [SimpleNamespace(trackId=22, yRel=-1.5), SimpleNamespace(trackId=3, yRel=0.4)]
  class SM:
    valid = {'radarTracks': True}
    alive = {'radarTracks': True}
    def __getitem__(self, k):
      return SimpleNamespace(points=pts)
  sm = SM()
  assert T.raw_track_y(sm) == {22: -1.5, 3: 0.4}
  sm.valid['radarTracks'] = False
  assert T.raw_track_y(sm) == {}
  assert T.raw_track_y({}) == {}


def _release(monkeypatch, radar=True):
  import openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_release as bs
  monkeypatch.setattr(bs, 'vehicle_supported', lambda CP: True)
  return BoschARelease(SimpleNamespace(radarUnavailable=not radar), DT)


def test_release_step_fast_letoff_and_no_gas(monkeypatch):
  rel = _release(monkeypatch)
  assert rel.enabled and rel.coast_enabled
  prev = -3.0
  prev = rel.step(lead_one=lead(), prev=prev, target=-3.0, raw_y={22: -0.8})
  prev = rel.step(lead_one=GONE, prev=prev, target=0.8, raw_y={22: -1.0})
  base_rise = BRAKE_RELEASE_JERK * DT
  assert prev <= -3.0 + 1e-6  # dwell / pending: no fast rise yet
  nxt = rel.step(lead_one=GONE, prev=prev, target=0.8, raw_y={22: -1.6})
  assert abs((nxt - prev) - T.FAST_JERK * DT) < 1e-6 and (nxt - prev) > base_rise
  for _ in range(20):
    nxt = rel.step(lead_one=GONE, prev=nxt, target=0.8, raw_y={22: -2.5})
    assert nxt <= 0.0  # no gas while the no-gas window runs
  assert rel.fast_letoff.fired == 1


def test_release_step_without_radar_never_fast(monkeypatch):
  rel = _release(monkeypatch, radar=False)
  assert rel.enabled and not rel.coast_enabled
  prev = rel.step(lead_one=lead(), prev=-3.0, target=-3.0, raw_y={22: -0.8})
  for raw in ({22: -1.0}, {22: -1.6}, {22: -2.5}):
    nxt = rel.step(lead_one=GONE, prev=prev, target=0.8, raw_y=raw)
    assert nxt - prev <= BRAKE_RELEASE_JERK * DT + 1e-6
    prev = nxt
  assert rel.fast_letoff.fired == 0


import pytest


@pytest.fixture(autouse=True)
def _no_ghost_arm(monkeypatch):
  """These tests pin the car build's step (coast + FastLetoff); arm G replaces it and has its own tests."""
  from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_release
  monkeypatch.setattr(bosch_a_release, 'GHOST_ARM', False)
