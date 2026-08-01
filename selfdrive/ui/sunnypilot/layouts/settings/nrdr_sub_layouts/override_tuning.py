"""
nrdr Override Tuning sub-panel.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.nrdr.handcrafted_lateral import is_handcrafted_lateral_enabled
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP


class OverrideTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._increase_override_tolerance = toggle_item_sp(
      param="NrdrIncreaseOverrideTolerance",
      title=lambda: tr("Increase Driver Override Hysteresis (Default: OFF)"),
      description=lambda: tr("Reduces the likelihood of false driver override detections (resulting in dropped torque) on sensitive Honda EPS platforms by doubling the override threshold below."),
    )

    self._driver_override_threshold = option_item_sp(
      param="NrdrDriverOverrideThreshold",
      title=lambda: tr("Driver Override Threshold (Default: 2400)"),
      min_value=100,
      max_value=5000,
      value_change_step=100,
      description=lambda: tr("Raw steering torque sensor reading above which you are considered to be steering (driver override). 1200 is Honda's stock threshold; on the few cars with a different stock threshold, your value is applied proportionally so 1200 always means stock."),
      label_callback=lambda value: f"{value}",
    )

    self._driver_override_threshold_cb = option_item_sp(
      param="NrdrOverrideThresholdCenterBoost",
      title=lambda: tr("Override Threshold Center Boost (Default: 1200)"),
      min_value=100,
      max_value=5000,
      value_change_step=100,
      description=lambda: tr("When the wheel is within the Center Boost degree band (on a straight), this lower override threshold applies instead of the one above - so you can override easily on straights while curves keep the higher threshold and don't drop torque from a false override. Set equal to Driver Override Threshold to disable."),
      label_callback=lambda value: f"{value}",
    )

    self._driver_assist_during_override = toggle_item_sp(
      param="HondaDriverAssistDuringOverride",
      title=lambda: tr("Pass-through assist torque on override (Default: ON)"),
      description=lambda: tr("When enabled, openpilot resets the EPS internal state which determines whether it is in lane assist mode or not. As such, enabling this will make the final override feel exactly the same as normal driving (after fade is completed), and when disabled the steering rack may carry on a more resistive feeling."),
    )

    self._override_fade_down = option_item_sp(
      param="HondaOverrideFadeDownSecs",
      title=lambda: tr("Override Torque Fade Down (Default: 0.1)"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Controls how quickly steering torque fades out when driver override begins."),
      label_callback=lambda value: f"{value / 100:.1f} s",
      use_float_scaling=True,
    )

    self._override_fade_up = option_item_sp(
      param="HondaOverrideFadeUpSecs",
      title=lambda: tr("Override Torque Fade Up (Default: 1.5)"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Controls how quickly steering torque fades back in after driver override ends."),
      label_callback=lambda value: f"{value / 100:.1f} s",
      use_float_scaling=True,
    )

    self._override_torque_scale = option_item_sp(
      param="HondaOverrideTorqueScale",
      title=lambda: tr("Override Torque Retain (Default: 0%)"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Controls how much openpilot steering torque remains when the override has gone past Override Torque Fade Down."),
      label_callback=lambda value: f"{value}%",
    )

    return [
      self._increase_override_tolerance,
      self._driver_override_threshold,
      self._driver_override_threshold_cb,
      LineSeparatorSP(40),
      self._driver_assist_during_override,
      self._override_fade_down,
      self._override_fade_up,
      self._override_torque_scale,
    ]

  def _update_state(self):
    super()._update_state()
    fingerprint = str(ui_state.CP.carFingerprint) if ui_state.CP is not None else ""
    editable = not is_handcrafted_lateral_enabled(fingerprint, ui_state.params)
    for item in (
      self._increase_override_tolerance, self._driver_override_threshold, self._driver_override_threshold_cb,
      self._driver_assist_during_override, self._override_fade_down, self._override_fade_up, self._override_torque_scale,
    ):
      item.action_item.set_enabled(editable)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
