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

  def test_long_tuning_active_is_the_one_radar_gate(self):
    # Biscuit-Labs bosch_a_toggles.long_tuning_active: verified Bosch-A Honda, openpilot long, radar on. active_for is its alias.
    self.assertIs(gate.active_for, gate.long_tuning_active)
    self.assertTrue(gate.long_tuning_active(BOSCH_A))
    self.assertFalse(gate.long_tuning_active(car(radar_unavailable=True)))
    for cp in NOT_BOSCH_A:
      self.assertFalse(gate.long_tuning_active(cp), cp)

  def test_gate_covers_all_fourteen_verified_bosch_a_cars(self):
    # D1: nrdr's HONDA_BOSCH_A now follows the platform table (opendbc fa47f331); needs the opendbc worktree at that commit.
    from opendbc.car.honda.values import HONDA_BOSCH_A
    self.assertEqual(len(HONDA_BOSCH_A), 14)
    for fingerprint in HONDA_BOSCH_A:
      self.assertTrue(gate.long_tuning_active(car(str(fingerprint))), fingerprint)

  def test_hbl_active_for_delegates_to_gate(self):
    for cp in (BOSCH_A, car(radar_unavailable=True), *NOT_BOSCH_A):
      self.assertEqual(hbl.active_for(cp), gate.active_for(cp), cp)


class TestEnhancementAlwaysOn(unittest.TestCase):
  def test_stock_feel_armed_without_a_toggle_on_bosch_a(self):
    e = hbl.HondaBoschALongEnhancement(BOSCH_A, 0.05)
    self.assertTrue(e.stock_feel)
    self.assertTrue(e.coast_enabled)  # the tip class has no `enabled`; stock_feel / coast_enabled carry the gate
    self.assertIsNotNone(e.drop_bound)
    self.assertTrue(hbl.NEWBORN_HOLD_ENABLED)
    self.assertIsNotNone(e.newborn_hold)  # independent of RADAR_LEAD_RECOVERY

  def test_nothing_armed_on_other_cars(self):
    for cp in NOT_BOSCH_A:
      e = hbl.HondaBoschALongEnhancement(cp, 0.05)
      self.assertFalse(e.stock_feel, cp)
      self.assertFalse(e.coast_enabled, cp)
      self.assertIsNone(e.drop_bound, cp)

  def test_shipped_switch_constants(self):
    # The tip removed STOP_EASE_ENABLED / RADAR_LEAD_RECOVERY / BIRTH_RAIL_ENABLED; these are the switches it keeps.
    self.assertTrue(hbl.NEED_FLOOR_ENABLED)
    self.assertTrue(hbl.NEED_FLOOR_MIN_GAP_ENABLED)
    self.assertTrue(hbl.NEWBORN_HOLD_ENABLED)
    for removed in ('STOP_EASE_ENABLED', 'RADAR_LEAD_RECOVERY', 'BIRTH_RAIL_ENABLED'):
      self.assertFalse(hasattr(hbl, removed), removed)


if __name__ == '__main__':
  unittest.main()
