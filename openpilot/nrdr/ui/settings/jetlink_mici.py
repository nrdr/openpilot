"""Compact counterpart of the nrdr Jetlink category."""
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiParamToggle, BigParamControl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.jetlink_adapter import KEYS, MODES
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


class JetlinkLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._link = BigMultiParamToggle(
      tr("Jetlink"), KEYS.link, [tr("Off"), "USB", "iOS"],
      description=tr("Runs big models on a compatible connected computer or phone. USB is for Mac, Jetson, Linux or Android; " +
                     "iOS is for iPhone or iPad. Requires companion setup and disables ADB. " +
                     "The small model runs until the big model is ready and is the fallback if the link fails. Change only while parked."),
    )
    self._link.set_enabled(lambda: ui_state.is_offroad())
    self._charge = BigParamControl(
      tr("Charge iPhone / iPad"), KEYS.charge_phone, font_size=30,
      description=tr("Allows charging the connected iOS device from the comma. This increases power use. Off disables phone charging."),
    )
    self._charge.set_visible(lambda: ui_state.params.get(KEYS.link) == MODES.index("ios"))
    self._charge.set_enabled(lambda: ui_state.is_offroad() and ui_state.params.get(KEYS.link) == MODES.index("ios"))
    self._scroller.add_widgets([self._link, self._charge])

  def _update_state(self):
    super()._update_state()
    self._link._load_value()
    self._charge.refresh()
