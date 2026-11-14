import math
from types import SimpleNamespace

import pytest

from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, gen_empty_fingerprint, structs
from opendbc.car.honda import bosch_gas_learner as gl
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal, star7_params
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

FLAT = gl.CIVIC_PITCH_BIAS


def owner(identity=CAR.HONDA_CIVIC_BOSCH):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
  return BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))


def inputs(speed=20.0, measured=0.0, active=True, state="pid", gas=False, brake=False):
  cc = structs.CarControl(longActive=active)
  cc.actuators.longControlState = state
  cs = SimpleNamespace(out=SimpleNamespace(vEgo=speed, aEgo=measured, gasPressed=gas, brakePressed=brake))
  return cc, cs


def drive(controller, accels, measured, pitch=FLAT, speed=20.0):
  controller.pitch = pitch
  for a in accels:
    cc, cs = inputs(speed=speed, measured=measured)
    controller.update(cc, cs, a)


def test_only_civic_bosch_gets_the_ns_learner():
  assert owner().civic_learner is not None and owner().learner_version == gl.LEARN_VERSION
  for car in (CAR.HONDA_ACCORD, CAR.HONDA_INSIGHT, CAR.HONDA_CRV_5G):
    other = owner(car)
    assert other.civic_learner is None and other.learner_version is None
    other.set_factors(0.01, 5.0)  # the shared learner keeps its own range
    assert (other.bosch_gas_factor, other.bosch_wind_factor) == (0.01, 5.0)


def test_civic_saved_factors_use_the_ns_range():
  c = owner()
  c.set_factors(3.0, 0.1)
  assert (c.bosch_gas_factor, c.bosch_wind_factor) == (gl.HARD_HI, gl.HARD_LO)
  assert c.civic_learner.gasfactor == gl.HARD_HI  # applied factor starts at the saved value, no transient
  c.set_factors(float("nan"), float("inf"))
  assert (c.bosch_gas_factor, c.bosch_wind_factor) == (1.0, 1.0)


def test_steady_under_delivery_raises_the_gas_factor():
  c = owner()
  drive(c, [0.5] * 100, measured=0.3)
  assert c.civic_learner.learning
  assert c.civic_learner.last_gas_error == pytest.approx(0.2)
  assert 1.0 < c.civic_learner.gasfactor < c.bosch_gas_factor  # applied trails learned through the filter


def test_learner_uses_the_command_from_half_a_second_ago():
  learner = gl.CivicGasLearner()
  args = dict(a_ego=0.5, gas_pedal_force=0.5, wind_brake_ms2=0.0, engaged=True, gas_pressed=False,
              brake_pressed=False, v_ego=20.0, pitch=FLAT, at_accel_max=False)
  learner.update(accel_cmd=0.3, **args)  # engagement edge fills the window with 0.3
  for _ in range(gl.LAG_TICKS - 1):
    learner.update(accel_cmd=0.3, **args)
  learner.update(accel_cmd=0.35, **args)  # newest differs, oldest is still 0.3
  assert learner.last_gas_error == pytest.approx(0.3 - 0.5)


@pytest.mark.parametrize("pitch", [FLAT + 0.03, FLAT - 0.03])
def test_no_learning_on_grades(pitch):
  c = owner()
  drive(c, [0.5] * 100, measured=0.3, pitch=pitch)
  assert not c.civic_learner.learning and c.bosch_gas_factor == 1.0


def test_no_learning_while_the_command_ramps():
  c = owner()
  drive(c, [i / 100 for i in range(100)], measured=0.0)  # 1 m/s^2 over 2 s = 0.5 m/s^3, above the 0.3 gate
  assert c.bosch_gas_factor == 1.0


def test_no_learning_with_driver_gas_or_brake_or_standstill():
  for kw in (dict(gas=True), dict(brake=True), dict(speed=0.0)):
    c = owner()
    c.pitch = FLAT
    for _ in range(100):
      cc, cs = inputs(measured=0.3, **kw)
      c.update(cc, cs, 0.5)
    assert c.bosch_gas_factor == 1.0, kw


def test_factor_decays_back_inside_the_soft_band():
  learner = gl.CivicGasLearner(1.5, 1.0)
  learner.update(0.0, 0.0, 0.0, 0.0, engaged=False, gas_pressed=False, brake_pressed=False, v_ego=0.0, pitch=FLAT,
                 at_accel_max=False)
  assert learner.raw_gasfactor == pytest.approx(1.5 - gl.DECAY_PER_TICK)
  inside = gl.CivicGasLearner(1.2, 1.0)
  inside.update(0.0, 0.0, 0.0, 0.0, engaged=False, gas_pressed=False, brake_pressed=False, v_ego=0.0, pitch=FLAT,
                at_accel_max=False)
  assert inside.raw_gasfactor == 1.2


def test_gas_lookup_is_unchanged_on_flat_road_and_gains_on_climbs():
  hill_flat = math.sin(FLAT) * ACCELERATION_DUE_TO_GRAVITY
  assert gl.gas_lookup_accel(0.5 + hill_flat, hill_flat, 1.0, -0.2) == pytest.approx(0.5 + hill_flat)
  # factor scales the offset from the gas-on threshold, not the hill term
  assert gl.gas_lookup_accel(0.5 + hill_flat, hill_flat, 1.2, -0.2) == pytest.approx((0.5 + 0.2) * 1.2 - 0.2 + hill_flat)
  hill = 0.8
  assert gl.gas_lookup_accel(hill, hill, 1.0, -0.2) == pytest.approx(hill + 0.1 * (hill - hill_flat))


def test_civic_keeps_star7_gas_table():
  c = owner()
  assert c.params.BOSCH_GAS_LOOKUP_BP == [-0.2, 2.0] and c.params.BOSCH_GAS_LOOKUP_V == [0, 750]


class FakeParams:
  def __init__(self, gas, wind):
    self.values = {"HondaGasFactorParams": gas, "HondaWindFactorParams": wind}

  def get(self, key, return_default=False):
    return self.values[key]

  def put(self, key, value):
    self.values[key] = value


def test_old_saved_factors_are_reset_once(tmp_path):
  # Needs the openpilot checkout; the feeding side (BoschLearningParams) is tested there.
  BoschLearningParams = pytest.importorskip("openpilot.starpilot.car.honda.longitudinal").BoschLearningParams
  meta = str(tmp_path / "meta.json")
  saved = FakeParams(1.4, 0.7)
  first = BoschLearningParams(saved, owner(), meta_path=meta)
  assert (first.owner.bosch_gas_factor, first.owner.bosch_wind_factor) == (1.0, 1.0)
  assert saved.values == {"HondaGasFactorParams": 1.0, "HondaWindFactorParams": 1.0}
  saved.values = {"HondaGasFactorParams": 1.3, "HondaWindFactorParams": 0.9}  # learned on the new math
  second = BoschLearningParams(saved, owner(), meta_path=meta)
  assert (second.owner.bosch_gas_factor, second.owner.bosch_wind_factor) == (1.3, 0.9)


def test_other_cars_never_reset_saved_factors(tmp_path):
  # Needs the openpilot checkout; the feeding side (BoschLearningParams) is tested there.
  BoschLearningParams = pytest.importorskip("openpilot.starpilot.car.honda.longitudinal").BoschLearningParams
  meta = tmp_path / "meta.json"
  saved = FakeParams(1.4, 0.7)
  learning = BoschLearningParams(saved, owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.4, 0.7)
  assert not meta.exists()
