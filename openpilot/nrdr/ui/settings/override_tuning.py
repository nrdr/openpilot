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
      title=lambda: tr("Override Torque Fade Down (Default: 0.10 s)"),
      min_value=0,
      max_value=1000,
      value_change_step=1,
      description=lambda: tr("Controls how quickly steering torque fades out when driver override begins."),
      label_callback=lambda value: f"{value / 100:.2f} s",
      use_float_scaling=True,
    )

    self._override_fade_up = option_item_sp(
      param="HondaOverrideFadeUpSecs",
      title=lambda: tr("Override Torque Fade Up (Default: 1.00 s)"),
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

    # Clarity mode-switch / angle-loop EPS (opendbc sunnypilot/car/honda/clarity_eps.py)
    self._clarity_angle_mode = toggle_item_sp(
      param="HondaClarityAngleMode",
      title=lambda: tr("Clarity Angle Mode (Restart Required)"),
      description=lambda: tr(
        "Clarity only: steer by wheel angle through the angle-loop EPS firmware (build 0x04/0x05). On any other EPS firmware "
        "steering stays unavailable, so leave this off. Takes effect at the next start."
      ),
    )
    self._clarity_angle_cap3 = toggle_item_sp(
      param="HondaClarityAngleCap3",
      title=lambda: tr("Clarity Angle Lateral Cap 3.0 m/s\u00b2"),
      description=lambda: tr(
        "Angle mode only: use the EPS's 3.0 m/s\u00b2 lateral-acceleration clamp (mode 4) instead of 4.0. Needs EPS build 0x05; "
        "no effect on other builds. Switches while lateral is off."
      ),
    )
    self._angle_rate_limit = option_item_sp(
      param="HondaEpsAngleRateLimit",
      title=lambda: tr("Clarity Angle Rate Limit"),
      min_value=0,
      max_value=300,
      value_change_step=10,
      description=lambda: tr("Angle mode only: caps how fast the steering-angle target may move, in deg/s. 0 turns the cap off."),
      label_callback=lambda value: tr("Off") if value == 0 else f"{value} deg/s",
    )

    return [
      self._driver_override_threshold_cb,
      self._driver_override_threshold,
      LineSeparatorSP(40),
      self._driver_assist_during_override,
      self._override_fade_down,
      self._override_fade_up,
      self._override_torque_scale,
      self._clarity_angle_mode,
      self._clarity_angle_cap3,
      self._angle_rate_limit,
    ]

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
