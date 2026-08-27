import ast
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest


# The controller is Linux-only, but these regressions exercise pure math and
# source-level plumbing in the Windows development tree.
if sys.platform == "win32":
  hardware_module = ModuleType("openpilot.common.hardware")
  hardware_module.PC = True
  hardware_module.HARDWARE = SimpleNamespace(get_device_type=lambda: "pc")
  sys.modules.setdefault("openpilot.common.hardware", hardware_module)
  hardware_hw_module = ModuleType("openpilot.common.hardware.hw")
  hardware_hw_module.Paths = SimpleNamespace(persist_root=lambda: "")
  sys.modules.setdefault("openpilot.common.hardware.hw", hardware_hw_module)

  params_module = ModuleType("openpilot.common.params")
  params_module.Params = type("Params", (), {
    "get": lambda _self, _key, **_kwargs: None,
    "get_bool": lambda _self, _key: False,
  })
  params_module.UnknownKeyName = type("UnknownKeyName", (Exception,), {})
  sys.modules.setdefault("openpilot.common.params", params_module)

  swaglog_module = ModuleType("openpilot.common.swaglog")
  swaglog_module.cloudlog = SimpleNamespace(
    exception=lambda *_args, **_kwargs: None,
    warning=lambda *_args, **_kwargs: None,
  )
  sys.modules.setdefault("openpilot.common.swaglog", swaglog_module)

  messaging_module = ModuleType("openpilot.cereal.messaging")
  messaging_module.SubMaster = object
  sys.modules.setdefault("openpilot.cereal.messaging", messaging_module)

from opendbc.car.honda.values import HondaFlags
from openpilot.common.pid import PIDController
from openpilot.nrdr.features.longitudinal.longcontrol import (
  LONG_PID_SCALE_DEFAULTS,
  LONG_PID_SCALE_EPSILON,
  LONG_PID_SCALE_SLEW_PER_SECOND,
  LongCtrlState,
  NrdrLongControl,
  effective_long_pid_scale,
  longitudinal_pid_gains,
  scaled_pid_limits,
)
from openpilot.nrdr.features.longitudinal.longitudinal_planner import NrdrLongitudinalPlanner, apply_cruise_overspeed_allowance


def _long_control(*, enabled: bool, nidec: bool = True, gas_interceptor: bool = True, brand: str = "honda"):
  control = NrdrLongControl.__new__(NrdrLongControl)
  control.roen_acceleration_limits = enabled
  control.CP = SimpleNamespace(brand=brand, flags=HondaFlags.NIDEC if nidec else 0)
  control.CP_SP = SimpleNamespace(enableGasInterceptor=gas_interceptor)
  return control


def test_longitudinal_pid_gains_use_current_compatibility_group():
  cp = SimpleNamespace(longitudinalTuning=SimpleNamespace(
    deprecated=SimpleNamespace(kpBP=[0.0], kpV=[0.0]),
    kiBP=[0.0, 5.0],
    kiV=[1.2, 0.8],
  ))

  assert longitudinal_pid_gains(cp) == (([0.0], [0.0]), ([0.0, 5.0], [1.2, 0.8]))


def test_roen_limits_raise_only_nidec_pedal_ceiling():
  upstream = (-4.0, 1.6)
  assert _long_control(enabled=True)._accel_limits(upstream, 0.0) == (-4.0, 4.0)
  assert _long_control(enabled=True)._accel_limits(upstream, 12.5) == (-4.0, 3.5)
  assert _long_control(enabled=True)._accel_limits(upstream, 20.0) == (-4.0, 3.0)
  assert _long_control(enabled=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, nidec=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, gas_interceptor=False)._accel_limits(upstream, 0.0) == upstream
  assert _long_control(enabled=True, brand="other")._accel_limits(upstream, 0.0) == upstream


@pytest.mark.parametrize(("personality", "expected"), tuple(enumerate(LONG_PID_SCALE_DEFAULTS)))
def test_personality_pid_scale_defaults(personality, expected):
  assert effective_long_pid_scale(LONG_PID_SCALE_DEFAULTS, personality, True, False) == expected
  assert effective_long_pid_scale(LONG_PID_SCALE_DEFAULTS, SimpleNamespace(raw=personality), True, False) == expected


@pytest.mark.parametrize("personality", range(4))
def test_personality_pid_scale_is_forced_to_one_with_learning_or_without_interceptor(personality):
  deliberately_extreme = (5.0, 4.0, 3.0, 0.0)
  assert effective_long_pid_scale(deliberately_extreme, personality, True, True) == 1.0
  assert effective_long_pid_scale(deliberately_extreme, personality, False, False) == 1.0


@pytest.mark.parametrize("personality", (-1, 4, None, True, 0.5, "unknown", SimpleNamespace(raw=9)))
def test_invalid_personality_pid_scale_falls_back_to_one(personality):
  assert effective_long_pid_scale(LONG_PID_SCALE_DEFAULTS, personality, True, False) == 1.0


@pytest.mark.parametrize(("personality", "expected"), ((0, 5.0), (1, 0.0), (2, 1.0), (3, 1.0)))
def test_personality_pid_scale_bounds_and_invalid_values(personality, expected):
  scales = (20.0, -2.0, float("nan"), "invalid")
  assert effective_long_pid_scale(scales, personality, True, False) == expected


@pytest.mark.parametrize("scale", (2.0, 5.0))
def test_static_feedforward_inverse_limits_preserve_final_raw_bounds(scale):
  raw_limits = (-4.0, 2.0)
  feedforward = 0.5

  pid_limits = scaled_pid_limits(*raw_limits, feedforward, scale, True)
  final_limits = tuple((limit - feedforward) * scale + feedforward for limit in pid_limits)

  assert final_limits == pytest.approx(raw_limits)


@pytest.mark.parametrize("scale", (2.0, 5.0))
def test_dynamic_feedforward_inverse_limits_preserve_final_raw_bounds(scale):
  raw_limits = (-4.0, 2.0)

  pid_limits = scaled_pid_limits(*raw_limits, 0.5, scale, False)
  final_limits = tuple(limit * scale for limit in pid_limits)

  assert final_limits == pytest.approx(raw_limits)


@pytest.mark.parametrize("scale", (1.0, 0.8, 0.0))
@pytest.mark.parametrize("static_feedforward", (False, True))
def test_pid_scales_at_or_below_one_leave_limits_exact(scale, static_feedforward):
  assert scaled_pid_limits(-4.0, 2.0, 0.5, scale, static_feedforward) == (-4.0, 2.0)


def _scale_control(*, scale=1.0, live_learning_gas=False, gas_interceptor=True):
  control = NrdrLongControl.__new__(NrdrLongControl)
  control.pid_scales = LONG_PID_SCALE_DEFAULTS
  control.pid_scale = scale
  control.live_learning_gas = live_learning_gas
  control.CP_SP = SimpleNamespace(enableGasInterceptor=gas_interceptor)
  control.long_control_state = LongCtrlState.pid
  return control


@pytest.mark.parametrize("scale", (0.0, LONG_PID_SCALE_EPSILON))
def test_zero_and_near_zero_dynamic_pid_scale_clears_and_freezes_integrator(scale):
  control = _scale_control(scale=scale)
  control.static_feedforward = False
  control.pid = PIDController(0.0, 1.0, pos_limit=2.0, neg_limit=-4.0, rate=100)
  control.pid.i = 0.25

  output = control._pid_accel(SimpleNamespace(aEgo=0.0, vEgo=10.0), a_target=1.0)

  assert output == pytest.approx(scale)
  assert control.pid.i == 0.0


@pytest.mark.parametrize(
  ("start", "personality", "expected"),
  ((1.0, 0, 1.02), (1.0, 3, 0.98)),
)
def test_active_personality_transition_slews_at_bounded_rate(start, personality, expected):
  control = _scale_control(scale=start)

  control._update_pid_scale(personality, was_pid=True)

  assert control.pid_scale == pytest.approx(expected)
  assert abs(control.pid_scale - start) == pytest.approx(LONG_PID_SCALE_SLEW_PER_SECOND * 0.01)


@pytest.mark.parametrize(
  ("live_learning_gas", "gas_interceptor", "personality"),
  ((True, True, 0), (False, False, 0), (False, True, -1)),
)
def test_forced_one_scale_snaps_without_slew(live_learning_gas, gas_interceptor, personality):
  control = _scale_control(scale=2.0, live_learning_gas=live_learning_gas, gas_interceptor=gas_interceptor)

  control._update_pid_scale(personality, was_pid=True)

  assert control.pid_scale == 1.0


def test_entering_pid_uses_selected_personality_without_slew():
  control = _scale_control(scale=1.0)

  control._update_pid_scale(3, was_pid=False)

  assert control.pid_scale == LONG_PID_SCALE_DEFAULTS[3]


def test_long_control_forwards_raw_personality_to_nrdr_controller():
  wrapper_path = Path(__file__).parents[2] / "selfdrive" / "controls" / "lib" / "longcontrol.py"
  tree = ast.parse(wrapper_path.read_text(encoding="utf-8"))
  forwarding_calls = [
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
    and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "nrdr_controller"
  ]

  assert any(call.args and isinstance(call.args[-1], ast.Name) and call.args[-1].id == "personality"
             for call in forwarding_calls)


def test_controlsd_passes_selfdrive_personality_directly_to_long_control():
  controlsd_path = Path(__file__).parents[2] / "selfdrive" / "controls" / "controlsd.py"
  tree = ast.parse(controlsd_path.read_text(encoding="utf-8"))
  expected = ast.parse("self.sm['selfdriveState'].personality", mode="eval").body
  personality_values = [
    keyword.value
    for node in ast.walk(tree)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
    and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "LoC"
    for keyword in node.keywords
    if keyword.arg == "personality"
  ]

  assert any(ast.dump(value) == ast.dump(expected) for value in personality_values)


def test_on_device_longitudinal_items_follow_toggle_then_option_order():
  layout_path = Path(__file__).parents[2] / "nrdr" / "ui" / "settings" / "longitudinal_tuning.py"
  tree = ast.parse(layout_path.read_text(encoding="utf-8"))
  initialize = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "_initialize_items")
  widgets_by_attribute = {}
  for node in initialize.body:
    if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute)
            and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)):
      continue
    if node.value.func.id not in ("toggle_item_sp", "option_item_sp"):
      continue
    param = next(keyword.value.value for keyword in node.value.keywords
                 if keyword.arg == "param" and isinstance(keyword.value, ast.Constant))
    widgets_by_attribute[node.targets[0].attr] = (param, node.value.func.id.removesuffix("_item_sp"))

  returned = next(node for node in initialize.body if isinstance(node, ast.Return))
  assert isinstance(returned.value, ast.List)
  ordered_items = [widgets_by_attribute[item.attr] for item in returned.value.elts
                   if isinstance(item, ast.Attribute) and item.attr in widgets_by_attribute]
  keys = [key for key, _ in ordered_items]
  widgets = [widget for _, widget in ordered_items]

  assert keys[0] == "HondaLiveLearningGas"
  assert max(i for i, widget in enumerate(widgets) if widget == "toggle") < min(i for i, widget in enumerate(widgets) if widget == "option")
  assert [key for key in keys if key.startswith("LongPidTuneScale")] == [
    "LongPidTuneScaleAggressive",
    "LongPidTuneScaleStandard",
    "LongPidTuneScaleRelaxed",
    "LongPidTuneScaleEcon",
  ]


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
