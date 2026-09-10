from enum import IntEnum

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import simple_button_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.lateral_tuning import LateralTuningLayout, honda_tuning_available
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.longitudinal_tuning import LongitudinalTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.party_tricks import PartyTricksLayout


class PanelType(IntEnum):
  NRDR = 0
  LATERAL = 1
  LONGITUDINAL = 2
  PARTY_TRICKS = 3


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.NRDR
    self._shown = False
    self._lateral_layout = LateralTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._longitudinal_layout = LongitudinalTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._party_tricks_layout = PartyTricksLayout(lambda: self._set_current_panel(PanelType.NRDR))

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

    return [
      self._lateral_button,
      LineSeparatorSP(40),
      self._longitudinal_button,
      *self._honda_only_items,
    ]

  def _panel_widget(self, panel: PanelType) -> Widget:
    if panel == PanelType.LATERAL:
      return self._lateral_layout
    if panel == PanelType.LONGITUDINAL:
      return self._longitudinal_layout
    if panel == PanelType.PARTY_TRICKS:
      return self._party_tricks_layout
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
