from __future__ import annotations

import ast
from collections import deque
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest


CONTROLS_DIR = Path(__file__).resolve().parents[1]
LANE_CENTERING_PATH = CONTROLS_DIR / "lib" / "lane_centering.py"
DRIVE_HELPERS_PATH = CONTROLS_DIR / "lib" / "drive_helpers.py"


def _load_drive_helpers() -> ModuleType:
  """Compile the production filters and shared curvature limiter in isolation."""
  tree = ast.parse(DRIVE_HELPERS_PATH.read_text(encoding="utf-8"), filename=str(DRIVE_HELPERS_PATH))
  constant_names = {
    "MIN_SPEED",
    "MAX_CURVATURE",
    "MAX_LATERAL_JERK",
    "MAX_LATERAL_ACCEL_NO_ROLL",
  }
  function_names = {"smooth_value", "clamp", "clip_curvature"}
  selected_nodes = []
  found_constants = set()
  found_functions = set()
  for node in tree.body:
    if isinstance(node, ast.Assign):
      assigned = {target.id for target in node.targets if isinstance(target, ast.Name)}
      if assigned & constant_names:
        selected_nodes.append(node)
        found_constants.update(assigned & constant_names)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in function_names:
      selected_nodes.append(node)
      found_functions.add(node.name)
  assert found_constants == constant_names
  assert found_functions == function_names

  module = ModuleType("standalone_drive_helpers")
  module.__dict__.update(
    np=np,
    DT_CTRL=0.01,
    DT_MDL=0.05,
    ACCELERATION_DUE_TO_GRAVITY=9.81,
  )
  executable = ast.fix_missing_locations(ast.Module(body=selected_nodes, type_ignores=[]))
  exec(compile(executable, str(DRIVE_HELPERS_PATH), "exec"), module.__dict__)
  return module


drive_helpers = _load_drive_helpers()


def _load_lane_centering() -> ModuleType:
  """Execute the real controller, replacing only unavailable openpilot imports."""
  tree = ast.parse(LANE_CENTERING_PATH.read_text(encoding="utf-8"), filename=str(LANE_CENTERING_PATH))
  kept_nodes = []
  removed_modules = []
  for node in tree.body:
    if isinstance(node, ast.ImportFrom) and node.module is not None and node.module.startswith("openpilot"):
      removed_modules.append(node.module)
    else:
      kept_nodes.append(node)

  assert set(removed_modules) == {
    "openpilot.cereal",
    "openpilot.common.constants",
    "openpilot.common.realtime",
    "openpilot.selfdrive.controls.lib.drive_helpers",
  }

  class LaneChangeState:
    off = 0

  class CV:
    MPH_TO_MS = 0.44704

  module = ModuleType("standalone_lane_centering")
  module.__dict__.update(
    log=SimpleNamespace(LaneChangeState=LaneChangeState),
    CV=CV,
    DT_CTRL=0.01,
    DT_MDL=0.05,
    smooth_value=drive_helpers.smooth_value,
  )
  executable = ast.fix_missing_locations(ast.Module(body=kept_nodes, type_ignores=tree.type_ignores))
  exec(compile(executable, str(LANE_CENTERING_PATH), "exec"), module.__dict__)
  return module


lane_centering = _load_lane_centering()
_MISSING = object()


def _values(spec, x: np.ndarray) -> np.ndarray:
  values = spec(x) if callable(spec) else spec
  values = np.asarray(values, dtype=float)
  if values.ndim == 0:
    values = np.full_like(x, float(values))
  return values


def _line(x: np.ndarray, y) -> SimpleNamespace:
  return SimpleNamespace(x=x.copy(), y=_values(y, x))


def _model(*, center=0.0, model_path=0.0, width=3.6,
           lane_probs=(0.8, 0.8), lane_stds=(0.1, 0.1),
           x: np.ndarray | None = None, y_std=0.1,
           position_t=_MISSING, lane_change_state=0) -> SimpleNamespace:
  x = np.linspace(0.0, 70.0, 141) if x is None else np.asarray(x, dtype=float)
  center_y = _values(center, x)
  width_y = _values(width, x)
  position = _line(x, model_path)
  if y_std is not None:
    position.yStd = _values(y_std, x)
  if position_t is not _MISSING:
    position.t = _values(position_t, x)
  return SimpleNamespace(
    laneLines=[
      _line(x, 0.0),
      _line(x, center_y - 0.5 * width_y),
      _line(x, center_y + 0.5 * width_y),
      _line(x, 0.0),
    ],
    laneLineProbs=np.array([0.0, *lane_probs, 0.0]),
    laneLineStds=np.array([1.0, *lane_stds, 1.0]),
    position=position,
    meta=SimpleNamespace(laneChangeState=lane_change_state),
  )


def _update(controller, model, **overrides) -> float:
  arguments = {
    "model_curvature": 0.0,
    "model_v2": model,
    "v_ego": 25.0,
    "min_speed_mph": 12,
    "enabled": True,
    "offset": 0.0,
    "e2e_authority": 0.0,
    "strength": 1.0,
    "lat_active": True,
    "model_valid": True,
    "pause_on_signal": False,
    "turn_signal_active": False,
    "driver_override": False,
    "model_frame": None,
    "action_time": 0.275,
  }
  arguments.update(overrides)
  return controller.update(**arguments)


def test_action_time_metadata_requires_an_exact_valid_model_frame():
  timing = SimpleNamespace(modelMonoTime=123_000_000, lateralActionTime=0.275)
  boundary_timing = SimpleNamespace(
    modelMonoTime=123_000_000,
    lateralActionTime=lane_centering._MAX_ACTION_TIME,
  )

  assert lane_centering.lane_centering_action_time(123_000_000, timing, True) == pytest.approx(0.275)
  assert lane_centering.lane_centering_action_time(123_000_000, boundary_timing, True) == pytest.approx(
    lane_centering._MAX_ACTION_TIME,
  )
  assert lane_centering.lane_centering_action_time(123_000_001, timing, True) is None
  assert lane_centering.lane_centering_action_time(123_000_000, timing, False) is None
  assert lane_centering.lane_centering_action_time(0, timing, True) is None


@pytest.mark.parametrize(
  "value",
  [None, "bad", 0.0, -0.1, np.nan, np.inf, lane_centering._MAX_ACTION_TIME + 2e-6, 1e308],
  ids=["missing", "nonnumeric", "zero", "negative", "nan", "infinite", "above-envelope", "huge"],
)
def test_action_time_metadata_rejects_invalid_values(value):
  timing = SimpleNamespace(modelMonoTime=123_000_000, lateralActionTime=value)

  assert lane_centering.lane_centering_action_time(123_000_000, timing, True) is None


def test_action_time_metadata_rejects_missing_fields():
  assert lane_centering.lane_centering_action_time(123_000_000, SimpleNamespace(), True) is None


@pytest.mark.parametrize(
  "action_time",
  [None, "bad", 0.0, -0.1, np.nan, np.inf, lane_centering._MAX_ACTION_TIME + 2e-6, 1e308],
  ids=["missing", "nonnumeric", "zero", "negative", "nan", "infinite", "above-envelope", "huge"],
)
def test_missing_or_invalid_action_time_fails_closed_to_model_action(action_time):
  controller = lane_centering.LaneCenteringController()
  model_action = 0.0023

  result = _update(controller, _model(center=0.45), model_curvature=model_action, action_time=action_time)

  assert result == pytest.approx(model_action)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.TIMING_UNAVAILABLE
  assert not controller.diagnostics.active
  assert not controller._lanes_armed
  assert controller._lane_width_estimate is None
  assert controller._path_cache_key is None


def test_missing_action_time_releases_an_existing_correction_smoothly():
  controller = lane_centering.LaneCenteringController()
  model = _model(center=0.45)
  _update(controller, model, action_time=0.275)
  previous_correction = controller._correction
  assert previous_correction > 0.0

  model_action = -0.001
  result = _update(controller, model, model_curvature=model_action, action_time=None)
  expected_correction = previous_correction * np.exp(-0.01 / lane_centering._CONFIDENCE_RELEASE_TAU)

  assert controller._correction == pytest.approx(expected_correction)
  assert result == pytest.approx(model_action + expected_correction)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.TIMING_UNAVAILABLE
  assert not controller.diagnostics.active


def test_half_second_physical_delay_is_outside_gate_and_uses_pure_model_action():
  controller = lane_centering.LaneCenteringController()
  model_action = -0.0023

  result = _update(
    controller,
    _model(center=0.45),
    model_curvature=model_action,
    action_time=0.500 + 0.075,
  )

  assert result == pytest.approx(model_action)
  assert controller._correction == 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.TIMING_UNAVAILABLE
  assert not controller.diagnostics.active


def test_action_time_gate_accepts_boundary_fades_above_it_and_recovers_without_stale_cache():
  controller = lane_centering.LaneCenteringController()
  right_model = _model(center=0.45)
  left_model = _model(center=-0.45)
  frame = 1_000_000_000

  accepted = _update(
    controller, right_model, model_frame=frame,
    action_time=lane_centering._MAX_ACTION_TIME,
  )
  accepted_correction = controller._correction
  assert accepted > 0.0
  assert accepted_correction > 0.0

  faded = _update(
    controller, left_model, model_frame=frame,
    action_time=lane_centering._MAX_ACTION_TIME + 2e-6,
  )
  expected_faded = accepted_correction * np.exp(-0.01 / lane_centering._CONFIDENCE_RELEASE_TAU)
  assert faded == pytest.approx(expected_faded)
  assert controller._correction == pytest.approx(expected_faded)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.TIMING_UNAVAILABLE
  assert controller._path_cache_key is None

  recovered = _update(
    controller, left_model, model_frame=frame,
    action_time=lane_centering._MAX_ACTION_TIME,
  )
  assert recovered < 0.0
  assert controller._correction < 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


@pytest.mark.parametrize("curve_sign", [-1.0, 1.0])
def test_coherent_curved_lane_and_model_need_no_correction(curve_sign):
  curve = lambda x: curve_sign * (0.0012 * x ** 2 + 0.02 * x)
  model = _model(center=curve, model_path=curve)
  controller = lane_centering.LaneCenteringController()

  result = _update(controller, model, model_curvature=0.002 * curve_sign)

  assert result == pytest.approx(0.002 * curve_sign, abs=1e-12)
  assert controller.diagnostics.target_correction_curvature == pytest.approx(0.0, abs=1e-12)
  assert controller.diagnostics.center_error == pytest.approx(0.0, abs=1e-12)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CENTERED


@pytest.mark.parametrize(
  ("translation", "heading", "curvature"),
  [
    (0.4, 0.03, 0.0015),
    (-0.4, -0.03, -0.0015),
    (0.2, -0.04, 0.0020),
    (-0.2, 0.04, -0.0020),
  ],
)
def test_shared_translation_heading_and_curvature_cancel_exactly(translation, heading, curvature):
  shared_path = lambda x: translation + heading * x + 0.5 * curvature * x ** 2
  model = _model(center=shared_path, model_path=shared_path)
  controller = lane_centering.LaneCenteringController()
  model_action = -0.0031

  result = _update(controller, model, model_curvature=model_action)

  assert result == pytest.approx(model_action, abs=1e-12)
  assert controller.diagnostics.target_correction_curvature == pytest.approx(0.0, abs=1e-12)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CENTERED


@pytest.mark.parametrize("residual_sign", [-1.0, 1.0])
def test_shared_curvature_does_not_change_a_nonzero_lane_model_residual(residual_sign):
  residual = 0.45 * residual_sign
  shared_path = lambda x: -0.2 + 0.035 * x - 0.0008 * x ** 2
  base_controller = lane_centering.LaneCenteringController()
  shared_controller = lane_centering.LaneCenteringController()

  base_valid, base_correction = base_controller._raw_correction(
    _model(center=residual, model_path=0.0), 25.0, 0.0, 0.0,
  )
  shared_valid, shared_correction = shared_controller._raw_correction(
    _model(center=lambda x: shared_path(x) + residual, model_path=shared_path), 25.0, 0.0, 0.0,
  )

  assert base_valid and shared_valid
  assert shared_correction == pytest.approx(base_correction, abs=1e-12)


def test_position_time_maps_action_and_preview_into_path_distance():
  position_t = np.linspace(0.0, 3.0, 121)
  position_x = 12.0 * position_t + 1.5 * position_t ** 2
  action_time = 0.275
  model = _model(x=position_x, position_t=position_t, center=0.45)
  controller = lane_centering.LaneCenteringController()

  valid, raw_correction = controller._raw_correction(model, 25.0, 0.0, 0.0, action_time=action_time)

  sample_times = np.linspace(
    action_time + lane_centering._PREVIEW_START,
    action_time + lane_centering._POST_ACTION_PREVIEW,
    lane_centering._PATH_SAMPLE_COUNT,
  )
  action_x = np.interp(action_time, position_t, position_x)
  sampled_x = np.interp(sample_times, position_t, position_x)
  basis = 0.5 * (sampled_x - action_x) ** 2
  expected_correction = np.dot(basis, np.full_like(basis, 0.45 - lane_centering._CENTER_ERROR_DEADBAND)) / np.dot(basis, basis)
  expected_lookahead = np.interp(action_time + lane_centering._POST_ACTION_PREVIEW, position_t, position_x)
  assert valid
  assert raw_correction == pytest.approx(expected_correction)
  assert controller.diagnostics.lookahead == pytest.approx(expected_lookahead)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


def test_absent_and_empty_position_time_use_the_same_speed_fallback():
  absent_controller = lane_centering.LaneCenteringController()
  empty_controller = lane_centering.LaneCenteringController()

  absent_result = _update(absent_controller, _model(center=0.45))
  empty_result = _update(empty_controller, _model(center=0.45, position_t=[]))

  expected_lookahead = 25.0 * (0.275 + lane_centering._POST_ACTION_PREVIEW)
  assert absent_result == pytest.approx(empty_result)
  assert absent_controller.diagnostics.lookahead == pytest.approx(expected_lookahead)
  assert empty_controller.diagnostics.lookahead == pytest.approx(expected_lookahead)


@pytest.mark.parametrize(
  "position_t",
  [
    np.linspace(0.0, 3.0, 140),
    np.linspace(0.0, 3.0, 141).reshape(3, 47),
    np.concatenate((np.linspace(0.0, 1.0, 50), [np.nan], np.linspace(1.1, 3.0, 90))),
    np.concatenate((np.linspace(0.0, 1.5, 71), np.linspace(1.4, 3.0, 70))),
  ],
  ids=["length-mismatch", "not-one-dimensional", "nonfinite", "nonmonotonic"],
)
def test_nonempty_malformed_position_time_is_invalid(position_t):
  controller = lane_centering.LaneCenteringController()

  result = _update(controller, _model(center=0.45, position_t=position_t))

  assert result == pytest.approx(0.0)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.LANE_DATA_INVALID


@pytest.mark.parametrize(
  "position_t",
  [
    np.linspace(0.30, 3.30, 141),
    np.linspace(0.0, 1.20, 141),
  ],
  ids=["does-not-cover-action", "less-than-one-second-after-action"],
)
def test_position_time_with_insufficient_post_action_coverage_fails_closed(position_t):
  controller = lane_centering.LaneCenteringController()

  result = _update(controller, _model(center=0.45, position_t=position_t))

  assert result == pytest.approx(0.0)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.PREVIEW_TOO_SHORT


def test_position_time_accepts_exactly_one_second_after_action():
  action_time = 0.275
  position_t = np.linspace(0.0, action_time + lane_centering._MIN_POST_ACTION_PREVIEW, 141)
  position_x = 25.0 * position_t
  controller = lane_centering.LaneCenteringController()

  result = _update(
    controller,
    _model(x=position_x, center=0.45, position_t=position_t),
    action_time=action_time,
  )

  assert result > 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


def test_position_time_rejects_just_under_one_second_after_action():
  action_time = 0.275
  position_t = np.linspace(0.0, action_time + lane_centering._MIN_POST_ACTION_PREVIEW - 2e-6, 141)
  position_x = 25.0 * position_t
  controller = lane_centering.LaneCenteringController()

  result = _update(
    controller,
    _model(x=position_x, center=0.45, position_t=position_t),
    action_time=action_time,
  )

  assert result == pytest.approx(0.0)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.PREVIEW_TOO_SHORT


@pytest.mark.parametrize("offset_sign", [-1.0, 1.0])
def test_mirrored_lane_minus_model_offsets_have_mirrored_signs(offset_sign):
  model = _model(center=0.45 * offset_sign, model_path=0.0)
  controller = lane_centering.LaneCenteringController()

  result = _update(controller, model)

  assert result * offset_sign > 0.0
  assert controller.diagnostics.target_correction_curvature * offset_sign > 0.0
  assert controller.diagnostics.center_error == pytest.approx(0.45 * offset_sign)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


@pytest.mark.parametrize("offset_sign", [-1.0, 1.0])
def test_requested_center_offset_has_matching_sign_and_is_input_clamped(offset_sign):
  model = _model()
  requested = lane_centering.LaneCenteringController()
  extreme = lane_centering.LaneCenteringController()
  expected_clip = lane_centering.LaneCenteringController()

  valid, requested_correction = requested._raw_correction(model, 25.0, 0.20 * offset_sign, 0.0)
  valid_extreme, extreme_correction = extreme._raw_correction(model, 25.0, 100.0 * offset_sign, 0.0)
  valid_clipped, clipped_correction = expected_clip._raw_correction(
    model, 25.0, lane_centering._MAX_OFFSET * offset_sign, 0.0,
  )

  assert valid and valid_extreme and valid_clipped
  assert requested_correction * offset_sign > 0.0
  # Both the public boundary and the core's clearance guard clamp extreme offsets.
  public_extreme = _update(lane_centering.LaneCenteringController(), model, offset=100.0 * offset_sign)
  public_clipped = _update(
    lane_centering.LaneCenteringController(), model,
    offset=lane_centering._MAX_OFFSET * offset_sign,
  )
  assert public_extreme == pytest.approx(public_clipped)
  assert clipped_correction * offset_sign > 0.0
  assert extreme_correction == pytest.approx(clipped_correction)


def test_full_preview_fit_sees_interior_error_when_endpoint_error_is_zero():
  speed = 25.0
  action_time = 0.275
  preview_start = speed * (action_time + lane_centering._PREVIEW_START)
  preview_end = speed * (action_time + lane_centering._POST_ACTION_PREVIEW)
  x = np.unique(np.concatenate((np.linspace(0.0, 70.0, 701), [preview_start, preview_end])))
  interior_hump = lambda distance: 0.45 * np.sin(np.pi * (distance - preview_start) / (preview_end - preview_start))
  model = _model(x=x, center=interior_hump, model_path=0.0)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, speed, 0.0, 0.0, action_time=action_time)

  assert valid
  assert controller.diagnostics.center_error == pytest.approx(0.0, abs=1e-10)
  assert controller.diagnostics.effective_center_error == pytest.approx(0.0, abs=1e-10)
  assert correction > 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


def test_lane_probability_scales_authority_and_requires_rearm():
  model_full = _model(center=0.45, lane_probs=(0.8, 0.8))
  model_half = _model(center=0.45, lane_probs=(0.7, 0.7))
  full_controller = lane_centering.LaneCenteringController()
  half_controller = lane_centering.LaneCenteringController()

  full_valid, full_correction = full_controller._raw_correction(model_full, 25.0, 0.0, 0.0)
  half_valid, half_correction = half_controller._raw_correction(model_half, 25.0, 0.0, 0.0)

  assert full_valid and half_valid
  assert half_correction == pytest.approx(0.5 * full_correction)

  controller = lane_centering.LaneCenteringController()
  valid, _ = controller._raw_correction(_model(center=0.45, lane_probs=(0.64, 0.64)), 25.0, 0.0, 0.0)
  assert not valid
  assert not controller._lanes_armed

  valid, _ = controller._raw_correction(_model(center=0.45, lane_probs=(0.65, 0.65)), 25.0, 0.0, 0.0)
  assert valid
  assert controller._lanes_armed

  valid, held_correction = controller._raw_correction(
    _model(center=0.45, lane_probs=(0.61, 0.61)), 25.0, 0.0, 0.0,
  )
  assert valid
  assert held_correction > 0.0

  valid, _ = controller._raw_correction(_model(center=0.45, lane_probs=(0.59, 0.59)), 25.0, 0.0, 0.0)
  assert not valid
  assert not controller._lanes_armed
  valid, _ = controller._raw_correction(_model(center=0.45, lane_probs=(0.64, 0.64)), 25.0, 0.0, 0.0)
  assert not valid


def test_high_confidence_model_can_retain_authority_for_large_disagreement():
  model = _model(center=0.0, model_path=-0.7, y_std=0.1)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, 25.0, 0.0, 1.0)

  assert valid
  assert correction == pytest.approx(0.0)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.MODEL_AUTHORITY


def test_zero_strength_preserves_model_action_and_reports_inactive():
  controller = lane_centering.LaneCenteringController()
  model = _model(center=0.45)
  _update(controller, model, strength=1.0)
  assert controller._correction > 0.0
  model_action = -0.0024

  result = _update(controller, model, model_curvature=model_action, strength=0.0)

  assert result == pytest.approx(model_action)
  assert controller._correction == pytest.approx(0.0)
  assert controller.diagnostics.target_correction_curvature == pytest.approx(0.0)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.ZERO_STRENGTH
  assert not controller.diagnostics.active


def test_zero_strength_clears_residual_before_timing_confidence_and_signal_gates():
  controller = lane_centering.LaneCenteringController()
  healthy_model = _model(center=0.45)
  _update(controller, healthy_model, strength=1.0, action_time=0.275)
  assert controller._correction > 0.0

  invalid_model = _model(center=0.45, lane_probs=(0.0, 0.0))
  del invalid_model.laneLines
  model_action = -0.0024
  result = _update(
    controller,
    invalid_model,
    model_curvature=model_action,
    strength=0.0,
    action_time=None,
    pause_on_signal=True,
    turn_signal_active=True,
  )

  assert result == pytest.approx(model_action)
  assert controller._correction == 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.ZERO_STRENGTH
  assert not controller.diagnostics.active
  assert not controller._speed_armed
  assert not controller._lanes_armed
  assert controller._path_cache_key is None


@pytest.mark.parametrize(
  ("argument", "value"),
  [
    ("v_ego", np.inf),
    ("offset", np.inf),
    ("e2e_authority", np.inf),
    ("strength", np.inf),
    ("strength", -1e308),
    ("strength", 1e308),
  ],
)
def test_nonfinite_or_huge_public_inputs_fail_closed(argument, value):
  controller = lane_centering.LaneCenteringController()
  model_action = 0.0021

  result = _update(controller, _model(center=0.45), model_curvature=model_action, **{argument: value})

  assert result == pytest.approx(model_action)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.INVALID_INPUT
  assert controller._correction == 0.0
  assert not controller.diagnostics.active


def test_huge_finite_path_values_fail_closed_without_raising():
  controller = lane_centering.LaneCenteringController()
  model_action = 0.0021

  with np.errstate(over="ignore", invalid="ignore"):
    result = _update(controller, _model(center=0.0, model_path=1e308), model_curvature=model_action)

  assert result == pytest.approx(model_action)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.LANE_DATA_INVALID
  assert not controller.diagnostics.active


@pytest.mark.parametrize(
  "width",
  [
    lambda x: 3.4 + 1.5 * x / 50.0,
    lambda x: 3.4 - 0.9 * x / 50.0,
  ],
  ids=["too-wide-at-far-horizon", "too-narrow-at-far-horizon"],
)
def test_far_horizon_width_divergence_is_rejected_even_when_lookahead_width_is_valid(width):
  model = _model(width=width)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, 25.0, 0.0, 0.0)

  assert not valid
  assert correction == 0.0
  assert lane_centering._MIN_LANE_WIDTH < controller.diagnostics.lane_width < lane_centering._MAX_LANE_WIDTH
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.LANE_GEOMETRY_INVALID
  assert not controller._lanes_armed
  assert controller._lane_width_estimate is None


def _missing_lane_lines(model):
  del model.laneLines


def _too_few_lane_lines(model):
  model.laneLines = model.laneLines[:2]


def _short_probabilities(model):
  model.laneLineProbs = np.array([0.0, 0.8])


def _nonfinite_probability(model):
  model.laneLineProbs[1] = np.nan


def _mismatched_lane_xy(model):
  model.laneLines[1].y = model.laneLines[1].y[:-1]


def _nonmonotonic_lane_x(model):
  model.laneLines[2].x[20] = model.laneLines[2].x[19]


def _nonfinite_model_path(model):
  model.position.y[20] = np.inf


def _insufficient_path_coverage(model):
  model.position.x = model.position.x[:30]
  model.position.y = model.position.y[:30]
  model.position.yStd = model.position.yStd[:30]


@pytest.mark.parametrize(
  "damage",
  [
    _missing_lane_lines,
    _too_few_lane_lines,
    _short_probabilities,
    _nonfinite_probability,
    _mismatched_lane_xy,
    _nonmonotonic_lane_x,
    _nonfinite_model_path,
  ],
)
def test_malformed_paths_fail_closed_without_raising(damage):
  model = _model(center=0.45)
  damage(model)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, 25.0, 0.0, 0.0)

  assert not valid
  assert correction == 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.LANE_DATA_INVALID


def test_less_than_one_second_common_post_action_coverage_fails_closed():
  model = _model(center=0.45)
  _insufficient_path_coverage(model)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, 25.0, 0.0, 0.0, action_time=0.275)

  assert not valid
  assert correction == 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.PREVIEW_TOO_SHORT


def test_diagnostics_schema_remains_stable():
  assert tuple(lane_centering.LaneCenteringDiagnostics.__slots__) == (
    "reason",
    "speed_armed",
    "active",
    "correction_curvature",
    "target_correction_curvature",
    "center_error",
    "effective_center_error",
    "lane_width",
    "lookahead",
    "min_lane_probability",
    "max_lane_std",
  )


def test_optional_position_uncertainty_field_is_backward_compatible():
  model = _model(center=0.45, y_std=None)
  controller = lane_centering.LaneCenteringController()

  result = _update(controller, model, e2e_authority=1.0)

  assert result > 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING


def test_driver_override_returns_model_action_and_clears_all_control_memory():
  model = _model(center=0.45)
  controller = lane_centering.LaneCenteringController()
  corrected = _update(controller, model, model_frame=1_000_000_000)
  assert corrected > 0.0
  assert controller._speed_armed and controller._lanes_armed
  assert controller._lane_width_estimate is not None

  model_action = 0.00321
  result = _update(
    controller, model, model_curvature=model_action,
    driver_override=True, model_frame=1_000_000_000,
  )

  assert result == pytest.approx(model_action)
  assert controller._correction == 0.0
  assert not controller._speed_armed
  assert not controller._lanes_armed
  assert controller._lane_width_estimate is None
  assert controller._path_cache_key is None
  assert controller._path_cache == (False, 0.0)
  assert controller._last_model_frame is None
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.DRIVER_OVERRIDE
  assert not controller.diagnostics.active


def test_unchanged_model_frame_reuses_path_and_new_frame_refreshes_it():
  controller = lane_centering.LaneCenteringController()
  right_model = _model(center=0.45)
  left_model = _model(center=-0.45)

  _update(controller, right_model, model_frame=1_000_000_000)
  first_target = controller.diagnostics.target_correction_curvature
  _update(controller, left_model, model_frame=1_000_000_000)
  cached_target = controller.diagnostics.target_correction_curvature
  _update(controller, left_model, model_frame=1_050_000_000)
  refreshed_target = controller.diagnostics.target_correction_curvature

  assert first_target > 0.0
  assert cached_target == pytest.approx(first_target)
  assert refreshed_target < 0.0


def test_changed_action_time_recomputes_path_on_the_same_model_frame():
  controller = lane_centering.LaneCenteringController()
  model = _model(center=lambda x: 0.003 * x, model_path=0.0)
  frame = 1_000_000_000

  _update(controller, model, model_frame=frame, action_time=0.275)
  first_target = controller.diagnostics.target_correction_curvature
  _update(controller, model, model_frame=frame, action_time=0.450)
  changed_target = controller.diagnostics.target_correction_curvature

  assert controller._path_cache_key[-1] == pytest.approx(0.450)
  assert changed_target != pytest.approx(first_target)


def test_confidence_change_is_cached_only_until_the_next_model_frame():
  controller = lane_centering.LaneCenteringController()
  high_confidence = _model(center=0.45, lane_probs=(0.8, 0.8))
  low_confidence = _model(center=-0.45, lane_probs=(0.59, 0.59))

  _update(controller, high_confidence, model_frame=1_000_000_000)
  cached_correction = controller._correction
  _update(controller, low_confidence, model_frame=1_000_000_000)
  assert controller._correction == pytest.approx(cached_correction)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING

  _update(controller, low_confidence, model_frame=1_050_000_000)
  expected_faded = cached_correction * np.exp(-0.01 / lane_centering._CONFIDENCE_RELEASE_TAU)
  assert controller._correction == pytest.approx(expected_faded)
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.LANE_CONFIDENCE_LOW
  assert not controller._lanes_armed

  _update(controller, high_confidence, model_frame=1_100_000_000)
  assert controller._correction > 0.0
  assert controller.diagnostics.reason == lane_centering.LaneCenteringReason.CORRECTING
  assert controller._lanes_armed


@pytest.mark.parametrize("correction_sign", [-1.0, 1.0])
def test_final_correction_never_exceeds_cap(correction_sign):
  model = _model(model_path=-20.0 * correction_sign)
  controller = lane_centering.LaneCenteringController()
  outputs = []

  for frame in range(1, 6):
    outputs.append(_update(controller, model, model_frame=frame * 50_000_000))
    assert abs(controller.diagnostics.target_correction_curvature) <= lane_centering._MAX_FINAL_CORRECTION

  assert controller.diagnostics.target_correction_curvature == pytest.approx(
    correction_sign * lane_centering._MAX_FINAL_CORRECTION,
  )
  assert np.max(np.abs(outputs)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert outputs[-1] == pytest.approx(correction_sign * lane_centering._MAX_FINAL_CORRECTION, rel=1e-5)


def _simulate_straight_lane(*, strength: float, delay_s: float, speed: float = 25.0,
                            initial_offset: float = 0.60, duration_s: float = 12.0,
                            conservative_model_age_s: float = 0.075, x_end: float | None = None):
  """Synthetic linear bicycle loop; a numerical guard, never road validation.

  ``delay_s`` is the physical controller-to-steering delay. For conservative
  temporal alignment, the model path uses a state ``conservative_model_age_s``
  old and the published action time is their sum. The default 75 ms covers the
  50 ms model frame plus the publisher's 25 ms midpoint allowance.
  """
  dt = 0.01
  action_time = delay_s + conservative_model_age_s
  x_end = max(100.0, speed * (action_time + lane_centering._POST_ACTION_PREVIEW + 0.6)) if x_end is None else x_end
  model_x = np.linspace(0.0, x_end, 161)
  lateral_position = initial_offset
  heading = 0.0
  delayed_curvatures = deque([0.0] * max(1, round(delay_s / dt)))
  history_size = max(2, int(np.ceil(conservative_model_age_s / dt)) + 2)
  state_history = deque([(-conservative_model_age_s, lateral_position, heading)], maxlen=history_size)
  controller = lane_centering.LaneCenteringController()
  frame = 0
  model = None
  previous_limited_curvature = 0.0
  positions = []
  commands = []

  for step in range(round(duration_s / dt)):
    now = step * dt
    state_history.append((now, lateral_position, heading))
    if step % 5 == 0:
      frame += 50_000_000
      sample_time = now - conservative_model_age_s
      history_times = np.asarray([sample[0] for sample in state_history])
      sampled_position = float(np.interp(sample_time, history_times, [sample[1] for sample in state_history]))
      sampled_heading = float(np.interp(sample_time, history_times, [sample[2] for sample in state_history]))
      model = _model(x=model_x, model_path=lambda x: sampled_position + sampled_heading * x)

    requested_curvature = _update(
      controller, model, strength=strength, model_frame=frame,
      e2e_authority=0.0, v_ego=speed, action_time=action_time,
    )
    command, _ = drive_helpers.clip_curvature(
      speed, previous_limited_curvature, requested_curvature, 0.0,
    )
    previous_limited_curvature = command
    delayed_curvatures.append(command)
    applied_curvature = delayed_curvatures.popleft()

    # Small-angle kinematic bicycle equations with curvature as the input.
    heading += speed * applied_curvature * dt
    lateral_position += speed * heading * dt
    positions.append(lateral_position)
    commands.append(command)

  return np.asarray(positions), np.asarray(commands)


@pytest.mark.parametrize(
  ("strength", "delay_s", "max_excursion", "max_final_error"),
  [
    (0.30, 0.20, 0.90, 0.20),
    (1.00, 0.40, 1.20, 0.30),
  ],
  ids=["default-strength-nominal-delay", "maximum-strength-long-delay"],
)
def test_synthetic_delayed_bicycle_loop_is_bounded(
  strength, delay_s, max_excursion, max_final_error,
):
  """This deliberately synthetic stability screen is not evidence of on-road safety."""
  positions, commands = _simulate_straight_lane(strength=strength, delay_s=delay_s)

  assert np.isfinite(positions).all()
  assert np.isfinite(commands).all()
  assert np.max(np.abs(commands)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert np.max(np.abs(positions)) < max_excursion
  assert abs(positions[-1]) < max_final_error


_VALIDATED_DELAY_GRID = [
  (speed, delay_s, strength, initial_offset)
  for speed in (12.0, 20.0, 30.0, 40.0)
  for delay_s in (0.10, 0.20, 0.30, 0.40)
  for strength in (0.30, 0.50, 0.70, 1.00)
  for initial_offset in (-0.60, 0.60)
]


@pytest.mark.parametrize(
  ("speed", "delay_s", "strength", "initial_offset"),
  _VALIDATED_DELAY_GRID,
  ids=lambda value: f"{value:g}",
)
def test_synthetic_validated_delay_grid_is_bounded(speed, delay_s, strength, initial_offset):
  """Exercise the complete intended envelope with exact published action timing."""
  positions, commands = _simulate_straight_lane(
    speed=speed,
    delay_s=delay_s,
    strength=strength,
    initial_offset=initial_offset,
  )
  max_excursion = float(np.max(np.abs(positions)))
  final_error = float(abs(positions[-1]))

  assert np.isfinite(positions).all()
  assert np.isfinite(commands).all()
  assert np.max(np.abs(commands)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert max_excursion < 1.20, f"max excursion {max_excursion:.6f} m"
  assert final_error < 0.30, f"final error {final_error:.6f} m"


_SIXTY_SECOND_SUPPORTED_GRID = [
  (40.0, delay_s, strength, initial_offset)
  for delay_s in (0.10, 0.20, 0.30, 0.40)
  for strength in (0.30, 0.50, 0.70, 1.00)
  for initial_offset in (-0.60, 0.60)
] + [
  (speed, 0.40, 1.00, initial_offset)
  for speed in (12.0, 25.0)
  for initial_offset in (-0.60, 0.60)
]


@pytest.mark.parametrize(
  ("speed", "delay_s", "strength", "initial_offset"),
  _SIXTY_SECOND_SUPPORTED_GRID,
  ids=lambda value: f"{value:g}",
)
def test_supported_delay_grid_remains_bounded_for_sixty_seconds(speed, delay_s, strength, initial_offset):
  positions, commands = _simulate_straight_lane(
    speed=speed,
    delay_s=delay_s,
    strength=strength,
    initial_offset=initial_offset,
    duration_s=60.0,
  )

  assert np.isfinite(positions).all()
  assert np.isfinite(commands).all()
  assert np.max(np.abs(commands)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert np.max(np.abs(positions)) < 1.20
  assert np.max(np.abs(positions[-1000:])) < 0.30


_RUN_HALF_SECOND_SOAK = os.getenv("RUN_LANE_CENTER_HALF_SECOND_SOAK") == "1"
@pytest.mark.skipif(
  not _RUN_HALF_SECOND_SOAK,
  reason="opt-in half-second soak intentionally exceeds the supported action-time gate",
)
@pytest.mark.parametrize("initial_offset", [-0.60, 0.60], ids=["left", "right"])
def test_exploratory_half_second_soak_retains_strict_bounds(monkeypatch, initial_offset):
  """Retain the known failing criterion outside the 0.475 s production gate."""
  monkeypatch.setattr(lane_centering, "_MAX_ACTION_TIME", np.inf)
  positions, commands = _simulate_straight_lane(
    speed=40.0,
    delay_s=0.50,
    strength=1.00,
    initial_offset=initial_offset,
    duration_s=60.0,
  )
  max_excursion = float(np.max(np.abs(positions)))
  final_tail_peak = float(np.max(np.abs(positions[-1000:])))

  assert np.isfinite(positions).all()
  assert np.isfinite(commands).all()
  assert np.max(np.abs(commands)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert max_excursion < 1.20, f"max excursion {max_excursion:.6f} m"
  assert final_tail_peak < 0.30, f"last-10-second peak {final_tail_peak:.6f} m"
