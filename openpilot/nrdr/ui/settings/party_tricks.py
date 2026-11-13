import subprocess
from collections.abc import Callable
import pyray as rl

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.html_render import HtmlModalSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp, option_item_sp, LineSeparatorSP
from openpilot.nrdr.ui.settings.footage import FootageLayout


class PartyTricksLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._showing_footage = False
    self._footage_layout = FootageLayout(self._close_footage)

    self._reregister_proc: subprocess.Popen | None = None

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _on_reregister(self):
    if self._reregister_proc is not None:
      return
    dialog = ConfirmDialog(
      tr("Re-register with konik? Clears the dongle ID and registers fresh. Only if the device won't come online."),
      tr("Re-register"),
      tr("Cancel"),
      callback=self._on_reregister_confirmed,
    )
    gui_app.push_widget(dialog)

  def _on_reregister_confirmed(self, result: DialogResult):
    if result != DialogResult.CONFIRM or self._reregister_proc is not None:
      return
    Params().remove("DongleId")
    self._reregister_proc = subprocess.Popen(
      ["python3", "-m", "openpilot.system.athena.registration"],
      cwd=BASEDIR,
    )
    gui_app.push_widget(HtmlModalSP(text=tr(
      "Re-registering with konik... this can take up to a minute. Check the connect status on the sidebar when it finishes."
    )))

  def _poll_reregister(self):
    if self._reregister_proc is not None and self._reregister_proc.poll() is not None:
      self._reregister_proc = None

  def _open_footage(self):
    self._showing_footage = True
    self._footage_layout.show_event()

  def _close_footage(self):
    self._showing_footage = False

  def _initialize_items(self):
    self._show_footage_item = button_item(
      lambda: tr("Show Footage"),
      lambda: tr("OPEN"),
      lambda: tr(
        "Choose a recorded drive and scan its QR code to watch it on your phone. Connect to the device's hotspot or the same Wi-Fi network."
      ),
      callback=self._open_footage,
    )

    self._reregister_item = button_item(
      lambda: tr("Re-register with konik"),
      lambda: tr("RE-REGISTER"),
      lambda: tr(
        "Registers the device with konik again. Use this if the device cannot connect after switching from comma connect."
      ),
      callback=self._on_reregister,
    )

    self._injection_test = toggle_item_sp(
      param="HondaInjectionTest",
      title=lambda: tr("Injection Test (Caution!) (Default: OFF)"),
      description=lambda: tr(
        "Multiplies the lateral PID output scale by 999% for diagnostic testing. Can cause abrupt steering; do not use on public roads."
      ),
    )

    self._alt_dashboard_speed = multiple_button_item_sp(
      title=lambda: tr("Alternative Dashboard Speed Design (Default: Stock)"),
      description=lambda: tr(
        "Choose whether the dashboard's set-speed display shows cruise set speed, lead speed, GPS speed, or cluster speed. Stock restores the normal display."
      ),
      buttons=[lambda: tr("Stock"), lambda: tr("Lead Speed"), lambda: tr("GPS Speed"), lambda: tr("Cluster Speed")],
      button_width=330,
      param="HondaAltDashboardSpeed",
    )

    self._alt_dashboard_distance = multiple_button_item_sp(
      title=lambda: tr("Alternative Dashboard Distance Design (Default: Stock)"),
      description=lambda: tr(
        "Choose distance bars that show the personality, lead proximity, or acceleration and braking. " +
            "Alternate designs remain visible while disengaged; Stock restores the normal display."
      ),
      buttons=[lambda: tr("Stock"), lambda: tr("Radar"), lambda: tr("Velocity")],
      button_width=330,
      param="HondaAltDashboardDistance",
    )

    self._clear_dash_faults = toggle_item_sp(
      param="NrdrClearDashFaults",
      title=lambda: tr("Clear Dashboard Fault Codes (Default: ON)"),
      description=lambda: tr(
        "Hides camera-related fault indicators and silences the factory forward-collision warning chime " +
            "without fixing the underlying faults. Off restores those warnings."
      ),
    )

    self._spoof_camera_messages = toggle_item_sp(
      param="HondaSpoofCameraMessages",
      title=lambda: tr("Spoof Camera Messages (Default: OFF)"),
      description=lambda: tr(
        "Prevents the automatic high-beam fault caused by a missing or failed camera. Leave off if the factory camera works."
      ),
    )

    self._cruise_button_sub_mode = toggle_item_sp(
      param="NrdrCruiseButtonSubMode",
      title=lambda: tr("Cruise Button Sub-Mode (Default: ON)"),
      description=lambda: tr(
        "The first cruise-button press opens a blinking preview; further presses adjust speed or " +
            "personality. Off lets the first press make the adjustment immediately."
      ),
    )

    self._cruise_button_sub_mode_secs = option_item_sp(
      param="NrdrCruiseButtonSubModeSecs",
      title=lambda: tr("Sub-Mode Visibility Time (Default: 15s)"),
      min_value=5,
      max_value=60,
      value_change_step=1,
      description=lambda: tr(
        "Sets how long the dashboard preview remains visible after a button press. Blinking speeds up as the preview approaches its timeout."
      ),
      label_callback=lambda value: f"{value}s",
    )

    return [
      self._show_footage_item,
      self._reregister_item,
      LineSeparatorSP(40),
      self._injection_test,
      LineSeparatorSP(40),
      self._alt_dashboard_speed,
      self._alt_dashboard_distance,
      LineSeparatorSP(40),
      self._clear_dash_faults,
      self._spoof_camera_messages,
      LineSeparatorSP(40),
      self._cruise_button_sub_mode,
      self._cruise_button_sub_mode_secs,
    ]

  def _update_state(self):
    super()._update_state()
    self._poll_reregister()
    self._injection_test.action_item.set_enabled(True)
    self._alt_dashboard_speed.action_item.set_enabled(True)
    self._alt_dashboard_distance.action_item.set_enabled(True)
    self._cruise_button_sub_mode.action_item.set_enabled(True)
    self._cruise_button_sub_mode_secs.set_visible(self._cruise_button_sub_mode.action_item.get_state())

  def _render(self, rect):
    if self._showing_footage:
      self._footage_layout.render(rect)
      return
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._showing_footage = False
    self._scroller.show_event()
