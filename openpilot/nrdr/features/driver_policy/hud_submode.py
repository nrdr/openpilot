import time


SUBMODE_WINDOW_DEFAULT_S = 15.0
SUBMODE_WINDOW_MIN_S = 5.0
SUBMODE_WINDOW_MAX_S = 60.0


def _window_duration(params) -> float:
  try:
    duration = float(params.get("NrdrCruiseButtonSubModeSecs") or SUBMODE_WINDOW_DEFAULT_S)
  except (TypeError, ValueError):
    duration = SUBMODE_WINDOW_DEFAULT_S
  return min(max(duration, SUBMODE_WINDOW_MIN_S), SUBMODE_WINDOW_MAX_S)


def consume_button_press(params) -> bool:
  try:
    if not params.get_bool("NrdrCruiseButtonSubMode"):
      return True
    now = time.monotonic()
    try:
      deadline = float(params.get("NrdrHudSubModeUntil") or 0.0)
    except (TypeError, ValueError):
      deadline = 0.0
    params.put("NrdrHudSubModeUntil", now + _window_duration(params))
    return deadline > now
  except Exception:
    return True
