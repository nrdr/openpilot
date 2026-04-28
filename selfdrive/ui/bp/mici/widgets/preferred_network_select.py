"""
BluePilot: MICI preferred WiFi network selector.

BP-styled: vertical scrolling list of saved networks rendered as frosted
row cards on the BP radial backdrop. Tap a network to set it as preferred,
or "None" to clear.
"""

from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.bp.mici.widgets.cards import BPSelectTile
from openpilot.selfdrive.ui.bp.mici.widgets.select_panel import BPSelectPanel
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wifi_manager import WifiManager, Network


WIFI_ICON = "icons_mici/settings/network/wifi_strength_full.png"


def _display_ssid(ssid: str) -> str:
  """Normalize SSID for display; fallback for empty."""
  s = (ssid or "").strip()
  if not s:
    return "Hidden Network"
  return "".join(c for c in s if c.isprintable() or c in " \t") or "Hidden Network"


class PreferredNetworkSelectMici(BPSelectPanel):
  """Tap a saved network to set it as preferred; tap "None" to clear."""
  TITLE = "Preferred Network"

  def __init__(self, wifi_manager: WifiManager, saved_networks: list[Network],
               on_dismiss: Callable[[], None] | None = None):
    self._params = Params()
    self._wifi_manager = wifi_manager
    self._saved_networks = saved_networks
    self._on_dismiss = on_dismiss
    self._current = ""
    val = self._params.get("WifiFavoriteSSID")
    if isinstance(val, bytes):
      val = val.decode("utf-8", errors="replace")
    self._current = (val or "").strip()
    super().__init__()
    if on_dismiss is not None:
      self.set_back_callback(on_dismiss)

  def _build_rows(self) -> list[BPSelectTile]:
    rows = [BPSelectTile(
      label=tr("None"),
      icon=WIFI_ICON,
      selected=(self._current == ""),
      on_click=lambda: self._select(""),
    )]
    for network in self._saved_networks:
      ssid = network.ssid
      rows.append(BPSelectTile(
        label=_display_ssid(ssid),
        icon=WIFI_ICON,
        selected=(ssid == self._current),
        on_click=lambda s=ssid: self._select(s),
      ))
    return rows

  def _select(self, ssid: str):
    """Save selection and dismiss."""
    self._params.put("WifiFavoriteSSID", ssid)
    if ssid:
      cloudlog.info(f"Set preferred network: {ssid}")
    else:
      cloudlog.info("Cleared preferred network")
    gui_app.pop_widget()
    if self._on_dismiss:
      self._on_dismiss()

  def show_event(self):
    super().show_event()
    self._wifi_manager.set_active(True)

  def hide_event(self):
    super().hide_event()
    self._wifi_manager.set_active(False)
