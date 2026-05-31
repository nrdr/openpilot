"""
nrdr experimental settings panel.
"""

from cereal import log
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP, ListItemSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.ui_state import ui_state


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    # Read-only display of openpilot's learned live parameters.
    self._lp_text = {
      "steerRatio": tr("learning…"),
      "stiffnessFactor": tr("learning…"),
      "angleOffsetAverageDeg": tr("learning…"),
      "angleOffsetDeg": tr("learning…"),
    }

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    # --- Read-only learned live parameters (top of panel) ---
    self._lp_steer_ratio = ListItemSP(
      title=lambda: f"{tr('Learned Steer Ratio')}: {self._lp_text['steerRatio']}",
    )
    self._lp_stiffness = ListItemSP(
      title=lambda: f"{tr('Learned Tire Stiffness Factor')}: {self._lp_text['stiffnessFactor']}",
    )
    self._lp_angle_avg = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Average)')}: {self._lp_text['angleOffsetAverageDeg']}",
    )
    self._lp_angle_inst = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Instant)')}: {self._lp_text['angleOffsetDeg']}",
    )

    # --- Tunable params ---
    self._lat_pid_tune_scale = option_item_sp(
      param="LatPidTuneScale",
      title=lambda: tr("Lateral PID Tune Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID controller values from their configured base tune."),
      label_callback=lambda value: f"{value}%",
    )

    self._center_scale = option_item_sp(
      param="HondaCenterScale",
      title=lambda: tr("Center Scale (Default: 0.50)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("High-speed center taper target; higher values increase on-center torque as speed rises."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._long_pid_tune_scale = option_item_sp(
      param="LongPidTuneScale",
      title=lambda: tr("Longitudinal PID Tune Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales longitudinal PID controller values from their configured base tune."),
      label_callback=lambda value: f"{value}%",
    )

    self._increase_override_tolerance = toggle_item_sp(
      param="NrdrIncreaseOverrideTolerance",
      title=lambda: tr("Increase Driver Override Tolerance (Default: ON)"),
      description=lambda: tr("Reduces the likelihood of false driver override detections on sensitive Honda EPS platforms."),
    )

    self._low_pass_filter = toggle_item_sp(
      param="HondaTorqueLowPassFilter",
      title=lambda: tr("Low Pass Filter (tau) (Default: ON)"),
      description=lambda: tr("Applies smoothing to requested steering torque."),
    )

    self._lpf_tau_low = option_item_sp(
      param="HondaLpfTauLowSpeed",
      title=lambda: tr("Low Speed Tau (Below 25mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) below 25 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_standard = option_item_sp(
      param="HondaLpfTauStandard",
      title=lambda: tr("Standard Tau (25-50mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) between 25 and 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_highway = option_item_sp(
      param="HondaLpfTauHighway",
      title=lambda: tr("Highway Tau (50mph+) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) above 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._driver_assist_during_override = toggle_item_sp(
      param="HondaDriverAssistDuringOverride",
      title=lambda: tr("Pass-through assist torque on override (Default: ON)"),
      description=lambda: tr("When ON, openpilot tells the EPS it is fully inactive (normal manual feel). When OFF, openpilot keeps sending standby messages to the EPS, which makes the steering feel more resistive."),
    )

    self._override_fade_down = option_item_sp(
      param="HondaOverrideFadeDownSecs",
      title=lambda: tr("Override Torque Fade Down (Default: 0.0)"),
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
      description=lambda: tr("Controls how much openpilot steering torque remains while the driver is overriding."),
      label_callback=lambda value: f"{value}%",
    )

    self._live_learning_gas = toggle_item_sp(
      param="HondaLiveLearningGas",
      title=lambda: tr("Live Learning Gas (Default: OFF)"),
      description=lambda: tr("Allows Honda gas and wind compensation factors to learn live while driving."),
    )

    self._steer_delta_limiter = toggle_item_sp(
      param="HondaSteerDeltaLimiter",
      title=lambda: tr("Steer Delta Rate Limiter (Default: OFF)"),
      description=lambda: tr("Limits how quickly requested steering torque can rise or fall."),
    )

    self._steer_delta_up = option_item_sp(
      param="HondaSteerDeltaUp",
      title=lambda: tr("Steer Delta Up (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum upward steering torque rate when the rate limiter is enabled."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._steer_delta_down = option_item_sp(
      param="HondaSteerDeltaDown",
      title=lambda: tr("Steer Delta Down (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum downward steering torque rate when the rate limiter is enabled."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._stopping_decel_rate = option_item_sp(
      param="HondaStoppingDecelRate",
      title=lambda: tr("Stopping Decel Rate (Default: 0.3)"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Controls the deceleration rate used while stopping."),
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

    return [
      self._lp_steer_ratio,
      self._lp_stiffness,
      self._lp_angle_avg,
      self._lp_angle_inst,
      LineSeparatorSP(40),
      self._lat_pid_tune_scale,
      self._center_scale,
      self._long_pid_tune_scale,
      LineSeparatorSP(40),
      self._increase_override_tolerance,
      LineSeparatorSP(40),
      self._low_pass_filter,
      self._lpf_tau_low,
      self._lpf_tau_standard,
      self._lpf_tau_highway,
      LineSeparatorSP(40),
      self._driver_assist_during_override,
      self._override_fade_down,
      self._override_fade_up,
      self._override_torque_scale,
      LineSeparatorSP(40),
      self._live_learning_gas,
      LineSeparatorSP(40),
      self._steer_delta_limiter,
      self._steer_delta_up,
      self._steer_delta_down,
      LineSeparatorSP(40),
      self._stopping_decel_rate,
      self._stop_accel,
      self._stopping_decel_rate_long,
      self._v_ego_stopping,
      self._v_ego_starting,
    ]

  def _refresh_live_params(self):
    vals = None
    try:
      if ui_state.started:
        lp = ui_state.sm['liveParameters']
        vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
      else:
        raw = ui_state.params.get("LiveParametersV2")
        if raw is not None:
          with log.Event.from_bytes(raw) as msg:
            lp = msg.liveParameters
            vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
    except Exception:
      vals = None

    if vals is None:
      self._lp_text = {k: tr("learning…") for k in self._lp_text}
    else:
      sr, sf, aoa, ao = vals
      self._lp_text = {
        "steerRatio": f"{sr:.2f}",
        "stiffnessFactor": f"{sf:.2f}",
        "angleOffsetAverageDeg": f"{aoa:.2f}°",
        "angleOffsetDeg": f"{ao:.2f}°",
      }

  def _update_state(self):
    super()._update_state()

    self._refresh_live_params()

    steer_delta_limiter_enabled = self._steer_delta_limiter.action_item.get_state()

    self._increase_override_tolerance.action_item.set_enabled(True)
    self._lat_pid_tune_scale.action_item.set_enabled(True)
    self._center_scale.action_item.set_enabled(True)
    self._long_pid_tune_scale.action_item.set_enabled(True)
    self._low_pass_filter.action_item.set_enabled(True)
    self._lpf_tau_low.action_item.set_enabled(True)
    self._lpf_tau_standard.action_item.set_enabled(True)
    self._lpf_tau_highway.action_item.set_enabled(True)
    self._override_torque_scale.action_item.set_enabled(True)
    self._steer_delta_limiter.action_item.set_enabled(True)
    self._steer_delta_up.action_item.set_enabled(True)
    self._steer_delta_down.action_item.set_enabled(True)

    # Live Learning Gas may only be changed offroad.
    self._live_learning_gas.action_item.set_enabled(ui_state.is_offroad())

    self._steer_delta_up.set_visible(steer_delta_limiter_enabled)
    self._steer_delta_down.set_visible(steer_delta_limiter_enabled)

    # Hide the tau sliders when the low-pass filter is disabled.
    lpf_enabled = self._low_pass_filter.action_item.get_state()
    self._lpf_tau_low.set_visible(lpf_enabled)
    self._lpf_tau_standard.set_visible(lpf_enabled)
    self._lpf_tau_highway.set_visible(lpf_enabled)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
