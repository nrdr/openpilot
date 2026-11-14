from types import SimpleNamespace

import pytest

from opendbc.car import DT_CTRL, gen_empty_fingerprint, structs
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal, star7_params
from opendbc.car.honda.bosch_low_speed_brake import (LowSpeedBrakeAssist, NEG_LIMIT, V_MAX, V_RESET,
                                                      RELEASE_RATE, STOP_DEEPEN_RATE)
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

DT = 2 * DT_CTRL


def test_inactive_returns_sent_and_resets():
  assist = LowSpeedBrakeAssist(DT)
  assist.i = -0.3
  assist.last = -1.2
  out = assist.update(target=-1.0, sent=-1.0, a_ego=-0.5, v_ego=1.0, active=False, stopping=False)
  assert out == -1.0
  assert assist.i == 0.0
  assert assist.last is None


def test_integrator_builds_up_over_one_second():
  assist = LowSpeedBrakeAssist(DT)
  out = -1.0
  for _ in range(int(round(1.0 / DT))):
    out = assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
  assert assist.i == pytest.approx(-0.2, abs=0.02)
  assert out == pytest.approx(-1.0 + assist.i, abs=1e-6)


def test_integral_clips_to_neg_limit_and_zero():
  assist = LowSpeedBrakeAssist(DT)
  # a_ego is less negative than target (an undershoot): the integrator deepens until clipped.
  for _ in range(2000):
    assist.update(target=-1.0, sent=-1.0, a_ego=0.0, v_ego=2.0, active=True, stopping=False)
  assert assist.i == pytest.approx(NEG_LIMIT)
  assert assist.i <= 0.0


def test_out_never_exceeds_sent_when_not_stopping():
  assist = LowSpeedBrakeAssist(DT)
  sent = -1.0
  for _ in range(100):
    out = assist.update(target=-1.0, sent=sent, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
    assert out <= sent + 1e-9


def test_release_above_v_max_or_positive_target():
  assist = LowSpeedBrakeAssist(DT)
  for _ in range(50):
    assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
  assert assist.i < 0.0
  # Above V_MAX, the integrator releases at RELEASE_RATE back to 0.
  steps = int(round(abs(assist.i) / (RELEASE_RATE * DT))) + 2
  for _ in range(steps):
    out = assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=V_MAX + 0.1, active=True, stopping=False)
  assert assist.i == pytest.approx(0.0, abs=1e-9)
  assert out == pytest.approx(-1.0, abs=1e-9)

  assist2 = LowSpeedBrakeAssist(DT)
  for _ in range(50):
    assist2.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
  assert assist2.i < 0.0
  steps2 = int(round(abs(assist2.i) / (RELEASE_RATE * DT))) + 2
  for _ in range(steps2):
    out2 = assist2.update(target=1.0, sent=-1.0, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
  assert assist2.i == pytest.approx(0.0, abs=1e-9)
  assert out2 == pytest.approx(-1.0, abs=1e-9)


def test_below_v_reset_drops_integral_immediately():
  assist = LowSpeedBrakeAssist(DT)
  for _ in range(50):
    assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=2.0, active=True, stopping=False)
  assert assist.i < 0.0
  out = assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=V_RESET - 0.1, active=True, stopping=False)
  assert assist.i == 0.0
  assert out == -1.0


def test_stopping_guard_limits_deepen_rate():
  assist = LowSpeedBrakeAssist(DT)
  # Build up some extra brake first.
  for _ in range(50):
    assist.update(target=-1.0, sent=-1.0, a_ego=-0.6, v_ego=1.0, active=True, stopping=False)
  prev = assist.last
  out = assist.update(target=-1.0, sent=-1.0, a_ego=-5.0, v_ego=1.0, active=True, stopping=True)
  # Even though the integrator would want to deepen a lot in one tick, the stopping guard caps it.
  assert out >= prev - STOP_DEEPEN_RATE * DT - 1e-9


def bosch(identity):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False, make_test_car_config(bosch_a_radar=True))
  return BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))


def frame(state="pid", gas=False, brake=False, active=True, speed=2.0, measured=0.0):
  cc = structs.CarControl(longActive=active)
  cc.actuators.longControlState = state
  return cc, SimpleNamespace(out=SimpleNamespace(vEgo=speed, aEgo=measured, gasPressed=gas, brakePressed=brake))


def test_bosch_a_harness_civic_gets_low_speed_brake():
  civic = bosch(CAR.HONDA_CIVIC_BOSCH)
  assert civic.low_speed_brake is not None


def test_non_harness_car_gets_none():
  # Civic 2022 is not a Bosch-A harness car (radarless); the Accord is one since the Bosch-A toggles (PR #45).
  other = bosch(CAR.HONDA_CIVIC_2022)
  assert other.low_speed_brake is None


def test_low_speed_shortfall_deepens_accel():
  civic = bosch(CAR.HONDA_CIVIC_BOSCH)
  cc, cs = frame(speed=2.0, measured=-0.4)
  civic.update(cc, cs, 0.0)
  for _ in range(50):
    result = civic.update(cc, cs, -1.0)
  assert result[0] < -1.0


def test_stopping_guard_never_holds_back_the_command():
  assist = LowSpeedBrakeAssist(DT)
  assist.update(target=0.0, sent=0.0, a_ego=0.0, v_ego=1.0, active=True, stopping=False)
  # A sudden deeper planner command in the stopping state passes through unchanged.
  out = assist.update(target=-1.5, sent=-1.5, a_ego=-1.5, v_ego=1.0, active=True, stopping=True)
  assert out == -1.5
  for _ in range(100):
    out = assist.update(target=-1.0, sent=-1.0, a_ego=0.0, v_ego=1.0, active=True, stopping=True)
    assert out <= -1.0
