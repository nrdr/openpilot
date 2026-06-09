"""
nrdr experimental settings panel.
"""
from enum import IntEnum

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import simple_button_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.learned_parameters import LearnedParametersLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.lateral_tuning import LateralTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.override_tuning import OverrideTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.longitudinal_tuning import LongitudinalTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.party_tricks import PartyTricksLayout


class PanelType(IntEnum):
  NRDR = 0
  LATERAL = 1
  OVERRIDE = 2
  LONGITUDINAL = 3
  PARTY_TRICKS = 4
  LEARNED = 5


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.NRDR
    self._learned_params_layout = LearnedParametersLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._lateral_layout = LateralTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._override_layout = OverrideTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._longitudinal_layout = LongitudinalTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._party_tricks_layout = PartyTricksLayout(lambda: self._set_current_panel(PanelType.NRDR))

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._learned_button = simple_button_item_sp(
      button_text=lambda: tr("Learned Parameters"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LEARNED),
    )
    self._lateral_button = simple_button_item_sp(
      button_text=lambda: tr("Lateral Tuning"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LATERAL),
    )
    self._override_button = simple_button_item_sp(
      button_text=lambda: tr("Override Tuning"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.OVERRIDE),
    )
    self._longitudinal_button = simple_button_item_sp(
      button_text=lambda: tr("Longitudinal Tuning"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LONGITUDINAL),
    )
    self._party_tricks_button = simple_button_item_sp(
      button_text=lambda: tr("Party Tricks"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.PARTY_TRICKS),
    )

    return [
      self._learned_button,
      LineSeparatorSP(40),
      self._lateral_button,
      LineSeparatorSP(40),
      self._override_button,
      LineSeparatorSP(40),
      self._longitudinal_button,
      LineSeparatorSP(40),
      self._party_tricks_button,
    ]

  def _set_current_panel(self, panel: PanelType):
    self._current_panel = panel

  def _render(self, rect):
    if self._current_panel == PanelType.LEARNED:
      self._learned_params_layout.render(rect)
    elif self._current_panel == PanelType.LATERAL:
      self._lateral_layout.render(rect)
    elif self._current_panel == PanelType.OVERRIDE:
      self._override_layout.render(rect)
    elif self._current_panel == PanelType.LONGITUDINAL:
      self._longitudinal_layout.render(rect)
    elif self._current_panel == PanelType.PARTY_TRICKS:
      self._party_tricks_layout.render(rect)
    else:
      self._scroller.render(rect)

  def show_event(self):
    self._set_current_panel(PanelType.NRDR)
    self._scroller.show_event()
