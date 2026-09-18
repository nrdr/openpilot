import unittest

from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, HONDA_BOSCH, HONDA_BOSCH_CANFD, HondaFlags


class TestHondaFingerprint(unittest.TestCase):
  def test_tja_bosch_only(self):
    for car_model in CAR:
      if car_model.config.flags & HondaFlags.BOSCH_TJA_CONTROL:
        assert car_model.config.flags & HondaFlags.BOSCH, "Nidec car found with TJA control"


class TestHondaParameters(unittest.TestCase):
  def test_bosch_longitudinal_actuator_delay(self):
    for car_model in HONDA_BOSCH:
      with self.subTest(car_model=car_model):
        CP = CarInterface.get_non_essential_params(car_model)
        expected_delay = 0.05 if car_model in HONDA_BOSCH_CANFD else 0.25
        self.assertAlmostEqual(CP.longitudinalActuatorDelay, expected_delay)
