"""BP Network panel — mirrors selfdrive/ui/mici/layouts/settings/network/network_layout.py.

The actual Wi-Fi list / connect flow is delegated to the existing WifiUIMici so
we don't reimplement the wifi UI; the BP panel just provides the entry point
plus tethering / metered / roaming / APN.
"""
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.wifi_manager import WifiManager, MeteredType
from openpilot.selfdrive.ui.bp.mici.layouts.wifi_ui_bp import BPWifiUI
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPInputDialog
from openpilot.selfdrive.ui.ui_state import ui_state

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import (
  BigToggleCard, BigMultiToggleCard, BigButtonCard,
)


class NetworkLayoutBP(BPSubPanel):
  TITLE = "Network"

  def __init__(self, back_callback=None):
    self._wifi_manager = WifiManager()
    self._wifi_manager.set_active(False)
    self._wifi_ui = BPWifiUI(self._wifi_manager)
    super().__init__(back_callback=back_callback)

  def _open_wifi(self):
    gui_app.push_widget(self._wifi_ui)

  def _open_tethering_password(self):
    current = self._wifi_manager.tethering_password or ""

    def on_confirm(password: str):
      if password:
        self._wifi_manager.set_tethering_password(password)

    gui_app.push_widget(BPInputDialog(
      "enter password...", current, minimum_length=8, confirm_callback=on_confirm,
    ))

  def _open_apn(self):
    current = ui_state.params.get("GsmApn") or ""

    def on_confirm(apn: str):
      apn = apn.strip()
      if apn == "":
        ui_state.params.remove("GsmApn")
      else:
        ui_state.params.put("GsmApn", apn)

    gui_app.push_widget(BPInputDialog(
      "enter APN...", current, minimum_length=0, confirm_callback=on_confirm,
    ))

  def _network_metered_change(self, idx: int):
    metered = [MeteredType.UNKNOWN, MeteredType.YES, MeteredType.NO][idx]
    self._wifi_manager.set_current_network_metered(metered)

  def _build_pages(self):
    return [
      BigButtonCard(
        "Wi-Fi networks", icon="icons_mici/settings/network/wifi_strength_full.png",
        on_click=self._open_wifi,
      ),
      BigMultiToggleCard(
        "Network Usage",
        "Tag this Wi-Fi as default, metered, or unmetered.",
        options=["default", "metered", "unmetered"],
        on_change=self._network_metered_change,
      ),
      BigToggleCard(
        "Enable Tethering",
        "Share this device's connection over Wi-Fi.",
        # Stock uses set_tethering_active() rather than a Params bool — for
        # simplicity in the carousel we expose the WifiManager state.
      ),
      BigButtonCard(
        "Tethering Password", icon="icons_mici/settings/network/tethering.png",
        on_click=self._open_tethering_password,
      ),
      BigToggleCard(
        "Enable Roaming",
        "Allow data on roaming carriers.",
        param_key="GsmRoaming",
      ),
      BigButtonCard(
        "APN Settings", on_click=self._open_apn,
      ),
      BigToggleCard(
        "Cellular Metered",
        "Treat the SIM as a metered connection.",
        param_key="GsmMetered",
      ),
    ]

  # Lifecycle parity with stock NetworkLayoutMici.
  def show_event(self):
    super().show_event()
    self._wifi_manager.set_active(True)
    gui_app.add_nav_stack_tick(self._wifi_manager.process_callbacks)

  def hide_event(self):
    super().hide_event()
    self._wifi_manager.set_active(False)
    gui_app.remove_nav_stack_tick(self._wifi_manager.process_callbacks)
