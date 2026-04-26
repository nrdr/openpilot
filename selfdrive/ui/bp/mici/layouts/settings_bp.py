"""BluePilot MICI settings landing — horizontal row of category tiles.

Replaces stock SettingsLayout (and sunnypilot's SettingsLayoutSP) with the
mockup-faithful layout: a "Settings" topbar at top, then a row of frosted
category tiles (5 visible at once on a 536px screen) drawn with feather-style
procedural icons.

The two existing BP-only panels (Vehicle and BluePilot) are kept as the 6th
and 7th tiles so functionality stays at parity — they scroll into view.
"""
import pyray as rl
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.scroller import _Scroller

from openpilot.selfdrive.ui.bp.mici.widgets.cards import BigCategoryTile
from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.bp_topbar import BPTopbar, TOPBAR_HEIGHT


# --- new BP-styled panels (mirror stock content / replace legacy BP panels) ---
from openpilot.selfdrive.ui.bp.mici.layouts.panels.toggles_bp import TogglesLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.network_bp import NetworkLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.device_bp import DeviceLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.firehose_bp import FirehoseLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.developer_bp import DeveloperLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.bluepilot_bp import BluePilotLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.vehicle_bp import VehicleLayoutBP


# Each tile: (panel key, display label, icon PNG path).
_TILES: list[tuple[str, str, str]] = [
  ("toggles",   "Toggles",   "icons_mici/settings.png"),
  ("network",   "Network",   "icons_mici/settings/network/wifi_strength_full.png"),
  ("device",    "Device",    "icons_mici/settings/device_icon.png"),
  ("firehose",  "Firehose",  "icons_mici/settings/firehose.png"),
  ("developer", "Developer", "icons_mici/settings/developer_icon.png"),
  ("vehicle",   "Vehicle",   "../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"),
  ("bluepilot", "BluePilot", "icons_mici/settings/car_icon.png"),
]


class SettingsLayoutBP(NavWidget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))

    self._bg = self._child(BPRadialBackground())
    self._topbar = self._child(BPTopbar(title="Settings", on_back=self._on_back))

    # Lazy panel instantiation so opening Settings doesn't pay WifiManager
    # init costs unless the user actually drills into a panel.
    panels: dict[str, object] = {}

    def _ensure(name):
      if name not in panels:
        panels[name] = {
          "toggles":   TogglesLayoutBP,
          "network":   NetworkLayoutBP,
          "device":    DeviceLayoutBP,
          "firehose":  FirehoseLayoutBP,
          "developer": DeveloperLayoutBP,
          "vehicle":   lambda: VehicleLayoutBP(back_callback=gui_app.pop_widget),
          "bluepilot": lambda: BluePilotLayoutBP(back_callback=gui_app.pop_widget),
        }[name]()
      return panels[name]

    tiles = []
    for key, label, icon_path in _TILES:
      tile = BigCategoryTile(label=label, icon=icon_path)
      tile.set_click_callback(lambda n=key: gui_app.push_widget(_ensure(n)))
      tiles.append(tile)

    # Horizontal scroller below the topbar — restore the framework's scroll
    # indicator + edge shadows so the user sees there's more to scroll into
    # (Vehicle / BluePilot tiles past the visible 5).
    self._scroller = self._child(_Scroller(
      tiles, horizontal=True, snap_items=False,
      spacing=6, pad=10,
      scroll_indicator=True, edge_shadows=True,
    ))

  def _on_back(self):
    gui_app.pop_widget()

  def _render(self, _):
    r = self._rect
    self._bg.render(r)
    self._topbar.render(rl.Rectangle(r.x, r.y, r.width, TOPBAR_HEIGHT))
    body = rl.Rectangle(r.x, r.y + TOPBAR_HEIGHT, r.width, r.height - TOPBAR_HEIGHT)
    self._scroller.render(body)
