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

    self._alt_dashboard_speed = multiple_button_item_sp(
      title=lambda: tr("Alternative Dashboard Speed Design (Default: Stock)"),
      description=lambda: tr("Repurposes the cluster's set-speed slot (requires openpilot longitudinal). "
                            "Stock: normal set speed. "
                            "Lead Speed: the lead's speed in mph, always whole numbers (\"Stopped\" below 1 mph, \"--\" when no lead). "
                            "GPS Speed: the comma's own true speed. "
                            "Cluster Speed: exactly what the dash cluster reads."),
      buttons=[lambda: tr("Stock"), lambda: tr("Lead Speed"), lambda: tr("GPS Speed"), lambda: tr("Cluster Speed")],
      button_width=330,
      param="HondaAltDashboardSpeed",
    )

    self._alt_dashboard_distance = multiple_button_item_sp(
      title=lambda: tr("Alternative Dashboard Distance Design (Default: Stock)"),
      description=lambda: tr("Repurposes the cluster's distance bars / mini car (requires openpilot longitudinal). "
                            "Stock: normal personality bars while engaged. "
                            "Radar: the bars close in as the lead approaches. "
                            "Velocity: the bars push out under acceleration and pull in under braking. "
                            "Non-stock designs stay on the cluster permanently, even when not engaged."),
      buttons=[lambda: tr("Stock"), lambda: tr("Radar"), lambda: tr("Velocity")],
      button_width=330,
      param="HondaAltDashboardDistance",
    )

    self._distance_button_sub_mode = toggle_item_sp(
      param="NrdrDistanceButtonSubMode",
      title=lambda: tr("Distance Button Sub-Mode (Default: ON)"),
      description=lambda: tr("Dynamic HUD: pressing the distance button or set/resume first wakes a 15-second preview on the cluster - "
                            "the distance bars light up with your CURRENT personality (parked or driving, any design) and the set speed shows if cruise is engaged, all blinking. "
                            "Only presses made during the preview actually change the personality or set speed. "
                            "The blink speeds up over the final 10 and 5 seconds before it times out."),
    )

    return [
      self._injection_test,
      LineSeparatorSP(40),
      self._alt_dashboard_speed,
      self._alt_dashboard_distance,
      LineSeparatorSP(40),
      self._distance_button_sub_mode,
    ]

  def _update_state(self):
    super()._update_state()
    self._injection_test.action_item.set_enabled(True)
    self._alt_dashboard_speed.action_item.set_enabled(True)
    self._alt_dashboard_distance.action_item.set_enabled(True)
    self._distance_button_sub_mode.action_item.set_enabled(True)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
