"""Wiring of the Honda-PTM-Testing Bosch-A longitudinal modules into the nrdr CarController (static tests, no road evidence)."""
from dataclasses import replace

import pytest

from opendbc.car import structs
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

PID = structs.CarControl.Actuators.LongControlState.pid


def build(car, *, bosch_a_radar=True, mvl=False, alpha_long=True):
  config = make_test_car_config(bosch_a_radar=bosch_a_radar)
  if mvl:
    config = replace(config, honda=replace(config.honda, mvl_longitudinal=True))
  fp = {i: {} for i in range(7)}
  cp = CarInterface.get_params(car, fp, [], alpha_long, False, False, config)
  sp = CarInterface.get_params_sp(cp, car, fp, [], alpha_long, False, False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 12.0
  ci.CS.out.cruiseState.speed = 25.0
  ci.CS.out.cruiseState.available = True
  return ci


def drive(ci, accel, ticks=200):
  cc = structs.CarControl(enabled=True, longActive=True, latActive=True)
  cc.actuators.accel = accel
  cc.actuators.longControlState = PID
  sent = []
  for tick in range(ticks):
    _, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
    sent.extend(messages)
  return sent


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G, CAR.HONDA_ACCORD])
def test_bosch_a_cars_get_the_testing_modules_in_both_mvl_modes(car):
  for mvl in (False, True):
    ci = build(car, mvl=mvl)
    assert isinstance(ci.CC.bosch_longitudinal, BoschLongitudinal)
    assert ci.CC.bosch_learning_params is None  # the host sets it, like Testing's controller_extensions
    assert ci.CC.bosch_longitudinal.params.BOSCH_GAS_LOOKUP_BP == [-0.2, 2.0]


def test_star7_gas_table_is_per_car_and_leaves_nrdr_params_alone():
  civic = build(CAR.HONDA_CIVIC_BOSCH)
  assert civic.CC.bosch_longitudinal.params.BOSCH_GAS_LOOKUP_V == [0, 750]
  # nrdr's own (class-shared, mutated by other cars' interface setup) params object is not the one handed over
  assert civic.CC.params is not civic.CC.bosch_longitudinal.params
  assert build(CAR.HONDA_CRV_5G).CC.bosch_longitudinal.params.BOSCH_GAS_LOOKUP_V == [0, 1600]


@pytest.mark.parametrize("kwargs", [dict(bosch_a_radar=False), dict(alpha_long=False)])
def test_no_modules_without_the_bosch_a_radar_or_openpilot_long(kwargs):
  assert build(CAR.HONDA_CIVIC_BOSCH, **kwargs).CC.bosch_longitudinal is None


def test_non_bosch_a_cars_are_untouched():
  assert build(CAR.HONDA_CLARITY).CC.bosch_longitudinal is None
  assert build(CAR.HONDA_CIVIC).CC.bosch_longitudinal is None


def test_mvl_off_replaces_the_nrdr_brake_pid_and_factors():
  ci = build(CAR.HONDA_CIVIC_BOSCH)
  gas0, wind0, applied0 = ci.CC.gasfactor, ci.CC.windfactor, ci.CC.last_applied_brake
  sent = drive(ci, -0.6)
  assert any(addr == 0x1DF for addr, _, _ in sent)  # ACC_CONTROL
  # nrdr's own extra-brake controller and its factors are bypassed on this car
  assert ci.CC.last_applied_brake == applied0
  assert (ci.CC.gasfactor, ci.CC.windfactor) == (gas0, wind0)
  assert ci.CC.bosch_longitudinal.bosch_braking is True
  assert ci.CC.accel == pytest.approx(ci.CC.bosch_longitudinal.accel)


def test_mvl_off_calls_learning_params_persist_with_the_frame():
  ci = build(CAR.HONDA_CIVIC_BOSCH)
  frames = []
  ci.CC.bosch_learning_params = type("L", (), {"persist": lambda self, frame: frames.append(frame)})()
  drive(ci, 0.3, ticks=20)
  assert frames and frames == sorted(frames)


def test_mvl_on_keeps_mvl_path_but_uses_the_testing_civic_gas_learner():
  ci = build(CAR.HONDA_CIVIC_BOSCH, mvl=True)
  assert ci.CC.mvl_longitudinal
  learner = ci.CC.bosch_longitudinal.civic_learner
  assert learner is not None
  gas_before, alpha_before = ci.CC.gasfactor, ci.CC.gasalpha
  sent = drive(ci, 0.8, ticks=300)
  assert any(addr == 0x1DF for addr, _, _ in sent)
  # MVL's learned gas factor / alpha are not applied nor learned on this car
  assert (ci.CC.gasfactor, ci.CC.gasalpha) == (gas_before, alpha_before)
  assert ci.CC.gas > 0.0


def test_mvl_on_non_civic_keeps_mvl_learner():
  ci = build(CAR.HONDA_CRV_5G, mvl=True)
  assert ci.CC.bosch_longitudinal.civic_learner is None
  # control: MVL's own learner still runs there, so the Civic test above is not passing for lack of learning
  ci.CS.out.aEgo = 0.0
  before = ci.CC.gasfactor
  drive(ci, 0.8, ticks=300)
  assert ci.CC.gasfactor != before
