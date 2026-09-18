"""Controller math only: no native messaging, Params or vehicle actuation."""

import numpy as np
import pytest

from openpilot.common.pid import PIDController
from openpilot.nrdr.features.lateral.integral_pid import IntegralScaledPIDController


def lateral_update(pid, **changes):
  args = {"error": 0.5, "feedforward": 0.0, "speed": 27.0, "i_scale": 1.0, "eps_modified": True,
          "steer_limited": False, "steering_pressed": False, "stiction_freeze": False}
  return pid.update_lateral(**(args | changes))


def test_unit_scale_matches_upstream_pid_including_antiwindup():
  args = (0.3, 0.2, 0.05)
  base = PIDController(*args, pos_limit=1.0, neg_limit=-1.0)
  scaled = IntegralScaledPIDController(*args, pos_limit=1.0, neg_limit=-1.0)
  for index in range(1000):
    error = float(5.0 * np.sin(index / 21.0))
    kwargs = {"error_rate": 0.1, "speed": 20.0, "feedforward": 0.02, "freeze_integrator": index % 13 == 0}
    assert scaled.update(error, **kwargs) == base.update(error, **kwargs)
    assert scaled.i == base.i


@pytest.mark.parametrize("scale", (0.0, 0.2, 0.5, 1.0, 1.35, 2.0, 5.0))
def test_i_strength_scales_accumulation_once(scale):
  pid = IntegralScaledPIDController(0.0, 0.2)
  for _ in range(100):
    lateral_update(pid, i_scale=scale)
  assert pid.i == pytest.approx(0.1 * scale)
  assert pid.control == pytest.approx(pid.i)


def test_nonzero_scale_change_does_not_rescale_stored_correction():
  pid = IntegralScaledPIDController(0.0, 0.2)
  pid.i = 0.15
  lateral_update(pid, i_scale=0.2, steer_limited=True)
  assert pid.i == pid.control == 0.15
  lateral_update(pid, i_scale=2.0)
  assert pid.i == pytest.approx(0.152)


@pytest.mark.parametrize("guard", ("steer_limited", "steering_pressed", "stiction_freeze"))
def test_zero_i_clears_state_even_when_another_guard_freezes_updates(guard):
  pid = IntegralScaledPIDController(0.0, 0.2)
  pid.i = 0.3
  lateral_update(pid, i_scale=0.0, **{guard: True})
  assert pid.i == 0.0
  lateral_update(pid, i_scale=1.0)
  assert pid.i == pytest.approx(0.001)


@pytest.mark.parametrize("guard", ("steer_limited", "steering_pressed", "stiction_freeze"))
@pytest.mark.parametrize("speed", (5.0, 15.0, 27.0))
def test_genuine_freeze_guards_remain_at_all_speeds(guard, speed):
  pid = IntegralScaledPIDController(0.0, 0.2)
  pid.i = 0.1
  lateral_update(pid, speed=speed, **{guard: True})
  assert pid.i == 0.1


@pytest.mark.parametrize("eps_modified, speed, expected", (
  (True, 0.0, 0.0), (True, 1.99, 0.0), (True, 2.0, 0.101),
  (False, 4.99, 0.1), (False, 5.0, 0.101),
))
def test_low_speed_threshold_and_modified_eps_reset(eps_modified, speed, expected):
  pid = IntegralScaledPIDController(0.0, 0.2)
  pid.i = 0.1
  lateral_update(pid, eps_modified=eps_modified, speed=speed)
  assert pid.i == pytest.approx(expected)


@pytest.mark.parametrize("sign", (-1, 1))
@pytest.mark.parametrize("scale", (0.2, 1.0, 5.0))
def test_saturation_stops_windup_and_opposite_error_can_unwind(sign, scale):
  pid = IntegralScaledPIDController(1.0, 1.0, pos_limit=1.0, neg_limit=-1.0)
  pid.i = sign * 0.4
  for _ in range(100):
    lateral_update(pid, error=sign * 2.0, i_scale=scale)
  assert pid.i == sign * 0.4
  lateral_update(pid, error=-sign * 0.1, i_scale=scale)
  assert abs(pid.i) < 0.4
