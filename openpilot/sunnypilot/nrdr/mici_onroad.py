import pyray as rl

from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import AugmentedRoadView
from openpilot.selfdrive.ui.mici.onroad.confidence_ball import ConfidenceBall, draw_circle_gradient
from openpilot.selfdrive.ui.mici.onroad.driver_state import DriverStateRenderer
from openpilot.selfdrive.ui.ui_state import UIStatus, ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiState
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import (
  DesiredLateralAccelElement,
  DesiredSteeringAngleElement,
  DesiredSteeringPIDElement,
  LeadSpeedElement,
  RelDistElement,
  SteeringAngleElement,
)
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


class NrdrConfidenceBall(ConfidenceBall):
  def _render(self, _):
    radius = 24
    x = self._rect.x + self._rect.width - SIDE_PANEL_WIDTH - radius - 16
    y = self._rect.y + radius + 36

    if ui_state.status == UIStatus.ENGAGED or self._demo:
      if self._confidence_filter.x > 0.5:
        top = rl.Color(0, 255, 204, 255)
        bottom = rl.Color(0, 255, 38, 255)
      elif self._confidence_filter.x > 0.2:
        top = rl.Color(255, 200, 0, 255)
        bottom = rl.Color(255, 115, 0, 255)
      else:
        top = rl.Color(255, 0, 21, 255)
        bottom = rl.Color(255, 0, 89, 255)
    elif ui_state.status in (UIStatus.LAT_ONLY, UIStatus.LONG_ONLY):
      top = bottom = self.get_lat_long_dot_color()
    elif ui_state.status == UIStatus.OVERRIDE:
      top = rl.Color(255, 255, 255, 255)
      bottom = rl.Color(82, 82, 82, 255)
    else:
      top = rl.Color(50, 50, 50, 255)
      bottom = rl.Color(13, 13, 13, 255)
    draw_circle_gradient(x, y, radius, top, bottom)


class StripDevUiRenderer(Widget):
  TOP_OFFSET = 28
  ROW_SPACING = 44
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
    desired = self._desired(sm)
    distance = self.rel_dist_elem.update(sm, ui_state.is_metric)
    lead_speed = self.lead_speed_elem.update(sm, ui_state.is_metric)
    distance_value = distance.value + distance.unit if distance.value != "-" else distance.value
    rows = (
      ("REAL", real.value, real.color),
      ("DESIRE", desired.value, desired.color),
      ("DIST", distance_value, distance.color),
      ("LSPD", lead_speed.value, lead_speed.color),
    )

    x = int(self._rect.x + self._rect.width - SIDE_PANEL_WIDTH / 2)
    y = int(self._rect.y + self.TOP_OFFSET)
    for label, value, color in rows:
      label_width = measure_text_cached(self._font_semi_bold, label, self.LABEL_SIZE, 0).x
      rl.draw_text_ex(self._font_semi_bold, label, rl.Vector2(x - label_width / 2, y), self.LABEL_SIZE, 0, self.LABEL_COLOR)
      value_width = measure_text_cached(self._font_bold, value, self.VALUE_SIZE, 0).x
      rl.draw_text_ex(self._font_bold, value, rl.Vector2(x - value_width / 2, y + self.LABEL_SIZE + 3), self.VALUE_SIZE, 0, color)
      y += self.ROW_SPACING


class NrdrDriverStateRenderer(DriverStateRenderer):
  def __init__(self, view):
    super().__init__()
    self.view = view

  def set_should_draw(self, _):
    super().set_should_draw(ui_state.status != UIStatus.DISENGAGED or ui_state.always_on_dm)

  def set_position(self, _x, _y):
    size = self.BASE_SIZE
    super().set_position(
      self.view._rect.x + self.view._rect.width - SIDE_PANEL_WIDTH - size - 16,
      self.view._rect.y + self.view._rect.height - size - 16,
    )


class NrdrAugmentedRoadView(AugmentedRoadView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._confidence_ball = NrdrConfidenceBall()
    self._driver_state_renderer = NrdrDriverStateRenderer(self)
    self._strip_dev_ui = StripDevUiRenderer()

  def _render(self, rect):
    super()._render(rect)
    self._strip_dev_ui.render(self.rect)
