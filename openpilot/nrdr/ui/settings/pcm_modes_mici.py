"""Compact longitudinal controls with the same saved-choice guards as tici."""
from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled
from openpilot.nrdr.params.tuning_policy import reset_learning_scales
from openpilot.nrdr.ui.honda_pcm import pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice
from openpilot.nrdr.ui.settings.live_gas_reset import mici_reset_button
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle, BigParamControl, BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr


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
  return [LiveGasControl(), mici_reset_button(), PcmModeControl(), WindBrakeControl(), static]
