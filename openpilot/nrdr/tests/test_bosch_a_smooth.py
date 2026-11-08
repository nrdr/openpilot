"""Static tests for bosch_a_smooth (brake release limit + dwell, short plan read-ahead). Not road evidence."""
from types import SimpleNamespace
import unittest

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_smooth as bs

BOSCH_A = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True)
NOT_BOSCH_A = (SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=False),
               SimpleNamespace(brand="honda", carFingerprint="HONDA_ODYSSEY", openpilotLongitudinalControl=True),
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
    self.assertTrue(bs.BoschASmooth(BOSCH_A).enabled)
    # PR #37: every Bosch-A platform is in scope, including the Accord.
    self.assertTrue(bs.BoschASmooth(SimpleNamespace(brand="honda", carFingerprint="HONDA_ACCORD",
                                                    openpilotLongitudinalControl=True)).enabled)
    for cp in NOT_BOSCH_A + (None,):
      s = bs.BoschASmooth(cp)
      self.assertFalse(s.enabled, cp)
      self.assertEqual(s.action_t(0.5), 0.5 + DT_MDL)
      self.assertEqual(s.step(-2.0, 1.0, reset=False), 1.0)

  def test_reset_passes_through(self):
    s = bs.BoschASmooth(BOSCH_A)
    self.assertEqual(s.step(-2.0, 1.0, reset=True), 1.0)

  def test_flutter_is_held_and_release_is_slewed(self):
    # ns 25e 732.5-733.0 pattern: target alternates between hard and soft brake every cycle.
    s = bs.BoschASmooth(BOSCH_A)
    prev, outs = -1.0, []
    for target in (-1.99, -0.50, -1.70, -0.46, -1.80, -0.50):
      prev = s.step(prev, target, reset=False)
      outs.append(prev)
    self.assertEqual(outs[:3], [-1.99, -1.99, -1.99])  # the first two rise requests are held
    for a, b in zip([-1.0] + outs, outs, strict=False):
      self.assertLessEqual(b - a, STEP + 1e-9)  # then it rises at most one slew step, not to -0.46
    # A sustained release: held two ticks, then rises at most STEP per tick, never past the request.
    s = bs.BoschASmooth(BOSCH_A)
    prev = s.step(-1.0, -2.0, reset=False)  # the brake is applied first; the hold counts from here
    outs = []
    for _ in range(30):
      prev = s.step(prev, 0.5, reset=False)
      outs.append(prev)
    self.assertEqual(outs[:2], [-2.0, -2.0])
    for a, b in zip(outs, outs[1:], strict=False):
      if a < 0.0:  # the limit applies only while braking; at zero the coast/gas request passes through
        self.assertLessEqual(b - a, STEP + 1e-9)
    self.assertEqual(outs[-1], 0.5)


if __name__ == "__main__":
  unittest.main()
