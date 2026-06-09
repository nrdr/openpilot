"""
nrdr Override Tuning sub-panel.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
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
      title=lambda: tr("Increase Driver Override Tolerance (Default: ON)"),
      description=lambda: tr("Reduces the likelihood of false driver override detections (resulting in dropped torque) on sensitive Honda EPS platforms."),
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
      LineSeparatorSP(40),
      self._driver_assist_during_override,
      self._override_fade_down,
      self._override_fade_up,
      self._override_torque_scale,
    ]

  def _update_state(self):
    super()._update_state()
    self._increase_override_tolerance.action_item.set_enabled(True)
    self._driver_assist_during_override.action_item.set_enabled(True)
    self._override_fade_down.action_item.set_enabled(True)
    self._override_fade_up.action_item.set_enabled(True)
    self._override_torque_scale.action_item.set_enabled(True)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
