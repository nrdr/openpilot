"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.nrdr.ui.settings.device_power import attach_mici_automatic_shutdown_control
from openpilot.nrdr.ui.settings.pcm_modes_mici import longitudinal_controls
from openpilot.nrdr.ui.settings.jetlink_mici import JetlinkLayoutMici
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.ui.settings.lateral_experiments import LATERAL_EXPERIMENTS, confirmed_honda_tuning
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


class LateralTuningLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._toggles = []
    for key, title, description in LATERAL_EXPERIMENTS:
      control = BigParamControl(tr(title), key, font_size=30, description=tr(description))
      control.set_enabled(lambda key=key: confirmed_honda_tuning(ui_state) and
                          tuning_write_allowed(ui_state.params, key, is_offroad=ui_state.is_offroad()))
      self._toggles.append(control)
    self._scroller.add_widgets(self._toggles)

  def _update_state(self):
    super()._update_state()
    for control in self._toggles:
      control.refresh()


class DeviceLayoutMiciSP(DeviceLayoutMici):
  def __init__(self):
    super().__init__()
    self._disable_power_down = attach_mici_automatic_shutdown_control(self._scroller)
    self._longitudinal_controls = longitudinal_controls()
    self._scroller.add_widgets(self._longitudinal_controls)
    self._lateral_panel = LateralTuningLayoutMici()
    self._lateral_btn = BigButton(tr("Lateral Tuning"), tr("settings"))
    self._lateral_btn.set_visible(lambda: confirmed_honda_tuning(ui_state))
    self._lateral_btn.set_click_callback(lambda: gui_app.push_widget(self._lateral_panel))
    self._scroller.add_widgets([self._lateral_btn])
    self._jetlink_panel = JetlinkLayoutMici()
    self._jetlink_btn = BigButton(tr("Jetlink"), tr("settings"))
    self._jetlink_btn.set_click_callback(lambda: gui_app.push_widget(self._jetlink_panel))
    self._scroller.add_widgets([self._jetlink_btn])
    self._scroller.set_scrolling_enabled(lambda: not any(
      getattr(control, "captures_horizontal_scroll", lambda: False)() for control in self._longitudinal_controls
    ))

  def show_event(self):
    super().show_event()
    self._scroller._items.remove(self._jetlink_btn)
    self._scroller._items.append(self._jetlink_btn)
    self._disable_power_down.refresh()
    for control in self._longitudinal_controls:
      refresh = getattr(control, "refresh", None)
      if callable(refresh):
        refresh()
