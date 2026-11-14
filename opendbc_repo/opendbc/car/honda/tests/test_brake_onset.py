from types import SimpleNamespace

import pytest

from opendbc.car import DT_CTRL, gen_empty_fingerprint, structs
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal, star7_params
from opendbc.car.honda.brake_onset import (BrakeOnsetCompensation, FADE_END_MPS2, MAX_RELIEF_MPS2,
                                           OVERSHOOT_GAIN, OVERSHOOT_TAU_S)
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

DT = 2 * DT_CTRL


def plant(commands, gain=OVERSHOOT_GAIN, tau=OVERSHOOT_TAU_S):
  """The fitted overshoot model: the car decelerates past a deepening command."""
  alpha = DT / (tau + DT)
  state = min(commands[0], 0.0)
  out = []
  for u in commands:
    braking = min(u, 0.0)
    state += alpha * (braking - state)
    out.append(u + gain * min(braking - state, 0.0))
  return out


def ramp(start, end, rate, hold_s=2.0):
  commands, value = [], start
  while value > end:
    commands.append(value)
    value -= rate * DT
  return commands + [end] * int(hold_s / DT)


def compensate(commands, active=True):
  comp = BrakeOnsetCompensation(DT)
  return [comp.update(u, active) for u in commands]


@pytest.mark.parametrize("end,rate,capped", [(-1.0, 1.5, False), (-2.3, 3.0, False), (-2.7, 4.0, True)])
def test_modelled_car_tracks_the_planner_command(end, rate, capped):
  commands = ramp(0.0, end, rate, hold_s=8.0)
  raw = plant(commands)
  compensated = plant(compensate(commands))
  raw_miss = max(abs(a - u) for a, u in zip(raw, commands, strict=True))
  comp_miss = max(abs(a - u) for a, u in zip(compensated, commands, strict=True))
  assert raw_miss > 0.1
  if capped:
    # The relief cap leaves part of a very steep onset uncorrected.
    assert comp_miss < raw_miss / 2
  else:
    assert comp_miss < 1e-6
  # The settled command is delivered unchanged.
  assert compensate(commands)[-1] == pytest.approx(end, abs=0.01)


def test_never_adds_braking_and_never_touches_a_release():
  commands = ramp(0.5, -2.0, 3.0, hold_s=0.5) + [-2.0 + 0.1 * i for i in range(30)]
  comp = BrakeOnsetCompensation(DT)
  for u in commands:
    deepening = comp.state is not None and min(u, 0.0) < comp.state
    out = comp.update(u, True)
    assert out >= u
    assert out - u <= MAX_RELIEF_MPS2 + 1e-9
    if not deepening:
      assert out == u


def test_full_brake_request_is_sent_as_asked():
  commands = [0.0] * 5 + [-3.5] * 20
  assert compensate(commands)[5:] == commands[5:]
  assert all(out >= u for out, u in zip(compensate([0.0, -3.2]), [0.0, -3.2], strict=True))
  assert compensate([0.0, FADE_END_MPS2 - 0.1])[-1] == FADE_END_MPS2 - 0.1


def test_inactive_passes_through_and_resets():
  commands = ramp(0.0, -2.0, 3.0)
  assert compensate(commands, active=False) == commands
  comp = BrakeOnsetCompensation(DT)
  comp.update(0.0, True)
  comp.update(-1.0, True)
  assert comp.relief > 0
  assert comp.update(-1.5, False) == -1.5
  assert comp.relief == 0.0
  assert comp.update(-1.5, True) == -1.5


def bosch(identity):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
  return BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))


def frame(state="pid", gas=False, brake=False, active=True):
  cc = structs.CarControl(longActive=active)
  cc.actuators.longControlState = state
  return cc, SimpleNamespace(out=SimpleNamespace(vEgo=10.0, aEgo=0.0, gasPressed=gas, brakePressed=brake))


def test_civic_bosch_command_is_compensated_only_in_pid():
  civic = bosch(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = frame()
  civic.update(cc, cs, 0.0)
  assert civic.update(cc, cs, -1.5)[0] > -1.5
  for state, gas, brake in (("stopping", False, False), ("pid", True, False), ("pid", False, True)):
    other = bosch(CAR.HONDA_CIVIC_BOSCH)
    cc, cs = frame(state, gas, brake)
    other.update(cc, cs, 0.0)
    assert other.update(cc, cs, -1.5)[0] == -1.5


def test_accord_bosch_a_harness_command_is_compensated():
  accord = bosch(CAR.HONDA_ACCORD)
  assert accord.brake_onset is not None
  cc, cs = frame()
  accord.update(cc, cs, 0.0)
  assert accord.update(cc, cs, -1.5)[0] > -1.5


def test_other_bosch_cars_are_unchanged():
  # Civic 2022 is not a Bosch-A harness car.
  other = bosch(CAR.HONDA_CIVIC_2022)
  assert other.brake_onset is None
  cc, cs = frame()
  other.update(cc, cs, 0.0)
  assert other.update(cc, cs, -1.5)[0] == -1.5
