"""BP Developer panel — mirrors selfdrive/ui/mici/layouts/settings/developer.py.

Same param keys; same SSH-keys flow (delegates to existing SshKeyFetcher and
the BigInputDialog). One-per-page layout with mono ID stat cards on top.
"""
from openpilot.common.time_helpers import system_time_valid
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPInfoDialog, BPInputDialog
from openpilot.selfdrive.ui.widgets.ssh_key import SshKeyFetcher

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import (
  StatCard, BigToggleCard, BigButtonCard,
)


def _dongle_id() -> str:
  return (ui_state.params.get("DongleId") or "-").strip()


def _serial() -> str:
  return (ui_state.params.get("HardwareSerial") or "-").strip()


class DeveloperLayoutBP(BPSubPanel):
  TITLE = "Developer"

  def __init__(self, back_callback=None):
    self._ssh_fetcher = SshKeyFetcher(ui_state.params)
    super().__init__(back_callback=back_callback)

  def _open_ssh_keys(self):
    if not system_time_valid():
      gui_app.push_widget(BPInfoDialog("Wi-Fi required", "Connect to Wi-Fi to fetch your key."))
      return

    current = ui_state.params.get("GithubUsername") or ""

    def on_username(username: str):
      if not username:
        self._ssh_fetcher.clear()
        return

      def on_response(error):
        if error is not None:
          gui_app.push_widget(BPInfoDialog("SSH key error", error))

      self._ssh_fetcher.fetch(username, on_response)

    gui_app.push_widget(BPInputDialog(
      "enter GitHub username...", current, minimum_length=0, confirm_callback=on_username,
    ))

  def _on_debug_toggle(self, on: bool):
    gui_app.set_show_touches(on)
    gui_app.set_show_fps(on)

  def _build_pages(self):
    return [
      StatCard("Dongle ID", _dongle_id, variant="mono"),
      StatCard("Serial",    _serial,    variant="mono"),
      BigToggleCard("Enable ADB", "Remote shell over USB.", param_key="AdbEnabled"),
      BigToggleCard("Enable SSH", "Allow SSH connections to the device.", param_key="SshEnabled"),
      BigButtonCard("SSH Keys", on_click=self._open_ssh_keys),
      BigToggleCard("Joystick Debug Mode", "Manually drive the actuators with a joystick.",
                    param_key="JoystickDebugMode"),
      BigToggleCard("Longitudinal Maneuver Mode", "Run scripted long maneuvers offroad.",
                    param_key="LongitudinalManeuverMode"),
      BigToggleCard("Lateral Maneuver Mode", "Run scripted lat maneuvers offroad.",
                    param_key="LateralManeuverMode"),
      BigToggleCard("Alpha Longitudinal", "Enable in-development longitudinal control.",
                    param_key="AlphaLongitudinalEnabled"),
      BigToggleCard("UI Debug Mode", "Show touch points and FPS counter.",
                    param_key="ShowDebugInfo", on_change=self._on_debug_toggle),
    ]
