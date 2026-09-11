from enum import StrEnum

import numpy as np

from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.drive_helpers import smooth_value


_MIN_V_EGO = 5.0
LANE_CENTERING_MIN_SPEED_DEFAULT_MPH = 50
LANE_CENTERING_MIN_SPEED_MIN_MPH = 12
LANE_CENTERING_MIN_SPEED_MAX_MPH = 100
LANE_CENTERING_SPEED_HYSTERESIS_MPH = 3
_MIN_LANE_PROB = 0.6
_MAX_LANE_STD = 0.3
_MIN_LANE_WIDTH = 2.6
_MAX_LANE_WIDTH = 4.8
_MAX_OFFSET = 0.3
_MIN_CENTER_TO_LINE = 1.1
_MAX_RAW_CORRECTION = 0.004
_MAX_GAIN = 0.30
_MAX_FINAL_CORRECTION = _MAX_RAW_CORRECTION * _MAX_GAIN
_SMOOTH_TAU = 0.4
_SIGNAL_RELEASE_TAU = 0.20
_CONFIDENCE_RELEASE_TAU = 0.20
_SPEED_RELEASE_TAU = 0.20
_CENTER_ERROR_DEADBAND = 0.08

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


class LaneCenteringController:
  def __init__(self) -> None:
    self._correction = 0.0
    self._speed_armed = False
    self.diagnostics = LaneCenteringDiagnostics()

  def reset(self) -> None:
    self._correction = 0.0
    self._speed_armed = False
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
             pause_on_signal=False, turn_signal_active=False, driver_override=False) -> float:
    model_curvature = float(model_curvature)
    self._begin_diagnostics()

    try:
      v_ego = float(v_ego)
      offset = float(offset)
      e2e_authority = float(e2e_authority)
      strength = float(strength)
    except (TypeError, ValueError):
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

    valid, raw_correction = self._raw_correction(
      model_v2,
      v_ego,
      float(np.clip(offset, -_MAX_OFFSET, _MAX_OFFSET)),
      float(np.clip(e2e_authority, 0.0, 1.0)),
    )
    if not valid:
      self._correction = float(smooth_value(0.0, self._correction, _CONFIDENCE_RELEASE_TAU, dt=DT_CTRL))
      self._finish_diagnostics()
      return model_curvature + self._correction

    bounded_raw_correction = float(np.clip(raw_correction, -_MAX_RAW_CORRECTION, _MAX_RAW_CORRECTION))
    target = float(np.clip(bounded_raw_correction * strength, -_MAX_FINAL_CORRECTION, _MAX_FINAL_CORRECTION))
    if strength == 0.0 and raw_correction != 0.0:
      self.diagnostics.reason = LaneCenteringReason.ZERO_STRENGTH
    self._correction = float(smooth_value(target, self._correction, _SMOOTH_TAU, dt=DT_CTRL))
    self._finish_diagnostics(target=target, active=self.diagnostics.reason == LaneCenteringReason.CORRECTING and target != 0.0)
    return model_curvature + self._correction

  @staticmethod
  def _valid_path(x, y) -> bool:
    return bool(x.size >= 2 and x.size == y.size and np.isfinite(x).all() and np.isfinite(y).all() and np.all(np.diff(x) > 0))

  @staticmethod
  def _covers(x, distance: float) -> bool:
    return bool(x[0] <= distance <= x[-1])

  def _raw_correction(self, model_v2, v_ego: float, offset: float, e2e_authority: float) -> tuple[bool, float]:
    try:
      lane_lines = model_v2.laneLines
      probs = np.asarray(model_v2.laneLineProbs, dtype=float)
      stds = np.asarray(model_v2.laneLineStds, dtype=float)
      if len(lane_lines) < 3 or probs.size < 3 or stds.size < 3:
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0
      if not np.isfinite(probs[[1, 2]]).all() or not np.isfinite(stds[[1, 2]]).all():
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0
      self.diagnostics.min_lane_probability = float(min(probs[1], probs[2]))
      self.diagnostics.max_lane_std = float(max(stds[1], stds[2]))
      if np.any(probs[[1, 2]] < _MIN_LANE_PROB) or np.any(probs[[1, 2]] > 1.0):
        self.diagnostics.reason = LaneCenteringReason.LANE_CONFIDENCE_LOW
        return False, 0.0
      if np.any(stds[[1, 2]] < 0.0) or np.any(stds[[1, 2]] > _MAX_LANE_STD):
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

      lookahead = float(np.clip(v_ego, 8.0, 35.0))
      self.diagnostics.lookahead = lookahead
      if not all(self._covers(x, lookahead) for x in (left_x, right_x, pos_x)):
        self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
        return False, 0.0

      left = float(np.interp(lookahead, left_x, left_y))
      right = float(np.interp(lookahead, right_x, right_y))
      width = right - left
      self.diagnostics.lane_width = width
      if not _MIN_LANE_WIDTH <= width <= _MAX_LANE_WIDTH:
        self.diagnostics.reason = LaneCenteringReason.LANE_GEOMETRY_INVALID
        return False, 0.0

      max_safe_offset = min(_MAX_OFFSET, max(0.0, width * 0.5 - _MIN_CENTER_TO_LINE))
      target_y = 0.5 * (left + right) + float(np.clip(offset, -max_safe_offset, max_safe_offset))
      model_y = float(np.interp(lookahead, pos_x, pos_y))
      error = target_y - model_y
      self.diagnostics.center_error = error
      error_abs = abs(error)
      if error_abs <= _CENTER_ERROR_DEADBAND:
        error = 0.0
      else:
        error = np.copysign(error_abs - _CENTER_ERROR_DEADBAND, error)

      try:
        pos_y_std = np.asarray(model_v2.position.yStd, dtype=float)
        if self._valid_path(pos_x, pos_y_std):
          path_std = float(np.interp(lookahead, pos_x, pos_y_std))
          if 0.0 <= path_std <= _E2E_MAX_PATH_STD:
            break_in = np.clip(
              (error_abs - _E2E_BREAK_IN_START) / (_E2E_BREAK_IN_FULL - _E2E_BREAK_IN_START),
              0.0,
              1.0,
            )
            error *= 1.0 - e2e_authority * float(break_in)
      except (AttributeError, TypeError, ValueError):
        pass

      self.diagnostics.effective_center_error = error
      if error_abs <= _CENTER_ERROR_DEADBAND:
        self.diagnostics.reason = LaneCenteringReason.CENTERED
      elif error == 0.0:
        self.diagnostics.reason = LaneCenteringReason.MODEL_AUTHORITY
      else:
        self.diagnostics.reason = LaneCenteringReason.CORRECTING
      return True, float(2.0 * error / lookahead ** 2)
    except (AttributeError, IndexError, TypeError, ValueError):
      self.diagnostics.reason = LaneCenteringReason.LANE_DATA_INVALID
      return False, 0.0
