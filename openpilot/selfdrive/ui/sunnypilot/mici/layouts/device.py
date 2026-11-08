"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.nrdr.ui.settings.device_power import attach_mici_automatic_shutdown_control
from openpilot.nrdr.ui.settings.pcm_modes_mici import longitudinal_controls
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici


class DeviceLayoutMiciSP(DeviceLayoutMici):
  def __init__(self):
    super().__init__()
    self._disable_power_down = attach_mici_automatic_shutdown_control(self._scroller)
    self._longitudinal_controls = longitudinal_controls()
    self._scroller.add_widgets(self._longitudinal_controls)
    self._scroller.set_scrolling_enabled(lambda: not any(
      getattr(control, "captures_horizontal_scroll", lambda: False)() for control in self._longitudinal_controls
    ))

  def show_event(self):
    super().show_event()
    self._disable_power_down.refresh()
    for control in self._longitudinal_controls:
      refresh = getattr(control, "refresh", None)
      if callable(refresh):
        refresh()
