"""LPF and host-to-Honda command handoff; no CAN, native services or Params."""

import ast
import json
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import numpy as np
import pytest

from openpilot.nrdr.features.lateral.live_tuning import LiveTorqueTransition
from openpilot.nrdr.features.lateral.torque_output_filter import HondaTorqueOutputFilter, MPH_TO_MS, torque_lpf_tau
from openpilot.nrdr.hooks.controlsd import finalize_lateral_torque
from openpilot.nrdr.params.snapshots import ParamSnapshot


def tuning(**changes):
  return SimpleNamespace(**({"torque_lpf_enabled": True, "lpf_tau_low": 0.1, "lpf_tau_standard": 0.09,
                            "lpf_tau_highway": 0.07, "increase_override_tolerance": False,
                            "override_fade_up_s": 0.1, "override_fade_down_s": 0.1, "override_torque_scale": 0.0,
                            "steer_delta_limiter_enabled": False, "steer_delta_up": 3.0, "steer_delta_down": 3.0,
                            "driver_assist_during_override": True} | changes))


def honda_postprocessor():
  # Execute the production steering methods without importing the constructor's
  # unrelated longitudinal learner and native CAN/serialization dependencies.
  root = Path(__file__).resolve().parents[3]
  source = root / "opendbc_repo/opendbc/sunnypilot/car/honda/controller_features.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "HondaControllerFeatures")
  cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and
              node.name in ("_filtered_steering_pressed", "update_steering_torque")]
  car_tree = ast.parse((root / "opendbc_repo/opendbc/car/__init__.py").read_text(encoding="utf-8"))
  rate_limit = next(node for node in car_tree.body if isinstance(node, ast.FunctionDef) and node.name == "rate_limit")
  namespace = {"DT_CTRL": 0.01, "np": np}
  exec(compile(ast.Module(body=[rate_limit, cls], type_ignores=[]), str(source), "exec"), namespace)
  honda = namespace["HondaControllerFeatures"]()
  honda.override_ramp = 1.0
  honda.lat_active_previous = True
  honda.steering_pressed_filter = 0.0
  honda.steering_pressed_previous = False
  return honda


def host(live, brand="honda"):
  def cached_tuning(*, refresh_if_uninitialized):
    assert not refresh_if_uninitialized  # Never let the control loop read storage.
    return live

  return SimpleNamespace(
    CP=SimpleNamespace(brand=brand),
    CI=SimpleNamespace(interface_config=SimpleNamespace(honda=SimpleNamespace(
      provider=SimpleNamespace(get_live_tuning=cached_tuning)))),
    nrdr_live_torque_transition=LiveTorqueTransition(), nrdr_torque_output_filter=HondaTorqueOutputFilter(),
    nrdr_lateral_snapshot=ParamSnapshot(1, MappingProxyType({})),
  )


@pytest.mark.parametrize("mph, expected", ((0, 0.1), (24.999, 0.1), (25, 0.09), (49.999, 0.09), (50, 0.07), (80, 0.07)))
def test_existing_speed_band_boundaries(mph, expected):
  assert torque_lpf_tau(mph * MPH_TO_MS, 0.1, 0.09, 0.07) == expected


@pytest.mark.parametrize("tau", (0.0, 0.01, 0.07, 0.1, 5.0))
@pytest.mark.parametrize("sign", (-1, 1))
def test_filter_matches_first_order_response(tau, sign):
  filt = HondaTorqueOutputFilter()
  live = tuning(lpf_tau_highway=tau)
  alpha = 0.01 / (tau + 0.01)
  for frame in range(1, 101):
    result = filt.update(sign * 0.8, True, 27.0, live, 0.01)
    assert result == pytest.approx(sign * 0.8 * (1.0 - (1.0 - alpha) ** frame))
    assert abs(result) <= 0.8


def test_lower_tau_means_less_smoothing():
  fast = HondaTorqueOutputFilter().update(0.5, True, 27.0, tuning(lpf_tau_highway=0.01), 0.01)
  slow = HondaTorqueOutputFilter().update(0.5, True, 27.0, tuning(lpf_tau_highway=0.1), 0.01)
  assert fast > slow


@pytest.mark.parametrize("mph", (0, 5, 10, 20, 24.99, 25, 40, 50, 65))
def test_zero_upper_bands_do_not_disable_low_speed_filter(mph):
  live = tuning(lpf_tau_low=0.1, lpf_tau_standard=0.0, lpf_tau_highway=0.0)
  controls = host(live)
  cs = SimpleNamespace(vEgo=mph * MPH_TO_MS, steeringPressed=False)
  assert finalize_lateral_torque(controls, 0.8, cs, True, 0.01) == pytest.approx(0.8 / 11 if mph < 25 else 0.8)
  live.torque_lpf_enabled = False
  assert finalize_lateral_torque(controls, 0.8, cs, True, 0.01) == 0.8


def test_lpf_audit_records_consumed_snapshot_only_when_configuration_changes():
  live = tuning(generation=7, lpf_tau_low=0.1, lpf_tau_standard=0.0, lpf_tau_highway=0.0)
  controls = host(live)
  records = []
  controls.nrdr_live_params = SimpleNamespace(record_applied_settings=lambda *args, **kwargs: records.append((args, kwargs)))
  cs = SimpleNamespace(vEgo=10 * MPH_TO_MS, steeringPressed=False)
  result = finalize_lateral_torque(controls, 0.8, cs, True, 0.01)
  assert records == [(('honda_torque_lpf', 7), {
    "enabled": True, "tau_low": 0.1, "tau_standard": 0.0, "tau_highway": 0.0, "selected_tau": 0.1,
    "active": True, "speed_ms": cs.vEgo, "input_torque": 0.8, "output_torque": result,
  })]
  for _ in range(100):
    finalize_lateral_torque(controls, 0.8, cs, True, 0.01)
  assert len(records) == 1
  live.generation = 8
  live.torque_lpf_enabled = False
  assert finalize_lateral_torque(controls, 0.8, cs, True, 0.01) == 0.8
  assert records[-1][0] == ("honda_torque_lpf", 8)
  assert records[-1][1]["selected_tau"] == 0.0
  assert records[-1][1]["enabled"] is False


def test_toggle_and_tau_change_are_live_without_stale_state():
  filt = HondaTorqueOutputFilter()
  live = tuning()
  filt.update(0.8, True, 27.0, live, 0.01)
  live.torque_lpf_enabled = False
  assert filt.update(-0.3, True, 27.0, live, 0.01) == -0.3
  live.torque_lpf_enabled = True
  live.lpf_tau_highway = 0.01
  assert filt.update(0.5, True, 27.0, live, 0.01) == pytest.approx(0.1)
  live.lpf_tau_highway = 0.0
  assert filt.update(0.5, True, 27.0, live, 0.01) == 0.5


@pytest.mark.parametrize("value,active", ((0.8, False), (float("nan"), True), (float("inf"), True)))
def test_inactive_or_invalid_command_clears_filter(value, active):
  filt = HondaTorqueOutputFilter(0.7)
  live = tuning()
  assert filt.update(value, active, 27.0, live, 0.01) == 0.0
  assert filt.update(0.8, True, 27.0, live, 0.01) == pytest.approx(0.1)


def test_honda_filtered_request_does_not_create_false_limiting():
  live = tuning()
  controls = host(live)
  controls.nrdr_torque_output_filter.output = 0.1
  honda = honda_postprocessor()
  cs = SimpleNamespace(vEgo=60.0 * MPH_TO_MS, steeringPressed=False)
  car = SimpleNamespace(out=cs)
  command = SimpleNamespace(latActive=True, actuators=SimpleNamespace(torque=0.1))
  previous = 0.1
  old_filter = HondaTorqueOutputFilter(0.1)
  old_flags = 0
  for frame in range(1, 101):
    raw = 0.1 + frame * 0.002
    old_output = old_filter.update(raw, True, cs.vEgo, live, 0.01)
    old_flags += abs(raw - old_output) > 0.01
    requested = finalize_lateral_torque(controls, raw, cs, True, 0.01)
    command.actuators.torque = requested
    delivered, active = honda.update_steering_torque(command, car, live, previous)
    assert active
    assert delivered == requested  # No car-side second filter.
    assert abs(requested - previous) < 0.01  # Also check a one-frame feedback delay.
    previous = delivered
  assert old_flags == 91


@pytest.mark.parametrize("guard", ("driver", "rate_limit"))
def test_actual_override_and_rate_limit_still_create_request_output_difference(guard):
  live = tuning(steer_delta_limiter_enabled=guard == "rate_limit")
  controls = host(live)
  controls.nrdr_torque_output_filter.output = 0.6
  cs = SimpleNamespace(vEgo=27.0, steeringPressed=guard == "driver")
  requested = finalize_lateral_torque(controls, 0.6, cs, True, 0.01)
  command = SimpleNamespace(latActive=True, actuators=SimpleNamespace(torque=requested))
  delivered, active = honda_postprocessor().update_steering_torque(command, SimpleNamespace(out=cs), live, 0.0)
  assert abs(requested - delivered) > 0.01
  assert active == (guard != "driver")


@pytest.mark.parametrize("brand", ("toyota", "hyundai", "subaru"))
def test_non_honda_output_is_not_filtered(brand):
  controls = host(tuning(), brand)
  controls.CI = None  # A non-Honda controller must not look for Honda settings.
  cs = SimpleNamespace(vEgo=27.0, steeringPressed=False)
  for torque in (0.8, -0.7, 0.1):
    assert finalize_lateral_torque(controls, torque, cs, True, 0.01) == torque


def test_live_edit_transition_is_followed_by_one_filter_before_publication():
  controls = host(tuning())
  cs = SimpleNamespace(vEgo=27.0, steeringPressed=False)
  for _ in range(200):
    before = finalize_lateral_torque(controls, 0.3, cs, True, 0.01)
  controls.nrdr_lateral_snapshot = ParamSnapshot(2, MappingProxyType({"LatPScaleHighway": 120}))
  assert finalize_lateral_torque(controls, 0.7, cs, True, 0.01) == pytest.approx(before)
  values = [finalize_lateral_torque(controls, 0.7, cs, True, 0.01) for _ in range(200)]
  assert all(0.3 <= value <= 0.7 for value in values)
  assert values[-1] == pytest.approx(0.7, abs=1e-6)


def test_controlsd_publishes_finalized_torque_and_keeps_limiting_detection():
  root = Path(__file__).resolve().parents[2]
  source = (root / "selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
  assert source.index("steer = finalize_lateral_torque(") < source.index("actuators.torque = float(steer)")
  assert "abs(CC.actuators.torque - CO.actuatorsOutput.torque) > 1e-2" in source


def test_sunnylink_lpf_bands_require_explicit_master_switch():
  root = Path(__file__).resolve().parents[3]
  schema = json.loads((root / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))

  def walk(node):
    if isinstance(node, dict):
      yield node
      for value in node.values():
        yield from walk(value)
    elif isinstance(node, list):
      for value in node:
        yield from walk(value)

  items = {item["key"]: item for item in walk(schema) if "key" in item and "widget" in item}
  master = items["HondaTorqueLowPassFilter"]
  assert "OFF bypasses" in master["description"]
  assert "does not turn the filter on" in master["details"]
  for key in ("HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway"):
    assert {"type": "param", "key": "HondaTorqueLowPassFilter", "equals": True} in items[key]["enablement"]
    assert "Requires the master switch ON" in items[key]["description"]
