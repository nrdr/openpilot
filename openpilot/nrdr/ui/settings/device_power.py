"""Native presentation adapters for Prevent Automatic Shutdown.

Sunnylink integration note: its device fragment remains in
``settings_ui_src/pages/device.yaml`` until the separate canonical-fragment
migration lands. This module intentionally does not read or rewrite that file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openpilot.nrdr.params.generated.keys import NrdrParamKey

if TYPE_CHECKING:
  from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
  from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP


def automatic_shutdown_timer_description() -> str:
  from openpilot.system.ui.lib.multilang import tr

  return tr("Sets the automatic shutdown timer after the vehicle is turned off. This applies only when Prevent Automatic Shutdown is disabled; battery safeguards may shut the device down sooner.\n(30h is the default)")  # noqa: E501


def automatic_shutdown_timer_enabled() -> bool:
  from openpilot.selfdrive.ui.ui_state import ui_state

  return ui_state.is_offroad() and not ui_state.params.get_bool(NrdrParamKey.DISABLE_POWER_DOWN)


def automatic_shutdown_toggle_item() -> ListItemSP:
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.multilang import tr
  from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp

  return toggle_item_sp(
    title=lambda: tr("Prevent Automatic Shutdown"),
    description=lambda: tr("Prevents openpilot's automatic offroad shutdowns after the vehicle is turned off. This bypasses the Max Time Offroad timer and its low-voltage and estimated-battery safeguards, and can drain the vehicle battery. When disabled, those safeguards resume after a 60-second grace period. Manual Power Off still works."),  # noqa: E501
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
  )
  control.set_value(tr("battery drain risk"))
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
