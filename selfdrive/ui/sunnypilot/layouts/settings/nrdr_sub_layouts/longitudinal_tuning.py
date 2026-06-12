"""
nrdr Longitudinal Tuning sub-panel.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP


class LongitudinalTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._long_pid_tune_scale = option_item_sp(
      param="LongPidTuneScale",
      title=lambda: tr("Longitudinal PID Tune Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales longitudinal PID controller values from their configured base tune."),
      label_callback=lambda value: f"{value}%",
    )

    self._static_feedforward_long = toggle_item_sp(
      param="StaticFeedforwardLong",
      title=lambda: tr("Keep Feedforward Static (Default: ON)"),
      description=lambda: tr("When ON, the longitudinal PID scale above multiplies only the feedback (P+I) terms; the feedforward (kf) keeps its tuned value instead of being scaled along with it. The lateral PID scales have their own toggle in Lateral Tuning."),
    )

    self._live_learning_gas = toggle_item_sp(
      param="HondaLiveLearningGas",
      title=lambda: tr("Live Learning Gas"),
      description=lambda: tr("Allows Honda gas and wind compensation factors to learn live while driving."),
    )

    self._stopping_decel_rate = option_item_sp(
      param="HondaStoppingDecelRate",
      title=lambda: tr("Stopping Decel Rate (Default: 0.3)"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Brake-rate limiter used while coming to a stop (carcontroller)."),
      label_callback=lambda value: f"{value / 100:.2f}",
    )

    self._stop_accel = option_item_sp(
      param="HondaStopAccel",
      title=lambda: tr("Stop Accel (Default: -2.0)"),
      min_value=-400,
      max_value=0,
      value_change_step=1,
      description=lambda: tr("Target acceleration once stopped (holds the brake)."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._stopping_decel_rate_long = option_item_sp(
      param="HondaStoppingDecelRateLong",
      title=lambda: tr("Planner Stopping Rate (Default: 0.3)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("How quickly commanded deceleration ramps down while coming to a stop."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._v_ego_stopping = option_item_sp(
      param="HondaVEgoStopping",
      title=lambda: tr("vEgo Stopping (Default: 0.5)"),
      min_value=0,
      max_value=300,
      value_change_step=1,
      description=lambda: tr("Speed (m/s) below which the planner treats the car as stopping."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._v_ego_starting = option_item_sp(
      param="HondaVEgoStarting",
      title=lambda: tr("vEgo Starting (Default: 0.5)"),
      min_value=0,
      max_value=300,
      value_change_step=1,
      description=lambda: tr("Speed (m/s) above which the car is considered moving again."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._radar_tryout = toggle_item_sp(
      param="HondaCivicRadarTryout",
      title=lambda: tr("Try Honda Bosch Radar (Default: OFF)"),
      description=lambda: tr("EXPERIMENTAL — Honda Bosch radar. When ON, openpilot reads the factory Bosch radar's fine-range objects (0x280) and treats this car like a fingerprint-matched radar car (radarUnavailable=False + the custom honda_civic_bosch_radar DBC). If you ALSO enable openpilot experimental/alpha longitudinal, this radar WILL feed openpilot's lead tracking and command braking/acceleration — exactly like a matched car. With openpilot longitudinal OFF (stock ACC) it is perception only. The 0x280 decode is reverse-engineered and cross-car validated (~0.99) but NOT verified on your specific car: before enabling openpilot longitudinal, VALIDATE that lead distance and closing-rate match reality. Honda Civic Bosch only. Leave OFF if unsure."),
    )

    return [
      self._long_pid_tune_scale,
      self._static_feedforward_long,
      LineSeparatorSP(40),
      self._live_learning_gas,
      LineSeparatorSP(40),
      self._stopping_decel_rate,
      self._stop_accel,
      self._stopping_decel_rate_long,
      self._v_ego_stopping,
      self._v_ego_starting,
      LineSeparatorSP(40),
      self._radar_tryout,
    ]

  def _update_state(self):
    super()._update_state()
    # Live Learning Gas may only be changed offroad.
    self._live_learning_gas.action_item.set_enabled(ui_state.is_offroad())

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
