"""
BluePilot: MICI vehicle fingerprint selector (make → model).

BP-styled: uses BPSelectPanel (BP topbar + radial backdrop + vertical
scrolling frosted row cards) to match the rest of the BP UI. Car data from
sunnypilot selfdrive/car/car_list.json (same as TICI PlatformSelector).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable

from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPConfirmDialog
from openpilot.selfdrive.ui.bp.mici.widgets.cards import BPSelectTile
from openpilot.selfdrive.ui.bp.mici.widgets.select_panel import BPSelectPanel
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr

CAR_LIST_JSON = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "car", "car_list.json")
VEHICLE_ICON = "../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"


def load_car_platforms() -> dict:
  with open(CAR_LIST_JSON) as f:
    return json.load(f)


def platform_names_for_make(platforms: dict, make: str) -> list[str]:
  names = [p for p, d in platforms.items() if d.get("make") == make]
  return sorted(names)


def makes_available(platforms: dict) -> list[tuple[str, str]]:
  """Every unique ``make`` from car_list.json, sorted."""
  makes = sorted({d.get("make") for d in platforms.values() if d.get("make")})
  return [(m, m) for m in makes]


def _current_platform_name() -> str:
  bundle = ui_state.params.get("CarPlatformBundle")
  if not bundle:
    return ""
  name = bundle.get("name", "") if isinstance(bundle, dict) else ""
  if isinstance(name, bytes):
    name = name.decode("utf-8", errors="replace")
  return str(name).strip()


class VehicleMakeSelectMici(BPSelectPanel):
  """Vertical list of make rows; tapping a make pushes the model selector."""
  TITLE = "Select Make"

  def __init__(
    self,
    platforms: dict,
    on_stack_done: Callable[[], None] | None = None,
  ):
    self._platforms = platforms
    self._on_stack_done = on_stack_done
    self._current_make = ""
    cur = _current_platform_name()
    if cur:
      data = platforms.get(cur)
      if data:
        self._current_make = data.get("make", "")
    super().__init__()
    # Wire swipe-down + chevron back to fire on_stack_done so the parent
    # panel (Vehicle settings) refreshes its current-vehicle text.
    if on_stack_done is not None:
      self.set_back_callback(on_stack_done)

  def _build_rows(self) -> list[BPSelectTile]:
    rows: list[BPSelectTile] = []
    for display_label, make_key in makes_available(self._platforms):
      rows.append(BPSelectTile(
        label=display_label,
        icon=VEHICLE_ICON,
        selected=(make_key == self._current_make),
        on_click=lambda mk=make_key: self._open_models(mk),
      ))
    return rows

  def _open_models(self, make_key: str):
    names = platform_names_for_make(self._platforms, make_key)
    if not names:
      cloudlog.warning(f"No platforms for make {make_key}")
      return
    panel = VehicleModelSelectMici(
      self._platforms,
      names,
      on_vehicle_set=self._after_vehicle_set,
    )
    gui_app.push_widget(panel)

  def _after_vehicle_set(self):
    """User confirmed a vehicle: pop make panel, refresh root screen."""
    gui_app.pop_widget()
    if self._on_stack_done:
      self._on_stack_done()


class VehicleModelSelectMici(BPSelectPanel):
  """Vertical list of platform names for the chosen make; tap to confirm + apply."""
  TITLE = "Select Model"

  def __init__(
    self,
    platforms: dict,
    platform_names: list[str],
    on_vehicle_set: Callable[[], None] | None = None,
  ):
    self._platforms = platforms
    self._platform_names = platform_names
    self._on_vehicle_set = on_vehicle_set
    self._current = _current_platform_name()
    super().__init__()

  def _build_rows(self) -> list[BPSelectTile]:
    # Models can be 50+ chars (e.g. "Hyundai Ioniq 5 (Southeast Asia ...)") —
    # widen each tile so ~2 fit per page and let the label wrap to 2-3 lines.
    rows: list[BPSelectTile] = []
    for name in self._platform_names:
      rows.append(BPSelectTile(
        label=name,
        icon=VEHICLE_ICON,
        selected=(name == self._current),
        on_click=lambda n=name: self._ask_confirm(n),
        width=260,
        wrap_label=True,
      ))
    return rows

  def _ask_confirm(self, platform_name: str):
    title = (
      tr("slide to\napply now")
      if ui_state.is_offroad
      else tr("slide to\napply when offroad")
    )
    dlg = BPConfirmDialog(
      title,
      gui_app.texture("icons_mici/settings/car_icon.png", 64, 64),
      red=False,
      confirm_callback=lambda: self._apply_vehicle(platform_name),
    )
    gui_app.push_widget(dlg)

  def _apply_vehicle(self, platform_name: str):
    data = self._platforms.get(platform_name)
    if not data:
      cloudlog.error(f"Missing car_list entry for {platform_name}")
      return
    ui_state.params.put("CarPlatformBundle", {**data, "name": platform_name})
    cloudlog.info(f"MICI vehicle: set CarPlatformBundle to {platform_name}")
    gui_app.pop_widget()
    if self._on_vehicle_set:
      self._on_vehicle_set()
