import unittest

from opendbc.car.honda.nidec_long_helpers import nidec_speed_lead_mps


class TestNidecSpeedLead(unittest.TestCase):
  def test_poisoned_alpha_floor_from_route_21_seg62(self):
    # Ridgeline route 7862788bd18c1a53/21 seg 62: cmd ~0.17, sf_low ~2.18, alpha ~-0.66 -> lead -0.29
    sf = 2.177781581878662
    accel = 0.17166689038276672
    alpha = -0.6604037894504735
    lead = nidec_speed_lead_mps(sf, accel, alpha)
    self.assertGreaterEqual(lead, 0.35)
    self.assertAlmostEqual(lead, 0.35, places=2)

  def test_coasting_plan_unchanged(self):
    self.assertAlmostEqual(nidec_speed_lead_mps(2.0, 0.0, -0.5), -0.5)

  def test_healthy_alpha_unchanged(self):
    self.assertAlmostEqual(nidec_speed_lead_mps(2.5, 0.4, 0.2), 1.2)


if __name__ == "__main__":
  unittest.main()
