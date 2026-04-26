"""Top-edge progress strip for long-press feedback on the BP home.

The home owns the long-press timer (mirrors stock MiciHomeLayout). It calls
update(progress) each frame with 0..1; this widget paints a 4px cyan strip
whose width = progress * rect_width. Glows out via box drop-shadow.
"""
import pyray as rl
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


class LongPressBar(Widget):
  HEIGHT = 4

  def __init__(self):
    super().__init__()
    self._progress: float = 0.0   # 0..1

  def set_progress(self, p: float) -> None:
    self._progress = max(0.0, min(1.0, p))

  def _render(self, _):
    if self._progress <= 0.0:
      return
    r = self._rect
    w = r.width * self._progress
    rl.draw_rectangle(int(r.x), int(r.y), int(w), self.HEIGHT, P.ACCENT2)
    # Subtle halo: a slightly translucent overlay one row below
    halo = rl.Color(P.ACCENT2.r, P.ACCENT2.g, P.ACCENT2.b, 90)
    rl.draw_rectangle(int(r.x), int(r.y) + self.HEIGHT, int(w), 2, halo)
