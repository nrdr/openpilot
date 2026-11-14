"""Native presentation adapters for Prevent Automatic Shutdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openpilot.nrdr.params.generated.keys import NrdrParamKey

if TYPE_CHECKING:
  from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
  from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP


def automatic_shutdown_timer_description() -> str:
  from openpilot.system.ui.lib.multilang import tr

  return tr("Sets how long the device stays on after the car is turned off. Battery protection may shut it down sooner; Prevent Automatic Shutdown bypasses both.")  # noqa: E501


def automatic_shutdown_timer_enabled() -> bool:
  from openpilot.selfdrive.ui.ui_state import ui_state

  return ui_state.is_offroad() and not ui_state.params.get_bool(NrdrParamKey.DISABLE_POWER_DOWN)


def automatic_shutdown_toggle_item() -> ListItemSP:
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.multilang import tr
  from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp

  return toggle_item_sp(
    title=lambda: tr("Prevent Automatic Shutdown"),
    description=lambda: tr("Keeps the device on after the car is off, bypassing the shutdown timer and battery protection; this can drain the car battery. Turning this off restores those protections after 60 seconds."),  # noqa: E501
    param=NrdrParamKey.DISABLE_POWER_DOWN,
    enabled=ui_state.is_offroad,
  )


def attach_mici_automatic_shutdown_control(scroller) -> BigParamControl:
  from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.multilang import tr

  control = BigParamControl(
    tr("prevent automatic\nshutdown"),
    NrdrParamKey.DISABLE_POWER_DOWN,
    # Two title lines plus the warning must fit the C4's fixed 180px tile.
    font_size=30,
  )
  control.set_value(tr("battery drain"))
  control.set_enabled(ui_state.is_offroad)

  # Keep power behavior together, immediately before reset/reboot/power-off.
  scroller.add_widget(control)
  power_control = scroller.items.pop()
  scroller.items.insert(len(scroller.items) - 3, power_control)
  return control


__all__ = (
  "attach_mici_automatic_shutdown_control",
  "automatic_shutdown_timer_description",
  "automatic_shutdown_timer_enabled",
  "automatic_shutdown_toggle_item",
)
