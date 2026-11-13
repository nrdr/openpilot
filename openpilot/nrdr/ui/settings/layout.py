from enum import IntEnum

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import simple_button_item_sp, option_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.hooks.driver_monitoring import monitoring_customization_available
from openpilot.nrdr.ui.settings.lateral_tuning import LateralTuningLayout, honda_tuning_available
from openpilot.nrdr.ui.settings.longitudinal_tuning import LongitudinalTuningLayout
from openpilot.nrdr.ui.settings.party_tricks import PartyTricksLayout
from openpilot.nrdr.ui.settings.custom_audio_visuals import CustomAudioVisualsLayout


class PanelType(IntEnum):
  NRDR = 0
  LATERAL = 1
  LONGITUDINAL = 2
  PARTY_TRICKS = 3
  CUSTOM_AUDIO_VISUALS = 4


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.NRDR
    self._shown = False
    self._lateral_layout = LateralTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._longitudinal_layout = LongitudinalTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._party_tricks_layout = PartyTricksLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._custom_audio_visuals_layout = CustomAudioVisualsLayout(lambda: self._set_current_panel(PanelType.NRDR))

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lateral_button = simple_button_item_sp(
      button_text=lambda: tr("Lateral Tuning"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LATERAL),
    )
    self._longitudinal_button = simple_button_item_sp(
      button_text=lambda: tr("Longitudinal Tuning"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LONGITUDINAL),
    )
    self._party_tricks_button = simple_button_item_sp(
      button_text=lambda: tr("Special"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.PARTY_TRICKS),
    )
    self._party_tricks_separator = LineSeparatorSP(40)
    self._honda_only_items = (self._party_tricks_separator, self._party_tricks_button)
    for item in self._honda_only_items:
      item.set_visible(False)

    self._monitoring_reminder = option_item_sp(
      title=lambda: tr("Driver Monitoring: First Reminder Timing"),
      param="NrdrDriverMonitoringReminderPercent",
      min_value=50, max_value=250, value_change_step=5,
      label_callback=lambda value: f"{value}%",
      description=lambda: tr("Adjusts the delay before the first attention reminder; 100% uses standard timing. " +
                             "Monitoring stays enabled with unchanged later-warning intervals; applies after reboot."),
      enabled=lambda: monitoring_customization_available() and ui_state.is_offroad(),
    )
    self._monitoring_reminder.set_visible(monitoring_customization_available)
    self._monitoring_separator = LineSeparatorSP(40)
    self._monitoring_separator.set_visible(monitoring_customization_available)

    self._custom_audio_visuals_button = simple_button_item_sp(
      button_text=lambda: tr("Custom Audio & Visuals"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.CUSTOM_AUDIO_VISUALS),
    )

    return [
      self._lateral_button,
      LineSeparatorSP(40),
      self._longitudinal_button,
      *self._honda_only_items,
      self._monitoring_separator,
      self._monitoring_reminder,
      LineSeparatorSP(40),
      self._custom_audio_visuals_button,
    ]

  def _panel_widget(self, panel: PanelType) -> Widget:
    if panel == PanelType.LATERAL:
      return self._lateral_layout
    if panel == PanelType.LONGITUDINAL:
      return self._longitudinal_layout
    if panel == PanelType.PARTY_TRICKS:
      return self._party_tricks_layout
    if panel == PanelType.CUSTOM_AUDIO_VISUALS:
      return self._custom_audio_visuals_layout
    return self._scroller

  def _set_current_panel(self, panel: PanelType):
    next_panel = PanelType.NRDR if panel == PanelType.PARTY_TRICKS and not honda_tuning_available() else panel
    if next_panel == self._current_panel:
      return
    if self._shown:
      self._panel_widget(self._current_panel).hide_event()
    self._current_panel = next_panel
    if self._shown:
      self._panel_widget(self._current_panel).show_event()

  def _update_state(self):
    super()._update_state()
    honda_available = honda_tuning_available()
    for item in self._honda_only_items:
      item.set_visible(honda_available)
    if self._current_panel == PanelType.PARTY_TRICKS and not honda_available:
      self._set_current_panel(PanelType.NRDR)

  def _render(self, rect):
    if self._current_panel == PanelType.LATERAL:
      self._lateral_layout.render(rect)
    elif self._current_panel == PanelType.LONGITUDINAL:
      self._longitudinal_layout.render(rect)
    elif self._current_panel == PanelType.PARTY_TRICKS:
      self._party_tricks_layout.render(rect)
    elif self._current_panel == PanelType.CUSTOM_AUDIO_VISUALS:
      self._custom_audio_visuals_layout.render(rect)
    else:
      self._scroller.render(rect)

  def show_event(self):
    if self._shown:
      return
    self._current_panel = PanelType.NRDR
    self._shown = True
    self._panel_widget(self._current_panel).show_event()

  def hide_event(self):
    if self._shown:
      self._panel_widget(self._current_panel).hide_event()
    self._shown = False
    self._current_panel = PanelType.NRDR
