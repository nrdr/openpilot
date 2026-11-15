"""Clean-only timing baseline; review against upstream when updating monitoring.

Source: commaai/openpilot 35e78a9d9518855ec0dacec919e719624a28131f,
openpilot/selfdrive/monitoring/policy.py (DRIVER_MONITOR_SETTINGS).
"""


def monitoring_customization_available() -> bool:
  return False


def validate_reminder_percent(value) -> None:
  return None


def apply_driver_monitoring_policy(settings, reminder_percent=None) -> None:
  from openpilot.common.realtime import DT_DMON

  # Applied after initialization so development timing edits cannot leak into clean.
  # Saved reminder preferences are deliberately neither read nor changed.
  settings._WHEELTOUCH_POLICY_ALERT_1_TIMEOUT = 5.
  settings._WHEELTOUCH_POLICY_ALERT_2_TIMEOUT = 15.
  settings._WHEELTOUCH_POLICY_ALERT_3_TIMEOUT = 25.
  settings._VISION_POLICY_ALERT_1_TIMEOUT = 5.
  settings._VISION_POLICY_ALERT_2_TIMEOUT = 8.
  settings._VISION_POLICY_ALERT_3_TIMEOUT = 13.
  settings._NO_RESPONSE_TIMEOUT = 5.
  settings._MAX_ALERT_3 = 2
  settings._MAX_NO_RESPONSE = 1
  settings._LOCKOUT_TIMES = [int(60 * n_min / DT_DMON) for n_min in [1, 5, 15, 30]]
  settings._TIMEOUT_RECOVERY_FACTOR_MAX = 5.
  settings._TIMEOUT_RECOVERY_FACTOR_MIN = 1.25
  settings._DCAM_UNCERTAIN_ALERT_COUNT = int(60 / DT_DMON)
  settings._DCAM_UNCERTAIN_RESET_COUNT = int(2 / DT_DMON)
  settings._HI_STD_FALLBACK_TIME = int(10 / DT_DMON)
  settings._DISTRACTED_FILTER_TS = 0.25
  settings._POSE_OFFSET_MIN_COUNT = int(60 / DT_DMON)
  settings._POSE_OFFSET_MAX_COUNT = int(360 / DT_DMON)
  settings._WHEELPOS_FILTER_MIN_COUNT = int(15 / DT_DMON)
