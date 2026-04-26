"""BP Firehose panel — short summary of training data uploads.

The stock FirehoseLayout is a long HTML scroll panel (Title + description +
FAQ). For MICI's small screen, we expose a couple of paged stat cards plus a
"learn more" jump back to the stock layout for users who want the full FAQ.
"""
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.mici.layouts.settings.firehose import FirehoseLayout

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import StatCard, BigButtonCard


def _segment_count() -> str:
  blob = Params().get("ApiCache_FirehoseStats")
  if not blob:
    return "0"
  try:
    return f"{int(blob.get('firehose', 0)):,}"
  except Exception:
    return "0"


class FirehoseLayoutBP(BPSubPanel):
  TITLE = "Firehose"

  def __init__(self, back_callback=None):
    self._stock_panel: FirehoseLayout | None = None
    super().__init__(back_callback=back_callback)

  def _open_full(self):
    if self._stock_panel is None:
      self._stock_panel = FirehoseLayout()
    gui_app.push_widget(self._stock_panel)

  def _build_pages(self):
    return [
      StatCard("Segments banked", _segment_count),
      StatCard("Status",          "Active", variant="small"),
      BigButtonCard("Learn more", on_click=self._open_full),
    ]
