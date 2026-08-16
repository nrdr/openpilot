from types import SimpleNamespace

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.sunnypilot.nrdr.longcontrol import NrdrLongControl
from openpilot.sunnypilot.nrdr.longitudinal_planner import NrdrLongitudinalPlanner, apply_cruise_overspeed_allowance


def _long_control(*, enabled: bool, nidec: bool = True, gas_interceptor: bool = True, brand: str = "honda"):
  control = NrdrLongControl.__new__(NrdrLongControl)
  control.roen_acceleration_limits = enabled
  control.CP = SimpleNamespace(brand=brand, flags=HondaFlags.NIDEC if nidec else 0)
  control.CP_SP = SimpleNamespace(enableGasInterceptor=gas_interceptor)
  return control


def test_roen_limits_raise_only_nidec_pedal_ceiling():
  upstream = (-4.0, 1.6)
  assert _long_control(enabled=True)._accel_limits(upstream, 0.0) == (-4.0, 4.0)
  assert _long_control(enabled=True)._accel_limits(upstream, 12.5) == (-4.0, 3.5)
  assert _long_control(enabled=True)._accel_limits(upstream, 20.0) == (-4.0, 3.0)
  assert _long_control(enabled=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, nidec=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, gas_interceptor=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, brand="other")._accel_limits(upstream, 0.0) == upstream


def _planner(*, enabled: bool, nidec: bool = True, gas_interceptor: bool = True, brand: str = "honda"):
  planner = NrdrLongitudinalPlanner.__new__(NrdrLongitudinalPlanner)
  planner.roen_acceleration_limits = enabled
  planner.CP = SimpleNamespace(brand=brand, flags=HondaFlags.NIDEC if nidec else 0)
  planner.CP_SP = SimpleNamespace(enableGasInterceptor=gas_interceptor)
  planner.tune = SimpleNamespace(a_cruise_max_scale=1.0)
  return planner


@pytest.mark.parametrize(("speed", "expected"), ((0.0, 4.0), (5.0, 4.0), (12.5, 3.0), (20.0, 2.0), (30.0, 2.0)))
def test_roen_planner_envelope(speed, expected):
  assert _planner(enabled=True).max_accel(speed) == pytest.approx(expected)


def test_roen_planner_gates_and_turn_threshold():
  assert _planner(enabled=False).max_accel(0.0) == 2.0
  assert _planner(enabled=True, nidec=False).max_accel(0.0) == 2.0
  assert _planner(enabled=True, gas_interceptor=False).max_accel(0.0) == 2.0
  assert _planner(enabled=True, brand="other").max_accel(0.0) == 2.0
  assert _planner(enabled=True).turn_accel_threshold() == 1.3
  assert _planner(enabled=False).turn_accel_threshold() == 0.0


def test_zero_overspeed_allowance_is_exact_noop():
  assert apply_cruise_overspeed_allowance(20.0, 20.0, 20.0, 22.0, 0.2, 0.0) == 20.0


def test_lower_selected_target_blocks_overspeed_allowance():
  assert apply_cruise_overspeed_allowance(18.0, 18.0, 20.0, 22.0, 0.2, 2.0) == 18.0


@pytest.mark.parametrize(("accel", "expected"), ((0.2, 21.5), (-0.2, 21.9)))
def test_overspeed_allowance_follows_vehicle_with_directional_buffer(accel, expected):
  assert apply_cruise_overspeed_allowance(20.0, 20.0, 20.0, 22.0, accel, 5.0) == pytest.approx(expected)


def test_overspeed_allowance_is_capped_from_raw_set_speed():
  assert apply_cruise_overspeed_allowance(20.0, 20.0, 20.0, 24.0, 0.2, 1.0) == 21.0


def test_overspeed_allowance_never_reduces_existing_target():
  assert apply_cruise_overspeed_allowance(22.0, 20.0, 20.0, 23.0, 0.2, 1.0) == 22.0
