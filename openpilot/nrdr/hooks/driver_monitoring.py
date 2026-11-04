"""First-reminder timing, with upstream escalation gaps and no disable mode."""

REMINDER_PARAM = "NrdrDriverMonitoringReminderPercent"


def monitoring_customization_available() -> bool:
  # The clean release overlay replaces this module with an upstream-only no-op.
  return True


def validate_reminder_percent(value) -> int | None:
  if isinstance(value, bytes):
    try:
      value = value.decode("ascii")
    except UnicodeDecodeError:
      return None
  if isinstance(value, str):
    if not 2 <= len(value) <= 3 or not value.isascii() or not value.isdecimal():
      return None
    value = int(value)
  if type(value) is not int or not 50 <= value <= 250 or value % 5:
    return None
  return value


def apply_driver_monitoring_policy(settings, reminder_percent=None) -> None:
  """Read once at monitor startup, never reset awareness to apply a live edit.

  Shift all three elapsed-time thresholds by the change to the first reminder.
  Later warning gaps, the no-response interval, lockouts, confidence checks and
  camera-fault handling are untouched. This does not multiply each stage.
  """
  if reminder_percent is None:
    from openpilot.common.params import Params
    reminder_percent = Params().get(REMINDER_PARAM, return_default=True)
  percent = validate_reminder_percent(reminder_percent)
  scale = (100 if percent is None else percent) / 100.0

  if not hasattr(settings, "_nrdr_upstream_reminder_timeouts"):
    settings._nrdr_upstream_reminder_timeouts = {
      policy: tuple(getattr(settings, f"_{policy}_POLICY_ALERT_{level}_TIMEOUT") for level in (1, 2, 3))
      for policy in ("VISION", "WHEELTOUCH")
    }
  for policy, (first, second, final) in settings._nrdr_upstream_reminder_timeouts.items():
    # Thresholds are elapsed times on one awareness clock, not cumulative delays.
    shift = first * (scale - 1.0)
    for level, threshold in enumerate((first, second, final), start=1):
      setattr(settings, f"_{policy}_POLICY_ALERT_{level}_TIMEOUT", threshold + shift)
