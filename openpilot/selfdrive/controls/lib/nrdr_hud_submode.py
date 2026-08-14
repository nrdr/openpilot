"""August-layout openpilot package module.

nrdr Dynamic HUD (Cruise Button Sub-Mode) shared press gate.

When NrdrCruiseButtonSubMode is ON, the first distance / set / resume press only
wakes an invisible 15-second HUD sub-mode (the cluster shows the current personality
on the distance bars and, if engaged, the set speed - all blinking, faster and
faster as the window runs out). Only presses made while the sub-mode window is
already open perform their normal action, and each press refreshes the window. The
window deadline is shared with the Honda carcontroller (which renders the blink)
through the NrdrHudSubModeUntil param, stored as a time.monotonic() deadline
(CLEAR_ON_MANAGER_START, so reboots reset it).
"""
import time

SUBMODE_WINDOW_DEFAULT_S = 15.0
SUBMODE_WINDOW_MIN_S = 5.0
SUBMODE_WINDOW_MAX_S = 60.0


def _window_s(params) -> float:
  try:
    w = float(params.get("NrdrCruiseButtonSubModeSecs") or SUBMODE_WINDOW_DEFAULT_S)
  except (TypeError, ValueError):
    w = SUBMODE_WINDOW_DEFAULT_S
  return min(max(w, SUBMODE_WINDOW_MIN_S), SUBMODE_WINDOW_MAX_S)


def consume_button_press(params) -> bool:
  """Gate a distance / set / resume button press through the HUD sub-mode.

  Returns True if the press should perform its normal action (sub-mode disabled, or
  the window was already open). Always refreshes/opens the window on every press,
  using the user-set window length (NrdrCruiseButtonSubModeSecs, 5-60s).
  Best-effort: any params problem (e.g. key missing on a build without a params
  rebuild) falls back to stock behavior instead of swallowing the press.
  """
  try:
    if not params.get_bool("NrdrCruiseButtonSubMode"):
      return True
    now = time.monotonic()
    try:
      until = float(params.get("NrdrHudSubModeUntil") or 0.0)
    except (TypeError, ValueError):
      until = 0.0
    params.put("NrdrHudSubModeUntil", now + _window_s(params))
    return until > now
  except Exception:
    return True
