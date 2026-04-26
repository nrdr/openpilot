"""BP-styled vehicle panel — port of selfdrive/ui/bp/mici/layouts/settings/vehicle_mici.py.

Same backend logic and dialogs; renders as a paged carousel matching the rest
of the BP UI.
"""
from collections.abc import Callable

from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.bp.mici.layouts.settings.vehicle_mici import CAR_LIST_JSON
from openpilot.selfdrive.ui.bp.mici.widgets.vehicle_select_mici import (
  VehicleMakeSelectMici, load_car_platforms,
)


def _vehicle_value_text() -> str:
  """Full (non-truncated) current-vehicle display string. The card auto-shrinks
  to fit, so we don't pre-elide here."""
  if bundle := ui_state.params.get("CarPlatformBundle"):
    name = bundle.get("name", "")
    if isinstance(name, bytes):
      name = name.decode("utf-8", errors="replace")
    return str(name).strip() or tr("unrecognized")
  if ui_state.CP is not None and ui_state.CP.carFingerprint != "MOCK":
    return str(ui_state.CP.carFingerprint)
  return tr("unrecognized")

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import StatCard, BigButtonCard


class VehicleLayoutBP(BPSubPanel):
  TITLE = "Vehicle"

  def __init__(self, back_callback: Callable | None = None):
    self._platforms: dict = {}
    try:
      self._platforms = load_car_platforms()
    except OSError as e:
      from openpilot.common.swaglog import cloudlog
      cloudlog.error(f"BP vehicle: could not load {CAR_LIST_JSON}: {e}")
    super().__init__(back_callback=back_callback)

  def _on_clear(self):
    ui_state.params.remove("CarPlatformBundle")

  def _on_select(self):
    if not self._platforms:
      return
    gui_app.push_widget(VehicleMakeSelectMici(self._platforms))

  def _build_pages(self):
    return [
      StatCard(
        tr("Current Vehicle"),
        _vehicle_value_text,
        variant="small",
      ),
      BigButtonCard(tr("Clear Vehicle"), on_click=self._on_clear),
      BigButtonCard(tr("Select Vehicle"), on_click=self._on_select),
    ]
