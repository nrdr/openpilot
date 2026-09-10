from enum import IntEnum

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import simple_button_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.nrdr.ui.settings.lateral_tuning import LateralTuningLayout, honda_tuning_available
from openpilot.nrdr.ui.settings.longitudinal_tuning import LongitudinalTuningLayout
from openpilot.nrdr.ui.settings.party_tricks import PartyTricksLayout


class PanelType(IntEnum):
  NRDR = 0
  LATERAL = 1
  LONGITUDINAL = 2
  PARTY_TRICKS = 3


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.NRDR
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

  def _set_current_panel(self, panel: PanelType):
    self._current_panel = PanelType.NRDR if panel == PanelType.PARTY_TRICKS and not honda_tuning_available() else panel

  def _update_state(self):
    super()._update_state()
    honda_available = honda_tuning_available()
    for item in self._honda_only_items:
      item.set_visible(honda_available)
    if self._current_panel == PanelType.PARTY_TRICKS and not honda_available:
      self._current_panel = PanelType.NRDR

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
    self._set_current_panel(PanelType.NRDR)
    self._scroller.show_event()
