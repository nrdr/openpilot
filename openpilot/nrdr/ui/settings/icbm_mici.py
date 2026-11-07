"""Independent, parked-only factory ACC and ICBM choices for C4 Device."""
from opendbc.car.honda.values import CAR, HondaFlags

from openpilot.nrdr.ui.icbm import ICBM_DESCRIPTION, icbm_available, save_icbm_choice
from openpilot.selfdrive.ui.mici.widgets.button import BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr


def civic_factory_acc_available(CP, CP_SP) -> bool:
  return bool(CP is not None and CP_SP is not None and getattr(CP, "brand", "") == "honda"
              and getattr(CP, "carFingerprint", "") == CAR.HONDA_CIVIC
              and getattr(CP, "flags", 0) & HondaFlags.NIDEC and not (getattr(CP, "flags", 0) & HondaFlags.BOSCH)
              and not (getattr(CP, "passive", False) or getattr(CP, "dashcamOnly", False))
              and not getattr(CP_SP, "enableGasInterceptor", True))


def save_civic_factory_acc_choice(state, value) -> bool:
  if type(value) is not bool or not state.is_offroad() or not civic_factory_acc_available(state.CP, state.CP_SP):
    return False
  state.params.put_bool("HondaEnforceStockLongitudinal", value, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True


class StockCruiseControl(BigToggle):
  def __init__(self, key, title, description, available, save_choice):
    self._key, self._choice_available, self._save_choice = key, available, save_choice
    super().__init__(tr(title), initial_state=ui_state.params.get_bool(key), font_size=30,
                     toggle_callback=self._select, description=tr(description))
    self.set_enabled(lambda: ui_state.is_offroad() and self._choice_available(ui_state.CP, ui_state.CP_SP))
    self.refresh()

  def _title_width_hint(self) -> int:
    return max(1, int(self._rect.width - self.LABEL_HORIZONTAL_PADDING - self._txt_enabled_toggle.width - 12))

  def _subtitle_width_hint(self) -> int:
    return self._title_width_hint()

  def _select(self, value):
    self._save_choice(ui_state, value)
    self.refresh()

  def refresh(self):
    saved = ui_state.params.get_bool(self._key)
    self.set_checked(saved)
    # Saved choices do not prove that a cached controller is running this mode.
    self.set_value(tr("Saved: On") if saved else tr("Saved: Off"))

  def _update_state(self):
    super()._update_state()
    self.refresh()


def stock_cruise_controls():
  return [
    StockCruiseControl(
      "HondaEnforceStockLongitudinal", "Honda Factory ACC",
      "Honda Enforce Factory Longitudinal: factory ACC controls gas, brakes and following distance. " +
      "Civic only. Default Off; ICBM is separate. Saved tuning is kept. Change while parked. Applies next drive; no device reboot.",
      civic_factory_acc_available, save_civic_factory_acc_choice,
    ),
    StockCruiseControl(
      "IntelligentCruiseButtonManagement", "Cruise Buttons (ICBM)",
      ICBM_DESCRIPTION + " Default Off. Change while parked; factory ACC is never enabled automatically.",
      icbm_available, save_icbm_choice,
    ),
  ]
