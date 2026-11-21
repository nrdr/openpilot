from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.params.tuning_policy import ANGLE_TUNING_KEYS, tuning_write_allowed
from openpilot.nrdr.ui.settings.lateral_experiments import LATERAL_EXPERIMENTS
from openpilot.nrdr.features.lateral.controller_selection import angle_controller_available, firmware_controller_profile
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
      remember("HondaClarityAngleCap3", toggle_item_sp(
        title=tr("Clarity Angle Lateral Cap 3.0 m/s²"), param="HondaClarityAngleCap3",
        description=tr("Uses the 3.0 m/s² clamp (mode 4) instead of 4.0. Requires EPS build 0x05. Switches while lateral is off."))),
      remember("HondaEpsAngleRateLimit", option_item_sp(
        title=tr("Clarity Angle Rate Limit"), param="HondaEpsAngleRateLimit", min_value=0, max_value=300, value_change_step=10,
        description=tr("Limits how fast the steering-angle target may move. Zero disables this optional cap."),
        label_callback=lambda value: tr("Off") if value == 0 else f"{value} deg/s")),
      *(remember(key, toggle_item_sp(title=tr(title), param=key, description=tr(description)))
        for key, title, description in LATERAL_EXPERIMENTS),
      remember("NrdrOptimizedLaneChanges", toggle_item_sp(
        title=tr("Optimized lane changes"), param="NrdrOptimizedLaneChanges",
        description=tr("Adjusts the steering response during lane changes to reduce abrupt corrections. Off keeps the " +
            "normal steering tune throughout the maneuver."))),
      remember("NrdrLatStiction", toggle_item_sp(
        title=tr("Predictive Lateral Stiction"), param="NrdrLatStiction",
        description=tr("Reduces steering force as the wheel reaches its target, then holds it steady until another " +
            "correction is needed. Off uses the normal steering response."))),
      remember("NrdrDeviceYawCorrection", toggle_item_sp(
        title=tr("Use Device Yaw Correction"), param="NrdrDeviceYawCorrection",
        description=tr("Adds a small steering correction based on the car's measured motion. Off uses PIF control alone."))),
      simple_button_item_sp(button_text=lambda: tr("Steer Ratio Tuning"), button_width=800, callback=steer_ratio_callback,
                            enabled=lambda: tuning_write_allowed(ui_state.params, "NrdrSteerRatioMode", CP=ui_state.CP, CP_SP=ui_state.CP_SP)),
    ]
    for band, label in (("LowSpeed", "[0-25MPH]"), ("Standard", "[25-50MPH]"), ("Highway", "[50+MPH]")):
      items.append(LineSeparatorSP(40))
      for term, name in (("P", "Proportional"), ("I", "Integral"), ("D", "Derivative"), ("F", "Feedforward")):
        key = f"NrdrLatRateDamping{band}" if term == "D" else f"Lat{term}Scale{band}"
        description = (("Resists rapid steering-wheel movement to reduce overshoot. Set to 0% to disable; optimized lane " +
            "changes temporarily bypass it.") if term == "D"
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
    saved = ui_state.params.get("NrdrLateralController")
    if angle_controller_available(ui_state.CP, ui_state.CP_SP) or saved in (3, "3", b"3"):
      return tr("Angle Controller")
    if saved in (2, "2", b"2"):
      return tr("PTM Testing")
    return tr("PTM Controller") if saved in (1, "1", b"1") else tr("PIF Control")

  @staticmethod
  def _commit_controller_selection(value):
    # Recheck on confirmation: the car may have started while the dialog was open.
    if not ui_state.is_offroad() or value not in (0, 1, 2, 3):
      return False
    if angle_controller_available(ui_state.CP, ui_state.CP_SP):
      return value == 3  # Firmware owns this choice. Leave the saved preference alone.
    if value in (1, 2) and firmware_controller_profile(ui_state.CP, ui_state.CP_SP, for_picker=True) is None:
      return False
    if value == 3:
      return False
    ui_state.params.put("NrdrLateralController", value, block=True)
    return True

  def _show_controller_selector(self):
    if not ui_state.is_offroad() or angle_controller_available(ui_state.CP, ui_state.CP_SP):
      return
    choices = {tr("PIF Control"): 0}
    if firmware_controller_profile(ui_state.CP, ui_state.CP_SP, for_picker=True) is not None:
      choices.update({tr("PTM Controller"): 1, tr("PTM Testing"): 2})
    options = list(choices)

    def selected(result):
      dialog, self._controller_dialog = self._controller_dialog, None
      if result == DialogResult.CONFIRM and dialog is not None and dialog.selection in options:
        self._commit_controller_selection(choices[dialog.selection])

    current = self._controller_label()
    self._controller_dialog = MultiOptionDialog(tr("Controller Type"), options, current if current in choices else options[0], callback=selected)
    gui_app.push_widget(self._controller_dialog)

  def _update_state(self):
    super()._update_state()
    angle_required = angle_controller_available(ui_state.CP, ui_state.CP_SP)
    self._controller.action_item.set_enabled(ui_state.is_offroad() and not angle_required)
    profile = firmware_controller_profile(ui_state.CP, ui_state.CP_SP)
    description = tr("PTM Testing is experimental and starts with the same PTM Timing Off behavior; no new tuning is deployed. " +
                     "Change while parked. Applies next drive. Clarity EPS 39990+TRW+A020 selects Angle Controller automatically. " +
                     "Angle assistance has unresolved steering dropouts; not for road use.")
    if profile is not None and profile.required_rwd:
      description += " " + tr("Requires the corrected PTM firmware (RWD {}). Older builds report the same EPS version and are not "
                       + "compatible.").format(profile.required_rwd)
      if profile.provisional:
        description += " " + tr("This calibration is not yet road-validated on that build.")
    self._controller.set_description(description)
    for key, item in self._tuning_items.items():
      available = key != "NrdrDeviceYawCorrection" or supports_interpolated_torque_pif(ui_state.CP, ui_state.CP_SP)
      if key in ANGLE_TUNING_KEYS:
        available = angle_controller_available(ui_state.CP, ui_state.CP_SP)
      if key == "NrdrDeviceYawCorrection":
        item.set_visible(angle_required or str(ui_state.params.get("NrdrLateralController")) not in ("1", "b'1'", "2", "b'2'"))
      item.action_item.set_enabled(available and tuning_write_allowed(ui_state.params, key, angle_required=angle_required))

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    height = self._back_button.rect.height + 40
    self._scroller.render(rl.Rectangle(rect.x, rect.y + height, rect.width, rect.height - height))

  def show_event(self):
    self._scroller.show_event()
