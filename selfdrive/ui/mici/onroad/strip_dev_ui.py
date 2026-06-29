"""
Compact developer UI for the C4 (mici): four metrics down the 60px side strip. The pinned
confidence ball now lives on the camera feed (top-right), so the whole strip is free. Reuses the
standard UiElement classes for the data, with hand-set short labels and compact values to fit the
narrow lane: REAL / DESIRE steering angle, DIST (lead gap, single-char unit), LSPD (lead speed,
number only). Shows when DevUIInfo selects the right column (RIGHT or BOTH). Sizes/offsets are
tune-on-device knobs.
"""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiState
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import (
  RelDistElement, SteeringAngleElement, DesiredSteeringAngleElement,
  DesiredSteeringPIDElement, DesiredLateralAccelElement, LeadSpeedElement,
)
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


class StripDevUiRenderer(Widget):
  TOP_OFFSET = 40       # ball moved off the strip onto the feed, so metrics start near the top
  ROW_SPACING = 56      # tightened (was 74) so four rows group neatly instead of sprawling
  LABEL_SIZE = 17
  VALUE_SIZE = 18
  LABEL_COLOR = rl.Color(255, 255, 255, 180)

  def __init__(self):
    super().__init__()
    self._font_bold = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold = gui_app.font(FontWeight.SEMI_BOLD)
    self.steering_angle_elem = SteeringAngleElement()
    self.desired_pid_steer_elem = DesiredSteeringPIDElement()
    self.desired_steer_elem = DesiredSteeringAngleElement()
    self.desired_lat_accel_elem = DesiredLateralAccelElement()
    self.rel_dist_elem = RelDistElement()
    self.lead_speed_elem = LeadSpeedElement()

  def _desired(self, sm):
    which = sm['controlsState'].lateralControlState.which()
    if which == 'angleState':
      return self.desired_steer_elem.update(sm, ui_state.is_metric)
    if which == 'torqueState':
      return self.desired_lat_accel_elem.update(sm, ui_state.is_metric)
    return self.desired_pid_steer_elem.update(sm, ui_state.is_metric)

  def _render(self, _):
    if ui_state.developer_ui not in (DeveloperUiState.RIGHT, DeveloperUiState.BOTH):
      return
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    real = self.steering_angle_elem.update(sm, ui_state.is_metric)
    des = self._desired(sm)
    dist = self.rel_dist_elem.update(sm, ui_state.is_metric)
    lspd = self.lead_speed_elem.update(sm, ui_state.is_metric)
    dist_str = (dist.value + dist.unit) if dist.value != "-" else dist.value

    # (label, value, color). DIST appends its single-char unit (m); LSPD is number-only.
    rows = [
      ("REAL", real.value, real.color),
      ("DESIRE", des.value, des.color),
      ("DIST", dist_str, dist.color),
      ("LSPD", lspd.value, lspd.color),
    ]

    cx = int(self._rect.x + self._rect.width - SIDE_PANEL_WIDTH / 2)
    y = int(self._rect.y + self.TOP_OFFSET)
    for label, value, color in rows:
      lw = measure_text_cached(self._font_semi_bold, label, self.LABEL_SIZE, 0).x
      rl.draw_text_ex(self._font_semi_bold, label, rl.Vector2(cx - lw / 2, y), self.LABEL_SIZE, 0, self.LABEL_COLOR)
      vw = measure_text_cached(self._font_bold, value, self.VALUE_SIZE, 0).x
      rl.draw_text_ex(self._font_bold, value, rl.Vector2(cx - vw / 2, y + self.LABEL_SIZE + 3), self.VALUE_SIZE, 0, color)
      y += self.ROW_SPACING
