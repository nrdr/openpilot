from collections.abc import Callable
import pyray as rl

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
    self._driver_override_threshold = option_item_sp(
      param="NrdrDriverOverrideThreshold",
      title=lambda: tr("Driver Override Threshold (During Curves)"),
      min_value=100,
      max_value=5000,
      value_change_step=100,
      description=lambda: tr(
        "Sets the driver steering force needed to override assistance outside the straight-ahead range. Higher values require more force."
      ),
      label_callback=lambda value: f"{value}",
    )

    self._driver_override_threshold_cb = option_item_sp(
      param="NrdrOverrideThresholdCenterBoost",
      title=lambda: tr("Driver Override Threshold (During Straights)"),
      min_value=100,
      max_value=5000,
      value_change_step=100,
      description=lambda: tr(
        "Sets the driver steering force needed to override assistance within the Center Boost angle range. Higher values require more force."
      ),
      label_callback=lambda value: f"{value}",
    )

    self._driver_assist_during_override = toggle_item_sp(
      param="HondaDriverAssistDuringOverride",
      title=lambda: tr("Assist Pass-Through"),
      description=lambda: tr(
        "Reduces steering assistance when you take over to make manual steering feel smoother. Off keeps the normal override response."
      ),
    )

    self._override_fade_down = option_item_sp(
      param="HondaOverrideFadeDownSecs",
      title=lambda: tr("Override Torque Fade Down (Default: 0.50 s)"),
      min_value=0,
      max_value=1000,
      value_change_step=1,
      description=lambda: tr("Controls how quickly steering torque fades out when driver override begins."),
      label_callback=lambda value: f"{value / 100:.2f} s",
      use_float_scaling=True,
    )

    self._override_fade_up = option_item_sp(
      param="HondaOverrideFadeUpSecs",
      title=lambda: tr("Override Torque Fade Up (Default: 0.01 s)"),
      min_value=0,
      max_value=1000,
      value_change_step=1,
      description=lambda: tr("Controls how quickly steering torque fades back in after driver override ends."),
      label_callback=lambda value: f"{value / 100:.2f} s",
      use_float_scaling=True,
    )

    self._override_torque_scale = option_item_sp(
      param="HondaOverrideTorqueScale",
      title=lambda: tr("Override Torque Retain (Default: 0%)"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Sets how much steering assistance remains after the override fade-out. Zero removes it completely."),
      label_callback=lambda value: f"{value}%",
    )

    return [
      self._driver_override_threshold_cb,
      self._driver_override_threshold,
      LineSeparatorSP(40),
      self._driver_assist_during_override,
      self._override_fade_down,
      self._override_fade_up,
      self._override_torque_scale,
    ]

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
