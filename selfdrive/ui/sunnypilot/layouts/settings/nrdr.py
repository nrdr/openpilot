"""
nrdr experimental settings panel.
"""

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.ui_state import ui_state


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._increase_override_tolerance = toggle_item_sp(
      param="NrdrIncreaseOverrideTolerance",
      title=lambda: tr("Increase Driver Override Tolerance"),
      description=lambda: tr("Reduces the likelihood of false driver override detections on sensitive Honda EPS platforms."),
    )

    return [
      self._increase_override_tolerance,
    ]

  def _update_state(self):
    super()._update_state()

    self._increase_override_tolerance.action_item.set_enabled(ui_state.is_offroad())

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()