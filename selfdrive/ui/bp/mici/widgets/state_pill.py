"""State pill — rounded pill with pulsing dot + caps label.

Three modes: STANDARD READY (green dot) / EXPERIMENTAL ARMED (amber dot) /
OFFLINE (grey dot, no pulse).
"""
import math
import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


class StatePill(Widget):
  """Pill: [colored dot] LABEL ; auto-sized to label width.

  Pass a callable that returns ('ready'|'experimental'|'offline', text). The
  pill recolors and resizes itself to fit the text per render.
  """
  PADDING_X = 18
  PADDING_Y = 8
  DOT_SIZE  = 16
  GAP       = 12

  def __init__(self, get_state: Callable[[], tuple[str, str]]):
    super().__init__()
    self._get_state = get_state
    self._label = UnifiedLabel(
      "",
      font_size=P.FS_PILL,
      font_weight=FontWeight.BOLD,
      text_color=P.TEXT,
      max_width=480,
      wrap_text=False,
    )
    self._mode = "ready"

  def _update_state(self):
    self._mode, text = self._get_state()
    self._label.set_text(text)

    # Resize self to fit content
    text_w = self._label.text_width
    pill_w = int(self.PADDING_X * 2 + self.DOT_SIZE + self.GAP + text_w)
    pill_h = int(self.PADDING_Y * 2 + max(self.DOT_SIZE, P.FS_PILL))
    self._rect = rl.Rectangle(self._rect.x, self._rect.y, pill_w, pill_h)

  def _dot_color(self) -> rl.Color:
    return {"experimental": P.WARN, "offline": P.OFFLINE}.get(self._mode, P.READY)

  def _render(self, _):
    r = self._rect

    # Pill bg
    rl.draw_rectangle_rounded(r, 1.0, 16, P.PANEL_BG)
    rl.draw_rectangle_rounded_lines_ex(r, 1.0, 16, 1, P.PANEL_BORDER)

    # Pulsing dot (no pulse when offline)
    cx = r.x + self.PADDING_X + self.DOT_SIZE / 2
    cy = r.y + r.height / 2
    color = self._dot_color()
    if self._mode != "offline":
      # Soft 1.8s pulse via sine: scale 0.85 → 1.0
      t = rl.get_time()
      pulse = 0.85 + 0.15 * (math.sin(t * (2 * math.pi / 1.8)) + 1) * 0.5
      glow = rl.Color(color.r, color.g, color.b, int(color.a * 0.5))
      rl.draw_circle(int(cx), int(cy), self.DOT_SIZE * 0.9 * pulse, glow)
    rl.draw_circle(int(cx), int(cy), self.DOT_SIZE / 2, color)

    # Label
    text_x = r.x + self.PADDING_X + self.DOT_SIZE + self.GAP
    # Vertical-center the label inside the pill (font baseline math via font_size)
    text_y = r.y + (r.height - P.FS_PILL) / 2
    self._label.set_position(text_x, text_y)
    self._label.render()
