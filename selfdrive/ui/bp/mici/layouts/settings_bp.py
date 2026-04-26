"""BluePilot MICI settings landing — horizontal row of category tiles.

Replaces stock SettingsLayout (and sunnypilot's SettingsLayoutSP) with a
mockup-faithful 7-tile carousel. Each tile pushes its sub-panel via
gui_app.push_widget. The two existing BP-only panels (Vehicle and BluePilot)
are kept as the 6th and 7th tiles so functionality stays at parity.

The first 5 sub-panels are *new* BP-styled paged carousels that mirror the
content of their stock equivalents (TogglesLayoutMici, NetworkLayoutMici,
DeviceLayoutMici, FirehoseLayout, DeveloperLayoutMici) one-for-one.
"""
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.scroller import NavScroller

from openpilot.selfdrive.ui.bp.mici.widgets.cards import BigCategoryTile
from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground


# --- new BP-styled panels (mirror stock content / replace legacy BP panels) ---
from openpilot.selfdrive.ui.bp.mici.layouts.panels.toggles_bp import TogglesLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.network_bp import NetworkLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.device_bp import DeviceLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.firehose_bp import FirehoseLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.panels.developer_bp import DeveloperLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.bluepilot_bp import BluePilotLayoutBP
from openpilot.selfdrive.ui.bp.mici.layouts.vehicle_bp import VehicleLayoutBP


# Tile asset map — reused from the stock buttons so we don't ship duplicates.
_TILES: list[tuple[str, str]] = [
  ("toggles",   "icons_mici/settings.png"),
  ("network",   "icons_mici/settings/network/wifi_strength_full.png"),
  ("device",    "icons_mici/settings/device_icon.png"),
  ("firehose",  "icons_mici/settings/firehose.png"),
  ("developer", "icons_mici/settings/developer_icon.png"),
  ("vehicle",   "../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"),
  ("bluepilot", "icons_mici/settings/car_icon.png"),
]


class SettingsLayoutBP(NavScroller):
  def __init__(self):
    # NavScroller wires up swipe-down dismiss + horizontal _Scroller.
    super().__init__()

    # Background gradient drawn beneath the scroller items.
    self._bg = self._child(BPRadialBackground())

    # Build sub-panels lazily — instantiate on first tap to avoid the WifiManager
    # init paying its cost when the user just glances at settings.
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
    for name, icon in _TILES:
      tile = BigCategoryTile(label=name, icon=icon)
      tile.set_click_callback(lambda n=name: gui_app.push_widget(_ensure(n)))
      tiles.append(tile)

    self._scroller.add_widgets(tiles)

  def _render(self, _):
    # Paint backdrop, then let the NavScroller draw the items on top.
    self._bg.render(self._rect)
    super()._render(self._rect)
