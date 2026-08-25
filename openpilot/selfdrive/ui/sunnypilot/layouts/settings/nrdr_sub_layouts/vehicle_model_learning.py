from collections.abc import Callable
import pyray as rl

from openpilot.cereal import log
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.nrdr.handcrafted_lateral import is_handcrafted_lateral_enabled
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, LineSeparatorSP, ListItemSP


class VehicleModelLearningLayout(Widget):
  def __init__(self, back_btn_callback: Callable, leading_items=()):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._lp_text = {
      "steerRatio": tr("learning..."),
      "stiffnessFactor": tr("learning..."),
      "angleOffsetAverageDeg": tr("learning..."),
      "angleOffsetDeg": tr("learning..."),
    }

    items = [*leading_items, LineSeparatorSP(40), *self._initialize_items()]
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lp_steer_ratio = ListItemSP(
      title=lambda: f"{tr('Learned Steer Ratio')}: {self._lp_text['steerRatio']}",
    )
    self._learn_steer_ratio = toggle_item_sp(
      param="NrdrLearnSteerRatio",
      title=lambda: tr("Learn Steer Ratio (Auto)"),
      description=lambda: tr("On uses the learned scalar on normal cars. Supported mapped Hondas use their configured " +
                             "On-Center anchor in both legacy and firmware-derived modes."),
      initial_state=False,
    )
    self._lp_stiffness = ListItemSP(
      title=lambda: f"{tr('Learned Tire Stiffness Factor')}: {self._lp_text['stiffnessFactor']}",
    )
    self._learn_stiffness = toggle_item_sp(
      param="NrdrLearnStiffness",
      title=lambda: tr("Learn Tire Stiffness (Auto)"),
      description=lambda: tr("When ON (Auto), uses the live-learned tire stiffness factor. When OFF, uses the static base value of 1.0."),
      initial_state=True,
    )
    self._lp_angle_avg = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Average)')}: {self._lp_text['angleOffsetAverageDeg']}",
    )
    self._lp_angle_inst = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Instant)')}: {self._lp_text['angleOffsetDeg']}",
    )
    self._learn_angle_offset = toggle_item_sp(
      param="NrdrLearnAngleOffset",
      title=lambda: tr("Learn Angle Offset (Auto)"),
      description=lambda: tr("When ON (Auto), uses the live-learned steering angle offset. When OFF, uses a static 0.0 offset. " +
                             "Turn OFF if a bad learned offset is pulling the car to one side."),
      initial_state=True,
    )

    return [
      self._lp_steer_ratio,
      self._learn_steer_ratio,
      self._lp_stiffness,
      self._learn_stiffness,
      self._lp_angle_avg,
      self._lp_angle_inst,
      self._learn_angle_offset,
    ]

  def _refresh_live_params(self):
    vals = None
    try:
      if ui_state.started:
        lp = ui_state.sm['vehicleParameters']
        vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
      else:
        raw = ui_state.params.get("LiveParametersV2")
        if raw is not None:
          with log.Event.from_bytes(raw) as msg:
            lp = msg.vehicleParameters
            vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
    except Exception:
      vals = None

    if vals is None:
      self._lp_text = {k: tr("learning...") for k in self._lp_text}
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
    fingerprint = str(ui_state.CP.carFingerprint) if ui_state.CP is not None else ""
    editable = not is_handcrafted_lateral_enabled(fingerprint, ui_state.params)
    for item in (self._learn_steer_ratio, self._learn_stiffness, self._learn_angle_offset):
      item.action_item.set_enabled(editable)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
