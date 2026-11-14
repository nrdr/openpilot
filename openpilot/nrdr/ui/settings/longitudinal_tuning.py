from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import ListItem
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled, nrdr_longitudinal_enabled
from openpilot.nrdr.ui.settings.live_gas_reset import available as gas_reset_available, large_reset_button
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.params.longitudinal_controller import CONTROLLER_LABELS, CONTROLLER_DESCRIPTION, BOSCH_RADAR_WARNING
from openpilot.nrdr.ui.settings.pcm_speed_deadzone import speed_deadzone_item
from openpilot.nrdr.ui.honda_pcm import (pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice,
                                       wind_brake_editable,
                                       live_gas_available, longitudinal_controller_choices,
                                       longitudinal_controller_label, save_longitudinal_controller,
                                       live_gas_status,
                                       mvl_pcm_deadzone_available)
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp, toggle_item_sp, option_item_sp, multiple_button_item_sp, LineSeparatorSP
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog


class LongitudinalTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._tuning_items = self._initialize_items()
    status = ListItem(
      title=lambda: (tr("Parked - controller changes apply next drive") if ui_state.is_offroad()
                     else tr("Full MVL longitudinal active") if mvl_longitudinal_enabled(ui_state.CP)
                     else tr("Custom longitudinal active") if nrdr_longitudinal_enabled(ui_state.CP)
                     and getattr(ui_state.CP, "openpilotLongitudinalControl", False)
                     else tr("Baseline longitudinal - nrdr tuning inactive")),
      description=lambda: tr("Controller changes apply next drive. ")
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
        "Adds space behind the vehicle ahead while creeping or stopped. Zero keeps the normal gap without changing the selected following-time profile."
      ),
    )
    self._long_pid_tune_scale_aggressive = option_item_sp(
      param="LongPidTuneScaleAggressive",
      title=lambda: tr("Distance 1 / Aggressive PID Scale (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr(
        "Adjusts Standard-controller pedal feedback for Aggressive; 100% keeps the base tune. Personal Pedal uses fixed gains."
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
        "Adjusts Standard-controller pedal feedback for the Standard personality; 100% keeps the base tune. Personal Pedal uses fixed gains."
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
        "Adjusts Standard-controller pedal feedback for Relaxed; 100% keeps the base tune. Personal Pedal uses fixed gains."
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
        "Adjusts Standard-controller pedal feedback for Econ; 100% keeps the base tune. Personal Pedal uses fixed gains."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._static_feedforward_long = toggle_item_sp(
      param="StaticFeedforwardLong",
      title=lambda: tr("Keep Feedforward Static (Default: OFF)"),
      description=lambda: tr("Keeps feedforward strength unchanged when adjusting the PID scale. Off scales feedforward with the rest of the tune."),
    )

    self._pcm_mode = multiple_button_item_sp(
      title=lambda: tr("Honda Nidec: ECU-Matched PCM Command Shaping"),
      buttons=[lambda: tr("Off"), lambda: tr("ECU-Matched"), lambda: tr("Experimental")],
      button_width=300, callback=lambda value: save_pcm_choice(ui_state, "NrdrHondaPcmMode", value),
      description=lambda: tr(
        "Adjusts PCM acceleration and the transition to braking; Off restores standard control. Experimental " +
            "supports Civic MVL learning and bypasses Wind Brake without changing its saved setting."
      ),
    )

    self._mvl_pcm_deadzone = speed_deadzone_item()

    self._wind_brake = toggle_item_sp(
      title=lambda: tr("Wind Brake"), initial_state=True,
      callback=lambda value: save_pcm_choice(ui_state, "NrdrHondaWindBrake", value),
      description=lambda: tr(
        "Adds coasting compensation on pedal cars; Off uses the gas request alone and leaves braking unchanged. "
        "On PCM cars, reduces braking for air resistance; Off removes that reduction."
      ),
    )

    self._full_brake_authority = toggle_item_sp(
      param="NrdrHondaFullBrakeAuthority",
      title=lambda: tr("Full Nidec Brake Authority (Default: ON)"),
      description=lambda: tr(
        "Allows the full available brake-command range. Off restores the standard brake-command limit."
      ),
    )

    self._roen_acceleration_limits = toggle_item_sp(
      param="NrdrRoenAccelerationLimits",
      title=lambda: tr("Roen Nidec Acceleration Limits (Default: OFF)"),
      description=lambda: tr(
        "Uses Roen's acceleration limits and full low-speed pedal response with Standard control. Off restores the normal acceleration limits."
      ),
    )

    self._cruise_mismatch_correction = option_item_sp(
      param="NrdrCruiseMismatchCorrection",
      title=lambda: tr("Cruise Mismatch Correction (Default: 100.0%)"),
      min_value=9500,
      max_value=10500,
      value_change_step=10,
      description=lambda: tr(
        "Adjusts the cruise target when the car consistently drives above or below the set speed. Lower the " +
            "value if it runs too fast; raise it if it runs too slowly."
      ),
      label_callback=lambda value: f"{value / 100:.1f}%",
      use_float_scaling=True,
    )

    self._controller_dialog = None
    self._longitudinal_controller = button_item_sp(
      title=lambda: tr("Longitudinal Controller"),
      button_text=lambda: tr(longitudinal_controller_label(ui_state)),
      description=lambda: tr(CONTROLLER_DESCRIPTION) + (" " + tr(BOSCH_RADAR_WARNING) if 2 in
        longitudinal_controller_choices(ui_state.CP, ui_state.CP_SP, ui_state.params) else ""),
      callback=self._show_controller_selector,
    )

    self._stopping_decel_rate = option_item_sp(
      param="HondaStoppingDecelRate",
      title=lambda: tr("Stopping Decel Rate (Default: 0.3)"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Limits how quickly braking builds as the car comes to a stop."),
      label_callback=lambda value: f"{value / 100:.2f}",
    )

    self._stop_accel = option_item_sp(
      param="HondaStopAccel",
      title=lambda: tr("Stop Accel (Default: -2.0)"),
      min_value=-400,
      max_value=0,
      value_change_step=1,
      description=lambda: tr("Sets the braking target used to hold the car at a stop."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._stopping_decel_rate_long = option_item_sp(
      param="HondaStoppingDecelRateLong",
      title=lambda: tr("Planner Stopping Rate (Default: 0.3)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Sets how quickly the planned braking target increases when stopping."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._v_ego_stopping = option_item_sp(
      param="HondaVEgoStopping",
      title=lambda: tr("vEgo Stopping (Default: 0.5)"),
      min_value=0,
      max_value=300,
      value_change_step=1,
      description=lambda: tr("Sets the speed below which stopping control takes over, in m/s."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._v_ego_starting = option_item_sp(
      param="HondaVEgoStarting",
      title=lambda: tr("vEgo Starting (Default: 0.5)"),
      min_value=0,
      max_value=300,
      value_change_step=1,
      description=lambda: tr("Sets the speed above which the car is treated as moving again, in m/s."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._dashboard_variant = toggle_item_sp(
      param="NrdrHondaDashVariantB",
      title=lambda: tr("Honda Dashboard Variant B (Default: OFF)"),
      description=lambda: tr(
        "Saves the dashboard variant with four dashed lane lines. This setting currently has no effect."
      ),
    )

    self._reset_live_gas = large_reset_button()
    return [
      self._longitudinal_controller,
      self._reset_live_gas,
      self._mvl_pcm_deadzone,
      LineSeparatorSP(40),
      self._pcm_mode,
      self._wind_brake,
      self._static_feedforward_long,
      self._full_brake_authority,
      self._roen_acceleration_limits,
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

  def _show_controller_selector(self):
    if not ui_state.is_offroad():
      return
    choices = longitudinal_controller_choices(ui_state.CP, ui_state.CP_SP, ui_state.params)
    labels = [tr(CONTROLLER_LABELS[value]) for value in choices]

    def selected(result):
      dialog, self._controller_dialog = self._controller_dialog, None
      if result == DialogResult.CONFIRM and dialog is not None and dialog.selection in labels:
        save_longitudinal_controller(ui_state, int(choices[labels.index(dialog.selection)]))

    self._controller_dialog = MultiOptionDialog(tr("Longitudinal Controller"), labels,
                                                tr(longitudinal_controller_label(ui_state)), callback=selected)
    gui_app.push_widget(self._controller_dialog)

  def _update_state(self):
    super()._update_state()
    enabled = nrdr_longitudinal_enabled(ui_state.CP)
    for item in self._tuning_items:
      if action := getattr(item, "action_item", None):
        action.set_enabled(enabled and tuning_write_allowed(ui_state.params, getattr(action, "param_key", None),
                                                           CP=ui_state.CP, CP_SP=ui_state.CP_SP, is_offroad=ui_state.is_offroad()))
    self._longitudinal_controller.action_item.set_enabled(
      ui_state.is_offroad() and live_gas_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self._reset_live_gas.action_item.set_enabled(gas_reset_available())
    self._mvl_pcm_deadzone.action_item.set_enabled(
      ui_state.is_offroad() and mvl_pcm_deadzone_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    pcm_available = pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
    pcm_enabled = ui_state.is_offroad() and pcm_available
    self._pcm_mode.action_item.set_enabled(pcm_enabled)
    self._wind_brake.action_item.set_enabled(
      wind_brake_editable(ui_state.CP, ui_state.CP_SP, ui_state.params, is_offroad=ui_state.is_offroad()))
    self._pcm_mode.action_item.set_selected_button(saved_pcm_mode(ui_state.params))
    self._wind_brake.action_item.set_state(saved_wind_brake(ui_state.params))
    self._standstill_gap.action_item.set_enabled(
      enabled and ui_state.is_offroad() and bool(ui_state.CP and ui_state.CP.openpilotLongitudinalControl)
    )

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
