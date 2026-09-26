from enum import StrEnum

import numpy as np

from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_CTRL, DT_MDL
from openpilot.selfdrive.controls.lib.drive_helpers import smooth_value


_MIN_V_EGO = 5.0
LANE_CENTERING_MIN_SPEED_DEFAULT_MPH = 50
LANE_CENTERING_MIN_SPEED_MIN_MPH = 12
LANE_CENTERING_MIN_SPEED_MAX_MPH = 100
LANE_CENTERING_SPEED_HYSTERESIS_MPH = 3
_MIN_LANE_PROB = 0.6
_LANE_PROB_REARM = 0.65
_FULL_LANE_PROB = 0.8
_MAX_LANE_STD = 0.3
_MIN_LANE_WIDTH = 2.6
_MAX_LANE_WIDTH = 4.8
_MAX_OFFSET = 0.3
_MIN_CENTER_TO_LINE = 1.1
_MAX_RAW_CORRECTION = 0.004
_MAX_GAIN = 0.30
_MAX_FINAL_CORRECTION = _MAX_RAW_CORRECTION * _MAX_GAIN
_SIGNAL_RELEASE_TAU = 0.20
_CONFIDENCE_RELEASE_TAU = 0.20
_SPEED_RELEASE_TAU = 0.20
_CENTER_ERROR_DEADBAND = 0.08
_PATH_SAMPLE_COUNT = 17
_LANE_WIDTH_TAU = 3.0
_POST_ACTION_PREVIEW = 1.5
_MIN_POST_ACTION_PREVIEW = 1.0
_ACTION_PREVIEW_DELAY_SCALE = 3.0
_PREVIEW_TIME_EPSILON = 1e-6
_PREVIEW_START = 0.25
# Finite envelope exercised by the synthetic long-duration delay suite; this
# is a numerical development guard, not evidence of vehicle-level stability.
_MAX_ACTION_TIME = 0.875

_E2E_MAX_PATH_STD = 0.35
_E2E_BREAK_IN_START = 0.15
_E2E_BREAK_IN_FULL = 0.50

LANE_CENTERING_STRENGTH_DEFAULT = _MAX_GAIN
LANE_CENTERING_STRENGTH_MIN = 0.0
LANE_CENTERING_STRENGTH_MAX = 1.0


class LaneCenteringReason(StrEnum):
  """Stable, passive explanation of the lane-centering controller state."""

  UNAVAILABLE = "unavailable"
  DISABLED = "disabled"
  LATERAL_INACTIVE = "lateralInactive"
  INVALID_INPUT = "invalidInput"
  MODEL_INVALID = "modelInvalid"
  DRIVER_OVERRIDE = "driverOverride"
  LANE_CHANGE = "laneChange"
  BELOW_SPEED = "belowSpeed"
  TURN_SIGNAL_FADE = "turnSignalFade"
  LANE_DATA_INVALID = "laneDataInvalid"
  LANE_CONFIDENCE_LOW = "laneConfidenceLow"
  LANE_GEOMETRY_INVALID = "laneGeometryInvalid"
  CENTERED = "centered"
  MODEL_AUTHORITY = "modelAuthority"
  CORRECTING = "correcting"
  ZERO_STRENGTH = "zeroStrength"
  TIMING_UNAVAILABLE = "timingUnavailable"
  PREVIEW_TOO_SHORT = "previewTooShort"


class LaneCenteringDiagnostics:
  """Mutable observability snapshot; none of these fields feed control output."""

  __slots__ = (
    "reason", "speed_armed", "active", "correction_curvature", "target_correction_curvature",
    "center_error", "effective_center_error", "lane_width", "lookahead", "min_lane_probability", "max_lane_std",
  )

  def __init__(self) -> None:
    self.reset()

  def reset(self) -> None:
    self.reason = LaneCenteringReason.UNAVAILABLE
    self.speed_armed = False
    self.active = False
    self.correction_curvature = 0.0
    self.target_correction_curvature = 0.0
    self.center_error = 0.0
    self.effective_center_error = 0.0
    self.lane_width = 0.0
    self.lookahead = 0.0
    self.min_lane_probability = 0.0
    self.max_lane_std = 0.0


def lane_centering_min_speed_mph(value) -> float:
  """Return the valid canonical-mph lane-centering arm speed, failing closed to 50 mph."""
  try:
    speed_mph = float(value)
  except (OverflowError, TypeError, ValueError):
    return float(LANE_CENTERING_MIN_SPEED_DEFAULT_MPH)
  if (not np.isfinite(speed_mph) or not speed_mph.is_integer()
      or not LANE_CENTERING_MIN_SPEED_MIN_MPH <= speed_mph <= LANE_CENTERING_MIN_SPEED_MAX_MPH):
    return float(LANE_CENTERING_MIN_SPEED_DEFAULT_MPH)
  return speed_mph


def lane_centering_speed_thresholds(value) -> tuple[float, float]:
  arm_mph = lane_centering_min_speed_mph(value)
  arm_speed = max(_MIN_V_EGO, arm_mph * CV.MPH_TO_MS)
  release_speed = max(_MIN_V_EGO, (arm_mph - LANE_CENTERING_SPEED_HYSTERESIS_MPH) * CV.MPH_TO_MS)
  return arm_speed, release_speed


def lane_centering_strength(value) -> float:
  """Return a bounded direct lane-centering strength, failing closed to the legacy 30% gain."""
  try:
    strength = float(value)
  except (OverflowError, TypeError, ValueError):
    return float(LANE_CENTERING_STRENGTH_DEFAULT)
  if not np.isfinite(strength) or not LANE_CENTERING_STRENGTH_MIN <= strength <= LANE_CENTERING_STRENGTH_MAX:
    return float(LANE_CENTERING_STRENGTH_DEFAULT)
  return strength


def lane_centering_action_time(model_v2) -> float | None:
  """Read timing atomically with the action; model validity is checked by the caller."""
  try:
    action_time = float(model_v2.action.lateralActionTime)
    if not np.isfinite(action_time) or not 0.0 < action_time <= _MAX_ACTION_TIME + 1e-6:
      return None
    return action_time
  except (AttributeError, OverflowError, TypeError, ValueError):
    return None


class LaneCenteringController:
  def __init__(self) -> None:
    self._correction = 0.0
    self._speed_armed = False
    self._lanes_armed = False
    self._lane_width_estimate = None
    self._path_cache_key = None
    self._path_cache = (False, 0.0)
    self._last_model_frame = None
    self.diagnostics = LaneCenteringDiagnostics()

  def reset(self) -> None:
    self._correction = 0.0
    self._speed_armed = False
    self._lanes_armed = False
    self._lane_width_estimate = None
    self._path_cache_key = None
    self._path_cache = (False, 0.0)
    self._last_model_frame = None
    self.diagnostics.reset()

  def _begin_diagnostics(self) -> None:
    self.diagnostics.reset()
    self.diagnostics.correction_curvature = self._correction
    self.diagnostics.speed_armed = self._speed_armed

  def _finish_diagnostics(self, reason: LaneCenteringReason | None = None, *, target: float = 0.0,
                          active: bool = False) -> None:
    if reason is not None:
      self.diagnostics.reason = reason
    self.diagnostics.speed_armed = self._speed_armed
    self.diagnostics.active = active
    self.diagnostics.correction_curvature = self._correction
    self.diagnostics.target_correction_curvature = target

  def update(self, model_curvature, model_v2, v_ego, min_speed_mph, enabled, offset, e2e_authority, strength, lat_active, model_valid,
             pause_on_signal=False, turn_signal_active=False, driver_override=False, model_frame=None, action_time=None) -> float:
    model_curvature = float(model_curvature)
    self._begin_diagnostics()

    try:
      v_ego = float(v_ego)
      offset = float(offset)
      e2e_authority = float(e2e_authority)
      strength = float(strength)
    except (OverflowError, TypeError, ValueError):
      self.reset()
      self._finish_diagnostics(LaneCenteringReason.INVALID_INPUT)
      return model_curvature

    if (not np.isfinite([v_ego, offset, e2e_authority, strength]).all()
        or not LANE_CENTERING_STRENGTH_MIN <= strength <= LANE_CENTERING_STRENGTH_MAX):
      self.reset()
      self._finish_diagnostics(LaneCenteringReason.INVALID_INPUT)
      return model_curvature

    if not model_valid or not enabled or not lat_active or v_ego < _MIN_V_EGO:
      reason = (LaneCenteringReason.DISABLED if not enabled else
                LaneCenteringReason.LATERAL_INACTIVE if not lat_active else
                LaneCenteringReason.MODEL_INVALID if not model_valid else
                LaneCenteringReason.BELOW_SPEED)
      self.reset()
      self._finish_diagnostics(reason)
      return model_curvature

    if driver_override:
      self.reset()
      self._finish_diagnostics(LaneCenteringReason.DRIVER_OVERRIDE)
      return model_curvature

    if strength == 0.0:
      # Explicit model-only mode must not retain a residual lane correction,
      # even while timing, confidence, or signal gates are unavailable.
      self.reset()
      self._finish_diagnostics(LaneCenteringReason.ZERO_STRENGTH)
      return model_curvature

    try:
      if model_v2.meta.laneChangeState != log.LaneChangeState.off:
        self.reset()
        self._finish_diagnostics(LaneCenteringReason.LANE_CHANGE)
        return model_curvature
    except (AttributeError, TypeError, ValueError):
      self.reset()
      self._finish_diagnostics(LaneCenteringReason.LANE_DATA_INVALID)
      return model_curvature

    arm_speed, release_speed = lane_centering_speed_thresholds(min_speed_mph)
    if self._speed_armed and v_ego < release_speed:
      self._speed_armed = False
    if not self._speed_armed:
      if v_ego >= arm_speed:
        self._speed_armed = True
      else:
        self._correction = float(smooth_value(0.0, self._correction, _SPEED_RELEASE_TAU, dt=DT_CTRL))
        self._finish_diagnostics(LaneCenteringReason.BELOW_SPEED)
        return model_curvature + self._correction

    if pause_on_signal and turn_signal_active:
      self._correction = float(smooth_value(0.0, self._correction, _SIGNAL_RELEASE_TAU, dt=DT_CTRL))
      self._finish_diagnostics(LaneCenteringReason.TURN_SIGNAL_FADE)
      return model_curvature + self._correction

    try:
      action_time = float(action_time)
      timing_valid = np.isfinite(action_time) and 0.0 < action_time <= _MAX_ACTION_TIME + 1e-6
    except (OverflowError, TypeError, ValueError):
      timing_valid = False
    if not timing_valid:
      self._lanes_armed = False
      self._lane_width_estimate = None
      self._path_cache_key = None
      self._correction = float(smooth_value(0.0, self._correction, _CONFIDENCE_RELEASE_TAU, dt=DT_CTRL))
      self._finish_diagnostics(LaneCenteringReason.TIMING_UNAVAILABLE)
      return model_curvature + self._correction

    # Freeze speed-dependent geometry for each 20 Hz model frame; only the
    # release filters and engagement/driver gates run at the 100 Hz control rate.
    cache_key = (model_frame, offset, e2e_authority, action_time)
    if model_frame is None or cache_key != self._path_cache_key:
      path_dt = DT_CTRL if model_frame is None else DT_MDL
      if model_frame is not None and self._last_model_frame is not None:
        path_dt = float(np.clip((model_frame - self._last_model_frame) * 1e-9, DT_CTRL, 0.1))
      self._path_cache = self._raw_correction(
        model_v2, v_ego, float(np.clip(offset, -_MAX_OFFSET, _MAX_OFFSET)),
        float(np.clip(e2e_authority, 0.0, 1.0)), path_dt, action_time,
      )
      self._path_cache_key = cache_key
      self._last_model_frame = model_frame
      self._path_diagnostics = {key: getattr(self.diagnostics, key) for key in (
        "reason", "center_error", "effective_center_error", "lane_width", "lookahead", "min_lane_probability", "max_lane_std",
      )}
    else:
      for key, value in self._path_diagnostics.items():
        setattr(self.diagnostics, key, value)
    valid, raw_correction = self._path_cache
    if not valid:
      self._lanes_armed = False
      self._lane_width_estimate = None
      self._correction = float(smooth_value(0.0, self._correction, _CONFIDENCE_RELEASE_TAU, dt=DT_CTRL))
      self._finish_diagnostics()
      return model_curvature + self._correction

    # Strength blends the lane-derived path with the model path. Translate the
    # full-preview path difference into a bounded change to the modern action.
    bounded_correction = float(np.clip(raw_correction, -_MAX_RAW_CORRECTION, _MAX_RAW_CORRECTION))
    target = float(np.clip(bounded_correction * strength, -_MAX_FINAL_CORRECTION, _MAX_FINAL_CORRECTION))
    # Do not add another low-pass pole to this delayed feedback loop. The
    # combined model + lane command MUST pass through controlsd.clip_curvature,
    # which limits the final physical jerk/acceleration, including model motion.
    self._correction = target
    self._finish_diagnostics(target=target, active=self.diagnostics.reason == LaneCenteringReason.CORRECTING and target != 0.0)
    return model_curvature + self._correction

  @staticmethod
  def _valid_path(x, y) -> bool:
    return bool(x.ndim == y.ndim == 1 and x.size >= 2 and x.size == y.size
                and np.isfinite(x).all() and np.isfinite(y).all() and np.all(np.diff(x) > 0))

  @staticmethod
  def _covers(x, distance: float) -> bool:
    return bool(x[0] <= distance <= x[-1])

  def _raw_correction(self, model_v2, v_ego: float, offset: float, e2e_authority: float,
                      path_dt: float = DT_CTRL, action_time: float = 0.275) -> tuple[bool, float]:
    try:
      lane_lines = model_v2.laneLines
      probs = np.asarray(model_v2.laneLineProbs, dtype=float)
      stds = np.asarray(model_v2.laneLineStds, dtype=float)
      if len(lane_lines) < 3 or probs.ndim != 1 or stds.ndim != 1 or probs.size < 3 or stds.size < 3:
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0
      if not np.isfinite(probs[[1, 2]]).all() or not np.isfinite(stds[[1, 2]]).all():
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0
      self.diagnostics.min_lane_probability = float(min(probs[1], probs[2]))
      self.diagnostics.max_lane_std = float(max(stds[1], stds[2]))
      if np.any(probs[[1, 2]] < _MIN_LANE_PROB) or np.any(probs[[1, 2]] > 1.0):
        self._lanes_armed = False
        self.diagnostics.reason = LaneCenteringReason.LANE_CONFIDENCE_LOW
        return False, 0.0
      if np.any(stds[[1, 2]] < 0.0) or np.any(stds[[1, 2]] > _MAX_LANE_STD):
        self.diagnostics.reason = LaneCenteringReason.LANE_CONFIDENCE_LOW
        self._lanes_armed = False
        return False, 0.0

      if not self._lanes_armed and min(probs[1], probs[2]) < _LANE_PROB_REARM:
        self.diagnostics.reason = LaneCenteringReason.LANE_CONFIDENCE_LOW
        return False, 0.0

      left_x = np.asarray(lane_lines[1].x, dtype=float)
      left_y = np.asarray(lane_lines[1].y, dtype=float)
      right_x = np.asarray(lane_lines[2].x, dtype=float)
      right_y = np.asarray(lane_lines[2].y, dtype=float)
      pos_x = np.asarray(model_v2.position.x, dtype=float)
      pos_y = np.asarray(model_v2.position.y, dtype=float)
      if not (self._valid_path(left_x, left_y) and self._valid_path(right_x, right_y) and self._valid_path(pos_x, pos_y)):
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0

      # Locate actuation in the same coordinate frame as the model's path.
      # Nonempty malformed timing is invalid; only absent timing uses the
      # constant-speed approximation needed by older model path formats.
      pos_t = np.asarray(getattr(model_v2.position, 't', []), dtype=float)
      common_end = min(left_x[-1], right_x[-1], pos_x[-1])
      # A fixed preview raises feedback bandwidth relative to a longer action
      # delay. Extend the same geometric fit instead of reducing the requested
      # lane-path strength: its position gain falls roughly as 1 / preview**2.
      # Require that delay-scaled horizon in the actual shared path coverage;
      # silently clipping it back to a short preview defeats the delay margin.
      delay_preview = _ACTION_PREVIEW_DELAY_SCALE * action_time
      post_action_preview = max(_POST_ACTION_PREVIEW, delay_preview)
      min_post_action_preview = max(_MIN_POST_ACTION_PREVIEW, delay_preview)
      if pos_t.size:
        if not self._valid_path(pos_t, pos_x):
          self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
          return False, 0.0
        if not self._covers(pos_t, action_time):
          self.diagnostics.reason = LaneCenteringReason.PREVIEW_TOO_SHORT
          return False, 0.0
        action_x = float(np.interp(action_time, pos_t, pos_x))
        end_time = min(action_time + post_action_preview, float(np.interp(common_end, pos_x, pos_t)))
        if end_time - action_time + _PREVIEW_TIME_EPSILON < min_post_action_preview:
          self.diagnostics.reason = LaneCenteringReason.PREVIEW_TOO_SHORT
          return False, 0.0
        path_x = np.interp(np.linspace(action_time + _PREVIEW_START, end_time, _PATH_SAMPLE_COUNT), pos_t, pos_x)
        horizon = min(common_end, float(np.interp(end_time + 0.5, pos_t, pos_x)))
      else:
        action_x = v_ego * action_time
        end_x = min(common_end, action_x + v_ego * post_action_preview)
        if end_x - action_x + v_ego * _PREVIEW_TIME_EPSILON < v_ego * min_post_action_preview:
          self.diagnostics.reason = LaneCenteringReason.PREVIEW_TOO_SHORT
          return False, 0.0
        path_x = np.linspace(action_x + v_ego * _PREVIEW_START, end_x, _PATH_SAMPLE_COUNT)
        horizon = min(common_end, end_x + 0.5 * v_ego)
      lookahead = float(path_x[-1])
      self.diagnostics.lookahead = lookahead
      corridor_start = max(0.0, left_x[0], right_x[0], pos_x[0])
      if corridor_start > path_x[0] or not all(self._covers(x, lookahead) for x in (left_x, right_x, pos_x)):
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0

      # Adapted from the multi-horizon corridor checks and confidence-weighted
      # lane path in phr00t/openpilot's oldbranch lane_planner. Keep current
      # finite/monotonic validation and never infer a lane from a missing side.
      corridor_x = np.linspace(corridor_start, horizon, _PATH_SAMPLE_COUNT)
      corridor_widths = np.interp(corridor_x, right_x, right_y) - np.interp(corridor_x, left_x, left_y)
      width = float(np.interp(lookahead, corridor_x, corridor_widths))
      self.diagnostics.lane_width = width
      if np.any(corridor_widths < _MIN_LANE_WIDTH) or np.any(corridor_widths > _MAX_LANE_WIDTH):
        self._lanes_armed = False
        self._lane_width_estimate = None
        self.diagnostics.reason = LaneCenteringReason.LANE_GEOMETRY_INVALID
        return False, 0.0

      confidence = float(np.interp(min(probs[1], probs[2]), [_MIN_LANE_PROB, _FULL_LANE_PROB], [0.0, 1.0]))
      confidence *= float(np.interp(max(stds[1], stds[2]), [0.15, _MAX_LANE_STD], [1.0, 0.0]))
      confidence *= float(np.interp(np.max(corridor_widths), [4.0, _MAX_LANE_WIDTH], [1.0, 0.0]))
      if confidence <= 0.0:
        self._lanes_armed = False
        self.diagnostics.reason = LaneCenteringReason.LANE_CONFIDENCE_LOW
        return False, 0.0
      self._lanes_armed = True

      measured_width = float(corridor_widths[0])
      if self._lane_width_estimate is None:
        self._lane_width_estimate = measured_width
      else:
        self._lane_width_estimate = float(smooth_value(measured_width, self._lane_width_estimate, _LANE_WIDTH_TAU, dt=path_dt))
      confidence *= float(np.interp(abs(measured_width - self._lane_width_estimate), [0.2, 0.8], [1.0, 0.2]))

      left = np.interp(path_x, left_x, left_y)
      right = np.interp(path_x, right_x, right_y)
      # Both boundaries remain required. Width history can soften confidence,
      # but cannot shift the midpoint or replace the current clearance checks.
      lane_path = 0.5 * (left + right)
      safe_offset = min(_MAX_OFFSET, max(0.0, float(np.min(corridor_widths)) * 0.5 - _MIN_CENTER_TO_LINE))
      lane_path += float(np.clip(offset, -safe_offset, safe_offset))
      lane_path = np.clip(lane_path, left + _MIN_CENTER_TO_LINE, right - _MIN_CENTER_TO_LINE)
      model_path = np.interp(path_x, pos_x, pos_y)
      path_errors = lane_path - model_path
      error = float(path_errors[-1])
      self.diagnostics.center_error = error
      # Fit lane-minus-model path error, not absolute camera-frame y. Shared
      # curve shape and coherent camera-frame motion then cancel exactly.
      # The correction cannot affect the path before actuation. Fit its
      # post-actuation response, rather than immediate curvature from x=0.
      basis = 0.5 * (path_x - action_x) ** 2
      fit_weights = basis ** 2
      error_abs = float(np.sqrt(np.dot(fit_weights, path_errors ** 2) / np.sum(fit_weights)))
      bounded_errors = np.sign(path_errors) * np.maximum(np.abs(path_errors) - _CENTER_ERROR_DEADBAND, 0.0)
      correction = float(np.dot(basis, bounded_errors) / np.dot(basis, basis))
      model_weight = 1.0

      try:
        pos_y_std = np.asarray(model_v2.position.yStd, dtype=float)
        if self._valid_path(pos_x, pos_y_std) and np.all(pos_y_std >= 0.0):
          path_std = float(np.max(np.interp(path_x, pos_x, pos_y_std)))
          if 0.0 <= path_std <= _E2E_MAX_PATH_STD:
            break_in = np.clip(
              (error_abs - _E2E_BREAK_IN_START) / (_E2E_BREAK_IN_FULL - _E2E_BREAK_IN_START),
              0.0,
              1.0,
            )
            model_weight = 1.0 - e2e_authority * float(break_in)
      except (AttributeError, TypeError, ValueError):
        pass

      result = float(correction * confidence * model_weight)
      if not np.isfinite([confidence, error_abs, correction, model_weight, result]).all():
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0
      self.diagnostics.effective_center_error = float(bounded_errors[-1]) * confidence * model_weight
      if abs(correction) < 1e-9:
        self.diagnostics.reason = LaneCenteringReason.CENTERED
      elif model_weight == 0.0:
        self.diagnostics.reason = LaneCenteringReason.MODEL_AUTHORITY
      else:
        self.diagnostics.reason = LaneCenteringReason.CORRECTING
      return True, result
    except (AttributeError, FloatingPointError, IndexError, OverflowError, TypeError, ValueError):
      self._lanes_armed = False
      self._lane_width_estimate = None
      self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
      return False, 0.0
