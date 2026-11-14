import math
import unittest
from types import SimpleNamespace

from opendbc.car.honda.hondacan import bosch_force_command_state, create_acc_commands
from opendbc.car.honda.values import HondaFlags


class FakePacker:
  def make_can_msg(self, name, bus, values):
    return name, bus, dict(values)


def _acc_control(force, *, active=True, accel=-0.25, flags=0, stopping_counter=0):
  commands = create_acc_commands(
    FakePacker(),
    SimpleNamespace(pt=0),
    enabled=active,
    active=active,
    accel=accel,
    gas=123,
    stopping_counter=stopping_counter,
    CP=SimpleNamespace(flags=HondaFlags(flags)),
    gas_force=force,
  )
  return next(values for name, _, values in commands if name == "ACC_CONTROL")


class TestBoschForceCommandState(unittest.TestCase):
  def test_sign_boundaries_are_mutually_exclusive(self):
    for force, expected in ((-1e-12, (False, True)), (0.0, (False, False)), (1e-12, (True, False))):
      with self.subTest(force=force):
        self.assertEqual(bosch_force_command_state(True, force), expected)

  def test_inactive_and_nonfinite_fail_closed(self):
    for force in (-1.0, 0.0, 1.0, math.nan, math.inf, -math.inf):
      with self.subTest(force=force):
        self.assertEqual(bosch_force_command_state(False, force), (False, False))
    for force in (math.nan, math.inf, -math.inf):
      with self.subTest(force=force):
        self.assertEqual(bosch_force_command_state(True, force), (False, False))

  def test_classic_acc_control_uses_one_force_decision(self):
    for force, gas, brake in ((-1e-12, -30000, 1), (0.0, -30000, 0), (1e-12, 123, 0)):
      with self.subTest(force=force):
        values = _acc_control(force)
        self.assertEqual(values["GAS_COMMAND"], gas)
        self.assertEqual(values["BRAKE_REQUEST"], brake)
        self.assertEqual(values["BRAKE_LIGHTS"], brake)
        self.assertFalse(values["GAS_COMMAND"] != -30000 and values["BRAKE_REQUEST"])

  def test_positive_compensated_force_cannot_overlap_negative_accel_brake(self):
    values = _acc_control(0.05, accel=-0.25)
    self.assertEqual(values["GAS_COMMAND"], 123)
    self.assertEqual(values["BRAKE_REQUEST"], 0)
    self.assertEqual(values["BRAKE_LIGHTS"], 0)

  def test_inactive_classic_command_has_no_gas_or_brake(self):
    for force in (-1.0, 1.0):
      with self.subTest(force=force):
        values = _acc_control(force, active=False)
        self.assertEqual(values["GAS_COMMAND"], -30000)
        self.assertEqual(values["BRAKE_REQUEST"], 0)
        self.assertEqual(values["BRAKE_LIGHTS"], 0)

  def test_radarless_brake_assist_uses_same_force_decision(self):
    flags = HondaFlags.BOSCH_RADARLESS | HondaFlags.HYBRID
    self.assertEqual(_acc_control(-1e-12, flags=flags)["COMPUTER_BRAKE_ASSIST"], 1)
    self.assertEqual(_acc_control(0.0, flags=flags)["COMPUTER_BRAKE_ASSIST"], 0)
    self.assertEqual(_acc_control(1e-12, flags=flags)["COMPUTER_BRAKE_ASSIST"], 0)
