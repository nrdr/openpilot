"""Experimental Civic PCM speed-setpoint deadband, in m/s (not acceleration)."""
import math

PCM_SPEED_DEADZONE_KEY = "NrdrPcmSpeedDeadzone"
PCM_SPEED_DEADZONE_DEFAULT = 0.15
PCM_SPEED_DEADZONE_TITLE = "PCM Speed-Error Deadzone"
PCM_SPEED_DEADZONE_DESCRIPTION = (
  "Deadbands the Experimental Civic PCM speed-target error, not acceleration feedback. " +
  "0 = Off; default 0.15 m/s. Editable while parked, even with Experimental off. Applies next drive; no device reboot."
)
PCM_SPEED_DEADZONE_DETAILS = (
  "Width ramps from zero at 0 m/s to the selected maximum at 9 m/s (about 20 mph). " +
  "Inside the band, PCM requests current speed, not zero. Outside it, the width is subtracted from the error. " +
  "Launch, friction-brake requests, stopping and override/AEB releases are not delayed. " +
  "Speed-gain and ceiling learning pause while the deadband changes the target. " +
  "This is not the old speed-error PID or an overspeed allowance."
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
