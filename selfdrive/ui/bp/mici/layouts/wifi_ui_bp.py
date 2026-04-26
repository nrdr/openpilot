"""BP Wi-Fi UI — paged carousel of SSIDs.

Drop-in replacement for selfdrive/ui/mici/layouts/settings/network/wifi_ui.py
that renders the SSID list as one full-screen card per network. Tap a card to
connect (or to push a BPInputDialog if a password is needed). Currently does
not expose a "forget" affordance; that can be added with a long-press in a
future pass.
"""
import pyray as rl
from openpilot.common.swaglog import cloudlog
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.wifi_manager import WifiManager, Network, SecurityType
from openpilot.system.ui.widgets.nav_widget import NavWidget

from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.bp_topbar import BPTopbar, TOPBAR_HEIGHT
from openpilot.selfdrive.ui.bp.mici.widgets.paged_scroller import PagedScroller
from openpilot.selfdrive.ui.bp.mici.widgets.page_dots import PageDots
from openpilot.selfdrive.ui.bp.mici.widgets.cards import SsidRowCard
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPInputDialog


DOTS_HEIGHT = 20


class BPWifiUI(NavWidget):
  TITLE = "Wi-Fi"

  def __init__(self, wifi_manager: WifiManager):
    super().__init__()
    self._wifi_manager = wifi_manager
    self._networks: list[Network] = []
    self._cards: list[SsidRowCard] = []

    self._bg = self._child(BPRadialBackground())
    # Pager + dots are rebuilt whenever the network list changes.
    self._pager = self._child(PagedScroller([]))
    self._topbar = self._child(BPTopbar(
      title=self.TITLE,
      on_back=self._on_back,
      get_page_meta=lambda: (self._pager.current_page, self._pager.page_count),
    ))
    self._dots = self._child(PageDots(
      get_current_page=lambda: self._pager.current_page,
      get_page_count=lambda: self._pager.page_count,
    ))

    self._wifi_manager.add_callbacks(
      need_auth=self._on_need_auth,
      networks_updated=self._on_networks_updated,
    )

  # ---- public ----
  def show_event(self):
    super().show_event()
    self._wifi_manager.set_active(True)
    self._rebuild_pages(list(self._wifi_manager.networks))

  def hide_event(self):
    super().hide_event()
    self._wifi_manager.set_active(False)

  def _on_back(self):
    gui_app.pop_widget()

  def _on_networks_updated(self, networks: list[Network]):
    self._rebuild_pages(networks)

  def _rebuild_pages(self, networks: list[Network]):
    """Build one SsidRowCard per network and push them into the pager."""
    self._networks = networks
    self._cards = []
    for net in networks:
      strength_bars = max(0, min(4, int(net.strength * 4 / 100)))
      connected = (self._wifi_manager.connected_ssid == net.ssid)
      secured = (net.security_type != SecurityType.OPEN)
      card = SsidRowCard(
        ssid=net.ssid,
        secured=secured,
        strength=strength_bars,
        connected=connected,
        on_click=lambda ssid=net.ssid: self._connect_to(ssid),
      )
      self._cards.append(card)

    # Replace the pager's items in-place.
    self._pager._items = self._cards
    # Re-add to underlying scroller (clear + re-add).
    self._pager._scroller._items = []
    for c in self._cards:
      self._pager._scroller.add_widget(c)

  # ---- connect flow ----
  def _connect_to(self, ssid: str):
    network = next((n for n in self._networks if n.ssid == ssid), None)
    if network is None:
      cloudlog.warning(f"BPWifiUI: unknown SSID {ssid!r}")
      return

    if self._wifi_manager.is_connection_saved(network.ssid):
      self._wifi_manager.activate_connection(network.ssid)
    elif network.security_type == SecurityType.OPEN:
      self._wifi_manager.connect_to_network(network.ssid, "")
    else:
      self._on_need_auth(network.ssid, incorrect_password=False)

  def _on_need_auth(self, ssid: str, incorrect_password: bool = True):
    hint = "wrong password — re-enter" if incorrect_password else "enter password..."
    gui_app.push_widget(BPInputDialog(
      hint, "", minimum_length=8,
      confirm_callback=lambda pw: self._wifi_manager.connect_to_network(ssid, pw),
    ))

  # ---- render ----
  def _render(self, _):
    r = self._rect
    self._bg.render(r)

    topbar_rect = rl.Rectangle(r.x, r.y, r.width, TOPBAR_HEIGHT)
    self._topbar.render(topbar_rect)

    pager_y = r.y + TOPBAR_HEIGHT
    pager_h = r.height - TOPBAR_HEIGHT - DOTS_HEIGHT
    self._pager.render(rl.Rectangle(r.x, pager_y, r.width, pager_h))

    self._dots.render(rl.Rectangle(r.x, r.y + r.height - DOTS_HEIGHT, r.width, DOTS_HEIGHT))
