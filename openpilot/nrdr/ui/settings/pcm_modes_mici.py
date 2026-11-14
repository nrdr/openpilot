"""Compact longitudinal controls with the same saved-choice guards as tici."""
from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.params.longitudinal_controller import CONTROLLER_LABELS, CONTROLLER_DESCRIPTION, BOSCH_RADAR_WARNING
from openpilot.nrdr.ui.settings.pcm_speed_deadzone import PcmSpeedDeadzoneSlider
from openpilot.nrdr.ui.honda_pcm import (pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice,
                                       wind_brake_editable,
                                       live_gas_available, longitudinal_controller_choices,
                                       longitudinal_controller_label, save_longitudinal_controller)
from openpilot.nrdr.ui.settings.live_gas_reset import mici_reset_button
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiToggle, BigToggle
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.system.ui.lib.application import gui_app
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
                     description=tr("Adds coasting compensation on pedal cars; Off uses the gas request alone and leaves braking unchanged. "
                                    "On PCM cars, reduces braking for air resistance; Off removes that reduction."))
    self.set_enabled(lambda: wind_brake_editable(ui_state.CP, ui_state.CP_SP, ui_state.params, is_offroad=ui_state.is_offroad()))

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


class LongitudinalControllerControl(BigButton):
  def __init__(self):
    super().__init__(tr("Longitudinal Controller"), font_size=30, description=tr(CONTROLLER_DESCRIPTION))
    self.set_click_callback(self._show_choices)
    self.set_enabled(lambda: ui_state.is_offroad() and live_gas_available(ui_state.CP, ui_state.CP_SP, ui_state.params))
    self._refresh()

  def _refresh(self):
    self.set_value(tr(longitudinal_controller_label(ui_state)))

  def _show_choices(self):
    if not ui_state.is_offroad():
      return
    panel = NavScroller()
    for value in longitudinal_controller_choices(ui_state.CP, ui_state.CP_SP, ui_state.params):
      button = BigButton(tr(CONTROLLER_LABELS[value]), font_size=30,
                         description=tr(BOSCH_RADAR_WARNING if value == 2 else CONTROLLER_DESCRIPTION))

      def selected(choice=int(value)):
        if save_longitudinal_controller(ui_state, choice):
          self._refresh()
          gui_app.pop_widget()

      button.set_click_callback(selected)
      panel._scroller.add_widgets([button])
    gui_app.push_widget(panel)

  def _update_state(self):
    super()._update_state()
    self._refresh()


def longitudinal_controls():
  return [LongitudinalControllerControl(), mici_reset_button(), PcmModeControl(), WindBrakeControl(), StaticFeedforwardControl(), MvlPcmDeadzoneControl()]
