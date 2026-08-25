"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr


class DeviceLayoutMiciSP(DeviceLayoutMici):
  def __init__(self):
    super().__init__()

    self._disable_power_down = BigParamControl(
      tr("prevent automatic\nshutdown"),
      "DisablePowerDown",
    )
    self._disable_power_down.set_value(tr("battery drain risk"))
    self._disable_power_down.set_enabled(ui_state.is_offroad)

    # Keep power behavior together, immediately before reset/reboot/power-off.
    self._scroller.add_widget(self._disable_power_down)
    power_control = self._scroller.items.pop()
    self._scroller.items.insert(len(self._scroller.items) - 3, power_control)

  def show_event(self):
    super().show_event()
    self._disable_power_down.refresh()
