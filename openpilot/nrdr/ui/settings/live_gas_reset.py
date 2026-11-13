"""Native presentations of the same parked one-shot command used by Sunnylink."""
from openpilot.nrdr.car.live_gas_reset import REQUEST, STATUS, honda_fingerprint, request_reset
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr


def available():
  return bool(ui_state.is_offroad() and not ui_state.ignition and honda_fingerprint(ui_state.params, ui_state.CP)
              and not ui_state.params.get_bool(REQUEST))


def submit():
  if available():
    try:
      request_reset(ui_state.params, ui_state.CP)
    except (OSError, ValueError) as error:
      from openpilot.common.swaglog import cloudlog
      cloudlog.warning(f"Live gas reset request rejected: {error}")


def reset_description():
  return tr("Resets learned Honda gas and wind compensation without changing brake tuning. Resetting wind compensation may change when braking begins.")


def description():
  return reset_description() + " " + (ui_state.params.get(STATUS) or "")


def large_reset_button():
  from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp
  from openpilot.system.ui.widgets import DialogResult
  from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

  def confirm():
    if available():
      gui_app.push_widget(ConfirmDialog(tr("Clear this device's shared Honda gas and wind learning?"),
                                        tr("Reset"), tr("Cancel"), callback=lambda result: submit() if result == DialogResult.CONFIRM else None))

  return button_item_sp(lambda: tr("Reset Live Learning Gas"), lambda: tr("Reset"), description=description, callback=confirm, enabled=available)


def mici_reset_button():
  from openpilot.selfdrive.ui.mici.layouts.settings.device import EngagedConfirmationButton

  class GasResetButton(EngagedConfirmationButton):
    def _update_state(self):
      super()._update_state()
      status = ui_state.params.get(STATUS) or ""
      if status.startswith("Requested:") or status == "Resetting":
        label = tr("requested")
      elif status == "Reset complete.":
        label = tr("complete")
      else:
        label = tr("not complete") if status else ""
      if label != self.get_value():
        self.set_value(label)

  button = GasResetButton(tr("reset live gas"), tr("reset live gas"), gui_app.texture("icons_mici/settings/device/lkas.png", 122, 64),
                          submit, red=True, description=reset_description())
  button.set_enabled(available)
  return button
