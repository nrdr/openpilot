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
      description=lambda: tr(
        "When ON, the longitudinal PID scale above multiplies only the feedback (P+I) terms; the feedforward (kf) keeps its tuned value " +
        "instead of being scaled along with it. The lateral PID scales have their own toggle in Lateral Tuning."
      ),
    )

    self._ecu_matched_long = toggle_item_sp(
      param="NrdrHondaEcuMatchedLong",
      title=lambda: tr("Nidec ECU-Matched Long (Default: OFF)"),
      description=lambda: tr(
        "Honda Nidec only. Shapes the longitudinal command to match the factory ECU: rate-limits the acceleration command to the ECU's " +
        "ramp rates, applies a speed-dependent coasting deadband (wide at low speed, tight on the highway), and briefly coasts through " +
        "gas/brake transitions to avoid lurch. Calibrated on the 2019 Pilot; other Nidec cars may need tuning. OFF = stock command path."
      ),
    )

    self._full_brake_authority = toggle_item_sp(
      param="NrdrHondaFullBrakeAuthority",
      title=lambda: tr("Full Nidec Brake Authority (Default: ON)"),
      description=lambda: tr(
        "Allows supported Honda Nidec longitudinal control to use the full normalized brake-command range. " +
        "Disable to retain the upstream brake-command headroom."
      ),
    )

    self._roen_acceleration_limits = toggle_item_sp(
      param="NrdrRoenAccelerationLimits",
      title=lambda: tr("Roen Nidec Acceleration Limits (Default: ON)"),
      description=lambda: tr(
        "Uses Roen's ISO-based planner and Nidec pedal-controller acceleration envelopes with full low-speed pedal scaling. " +
        "This operates independently of Live Learning Gas."
      ),
    )

    self._cruise_overspeed_allowance = option_item_sp(
      param="NrdrCruiseOverspeedAllowance",
      title=lambda: tr("Set-Speed Overshoot Allowance (Default: 0 mph)"),
      min_value=0,
      max_value=10,
      value_change_step=1,
      description=lambda: tr(
        "Allows the cruise target to follow vehicle speed by up to this amount above the set speed when no other speed target is lower. " +
        "0 mph preserves stock behavior."
      ),
      label_callback=lambda value: f"{value} mph",
    )

    self._cruise_mismatch_correction = option_item_sp(
      param="NrdrCruiseMismatchCorrection",
      title=lambda: tr("Cruise Mismatch Correction (Default: 100.0%)"),
      min_value=9500,
      max_value=10500,
      value_change_step=10,
      description=lambda: tr(
        "Correct slight variances in final cruising target speed to better match the current and set speeds together. Tire, suspension, " +
        "and other vehicle dynamics can affect this including manufacturer design. If your car permanently drives at 71mph set at 70mph, " +
        "lower this until correct on a flat road, or vice versa for the opposite problem."
      ),
      label_callback=lambda value: f"{value / 100:.1f}%",
      use_float_scaling=True,
    )

    self._live_learning_gas = toggle_item_sp(
      param="HondaLiveLearningGas",
      title=lambda: tr("Live Learning Gas (Default: OFF with Gas Interceptor)"),
      description=lambda: tr(
        "Allows Honda gas and wind compensation factors to learn live while driving. Fresh installs default OFF when a gas pedal " +
        "interceptor is detected and ON otherwise; your selection is preserved afterward."
      ),
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
      description=lambda: tr(
        "EXPERIMENTAL - Honda Bosch radar. When ON, openpilot reads the factory Bosch radar's fine-range objects (0x280) and treats this car " +
        "like a fingerprint-matched radar car (radarUnavailable=False + the custom honda_civic_bosch_radar DBC). If you ALSO enable openpilot " +
        "experimental/alpha longitudinal, this radar WILL feed openpilot's lead tracking and command braking/acceleration - exactly like a " +
        "matched car. With openpilot longitudinal OFF (stock ACC) it is perception only. The 0x280 decode is reverse-engineered and cross-car " +
        "validated (~0.99) but NOT verified on your specific car: before enabling openpilot longitudinal, VALIDATE that lead distance and " +
        "closing-rate match reality. Honda Civic Bosch only. Leave OFF if unsure."
      ),
    )

    self._dashboard_variant = toggle_item_sp(
      param="NrdrHondaDashVariantB",
      title=lambda: tr("Honda Dashboard Variant B (Default: OFF)"),
      description=lambda: tr(
        "Honda clusters round the cruise set-speed (km/h to mph) two different ways. Variant A (3 dashed lane lines drawn, the default) and " +
        "Variant B (4 dashed lane lines) round differently, so the same speed reads e.g. 60 on A vs 61 on B. Turn ON if your cluster is " +
        "Variant B. Placeholder for now - has no effect until the rounding correction is built."
      ),
    )

    return [
      self._long_pid_tune_scale,
      self._static_feedforward_long,
      self._ecu_matched_long,
      self._full_brake_authority,
      self._roen_acceleration_limits,
      self._cruise_overspeed_allowance,
      self._cruise_mismatch_correction,
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
      LineSeparatorSP(40),
      self._dashboard_variant,
    ]

  def _update_state(self):
    super()._update_state()
    self._live_learning_gas.action_item.set_enabled(ui_state.is_offroad())

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
