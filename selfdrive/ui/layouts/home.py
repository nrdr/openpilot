import time
import os
import subprocess
import pyray as rl
from collections.abc import Callable
from enum import IntEnum
from openpilot.common.params import Params
from openpilot.selfdrive.ui.widgets.offroad_alerts import UpdateAlert, OffroadAlert
from openpilot.selfdrive.ui.widgets.exp_mode_button import ExperimentalModeButton
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.multilang import tr, trn
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.trips import TripsLayout

HEADER_HEIGHT = 80
HEAD_BUTTON_FONT_SIZE = 40
CONTENT_MARGIN = 40
SPACING = 25
RIGHT_COLUMN_WIDTH = 750
REFRESH_INTERVAL = 10.0



class NrdrForkWidget(Widget):
  OPSYNC_PATHS = (
    "/data/openpilot/scripts/bash/opsync.sh",
    "/data/openpilot/scripts/opsync.sh",
  )

  def __init__(self):
    super().__init__()
    self._button_rect = rl.Rectangle(0, 0, 0, 0)
    self._update_button_rect = rl.Rectangle(0, 0, 0, 0)
    self._tune_click_callback: Callable[[], None] | None = None
    self._force_update_flash_until = 0.0
    self._force_update_status_text = "FORCE UPDATE"
    self._force_update_status_color = rl.Color(70, 135, 255, 255)
    self._tune_flash_until = 0.0
    self._pending_tune_callback = False

  def set_click_callback(self, callback: Callable[[], None]):
    self._tune_click_callback = callback

  def _handle_mouse_release(self, mouse_pos: MousePos):
    # Handle the inner buttons before calling the base Widget handler. The base
    # handler may treat this whole card as clickable, so FORCE UPDATE must be
    # consumed here before the Tune Your Car callback can fire.
    if rl.check_collision_point_rec(mouse_pos, self._update_button_rect):
      self._run_force_update()
      return

    if self._tune_click_callback is not None and rl.check_collision_point_rec(mouse_pos, self._button_rect):
      self._tune_flash_until = time.monotonic() + 0.18
      self._pending_tune_callback = True
      return

    super()._handle_mouse_release(mouse_pos)

  def _run_force_update(self):
    opsync_path = next((path for path in self.OPSYNC_PATHS if os.path.exists(path)), None)
    self._force_update_flash_until = time.monotonic() + 1.5

    if opsync_path is None:
      self._force_update_status_text = "SCRIPT MISSING"
      self._force_update_status_color = rl.Color(190, 68, 68, 255)
      return

    self._force_update_status_text = "FETCHING UPSTREAM"
    self._force_update_status_color = rl.Color(58, 150, 90, 255)

    subprocess.Popen(
      ["bash", opsync_path],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      cwd="/data/openpilot",
    )

  def _render(self, rect: rl.Rectangle):
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

    title = "nrdr"
    subtitle = "Your drives will upload to stable.konik.ai."
    body = "Making Toyota and HKG users jealous, one day at a time."

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

    force_update_active = time.monotonic() < self._force_update_flash_until
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


class HomeLayoutState(IntEnum):
  HOME = 0
  UPDATE = 1
  ALERTS = 2


class HomeLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self._first_run_prompt_shown = False  # nrdr first-run model/map setup popup

    self.update_alert = UpdateAlert()
    self.offroad_alert = OffroadAlert()

    self._layout_widgets = {HomeLayoutState.UPDATE: self.update_alert, HomeLayoutState.ALERTS: self.offroad_alert}

    self.current_state = HomeLayoutState.HOME
    self.last_refresh = 0
    self.settings_callback: Callable[[], None] | None = None

    self.update_available = False
    self.alert_count = 0
    self._version_text = ""
    self._prev_update_available = False
    self._prev_alerts_present = False

    self.header_rect = rl.Rectangle(0, 0, 0, 0)
    self.content_rect = rl.Rectangle(0, 0, 0, 0)
    self.left_column_rect = rl.Rectangle(0, 0, 0, 0)
    self.right_column_rect = rl.Rectangle(0, 0, 0, 0)

    self.update_notif_rect = rl.Rectangle(0, 0, 200, HEADER_HEIGHT - 10)
    self.alert_notif_rect = rl.Rectangle(0, 0, 220, HEADER_HEIGHT - 10)

    self._trips_widget = TripsLayout()
    self._nrdr_widget = NrdrForkWidget()

    self._exp_mode_button = ExperimentalModeButton()
    self._setup_callbacks()

  def show_event(self):
    super().show_event()
    self._exp_mode_button.show_event()
    self.last_refresh = time.monotonic()
    self._refresh()

  def _setup_callbacks(self):
    self.update_alert.set_dismiss_callback(lambda: self._set_state(HomeLayoutState.HOME))
    self.offroad_alert.set_dismiss_callback(lambda: self._set_state(HomeLayoutState.HOME))
    self._exp_mode_button.set_click_callback(lambda: self.settings_callback() if self.settings_callback else None)
    self._nrdr_widget.set_click_callback(lambda: self.settings_callback() if self.settings_callback else None)

  def set_settings_callback(self, callback: Callable):
    self.settings_callback = callback

  def _set_state(self, state: HomeLayoutState):
    # propagate show/hide events
    if state != self.current_state:
      if state == HomeLayoutState.HOME:
        self._exp_mode_button.show_event()

      if state in self._layout_widgets:
        self._layout_widgets[state].show_event()
      if self.current_state in self._layout_widgets:
        self._layout_widgets[self.current_state].hide_event()

    self.current_state = state

  def _render(self, rect: rl.Rectangle):
    current_time = time.monotonic()
    if current_time - self.last_refresh >= REFRESH_INTERVAL:
      self._refresh()
      self.last_refresh = current_time

    self._render_header()

    # Render content based on current state
    if self.current_state == HomeLayoutState.HOME:
      self._render_home_content()
    elif self.current_state == HomeLayoutState.UPDATE:
      self._render_update_view()
    elif self.current_state == HomeLayoutState.ALERTS:
      self._render_alerts_view()

  def _maybe_show_first_run(self):
    # First boot only: two short, independent prompts (model, then maps). The home
    # screen only renders offroad, so no extra ignition check is needed.
    if self._first_run_prompt_shown:
      return
    try:
      first_run_done = self.params.get_bool("NrdrFirstRunSetupDone")
    except Exception:
      # Key not in this build's params registry (params lib not rebuilt for the new
      # keys). Disable the first-run flow instead of crashing the UI every frame.
      self._first_run_prompt_shown = True
      return
    if first_run_done:
      return
    self._first_run_prompt_shown = True
    self._show_first_run_model_prompt()

  def _show_first_run_model_prompt(self):
    def _cb(result):
      if result == DialogResult.CONFIRM:
        # Ask the model daemon to find + download Pop V2 (it has the bundle list).
        self.params.put_bool("NrdrAutoSelectModel", True)
      self._show_first_run_maps_prompt()

    msg = tr("Download the recommended Pop V2 driving model? It downloads in the background over Wi-Fi.")
    gui_app.push_widget(ConfirmDialog(msg, tr("Download model"), callback=_cb))

  def _show_first_run_maps_prompt(self):
    def _cb(result):
      if result == DialogResult.CONFIRM:
        self._start_us_map_download()
      self.params.put_bool("NrdrFirstRunSetupDone", True)

    msg = tr("Also download offline maps for the entire United States (about 6 GB) over Wi-Fi?")
    gui_app.push_widget(ConfirmDialog(msg, tr("Download maps"), callback=_cb))

  def _start_us_map_download(self):
    p = self.params
    # Entire US OSM map (matches the osm.py "All states" selection), then trigger mapd.
    p.put("OsmLocationName", "US")
    p.put("OsmLocationTitle", "United States")
    p.put_bool("OsmLocal", True)
    p.put("OsmStateName", "All")
    p.put("OsmStateTitle", "All states (~6.0 GB)")
    p.put_bool("OsmDbUpdatesCheck", True)

  def _update_state(self):
    self._maybe_show_first_run()

    self.header_rect = rl.Rectangle(
      self._rect.x + CONTENT_MARGIN, self._rect.y + CONTENT_MARGIN, self._rect.width - 2 * CONTENT_MARGIN, HEADER_HEIGHT
    )

    content_y = self._rect.y + CONTENT_MARGIN + HEADER_HEIGHT + SPACING
    content_height = self._rect.height - CONTENT_MARGIN - HEADER_HEIGHT - SPACING - CONTENT_MARGIN

    self.content_rect = rl.Rectangle(
      self._rect.x + CONTENT_MARGIN, content_y, self._rect.width - 2 * CONTENT_MARGIN, content_height
    )

    left_width = self.content_rect.width - RIGHT_COLUMN_WIDTH - SPACING

    self.left_column_rect = rl.Rectangle(self.content_rect.x, self.content_rect.y, left_width, self.content_rect.height)

    self.right_column_rect = rl.Rectangle(
      self.content_rect.x + left_width + SPACING, self.content_rect.y, RIGHT_COLUMN_WIDTH, self.content_rect.height
    )

    self.update_notif_rect.x = self.header_rect.x
    self.update_notif_rect.y = self.header_rect.y + (self.header_rect.height - 60) // 2

    notif_x = self.header_rect.x + (220 if self.update_available else 0)
    self.alert_notif_rect.x = notif_x
    self.alert_notif_rect.y = self.header_rect.y + (self.header_rect.height - 60) // 2

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    if self.update_available and rl.check_collision_point_rec(mouse_pos, self.update_notif_rect):
      self._set_state(HomeLayoutState.UPDATE)
    elif self.alert_count > 0 and rl.check_collision_point_rec(mouse_pos, self.alert_notif_rect):
      self._set_state(HomeLayoutState.ALERTS)

  def _render_header(self):
    font = gui_app.font(FontWeight.MEDIUM)

    version_text_width = self.header_rect.width

    # Update notification button
    if self.update_available:
      version_text_width -= self.update_notif_rect.width

      # Highlight if currently viewing updates
      highlight_color = rl.Color(75, 95, 255, 255) if self.current_state == HomeLayoutState.UPDATE else rl.Color(54, 77, 239, 255)
      rl.draw_rectangle_rounded(self.update_notif_rect, 0.3, 10, highlight_color)

      text = tr("UPDATE")
      text_size = measure_text_cached(font, text, HEAD_BUTTON_FONT_SIZE)
      text_x = self.update_notif_rect.x + (self.update_notif_rect.width - text_size.x) // 2
      text_y = self.update_notif_rect.y + (self.update_notif_rect.height - text_size.y) // 2
      rl.draw_text_ex(font, text, rl.Vector2(int(text_x), int(text_y)), HEAD_BUTTON_FONT_SIZE, 0, rl.WHITE)

    # Alert notification button
    if self.alert_count > 0:
      version_text_width -= self.alert_notif_rect.width

      # Highlight if currently viewing alerts
      highlight_color = rl.Color(255, 70, 70, 255) if self.current_state == HomeLayoutState.ALERTS else rl.Color(226, 44, 44, 255)
      rl.draw_rectangle_rounded(self.alert_notif_rect, 0.3, 10, highlight_color)

      alert_text = trn("{} ALERT", "{} ALERTS", self.alert_count).format(self.alert_count)
      text_size = measure_text_cached(font, alert_text, HEAD_BUTTON_FONT_SIZE)
      text_x = self.alert_notif_rect.x + (self.alert_notif_rect.width - text_size.x) // 2
      text_y = self.alert_notif_rect.y + (self.alert_notif_rect.height - text_size.y) // 2
      rl.draw_text_ex(font, alert_text, rl.Vector2(int(text_x), int(text_y)), HEAD_BUTTON_FONT_SIZE, 0, rl.WHITE)

    # Version text (right aligned)
    if self.update_available or self.alert_count > 0:
      version_text_width -= SPACING * 1.5

    version_rect = rl.Rectangle(self.header_rect.x + self.header_rect.width - version_text_width, self.header_rect.y,
                                version_text_width, self.header_rect.height)
    gui_label(version_rect, self._version_text, 48, rl.WHITE, alignment=rl.GuiTextAlignment.TEXT_ALIGN_RIGHT)

  def _render_home_content(self):
    self._render_left_column()
    self._render_right_column()

  def _render_update_view(self):
    self.update_alert.render(self.content_rect)

  def _render_alerts_view(self):
    self.offroad_alert.render(self.content_rect)

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

  def _refresh(self):
    self._version_text = self._get_version_text()
    update_available = self.update_alert.refresh()
    alert_count = self.offroad_alert.refresh()
    alerts_present = alert_count > 0

    # Show panels on transition from no alert/update to any alerts/update
    if not update_available and not alerts_present:
      self._set_state(HomeLayoutState.HOME)
    elif update_available and ((not self._prev_update_available) or (not alerts_present and self.current_state == HomeLayoutState.ALERTS)):
      self._set_state(HomeLayoutState.UPDATE)
    elif alerts_present and ((not self._prev_alerts_present) or (not update_available and self.current_state == HomeLayoutState.UPDATE)):
      self._set_state(HomeLayoutState.ALERTS)

    self.update_available = update_available
    self.alert_count = alert_count
    self._prev_update_available = update_available
    self._prev_alerts_present = alerts_present

  def _get_version_text(self) -> str:
    brand = "nrdr"
    description = self.params.get("UpdaterCurrentDescription")
    return f"{brand} {description}" if description else brand
