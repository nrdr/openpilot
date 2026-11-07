from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import ListItem
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled, nrdr_longitudinal_enabled
from openpilot.nrdr.ui.settings.live_gas_reset import available as gas_reset_available, large_reset_button
from openpilot.nrdr.params.tuning_policy import MVL_DESCRIPTION, mvl_tuning_locked, tuning_write_allowed, legacy_pcm_active, legacy_pcm_tuning_locked
from openpilot.nrdr.params.nidec_pcm import PCM_EXPERIMENTS, PCM_EXPERIMENT_DETAILS
from openpilot.nrdr.params.mvl_pcm_deadzone import (
  MVL_PCM_DEADZONE_VALUES, MVL_PCM_DEADZONE_LABELS, MVL_PCM_DEADZONE_TITLE, MVL_PCM_DEADZONE_DESCRIPTION, MVL_PCM_DEADZONE_DETAILS,
)
from openpilot.nrdr.ui.honda_pcm import (pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice,
                                       live_gas_available, save_live_gas_choice,
                                       pcm_experiments_available, saved_pcm_experiment, save_pcm_experiment, pcm_experiment_status, live_gas_status,
                                       mvl_pcm_deadzone_available, saved_mvl_pcm_deadzone, save_mvl_pcm_deadzone)
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, multiple_button_item_sp, LineSeparatorSP


class LongitudinalTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._tuning_items = self._initialize_items()
    status = ListItem(
      title=lambda: (tr("Parked - saved settings apply next drive") if ui_state.is_offroad()
                     else tr("Legacy Kegman PCM active") if legacy_pcm_active(ui_state.CP)
                     else tr("Full MVL longitudinal active") if mvl_longitudinal_enabled(ui_state.CP)
                     else tr("Custom longitudinal active") if nrdr_longitudinal_enabled(ui_state.CP)
                     and getattr(ui_state.CP, "openpilotLongitudinalControl", False)
                     else tr("Baseline longitudinal - nrdr tuning inactive")),
      description=lambda: tr("Change while parked. Applies next drive; no device reboot. ")
                          + tr(live_gas_status(ui_state.CP, ui_state.params, ui_state.CP_SP,
                                               is_offroad=ui_state.is_offroad()).replace("\n", "; ")),
    )
    self._scroller = Scroller([status, *self._tuning_items], line_separator=False, spacing=0)

  def _initialize_items(self):
    self._standstill_gap = option_item_sp(
      param="NrdrStandstillGapExtra",
      title=lambda: tr("Extra Stopped Lead Gap (Default: 0 m)"),
      min_value=0, max_value=500, value_change_step=25, use_float_scaling=True,
      label_callback=lambda value: f"+{value / 100:.2f} m",
      description=lambda: tr(
        "Additional lead clearance retained through creeping and at a complete stop. " +
        "This adds to the planner's distance floor, not the distance-bar time gap. " +
        "0 preserves existing behavior. Measured bumper clearance can vary with lead sensing and braking. " +
        "Configure offroad; applies on the next engagement. Requires nrdr-supported openpilot longitudinal control."
      ),
    )
    self._long_pid_tune_scale_aggressive = option_item_sp(
      param="LongPidTuneScaleAggressive",
      title=lambda: tr("Distance 1 / Aggressive PID Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr(
        "Used with the Aggressive personality (distance setting 1). Effective only with a gas pedal interceptor and Live Learning Gas OFF; " +
        "otherwise longitudinal PID scaling is fixed at 100%."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._long_pid_tune_scale_standard = option_item_sp(
      param="LongPidTuneScaleStandard",
      title=lambda: tr("Distance 2 / Standard PID Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr(
        "Used with the Standard personality (distance setting 2). Effective only with a gas pedal interceptor and Live Learning Gas OFF; " +
        "otherwise longitudinal PID scaling is fixed at 100%."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._long_pid_tune_scale_relaxed = option_item_sp(
      param="LongPidTuneScaleRelaxed",
      title=lambda: tr("Distance 3 / Relaxed PID Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr(
        "Used with the Relaxed personality (distance setting 3). Effective only with a gas pedal interceptor and Live Learning Gas OFF; " +
        "otherwise longitudinal PID scaling is fixed at 100%."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._long_pid_tune_scale_econ = option_item_sp(
      param="LongPidTuneScaleEcon",
      title=lambda: tr("Distance 4 / Econ PID Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr(
        "Used with the Econ personality (distance setting 4). Effective only with a gas pedal interceptor and Live Learning Gas OFF; " +
        "otherwise longitudinal PID scaling is fixed at 100%."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._static_feedforward_long = toggle_item_sp(
      param="StaticFeedforwardLong",
      title=lambda: tr("Keep Feedforward Static (Default: OFF)"),
      description=lambda: tr("On: feedforward stays the same. Off: feedforward scales with the rest of the PID tune."),
    )

    self._pcm_mode = multiple_button_item_sp(
      title=lambda: tr("Honda Nidec: ECU-Matched PCM Command Shaping"),
      buttons=[lambda: tr("Off"), lambda: tr("ECU-Matched"), lambda: tr("Experimental")],
      button_width=300, callback=lambda value: save_pcm_choice(ui_state, "NrdrHondaPcmMode", value),
      description=lambda: tr(
        "Off uses upstream PCM control. ECU-Matched adds mmmorks' ramp, coast and brake-release rules. " +
        "Experimental uses the Civic trial. No gas interceptor. Change while parked. Applies next drive; no device reboot."
      ),
    )

    self._mvl_pcm_deadzone = multiple_button_item_sp(
      title=lambda: tr(MVL_PCM_DEADZONE_TITLE),
      buttons=[lambda label=label: tr(label) for label in MVL_PCM_DEADZONE_LABELS],
      button_width=160, callback=self._set_mvl_pcm_deadzone,
      description=lambda: tr(MVL_PCM_DEADZONE_DESCRIPTION) + " " + tr(MVL_PCM_DEADZONE_DETAILS),
    )

    self._pcm_experiments = {}
    for key, (title, description) in PCM_EXPERIMENTS.items():
      self._pcm_experiments[key] = multiple_button_item_sp(
        title=lambda title=title: tr(title),
        buttons=[lambda: tr("Off"), lambda: tr("On")], button_width=180,
        callback=lambda index, key=key: self._set_pcm_experiment(key, index),
        description=lambda key=key, description=description: tr(pcm_experiment_status(
          ui_state.CP, ui_state.CP_SP, ui_state.params, key, is_offroad=ui_state.is_offroad()))
                    + " " + tr(description) + " " + tr(PCM_EXPERIMENT_DETAILS[key]),
      )

    self._wind_brake = toggle_item_sp(
      title=lambda: tr("Wind Brake"), initial_state=True,
      callback=lambda value: save_pcm_choice(ui_state, "NrdrHondaWindBrake", value),
      description=lambda: tr(
        "Subtracts estimated wind drag from brake demand. PCM only; gas compensation is unchanged. " +
        "Change while parked. Applies next drive; no device reboot."
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
      title=lambda: tr("Roen Nidec Acceleration Limits (Default: OFF)"),
      description=lambda: tr(
        "Uses Roen's ISO-based planner and Nidec pedal-controller acceleration envelopes with full low-speed pedal scaling. " +
        "Saved while parked; ignored when MVL longitudinal is active."
      ),
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
      title=lambda: tr("Live Learning Gas - Full MVL Longitudinal"),
      initial_state=ui_state.params.get_bool("HondaLiveLearningGas"),
      description=lambda: tr(live_gas_status(ui_state.CP, ui_state.params, ui_state.CP_SP,
                                             is_offroad=ui_state.is_offroad()).replace("\n", "; ")) + ". " + tr(MVL_DESCRIPTION),
      callback=self._set_live_gas,
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
      param="HondaBoschARadar",
      title=lambda: tr("Honda Bosch-A Radar (Default: ON)"),
      description=lambda: tr(
        "EXPERIMENTAL - Decodes the factory radar on supported Honda Bosch-A vehicles with stock longitudinal or openpilot Alpha Long. " +
        "The reverse-engineered object format has not been road-validated on every supported model, so disable this setting if radar tracks " +
        "look incorrect. With Alpha Long, these tracks feed openpilot's lead tracking and longitudinal commands; factory Honda AEB/CMBS " +
        "remains unavailable."
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

    self._reset_live_gas = large_reset_button()
    return [
      self._live_learning_gas,
      *self._pcm_experiments.values(),
      self._reset_live_gas,
      self._mvl_pcm_deadzone,
      LineSeparatorSP(40),
      self._pcm_mode,
      self._wind_brake,
      self._static_feedforward_long,
      self._full_brake_authority,
      self._roen_acceleration_limits,
      self._radar_tryout,
      self._dashboard_variant,
      LineSeparatorSP(40),
      self._long_pid_tune_scale_aggressive,
      self._long_pid_tune_scale_standard,
      self._long_pid_tune_scale_relaxed,
      self._long_pid_tune_scale_econ,
      self._cruise_mismatch_correction,
      self._standstill_gap,
      self._stopping_decel_rate,
      self._stop_accel,
      self._stopping_decel_rate_long,
      self._v_ego_stopping,
      self._v_ego_starting,
    ]

  def _set_live_gas(self, value):
    # No param binding: ToggleSP otherwise writes after the guarded callback,
    # even when the vehicle became ineligible since the last display update.
    save_live_gas_choice(ui_state, value)
    self._live_learning_gas.action_item.set_state(ui_state.params.get_bool("HondaLiveLearningGas"))

  def _set_mvl_pcm_deadzone(self, index):
    if type(index) is int and 0 <= index < len(MVL_PCM_DEADZONE_VALUES):
      save_mvl_pcm_deadzone(ui_state, MVL_PCM_DEADZONE_VALUES[index])
    self._mvl_pcm_deadzone.action_item.set_selected_button(MVL_PCM_DEADZONE_VALUES.index(saved_mvl_pcm_deadzone(ui_state.params)))

  def _set_pcm_experiment(self, key, index):
    if type(index) is int and index in (0, 1):
      save_pcm_experiment(ui_state, key, bool(index))
    self._pcm_experiments[key].action_item.set_selected_button(int(saved_pcm_experiment(ui_state.params, key)))

  def _update_state(self):
    super()._update_state()
    enabled = nrdr_longitudinal_enabled(ui_state.CP)
    for item in self._tuning_items:
      if action := getattr(item, "action_item", None):
        action.set_enabled(enabled and tuning_write_allowed(ui_state.params, getattr(action, "param_key", None),
                                                           CP=ui_state.CP, CP_SP=ui_state.CP_SP, is_offroad=ui_state.is_offroad()))
    learning = not ui_state.is_offroad() and (mvl_tuning_locked(ui_state.params, ui_state.CP)
                                            or legacy_pcm_tuning_locked(ui_state.params, ui_state.CP, ui_state.CP_SP))
    for item in (self._long_pid_tune_scale_aggressive, self._long_pid_tune_scale_standard,
                 self._long_pid_tune_scale_relaxed, self._long_pid_tune_scale_econ):
      item.set_visible(not learning)
      item.action_item.set_enabled(enabled and not learning)
    self._live_learning_gas.action_item.set_enabled(
      ui_state.is_offroad() and live_gas_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self._live_learning_gas.action_item.set_state(ui_state.params.get_bool("HondaLiveLearningGas"))
    for key, item in self._pcm_experiments.items():
      item.action_item.set_enabled(ui_state.is_offroad() and pcm_experiments_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
      item.action_item.set_selected_button(int(saved_pcm_experiment(ui_state.params, key)))
    self._reset_live_gas.action_item.set_enabled(gas_reset_available())
    self._mvl_pcm_deadzone.action_item.set_enabled(
      ui_state.is_offroad() and mvl_pcm_deadzone_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self._mvl_pcm_deadzone.action_item.set_selected_button(MVL_PCM_DEADZONE_VALUES.index(saved_mvl_pcm_deadzone(ui_state.params)))
    pcm_available = pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
    pcm_enabled = ui_state.is_offroad() and pcm_available and not learning
    self._pcm_mode.action_item.set_enabled(pcm_enabled)
    self._wind_brake.action_item.set_enabled(pcm_enabled)
    self._pcm_mode.action_item.set_selected_button(saved_pcm_mode(ui_state.params))
    self._wind_brake.action_item.set_state(saved_wind_brake(ui_state.params))
    self._standstill_gap.action_item.set_enabled(
      enabled and not learning and ui_state.is_offroad() and bool(ui_state.CP and ui_state.CP.openpilotLongitudinalControl)
    )

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
