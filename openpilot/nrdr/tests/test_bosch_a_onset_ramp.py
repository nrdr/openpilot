"""Static tests for bosch_a_onset_ramp (stock-like brake onset for far leads). Not road evidence."""
from types import SimpleNamespace
import unittest

from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_onset_ramp as orp

BOSCH_A = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True,
                          radarUnavailable=False)
OTHER = SimpleNamespace(brand="toyota", carFingerprint="TOYOTA_RAV4", openpilotLongitudinalControl=True,
                        radarUnavailable=False)
NONE = SimpleNamespace(present=False, dRel=0.0, vRel=0.0)
DT = 0.05
STEP = orp.ONSET_JERK * DT


def lead(d, v_rel):
  return SimpleNamespace(present=True, dRel=d, vRel=v_rel)


def run(ramp, l1, targets, prev=0.0, fcw=False, stopping=False, l2=NONE):
  out = []
  for target in targets:
    prev = ramp.step(lead_one=l1, lead_two=l2, prev=prev, target=target, fcw=fcw, stopping=stopping, reset=False)
    out.append(prev)
  return out


class TestOnsetRamp(unittest.TestCase):
  def test_far_brake_builds_at_onset_jerk_and_reaches_the_peak(self):
    # 84 E1: lead ~93 m, closing 7.4 m/s, target steps 0 -> -3.5 in one frame
    out = run(orp.BoschAOnsetRamp(BOSCH_A, DT), lead(93.0, -7.4), [-3.5] * 12)
    self.assertAlmostEqual(out[0], -STEP)
    for a, b in zip(out, out[1:], strict=False):
      self.assertGreaterEqual(b, a - STEP - 1e-9)
    self.assertEqual(out[-1], -3.5)  # the peak is never reduced

  def test_close_lead_at_onset_is_exempt_for_the_episode(self):
    # 2f5 11830: onset with the lead at 38.1 m
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    self.assertEqual(run(ramp, lead(38.1, -2.0), [-3.5]), [-3.5])
    self.assertTrue(ramp.free)
    # still exempt while the episode lasts, even after the lead reads farther
    self.assertEqual(run(ramp, lead(45.0, -2.0), [-2.0, -3.0], prev=-3.5), [-2.0, -3.0])

  def test_episode_decision_is_latched_until_the_brake_ends(self):
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    run(ramp, lead(80.0, -3.0), [-1.0])
    self.assertFalse(ramp.free)
    # closing to 39 m mid-brake does not exempt it (R5 replay: no gain); TTC 39/3 = 13 s
    self.assertAlmostEqual(run(ramp, lead(39.0, -3.0), [-3.0], prev=-0.4)[0], -0.4 - STEP)
    # the brake ends, a new one starts with the lead close: exempt
    run(ramp, lead(39.0, -3.0), [0.0], prev=-1.0)
    self.assertFalse(ramp.in_episode)
    self.assertEqual(run(ramp, lead(39.0, -3.0), [-2.0])[0], -2.0)

  def test_low_ttc_stands_down_for_the_rest_of_the_episode(self):
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    run(ramp, lead(60.0, -10.0), [-3.5])
    self.assertEqual(run(ramp, lead(50.0, -25.0), [-3.5], prev=-0.4), [-3.5])  # TTC 2.0 s
    self.assertEqual(run(ramp, lead(60.0, -5.0), [-3.5], prev=-3.5), [-3.5])  # stays down

  def test_railed_vrel_only_shortens_ttc(self):
    # U11 low rail vRel -12 at 22 m/s... the TTC check reads it as published, which can only stand the ramp down
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    self.assertEqual(run(ramp, lead(23.0, -12.0), [-3.5]), [-3.5])  # also under the 40 m exemption
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    run(ramp, lead(80.0, -5.0), [-1.0])
    self.assertEqual(run(ramp, lead(24.0, -12.0), [-3.5], prev=-0.4), [-3.5])

  def test_fcw_and_stopping_pass_through(self):
    self.assertEqual(run(orp.BoschAOnsetRamp(BOSCH_A, DT), lead(90.0, -5.0), [-3.5], fcw=True), [-3.5])
    self.assertEqual(run(orp.BoschAOnsetRamp(BOSCH_A, DT), lead(90.0, -5.0), [-3.5], stopping=True), [-3.5])

  def test_second_lead_close_exempts(self):
    out = run(orp.BoschAOnsetRamp(BOSCH_A, DT), lead(90.0, -5.0), [-3.5], l2=lead(20.0, 0.0))
    self.assertEqual(out, [-3.5])

  def test_no_lead_brake_is_ramped(self):
    # cruise/curve slowdowns with no lead: capped, as in the replay (onsets with dRel -1)
    out = run(orp.BoschAOnsetRamp(BOSCH_A, DT), NONE, [-2.0, -2.0])
    self.assertAlmostEqual(out[0], -STEP)

  def test_gentle_target_and_rises_pass_through(self):
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    self.assertEqual(run(ramp, lead(90.0, -2.0), [-0.25, 0.5, 1.0]), [-0.25, 0.5, 1.0])
    self.assertFalse(ramp.in_episode)
    # the ramp starts from min(prev, 0): a throttle cut to zero is immediate
    self.assertAlmostEqual(run(orp.BoschAOnsetRamp(BOSCH_A, DT), lead(90.0, -2.0), [-1.0], prev=1.2)[0], -STEP)

  def test_reset_and_other_cars_pass_through(self):
    ramp = orp.BoschAOnsetRamp(BOSCH_A, DT)
    run(ramp, lead(90.0, -5.0), [-1.0])
    self.assertEqual(ramp.step(lead_one=lead(90.0, -5.0), lead_two=NONE, prev=-0.4, target=-3.5, fcw=False,
                               stopping=False, reset=True), -3.5)
    self.assertFalse(ramp.in_episode)
    self.assertEqual(run(orp.BoschAOnsetRamp(OTHER, DT), lead(90.0, -5.0), [-3.5]), [-3.5])


if __name__ == "__main__":
  unittest.main()
