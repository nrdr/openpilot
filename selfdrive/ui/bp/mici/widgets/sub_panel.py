"""Base class for BP MICI sub-panels.

Composes a topbar, a paged-carousel of single-item-per-page cards, and a row
of page-indicator dots on top of the BP radial backdrop. Subclasses just
provide a list of card widgets.
"""
import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.nav_widget import NavWidget

from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.bp_topbar import BPTopbar, TOPBAR_HEIGHT
from openpilot.selfdrive.ui.bp.mici.widgets.paged_scroller import PagedScroller
from openpilot.selfdrive.ui.bp.mici.widgets.page_dots import PageDots


DOTS_HEIGHT = 20


class BPSubPanel(NavWidget):
  """A NavWidget containing topbar + paged carousel + dot indicator.

  Override `_build_pages()` (returns list[Widget]) in subclasses.
  Title is provided via `title` parameter; back_callback is optional (NavWidget
  also supports swipe-down to dismiss).
  """
  TITLE: str = ""

  def __init__(self, back_callback: Callable | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)

    self._bg = self._child(BPRadialBackground())

    pages = self._build_pages()
    self._pager = self._child(PagedScroller(pages))

    self._topbar = self._child(BPTopbar(
      title=self.TITLE,
      on_back=self._on_back,
      get_page_meta=lambda: (self._pager.current_page, self._pager.page_count),
    ))

    self._dots = self._child(PageDots(
      get_current_page=lambda: self._pager.current_page,
      get_page_count=lambda: self._pager.page_count,
    ))

  def _on_back(self):
    # Tapping the back chevron same as a programmatic dismiss.
    from openpilot.system.ui.lib.application import gui_app as _ga
    _ga.pop_widget()
    if self._back_callback is not None:
      self._back_callback()

  # ---- subclass hook ----
  def _build_pages(self) -> list[Widget]:
    """Return the cards (one per page)."""
    raise NotImplementedError

  # ---- render ----
  def _render(self, _):
    r = self._rect
    self._bg.render(r)

    # Topbar (50px) at the top
    topbar_rect = rl.Rectangle(r.x, r.y, r.width, TOPBAR_HEIGHT)
    self._topbar.render(topbar_rect)

    # Pager fills middle, leaving room for dots at bottom
    pager_y = r.y + TOPBAR_HEIGHT
    pager_h = r.height - TOPBAR_HEIGHT - DOTS_HEIGHT
    self._pager.render(rl.Rectangle(r.x, pager_y, r.width, pager_h))

    # Dots row pinned to bottom
    self._dots.render(rl.Rectangle(r.x, r.y + r.height - DOTS_HEIGHT, r.width, DOTS_HEIGHT))
