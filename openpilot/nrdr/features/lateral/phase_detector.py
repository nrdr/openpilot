PHASE_SWITCH_MIN_SPEED = 0.5 * 0.44704


def phase_with_latch(angle: float, angle_delta: float, v_ego: float, direction: float) -> tuple[float, float]:
  phase = angle * angle_delta
  if phase != 0.0 and (v_ego > PHASE_SWITCH_MIN_SPEED or direction == 0.0):
    direction = 1.0 if phase > 0.0 else -1.0
  return abs(phase) * direction, direction
