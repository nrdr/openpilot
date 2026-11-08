"""Startup-only MVL PCM deadzone choices, in hundredths of m/s²."""

MVL_PCM_DEADZONE_VALUES = (0, 2, 5, 10)
MVL_PCM_DEADZONE_LABELS = ("Off", "0.02", "0.05", "0.10")
MVL_PCM_DEADZONE_TITLE = "PCM Feedback Deadzone (Experimental)"
MVL_PCM_DEADZONE_DESCRIPTION = (
  "Filters small acceleration errors only while MVL controls Civic PCM. Ignored during Civic Experimental shaping. " +
  "Editable while parked even with MVL off. Off keeps MVL unchanged. Applies next drive; no device reboot."
)
MVL_PCM_DEADZONE_DETAILS = (
  "Width (m/s²) ramps from 0 at 2.3 m/s to the selected maximum at 9 m/s. " +
  "Bypasses requested deceleration, stopping, overrides and AEB. This filters acceleration error, not a throttle ramp or delay model. " +
  "It may hold existing integral correction longer. Learning can change; Off does not undo saved learning."
)


def decode_mvl_pcm_deadzone(value) -> int | None:
  """Accept only enum integers or their canonical storage/wire encodings."""
  if type(value) is bytes:
    try:
      value = value.decode("ascii")
    except UnicodeDecodeError:
      return None
  if type(value) is str:
    return {"0": 0, "2": 2, "5": 5, "10": 10}.get(value)
  return value if type(value) is int and value in MVL_PCM_DEADZONE_VALUES else None
