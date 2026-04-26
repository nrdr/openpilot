"""One-item-per-page horizontal carousel for BP MICI sub-panels.

Wraps the existing _Scroller (snap-to-item) by forcing every child to occupy a
full page width. The user-facing view is a horizontal pager with edge resistance
and momentum from GuiScrollPanel2.

Public API:
  - PagedScroller(items=[card,...]) — items are full-page widgets sized to
    (page_width, page_height); they are auto-resized in show_event() and
    whenever the parent rect changes.
  - current_page — int, the page closest to center.
  - page_count — int.
  - set_page(idx) — smooth scroll to page idx.

The included tap-vs-swipe arbitration is automatic: _Scroller's touch_valid
callback gates child clicks on `scroll_panel.is_touch_valid()`, which goes False
during a drag. So tap on a switch only fires if the carousel never entered
DRAGGING — the raylib equivalent of the mockup's setPointerCapture +
elementFromPoint dance.
"""
import pyray as rl

from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import _Scroller


class PagedScroller(Widget):
  def __init__(self, items: list[Widget]):
    super().__init__()
    # spacing=0, pad=0 means each item takes exactly 1 page; snap_items=True
    # snaps to the centered item ⇒ snaps to whole pages.
    self._scroller = self._child(_Scroller(
      [], horizontal=True, snap_items=True,
      spacing=0, pad=0,
      scroll_indicator=False, edge_shadows=False,
    ))
    self._items = items
    for item in items:
      self._scroller.add_widget(item)

  # ---- public API ----
  @property
  def page_count(self) -> int:
    return len(self._items)

  @property
  def current_page(self) -> int:
    """Page index closest to the viewport center."""
    if self.page_count == 0 or self._rect.width <= 0:
      return 0
    page_w = self._rect.width
    # scroll_offset is negative as we scroll right. 0 = page 0.
    raw = -self._scroller._scroll_offset / page_w
    return max(0, min(self.page_count - 1, round(raw)))

  def set_page(self, idx: int, smooth: bool = True) -> None:
    """Move to page `idx`. Sets the underlying scroll offset directly so
    snap math doesn't fight us — Scroller.scroll_to() expects screen-space
    coordinates which we don't always have here.
    """
    idx = max(0, min(self.page_count - 1, idx))
    target_offset = -idx * self._rect.width
    self._scroller.scroll_panel.set_offset(target_offset)
    if not smooth:
      # Cancel any in-flight snap interp so the new offset sticks.
      self._scroller._scrolling_to = (None, False)
      self._scroller._scroll_snap_filter.x = 0.0

  # ---- lifecycle ----
  def _update_layout_rects(self) -> None:
    # Resize every child to a full page so snap-to-item == snap-to-page.
    for item in self._items:
      item.set_rect(rl.Rectangle(0, 0, self._rect.width, self._rect.height))

  def show_event(self):
    super().show_event()
    # Make sure children are sized correctly for first render
    self._update_layout_rects()

  def _render(self, _):
    self._scroller.render(self._rect)
