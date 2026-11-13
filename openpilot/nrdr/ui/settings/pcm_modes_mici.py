"""Compact longitudinal controls with the same saved-choice guards as tici."""
from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled
from openpilot.nrdr.params.tuning_policy import MVL_DESCRIPTION, tuning_write_allowed
from openpilot.nrdr.ui.settings.pcm_speed_deadzone import PcmSpeedDeadzoneSlider
from openpilot.nrdr.ui.honda_pcm import (pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice,
                                       live_gas_available, save_live_gas_choice,
                                       live_gas_status)
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
                     description=tr("Adjusts PCM acceleration and the transition to braking; Off restores standard control. Experimental " +
                         "supports Civic MVL learning and bypasses Wind Brake without changing its saved setting."))
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
                     and tuning_write_allowed(ui_state.params, "NrdrHondaPcmMode", CP=ui_state.CP, CP_SP=ui_state.CP_SP,
                                              is_offroad=ui_state.is_offroad()))
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


class MvlPcmDeadzoneControl(PcmSpeedDeadzoneSlider):
  def __init__(self):
    super().__init__(compact=True)


class WindBrakeControl(BigToggle):
  def __init__(self):
    super().__init__(tr("Wind Brake"), initial_state=saved_wind_brake(ui_state.params),
                     toggle_callback=self._select,
                     description=tr("Reduces brake demand to account for estimated air resistance. Off removes this compensation; " +
                         "Experimental PCM shaping ignores it without changing your saved choice."))
    self.set_enabled(lambda: ui_state.is_offroad() and pcm_tuning_available(ui_state.CP, ui_state.CP_SP, ui_state.params)
                     and tuning_write_allowed(ui_state.params, "NrdrHondaWindBrake", CP=ui_state.CP, CP_SP=ui_state.CP_SP,
                                              is_offroad=ui_state.is_offroad()))

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
                     description=tr("Keeps feedforward strength unchanged when adjusting the PID scale. Off scales feedforward with the rest of the tune."))
    self.set_enabled(self._available)

  @staticmethod
  def _available():
    return (nrdr_longitudinal_enabled(ui_state.CP)
            and tuning_write_allowed(ui_state.params, "StaticFeedforwardLong", CP=ui_state.CP, CP_SP=ui_state.CP_SP,
                                     is_offroad=ui_state.is_offroad()))

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
    return tr(live_gas_status(ui_state.CP, ui_state.params, ui_state.CP_SP, is_offroad=ui_state.is_offroad()))

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
