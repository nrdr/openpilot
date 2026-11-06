"""Compact longitudinal controls with the same saved-choice guards as tici."""
from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled
from openpilot.nrdr.params.tuning_policy import reset_learning_scales
from openpilot.nrdr.ui.honda_pcm import pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice
from openpilot.nrdr.ui.settings.live_gas_reset import mici_reset_button
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiToggle, BigParamControl, BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


class PcmModeControl(BigMultiToggle):
  PILL_TEXT_GAP = 12

  def __init__(self):
    self._labels = [tr("Off"), tr("ECU-Matched"), tr("Experimental")]
    super().__init__(tr("PCM Command Shaping"), self._labels,
                     select_callback=self._select, font_size=34,
                     description=tr("Honda Nidec: ECU-Matched PCM Command Shaping. " +
                                    "Off uses upstream PCM control. ECU-Matched adds mmmorks' ramp, coast and brake-release rules. " +
                                    "Experimental uses the Civic trial. No gas interceptor. Restart required."))
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self.set_value(self._labels[saved_pcm_mode(ui_state.params)])

  def _title_width_hint(self) -> int:
    # BigMultiToggle's three pills occupy the right column, but BigButton's
    # default text widths only account for an icon, not these pills.
    return max(1, int(self._rect.width - self.LABEL_HORIZONTAL_PADDING - self._txt_enabled_toggle.width - self.PILL_TEXT_GAP))

  def _subtitle_width_hint(self) -> int:
    return self._title_width_hint()

  def _select(self, label):
    save_pcm_choice(ui_state, "NrdrHondaPcmMode", self._labels.index(label))
    self.set_value(self._labels[saved_pcm_mode(ui_state.params)])

  def _update_state(self):
    super()._update_state()
    label = self._labels[saved_pcm_mode(ui_state.params)]
    if self.value != label:
      self.set_value(label)


class WindBrakeControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Wind Brake"), initial_state=saved_wind_brake(ui_state.params),
                     toggle_callback=self._select,
                     description=tr("Subtracts estimated wind drag from brake demand. PCM only; gas compensation is unchanged. Restart required."))
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params))

  def _select(self, value):
    save_pcm_choice(ui_state, "NrdrHondaWindBrake", value)
    self.set_checked(saved_wind_brake(ui_state.params))

  def _update_state(self):
    super()._update_state()
    self.set_checked(saved_wind_brake(ui_state.params))


class EngineBrakeControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Experimental Engine Braking"),
                     initial_state=ui_state.params.get_bool("NrdrExperimentalEngineBraking"),
                     toggle_callback=self._select, font_size=34,
                     description=tr("Civic PCM only. On fades the PCM speed request toward zero over 3 seconds; " +
                                    "Off still coasts within the allowance. Throttle recovers over 3 seconds. " +
                                    "Braking and pedal overrides take priority."))
    self.set_enabled(lambda: pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
                     and str(ui_state.CP.carFingerprint) == "HONDA_CIVIC")

  def _title_width_hint(self) -> int:
    return max(1, int(self._rect.width - self.LABEL_HORIZONTAL_PADDING - 84 - 12))

  def _select(self, value):
    save_pcm_choice(ui_state, "NrdrExperimentalEngineBraking", value)
    self.refresh()

  def refresh(self):
    self.set_checked(ui_state.params.get_bool("NrdrExperimentalEngineBraking"))

  def _update_state(self):
    super()._update_state()
    self.refresh()


class OverspeedAllowanceControl(BigButton):
  def __init__(self):
    super().__init__(tr("Set-Speed Overshoot Allowance"), font_size=30,
                     description=tr("Allows up to this much above set speed when no lower target applies. " +
                                    "Lead braking and other slowdown requests retain priority. " +
                                    "0 mph preserves stock behavior."))
    self.set_enabled(self._available)
    self.set_click_callback(self._show_choices)
    self.refresh()

  @staticmethod
  def _available():
    return ui_state.is_offroad() and nrdr_longitudinal_enabled(ui_state.CP)

  @staticmethod
  def _saved_value():
    value = ui_state.params.get("NrdrCruiseOverspeedAllowance")
    return value if type(value) is int and 0 <= value <= 10 else 0

  def refresh(self):
    label = f"{self._saved_value()} mph"
    if self.value != label:
      self.set_value(label)

  def _show_choices(self):
    if not self._available():
      return
    selector = NavScroller()
    for value in range(11):
      button = BigButton(f"{value} mph", value=tr("selected") if value == self._saved_value() else "")
      button.set_enabled(self._available)
      button.set_click_callback(lambda v=value: self._select(v))
      selector._scroller.add_widgets([button])
    gui_app.push_widget(selector)

  def _select(self, value):
    # Recheck at selection time: the vehicle may have changed since opening.
    if not self._available() or type(value) is not int or not 0 <= value <= 10:
      return
    ui_state.params.put("NrdrCruiseOverspeedAllowance", value, block=True)
    self.refresh()
    gui_app.pop_widget()

  def _update_state(self):
    super()._update_state()
    self.refresh()


class LiveGasControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Live Learning Gas"), initial_state=ui_state.params.get_bool("HondaLiveLearningGas"),
                     toggle_callback=self._select,
                     description=tr("Learns gas and wind compensation. Frozen in ECU-Matched and Civic Experimental. " +
                                    "When ON, longitudinal PID scales stay at 100%."))
    self.set_enabled(lambda: ui_state.is_offroad() and nrdr_longitudinal_enabled(ui_state.CP))

  def _select(self, value):
    if ui_state.is_offroad() and nrdr_longitudinal_enabled(ui_state.CP):
      ui_state.params.put_bool("HondaLiveLearningGas", value, block=True)
      if value:
        reset_learning_scales(ui_state.params)
    self.set_checked(ui_state.params.get_bool("HondaLiveLearningGas"))

  def _update_state(self):
    super()._update_state()
    self.set_checked(ui_state.params.get_bool("HondaLiveLearningGas"))


def longitudinal_controls():
  static = BigParamControl(tr("Keep Feedforward Static"), "StaticFeedforwardLong",
                           description=tr("On: feedforward stays the same. Off: feedforward scales with the rest of the PID tune."))
  static.set_enabled(lambda: nrdr_longitudinal_enabled(ui_state.CP))
  return [LiveGasControl(), mici_reset_button(), PcmModeControl(), WindBrakeControl(), static,
          EngineBrakeControl(), OverspeedAllowanceControl()]
