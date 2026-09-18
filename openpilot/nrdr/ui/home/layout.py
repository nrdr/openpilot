import os
import socket
import subprocess
import time
from collections.abc import Callable

import pyray as rl

from openpilot.common.params import Params
from openpilot.selfdrive.ui.layouts.home import SPACING
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.trips import TripsLayout
from openpilot.system.ui.lib.application import FontWeight, MousePos, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog


__all__ = ("REFRESH_INTERVAL", "FirstRunSetup", "NrdrForkWidget", "NrdrHomeLayout")


REFRESH_INTERVAL = 10.0



def _local_ip() -> str:
  try:
    out = subprocess.check_output(["ip", "-4", "-o", "addr"], encoding="utf8", timeout=2)
    addrs = []
    for line in out.splitlines():
      parts = line.split()
      if len(parts) >= 4 and parts[2] == "inet":
        addrs.append((parts[1], parts[3].split("/")[0]))
    for _ifname, ip in addrs:
      if ip.startswith("192.168.43."):
        return ip
    for ifname, ip in addrs:
      if ifname.startswith("wlan"):
        return ip
  except Exception:
    pass
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
      s.connect(("8.8.8.8", 80))
      return s.getsockname()[0]
  except Exception:
    return "--"

class NrdrForkWidget(Widget):
  FU_IDLE = 0
  FU_CHECKING = 1
  FU_DOWNLOADING = 2
  FU_REBOOTING = 3

  FU_POLL_INTERVAL = 0.5
  FU_WAKE_TIMEOUT = 15.0
  FU_PHASE_TIMEOUT = 900.0

  def __init__(self):
    super().__init__()
    self._params = Params()
    self._button_rect = rl.Rectangle(0, 0, 0, 0)
    self._update_button_rect = rl.Rectangle(0, 0, 0, 0)
    self._tune_click_callback: Callable[[], None] | None = None
    self._force_update_flash_until = 0.0
    self._force_update_status_text = "FORCE UPDATE"
    self._force_update_status_color = rl.Color(70, 135, 255, 255)
    self._tune_flash_until = 0.0
    self._pending_tune_callback = False
    self._fu_state = self.FU_IDLE
    self._fu_phase_start = 0.0
    self._fu_saw_active = False
    self._fu_baseline_failed_count = 0
    self._fu_last_poll = 0.0
    self._ip_text = "--"
    self._ip_last_check = 0.0

  def set_click_callback(self, callback: Callable[[], None]):
    self._tune_click_callback = callback

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if rl.check_collision_point_rec(mouse_pos, self._update_button_rect):
      self._run_force_update()
      return

    if self._tune_click_callback is not None and rl.check_collision_point_rec(mouse_pos, self._button_rect):
      self._tune_flash_until = time.monotonic() + 0.18
      self._pending_tune_callback = True
      return

    super()._handle_mouse_release(mouse_pos)

  def _fu_set_status(self, text: str, color: rl.Color, flash_secs: float | None = None):
    self._force_update_status_text = text
    self._force_update_status_color = color
    if flash_secs is not None:
      self._force_update_flash_until = time.monotonic() + flash_secs

  def _fu_enter(self, state: int):
    self._fu_state = state
    self._fu_phase_start = time.monotonic()
    self._fu_saw_active = False

  def _fu_fail(self, text: str):
    self._fu_state = self.FU_IDLE
    self._fu_set_status(text, rl.Color(190, 68, 68, 255), flash_secs=4.0)

  def _run_force_update(self):
    if self._fu_state != self.FU_IDLE:
      return

    try:
      update_available = self._params.get_bool("UpdateAvailable")
      fetch_available = self._params.get_bool("UpdaterFetchAvailable")
      self._fu_baseline_failed_count = self._params.get("UpdateFailedCount") or 0
    except Exception:
      update_available = fetch_available = False
      self._fu_baseline_failed_count = 0

    if update_available:
      self._fu_install()
      return

    if fetch_available:
      os.system("pkill -SIGHUP -f system.updated.updated")
      self._fu_enter(self.FU_DOWNLOADING)
      self._fu_set_status("DOWNLOADING", rl.Color(58, 150, 90, 255))
      return

    os.system("pkill -SIGUSR1 -f system.updated.updated")
    self._fu_enter(self.FU_CHECKING)
    self._fu_set_status("CHECKING", rl.Color(58, 150, 90, 255))

  def _fu_install(self):
    self._fu_enter(self.FU_REBOOTING)
    self._fu_set_status("REBOOTING TO INSTALL", rl.Color(70, 135, 255, 255))
    try:
      self._params.put_bool("DoReboot", True)
    except Exception:
      self._fu_fail("REBOOT FAILED")

  def _fu_poll(self):
    if self._fu_state in (self.FU_IDLE, self.FU_REBOOTING):
      return

    now = time.monotonic()
    if now - self._fu_last_poll < self.FU_POLL_INTERVAL:
      return
    self._fu_last_poll = now

    try:
      updater_state = (self._params.get("UpdaterState") or "idle").strip()
      fetch_available = self._params.get_bool("UpdaterFetchAvailable")
      update_available = self._params.get_bool("UpdateAvailable")
      failed_count = self._params.get("UpdateFailedCount") or 0
    except Exception:
      return

    elapsed = now - self._fu_phase_start

    if updater_state != "idle":
      self._fu_saw_active = True
      self._fu_set_status(updater_state.rstrip(".").upper(), rl.Color(58, 150, 90, 255))
      if elapsed > self.FU_PHASE_TIMEOUT:
        self._fu_fail("UPDATER TIMED OUT")
      return

    if not self._fu_saw_active:
      if self._fu_state == self.FU_CHECKING and (fetch_available or update_available or failed_count > self._fu_baseline_failed_count):
        pass
      elif self._fu_state == self.FU_DOWNLOADING and (update_available or failed_count > self._fu_baseline_failed_count):
        pass
      elif elapsed < self.FU_WAKE_TIMEOUT:
        return
      else:
        self._fu_fail("UPDATER NOT RESPONDING")
        return

    if failed_count > self._fu_baseline_failed_count:
      self._fu_fail("UPDATE CHECK FAILED")
      return

    if self._fu_state == self.FU_CHECKING:
      if update_available:
        self._fu_install()
      elif fetch_available:
        os.system("pkill -SIGHUP -f system.updated.updated")
        self._fu_enter(self.FU_DOWNLOADING)
        self._fu_set_status("DOWNLOADING", rl.Color(58, 150, 90, 255))
      elif self._fu_saw_active:
        self._fu_state = self.FU_IDLE
        self._fu_set_status("UP TO DATE", rl.Color(58, 150, 90, 255), flash_secs=3.0)
      return

    if self._fu_state == self.FU_DOWNLOADING:
      if update_available:
        self._fu_install()
      elif self._fu_saw_active:
        self._fu_fail("DOWNLOAD FAILED")

  def _render(self, rect: rl.Rectangle):
    self._fu_poll()

    if self._pending_tune_callback and time.monotonic() >= self._tune_flash_until:
      self._pending_tune_callback = False
      if self._tune_click_callback is not None:
        self._tune_click_callback()

    rl.draw_rectangle_rounded(rect, 0.04, 16, rl.Color(30, 30, 30, 255))

    title_font = gui_app.font(FontWeight.BOLD)
    body_font = gui_app.font(FontWeight.NORMAL)
    button_font = gui_app.font(FontWeight.MEDIUM)

    x = rect.x + 55
    y = rect.y + 75
    w = rect.width - 110

    now = time.monotonic()
    if now - self._ip_last_check > REFRESH_INTERVAL:
      self._ip_last_check = now
      self._ip_text = _local_ip()

    title = "nrdr"
    subtitle = "Your drives will upload to connect.comma.ai."
    body = f"IP: {self._ip_text}"

    rl.draw_text_ex(title_font, title, rl.Vector2(x, y), 97, 0, rl.WHITE)

    subtitle_words = subtitle.split()
    subtitle_lines = []
    subtitle_line = ""

    for word in subtitle_words:
      test_line = f"{subtitle_line} {word}".strip()

      if measure_text_cached(body_font, test_line, 54).x > w and subtitle_line:
        subtitle_lines.append(subtitle_line)
        subtitle_line = word
      else:
        subtitle_line = test_line

    if subtitle_line:
      subtitle_lines.append(subtitle_line)

    for idx, line_text in enumerate(subtitle_lines[:2]):
      rl.draw_text_ex(
        body_font,
        line_text,
        rl.Vector2(x, y + 110 + idx * 46),
        54,
        0,
        rl.Color(225, 225, 225, 255),
      )

    max_line_width = int(w)
    words = body.split()
    lines = []
    line = ""

    for word in words:
      test_line = f"{line} {word}".strip()
      if measure_text_cached(body_font, test_line, 44).x > max_line_width and line:
        lines.append(line)
        line = word
      else:
        line = test_line

    if line:
      lines.append(line)

    body_y = y + 275

    for idx, line_text in enumerate(lines[:4]):
      rl.draw_text_ex(
        body_font,
        line_text,
        rl.Vector2(x, body_y + idx * 47),
        37,
        0,
        rl.Color(175, 175, 175, 255),
      )

    button_width = min(650, w)
    button_x = rect.x + (rect.width - button_width) / 2

    tune_button_height = 109
    update_button_height = 109
    button_gap = 24
    bottom_margin = 45

    self._update_button_rect = rl.Rectangle(
      button_x,
      rect.y + rect.height - bottom_margin - update_button_height,
      button_width,
      update_button_height,
    )

    self._button_rect = rl.Rectangle(
      button_x,
      self._update_button_rect.y - button_gap - tune_button_height,
      button_width,
      tune_button_height,
    )

    tune_button_active = time.monotonic() < self._tune_flash_until
    tune_color = rl.Color(70, 135, 255, 255) if tune_button_active else rl.Color(58, 58, 58, 255)

    rl.draw_rectangle_rounded(
      self._button_rect,
      0.32,
      18,
      tune_color,
    )

    button_text = "TUNE YOUR CAR"
    button_size = measure_text_cached(button_font, button_text, 52)

    rl.draw_text_ex(
      button_font,
      button_text,
      rl.Vector2(
        self._button_rect.x + (self._button_rect.width - button_size.x) / 2,
        self._button_rect.y + (self._button_rect.height - button_size.y) / 2,
      ),
      52,
      0,
      rl.WHITE,
    )

    force_update_active = self._fu_state != self.FU_IDLE or time.monotonic() < self._force_update_flash_until
    update_color = self._force_update_status_color if force_update_active else rl.Color(58, 58, 58, 255)
    update_text = self._force_update_status_text if force_update_active else "FORCE UPDATE"

    rl.draw_rectangle_rounded(
      self._update_button_rect,
      0.32,
      18,
      update_color,
    )

    update_size = measure_text_cached(button_font, update_text, 52)

    rl.draw_text_ex(
      button_font,
      update_text,
      rl.Vector2(
        self._update_button_rect.x + (self._update_button_rect.width - update_size.x) / 2,
        self._update_button_rect.y + (self._update_button_rect.height - update_size.y) / 2,
      ),
      52,
      0,
      rl.WHITE,
    )

class FirstRunSetup:
  def __init__(self, params: Params):
    self.params = params
    self.shown = False

  def update(self) -> None:
    if self.shown:
      return
    try:
      if self.params.get_bool("NrdrFirstRunSetupDone"):
        return
    except Exception:
      self.shown = True
      return
    self.shown = True
    gui_app.push_widget(ConfirmDialog(
      tr("Download the recommended Pop V2 driving model? It downloads in the background over Wi-Fi."),
      tr("Download model"),
      callback=self._model_selected,
    ))

  def _model_selected(self, result: DialogResult) -> None:
    if result == DialogResult.CONFIRM:
      self.params.put_bool("NrdrAutoSelectModel", True)
    gui_app.push_widget(ConfirmDialog(
      tr("Also download offline maps for the entire United States (about 6 GB) over Wi-Fi?"),
      tr("Download maps"),
      callback=self._maps_selected,
    ))

  def _maps_selected(self, result: DialogResult) -> None:
    if result == DialogResult.CONFIRM:
      self.params.put("OsmLocationName", "US")
      self.params.put("OsmLocationTitle", "United States")
      self.params.put_bool("OsmLocal", True)
      self.params.put("OsmStateName", "All")
      self.params.put("OsmStateTitle", "All states (~6.0 GB)")
      self.params.put_bool("OsmDbUpdatesCheck", True)
    self.params.put_bool("NrdrFirstRunSetupDone", True)


class NrdrHomeLayout:
  def __init__(self):
    super().__init__()
    self._first_run = FirstRunSetup(self.params)
    self._trips_widget = TripsLayout()
    self._nrdr_widget = NrdrForkWidget()
    self._nrdr_widget.set_click_callback(lambda: self.settings_callback() if self.settings_callback else None)

  def _update_state(self):
    self._first_run.update()
    super()._update_state()

  def _render_left_column(self):
    self._trips_widget.render(self.left_column_rect)

  def _render_right_column(self):
    exp_height = 125
    exp_rect = rl.Rectangle(
      self.right_column_rect.x, self.right_column_rect.y, self.right_column_rect.width, exp_height
    )
    self._exp_mode_button.render(exp_rect)

    setup_rect = rl.Rectangle(
      self.right_column_rect.x,
      self.right_column_rect.y + exp_height + SPACING,
      self.right_column_rect.width,
      self.right_column_rect.height - exp_height - SPACING,
    )
    self._nrdr_widget.render(setup_rect)
