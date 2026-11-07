"""Clarity SP flags must remain plain integers at the host serialization boundary."""
from dataclasses import replace
from itertools import product
import unittest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, HondaSafetyFlagsSP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


class TestClarityFlags(unittest.TestCase):
  def test_actual_interface_returns_plain_int_without_changing_capability_or_safety_bits(self):
    for hybrid, pedal_size, modified_eps, stock_long in product((False, True), (0, 6, 8), (False, True), (False, True)):
      with self.subTest(hybrid=hybrid, pedal_size=pedal_size, modified_eps=modified_eps, stock_long=stock_long):
        fingerprint = gen_empty_fingerprint()
        fingerprint[0][0x1A3] = 8
        if hybrid:
          fingerprint[0][0x184] = 8
        if pedal_size:
          fingerprint[0][0x201] = pedal_size
        firmware = [structs.CarParams.CarFw(ecu='eps', fwVersion=b'39990,TRW,A020' if modified_eps else b'39990-TRW-A020')]
        config = make_test_car_config(honda_stock_longitudinal=stock_long)
        cp = CarInterface.get_params(CAR.HONDA_CLARITY, fingerprint, firmware, False, False, False, interface_config=config)
        sp = CarInterface.get_params_sp(cp, CAR.HONDA_CLARITY, fingerprint, firmware, False, False, False)
        expected_flags = (HondaFlagsSP.NIDEC_HYBRID.value if hybrid else 0) | (HondaFlagsSP.EPS_MODIFIED.value if modified_eps else 0)
        if hybrid and pedal_size == 6:
          expected_flags |= HondaFlagsSP.CLARITY_INTERCEPTOR_BRAKE_CAPABLE.value
        expected_safety = (HondaSafetyFlagsSP.NIDEC_HYBRID if hybrid else 0) | (HondaSafetyFlagsSP.GAS_INTERCEPTOR if pedal_size else 0)
        self.assertIs(type(sp.flags), int)  # isinstance(IntFlag, int) would miss the serializer failure.
        self.assertEqual(sp.flags, expected_flags)
        self.assertEqual(sp.safetyParam, expected_safety)

        setup_interfaces(CarInterface, cp, sp, config)
        self.assertIs(type(sp.flags), int)
        self.assertEqual(sp.flags, expected_flags | (HondaFlagsSP.STOCK_LONGITUDINAL.value if stock_long else 0))
        self.assertEqual(sp.safetyParam, expected_safety | (HondaSafetyFlagsSP.STOCK_LONGITUDINAL if stock_long else 0))
        self.assertFalse(sp.safetyParam & HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE)

  def test_explicit_bench_safety_admission_does_not_change_flag_type_or_bits(self):
    fingerprint = gen_empty_fingerprint()
    fingerprint[0].update({0x184: 8, 0x201: 6})
    config = make_test_car_config()
    config = replace(config, honda=replace(config.honda, clarity_interceptor_brake_bench=True))
    cp = CarInterface.get_params(CAR.HONDA_CLARITY, fingerprint, [], False, False, False, interface_config=config)
    sp = CarInterface.get_params_sp(cp, CAR.HONDA_CLARITY, fingerprint, [], False, False, False)
    setup_interfaces(CarInterface, cp, sp, config)
    self.assertIs(type(sp.flags), int)
    self.assertEqual(sp.flags, HondaFlagsSP.NIDEC_HYBRID.value | HondaFlagsSP.CLARITY_INTERCEPTOR_BRAKE_CAPABLE.value)
    self.assertEqual(sp.safetyParam, HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR | HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE)
