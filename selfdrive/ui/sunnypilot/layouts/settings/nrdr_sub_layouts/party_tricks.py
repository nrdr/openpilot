"""
nrdr Party Tricks sub-panel: fun / experimental dashboard and diagnostic toggles.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp, LineSeparatorSP


class PartyTricksLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._injection_test = toggle_item_sp(
      param="HondaInjectionTest",
      title=lambda: tr("Injection Test (Caution!) (Default: OFF)"),
      description=lambda: tr("When enabled, the lateral PID output scale is multiplied by 999%. This is a diagnostic stress test to see how the car reacts to a massive steering command. Use with extreme caution on a safe, empty road."),
    )

    self._alt_dashboard = multiple_button_item_sp(
      title=lambda: tr("Alternative Dashboard UI Design (Default: Stock)"),
      description=lambda: tr("Repurposes the factory ACC cluster (requires openpilot longitudinal). "
                            "Stock: normal display. "
                            "Lead Information: the distance bars close in as the lead approaches and the lead's speed shows in place of your set speed (\"Stopped\" below 1 mph, \"--\" when no lead). Best on radar cars. "
                            "Vehicle Information: shows your own speed, with the bars pushing out under acceleration and pulling in under braking. Good when there's no useful lead."),
      buttons=[lambda: tr("Stock"), lambda: tr("Lead Information"), lambda: tr("Vehicle Information")],
      button_width=420,
      param="HondaAltDashboard",
    )

    return [
      self._injection_test,
      LineSeparatorSP(40),
      self._alt_dashboard,
    ]

  def _update_state(self):
    super()._update_state()
    self._injection_test.action_item.set_enabled(True)
    self._alt_dashboard.action_item.set_enabled(True)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
