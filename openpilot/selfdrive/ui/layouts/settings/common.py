from openpilot.selfdrive.ui.ui_state import ui_state

# preset choices for the lane centering developer settings on the mici menu
LANE_CENTER_OFFSET_VALUES = (-0.2, -0.1, 0.0, 0.1, 0.2)
LANE_CENTER_OFFSET_LABELS = ("-0.2m", "-0.1m", "0m", "+0.1m", "+0.2m")
LANE_CENTERING_E2E_AUTHORITY_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0)
LANE_CENTERING_E2E_AUTHORITY_LABELS = ("0%", "25%", "50%", "75%", "100%")
LANE_CENTERING_STRENGTH_VALUES = (0.0, 0.15, 0.3, 0.5, 1.0)
LANE_CENTERING_STRENGTH_LABELS = ("0%", "15%", "30%", "50%", "100%")
LANE_CENTERING_MIN_SPEED_VALUES = (12, 25, 35, 45, 50, 55, 65, 80, 100)
LANE_CENTERING_MIN_SPEED_LABELS = tuple(f"{speed}mph" for speed in LANE_CENTERING_MIN_SPEED_VALUES)


def closest_value_index(values, value) -> int:
  return min(range(len(values)), key=lambda i: abs(values[i] - float(value)))


def restart_needed_callback(_=None):
  ui_state.params.put_bool("OnroadCycleRequested", True)
