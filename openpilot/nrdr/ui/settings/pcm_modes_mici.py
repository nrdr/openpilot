"""Compact longitudinal controls with the same saved-choice guards as tici."""
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled, nrdr_longitudinal_enabled
from openpilot.nrdr.params.tuning_policy import MVL_DESCRIPTION, mvl_tuning_locked, tuning_write_allowed
from openpilot.nrdr.params.mvl_pcm_deadzone import (
  MVL_PCM_DEADZONE_VALUES, MVL_PCM_DEADZONE_LABELS, MVL_PCM_DEADZONE_TITLE, MVL_PCM_DEADZONE_DESCRIPTION, MVL_PCM_DEADZONE_DETAILS,
)
from openpilot.nrdr.ui.honda_pcm import (pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice,
                                       live_gas_available, save_live_gas_choice,
                                       mvl_pcm_deadzone_available, saved_mvl_pcm_deadzone, save_mvl_pcm_deadzone)
from openpilot.nrdr.ui.settings.live_gas_reset import mici_reset_button
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle, BigToggle
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
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
                     and not mvl_tuning_locked(ui_state.params, ui_state.CP))
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


class MvlPcmDeadzoneControl(BigMultiToggle):
  def __init__(self):
    self._labels = [tr(label) for label in MVL_PCM_DEADZONE_LABELS]
    super().__init__(tr(MVL_PCM_DEADZONE_TITLE), self._labels, select_callback=self._select, font_size=24,
                     description=tr(MVL_PCM_DEADZONE_DESCRIPTION) + " " + tr(MVL_PCM_DEADZONE_DETAILS))
    self.set_enabled(lambda: ui_state.is_offroad() and mvl_pcm_deadzone_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self.refresh()

  def _title_width_hint(self) -> int:
    return max(1, int(self._rect.width - self.LABEL_HORIZONTAL_PADDING - self._txt_enabled_toggle.width - 12))

  def _subtitle_width_hint(self) -> int:
    return self._title_width_hint()

  def _select(self, label):
    if label in self._labels:
      save_mvl_pcm_deadzone(ui_state, MVL_PCM_DEADZONE_VALUES[self._labels.index(label)])
    self.refresh()

  def refresh(self):
    self.set_value(self._labels[MVL_PCM_DEADZONE_VALUES.index(saved_mvl_pcm_deadzone(ui_state.params))])

  def _update_state(self):
    super()._update_state()
    self.refresh()


class WindBrakeControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Wind Brake"), initial_state=saved_wind_brake(ui_state.params),
                     toggle_callback=self._select,
                     description=tr("Subtracts estimated wind drag from brake demand. PCM only; gas compensation is unchanged. Restart required."))
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
                     and not mvl_tuning_locked(ui_state.params, ui_state.CP))

  def _select(self, value):
    save_pcm_choice(ui_state, "NrdrHondaWindBrake", value)
    self.set_checked(saved_wind_brake(ui_state.params))

  def _update_state(self):
    super()._update_state()
    self.set_checked(saved_wind_brake(ui_state.params))


class StaticFeedforwardControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Keep Feedforward Static"), initial_state=ui_state.params.get_bool("StaticFeedforwardLong"),
                     toggle_callback=self._select,
                     description=tr("On: feedforward stays the same. Off: feedforward scales with the rest of the PID tune."))
    self.set_enabled(self._available)

  @staticmethod
  def _available():
    return (nrdr_longitudinal_enabled(ui_state.CP)
            and tuning_write_allowed(ui_state.params, "StaticFeedforwardLong", CP=ui_state.CP))

  def _select(self, value):
    if type(value) is bool and self._available():
      ui_state.params.put_bool("StaticFeedforwardLong", value, block=True)
    self.refresh()

  def refresh(self):
    self.set_checked(ui_state.params.get_bool("StaticFeedforwardLong"))

  def _update_state(self):
    super()._update_state()
    self.refresh()


class LiveGasControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Live Learning Gas"), initial_state=ui_state.params.get_bool("HondaLiveLearningGas"),
                     toggle_callback=self._select, font_size=30,
                     description=tr(MVL_DESCRIPTION))
    self.set_enabled(lambda: ui_state.is_offroad() and live_gas_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self._refresh()

  def _title_width_hint(self) -> int:
    return max(1, int(self._rect.width - self.LABEL_HORIZONTAL_PADDING - self._txt_enabled_toggle.width - 12))

  @staticmethod
  def _mode_status():
    selected = ui_state.params.get_bool("HondaLiveLearningGas")
    if mvl_longitudinal_enabled(ui_state.CP):
      return tr("MVL active") if selected else tr("MVL active\nOFF after restart")
    return tr("MVL selected\nRestart required") if selected else tr("MVL inactive")

  def _refresh(self):
    self.set_checked(ui_state.params.get_bool("HondaLiveLearningGas"))
    self.set_value(self._mode_status())

  def _select(self, value):
    save_live_gas_choice(ui_state, value)
    self._refresh()

  def _update_state(self):
    super()._update_state()
    self._refresh()


def longitudinal_controls():
  return [LiveGasControl(), mici_reset_button(), PcmModeControl(), WindBrakeControl(), StaticFeedforwardControl(), MvlPcmDeadzoneControl()]
