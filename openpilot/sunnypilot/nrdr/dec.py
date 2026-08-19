def enforce_mode_dwell(manager, requested_mode) -> bool:
  override_holds = manager.emergency_override and requested_mode == manager.current_mode
  return manager.mode_duration < manager.min_mode_duration and not override_holds


def slow_down_threshold(base: float, active: bool, enter_scale: float, exit_scale: float) -> float:
  return base * (exit_scale if active else enter_scale)
