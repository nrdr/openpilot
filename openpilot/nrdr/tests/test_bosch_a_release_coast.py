from types import SimpleNamespace

from openpilot.cereal import log
from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_release_coast as rc

LaneChangeState = log.LaneChangeState


def lead(present, d, v, track_id=39):
  return SimpleNamespace(present=present, dRel=d, vRel=v, radarTrackId=track_id)


def planner(monkeypatch):
  monkeypatch.setattr(rc, 'vehicle_supported', lambda CP: True)
  return rc.BoschAReleaseCoast(SimpleNamespace(radarUnavailable=False))


def step(p, ld, target, lane_change_state=LaneChangeState.off, left_blinker=False, right_blinker=False,
         gas_pressed=False):
  return p.update(lead_one=ld, target=target, lane_change_state=lane_change_state, left_blinker=left_blinker,
                   right_blinker=right_blinker, gas_pressed=gas_pressed, reset_state=False)


def test_9e_release_withholds_gas_for_the_hold(monkeypatch):
  # route 9e: radar track 39 at 21 m closing -7 m/s, released to a camera lead 84 m away, planner asks +0.5
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  out = step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5)
  assert out == 0.0
  for _ in range(19):
    out = step(p, lead(True, 90.0, 0.0, track_id=-1), 0.5)
  assert out == 0.0  # still inside HOLD_S (1.0 s at DT_MDL=0.05)
  out = step(p, lead(True, 95.0, 0.0, track_id=-1), 0.5)
  assert out == 0.5  # hold elapsed, resumes


def test_lead_lost_entirely_caps_like_a_release(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert step(p, lead(False, 0.0, 0.0), 0.5) == 0.0


def test_previous_lead_not_closing_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -1.0), -1.8) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_previous_lead_far_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 60.0, -7.0), -1.8) == -1.8
  assert step(p, lead(True, 90.0, 0.0, track_id=-1), 0.5) == 0.5


def test_lane_change_active_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8, lane_change_state=LaneChangeState.laneChangeStarting) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, lane_change_state=LaneChangeState.laneChangeStarting) == 0.5


def test_blinker_on_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8, right_blinker=True) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, right_blinker=True) == 0.5


def test_gas_pressed_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, gas_pressed=True) == 0.5


def test_negative_target_during_hold_passes_through(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), -0.3) == -0.3


def test_new_close_closing_lead_ends_the_hold(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.0
  # a new, closing lead inside RELEASE_D_MAX shows up mid-hold: ends the hold (the cap is harmless there anyway,
  # since the planner's own target would already be braking for it)
  assert step(p, lead(True, 25.0, -3.0, track_id=41), 0.5) == 0.5
  assert step(p, lead(True, 28.0, -3.0, track_id=41), 0.5) == 0.5


def test_normal_handover_small_jump_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  # handover to a nearer or slightly farther radar lead (jump < RELEASE_JUMP_M)
  assert step(p, lead(True, 35.0, -1.0, track_id=41), 0.5) == 0.5


def test_previous_lead_vision_only_no_cap(monkeypatch):
  # previous leadOne was vision-only (radarTrackId -1), not a radar-matched track: not a release
  p = planner(monkeypatch)
  assert step(p, lead(True, 21.0, -7.0, track_id=-1), -1.8) == -1.8
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_gas_pressed_mid_hold_ends_the_hold(monkeypatch):
  p = planner(monkeypatch)
  step(p, lead(True, 21.0, -7.0), -1.8)
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.0
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, gas_pressed=True) == 0.5
  assert step(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_previous_lead_is_copied_not_aliased(monkeypatch):
  # a reused radarState lead object mutated in place must still show the release
  p = planner(monkeypatch)
  ld = lead(True, 21.0, -7.0)
  step(p, ld, -1.8)
  ld.dRel, ld.vRel, ld.radarTrackId = 84.0, 0.0, -1
  assert step(p, ld, 0.5) == 0.0
