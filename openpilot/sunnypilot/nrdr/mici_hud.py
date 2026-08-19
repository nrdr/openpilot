import pyray as rl

from openpilot.selfdrive.ui.mici.onroad.hud_renderer import COLORS, FONT_SIZES, KM_TO_MILE, SET_SPEED_PERSISTENCE
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached


class NrdrHudRenderer:
  def _set_speed_color(self, alpha: float) -> rl.Color:
    color = (0, 255, 70) if ui_state.sm['longitudinalPlanSP'].speedLimit.assist.active else (255, 255, 255)
    return rl.Color(*color, int(255 * 0.9 * alpha))

  def _draw_additional_speed(self, rect: rl.Rectangle) -> None:
    if not self._can_draw_top_icons:
      return
    if self._engaged and 0 < rl.get_time() - self._set_speed_changed_time < SET_SPEED_PERSISTENCE:
      return

    x = int(rect.x + 16)
    y = int(rect.y + 12)
    speed_text = str(round(self.speed))
    speed_size = measure_text_cached(self._font_bold, speed_text, 100)
    rl.draw_text_ex(self._font_bold, speed_text, rl.Vector2(x, y), 100, 0, COLORS.WHITE)

    unit = tr("km/h") if ui_state.is_metric else tr("mph")
    rl.draw_text_ex(self._font_medium, unit, rl.Vector2(x + 6, y + speed_size.y - 26),
                    FONT_SIZES.speed_unit // 2, 0, COLORS.WHITE_TRANSLUCENT)

    if self.is_cruise_set and self._engaged:
      set_speed = self.set_speed if ui_state.is_metric else self.set_speed * KM_TO_MILE
      color = rl.Color(0, 255, 70, 255) if ui_state.sm['longitudinalPlanSP'].speedLimit.assist.active else rl.WHITE
      rl.draw_text_ex(self._font_display, str(round(set_speed)), rl.Vector2(x + speed_size.x + 14, y + 6), 54, 0, color)
