"""
nrdr "Special" sub-panel (formerly Party Tricks): dashboard designs, the Dynamic
HUD, diagnostics, and the Show Footage QR flow.
"""
import os
import subprocess
from collections.abc import Callable
import pyray as rl

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.html_render import HtmlModalSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp, option_item_sp, LineSeparatorSP
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.footage import FootageLayout


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
    # Clear the cached dongle so konik.register() does a fresh registration
    # (it keeps an existing valid dongle otherwise). Mainly for comma->konik
    # migrants; existing konik users never need this.
    Params().remove("DongleId")
    self._reregister_proc = subprocess.Popen(
      ["python3", "-m", "openpilot.system.athena.konik"],
      cwd=BASEDIR,
    )
    gui_app.push_widget(HtmlModalSP(text=tr("Re-registering with konik... this can take up to a minute. Check the connect status on the sidebar when it finishes.")))

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
      lambda: tr("Pick a drive and get a QR code that lets a phone on this device's hotspot (or the same Wi-Fi) watch the recorded video. Made for the roadside \"can I see the footage?\" moment."),
      callback=self._open_footage,
    )

    self._reregister_item = button_item(
      lambda: tr("Re-register with konik"),
      lambda: tr("RE-REGISTER"),
      lambda: tr("Forces a fresh konik registration by clearing the cached dongle ID. Use this only if you switched from comma connect and the device won't come online on konik. Existing konik users never need this - your dongle is kept automatically."),
      callback=self._on_reregister,
    )

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

    self._clear_dash_faults = toggle_item_sp(
      param="NrdrClearDashFaults",
      title=lambda: tr("Clear Dashboard Fault Codes (Default: ON)"),
      description=lambda: tr("Forces the cluster's FCM/icon fault bits off and suppresses the stock FCW chime. Lets a car with a dead or absent stock camera run a clean dash. Turn OFF for stock openpilot behavior (camera values passed through, FCW chime active)."),
    )

    self._spoof_camera_messages = toggle_item_sp(
      param="HondaSpoofCameraMessages",
      title=lambda: tr("Spoof Camera Messages (Default: OFF)"),
      description=lambda: tr("Dead camera only: keeps the camera's CAMERA_MESSAGES broadcast alive so the cluster never raises \"Auto High Beam System Problem\" - that fault is a message timeout, not a code. Leave OFF if your stock camera works; a live camera already sends this message."),
    )

    self._cruise_button_sub_mode = toggle_item_sp(
      param="NrdrCruiseButtonSubMode",
      title=lambda: tr("Cruise Button Sub-Mode (Default: ON)"),
      description=lambda: tr("Dynamic HUD: pressing the distance button or set/resume first wakes a 15-second preview on the cluster - "
                            "the distance bars light up with your CURRENT personality (parked or driving, any design) and the set speed shows if cruise is engaged, all blinking. "
                            "Only presses made during the preview actually change the personality or set speed. "
                            "The blink starts lazy and accelerates continuously until it cuts off."),
    )

    self._cruise_button_sub_mode_secs = option_item_sp(
      param="NrdrCruiseButtonSubModeSecs",
      title=lambda: tr("Sub-Mode Visibility Time (Default: 15s)"),
      min_value=5,
      max_value=60,
      value_change_step=1,
      description=lambda: tr("How long the preview stays on the cluster after a button press. The blink ramp always spans the whole window, slow at the start and rapid right before it falls off."),
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
    # Visibility time only matters while the sub-mode itself is enabled.
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
