from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp, toggle_item_sp


class SteerRatioTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._source = multiple_button_item_sp(
      title=lambda: tr("Primary Steer Ratio Source"), button_width=390,
      buttons=[lambda: tr("PTM (Auto)"), lambda: tr("Comma’s Learner (Legacy)")],
      callback=self._select_source,
      description=lambda: tr("PTM (Auto) uses the calibration for your steering firmware. Comma’s Learner estimates the ratio while driving."),
    )
    self._blend = toggle_item_sp(
      title=lambda: tr("Model-Specific Blend"), param="NrdrSteerRatioModelBlend",
      description=lambda: tr("Applies a model-specific steering-ratio adjustment. Off uses the PTM calibration unchanged."),
    )
    self._scroller = Scroller([self._source, self._blend], line_separator=False, spacing=0)

  @staticmethod
  def _select_source(index):
    if index not in (0, 1) or not tuning_write_allowed(ui_state.params, "NrdrSteerRatioMode",
                                                     CP=ui_state.CP, CP_SP=ui_state.CP_SP, is_offroad=ui_state.is_offroad()):
      return
    if index == 0 and (ui_state.CP is None or get_honda_vgr_profile(ui_state.CP) is None):
      return
    ui_state.params.put("NrdrSteerRatioMode", (3, 1)[index], block=True)

  def _update_state(self):
    super()._update_state()
    firmware = ui_state.CP is not None and get_honda_vgr_profile(ui_state.CP) is not None
    mode = ui_state.params.get("NrdrSteerRatioMode")
    self._source.action_item.set_selected_button(0 if mode == 3 else 1)
    self._source.action_item.set_enabled_buttons({0, 1} if firmware else {1})
    self._source.action_item.set_enabled(tuning_write_allowed(
      ui_state.params, "NrdrSteerRatioMode", CP=ui_state.CP, CP_SP=ui_state.CP_SP, is_offroad=ui_state.is_offroad()))
    self._blend.action_item.set_enabled(firmware and mode == 3 and tuning_write_allowed(
      ui_state.params, "NrdrSteerRatioModelBlend", CP=ui_state.CP, CP_SP=ui_state.CP_SP, is_offroad=ui_state.is_offroad()))

  def _render(self, rect):
    self._back_button.set_position(self._rect.x + 20, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()


__all__ = ("SteerRatioTuningLayout",)
