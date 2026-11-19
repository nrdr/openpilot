"""Need floor (NeedFloor / HondaBoschALongEnhancement.need_floor): pure python, replay-only behavior.

The parity test compares against an independent port of the ARM 'D' block of
~/longsim_frames/scorecard/replay_bd.py (Job's scorecard harness)."""
import random
from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.longitudinal.bosch_a import honda_bosch_a_long as hb


def lead(d, v_rel, a=0.0, tid=1, radar=True, present=True):
  return SimpleNamespace(present=present, radar=radar, radarTrackId=tid, dRel=d, vRel=v_rel, aLeadK=a)


def make(monkeypatch, enabled=True, active=True, min_gap=False):  # min_gap False keeps the floor mechanics tests independent of the headway gate
  monkeypatch.setattr(hb, 'active_for', lambda CP: active)
  monkeypatch.setattr(hb, 'NEED_FLOOR_ENABLED', enabled)
  monkeypatch.setattr(hb, 'NEED_FLOOR_MIN_GAP_ENABLED', min_gap)  # read by NeedFloor at construction
  return hb.HondaBoschALongEnhancement(SimpleNamespace(radarUnavailable=False), 0.05)


def nf(p, ld, target, v_ego=25.0, ld2=None, reset_state=False, **kw):
  return p.need_floor(lead_one=ld, lead_two=ld2, target=target, v_ego=v_ego, reset_state=reset_state, **kw)


# steady closing moving lead: v_ego 25, vRel -3 (vLead 22), d 80: need = 9 / (2 * (80 - 28)) = 0.0865 -> floor -0.8
def steady(**kw):
  d = {'d': 80.0, 'v_rel': -3.0, 'a': 0.0}
  d.update(kw)
  return lead(**d)


def run(p, ld, n, target=-2.0, **kw):
  out = None
  for _ in range(n):
    out = nf(p, ld, target, **kw)
  return out


def test_floor_after_gate_not_before(monkeypatch):
  # Reference quirk kept: the first frame on a new (id, radar) only latches the identity (count 0), so the count reaches
  # GATE_FRAMES on the frame after GATE_FRAMES qualifying frames, i.e. the floor first applies on call GATE_FRAMES + 1.
  p = make(monkeypatch)
  for i in range(hb.NEED_FLOOR_GATE_FRAMES):
    assert nf(p, steady(), -2.0) == -2.0, i
  assert nf(p, steady(), -2.0) == pytest.approx(-0.8)


def test_floor_uses_mult_need_when_above_min(monkeypatch):
  p = make(monkeypatch)
  # v_ego 20, vRel -8 (vLead 12), d 60: room 60 - 18 = 42; need = 64 / 84 = 0.762 -> min 0.8; d 45: room 27, need 1.185
  out = run(p, steady(d=45.0, v_rel=-8.0), 12, v_ego=20.0)
  assert out == pytest.approx(-hb.NEED_FLOOR_MULT * 64.0 / (2 * (45.0 - 18.0)))


def test_never_lowers_a_target(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(), 15, target=-0.3) == -0.3
  assert run(p, steady(), 1, target=0.5) == 0.5
  assert run(p, steady(), 1, target=-0.8) == pytest.approx(-0.8)


def test_no_floor_slow_lead(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(v_rel=-21.0), 20, v_ego=25.0) == -2.0  # vLead 4 < 5 (also closing hard); gate never opens


def test_no_floor_lead_braking(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(a=-1.0), 20) == -2.0  # aLeadK must be > -1.0
  p = make(monkeypatch)
  assert run(p, steady(a=-0.99), 20) == pytest.approx(-0.8)


def test_no_floor_low_ego_speed(monkeypatch):
  # A closing lead has vLead < v_ego, so with v_ego < 5 the gate (vLead >= 5) is closed first: the vEgo >= 5 term can never
  # be the only one that fails. v_ego 5.4 with vRel -0.3 (vLead 5.1) opens it; the same lead at v_ego 4.99 does not.
  p = make(monkeypatch)
  assert run(p, steady(d=30.0, v_rel=-0.3), 20, v_ego=5.4) == pytest.approx(-0.8)
  p = make(monkeypatch)
  assert run(p, steady(d=30.0, v_rel=-0.3), 20, v_ego=4.99) == -2.0


def test_no_floor_close_lead(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(d=14.9, v_rel=-0.5), 20) == -2.0
  p = make(monkeypatch)
  assert run(p, steady(d=15.0, v_rel=-0.5), 20) == pytest.approx(-0.8)


def test_no_floor_low_ttc(monkeypatch):
  p = make(monkeypatch)
  # d 60, vRel -20 (vLead 5): ttc 3.0 -> release; need = 400 / (2*max(60-11, 5)) = 4.08 >= 2 also; pick need < 2, ttc <= 3:
  # d 15, vRel -5.1, v_ego 25 (vLead 19.9): ttc 2.94, room 15 - 25.9 < 5 -> need = 26/10 = 2.6; so ttc and need both fire.
  assert run(p, steady(d=15.0, v_rel=-5.1), 20) == -2.0
  assert p._need_floor.off


def test_no_floor_high_need(monkeypatch):
  p = make(monkeypatch)
  # v_ego 25, vRel -6 (vLead 19), d 60: room 60 - 25 = 35; need = 36/70 = 0.51 (floor); d 40: room 15, need 1.2;
  # d 31: room 6, need 3.0 >= 2 (ttc 5.2 > 3), so only the need releases
  assert run(p, steady(d=31.0, v_rel=-6.0), 20) == -2.0
  assert p._need_floor.off


def test_sticky_after_release_and_clear_after_quiet(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(), 12) == pytest.approx(-0.8)
  assert nf(p, steady(d=15.0, v_rel=-5.1), -2.0) == -2.0  # release fires
  assert run(p, steady(), 30) == -2.0                      # sticky: closing lead, gate open, still off
  for _ in range(hb.NEED_FLOOR_QUIET_FRAMES - 1):
    assert nf(p, steady(v_rel=0.5), -2.0) == -2.0
  assert p._need_floor.off
  assert nf(p, steady(v_rel=0.5), -2.0) == -2.0
  assert not p._need_floor.off                             # 20th non-closing frame clears it
  assert nf(p, steady(), -2.0) == pytest.approx(-0.8)      # gate stayed open through the quiet frames


def test_sticky_after_emergency_latch(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(), 12) == pytest.approx(-0.8)
  p.emergency = True
  assert nf(p, steady(), -2.0) == -2.0
  p.emergency = False
  assert run(p, steady(), 30) == -2.0  # latch ended, floor stays off


def test_sticky_cleared_by_new_farther_track(monkeypatch):
  p = make(monkeypatch)
  assert nf(p, steady(d=15.0, v_rel=-5.1, tid=1), -2.0) == -2.0
  assert p._need_floor.off
  nf(p, steady(d=80.0, tid=2), -2.0)                       # new id, farther than 15.0: clears
  assert not p._need_floor.off


def test_sticky_not_cleared_by_new_nearer_track(monkeypatch):
  p = make(monkeypatch)
  nf(p, steady(d=31.0, v_rel=-6.0, tid=1), -2.0)           # need 3.0: release
  assert p._need_floor.off
  nf(p, steady(d=20.0, v_rel=-1.0, tid=2), -2.0)           # new id but nearer: stays off
  assert p._need_floor.off


def test_track_id_change_restarts_gate(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(tid=1), 11) == pytest.approx(-0.8)
  for _ in range(hb.NEED_FLOOR_GATE_FRAMES):               # gate restarts: the new id needs the full count again
    assert nf(p, steady(tid=2), -2.0) == -2.0
  assert nf(p, steady(tid=2), -2.0) == pytest.approx(-0.8)


# ---- fixes A + B (owner 2026-11-14, route 000000d2 seg 21 t1298.8) ---------------------------------------------------------
# d2 case: camera lead (tid -1, radar False) 73.7 m, vRel -5.34, v_ego 13.6 (vLead 8.3); e2e braking -1.89 for a red light.
def d2_lead(radar=False, tid=-1):
  return lead(73.7, -5.34, 0.0, tid=tid, radar=radar)


def test_d2_camera_lead_never_lifts(monkeypatch):
  p = make(monkeypatch, min_gap=True)
  assert run(p, d2_lead(), 30, target=-1.89, v_ego=13.6) == -1.89


def test_d2_radar_lead_lifted(monkeypatch):  # a radar lead: -0.80
  p = make(monkeypatch, min_gap=True)
  assert run(p, d2_lead(radar=True, tid=6), 30, target=-1.89, v_ego=13.6) == pytest.approx(-0.8)


def test_camera_lead_keeps_state_machine(monkeypatch):  # camera lead still latches sticky-off (it just never lifts)
  p = make(monkeypatch)
  nf(p, lead(40.0, -15.0, tid=-1, radar=False), -2.0)  # ttc 2.7 -> off
  assert p._need_floor.off


def test_default_radar_only_is_on():
  assert hb.NEED_FLOOR_RADAR_ONLY is True


def test_radar_flag_change_restarts_gate(monkeypatch):
  p = make(monkeypatch)
  assert run(p, steady(radar=True), 11) == pytest.approx(-0.8)
  assert nf(p, steady(radar=False), -2.0) == -2.0


def test_no_lead_gate_count_zero_and_quiet(monkeypatch):
  p = make(monkeypatch)
  run(p, steady(), 10)
  assert nf(p, None, -2.0) == -2.0
  assert p._need_floor.gate_count == 0
  assert nf(p, steady(), -2.0) == -2.0                     # gate has to rebuild
  p = make(monkeypatch)
  nf(p, steady(d=15.0, v_rel=-5.1), -2.0)
  assert p._need_floor.off
  for _ in range(hb.NEED_FLOOR_QUIET_FRAMES):
    nf(p, None, -2.0)
  assert not p._need_floor.off


def test_nearer_lead_is_used(monkeypatch):
  p = make(monkeypatch)
  far, near = steady(d=80.0, tid=1), steady(d=50.0, tid=2)
  out = run(p, far, 12, ld2=near)
  assert out == pytest.approx(-0.8)
  assert p._need_floor.last_id == (2, 1)


def test_reset_state_clears_and_passes_through(monkeypatch):
  p = make(monkeypatch)
  run(p, steady(), 12)
  p._need_floor.off = True
  assert nf(p, steady(), -2.0, reset_state=True) == -2.0
  nf_state = p._need_floor
  assert (nf_state.off, nf_state.quiet, nf_state.last_id, nf_state.gate_id, nf_state.gate_count) == (False, 0, None, None, 0)


def test_disabled_or_inactive_passes_through(monkeypatch):
  for kw in ({'enabled': False}, {'active': False}):
    p = make(monkeypatch, **kw)
    assert p._need_floor is None
    assert run(p, steady(), 30) == -2.0


# ---- parity vs an independent port of replay_bd.py's ARM 'D' block (MULT = NEED_FLOOR_MULT) -----------------------------------------
def ref_d(sticky, ld, ve, a_, emergency, MULT=None):
  MULT = hb.NEED_FLOOR_MULT if MULT is None else MULT
  """ld: list of dicts (id, radar, d, v, a) for present leads; mirrors replay_bd.py sg_w for ARM == 'D'."""
  if ld:
    l = min(ld, key=lambda x: x['d'])
    vr = l['v']
    d = l['d']
    vl = ve + vr
    need = max(0.0, vr * vr if vr < 0 else 0.0) / (2.0 * max(d - (max(vl, 0.0) * 1.0 + 6.0), 5.0))
    ttc = d / -vr if vr < -0.1 else float('inf')
    closing = vr < 0
    lid = (l['id'], l['radar'])
    if closing:
      sticky['quiet'] = 0
    else:
      sticky['quiet'] += 1
    if sticky['off'] and (sticky['quiet'] >= 20 or (sticky['id'] is not None and lid != sticky['id'] and sticky['d'] is not None and d > sticky['d'])):
      sticky['off'] = False
    sticky['id'] = lid
    sticky['d'] = d
    rel_now = closing and (ttc <= 3.0 or need >= 2.0)
    if rel_now or emergency:
      sticky['off'] = True
    al = float(l.get('a', 0.0))
    cond = vl >= 5.0 and al > -1.0
    if sticky.get('gid') != lid or not cond:
      sticky['gcnt'] = 0
    else:
      sticky['gcnt'] = sticky.get('gcnt', 0) + 1
    sticky['gid'] = lid
    gate_ok = sticky['gcnt'] >= 10
    if gate_ok and closing and not sticky['off'] and ve >= 5.0 and d >= 15.0 and ttc > 3.0 and need < 2.0 and l['radar']:  # + fix B
      fl = -max(MULT * need, 0.8)
      if a_ < fl:
        a_ = fl
  else:
    sticky['quiet'] += 1
    sticky['gcnt'] = 0
    if sticky['off'] and sticky['quiet'] >= 20:
      sticky['off'] = False
  return a_


def test_parity_with_reference_random_walk(monkeypatch):
  rng = random.Random(20261111)
  p = make(monkeypatch)
  sticky = {'off': False, 'quiet': 0, 'id': None, 'd': None}
  N = 60000
  tracks = [{'id': 1, 'd': 70.0, 'v': -2.0, 'a': 0.0, 'radar': 1}, {'id': 2, 'd': 110.0, 'v': 1.0, 'a': 0.0, 'radar': 1}]
  v_ego = 22.0
  emergency = False
  mismatches = binding = 0
  for _ in range(N):
    v_ego = min(35.0, max(0.0, v_ego + rng.gauss(0, 0.05)))
    for t in tracks:
      t['v'] = min(6.0, max(-25.0, t['v'] + rng.gauss(0, 0.15) - 0.01 * t['v']))
      t['a'] = min(2.0, max(-4.0, t['a'] + rng.gauss(0, 0.2) - 0.05 * t['a']))
      t['d'] = max(1.0, t['d'] + t['v'] * 0.05)
      if rng.random() < 0.01:  # track swap: new id, new range
        t['id'] += 10 + rng.randrange(5)
        t['d'] = rng.uniform(10.0, 140.0)
        t['v'] = rng.uniform(-8.0, 3.0)
        t['radar'] = int(rng.random() < 0.8)
      if t['d'] < 6.0 or t['d'] > 160.0:
        t['d'] = rng.uniform(40.0, 120.0)
    present = [rng.random() > 0.01 for _ in tracks]
    if rng.random() < 0.002:
      present = [False, False]
    leads = [lead(t['d'], t['v'], t['a'], t['id'], bool(t['radar']), pr) for t, pr in zip(tracks, present, strict=False)]
    ref_leads = [{'id': t['id'], 'radar': t['radar'], 'd': round(t['d'], 2), 'v': round(t['v'], 2), 'a': round(t['a'], 3)}
                 for t, pr in zip(tracks, present, strict=False) if pr]
    if rng.random() < 0.003:
      emergency = not emergency
    target = rng.choice([-3.0, -2.0, -1.5, -0.9, -0.5, 0.0, 0.4]) if rng.random() < 0.3 else rng.uniform(-3.0, 0.5)
    p.emergency = emergency
    got = p.need_floor(lead_one=leads[0], lead_two=leads[1], target=target, v_ego=v_ego, reset_state=False)
    want = ref_d(sticky, ref_leads, v_ego, target, emergency)
    if got != want:
      mismatches += 1
    if want != target:
      binding += 1
  print(f'parity frames {N}, floor binding {binding}, mismatches {mismatches}')
  assert mismatches == 0
  assert binding >= 300


# NEED_FLOOR_MIN_GAP_ENABLED (static, replay only; the module constant is on, make() sets it per test): v_ego 25 -> 1.5 s headway = 37.5 m. A
# slow-closing lead (vRel -0.5) keeps
# need, ttc and the other gates open at every gap used below, so only the headway condition differs.
def test_min_gap_off_floors_inside_1p5_s(monkeypatch):
  p = make(monkeypatch, min_gap=False)
  assert run(p, steady(d=30.0, v_rel=-0.5), 20) == pytest.approx(-0.8)


def test_min_gap_on_floors_at_and_above_1p5_s(monkeypatch):
  assert run(make(monkeypatch, min_gap=True), steady(d=37.5, v_rel=-0.5), 20) == pytest.approx(-0.8)
  assert run(make(monkeypatch, min_gap=True), steady(d=60.0, v_rel=-0.5), 20) == pytest.approx(-0.8)
  assert run(make(monkeypatch, min_gap=True), steady(), 20) == pytest.approx(-0.8)


def test_min_gap_on_does_not_floor_below_1p5_s(monkeypatch):
  p = make(monkeypatch, min_gap=True)
  assert run(p, steady(d=37.4, v_rel=-0.5), 30) == -2.0
  p = make(monkeypatch, min_gap=True)
  assert run(p, steady(d=30.0, v_rel=-0.5), 30) == -2.0


def test_min_gap_is_evaluated_every_frame_not_sticky(monkeypatch):
  p = make(monkeypatch, min_gap=True)
  assert run(p, steady(d=40.0, v_rel=-0.5), 20) == pytest.approx(-0.8)
  assert nf(p, steady(d=30.0, v_rel=-0.5), -2.0) == -2.0          # inside 1.5 s: off this frame
  assert nf(p, steady(d=30.0, v_rel=-0.5), -2.0) == -2.0
  assert (p._need_floor.off, p._need_floor.quiet) == (False, 0)    # gate state untouched
  assert p._need_floor.gate_count >= hb.NEED_FLOOR_GATE_FRAMES
  assert nf(p, steady(d=40.0, v_rel=-0.5), -2.0) == pytest.approx(-0.8)  # back above 1.5 s: on again at once


def test_min_gap_default_is_on(monkeypatch):
  monkeypatch.setattr(hb, 'active_for', lambda CP: True)
  assert hb.NEED_FLOOR_MIN_GAP_ENABLED is True
  assert hb.NeedFloor().min_gap is True
  monkeypatch.setattr(hb, 'NEED_FLOOR_MIN_GAP_ENABLED', False)   # a replay harness sets the module constant before construction
  assert hb.NeedFloor().min_gap is False
  assert hb.NEED_FLOOR_MIN_GAP_S == 1.5
