"""The same 0–0.20 m/s slider on compact and large native screens."""
import pyray as rl

from openpilot.nrdr.params.pcm_speed_deadzone import PCM_SPEED_DEADZONE_TITLE, PCM_SPEED_DEADZONE_DESCRIPTION, PCM_SPEED_DEADZONE_DETAILS
from openpilot.nrdr.ui.honda_pcm import mvl_pcm_deadzone_available, saved_pcm_speed_deadzone, save_pcm_speed_deadzone
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import TextAlignment, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.list_view import ItemAction, ListItem


class PcmSpeedDeadzoneSlider(ItemAction):
  def __init__(self, compact=False):
    super().__init__(width=402 if compact else 560)
    self.compact = compact
    self.set_rect(rl.Rectangle(0, 0, 402 if compact else 560, 180))
    self._dragging = False
    self.value = saved_pcm_speed_deadzone(ui_state.params)

  def _available(self):
    return self.enabled and ui_state.is_offroad() and mvl_pcm_deadzone_available(ui_state.CP, ui_state.CP_SP, ui_state.params)

  def _track(self):
    return rl.Rectangle(self._rect.x + 30, self._rect.y + self._rect.height - 55, self._rect.width - 60, 35)

  def captures_horizontal_scroll(self):
    # The compact settings carousel must not steal a drag that starts on this track.
    return self._available() and self._touch_valid() and (self._dragging or any(
      event.left_pressed and rl.check_collision_point_rec(event.pos, self._track()) for event in gui_app.mouse_events
    ))

  def _handle_mouse_event(self, event):
    super()._handle_mouse_event(event)
    if not self._available() or not self._touch_valid():
      self._dragging = False
      return
    track = self._track()
    if event.left_pressed and rl.check_collision_point_rec(event.pos, track):
      self._dragging = True
    if self._dragging:
      self.value = round(min(max((event.pos.x - track.x) / track.width, 0.0), 1.0) * 20) / 100
    if event.left_released and self._dragging:
      self._dragging = False
      save_pcm_speed_deadzone(ui_state, self.value)
      self.value = saved_pcm_speed_deadzone(ui_state.params)

  def hide_event(self):
    self._dragging = False
    super().hide_event()

  def _render(self, rect):
    available = self._available()
    if not available or not self._touch_valid():
      self._dragging = False
    if not self._dragging:
      self.value = saved_pcm_speed_deadzone(ui_state.params)
    color = rl.WHITE if available else rl.GRAY
    if self.compact:
      rl.draw_rectangle_rounded(rect, 0.15, 10, rl.Color(25, 25, 25, 255))
      gui_label(rl.Rectangle(rect.x + 20, rect.y + 12, rect.width - 40, 58),
                tr(PCM_SPEED_DEADZONE_TITLE), font_size=25, color=color, alignment=TextAlignment.CENTER)
    gui_label(rl.Rectangle(rect.x, rect.y + 72, rect.width, 38),
              tr("Off") if self.value == 0 else f"{self.value:.2f} m/s", font_size=30, color=color, alignment=TextAlignment.CENTER)
    track = self._track()
    center_y = track.y + track.height / 2
    x = track.x + track.width * self.value / 0.20
    rl.draw_line_ex(rl.Vector2(track.x, center_y), rl.Vector2(track.x + track.width, center_y), 5, rl.DARKGRAY)
    rl.draw_line_ex(rl.Vector2(track.x, center_y), rl.Vector2(x, center_y), 5, color)
    rl.draw_circle(int(x), int(center_y), 12, color)


def speed_deadzone_item():
  action = PcmSpeedDeadzoneSlider()
  item = ListItem(title=lambda: tr(PCM_SPEED_DEADZONE_TITLE),
                  description=lambda: tr(PCM_SPEED_DEADZONE_DESCRIPTION) + " " + tr(PCM_SPEED_DEADZONE_DETAILS),
                  action_item=action)
  item._child(action)  # Cancel a drag if the containing settings page is hidden.
  return item
