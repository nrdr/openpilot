"""
nrdr Dynamic HUD (Distance Button Sub-Mode) shared press gate.

When NrdrDistanceButtonSubMode is ON, the first distance / set / resume press only
wakes an invisible 15-second HUD sub-mode (the cluster shows the current personality
on the distance bars and, if engaged, the set speed - all blinking). Only presses
made while the sub-mode window is already open perform their normal action, and each
press refreshes the window. The window deadline is shared with the Honda
carcontroller (which renders the blink) through the NrdrHudSubModeUntil param,
stored as a time.monotonic() deadline (CLEAR_ON_MANAGER_START, so reboots reset it).
"""
import time

SUBMODE_WINDOW_S = 15.0


def consume_button_press(params) -> bool:
  """Gate a distance / set / resume button press through the HUD sub-mode.

  Returns True if the press should perform its normal action (sub-mode disabled, or
  the window was already open). Always refreshes/opens the window on every press.
  Best-effort: any params problem (e.g. key missing on a build without a params
  rebuild) falls back to stock behavior instead of swallowing the press.
  """
  try:
    if not params.get_bool("NrdrDistanceButtonSubMode"):
      return True
    now = time.monotonic()
    try:
      until = float(params.get("NrdrHudSubModeUntil") or 0.0)
    except (TypeError, ValueError):
      until = 0.0
    params.put_nonblocking("NrdrHudSubModeUntil", now + SUBMODE_WINDOW_S)
    return until > now
  except Exception:
    return True
