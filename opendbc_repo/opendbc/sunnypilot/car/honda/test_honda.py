"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest
from dataclasses import replace

from opendbc.testing import parameterized

from opendbc.car import gen_empty_fingerprint
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.structs import CarParams
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR, HONDA_GAS_INTERCEPTOR_THRESHOLD_512
from opendbc.sunnypilot.car.honda.interface_ext import TORQUE_MOD_PID_CARS
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, HondaSafetyFlagsSP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

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


class TestHondaGasInterceptor(unittest.TestCase):

  def test_clarity_brake_safety_flag(self):
    for car_name, pedal, hybrid, stock, passive, dashcam, expected in (
      (CAR.HONDA_CLARITY, 6, True, False, False, False, True),
      (CAR.HONDA_CLARITY, 0, True, False, False, False, False),
      (CAR.HONDA_CLARITY, 8, True, False, False, False, False),
      (CAR.HONDA_CLARITY, 6, False, False, False, False, False),
      (CAR.HONDA_CLARITY, 6, True, True, False, False, False),
      (CAR.HONDA_CLARITY, 6, True, False, True, False, False),
      (CAR.HONDA_CLARITY, 6, True, False, False, True, False),
      (CAR.HONDA_CIVIC, 6, True, False, False, False, False),
      (CAR.ACURA_RLX_HYBRID, 6, True, False, False, False, False),
    ):
      with self.subTest(car=car_name, pedal=pedal, hybrid=hybrid, stock=stock, passive=passive, dashcam=dashcam):
        config = make_test_car_config()
        config = replace(config, honda=replace(config.honda, enforce_stock_longitudinal=stock, clarity_interceptor_brake_bench=True))
        fingerprint = gen_empty_fingerprint()
        if pedal:
          fingerprint[0][0x201] = pedal
        if hybrid:
          fingerprint[0][0x184] = 8
        ci = interfaces[car_name]
        cp = ci.get_params(car_name, fingerprint, [], False, False, False, interface_config=config)
        cp.passive, cp.dashcamOnly = passive, dashcam
        sp = ci.get_params_sp(cp, car_name, fingerprint, [], False, False, False)
        setup_interfaces(ci, cp, sp, config)
        self.assertEqual(bool(sp.safetyParam & HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE), expected)
        if expected:
          self.assertEqual(cp.safetyConfigs[-1].safetyParam, 0)
          self.assertEqual(sp.safetyParam, HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE | HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR)

  def test_clarity_brake_requires_active_nidec_configuration(self):
    ci = interfaces[CAR.HONDA_CLARITY]
    config = make_test_car_config()
    bench = replace(config, honda=replace(config.honda, clarity_interceptor_brake_bench=True))
    fp = gen_empty_fingerprint()
    fp[0][0x184], fp[0][0x201] = 8, 6
    for host in (None, config):
      cp = ci.get_params(CAR.HONDA_CLARITY, fp, [], False, False, False)
      sp = ci.get_params_sp(cp, CAR.HONDA_CLARITY, fp, [], False, False, False)
      setup_interfaces(ci, cp, sp, host)
      self.assertTrue(sp.flags & HondaFlagsSP.CLARITY_INTERCEPTOR_BRAKE_CAPABLE)
      self.assertEqual(sp.safetyParam, HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR)
    for model, param, op_long, docs, pedal_bus in (
      (CarParams.SafetyModel.noOutput, 0, True, False, 0),
      (CarParams.SafetyModel.hondaNidec, 4, True, False, 0),
      (CarParams.SafetyModel.hondaNidec, 0, False, False, 0),
      (CarParams.SafetyModel.hondaNidec, 0, True, True, 0),
      (CarParams.SafetyModel.hondaNidec, 0, True, False, 2),
    ):
      with self.subTest(model=model, param=param, op_long=op_long, docs=docs, pedal_bus=pedal_bus):
        fp = gen_empty_fingerprint()
        fp[0][0x184], fp[pedal_bus][0x201] = 8, 6
        cp = ci.get_params(CAR.HONDA_CLARITY, fp, [], False, False, False)
        cp.openpilotLongitudinalControl = op_long
        cp.safetyConfigs[0].safetyModel, cp.safetyConfigs[0].safetyParam = model, param
        sp = ci.get_params_sp(cp, CAR.HONDA_CLARITY, fp, [], False, False, docs)
        setup_interfaces(ci, cp, sp, bench)
        self.assertFalse(sp.safetyParam & HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE)

  @parameterized("car_name", [*HONDA_GAS_INTERCEPTOR_THRESHOLD_512, CAR.HONDA_CLARITY])
  def test_vehicle_threshold_is_forwarded_to_panda_safety(self, car_name):
    fingerprint = gen_empty_fingerprint()
    fingerprint[0][0x201] = 6
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
    CP_SP = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)

    self.assertTrue(CP_SP.enableGasInterceptor)
    self.assertTrue(CP_SP.safetyParam & HondaSafetyFlagsSP.GAS_INTERCEPTOR)
    self.assertEqual(bool(CP_SP.safetyParam & HondaSafetyFlagsSP.GAS_INTERCEPTOR_THRESHOLD_512),
                     car_name in HONDA_GAS_INTERCEPTOR_THRESHOLD_512)


class TestHondaPidTune(unittest.TestCase):

  def _assert_float_sequence(self, actual, expected, delta=1e-6):
    self.assertEqual(len(actual), len(expected))
    for actual_value, expected_value in zip(actual, expected, strict=True):
      self.assertAlmostEqual(actual_value, expected_value, delta=delta)

  @parameterized("car_name", TORQUE_MOD_PID_CARS)
  def test_torque_mod_static_pid_tune(self, car_name):
    fingerprint = gen_empty_fingerprint()
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
    original_torque = (list(CP.lateralParams.torqueBP), list(CP.lateralParams.torqueV))
    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)

    self._assert_float_sequence(CP.lateralTuning.pid.kpBP, [0.0])
    self._assert_float_sequence(CP.lateralTuning.pid.kpV, [0.03])
    self._assert_float_sequence(CP.lateralTuning.pid.kiBP, [0.0])
    self._assert_float_sequence(CP.lateralTuning.pid.kiV, [0.01])
    self.assertAlmostEqual(CP.lateralTuning.pid.kf, 0.000012, delta=1e-12)
    self.assertEqual(list(CP.lateralTuning.pid.kfBP), [])
    self.assertEqual(list(CP.lateralTuning.pid.kfV), [])

    torque_limits = {
      CAR.HONDA_CIVIC: 3840,
      CAR.HONDA_CIVIC_BOSCH: 3840,
      CAR.HONDA_CIVIC_BOSCH_DIESEL: 4096,
      CAR.HONDA_CLARITY: 3840,
      CAR.HONDA_CRV_5G: 4096,
      CAR.HONDA_INSIGHT: 3840,
    }
    if car_name in torque_limits:
      torque_limit = torque_limits[car_name]
      self.assertEqual((list(CP.lateralParams.torqueBP), list(CP.lateralParams.torqueV)),
                       ([0, torque_limit], [0, torque_limit]))
    else:
      self.assertEqual((list(CP.lateralParams.torqueBP), list(CP.lateralParams.torqueV)), original_torque)

  @parameterized("car_name", [
    CAR.HONDA_ACCORD_11G,
    CAR.HONDA_CIVIC_2022,
    CAR.HONDA_CRV_6G,
    CAR.ACURA_MDX_4G,
  ])
  def test_other_hondas_keep_platform_pid_tune(self, car_name):
    fingerprint = gen_empty_fingerprint()
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
    original_tune = (list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                     list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV),
                     CP.lateralTuning.pid.kf, list(CP.lateralTuning.pid.kfBP), list(CP.lateralTuning.pid.kfV))

    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)

    self.assertEqual((list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                      list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV),
                      CP.lateralTuning.pid.kf, list(CP.lateralTuning.pid.kfBP), list(CP.lateralTuning.pid.kfV)), original_tune)

  def test_nbox_keeps_existing_extended_torque_feedforward_tune(self):
    fingerprint = gen_empty_fingerprint()
    CarInterface = interfaces[CAR.HONDA_NBOX_2G]
    CP = CarInterface.get_params(CAR.HONDA_NBOX_2G, fingerprint, [], False, False, False)
    original_pid = (list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                    list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV))

    _ = CarInterface.get_params_sp(CP, CAR.HONDA_NBOX_2G, fingerprint, [], False, False, False)

    low_max = 25. * CV.MPH_TO_MS
    self.assertEqual((list(CP.lateralTuning.pid.kpBP), list(CP.lateralTuning.pid.kpV),
                      list(CP.lateralTuning.pid.kiBP), list(CP.lateralTuning.pid.kiV)), original_pid)
    self.assertEqual((list(CP.lateralParams.torqueBP), list(CP.lateralParams.torqueV)),
                     ([0, 4096], [0, 4096]))
    self.assertAlmostEqual(CP.lateralTuning.pid.kf, 0.0000036, delta=1e-12)
    self._assert_float_sequence(CP.lateralTuning.pid.kfBP, [0., low_max - 1e-3, low_max, 50. * CV.MPH_TO_MS])
    self._assert_float_sequence(CP.lateralTuning.pid.kfV, [0.0000024, 0.0000018, 0.0000036, 0.000006], delta=1e-12)
