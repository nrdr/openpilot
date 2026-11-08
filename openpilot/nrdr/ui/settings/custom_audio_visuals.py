from collections.abc import Callable
import pyray as rl

from openpilot.common.params import Params
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller


class CustomAudioVisualsLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._params = Params()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._engagement_sounds = multiple_button_item_sp(
      title=lambda: tr("Engagement Sounds"),
      description=lambda: tr(
        "Choose engage, disengage and engagement-refused sounds with their matching automatic volume. Other alerts are unchanged. " +
        "Applies to the next chime without reboot. Quiet Mode still mutes these sounds."
      ),
      buttons=[lambda: tr("Current"), lambda: tr("June 2026")],
      button_width=330,
      param="NrdrEngagementSoundPack",
    )
    self._scroller = Scroller([self._engagement_sounds], line_separator=False, spacing=0)

  def _render(self, rect):
    self._back_button.set_position(rect.x, rect.y + 20)
    self._back_button.render()
    top = self._back_button.rect.height + 40
    self._scroller.render(rl.Rectangle(rect.x, rect.y + top, rect.width, rect.height - top))

  def show_event(self):
    # Refresh on entry so remote changes are reflected without restarting UI.
    value = self._params.get("NrdrEngagementSoundPack", return_default=True)
    self._engagement_sounds.action_item.set_selected_button(1 if value == 1 else 0)
    self._scroller.show_event()

  def hide_event(self):
    self._scroller.hide_event()
