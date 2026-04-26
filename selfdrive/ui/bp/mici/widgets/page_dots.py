"""Page-indicator dots row for the BP paged scroller.

Renders N dots with the active one elongated cyan (mockup style). Reads
current page + count from a callable so we don't have to reset on changes.
"""
import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.widgets import Widget
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


DOT_SIZE       = 7
DOT_ACTIVE_W   = 22
GAP            = 6
ANIMATION_RC   = 0.05


class PageDots(Widget):
  def __init__(self, get_current_page: Callable[[], int], get_page_count: Callable[[], int]):
    super().__init__()
    self._get_current = get_current_page
    self._get_count = get_page_count
    self._widths: list[FirstOrderFilter] = []

  def _ensure_filters(self, n: int) -> None:
    while len(self._widths) < n:
      self._widths.append(FirstOrderFilter(DOT_SIZE, ANIMATION_RC, 1 / gui_app.target_fps))
    while len(self._widths) > n:
      self._widths.pop()

  def _render(self, _):
    count = self._get_count()
    if count <= 1:
      return  # nothing to indicate
    cur = self._get_current()
    self._ensure_filters(count)

    # Animate widths (active → DOT_ACTIVE_W, others → DOT_SIZE)
    for i, f in enumerate(self._widths):
      target = DOT_ACTIVE_W if i == cur else DOT_SIZE
      f.update(target)

    total_w = sum(f.x for f in self._widths) + GAP * (count - 1)
    r = self._rect
    x = r.x + (r.width - total_w) / 2
    y = r.y + (r.height - DOT_SIZE) / 2

    for i, f in enumerate(self._widths):
      w = f.x
      if i == cur:
        # Active: cyan rounded pill
        dot_rect = rl.Rectangle(int(x), int(y), w, DOT_SIZE)
        rl.draw_rectangle_rounded(dot_rect, 1.0, 8, P.ACCENT2)
      else:
        # Inactive: dim circle
        cx = int(x + DOT_SIZE / 2)
        cy = int(y + DOT_SIZE / 2)
        rl.draw_circle(cx, cy, DOT_SIZE / 2, rl.Color(0xFF, 0xFF, 0xFF, int(0.25 * 255)))
      x += w + GAP
