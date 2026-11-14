import math
import time
from types import SimpleNamespace

import pytest

from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, gen_empty_fingerprint, structs
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal, bosch_a_harness, qualified, star7_params
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


def owner(identity=CAR.HONDA_ACCORD):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
  assert qualified(cp)
  return BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))


def inputs(speed=0.0, measured=0.0, active=True, state="pid", gas=False, brake=False):
  cc = structs.CarControl(longActive=active)
  cc.actuators.longControlState = state
  cs = SimpleNamespace(out=SimpleNamespace(vEgo=speed, aEgo=measured, gasPressed=gas, brakePressed=brake))
  return cc, cs


def test_pitch_observation_retains_odd_frame_sample_for_next_command():
  controller = owner()
  controller.observe_orientation((0.0, 0.1, 0.0))
  controller.observe_orientation(())
  cc, cs = inputs(state="off")
  result = controller.update(cc, cs, 0.0)
  assert result[2] == pytest.approx(math.sin(0.1) * ACCELERATION_DUE_TO_GRAVITY)
  controller.observe_orientation((0.0, -0.1, 0.0))
  assert controller.update(cc, cs, 0.0)[2] < 0


def test_disabled_update_preserves_original_gas_ramp_without_requesting_brakes():
  controller = owner()
  cc, cs = inputs(active=False, state="off")
  controller.observe_orientation((0.0, 0.2, 0.0))
  first = controller.update(cc, cs, 0.0)
  second = controller.update(cc, cs, 0.0)
  assert first[1] == 60.0
  assert second[1] == 120.0
  assert first[3] is second[3] is False
  assert controller.bosch_gas_factor == controller.bosch_wind_factor == 1.0


@pytest.mark.parametrize("identity,rate", ((CAR.HONDA_ACCORD, 50.0), (CAR.HONDA_INSIGHT, 150.0),
                                         (CAR.ACURA_RDX_3G, 300.0), (CAR.ACURA_RDX_3G_MMR, 300.0)))
def test_learning_uses_actual_vehicle_rate_and_driver_gas_override(identity, rate):
  controller = owner(identity)
  cc, cs = inputs(measured=0.5)
  controller.update(cc, cs, 1.0)
  assert controller.bosch_gas_factor == pytest.approx(1.0 + 0.5 / rate)
  previous = controller.bosch_gas_factor
  cs.out.gasPressed = True
  controller.update(cc, cs, 1.0)
  assert controller.bosch_gas_factor == previous


def test_braking_hysteresis_stopping_and_inactive_release():
  # Civic 2022 is not a Bosch-A harness car, so this checks the plain hysteresis without the brake fixes.
  controller = owner(CAR.HONDA_CIVIC_2022)
  cc, cs = inputs(state="off")
  assert controller.update(cc, cs, -0.13)[3]
  assert controller.update(cc, cs, -0.03)[3]
  assert not controller.update(cc, cs, -0.01)[3]
  cc.actuators.longControlState = "stopping"
  assert controller.update(cc, cs, 0.1)[3]
  cc.longActive = False
  assert not controller.update(cc, cs, 0.0)[3]


def test_saved_factors_keep_shared_learner_range_and_reject_invalid_values():
  controller = owner()
  controller.set_factors(0.01, 5.0)
  assert (controller.bosch_gas_factor, controller.bosch_wind_factor) == (0.01, 5.0)
  controller.set_factors(float("nan"), float("inf"))
  assert (controller.bosch_gas_factor, controller.bosch_wind_factor) == (1.0, 1.0)


def test_actual_controller_captures_pitch_on_non_transmit_frame():
  # nrdr adaptation: CarInterface needs CP_SP and the host config.
  config, fp = make_test_car_config(bosch_a_radar=True), gen_empty_fingerprint()
  cp = CarInterface.get_params(CAR.HONDA_ACCORD, fp, [], True, False, False, config)
  sp = CarInterface.get_params_sp(cp, CAR.HONDA_ACCORD, fp, [], True, False, False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  command = structs.CarControl()
  command.actuators.longControlState = "off"
  ci.apply(command.as_reader(), structs.CarControlSP(), 1_000_000_000)
  command.orientationNED = [0.0, 0.1, 0.0]
  ci.apply(command.as_reader(), structs.CarControlSP(), 1_010_000_000)
  command.orientationNED = []
  ci.apply(command.as_reader(), structs.CarControlSP(), 1_020_000_000)
  assert ci.CC.bosch_longitudinal.pitch == pytest.approx(0.1)
  assert ci.CC.bosch_longitudinal.bosch_last_gas > 0.0


def test_actual_configure_loads_typed_factors_without_startup_rewrite():
  # Needs the openpilot checkout (Params, starpilot.controller_extensions); the feeding side is tested there.
  pytest.importorskip("openpilot.starpilot.controller_extensions")
  from openpilot.common.params import Params
  from openpilot.common.prefix import OpenpilotPrefix
  from openpilot.starpilot.controller_extensions import configure_controller

  with OpenpilotPrefix():
    saved = Params()
    saved.put("HondaGasFactorParams", 1.25, block=True)
    saved.put("HondaWindFactorParams", 0.85, block=True)
    cp = CarInterface.get_params(CAR.HONDA_ACCORD, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
    ci = CarInterface(cp)
    configure_controller(ci, saved)
    learning = ci.CC.bosch_learning_params
    assert learning.owner is ci.CC.bosch_longitudinal
    assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.25, 0.85)
    learning.owner.set_factors(1.1, 0.9)
    learning.persist(0)
    learning.persist(5999)
    assert saved.get("HondaGasFactorParams") == 1.25
    assert saved.get("HondaWindFactorParams") == 0.85
    learning.persist(6000)
    deadline = time.monotonic() + 2.0
    while saved.get("HondaWindFactorParams") != 0.9 and time.monotonic() < deadline:
      time.sleep(0.01)
    assert saved.get("HondaGasFactorParams") == pytest.approx(1.1)
    assert saved.get("HondaWindFactorParams") == pytest.approx(0.9)
    writes = []
    learning.params = SimpleNamespace(put=lambda *args: writes.append(args))
    learning.persist(12000)
    assert writes == []
    learning.owner.set_factors(1.2, 0.9)
    learning.persist(18000)
    assert writes == [("HondaGasFactorParams", 1.2), ("HondaWindFactorParams", 0.9)]


def test_civic_brake_request_starts_deeper_and_coasts_the_band_above():
  controller = owner(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = inputs(speed=3.0)
  assert not controller.update(cc, cs, -0.15)[3]
  assert controller.update(cc, cs, -0.30)[3]


def test_civic_brake_request_holds_at_least_its_minimum_unless_accel_is_asked():
  from opendbc.car.honda.bosch_longitudinal import BOSCH_A_BRAKE_MIN_HOLD_S
  controller = owner(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = inputs(speed=3.0)
  assert controller.update(cc, cs, -0.4)[3]
  frames = 0
  while controller.update(cc, cs, 0.05)[3]:
    frames += 1
  assert frames * controller.brake_edge.dt == pytest.approx(BOSCH_A_BRAKE_MIN_HOLD_S, abs=0.03)
  assert controller.update(cc, cs, -0.4)[3]
  assert not controller.update(cc, cs, 0.5)[3]  # a clear accel request ends the hold at once


def test_civic_gas_after_release_ramps_from_35_instead_of_jumping_to_the_cap():
  from opendbc.car.honda.bosch_longitudinal import BOSCH_A_RELEASE_GAS_RAMP_S, BOSCH_A_RELEASE_GAS_START
  controller = owner(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = inputs(speed=3.0)
  for _ in range(100):
    controller.update(cc, cs, -0.4)
  gases = []
  for _ in range(int(BOSCH_A_RELEASE_GAS_RAMP_S / controller.brake_edge.dt) + 20):
    _, gas, _, braking = controller.update(cc, cs, 0.3)
    assert not braking
    gases.append(gas)
  assert gases[0] <= BOSCH_A_RELEASE_GAS_START
  assert all(b >= a - 1e-6 for a, b in zip(gases, gases[1:], strict=False))
  assert max(b - a for a, b in zip(gases, gases[1:], strict=False)) < 10.0
  free = owner(CAR.HONDA_CIVIC_BOSCH)
  for _ in range(100):
    target = free.update(cc, cs, 0.3)[1]
  assert gases[-1] == pytest.approx(target, rel=0.05)


def test_civic_brake_edge_keeps_stopping_and_long_drop_behavior():
  controller = owner(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = inputs(speed=1.0, state="stopping")
  assert controller.update(cc, cs, 0.1)[3]
  cc.longActive = False
  assert not controller.update(cc, cs, -1.0)[3]


def test_brake_fixes_run_on_bosch_a_harness_cars_only():
  for identity in (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G, CAR.HONDA_ACCORD):
    controller = owner(identity)
    assert controller.brake_edge is not None and controller.brake_onset is not None
  for identity in CAR:
    cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
    if qualified(cp):
      controller = BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))
      assert (controller.brake_edge is not None) == (controller.brake_onset is not None) == bosch_a_harness(cp), identity
  civic_2022 = owner(CAR.HONDA_CIVIC_2022)
  assert civic_2022.brake_edge is None and civic_2022.brake_onset is None
  cp = CarInterface.get_params(CAR.HONDA_CIVIC_BOSCH, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
  cp.radarUnavailable = True
  no_radar = BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))
  assert no_radar.brake_edge is None and no_radar.brake_onset is None


def test_crv_brake_edge_holds_the_request_and_ramps_gas_after_release():
  from opendbc.car.honda.bosch_longitudinal import BOSCH_A_RELEASE_GAS_RAMP_S, BOSCH_A_RELEASE_GAS_START
  controller = owner(CAR.HONDA_CRV_5G)
  cc, cs = inputs(speed=3.0)
  assert not controller.update(cc, cs, -0.15)[3]
  for _ in range(100):
    assert controller.update(cc, cs, -0.4)[3]
  gases = []
  for _ in range(int(BOSCH_A_RELEASE_GAS_RAMP_S / controller.brake_edge.dt) + 20):
    _, gas, _, braking = controller.update(cc, cs, 0.3)
    gases.append(gas)
  assert not braking and gases[0] <= BOSCH_A_RELEASE_GAS_START
  assert all(b >= a - 1e-6 for a, b in zip(gases, gases[1:], strict=False))


def test_brake_edge_launch_from_stopping_ramps_gas_faster_than_a_brake_cycle_release():
  from opendbc.car.honda.bosch_longitudinal import (BOSCH_A_LAUNCH_GAS_RAMP_S, BOSCH_A_RELEASE_GAS_RAMP_S,
                                                    BOSCH_A_RELEASE_GAS_START, BoschABrakeEdge)
  assert BOSCH_A_LAUNCH_GAS_RAMP_S < BOSCH_A_RELEASE_GAS_RAMP_S

  def gas_after_release(stopping_before):
    edge = BoschABrakeEdge(0.02)
    for _ in range(100):  # 2 s of braking: past the minimum hold
      assert edge.update(-0.5, stopping_before, True)
    gases = []
    for _ in range(int(BOSCH_A_RELEASE_GAS_RAMP_S / edge.dt) + 5):
      assert not edge.update(0.5, False, True)
      gases.append(edge.limit_gas(500.))
    return gases

  launch, cycle = gas_after_release(True), gas_after_release(False)
  assert launch[0] == cycle[0] == BOSCH_A_RELEASE_GAS_START
  n_launch = int(round(BOSCH_A_LAUNCH_GAS_RAMP_S / 0.02))
  assert launch[n_launch] == 500. and cycle[n_launch] < 500.
  assert all(a >= b for a, b in zip(launch, cycle, strict=True))
  assert cycle[-1] == 500.
