"""Parked Jetlink connection settings for the large-screen nrdr panel."""
from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.jetlink_adapter import KEYS, MODES
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp, toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller


class JetlinkLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._link = multiple_button_item_sp(
      title=tr("Jetlink Connection"), param=KEYS.link, buttons=[tr("Off"), "USB", "iOS"],
      description=tr("Runs big models on a compatible connected computer or phone. USB is for Mac, Jetson, Linux or Android; " +
                     "iOS is for iPhone or iPad. Requires companion setup and disables ADB. " +
                     "The small model runs until the big model is ready and is the fallback if the link fails. Change only while parked."),
    )
    self._charge = toggle_item_sp(
      title=tr("Charge iPhone / iPad"), param=KEYS.charge_phone,
      description=tr("Allows charging the connected iOS device from the comma. This increases power use. Off disables phone charging."),
    )
    self._scroller = Scroller([self._link, self._charge], line_separator=True)

  def _update_state(self):
    super()._update_state()
    self._link.action_item.selected_button = ui_state.params.get(KEYS.link, return_default=True)
    self._charge.action_item.set_state(ui_state.params.get_bool(KEYS.charge_phone))
    self._link.action_item.set_enabled(ui_state.is_offroad())
    ios = ui_state.params.get(KEYS.link) == MODES.index("ios")
    self._charge.set_visible(ios)
    self._charge.action_item.set_enabled(ui_state.is_offroad() and ios)

  def _render(self, rect):
    self._back_button.set_position(rect.x, rect.y + 20)
    self._back_button.render()
    offset = self._back_button.rect.height + 40
    self._scroller.render(rl.Rectangle(rect.x, rect.y + offset, rect.width, rect.height - offset))

  def show_event(self):
    self._scroller.show_event()

  def hide_event(self):
    self._scroller.hide_event()
