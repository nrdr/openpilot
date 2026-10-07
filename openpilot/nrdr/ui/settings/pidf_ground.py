from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile, yaw_controller_available
from openpilot.nrdr.features.lateral.capabilities import supports_interpolated_torque_pif
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import (
  LineSeparatorSP, button_item_sp, option_item_sp, simple_button_item_sp, toggle_item_sp,
)


class PidfGroundLayout(Widget):
  def __init__(self, back_btn_callback: Callable, steer_ratio_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._controller_dialog = None
    self._controller = button_item_sp(
      title=lambda: tr("Controller Type"), description="", button_text=self._controller_label,
      callback=self._show_controller_selector, enabled=lambda: ui_state.is_offroad())
    self._tuning_items = {}

    def remember(key, item):
      self._tuning_items[key] = item
      return item

    items = [self._controller,
      remember("NrdrLatStiction", toggle_item_sp(
        title=tr("Predictive Lateral Stiction"), param="NrdrLatStiction",
        description=tr("Tapers torque near a stable target. Driver input, lane changes, faults and steering limits bypass it."))),
      remember("NrdrDeviceYawCorrection", toggle_item_sp(
        title=tr("Use Device Yaw Correction"), param="NrdrDeviceYawCorrection",
        description=tr("Blends 1% device-yaw torque feedback with 99% PIF. Not used by Firmware Controller. Optimized lane changes bypass it."))),
      remember("NrdrOptimizedLaneChanges", toggle_item_sp(
        title=tr("Optimized lane changes"), param="NrdrOptimizedLaneChanges",
        description=tr("NRDR lane-change entry shaping. During the maneuver, uses P/I feedback without torque blend, feedforward or rate damping."))),
      simple_button_item_sp(button_text=lambda: tr("Steer Ratio Tuning"), button_width=800, callback=steer_ratio_callback),
    ]
    for band, label in (("LowSpeed", "[0-25MPH]"), ("Standard", "[25-50MPH]"), ("Highway", "[50+MPH]")):
      items.append(LineSeparatorSP(40))
      for term, name in (("P", "Proportional"), ("I", "Integral"), ("D", "Derivative"), ("F", "Feedforward")):
        key = f"NrdrLatRateDamping{band}" if term == "D" else f"Lat{term}Scale{band}"
        description = ("Opposes steering-wheel motion to help reduce overshoot (steering-rate damping). "
                       + "Defaults to 0% (off). Optimized lane changes bypass it." if term == "D"
                       else "Supplies anticipated steering torque before an error occurs.")
        spec = get_native_option_spec(key) if term in ("P", "I") else None
        if spec is not None:
          description = spec.description
        items.append(remember(key, option_item_sp(
          title=lambda label=label, name=name: tr(f"{label} {name}"), param=key,
          description=lambda description=description: tr(description), min_value=spec.min_value if spec else 0,
          max_value=spec.max_value if spec else (300 if term == "D" else 500),
          value_change_step=spec.value_change_step if spec else 5, label_callback=lambda value: f"{value}%")))
    items.append(LineSeparatorSP(40))
    for key, title, maximum, step, scaled, suffix in (
      ("HondaCenterScale", "Center Boost", 500, 1, True, "%"),
      ("HondaCenterBoostThreshold", "Center Boost Threshold", 1000, 10, True, "°"),
      ("HondaCenterBoostMinSpeed", "Center Boost Minimum Speed", 80, 1, False, " mph"),
    ):
      items.append(remember(key, option_item_sp(
        title=lambda title=title: tr(title), param=key, min_value=0, max_value=maximum,
        value_change_step=step, use_float_scaling=scaled,
        label_callback=lambda value, key=key, suffix=suffix: f"{value / 100 if key == 'HondaCenterBoostThreshold' else value:g}{suffix}")))
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  @staticmethod
  def _controller_label():
    return tr("Firmware Controller") if str(ui_state.params.get("NrdrLateralController")) in ("1", "b'1'") else tr("PIF Control")

  @staticmethod
  def _commit_controller_selection(value):
    # Recheck on confirmation: the car may have started while the dialog was open.
    if not ui_state.is_offroad() or value not in (0, 1):
      return False
    if value == 1 and not yaw_controller_available(ui_state.CP, ui_state.CP_SP):
      return False
    ui_state.params.put("NrdrLateralController", value, block=True)
    return True

  def _show_controller_selector(self):
    if not ui_state.is_offroad():
      return
    options = [tr("PIF Control")]
    if yaw_controller_available(ui_state.CP, ui_state.CP_SP):
      options.append(tr("Firmware Controller"))

    def selected(result):
      dialog, self._controller_dialog = self._controller_dialog, None
      if result == DialogResult.CONFIRM and dialog is not None and dialog.selection in options:
        self._commit_controller_selection(options.index(dialog.selection))

    self._controller_dialog = MultiOptionDialog(tr("Controller Type"), options, self._controller_label(), callback=selected)
    gui_app.push_widget(self._controller_dialog)

  def _update_state(self):
    super()._update_state()
    self._controller.action_item.set_enabled(ui_state.is_offroad())
    profile = firmware_controller_profile(ui_state.CP, ui_state.CP_SP)
    self._controller.set_description(tr("TEG-A010 uses the Bosch C020 tune as a provisional placeholder, not a road-validated calibration.")
                                     if profile is not None and profile.provisional else "")
    for key, item in self._tuning_items.items():
      available = key != "NrdrDeviceYawCorrection" or supports_interpolated_torque_pif(ui_state.CP, ui_state.CP_SP)
      if key == "NrdrDeviceYawCorrection":
        item.set_visible(str(ui_state.params.get("NrdrLateralController")) not in ("1", "b'1'"))
      item.action_item.set_enabled(available and tuning_write_allowed(ui_state.params, key))

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    height = self._back_button.rect.height + 40
    self._scroller.render(rl.Rectangle(rect.x, rect.y + height, rect.width, rect.height - height))

  def show_event(self):
    self._scroller.show_event()
