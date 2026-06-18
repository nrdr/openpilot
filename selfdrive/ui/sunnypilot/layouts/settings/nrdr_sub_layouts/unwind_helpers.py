"""
nrdr Unwind Helpers sub-panel.

Everything that shapes how the wheel returns toward center after a turn:
integrator freeze, model lookahead, and the low-speed feedforward boost.
One level under Lateral Tuning.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp


class UnwindHelpersLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._unwind_freeze = toggle_item_sp(
      param="HondaUnwindFreeze",
      title=lambda: tr("Unwind Integrator Freeze (Default: OFF)"),
      description=lambda: tr("Freezes the PID integrator while the steering is returning toward center, so it doesn't hold torque through the unwind."),
    )

    self._unwind_lookahead = toggle_item_sp(
      param="HondaUnwindLookahead",
      title=lambda: tr("Unwind Lookahead (Default: ON)"),
      description=lambda: tr("Reads the model's planned path to start unwinding earlier, before the instantaneous desired curvature drops."),
    )

    self._unwind_boost_seconds = option_item_sp(
      param="HondaUnwindBoostSeconds",
      title=lambda: tr("Unwind Boost Duration (Default: 1.0s)"),
      min_value=0,
      max_value=300,
      value_change_step=10,
      description=lambda: tr("How long the extra unwind feedforward is held at the start of each unwind before it fades out. Caps the low-speed return assist so it doesn't keep pushing torque through a long unwind. 0 = off."),
      label_callback=lambda value: f"{value / 100:.1f}s",
      use_float_scaling=True,
    )

    self._unwind_ff_multiplier = option_item_sp(
      param="HondaUnwindFfMultiplier",
      title=lambda: tr("Unwind Feedforward Multiplier (Default: 2.0x)"),
      min_value=100,
      max_value=400,
      value_change_step=10,
      description=lambda: tr("Peak feedforward multiplier during an unwind, strongest at a standstill and fading to 1x (no boost) by ~22 mph. Raise for more low-speed return authority if the wheel is lazy coming back to center."),
      label_callback=lambda value: f"{value / 100:.1f}x",
      use_float_scaling=True,
    )

    return [
      self._unwind_freeze,
      self._unwind_lookahead,
      self._unwind_boost_seconds,
      self._unwind_ff_multiplier,
    ]

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
