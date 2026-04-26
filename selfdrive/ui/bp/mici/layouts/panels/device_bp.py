"""BP Device panel — mirrors selfdrive/ui/mici/layouts/settings/device.py.

Reuses the existing dialogs (PairingDialog, DriverCameraDialog,
ReviewTrainingGuide, ReviewTermsPage, MiciFccModal, BigConfirmationDialog) so
the actions stay in lock-step with stock behavior. Param flips for the
destructive actions match stock.
"""
import os
import pyray as rl
from openpilot.common.basedir import BASEDIR
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.ui_state import ui_state, device

from openpilot.selfdrive.ui.mici.widgets.pairing_dialog import PairingDialog
from openpilot.selfdrive.ui.mici.onroad.driver_camera_dialog import DriverCameraDialog
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPConfirmDialog, BPInfoDialog
from openpilot.selfdrive.ui.mici.layouts.settings.device import (
  ReviewTrainingGuide, ReviewTermsPage, MiciFccModal,
)
from openpilot.system.ui.widgets.html_render import HtmlModal

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import StatCard, BigButtonCard


def _calibration_text() -> str:
  blob = ui_state.params.get("CalibrationParams")
  if not blob:
    return "-"
  # Stock writes a structured value; we just show "complete" when present.
  return "Complete"


def _paired_text() -> str:
  return "comma.ai" if ui_state.prime_state.is_paired() else "Not paired"


def _confirm(action_text: str, callback, icon_path: str, exit_on_confirm: bool = True, red: bool = False):
  """Stock-style: only fire if not engaged; show a slide-to-confirm dialog."""
  if ui_state.engaged:
    gui_app.push_widget(BPInfoDialog("Disengage first", f"Disengage to {action_text}."))
    return

  def on_confirm():
    if not ui_state.engaged:
      callback()

  gui_app.push_widget(BPConfirmDialog(
    f"slide to\n{action_text.lower()}",
    gui_app.texture(icon_path, 64, 64),
    on_confirm,
    exit_on_confirm=exit_on_confirm, red=red,
  ))


class DeviceLayoutBP(BPSubPanel):
  TITLE = "Device"

  def __init__(self, back_callback=None):
    self._fcc_dialog: HtmlModal | None = None
    super().__init__(back_callback=back_callback)

  # ---- callbacks ----
  def _open_pair(self):    gui_app.push_widget(PairingDialog())
  def _open_driver_cam(self): gui_app.push_widget(DriverCameraDialog())
  def _open_terms(self):   gui_app.push_widget(ReviewTermsPage())
  def _open_training(self):
    gui_app.push_widget(ReviewTrainingGuide(completed_callback=lambda: gui_app.pop_widgets_to(self)))

  def _open_regulatory(self):
    if not self._fcc_dialog:
      self._fcc_dialog = MiciFccModal(os.path.join(BASEDIR, "selfdrive/assets/offroad/mici_fcc.html"))
    gui_app.push_widget(self._fcc_dialog)

  def _reset_calibration(self):
    def go():
      params = ui_state.params
      params.remove("CalibrationParams")
      params.remove("LiveTorqueParameters")
      params.remove("LiveParameters")
      params.remove("LiveParametersV2")
      params.remove("LiveDelay")
      params.put_bool("OnroadCycleRequested", True)
    _confirm("reset calibration", go, "icons_mici/settings/device/lkas.png")

  def _reboot(self):
    _confirm("reboot", lambda: ui_state.params.put_bool("DoReboot", True),
             "icons_mici/settings/device/reboot.png", exit_on_confirm=False)

  def _power_off(self):
    _confirm("power off", lambda: ui_state.params.put_bool("DoShutdown", True),
             "icons_mici/settings/device/power.png", exit_on_confirm=False, red=True)

  def _uninstall(self):
    _confirm("uninstall", lambda: ui_state.params.put_bool("DoUninstall", True),
             "icons_mici/settings/device/uninstall.png", exit_on_confirm=False, red=True)

  # ---- pages ----
  def _build_pages(self):
    return [
      StatCard("Paired", _paired_text, variant="small"),
      StatCard("Calibration", _calibration_text, variant="small"),
      BigButtonCard("Pair Device",   icon="icons_mici/settings/comma_icon.png",         on_click=self._open_pair),
      BigButtonCard("Driver Camera", icon="icons_mici/settings/device/cameras.png",     on_click=self._open_driver_cam),
      BigButtonCard("Training Guide", icon="icons_mici/settings/device/info.png",        on_click=self._open_training),
      BigButtonCard("Terms",         icon="icons_mici/settings/device/info.png",         on_click=self._open_terms),
      BigButtonCard("Regulatory Info", icon="icons_mici/settings/device/info.png",       on_click=self._open_regulatory),
      BigButtonCard("Reset Calibration", icon="icons_mici/settings/device/lkas.png",     on_click=self._reset_calibration, danger=True),
      BigButtonCard("Uninstall",     icon="icons_mici/settings/device/uninstall.png",    on_click=self._uninstall, danger=True),
      BigButtonCard("Reboot",        icon="icons_mici/settings/device/reboot.png",       on_click=self._reboot),
      BigButtonCard("Power Off",     icon="icons_mici/settings/device/power.png",        on_click=self._power_off, danger=True),
    ]
