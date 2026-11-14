import math

import numpy as np

CONTROL_DT = 0.01
HARD_HOLD_FLOOR = -1.0
ACCELERATION_DUE_TO_GRAVITY = 9.81


def compute_stopping_accel(last_output_accel, stop_accel, stopping_decel_rate,
                           v_ego, v_ego_stopping, hold_accel, phase_switch_v,
                           proximity_scale_m, pitch_margin, drel_filtered, pitch):
  if not math.isfinite(last_output_accel):
    last_output_accel = 0.0

  if not math.isfinite(v_ego) or v_ego > v_ego_stopping:
    if last_output_accel > stop_accel:
      return min(last_output_accel, 0.0) - stopping_decel_rate * CONTROL_DT
    return last_output_accel

  speed_scale = float(np.interp(
    max(v_ego, 0.0),
    [0.0, 0.3, max(0.3 + 1e-6, v_ego_stopping)],
    [0.3, 0.7, 1.0],
  ))
  proximity_scale = 1.0
  if math.isfinite(drel_filtered) and proximity_scale_m > 0.0:
    proximity_scale = min(1.0, max(drel_filtered, 0.0) / proximity_scale_m)

  target = hold_accel
  if v_ego <= phase_switch_v:
    pitch_accel = -ACCELERATION_DUE_TO_GRAVITY * math.sin(pitch) * pitch_margin if math.isfinite(pitch) else 0.0
    target = max(min(hold_accel + pitch_accel, HARD_HOLD_FLOOR), stop_accel)

  if last_output_accel <= target:
    return last_output_accel
  rate = stopping_decel_rate * speed_scale * proximity_scale
  return max(target, min(last_output_accel, 0.0) - rate * CONTROL_DT)
