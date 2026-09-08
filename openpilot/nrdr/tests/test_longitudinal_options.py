import ast
import math
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
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
from openpilot.cereal import log
from openpilot.common.pid import PIDController
from openpilot.nrdr.features.longitudinal import longitudinal_planner as longitudinal_planner_module
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
from openpilot.nrdr.features.longitudinal.longitudinal_planner import (
  SUNNY_ACCEL_PROFILE_BP,
  SUNNY_ACCEL_PROFILE_ECO,
  SUNNY_ACCEL_PROFILE_NORMAL,
  SUNNY_ACCEL_PROFILE_SPORT,
  NrdrLongitudinalPlanner,
  apply_cruise_overspeed_allowance,
  sunny_personality_accel_max,
)


LONGITUDINAL_PERSONALITIES = (
  log.LongitudinalPersonality.aggressive,
  log.LongitudinalPersonality.standard,
  log.LongitudinalPersonality.relaxed,
  log.LongitudinalPersonality.econ,
)
VIBE_PROFILE_BP = (0.0, 4.0, 6.0, 9.0, 16.0, 25.0, 30.0, 55.0)
VIBE_PROFILE_ECO = (2.0, 1.99, 1.88, 1.10, 0.50, 0.292, 0.15, 0.10)
VIBE_PROFILE_NORMAL = (2.0, 2.0, 1.94, 1.22, 0.635, 0.33, 0.20, 0.16)
VIBE_PROFILE_SPORT = (2.0, 2.0, 2.0, 1.85, 0.80, 0.54, 0.32, 0.22)


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


def _planner(*, enabled: bool, nidec: bool = True, gas_interceptor: bool = True, brand: str = "honda",
             personality_profiles: bool = False, cruise_scale: float = 1.0):
  planner = NrdrLongitudinalPlanner.__new__(NrdrLongitudinalPlanner)
  planner.roen_acceleration_limits = enabled
  planner.personality_accel_profiles = personality_profiles
  planner.CP = SimpleNamespace(brand=brand, flags=HondaFlags.NIDEC if nidec else 0)
  planner.CP_SP = SimpleNamespace(enableGasInterceptor=gas_interceptor)
  planner.tune = SimpleNamespace(a_cruise_max_scale=cruise_scale)
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


@pytest.mark.parametrize(
  ("personality", "profile"),
  (
    (log.LongitudinalPersonality.aggressive, VIBE_PROFILE_SPORT),
    (log.LongitudinalPersonality.standard, VIBE_PROFILE_NORMAL),
    (log.LongitudinalPersonality.relaxed, VIBE_PROFILE_ECO),
    (log.LongitudinalPersonality.econ, VIBE_PROFILE_ECO),
  ),
)
def test_sunny_personality_profiles_match_final_vibe_breakpoints(personality, profile):
  assert SUNNY_ACCEL_PROFILE_BP == VIBE_PROFILE_BP
  assert SUNNY_ACCEL_PROFILE_ECO == VIBE_PROFILE_ECO
  assert SUNNY_ACCEL_PROFILE_NORMAL == VIBE_PROFILE_NORMAL
  assert SUNNY_ACCEL_PROFILE_SPORT == VIBE_PROFILE_SPORT
  actual = [sunny_personality_accel_max(speed, personality) for speed in VIBE_PROFILE_BP]
  assert actual == pytest.approx(profile)
  assert [sunny_personality_accel_max(speed, SimpleNamespace(raw=personality)) for speed in VIBE_PROFILE_BP] == pytest.approx(profile)


def test_sunny_personality_profile_interpolation_is_ordered_and_endpoint_saturating():
  speeds = np.linspace(-5.0, 70.0, 301)
  eco = np.asarray([sunny_personality_accel_max(speed, log.LongitudinalPersonality.econ) for speed in speeds])
  relaxed = np.asarray([sunny_personality_accel_max(speed, log.LongitudinalPersonality.relaxed) for speed in speeds])
  normal = np.asarray([sunny_personality_accel_max(speed, log.LongitudinalPersonality.standard) for speed in speeds])
  sport = np.asarray([sunny_personality_accel_max(speed, log.LongitudinalPersonality.aggressive) for speed in speeds])

  assert eco == pytest.approx(relaxed)
  assert np.all(sport >= normal)
  assert np.all(normal >= eco)
  assert sport[0] == sport[20] == VIBE_PROFILE_SPORT[0]
  assert sport[-1] == VIBE_PROFILE_SPORT[-1]


@pytest.mark.parametrize(
  ("personality", "profile"),
  (
    (log.LongitudinalPersonality.aggressive, VIBE_PROFILE_SPORT),
    (log.LongitudinalPersonality.standard, VIBE_PROFILE_NORMAL),
    (log.LongitudinalPersonality.relaxed, VIBE_PROFILE_ECO),
  ),
)
def test_sunny_personality_profile_uses_linear_interpolation_between_every_breakpoint(personality, profile):
  for left, right, left_value, right_value in zip(
    VIBE_PROFILE_BP[:-1], VIBE_PROFILE_BP[1:], profile[:-1], profile[1:], strict=True,
  ):
    midpoint = (left + right) / 2.0
    assert sunny_personality_accel_max(midpoint, personality) == pytest.approx((left_value + right_value) / 2.0)


@pytest.mark.parametrize("personality", (-1, 4, None, True, 0.5, "unknown", float("inf"), SimpleNamespace(raw=9)))
def test_invalid_accel_personality_falls_back_to_standard(personality):
  for speed in VIBE_PROFILE_BP:
    assert sunny_personality_accel_max(speed, personality) == pytest.approx(
      sunny_personality_accel_max(speed, log.LongitudinalPersonality.standard),
    )


@pytest.mark.parametrize("speed", (
  None, True, "unknown", float("nan"), float("inf"), float("-inf"),
  pytest.param(10 ** 10_000, id="overflowing-int"),
))
def test_nonfinite_or_malformed_speed_disables_profile_ceiling(speed):
  assert sunny_personality_accel_max(speed, log.LongitudinalPersonality.aggressive) is None


@pytest.mark.parametrize("enabled", (False, True))
@pytest.mark.parametrize("speed", (0.0, 4.0, 12.5, 25.0, 55.0))
@pytest.mark.parametrize("personality", LONGITUDINAL_PERSONALITIES)
def test_disabled_personality_profiles_are_exact_existing_platform_parity(enabled, speed, personality):
  planner = _planner(enabled=enabled, personality_profiles=False)
  assert planner.personality_accel_ceiling(speed, personality) is None


def test_personality_profile_setting_refreshes_from_planner_snapshot_and_defaults_off(monkeypatch):
  planner = NrdrLongitudinalPlanner.__new__(NrdrLongitudinalPlanner)
  planner.CP = SimpleNamespace(deprecated=SimpleNamespace(vEgoStopping=0.5))
  snapshot = SimpleNamespace(generation=7)
  planner.params = SimpleNamespace(snapshot=snapshot)
  bool_values = {}
  seen_bool_keys = []

  monkeypatch.setattr(longitudinal_planner_module, "read_float", lambda _snapshot, _key, default, *_bounds: default)

  def fake_read_bool(_snapshot, key, default):
    seen_bool_keys.append(key)
    return bool_values.get(key, default)

  monkeypatch.setattr(longitudinal_planner_module, "read_bool", fake_read_bool)

  planner._refresh_settings()
  assert planner.personality_accel_profiles is False
  assert longitudinal_planner_module.NrdrParamKey.NRDR_PERSONALITY_ACCEL_PROFILES in seen_bool_keys

  bool_values[longitudinal_planner_module.NrdrParamKey.NRDR_PERSONALITY_ACCEL_PROFILES] = True
  snapshot.generation = 8
  planner._refresh_settings()
  assert planner.personality_accel_profiles is True
  assert planner.settings_generation == 8


@pytest.mark.parametrize("enabled", (False, True))
@pytest.mark.parametrize("scale", (0.0, 0.5, 1.0, 3.0))
@pytest.mark.parametrize("speed", (0.0, 4.0, 9.0, 16.0, 40.0, 55.0))
@pytest.mark.parametrize("personality", LONGITUDINAL_PERSONALITIES)
def test_personality_profile_can_only_lower_existing_cruise_ceiling(enabled, scale, speed, personality):
  planner = _planner(enabled=enabled, personality_profiles=True, cruise_scale=scale)
  platform_max = planner.max_accel(speed)
  profile_max = sunny_personality_accel_max(speed, personality)
  assert planner.personality_accel_ceiling(speed, personality) == pytest.approx(profile_max)
  assert min(platform_max, planner.personality_accel_ceiling(speed, personality)) <= platform_max


def test_profile_setting_never_changes_roen_turn_or_global_accel_envelopes():
  planner = _planner(enabled=True, personality_profiles=True)
  assert planner.max_accel(0.0) == 4.0
  assert planner.turn_accel_threshold() == 1.3
  assert planner.personality_accel_ceiling(0.0, log.LongitudinalPersonality.relaxed) == 2.0


def test_core_planner_applies_profile_only_to_positive_cruise_ceiling():
  planner_path = Path(__file__).parents[2] / "selfdrive" / "controls" / "lib" / "longitudinal_planner.py"
  tree = ast.parse(planner_path.read_text(encoding="utf-8"))
  cruise_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name) and node.func.id == "get_cruise_accel"]
  assert len(cruise_calls) == 1
  keywords = {keyword.arg: keyword.value for keyword in cruise_calls[0].keywords}
  max_override = keywords["max_accel_override"]
  turn_threshold = keywords["min_lat_accel"]
  positive_ceiling = keywords["positive_accel_ceiling"]
  assert isinstance(max_override, ast.Call) and isinstance(max_override.func, ast.Attribute)
  assert max_override.func.attr == "max_accel"
  assert isinstance(turn_threshold, ast.Call) and isinstance(turn_threshold.func, ast.Attribute)
  assert turn_threshold.func.attr == "turn_accel_threshold"
  assert isinstance(positive_ceiling, ast.Call) and isinstance(positive_ceiling.func, ast.Attribute)
  assert positive_ceiling.func.attr == "personality_accel_ceiling"

  platform_max_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute) and node.func.attr == "max_accel"]
  assert len(platform_max_calls) == 2
  accel_clip_assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                            and any(isinstance(target, ast.Name) and target.id == "accel_clip" for target in node.targets)
                            and isinstance(node.value, ast.List)]
  assert len(accel_clip_assignments) == 1
  assert {id(call) for call in platform_max_calls} == {id(max_override), id(accel_clip_assignments[0].value.elts[1])}

  profile_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute) and node.func.attr == "personality_accel_ceiling"]
  assert profile_calls == [positive_ceiling]
  assert ast.dump(positive_ceiling.args[1]) == ast.dump(ast.parse("personality", mode="eval").body)


def _load_core_cruise_accel():
  planner_path = Path(__file__).parents[2] / "selfdrive" / "controls" / "lib" / "longitudinal_planner.py"
  tree = ast.parse(planner_path.read_text(encoding="utf-8"))
  required_assignments = {
    "A_CRUISE_MAX_VALS", "A_CRUISE_MAX_BP", "J_CRUISE_VALS", "A_CRUISE_MIN",
    "MIN_ALLOW_THROTTLE_SPEED", "_A_TOTAL_MAX_V", "_A_TOTAL_MAX_BP",
  }
  required_functions = {"get_max_accel", "limit_accel_in_turns", "get_cruise_accel"}
  nodes = [
    node for node in tree.body
    if (isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(isinstance(target, ast.Name) and target.id in required_assignments
                for target in (node.targets if isinstance(node, ast.Assign) else [node.target])))
    or (isinstance(node, ast.FunctionDef) and node.name in required_functions)
  ]
  namespace = {
    "math": math,
    "np": np,
    "CV": SimpleNamespace(DEG_TO_RAD=math.pi / 180.0),
    "ACCEL_MIN": -3.5,
    "ACCEL_MAX": 2.0,
  }
  exec(compile(ast.Module(body=nodes, type_ignores=[]), planner_path, "exec"), namespace)
  return namespace["get_cruise_accel"]


def test_personality_ceiling_changes_positive_acc_only_and_preserves_braking():
  get_cruise_accel = _load_core_cruise_accel()
  cp = SimpleNamespace(steerRatio=15.0, wheelbase=2.7)
  common = {
    "e2e": False, "v_ego": 10.0, "angle_steers": 0.0, "CP": cp, "dt": 0.05,
    "accel_coast": -0.3, "allow_throttle": True,
  }

  braking_original = get_cruise_accel(v_cruise=5.0, a_cruise_prev=-0.5, max_accel_override=2.0, **common)
  braking_profiled = get_cruise_accel(v_cruise=5.0, a_cruise_prev=-0.5, max_accel_override=2.0,
                                      positive_accel_ceiling=0.2, **common)
  accelerating_original = get_cruise_accel(v_cruise=20.0, a_cruise_prev=0.5, max_accel_override=2.0, **common)
  accelerating_profiled = get_cruise_accel(v_cruise=20.0, a_cruise_prev=0.5, max_accel_override=2.0,
                                           positive_accel_ceiling=0.2, **common)

  assert braking_original < 0.0
  assert braking_profiled == braking_original
  assert accelerating_profiled < accelerating_original


def test_personality_ceiling_preserves_no_throttle_coast_braking_exactly():
  get_cruise_accel = _load_core_cruise_accel()
  common = {
    "e2e": False, "v_cruise": 4.85, "v_ego": 4.9, "a_cruise_prev": -0.15,
    "angle_steers": 0.0, "CP": SimpleNamespace(steerRatio=15.0, wheelbase=2.7), "dt": 0.05,
    "accel_coast": -0.3, "allow_throttle": False, "max_accel_override": 4.0,
    "min_lat_accel": 1.3,
  }
  original = get_cruise_accel(positive_accel_ceiling=None, **common)
  profiled = get_cruise_accel(positive_accel_ceiling=1.97, **common)

  assert original == pytest.approx(-0.1280000000000001)
  assert profiled == original


@pytest.mark.parametrize("platform_max", (1.6, 4.0), ids=("standard-platform", "roen"))
@pytest.mark.parametrize("allow_throttle", (False, True))
@pytest.mark.parametrize("v_ego", (2.5, 3.0, 4.0, 4.9, 5.0))
@pytest.mark.parametrize("accel_coast", (-0.6, -0.3, 0.2))
@pytest.mark.parametrize("angle_steers", (0.0, 30.0))
def test_personality_ceiling_is_exact_noop_for_all_negative_cruise_targets(
  platform_max, allow_throttle, v_ego, accel_coast, angle_steers,
):
  get_cruise_accel = _load_core_cruise_accel()
  common = {
    "e2e": False, "v_cruise": v_ego - 0.05, "v_ego": v_ego, "a_cruise_prev": -0.15,
    "angle_steers": angle_steers, "CP": SimpleNamespace(steerRatio=15.0, wheelbase=2.7), "dt": 0.05,
    "accel_coast": accel_coast, "allow_throttle": allow_throttle, "max_accel_override": platform_max,
    "min_lat_accel": 1.3,
  }
  baseline = get_cruise_accel(positive_accel_ceiling=None, **common)
  profiled = get_cruise_accel(positive_accel_ceiling=0.1, **common)

  assert baseline <= 0.0
  assert profiled == baseline


def test_personality_ceiling_transition_keeps_existing_positive_jerk_slew():
  get_cruise_accel = _load_core_cruise_accel()
  v_ego = 10.0
  previous_accel = 1.0
  dt = 0.05
  profiled = get_cruise_accel(
    e2e=False, v_cruise=20.0, v_ego=v_ego, a_cruise_prev=previous_accel,
    angle_steers=0.0, CP=SimpleNamespace(steerRatio=15.0, wheelbase=2.7), dt=dt,
    accel_coast=-0.3, allow_throttle=True, max_accel_override=2.0,
    min_lat_accel=0.0, positive_accel_ceiling=0.1,
  )
  jerk_limit = float(np.interp(v_ego, (0.0, 10.0, 25.0, 40.0), (1.6, 1.2, 0.8, 0.6))) * dt

  assert profiled == pytest.approx(previous_accel - jerk_limit)
  assert abs(profiled - previous_accel) == pytest.approx(jerk_limit)


@pytest.mark.parametrize("ceiling", (None, "invalid", float("nan"), float("inf"), float("-inf")))
def test_invalid_positive_ceiling_preserves_existing_cruise_result(ceiling):
  get_cruise_accel = _load_core_cruise_accel()
  common = {
    "e2e": False, "v_cruise": 20.0, "v_ego": 10.0, "a_cruise_prev": 0.5,
    "angle_steers": 0.0, "CP": SimpleNamespace(steerRatio=15.0, wheelbase=2.7), "dt": 0.05,
    "accel_coast": -0.3, "allow_throttle": True, "max_accel_override": 2.0, "min_lat_accel": 0.0,
  }
  assert get_cruise_accel(positive_accel_ceiling=ceiling, **common) == get_cruise_accel(
    positive_accel_ceiling=None, **common,
  )


def test_e2e_cruise_path_ignores_personality_max_override():
  get_cruise_accel = _load_core_cruise_accel()
  cp = SimpleNamespace(steerRatio=15.0, wheelbase=2.7)
  common = {
    "e2e": True, "v_cruise": 20.0, "v_ego": 10.0, "a_cruise_prev": 0.5,
    "angle_steers": 0.0, "CP": cp, "dt": 0.05, "accel_coast": -0.3, "allow_throttle": True,
  }
  assert get_cruise_accel(max_accel_override=0.05, positive_accel_ceiling=0.01, **common) == get_cruise_accel(
    max_accel_override=None, positive_accel_ceiling=None, **common,
  )


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
