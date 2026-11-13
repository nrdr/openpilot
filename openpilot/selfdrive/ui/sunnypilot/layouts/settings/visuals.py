"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.ui import apply_chevron_preference
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget

CHEVRON_INFO_DESCRIPTION = {
  "enabled": tr_noop("Display useful metrics below the chevron that tracks the lead car " +
                     "only applicable to cars with sunnypilot longitudinal control."),
  "disabled": tr_noop("This feature requires sunnypilot longitudinal control to be available.")
}


class VisualsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._toggle_defs = {
      "BlindSpot": (
        lambda: tr("Show Blind Spot Warnings"),
        tr("Shows a warning when the car's blind-spot sensors detect another vehicle. Off hides the on-screen warnings without changing those sensors."),
        None,
      ),
      "TorqueBar": (
        lambda: tr("Steering Arc"),
        tr("Display steering arc on the driving screen when lateral control is enabled."),
        None,
      ),
      "RainbowMode": (
        lambda: tr("Enable Tesla Rainbow Mode"),
        tr("Adds a rainbow effect to the displayed driving path without changing driving behavior."),
        None,
      ),
      "StandstillTimer": (
        lambda: tr("Enable Standstill Timer"),
        tr("Show a timer on the HUD when the car is at a standstill."),
        None,
      ),
      "RoadNameToggle": (
        lambda: tr("Display Road Name"),
        tr("Shows the current road name on the driving screen. Requires downloaded OpenStreetMap data for the area."),
        None,
      ),
      "GreenLightAlert": (
        lambda: tr("Green Traffic Light Alert (Beta)"),
        tr("Plays an alert when the light turns green and there is no vehicle ahead. Check traffic before proceeding."),
        None,
      ),
      "LeadDepartAlert": (
        lambda: tr("Lead Departure Alert (Beta)"),
        tr("Plays an alert when you are stopped and the vehicle ahead starts moving. Check traffic before proceeding."),
        None,
      ),
      "TrueVEgoUI": (
        lambda: tr("Speedometer: Always Display True Speed"),
        tr("Shows wheel-sensor speed instead of the dashboard-adjusted speed on supported vehicles."),
        None,
      ),
      "HideVEgoUI": (
        lambda: tr("Speedometer: Hide from Onroad Screen"),
        tr("Hides the speedometer on the driving screen. Off shows it again."),
        None,
      ),
      "ShowTurnSignals": (
        lambda: tr("Display Turn Signals"),
        tr("Shows turn-signal indicators on the driving screen."),
        None,
      ),
      "RocketFuel": (
        lambda: tr("Real-time Acceleration Bar"),
        tr("Shows the car's measured acceleration and braking on the left side of the driving screen."),
        None,
      ),
    }
    self._toggles = {}
    for param, (title, desc, callback) in self._toggle_defs.items():
      toggle = toggle_item_sp(
        title=title,
        description=desc,
        param=param,
        initial_state=ui_state.params.get_bool(param),
        callback=callback,
      )
      self._toggles[param] = toggle

    self._chevron_info = multiple_button_item_sp(
      title=lambda: tr("Display Metrics Below Chevron"),
      description="",
      buttons=[lambda: tr("Off"), lambda: tr("Distance"), lambda: tr("Speed"), lambda: tr("Time"), lambda: tr("All")],
      param="ChevronInfo",
      inline=False
    )
    self._dev_ui_info = multiple_button_item_sp(
      title=lambda: tr("Developer UI"),
      description=lambda: tr("Display real-time parameters and metrics from various sources."),
      buttons=[lambda: tr("Off"), lambda: tr("Bottom"), lambda: tr("Right"), lambda: tr("Right & Bottom")],
      param="DevUIInfo",
      button_width=350,
      inline=False
    )

    items = list(self._toggles.values()) + [
      self._chevron_info,
      self._dev_ui_info,
    ]
    return items

  def _update_state(self):
    super()._update_state()
    chevron_info = ui_state.params.get("ChevronInfo", return_default=True)

    for param in self._toggle_defs:
      self._toggles[param].action_item.set_state(self._params.get_bool(param))

    self._dev_ui_info.action_item.set_selected_button(ui_state.params.get("DevUIInfo", return_default=True))

    if ui_state.has_longitudinal_control:
      self._chevron_info.set_description(tr(CHEVRON_INFO_DESCRIPTION["enabled"]))
      self._chevron_info.action_item.set_selected_button(ui_state.params.get("ChevronInfo", return_default=True))
      self._chevron_info.action_item.set_enabled(True)
    else:
      self._chevron_info.set_description(tr(CHEVRON_INFO_DESCRIPTION["disabled"]))
      self._chevron_info.action_item.set_enabled(False)
      ui_state.params.put("ChevronInfo", 0)

    apply_chevron_preference(self._chevron_info, ui_state, chevron_info)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
    if not ui_state.has_longitudinal_control:
      self._chevron_info.set_description(tr(CHEVRON_INFO_DESCRIPTION["disabled"]))
      self._chevron_info.show_description(True)
