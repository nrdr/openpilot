"""BP-styled offroad alerts pane.

Replaces the vertical-scroll list in selfdrive/ui/mici/layouts/offroad_alerts.py
with a paged horizontal carousel of alert cards on the BP radial backdrop.
Empty state shows a big centered "NO ALERTS" message.

Public API parity with MiciOffroadAlerts so MainLayout's wiring is unchanged:
- active_alerts() -> int
- scrolling() -> bool  (always False for our pager — alerts swipe horizontally)
"""
import time
import pyray as rl
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel

from openpilot.selfdrive.ui.mici.layouts.offroad_alerts import (
  OFFROAD_ALERTS, AlertData, REFRESH_INTERVAL,
)
from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.paged_scroller import PagedScroller
from openpilot.selfdrive.ui.bp.mici.widgets.page_dots import PageDots
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


SEVERITY_COLOR = {
  -1: P.ACCENT,         # update available
  0: P.OFFLINE,
  1: P.READY,
  2: P.WARN,
  3: P.DANGER,
}


class _AlertCard(Widget):
  """One alert per page."""
  def __init__(self, alert_data: AlertData, on_click: Callable | None = None):
    super().__init__()
    self.alert_data = alert_data
    self._on_click = on_click
    self._title = UnifiedLabel("", font_size=P.FS_NAME, font_weight=FontWeight.BOLD,
                               text_color=P.TEXT, max_width=520, wrap_text=True,
                               line_height=1.05)

  def _handle_mouse_release(self, _):
    if self._on_click:
      self._on_click()

  def _render(self, _):
    r = self._rect
    pad = 6
    bg = rl.Rectangle(r.x + pad, r.y + pad, r.width - pad * 2, r.height - pad * 2)
    color = SEVERITY_COLOR.get(self.alert_data.severity, P.WARN)

    # Card background — tinted by severity color
    card_bg = rl.Color(color.r, color.g, color.b, int(0.10 * 255))
    border = rl.Color(color.r, color.g, color.b, int(0.50 * 255))
    rl.draw_rectangle_rounded(bg, 0.10, 16, card_bg)
    rl.draw_rectangle_rounded_lines_ex(bg, 0.10, 16, 1, border)

    # Severity bar on the left
    rl.draw_rectangle(int(bg.x), int(bg.y) + 12, 6, int(bg.height) - 24, color)

    # Title
    text_x = bg.x + 22
    text_max_w = bg.width - 32
    self._title.set_text(self.alert_data.text)
    self._title.set_max_width(int(text_max_w))
    h = self._title.get_content_height(int(text_max_w)) + P.FS_NAME * 0.4
    self._title.set_rect(rl.Rectangle(text_x, bg.y + 14, text_max_w, h))
    self._title.render()


class MiciOffroadAlertsBP(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()
    self._sorted_alerts: list[AlertData] = []
    self._cards: list[_AlertCard] = []
    self._last_refresh = 0.0

    self._bg = self._child(BPRadialBackground())
    self._pager = self._child(PagedScroller([]))
    self._dots = self._child(PageDots(
      get_current_page=lambda: self._pager.current_page,
      get_page_count=lambda: self._pager.page_count,
    ))

    self._empty = UnifiedLabel(
      tr("no alerts"),
      font_size=72, font_weight=FontWeight.DISPLAY, text_color=P.MUTED,
      max_width=520, wrap_text=False,
    )

    self._build()

  # ---- public API parity ----
  def active_alerts(self) -> int:
    return sum(1 for a in self._sorted_alerts if a.visible)

  def max_severity(self) -> int | None:
    return max((a.severity for a in self._sorted_alerts if a.visible), default=None)

  def scrolling(self) -> bool:
    # Pager handles its own touch; report False so MainLayout doesn't gate.
    return False

  # ---- build / refresh ----
  def _build(self):
    self._sorted_alerts = []
    self._cards = []

    update = AlertData(key="UpdateAvailable", text="", severity=-1)
    self._sorted_alerts.append(update)
    self._cards.append(_AlertCard(update, on_click=lambda: HARDWARE.reboot()))

    for key, cfg in sorted(OFFROAD_ALERTS.items(),
                            key=lambda x: x[1].get("severity", 0), reverse=True):
      a = AlertData(key=key, text="", severity=cfg.get("severity", 0))
      self._sorted_alerts.append(a)
      self._cards.append(_AlertCard(a))

  def _refresh(self):
    update_available = self._params.get_bool("UpdateAvailable")

    for a in self._sorted_alerts:
      if a.key == "UpdateAvailable":
        if update_available:
          new_desc = self._params.get("UpdaterNewDescription") or ""
          version = ""
          if new_desc:
            parts = new_desc.split(" / ")
            if len(parts) > 3:
              version = f" — {parts[0]} ({parts[3]})"
          a.text = f"Update available{version}.  Tap to install."
          a.visible = True
        else:
          a.text = ""
          a.visible = False
      else:
        text = ""
        blob = self._params.get(a.key)
        if blob:
          text = blob.get("text", "").replace("%1", blob.get("extra", ""))
        a.text = text
        a.visible = bool(text)

    visible_cards = [c for c in self._cards if c.alert_data.visible]
    self._pager._items = visible_cards
    self._pager._scroller._items = []
    for c in visible_cards:
      self._pager._scroller.add_widget(c)

  # ---- lifecycle ----
  def show_event(self):
    super().show_event()
    self._last_refresh = time.monotonic()
    self._refresh()

  def _update_state(self):
    if time.monotonic() - self._last_refresh >= REFRESH_INTERVAL:
      self._refresh()
      self._last_refresh = time.monotonic()

  # ---- render ----
  def _render(self, _):
    r = self._rect
    self._bg.render(r)

    if self.active_alerts() == 0:
      tw = max(self._empty.text_width, 1)
      self._empty.set_position(r.x + (r.width - tw) / 2, r.y + (r.height - 72) / 2)
      self._empty.render()
      return

    # Pager + dots
    DOT = 20
    self._pager.render(rl.Rectangle(r.x, r.y, r.width, r.height - DOT))
    self._dots.render(rl.Rectangle(r.x, r.y + r.height - DOT, r.width, DOT))
