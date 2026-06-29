"""
Compact developer UI for the C4 (mici): the right-column metrics squeezed into the 60px side
strip, under the pinned confidence ball. Reuses the standard UiElement classes and just lays them
out tiny + stacked, with abbreviated labels and no units to fit the narrow strip. Shows when
DevUIInfo selects the right column (RIGHT or BOTH). The C4 renders no full-size devUI, so this is
the only devUI it has. Sizes/offsets here are first-draft knobs -- tune on the device.
"""
import pyray as rl

from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiState
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import (
  RelDistElement, RelSpeedElement, SteeringAngleElement,
  DesiredLateralAccelElement, DesiredSteeringAngleElement, DesiredSteeringPIDElement,
  ActualLateralAccelElement,
)
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

# Long element labels -> short tags that fit ~60px. Anything unmapped falls back to its first word.
LABEL_ABBR = {
  "REAL STEER": "REAL",
  "DESIRED STEER": "DESIRED",
  "DESIRED L.A.": "DESIRED",
}


class StripDevUiRenderer(Widget):
  TOP_OFFSET = 116      # clear the pinned ball (now dropped to clear the top edge)
  ROW_SPACING = 74
  LABEL_SIZE = 17       # ~15% smaller so REAL/DESIRED + values fit the 60px strip
  VALUE_SIZE = 18       # shrunk ~30% more so a -12.3-style readout fits the 60px lane

  def __init__(self):
    super().__init__()
    self._font_bold = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold = gui_app.font(FontWeight.SEMI_BOLD)
    self.rel_dist_elem = RelDistElement()
    self.rel_speed_elem = RelSpeedElement()
    self.steering_angle_elem = SteeringAngleElement()
    self.desired_lat_accel_elem = DesiredLateralAccelElement()
    self.desired_steer_elem = DesiredSteeringAngleElement()
    self.desired_pid_steer_elem = DesiredSteeringPIDElement()
    self.actual_lat_accel_elem = ActualLateralAccelElement()

  def _render(self, _):
    if ui_state.developer_ui not in (DeveloperUiState.RIGHT, DeveloperUiState.BOTH):
      return
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    # Only two metrics fit the 60px strip for now: REAL + DESIRED steering angle. The rest are
    # parked (instances kept) until there's a user picker for which to show.
    elements = [self.steering_angle_elem.update(sm, ui_state.is_metric)]   # REAL
    which = sm['controlsState'].lateralControlState.which()
    if which == 'pidState':
      elements.append(self.desired_pid_steer_elem.update(sm, ui_state.is_metric))   # DESIRED
    elif which == 'angleState':
      elements.append(self.desired_steer_elem.update(sm, ui_state.is_metric))
    elif which == 'torqueState':
      elements.append(self.desired_lat_accel_elem.update(sm, ui_state.is_metric))

    cx = int(self._rect.x + self._rect.width - SIDE_PANEL_WIDTH / 2)
    y = int(self._rect.y + self.TOP_OFFSET)
    for el in elements:
      self._draw_element(cx, y, el)
      y += self.ROW_SPACING

  def _draw_element(self, cx: int, y: int, element) -> None:
    label = LABEL_ABBR.get(element.label, element.label.split()[0] if element.label else "")
    lw = measure_text_cached(self._font_semi_bold, label, self.LABEL_SIZE, 0).x
    rl.draw_text_ex(self._font_semi_bold, label, rl.Vector2(cx - lw / 2, y), self.LABEL_SIZE, 0,
                    rl.Color(255, 255, 255, 180))
    vw = measure_text_cached(self._font_bold, element.value, self.VALUE_SIZE, 0).x
    rl.draw_text_ex(self._font_bold, element.value, rl.Vector2(cx - vw / 2, y + self.LABEL_SIZE + 3),
                    self.VALUE_SIZE, 0, element.color)
