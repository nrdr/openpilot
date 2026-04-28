"""Base class for BP MICI "select from a list" screens.

Same look as the BP sub-panels (radial backdrop, BP topbar, frosted tiles).
Body is a horizontal scroller of `BPSelectTile`s — matches the rest of the BP
UI (settings landing, sub-panels) and avoids the swipe-down-to-dismiss vs.
scroll-back-to-top conflict that bites NavWidget children using vertical
scrollers.
"""
import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.scroller import _Scroller

from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.bp_topbar import BPTopbar, TOPBAR_HEIGHT
from openpilot.selfdrive.ui.bp.mici.widgets.cards import BPSelectTile


class BPSelectPanel(NavWidget):
  """NavWidget composing topbar + horizontal scroller of `BPSelectTile`s."""
  TITLE: str = ""

  def __init__(self, back_callback: Callable | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)

    self._bg = self._child(BPRadialBackground())
    self._topbar = self._child(BPTopbar(title=self.TITLE, on_back=self._on_back))

    tiles = self._build_rows()
    self._scroller = self._child(_Scroller(
      tiles, horizontal=True, snap_items=False,
      spacing=6, pad=10,
      scroll_indicator=True, edge_shadows=False,
    ))

  def _on_back(self):
    gui_app.pop_widget()
    if self._back_callback is not None:
      self._back_callback()

  # ---- subclass hook ----
  def _build_rows(self) -> list[BPSelectTile]:
    raise NotImplementedError

  # ---- helper for subclasses to rebuild on data change ----
  def _replace_rows(self, tiles: list[BPSelectTile]):
    self._scroller._items = []
    for tile in tiles:
      self._scroller.add_widget(tile)

  # ---- render ----
  def _render(self, _):
    r = self._rect
    self._bg.render(r)

    topbar_rect = rl.Rectangle(r.x, r.y, r.width, TOPBAR_HEIGHT)
    self._topbar.render(topbar_rect)

    body_y = r.y + TOPBAR_HEIGHT
    body_h = r.height - TOPBAR_HEIGHT
    self._scroller.render(rl.Rectangle(r.x, body_y, r.width, body_h))
