from __future__ import annotations

import ast
from collections import deque
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest


CONTROLS_DIR = Path(__file__).resolve().parents[1]
LANE_CENTERING_PATH = CONTROLS_DIR / "lib" / "lane_centering.py"
DRIVE_HELPERS_PATH = CONTROLS_DIR / "lib" / "drive_helpers.py"


def _load_smooth_value():
  """Compile the production helper without importing the rest of openpilot."""
  tree = ast.parse(DRIVE_HELPERS_PATH.read_text(encoding="utf-8"), filename=str(DRIVE_HELPERS_PATH))
  function = next(
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "smooth_value"
  )
  namespace = {"np": np, "DT_MDL": 0.05}
  module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
  exec(compile(module, str(DRIVE_HELPERS_PATH), "exec"), namespace)
  return namespace["smooth_value"]


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
    smooth_value=_load_smooth_value(),
  )
  executable = ast.fix_missing_locations(ast.Module(body=kept_nodes, type_ignores=tree.type_ignores))
  exec(compile(executable, str(LANE_CENTERING_PATH), "exec"), module.__dict__)
  return module


lane_centering = _load_lane_centering()


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
           lane_change_state=0) -> SimpleNamespace:
  x = np.linspace(0.0, 70.0, 141) if x is None else np.asarray(x, dtype=float)
  center_y = _values(center, x)
  width_y = _values(width, x)
  position = _line(x, model_path)
  if y_std is not None:
    position.yStd = _values(y_std, x)
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
  }
  arguments.update(overrides)
  return controller.update(**arguments)


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
  lookahead = 25.0
  x = np.linspace(0.0, 70.0, 701)
  interior_hump = lambda distance: 0.45 * np.sin(np.pi * distance / lookahead)
  model = _model(x=x, center=interior_hump, model_path=0.0)
  controller = lane_centering.LaneCenteringController()

  valid, correction = controller._raw_correction(model, lookahead, 0.0, 0.0)

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
    _insufficient_path_coverage,
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


@pytest.mark.parametrize("correction_sign", [-1.0, 1.0])
def test_final_correction_never_exceeds_cap(correction_sign):
  model = _model(model_path=-20.0 * correction_sign)
  controller = lane_centering.LaneCenteringController()
  outputs = []

  for frame in range(1, 501):
    outputs.append(_update(controller, model, model_frame=frame * 50_000_000))
    assert abs(controller.diagnostics.target_correction_curvature) <= lane_centering._MAX_FINAL_CORRECTION

  assert controller.diagnostics.target_correction_curvature == pytest.approx(
    correction_sign * lane_centering._MAX_FINAL_CORRECTION,
  )
  assert np.max(np.abs(outputs)) <= lane_centering._MAX_FINAL_CORRECTION + 1e-15
  assert outputs[-1] == pytest.approx(correction_sign * lane_centering._MAX_FINAL_CORRECTION, rel=1e-5)


def _simulate_straight_lane(*, strength: float, delay_s: float, duration_s: float = 12.0):
  """Synthetic linear bicycle loop; useful as a numerical guard, not road validation."""
  dt = 0.01
  speed = 25.0
  lateral_position = 0.60
  heading = 0.0
  delayed_curvatures = deque([0.0] * max(1, round(delay_s / dt)))
  controller = lane_centering.LaneCenteringController()
  frame = 0
  model = None
  positions = []
  commands = []

  for step in range(round(duration_s / dt)):
    if step % 5 == 0:
      frame += 50_000_000
      sampled_position = lateral_position
      sampled_heading = heading
      model = _model(model_path=lambda x: sampled_position + sampled_heading * x)

    command = _update(
      controller, model, strength=strength, model_frame=frame,
      e2e_authority=0.0,
    )
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
