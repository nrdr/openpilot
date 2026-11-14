"""Bosch-A longitudinal gates: always on for a Bosch-A Honda with openpilot longitudinal, off otherwise.

Replaces the SOURCE toggle parsing / settings-row tests (the owner toggles are removed). Static tests only.
"""
from types import SimpleNamespace
import unittest

from openpilot.nrdr.features.longitudinal.bosch_a import gate
from openpilot.nrdr.features.longitudinal.bosch_a import honda_bosch_a_long as hbl


def car(fingerprint='HONDA_CIVIC_BOSCH', brand='honda', long=True, radar_unavailable=False):
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, openpilotLongitudinalControl=long,
                         radarUnavailable=radar_unavailable)


BOSCH_A = car()
NOT_BOSCH_A = (car('TOYOTA_RAV4_TSS2_2023', brand='toyota'), car('HONDA_CIVIC'), car('HONDA_ACCORD_11G'), car(long=False))


class TestGate(unittest.TestCase):
  def test_bosch_a_with_op_long_is_on(self):
    self.assertTrue(gate.vehicle_supported(BOSCH_A))
    self.assertTrue(gate.active_for(BOSCH_A))
    self.assertTrue(gate.human_following_enabled(BOSCH_A))

  def test_other_cars_and_no_op_long_are_off(self):
    for cp in NOT_BOSCH_A:
      self.assertFalse(gate.vehicle_supported(cp), cp)
      self.assertFalse(gate.active_for(cp), cp)
      self.assertFalse(gate.human_following_enabled(cp), cp)

  def test_radar_unavailable_turns_off_radar_gates_only(self):
    cp = car(radar_unavailable=True)
    self.assertFalse(gate.active_for(cp))
    # SOURCE semantics: vehicle_supported / human following do not need the radar (vision-only shares them).
    self.assertTrue(gate.vehicle_supported(cp))
    self.assertTrue(gate.human_following_enabled(cp))

  def test_none_and_malformed_cp_are_off(self):
    self.assertFalse(gate.vehicle_supported(None))
    self.assertFalse(gate.active_for(SimpleNamespace()))

  def test_gate_matches_nrdr_radar_predicate(self):
    from openpilot.nrdr.features.radar.radar import is_honda_bosch_a_radar
    for cp in (BOSCH_A, car(radar_unavailable=True), *NOT_BOSCH_A):
      self.assertEqual(gate.active_for(cp), is_honda_bosch_a_radar(cp) and cp.openpilotLongitudinalControl, cp)

  def test_hbl_active_for_delegates_to_gate(self):
    for cp in (BOSCH_A, car(radar_unavailable=True), *NOT_BOSCH_A):
      self.assertEqual(hbl.active_for(cp), gate.active_for(cp), cp)


class TestEnhancementAlwaysOn(unittest.TestCase):
  def test_stock_feel_armed_without_a_toggle_on_bosch_a(self):
    e = hbl.HondaBoschALongEnhancement(BOSCH_A, 0.05)
    self.assertTrue(e.stock_feel)
    self.assertTrue(e.enabled)
    self.assertIsNotNone(e.drop_bound)
    self.assertIsNone(e.newborn_hold)  # RADAR_LEAD_RECOVERY stays False

  def test_nothing_armed_on_other_cars(self):
    for cp in NOT_BOSCH_A:
      e = hbl.HondaBoschALongEnhancement(cp, 0.05)
      self.assertFalse(e.enabled, cp)
      self.assertIsNone(e.drop_bound, cp)

  def test_shipped_false_constants_stay_false(self):
    self.assertFalse(hbl.STOP_EASE_ENABLED)
    self.assertFalse(hbl.RADAR_LEAD_RECOVERY)
    self.assertFalse(hbl.BIRTH_RAIL_ENABLED)


if __name__ == '__main__':
  unittest.main()
