"""Static tests for bosch_a_release: release coast, brake release limit + dwell, short plan read-ahead, and the combined step. Not road evidence."""
from types import SimpleNamespace
import random
import unittest
from unittest import mock

from openpilot.common.realtime import DT_MDL
from openpilot.cereal import log
from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_release as bs

BOSCH_A = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True)
NOT_BOSCH_A = (SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=False),
               SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_2022", openpilotLongitudinalControl=True),
               SimpleNamespace(brand="toyota", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True))
STEP = bs.BRAKE_RELEASE_JERK * DT_MDL


class TestHelpers(unittest.TestCase):
  def test_release_limit_only_slows_a_rising_brake(self):
    self.assertAlmostEqual(bs.brake_release_limited_target(-2.0, 0.5, DT_MDL), -2.0 + STEP)
    self.assertEqual(bs.brake_release_limited_target(-2.0, -3.0, DT_MDL), -3.0)  # onset never limited
    self.assertEqual(bs.brake_release_limited_target(0.2, 1.0, DT_MDL), 1.0)    # throttle untouched
    self.assertEqual(bs.brake_release_limited_target(0.0, 1.0, DT_MDL), 1.0)

  def test_dwell_holds_brake_two_ticks_then_releases(self):
    ticks = bs.BRAKE_RELEASE_DWELL_TICKS + 1
    out, ticks = bs.brake_release_dwell_target(-1.0, -1.2, ticks)
    self.assertEqual((out, ticks), (-1.2, 0))  # more braking passes and resets the count
    for _ in range(bs.BRAKE_RELEASE_DWELL_TICKS):
      out, ticks = bs.brake_release_dwell_target(-1.2, -1.0, ticks)
      self.assertEqual(out, -1.2)
    out, ticks = bs.brake_release_dwell_target(-1.2, -1.0, ticks)
    self.assertEqual(out, -1.0)

  def test_dwell_never_holds_throttle(self):
    out, _ = bs.brake_release_dwell_target(0.1, 0.5, 0)
    self.assertEqual(out, 0.5)

  def test_action_t(self):
    self.assertEqual(bs.planner_action_t(0.5, False), 0.5 + DT_MDL)
    self.assertEqual(bs.planner_action_t(0.5, True), bs.PLANNER_ACTION_T_S)
    self.assertEqual(bs.planner_action_t(0.05, True), 0.05 + DT_MDL)  # never longer than the car's own


class TestShaper(unittest.TestCase):
  def test_gate(self):
    self.assertTrue(bs.BoschARelease(BOSCH_A).enabled)
    for cp in NOT_BOSCH_A + (None,):
      s = bs.BoschARelease(cp)
      self.assertFalse(s.enabled, cp)
      self.assertEqual(s.action_t(0.5), 0.5 + DT_MDL)
      self.assertEqual(s.smooth(-2.0, 1.0, reset=False), 1.0)

  def test_reset_passes_through(self):
    s = bs.BoschARelease(BOSCH_A)
    self.assertEqual(s.smooth(-2.0, 1.0, reset=True), 1.0)

  def test_flutter_is_held_and_release_is_slewed(self):
    # ns 25e 732.5-733.0 pattern: target alternates between hard and soft brake every cycle.
    s = bs.BoschARelease(BOSCH_A)
    prev, outs = -1.0, []
    for target in (-1.99, -0.50, -1.70, -0.46, -1.80, -0.50):
      prev = s.smooth(prev, target, reset=False)
      outs.append(prev)
    self.assertEqual(outs[:3], [-1.99, -1.99, -1.99])  # the first two rise requests are held
    for a, b in zip([-1.0] + outs, outs, strict=False):
      self.assertLessEqual(b - a, STEP + 1e-9)  # then it rises at most one slew step, not to -0.46
    # A sustained release: held two ticks, then rises at most STEP per tick, never past the request.
    s = bs.BoschARelease(BOSCH_A)
    prev = s.smooth(-1.0, -2.0, reset=False)  # the brake is applied first; the hold counts from here
    outs = []
    for _ in range(30):
      prev = s.smooth(prev, 0.5, reset=False)
      outs.append(prev)
    self.assertEqual(outs[:2], [-2.0, -2.0])
    for a, b in zip(outs, outs[1:], strict=False):
      if a < 0.0:  # the limit applies only while braking; at zero the coast/gas request passes through
        self.assertLessEqual(b - a, STEP + 1e-9)
    self.assertEqual(outs[-1], 0.5)


LaneChangeState = log.LaneChangeState


def _lead(present, d, v, track_id=39):
  return SimpleNamespace(present=present, dRel=d, vRel=v, radarTrackId=track_id)


class TestStep(unittest.TestCase):
  def setUp(self):
    # unittest runner (tools/test_runner.py) does not apply the pytest autouse fixture below; pin the coast + FastLetoff step here.
    patcher = mock.patch.object(bs, 'GHOST_ARM', False)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_step_is_coast_then_smooth(self):
    cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True, radarUnavailable=False)
    a, b = bs.BoschARelease(cp), bs.BoschARelease(cp)
    seq = [(_lead(True, 21.0, -7.0), -1.8, -1.0, False, False), (_lead(True, 84.0, 0.0, -1), 0.5, -1.8, False, False),
           (_lead(True, 90.0, 0.0, -1), 0.5, -1.7, False, False), (_lead(False, 0.0, 0.0), 0.4, -1.6, False, True),
           (_lead(True, 20.0, -1.0, 7), -1.0, 0.0, True, False), (_lead(True, 20.0, -1.0, 7), -2.0, -1.0, False, False)]
    for ld, target, prev, reset, standstill in seq:
      got = a.step(lead_one=ld, prev=prev, target=target, reset_state=reset, standstill=standstill)
      mid = b.coast(lead_one=ld, target=target, reset_state=reset)
      want = b.smooth(prev, mid, reset=bool(reset or standstill))
      self.assertEqual(got, want)
      self.assertEqual((a.hold_s, a.rise_ticks), (b.hold_s, b.rise_ticks))


class TestStepParity(unittest.TestCase):
  def setUp(self):
    # unittest runner (tools/test_runner.py) does not apply the pytest autouse fixture below; pin the coast + FastLetoff step here.
    patcher = mock.patch.object(bs, 'GHOST_ARM', False)
    patcher.start()
    self.addCleanup(patcher.stop)

  """Self-contained: one instance driven through step() vs a twin driven through coast() then smooth(), random cycles."""
  def test_random_cycles_match_twin(self):
    rng = random.Random(7)
    for radar_unavailable in (True, False):
      for cp in (BOSCH_A,) + NOT_BOSCH_A:
        cp = SimpleNamespace(**vars(cp), radarUnavailable=radar_unavailable)
        a, b = bs.BoschARelease(cp), bs.BoschARelease(cp)
        for _ in range(3000):
          ld = None if rng.random() < 0.05 else _lead(rng.random() < 0.8, rng.uniform(0, 100), rng.uniform(-10, 5), rng.choice((-1, 3, 39, 41)))
          kw = {'lead_one': ld, 'target': rng.uniform(-4, 2),
                'lane_change_state': rng.choice((None, LaneChangeState.off, LaneChangeState.laneChangeStarting)),
                'left_blinker': rng.random() < 0.1, 'right_blinker': rng.random() < 0.1, 'gas_pressed': rng.random() < 0.1}
          prev, reset, standstill = rng.uniform(-4, 2), rng.random() < 0.05, rng.random() < 0.05
          got = a.step(prev=prev, reset_state=reset, standstill=standstill, **kw)  # ty: ignore[invalid-argument-type]
          want = b.smooth(prev, b.coast(reset_state=reset, **kw), reset=bool(reset or standstill))
          self.assertEqual(got, want)
          self.assertEqual((a.hold_s, a.rise_ticks, a.prev_lead), (b.hold_s, b.rise_ticks, b.prev_lead))


# Release coast tests (pytest style)


def lead(present, d, v, track_id=39):
  return SimpleNamespace(present=present, dRel=d, vRel=v, radarTrackId=track_id)


def planner(monkeypatch):
  monkeypatch.setattr(bs, 'vehicle_supported', lambda CP: True)
  return bs.BoschARelease(SimpleNamespace(radarUnavailable=False))


def cstep(p, ld, target, lane_change_state=LaneChangeState.off, left_blinker=False, right_blinker=False,
         gas_pressed=False):
  return p.coast(lead_one=ld, target=target, lane_change_state=lane_change_state, left_blinker=left_blinker,
                   right_blinker=right_blinker, gas_pressed=gas_pressed, reset_state=False)


def test_9e_release_withholds_gas_for_the_hold(monkeypatch):
  # route 9e: radar track 39 at 21 m closing -7 m/s, released to a camera lead 84 m away, planner asks +0.5
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  out = cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5)
  assert out == 0.0
  for _ in range(19):
    out = cstep(p, lead(True, 90.0, 0.0, track_id=-1), 0.5)
  assert out == 0.0  # still inside HOLD_S (1.0 s at DT_MDL=0.05)
  out = cstep(p, lead(True, 95.0, 0.0, track_id=-1), 0.5)
  assert out == 0.5  # hold elapsed, resumes


def test_lead_lost_entirely_caps_like_a_release(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert cstep(p, lead(False, 0.0, 0.0), 0.5) == 0.0


def test_previous_lead_not_closing_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -1.0), -1.8) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_previous_lead_far_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 60.0, -7.0), -1.8) == -1.8
  assert cstep(p, lead(True, 90.0, 0.0, track_id=-1), 0.5) == 0.5


def test_lane_change_active_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8, lane_change_state=LaneChangeState.laneChangeStarting) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, lane_change_state=LaneChangeState.laneChangeStarting) == 0.5


def test_blinker_on_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8, right_blinker=True) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, right_blinker=True) == 0.5


def test_gas_pressed_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, gas_pressed=True) == 0.5


def test_negative_target_during_hold_passes_through(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), -0.3) == -0.3


def test_new_close_closing_lead_ends_the_hold(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.0
  # a new, closing lead inside RELEASE_D_MAX shows up mid-hold: ends the hold (the cap is harmless there anyway,
  # since the planner's own target would already be braking for it)
  assert cstep(p, lead(True, 25.0, -3.0, track_id=41), 0.5) == 0.5
  assert cstep(p, lead(True, 28.0, -3.0, track_id=41), 0.5) == 0.5


def test_normal_handover_small_jump_no_cap(monkeypatch):
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0), -1.8) == -1.8
  # handover to a nearer or slightly farther radar lead (jump < RELEASE_JUMP_M)
  assert cstep(p, lead(True, 35.0, -1.0, track_id=41), 0.5) == 0.5


def test_previous_lead_vision_only_no_cap(monkeypatch):
  # previous leadOne was vision-only (radarTrackId -1), not a radar-matched track: not a release
  p = planner(monkeypatch)
  assert cstep(p, lead(True, 21.0, -7.0, track_id=-1), -1.8) == -1.8
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_gas_pressed_mid_hold_ends_the_hold(monkeypatch):
  p = planner(monkeypatch)
  cstep(p, lead(True, 21.0, -7.0), -1.8)
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.0
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5, gas_pressed=True) == 0.5
  assert cstep(p, lead(True, 84.0, 0.0, track_id=-1), 0.5) == 0.5


def test_previous_lead_is_copied_not_aliased(monkeypatch):
  # a reused radarState lead object mutated in place must still show the release
  p = planner(monkeypatch)
  ld = lead(True, 21.0, -7.0)
  cstep(p, ld, -1.8)
  ld.dRel, ld.vRel, ld.radarTrackId = 84.0, 0.0, -1
  assert cstep(p, ld, 0.5) == 0.0


if __name__ == "__main__":
  unittest.main()


import pytest


@pytest.fixture(autouse=True)
def _no_ghost_arm(monkeypatch):
  """These tests pin the car build's step (coast + FastLetoff); arm G replaces it and has its own tests."""
  from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_release
  monkeypatch.setattr(bosch_a_release, 'GHOST_ARM', False)
