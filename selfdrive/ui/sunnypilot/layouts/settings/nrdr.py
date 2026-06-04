"""
nrdr experimental settings panel.
"""
from enum import IntEnum

from cereal import log
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import simple_button_item_sp, LineSeparatorSP, ListItemSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.lateral_tuning import LateralTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.override_tuning import OverrideTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.longitudinal_tuning import LongitudinalTuningLayout


class PanelType(IntEnum):
  NRDR = 0
  LATERAL = 1
  OVERRIDE = 2
  LONGITUDINAL = 3


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.NRDR
    self._lateral_layout = LateralTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._override_layout = OverrideTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))
    self._longitudinal_layout = LongitudinalTuningLayout(lambda: self._set_current_panel(PanelType.NRDR))

    # Read-only display of openpilot's learned live parameters.
    self._lp_text = {
      "steerRatio": tr("learning…"),
      "stiffnessFactor": tr("learning…"),
      "angleOffsetAverageDeg": tr("learning…"),
      "angleOffsetDeg": tr("learning…"),
    }

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lp_steer_ratio = ListItemSP(
      title=lambda: f"{tr('Learned Steer Ratio')}: {self._lp_text['steerRatio']}",
    )
    self._lp_stiffness = ListItemSP(
      title=lambda: f"{tr('Learned Tire Stiffness Factor')}: {self._lp_text['stiffnessFactor']}",
    )
    self._lp_angle_avg = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Average)')}: {self._lp_text['angleOffsetAverageDeg']}",
    )
    self._lp_angle_inst = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Instant)')}: {self._lp_text['angleOffsetDeg']}",
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

    return [
      self._lp_steer_ratio,
      self._lp_stiffness,
      self._lp_angle_avg,
      self._lp_angle_inst,
      LineSeparatorSP(40),
      self._lateral_button,
      LineSeparatorSP(40),
      self._override_button,
      LineSeparatorSP(40),
      self._longitudinal_button,
    ]

  def _set_current_panel(self, panel: PanelType):
    self._current_panel = panel

  def _refresh_live_params(self):
    vals = None
    try:
      if ui_state.started:
        lp = ui_state.sm['liveParameters']
        vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
      else:
        raw = ui_state.params.get("LiveParametersV2")
        if raw is not None:
          with log.Event.from_bytes(raw) as msg:
            lp = msg.liveParameters
            vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
    except Exception:
      vals = None

    if vals is None:
      self._lp_text = {k: tr("learning…") for k in self._lp_text}
    else:
      sr, sf, aoa, ao = vals
      self._lp_text = {
        "steerRatio": f"{sr:.2f}",
        "stiffnessFactor": f"{sf:.2f}",
        "angleOffsetAverageDeg": f"{aoa:.2f}°",
        "angleOffsetDeg": f"{ao:.2f}°",
      }

  def _update_state(self):
    super()._update_state()
    self._refresh_live_params()

  def _render(self, rect):
    if self._current_panel == PanelType.LATERAL:
      self._lateral_layout.render(rect)
    elif self._current_panel == PanelType.OVERRIDE:
      self._override_layout.render(rect)
    elif self._current_panel == PanelType.LONGITUDINAL:
      self._longitudinal_layout.render(rect)
    else:
      self._scroller.render(rect)

  def show_event(self):
    self._set_current_panel(PanelType.NRDR)
    self._scroller.show_event()
