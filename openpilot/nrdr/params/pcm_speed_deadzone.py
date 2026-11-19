"""Experimental Civic PCM speed-setpoint deadband, in m/s (not acceleration)."""
import math

PCM_SPEED_DEADZONE_KEY = "NrdrPcmSpeedDeadzone"
PCM_SPEED_DEADZONE_DEFAULT = 0.15
PCM_SPEED_DEADZONE_TITLE = "PCM Speed-Error Deadzone"
PCM_SPEED_DEADZONE_DESCRIPTION = (
  "Reduces small speed corrections in Experimental Civic PCM control; zero disables it."
)
PCM_SPEED_DEADZONE_DETAILS = (
  "The deadzone grows from zero at standstill to your selected value at 9 m/s (about 20 mph), without delaying brake requests or stopping."
)


def decode_speed_deadzone(value) -> float | None:
  if type(value) is bytes:
    try:
      value = value.decode("ascii")
    except UnicodeDecodeError:
      return None
  if type(value) is str:
    try:
      value = float(value)
    except ValueError:
      return None
  if type(value) not in (int, float) or not math.isfinite(value) or not 0.0 <= value <= 0.20:
    return None
  # Store real units. Only hundredth-m/s slider ticks are accepted.
  tick = round(value * 100)
  return tick / 100 if math.isclose(value, tick / 100, abs_tol=1e-9, rel_tol=0.0) else None


def read_speed_deadzone(value) -> float:
  if value is None:
    return PCM_SPEED_DEADZONE_DEFAULT
  decoded = decode_speed_deadzone(value)
  return decoded if decoded is not None else 0.0
