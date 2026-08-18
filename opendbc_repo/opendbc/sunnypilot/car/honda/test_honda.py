"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from opendbc.testing import parameterized

from opendbc.car import gen_empty_fingerprint
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.structs import CarParams
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.interface_ext import TORQUE_MOD_PID_CARS

CarFw = CarParams.CarFw


class TestHondaEpsMod(unittest.TestCase):

  @parameterized("car_name, fw", [(CAR.HONDA_CIVIC, b'39990-TBA,A030\x00\x00'), (CAR.HONDA_CIVIC, b'39990-TBA-A030\x00\x00'),
                                  (CAR.HONDA_CLARITY, b'39990-TRW-A020\x00\x00'), (CAR.HONDA_CLARITY, b'39990,TRW,A020\x00\x00')])
  def test_eps_mod_fingerprint(self, car_name, fw):
    fingerprint = gen_empty_fingerprint()
    car_fw = [CarFw(ecu="eps", fwVersion=fw)]

    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, car_fw, False, False, False)
    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, car_fw, False, False, False)

    self.assertFalse(CP.dashcamOnly)


class TestHondaPidTune(unittest.TestCase):

  @parameterized("car_name", TORQUE_MOD_PID_CARS)
  def test_torque_mod_four_breakpoint_pid_tune(self, car_name):
    fingerprint = gen_empty_fingerprint()
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)

    low_max = 25. * CV.MPH_TO_MS
    gain_bp = [0., low_max - 1e-3, low_max, 50. * CV.MPH_TO_MS]
    expected = (
      (CP.lateralTuning.pid.kpBP, gain_bp),
      (CP.lateralTuning.pid.kpV, [0.018, 0.024, 0.048, 0.060]),
      (CP.lateralTuning.pid.kiBP, gain_bp),
      (CP.lateralTuning.pid.kiV, [0.006, 0.008, 0.016, 0.020]),
    )
    for actual, target in expected:
      self.assertEqual(len(actual), len(target))
      for actual_value, target_value in zip(actual, target, strict=True):
        self.assertAlmostEqual(actual_value, target_value, delta=1e-6)

  @parameterized("car_name", [CAR.HONDA_ACCORD_11G, CAR.HONDA_CIVIC_2022, CAR.HONDA_NBOX_2G])
  def test_other_hondas_keep_platform_pid_tune(self, car_name):
    fingerprint = gen_empty_fingerprint()
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
    original_tune = (list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                     list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV))

    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)

    self.assertEqual((list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                      list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV)), original_tune)
