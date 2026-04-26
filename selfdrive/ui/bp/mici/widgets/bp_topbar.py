"""Topbar for BP sub-panels: chevron back + title + (optional) "n/N" page counter.

Sized at 50px tall to match the mockup. The back chevron is a normal Widget so
it gets the framework's pressed/hover states for free.
"""
import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


TOPBAR_HEIGHT = 50
BACK_HIT_SIZE = 56
BACK_VISIBLE  = 28
TITLE_FONT    = 30


class _BackChevron(Widget):
  """Procedural left-chevron with a touch hit rect bigger than the visible glyph."""
  def __init__(self, on_back: Callable | None = None):
    super().__init__()
    self._on_back = on_back

  def _handle_mouse_release(self, _):
    if self._on_back:
      self._on_back()

  def _render(self, _):
    r = self._rect
    color = rl.Color(P.TEXT.r, P.TEXT.g, P.TEXT.b, 240) if not self.is_pressed else P.ACCENT2
    cx = r.x + r.width / 2
    cy = r.y + r.height / 2
    s = BACK_VISIBLE / 2
    # "<" — two line segments.
    rl.draw_line_ex(rl.Vector2(cx + s * 0.5, cy - s),
                    rl.Vector2(cx - s * 0.5, cy),  thickness := 4, color)
    rl.draw_line_ex(rl.Vector2(cx - s * 0.5, cy),
                    rl.Vector2(cx + s * 0.5, cy + s), thickness, color)


class BPTopbar(Widget):
  def __init__(self, title: str, on_back: Callable | None = None,
               get_page_meta: Callable[[], tuple[int, int]] | None = None):
    """
    title: shown at left next to back chevron.
    on_back: tap callback for the back chevron.
    get_page_meta: optional callable returning (current_page_zero_indexed, count)
                   shown as "n/N" at right.
    """
    super().__init__()
    self._on_back = on_back
    self._get_page_meta = get_page_meta

    self._back = self._child(_BackChevron(on_back=on_back))

    self._title = UnifiedLabel(
      title,
      font_size=TITLE_FONT,
      font_weight=FontWeight.BOLD,
      text_color=P.TEXT,
      max_width=400,
      wrap_text=False,
    )
    self._counter = UnifiedLabel(
      "",
      font_size=P.FS_PAGE_CTR,
      font_weight=FontWeight.MEDIUM,
      text_color=P.MUTED,
      max_width=120,
      wrap_text=False,
    )

  def _render(self, _):
    r = self._rect
    # Subtle gradient background so scrolled body content visually clips
    rl.draw_rectangle_gradient_v(int(r.x), int(r.y), int(r.width), int(r.height),
                                  rl.Color(0x02, 0x06, 0x0F, int(0.55 * 255)),
                                  rl.Color(0x02, 0x06, 0x0F, 0))

    # Back chevron — touch hit rect is BACK_HIT_SIZE square
    back_x = r.x + 8
    back_y = r.y + (r.height - BACK_HIT_SIZE) / 2
    self._back.render(rl.Rectangle(back_x, back_y, BACK_HIT_SIZE, BACK_HIT_SIZE))

    # Title — to the right of the chevron
    title_x = back_x + BACK_HIT_SIZE + 4
    title_y = r.y + (r.height - TITLE_FONT) / 2 - 2
    self._title.set_position(title_x, title_y)
    self._title.render()

    # Counter — right edge
    if self._get_page_meta is not None:
      cur, n = self._get_page_meta()
      if n > 1:
        self._counter.set_text(f"{cur + 1}/{n}")
        cw = max(self._counter.text_width, 1)
        cx = r.x + r.width - cw - 16
        cy = r.y + (r.height - P.FS_PAGE_CTR) / 2
        self._counter.set_position(cx, cy)
        self._counter.render()
