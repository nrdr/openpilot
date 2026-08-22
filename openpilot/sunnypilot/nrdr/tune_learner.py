#!/usr/bin/env python3
import numpy as np

from openpilot.common.params import Params
from openpilot.sunnypilot.nrdr.live_params import get_live_params
from openpilot.sunnypilot.nrdr.params import read_float


MS_TO_MPH = 2.23694
SPEED_MAX_MPH = 85.0
SPEED_BIN_MPH = 5.0
ANGLE_MAX_DEG = 500.0
ANGLE_BIN_DEG = 20.0
N_SPEED = int(SPEED_MAX_MPH / SPEED_BIN_MPH)
N_ANGLE = int(ANGLE_MAX_DEG / ANGLE_BIN_DEG)

MIN_ABS_DES = 1.0
TRIM_HARD_FRAC = 1.0
LEARN_RATE_REF = 2.0e-5
LEARN_MIN_SPEED_MS = 5.0 / MS_TO_MPH
RATE_GATE_DEG_S = 25.0
ERR_REJECT_DEG = 30.0
ERROR_GATE_FULL_DEG = 2.0
SAVE_FRAMES = 3000


def _clip(value: float, low: float, high: float) -> float:
  return min(max(value, low), high)


class TuneLearner:
  def __init__(self, dt: float, steer_max: float, settings=None):
    self.steer_max = float(steer_max) if steer_max else 1.0
    self.params = Params()
    self.settings = settings if settings is not None else get_live_params()
    self.settings_generation = -1
    self.left_map = np.zeros((N_SPEED, N_ANGLE), dtype=np.float32)
    self.right_map = np.zeros((N_SPEED, N_ANGLE), dtype=np.float32)
    self.enabled = False
    self.reset_consumed = False
    self.max_trim = 0.10 * self.steer_max
    self.rate = 0.30
    self.dirty = False
    self._load()
    self._refresh_params()

  def _grid_position(self, v_ego: float, abs_desired: float):
    speed_position = _clip((v_ego * MS_TO_MPH) / SPEED_BIN_MPH - 0.5, 0.0, N_SPEED - 1.0)
    angle_position = _clip(abs_desired / ANGLE_BIN_DEG - 0.5, 0.0, N_ANGLE - 1.0)
    speed_low = int(speed_position)
    angle_low = int(angle_position)
    return (
      speed_low,
      min(speed_low + 1, N_SPEED - 1),
      angle_low,
      min(angle_low + 1, N_ANGLE - 1),
      speed_position - speed_low,
      angle_position - angle_low,
    )

  def _interpolate(self, trim_map, v_ego: float, abs_desired: float) -> float:
    speed_low, speed_high, angle_low, angle_high, speed_weight, angle_weight = \
      self._grid_position(v_ego, abs_desired)
    return float(
      trim_map[speed_low, angle_low] * (1.0 - speed_weight) * (1.0 - angle_weight)
      + trim_map[speed_high, angle_low] * speed_weight * (1.0 - angle_weight)
      + trim_map[speed_low, angle_high] * (1.0 - speed_weight) * angle_weight
      + trim_map[speed_high, angle_high] * speed_weight * angle_weight
    )

  def _accumulate(self, trim_map, v_ego: float, abs_desired: float, delta: float) -> None:
    hard_limit = TRIM_HARD_FRAC * self.steer_max
    speed_low, speed_high, angle_low, angle_high, speed_weight, angle_weight = \
      self._grid_position(v_ego, abs_desired)
    cells = (
      (speed_low, angle_low, (1.0 - speed_weight) * (1.0 - angle_weight)),
      (speed_high, angle_low, speed_weight * (1.0 - angle_weight)),
      (speed_low, angle_high, (1.0 - speed_weight) * angle_weight),
      (speed_high, angle_high, speed_weight * angle_weight),
    )
    for speed, angle, weight in cells:
      trim_map[speed, angle] = _clip(float(trim_map[speed, angle]) + delta * weight, -hard_limit, hard_limit)

  def apply(self, v_ego: float, desired_deg: float, error_deg: float) -> float:
    if not self.enabled or abs(desired_deg) < MIN_ABS_DES:
      return 0.0

    trim_map = self.left_map if desired_deg > 0.0 else self.right_map
    trim = _clip(self._interpolate(trim_map, v_ego, abs(desired_deg)), -self.max_trim, self.max_trim)
    normalized_error = error_deg if desired_deg > 0.0 else -error_deg
    authority = _clip(normalized_error / ERROR_GATE_FULL_DEG, -1.0, 1.0)
    if trim * authority <= 0.0:
      return 0.0
    output = trim * abs(authority)
    return output if desired_deg > 0.0 else -output

  def learn(self, v_ego: float, desired_deg: float, error: float, steering_rate_deg: float,
            steering_pressed: bool, paramsd_ok: bool, frame: int) -> None:
    if self.settings_generation != self.settings.generation:
      self._refresh_params()
    if self.dirty and self.enabled and frame % SAVE_FRAMES == 0:
      self._save()
    if not self.enabled:
      return

    abs_desired = abs(desired_deg)
    invalid = (
      steering_pressed
      or not paramsd_ok
      or abs_desired < MIN_ABS_DES
      or v_ego < LEARN_MIN_SPEED_MS
      or abs(steering_rate_deg) > RATE_GATE_DEG_S
      or abs(error) > ERR_REJECT_DEG
    )
    if invalid:
      return

    normalized_error = error if desired_deg > 0.0 else -error
    trim_map = self.left_map if desired_deg > 0.0 else self.right_map
    self._accumulate(trim_map, v_ego, abs_desired, self.rate * LEARN_RATE_REF * normalized_error)
    self.dirty = True

  def _refresh_params(self) -> None:
    snapshot = self.settings.snapshot
    self.enabled = snapshot.get_bool("NrdrTuneLearner")
    strength = read_float(snapshot, "NrdrTuneLearnerStrength", 0.10, 0.0, TRIM_HARD_FRAC, scale=100.0)
    self.max_trim = strength * self.steer_max
    self.rate = read_float(snapshot, "NrdrTuneLearnerRate", 0.30, 0.0, 1.0, scale=100.0)
    reset_requested = snapshot.get_bool("NrdrTuneLearnerReset")
    if not reset_requested:
      self.reset_consumed = False
    elif not self.reset_consumed:
      self.left_map.fill(0.0)
      self.right_map.fill(0.0)
      self.dirty = True
      self._save()
      self.settings.put_async("NrdrTuneLearnerReset", False, is_bool=True)
      self.reset_consumed = True
    self.settings_generation = snapshot.generation

  def _load(self) -> None:
    raw = self.params.get("NrdrTuneLearnerMap")
    cell_count = N_SPEED * N_ANGLE
    if not raw or len(raw) != 2 * cell_count * 4:
      return
    values = np.frombuffer(raw, dtype=np.float32)
    self.left_map = values[:cell_count].reshape(N_SPEED, N_ANGLE).copy()
    self.right_map = values[cell_count:].reshape(N_SPEED, N_ANGLE).copy()

  def _save(self) -> None:
    values = np.concatenate((self.left_map.ravel(), self.right_map.ravel())).astype(np.float32)
    self.settings.put_async("NrdrTuneLearnerMap", values.tobytes())
    self.dirty = False
