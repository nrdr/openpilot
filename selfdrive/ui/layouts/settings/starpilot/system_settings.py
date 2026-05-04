from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

import pyray as rl

from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app, FontWeight, MouseEvent, MousePos
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog, alert_dialog
from openpilot.system.ui.widgets.keyboard import Keyboard
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.label import gui_label

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.layouts.settings.starpilot.panel import _SettingsPage
from openpilot.selfdrive.ui.layouts.settings.starpilot.aethergrid import (
  AETHER_LIST_METRICS,
  AetherAdjustorRow,
  AetherScrollbar,
  AetherSegmentedControl,
  AetherListColors,
  DEFAULT_PANEL_STYLE,
  _point_hits,
  init_list_panel,
  draw_list_group_shell,
  draw_list_scroll_fades,
  draw_section_header,
  draw_selection_list_row,
  draw_settings_list_row,
  draw_settings_panel_header,
  draw_soft_card,
  draw_tab_card,
)

LEGACY_STARPILOT_PARAM_RENAMES = {
  "FrogPilotApiToken": "StarPilotApiToken",
  "FrogPilotCarParams": "StarPilotCarParams",
  "FrogPilotCarParamsPersistent": "StarPilotCarParamsPersistent",
  "FrogPilotDongleId": "StarPilotDongleId",
  "FrogPilotStats": "StarPilotStats",
}

EXCLUDED_KEYS = {
  "AvailableModels",
  "AvailableModelNames",
  "StarPilotStats",
  "GithubSshKeys",
  "GithubUsername",
  "MapBoxRequests",
  "ModelDrivesAndScores",
  "OverpassRequests",
  "SpeedLimits",
  "SpeedLimitsFiltered",
  "UpdaterAvailableBranches",
}

REPORT_CATEGORIES = [
  "Acceleration feels harsh or jerky",
  "An alert was unclear and I'm not sure what it meant",
  "Braking is too sudden or uncomfortable",
  "I'm not sure if this is normal or a bug:",
  "My steering wheel buttons aren't working",
  "openpilot disengages when I don't expect it",
  "openpilot feels sluggish or slow to respond",
  "Something else (please describe)",
]


class SystemSettingsManagerView(Widget):
  HEADER_SUBTITLE_HEIGHT = 24
  HEADER_SUMMARY_GAP = 12
  HEADER_CARD_HEIGHT = 108
  TAB_HEIGHT = 56
  TAB_GAP = 10
  TAB_BOTTOM_GAP = 18
  SECTION_GAP = AETHER_LIST_METRICS.section_gap
  SECTION_HEADER_HEIGHT = AETHER_LIST_METRICS.section_header_height
  SECTION_HEADER_GAP = AETHER_LIST_METRICS.section_header_gap
  ROW_HEIGHT = AETHER_LIST_METRICS.row_height
  FADE_HEIGHT = AETHER_LIST_METRICS.fade_height
  COLUMN_GAP = 22
  TWO_COLUMN_BREAKPOINT = 1180
  ACTION_PILL_WIDTH = 132
  DANGER_PILL_WIDTH = 112

  PANEL_STYLE = DEFAULT_PANEL_STYLE

  def __init__(self, controller: "StarPilotSystemLayout"):
    super().__init__()
    self._controller = controller
    self._scroll_panel = GuiScrollPanel2(horizontal=False)
    self._scrollbar = AetherScrollbar()
    self._content_height = 0.0
    self._scroll_offset = 0.0
    self._ensure_visible_key: str | None = None
    self._interactive_rects: dict[str, rl.Rectangle] = {}
    self._pressed_target: str | None = None
    self._can_click = True
    self._active_tab_key = "basics"
    self._active_adjustor_key: str | None = None
    self._adjustor_rows: dict[str, AetherAdjustorRow] = {}
    self._display_slider_keys = ["ScreenBrightness", "ScreenBrightnessOnroad", "ScreenTimeout", "ScreenTimeoutOnroad"]
    self._power_slider_keys = ["DeviceShutdown", "LowVoltageShutdown"]

    shutdown_labels = {0: tr("5 mins")}
    for i in range(1, 4): shutdown_labels[i] = f"{i * 15} mins"
    for i in range(4, 34): shutdown_labels[i] = f"{i - 3} " + (tr("hour") if i == 4 else tr("hours"))
    brightness_labels = {101: tr("Auto"), 0: tr("Off")}

    self._slider_specs = {
      "ScreenBrightness": {
        "title": tr("Offroad Brightness"),
        "subtitle": tr("Primary screen brightness while parked."),
        "unit": "%",
        "labels": brightness_labels,
        "min": 0,
        "max": 101,
        "step": 1,
        "live": True,
        "presets": [0, 25, 50, 75, 101],
        "get": lambda: float(self._controller._params.get_int("ScreenBrightness")),
        "set": lambda v: self._controller._set_brightness("ScreenBrightness", v),
      },
      "ScreenBrightnessOnroad": {
        "title": tr("Onroad Brightness"),
        "subtitle": tr("Screen brightness while driving."),
        "unit": "%",
        "labels": brightness_labels,
        "min": 1,
        "max": 101,
        "step": 1,
        "live": True,
        "presets": [1, 35, 60, 80, 101],
        "get": lambda: float(max(1, self._controller._params.get_int("ScreenBrightnessOnroad"))),
        "set": lambda v: self._controller._set_brightness("ScreenBrightnessOnroad", max(1, int(v))),
      },
      "ScreenTimeout": {
        "title": tr("Offroad Screen Timeout"),
        "subtitle": tr("How long the display stays awake while parked."),
        "unit": "s",
        "labels": {},
        "min": 5,
        "max": 60,
        "step": 5,
        "live": False,
        "presets": [5, 15, 30, 60],
        "get": lambda: float(self._controller._params.get_int("ScreenTimeout")),
        "set": lambda v: self._controller._params.put_int("ScreenTimeout", int(v)),
      },
      "ScreenTimeoutOnroad": {
        "title": tr("Onroad Screen Timeout"),
        "subtitle": tr("How long the display stays on while driving."),
        "unit": "s",
        "labels": {},
        "min": 5,
        "max": 60,
        "step": 5,
        "live": False,
        "presets": [5, 15, 30, 60],
        "get": lambda: float(self._controller._params.get_int("ScreenTimeoutOnroad")),
        "set": lambda v: self._controller._params.put_int("ScreenTimeoutOnroad", int(v)),
      },
      "DeviceShutdown": {
        "title": tr("Shutdown Delay"),
        "subtitle": tr("How long the device waits before powering down."),
        "unit": "",
        "labels": shutdown_labels,
        "min": 0,
        "max": 33,
        "step": 1,
        "live": False,
        "presets": [0, 1, 4, 8],
        "get": lambda: float(self._controller._params.get_int("DeviceShutdown")),
        "set": lambda v: self._controller._params.put_int("DeviceShutdown", int(v)),
      },
      "LowVoltageShutdown": {
        "title": tr("Low Voltage Shutdown"),
        "subtitle": tr("Voltage threshold that protects the car battery."),
        "unit": "V",
        "labels": {},
        "min": 11.8,
        "max": 12.5,
        "step": 0.1,
        "live": False,
        "presets": [11.8, 12.0, 12.2, 12.5],
        "get": lambda: float(self._controller._params.get_float("LowVoltageShutdown")),
        "set": lambda v: self._controller._params.put_float("LowVoltageShutdown", float(v)),
      },
    }

    for key, spec in self._slider_specs.items():
      on_change = (lambda value, setter=spec["set"]: setter(value)) if spec.get("live") else (lambda _value: None)
      on_commit = None if spec.get("live") else (lambda value, setter=spec["set"]: setter(value))
      adjustor = self._child(
        AetherAdjustorRow(
          spec["title"],
          spec["subtitle"],
          spec["min"],
          spec["max"],
          spec["step"],
          spec["get"],
          on_change,
          on_commit=on_commit,
          unit=spec["unit"],
          labels=spec["labels"],
          presets=spec.get("presets", []),
          is_active=lambda key=key: self._active_adjustor_key == key,
          set_active=lambda active, key=key: self._set_active_adjustor(key, active),
          style=self.PANEL_STYLE,
          color=self.PANEL_STYLE.accent,
        )
      )
      adjustor.set_touch_valid_callback(lambda adjustor=adjustor: self._scroll_panel.is_touch_valid() or adjustor.is_interacting)
      self._adjustor_rows[key] = adjustor

    self._toggle_defs = [
      {
        "id": "StandbyMode",
        "title": tr("Standby Mode"),
        "subtitle": tr("Keep the device ready for faster wake-ups."),
        "get": lambda: self._controller._params.get_bool("StandbyMode"),
        "set": lambda v: self._controller._params.put_bool("StandbyMode", v),
      },
      {
        "id": "IncreaseThermalLimits",
        "title": tr("Raise Thermal Limits"),
        "subtitle": tr("Allow the device to run warmer before backing off."),
        "get": lambda: self._controller._params.get_bool("IncreaseThermalLimits"),
        "set": lambda v: self._controller._params.put_bool("IncreaseThermalLimits", v),
      },
      {
        "id": "UseKonikServer",
        "title": tr("Use Konik Server"),
        "subtitle": tr("Switch remote services to the Konik endpoint."),
        "get": self._controller._get_konik_state,
        "set": self._controller._on_konik_toggle,
      },
      {
        "id": "DebugMode",
        "title": tr("Debug Mode"),
        "subtitle": tr("Expose additional debugging and developer toggles."),
        "get": lambda: self._controller._params.get_bool("DebugMode"),
        "set": lambda v: self._controller._params.put_bool("DebugMode", v),
      },
      {
        "id": "NoUploads",
        "title": tr("Disable Uploads"),
        "subtitle": tr("Stop all cloud uploads from this device."),
        "get": lambda: self._controller._params.get_bool("NoUploads"),
        "set": lambda v: self._controller._params.put_bool("NoUploads", v),
      },
      {
        "id": "DisableOnroadUploads",
        "title": tr("Disable Onroad Uploads"),
        "subtitle": tr("Block uploads while the car is onroad."),
        "get": lambda: self._controller._params.get_bool("DisableOnroadUploads"),
        "set": lambda v: self._controller._params.put_bool("DisableOnroadUploads", v),
        "is_enabled": lambda: not self._controller._params.get_bool("NoUploads"),
        "disabled_label": tr("Turn off Disable Uploads first"),
      },
      {
        "id": "NoLogging",
        "title": tr("Disable Logging"),
        "subtitle": tr("Stop writing standard log data to storage."),
        "get": lambda: self._controller._params.get_bool("NoLogging"),
        "set": lambda v: self._controller._params.put_bool("NoLogging", v),
      },
      {
        "id": "HigherBitrate",
        "title": tr("High Bitrate Recording"),
        "subtitle": tr("Capture higher-quality onroad footage."),
        "get": lambda: self._controller._params.get_bool("HigherBitrate"),
        "set": self._controller._on_higher_bitrate_toggle,
        "is_enabled": lambda: not self._controller._params.get_bool("DisableOnroadUploads") and not self._controller._params.get_bool("NoUploads"),
        "disabled_label": tr("Uploads must stay enabled"),
      },
    ]

    self._support_rows = [
      {
        "id": "ReportIssue",
        "title": tr("Report Issue"),
        "subtitle": tr("Send feedback with your Discord handle."),
        "action": tr("Open"),
      },
      {
        "id": "FlashPanda",
        "title": tr("Flash Panda"),
        "subtitle": tr("Reflash Panda firmware from this panel."),
        "action": tr("Flash"),
      },
    ]
    self._danger_rows = [
      {
        "id": "Storage",
        "title": tr("Clear Driving Data"),
        "subtitle": tr("Delete recorded driving data and footage."),
        "action": tr("Delete"),
      },
      {
        "id": "ErrorLogs",
        "title": tr("Clear Error Logs"),
        "subtitle": tr("Remove saved crash logs and diagnostics."),
        "action": tr("Delete"),
      },
      {
        "id": "ResetDefaults",
        "title": tr("Reset Toggles"),
        "subtitle": tr("Restore StarPilot defaults for all toggles."),
        "action": tr("Reset"),
      },
      {
        "id": "ResetStock",
        "title": tr("Reset To Stock"),
        "subtitle": tr("Restore stock openpilot toggle values."),
        "action": tr("Reset"),
      },
    ]
    self._toggle_groups = [
      {
        "id": "device_controls",
        "title": tr("Device Controls"),
        "toggle_ids": ["StandbyMode", "IncreaseThermalLimits", "UseKonikServer", "DebugMode"],
      },
      {
        "id": "uploads_logging",
        "title": tr("Uploads & Logging"),
        "toggle_ids": ["NoUploads", "DisableOnroadUploads", "NoLogging", "HigherBitrate"],
      },
    ]
    self._tab_defs = [
      {"id": "basics", "title": tr("Display & Power")},
      {"id": "connectivity", "title": tr("Connectivity")},
      {"id": "care", "title": tr("Backups & Care")},
    ]

    self._drive_mode_control = self._child(
      AetherSegmentedControl(
        [tr("Auto"), tr("Onroad"), tr("Offroad")],
        self._get_drive_mode_index,
        self._on_drive_mode_change,
        statuses=[tr("Default"), tr("Force on"), tr("Force off")],
      )
    )

    self._scroll_rect = rl.Rectangle(0, 0, 0, 0)

  def _section_height(self, count: int, row_height: float) -> float:
    return 0.0 if count <= 0 else count * row_height

  def _stacked_section_height(self, sections: list[float]) -> float:
    if not sections:
      return 0.0
    return max(0.0, sum(sections) - self.SECTION_GAP)

  def _uses_two_columns(self, width: float) -> bool:
    return width >= self.TWO_COLUMN_BREAKPOINT

  def _column_width(self, width: float) -> float:
    return (width - self.COLUMN_GAP) / 2 if self._uses_two_columns(width) else width

  def _interactive_state(self, target_id: str, rect: rl.Rectangle, *, pad_y: float = 0) -> tuple[bool, bool]:
    self._interactive_rects[target_id] = rect
    hovered = _point_hits(gui_app.last_mouse_event.pos, rect, self._scroll_rect, pad_x=6, pad_y=pad_y)
    return hovered, self._pressed_target == target_id

  def _lookup_toggle(self, toggle_id: str):
    return next((toggle for toggle in self._toggle_defs if toggle["id"] == toggle_id), None)

  def _toggle_defs_for_group(self, group: dict) -> list[dict]:
    return [toggle for toggle_id in group["toggle_ids"] if (toggle := self._lookup_toggle(toggle_id)) is not None]

  def _tab_subtitle(self, tab_id: str) -> str:
    if tab_id == "basics":
      return tr("{} controls").format(len(self._display_slider_keys) + len(self._power_slider_keys))
    if tab_id == "connectivity":
      return tr("{} toggles").format(len(self._toggle_defs))
    return self._controller.backup_status_text()

  def _format_slider_value(self, key: str) -> str:
    adjustor = self._adjustor_rows.get(key)
    if adjustor is not None:
      return adjustor.formatted_value()
    spec = self._slider_specs[key]
    current_val = spec["get"]()
    if current_val in spec["labels"]:
      return spec["labels"][current_val]
    if spec["step"] < 1:
      return f"{current_val:.1f}{spec['unit']}"
    return f"{int(current_val)}{spec['unit']}"

  def _set_active_adjustor(self, key: str, active: bool):
    if active:
      self._active_adjustor_key = key
      self._ensure_visible_key = key
    elif self._active_adjustor_key == key:
      self._active_adjustor_key = None
      self._ensure_visible_key = None

  def _get_drive_mode_index(self):
    state = self._controller._get_force_drive_state()
    if state == tr("Default"): return 0
    if state == tr("Onroad"): return 1
    if state == tr("Offroad"): return 2
    return 0

  def _on_drive_mode_change(self, idx):
    if idx == 0:
        self._controller.handle_action("DriveDefault")
    elif idx == 1:
        self._controller.handle_action("DriveOnroad")
    elif idx == 2:
        self._controller.handle_action("DriveOffroad")

  def _clear_ephemeral_state(self):
    self._pressed_target = None
    self._can_click = True
    self._active_adjustor_key = None
    self._ensure_visible_key = None
    for adjustor in self._adjustor_rows.values():
      adjustor.reset_interaction()

  def show_event(self):
    super().show_event()
    self._clear_ephemeral_state()
    self._scroll_offset = 0.0

  def hide_event(self):
    super().hide_event()
    self._clear_ephemeral_state()

  def _handle_mouse_press(self, mouse_pos: MousePos):
    self._pressed_target = self._target_at(mouse_pos)
    self._can_click = True

  def _handle_mouse_event(self, mouse_event: MouseEvent):
    if not self._scroll_panel.is_touch_valid():
      self._can_click = False
      return
    if self._pressed_target is not None and self._target_at(mouse_event.pos) != self._pressed_target:
      self._pressed_target = None

  def _handle_mouse_release(self, mouse_pos: MousePos):
    target = self._target_at(mouse_pos) if self._scroll_panel.is_touch_valid() else None
    if self._pressed_target is not None and self._pressed_target == target and self._can_click:
      self._activate_target(target)
    self._pressed_target = None
    self._can_click = True

  def _target_at(self, mouse_pos: MousePos) -> str | None:
    for target_id, rect in self._interactive_rects.items():
      if _point_hits(mouse_pos, rect, self._scroll_rect, pad_x=6, pad_y=0):
        return target_id
    return None

  def _activate_target(self, target_id: str | None):
    if not target_id:
      return
    prefix, _, value = target_id.partition(":")
    if prefix == "tab":
      self._active_tab_key = value
      self._active_adjustor_key = None
      for adjustor in self._adjustor_rows.values():
        adjustor.reset_interaction()
      return
    if prefix == "toggle":
      toggle_def = self._lookup_toggle(value)
      if toggle_def is None:
        return
      is_enabled = toggle_def.get("is_enabled", lambda: True)
      if is_enabled():
        toggle_def["set"](not toggle_def["get"]())
      return
    if prefix == "backup":
      self._controller.open_backup_manager(value)
      return
    if prefix == "action":
      self._controller.handle_action(value)

  def _render(self, rect: rl.Rectangle):
    self.set_rect(rect)

    frame, scroll_rect, content_width = init_list_panel(rect, self.PANEL_STYLE)
    self._scroll_rect = scroll_rect

    self._drive_mode_control.set_parent_rect(frame.header)

    self._draw_header(frame.header)
    self._content_height = self._measure_content_height(content_width)
    self._scroll_panel.set_enabled(self.is_visible)
    self._scroll_offset = self._scroll_panel.update(scroll_rect, max(self._content_height, scroll_rect.height))

    rl.begin_scissor_mode(int(scroll_rect.x), int(scroll_rect.y), int(scroll_rect.width), int(scroll_rect.height))
    self._draw_scroll_content(scroll_rect, content_width)
    rl.end_scissor_mode()

    if self._content_height > scroll_rect.height:
      self._scrollbar.render(scroll_rect, self._content_height, self._scroll_offset)

    draw_list_scroll_fades(scroll_rect, self._content_height, self._scroll_offset, AetherListColors.PANEL_BG, fade_height=self.FADE_HEIGHT)

  def _draw_header(self, rect: rl.Rectangle):
    draw_settings_panel_header(rect, tr("System Settings"),
                                tr("Manage display, backups, connectivity, and device maintenance from one touch-first panel."),
                                max_title_width=0.60, max_subtitle_width=0.62)

    summary_y = rect.y + 48 + self.HEADER_SUBTITLE_HEIGHT + self.HEADER_SUMMARY_GAP
    summary_rect = rl.Rectangle(rect.x, summary_y, rect.width, min(self.HEADER_CARD_HEIGHT, rect.y + rect.height - summary_y))
    self._draw_summary_card(summary_rect)

  def _draw_summary_card(self, rect: rl.Rectangle):
    draw_soft_card(rect, self.PANEL_STYLE.surface_fill, self.PANEL_STYLE.surface_border)
    inset = 18
    left_x = rect.x + inset
    left_w = rect.width * 0.40
    gui_label(rl.Rectangle(left_x, rect.y + 9, left_w, 22), tr("Current Drive State"), 20, AetherListColors.MUTED, FontWeight.MEDIUM)
    gui_label(rl.Rectangle(left_x, rect.y + 33, left_w, 28), self._controller._get_force_drive_state(), 24, AetherListColors.HEADER, FontWeight.MEDIUM)

    control_w = max(300.0, min(420.0, rect.width * 0.34))
    control_x = rect.x + rect.width - control_w - inset

    metric_col_x = left_x + left_w + 24
    metric_col_w = control_x - 24 - metric_col_x
    metric_rows = [
      (tr("Storage"), self._controller.storage_summary()),
      (tr("System Backups"), self._controller.backup_count_text()),
      (tr("Toggle Snapshots"), self._controller.toggle_backup_count_text()),
    ]
    metric_row_h = 18
    metric_row_gap = 6
    metric_start_y = rect.y + 14

    label_font = gui_app.font(FontWeight.MEDIUM)
    for i, (label, value) in enumerate(metric_rows):
      row_y = metric_start_y + i * (metric_row_h + metric_row_gap)
      label_w = measure_text_cached(label_font, label, 18).x + 4
      gui_label(rl.Rectangle(metric_col_x, row_y, label_w, metric_row_h + 2),
                label, 18, AetherListColors.MUTED, FontWeight.MEDIUM)
      value_x = metric_col_x + label_w + 12
      gui_label(rl.Rectangle(value_x, row_y, metric_col_x + metric_col_w - value_x, metric_row_h + 2),
                value, 18, AetherListColors.HEADER, FontWeight.MEDIUM)

    control_rect = rl.Rectangle(control_x, rect.y + 14, control_w, rect.height - 28)
    self._drive_mode_control.render(control_rect)

  def _measure_content_height(self, width: float) -> float:
    content_height = self._measure_active_tab_height(width)
    return self.TAB_HEIGHT + self.TAB_BOTTOM_GAP + content_height

  def _measure_active_tab_height(self, width: float) -> float:
    display_h = self._section_block_height(self._slider_section_height(self._display_slider_keys, width))
    power_h = self._section_block_height(self._slider_section_height(self._power_slider_keys, width))
    backups_h = self._section_block_height(self._section_height(2, self.ROW_HEIGHT))
    maintenance_h = self._section_block_height(self._maintenance_section_content_height())
    if self._active_tab_key == "basics":
      if self._uses_two_columns(width):
        return max(display_h, power_h)
      return self._stacked_section_height([display_h, power_h])

    if self._active_tab_key == "connectivity":
      group_heights = [self._section_block_height(self._section_height(len(self._toggle_defs_for_group(group)), self.ROW_HEIGHT)) for group in self._toggle_groups]
      if self._uses_two_columns(width):
        return max(group_heights)
      return self._stacked_section_height(group_heights)

    if self._uses_two_columns(width):
      return max(backups_h, maintenance_h)
    return self._stacked_section_height([backups_h, maintenance_h])

  def _section_block_height(self, content_height: float) -> float:
    return self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP + content_height + self.SECTION_GAP

  def _slider_section_height(self, keys: list[str], width: float) -> float:
    total = 0.0
    for key in keys:
      adjustor = self._adjustor_rows[key]
      total += adjustor.measure_height(width)
    return total

  def _maintenance_section_content_height(self) -> float:
    support_h = self._section_height(len(self._support_rows), self.ROW_HEIGHT)
    danger_h = self._section_height(len(self._danger_rows), self.ROW_HEIGHT)
    return support_h + 12 + 30 + danger_h

  def _draw_scroll_content(self, rect: rl.Rectangle, width: float):
    self._interactive_rects.clear()
    y = rect.y + self._scroll_offset
    self._draw_tabs(rl.Rectangle(rect.x, y, width, self.TAB_HEIGHT))
    y += self.TAB_HEIGHT + self.TAB_BOTTOM_GAP

    if self._active_tab_key == "basics":
      self._draw_basics_tab(y, rect.x, width)
    elif self._active_tab_key == "connectivity":
      self._draw_connectivity_tab(y, rect.x, width)
    else:
      self._draw_care_tab(y, rect.x, width)

  def _draw_tabs(self, rect: rl.Rectangle):
    if not self._tab_defs:
      return
    available_w = max(1.0, rect.width)
    tab_w = (available_w - self.TAB_GAP * max(0, len(self._tab_defs) - 1)) / max(1, len(self._tab_defs))
    for index, tab in enumerate(self._tab_defs):
      tab_rect = rl.Rectangle(rect.x + index * (tab_w + self.TAB_GAP), rect.y, tab_w, self.TAB_HEIGHT)
      target_id = f"tab:{tab['id']}"
      hovered, pressed = self._interactive_state(target_id, tab_rect, pad_y=4)
      draw_tab_card(
        tab_rect,
        tab["title"],
        self._tab_subtitle(tab["id"]),
        current=self._active_tab_key == tab["id"],
        hovered=hovered,
        pressed=pressed,
        title_size=26,
        subtitle_size=17,
        show_underline=True,
        style=self.PANEL_STYLE,
      )

  def _draw_basics_tab(self, y: float, x: float, width: float):
    if self._uses_two_columns(width):
      column_w = self._column_width(width)
      self._draw_slider_section(y, x, column_w, tr("Display"), self._display_slider_keys)
      self._draw_slider_section(y, x + column_w + self.COLUMN_GAP, column_w, tr("Power"), self._power_slider_keys)
      return
    y = self._draw_slider_section(y, x, width, tr("Display"), self._display_slider_keys)
    self._draw_slider_section(y, x, width, tr("Power"), self._power_slider_keys)

  def _draw_connectivity_tab(self, y: float, x: float, width: float):
    if self._uses_two_columns(width):
      column_w = self._column_width(width)
      self._draw_toggle_group_section(y, x, column_w, self._toggle_groups[0])
      self._draw_toggle_group_section(y, x + column_w + self.COLUMN_GAP, column_w, self._toggle_groups[1])
      return
    current_y = y
    for group in self._toggle_groups:
      current_y = self._draw_toggle_group_section(current_y, x, width, group)

  def _draw_care_tab(self, y: float, x: float, width: float):
    if self._uses_two_columns(width):
      column_w = self._column_width(width)
      self._draw_backups_section(y, x, column_w)
      self._draw_maintenance_section(y, x + column_w + self.COLUMN_GAP, column_w)
      return
    y = self._draw_backups_section(y, x, width)
    self._draw_maintenance_section(y, x, width)

  def _draw_slider_section(self, y: float, x: float, width: float, title: str, keys: list[str]) -> float:
    draw_section_header(rl.Rectangle(x, y, width, self.SECTION_HEADER_HEIGHT), title, style=self.PANEL_STYLE)
    y += self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP
    group_rect = rl.Rectangle(x, y, width, self._slider_section_height(keys, width))
    draw_list_group_shell(group_rect)
    current_y = group_rect.y
    for index, key in enumerate(keys):
      current_y = self._draw_slider_row(rl.Rectangle(group_rect.x, current_y, group_rect.width, 0), key, is_last=index == len(keys) - 1)
    return y + group_rect.height + self.SECTION_GAP

  def _draw_slider_row(self, rect: rl.Rectangle, key: str, is_last: bool) -> float:
    adjustor = self._adjustor_rows[key]
    adjustor.set_is_last(is_last)
    row_h = adjustor.measure_height(rect.width)
    row_rect = rl.Rectangle(rect.x, rect.y, rect.width, row_h)
    if self._ensure_visible_key == key:
      padding = 12.0
      min_offset = min(0.0, self._scroll_rect.y + padding - row_rect.y)
      max_offset = min(0.0, self._scroll_rect.y + self._scroll_rect.height - padding - (row_rect.y + row_rect.height))
      current_offset = self._scroll_panel.get_offset()
      if current_offset < max_offset:
        self._scroll_panel.set_offset(max_offset)
      elif current_offset > min_offset:
        self._scroll_panel.set_offset(min_offset)
      self._ensure_visible_key = None
    adjustor.set_parent_rect(self._scroll_rect)
    adjustor.render(row_rect)
    return rect.y + row_h

  def _draw_toggle_group_section(self, y: float, x: float, width: float, group: dict) -> float:
    toggles = self._toggle_defs_for_group(group)
    trailing_text = tr("{} toggles").format(len(toggles))
    draw_section_header(rl.Rectangle(x, y, width, self.SECTION_HEADER_HEIGHT), group["title"], trailing_text=trailing_text, style=self.PANEL_STYLE)
    y += self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP
    toggle_rect = rl.Rectangle(x, y, width, self._section_height(len(toggles), self.ROW_HEIGHT))
    draw_list_group_shell(toggle_rect)
    for index, toggle_def in enumerate(toggles):
      self._draw_toggle_row(rl.Rectangle(toggle_rect.x, toggle_rect.y + index * self.ROW_HEIGHT, toggle_rect.width, self.ROW_HEIGHT), toggle_def, is_last=index == len(toggles) - 1)
    return y + toggle_rect.height + self.SECTION_GAP

  def _draw_toggle_row(self, rect: rl.Rectangle, toggle_def: dict, is_last: bool):
    target_id = f"toggle:{toggle_def['id']}"
    hovered, pressed = self._interactive_state(target_id, rect)
    is_enabled = toggle_def.get("is_enabled", lambda: True)()
    subtitle = toggle_def.get("disabled_label", "") if not is_enabled and toggle_def.get("disabled_label") else toggle_def["subtitle"]
    draw_settings_list_row(
      rect,
      title=toggle_def["title"],
      subtitle=subtitle,
      toggle_value=toggle_def["get"](),
      enabled=is_enabled,
      hovered=hovered,
      pressed=pressed,
      is_last=is_last,
      show_chevron=False,
      title_size=34,
      subtitle_size=22,
      style=self.PANEL_STYLE,
    )

  def _draw_backups_section(self, y: float, x: float, width: float) -> float:
    draw_section_header(rl.Rectangle(x, y, width, self.SECTION_HEADER_HEIGHT), tr("Backups"), trailing_text=self._controller.backup_status_text(), style=self.PANEL_STYLE)
    y += self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP

    summary_rect = rl.Rectangle(x, y, width, self.ROW_HEIGHT * 2)
    draw_list_group_shell(summary_rect)
    self._draw_backup_manager_row(rl.Rectangle(summary_rect.x, summary_rect.y, summary_rect.width, self.ROW_HEIGHT), "system", is_last=False)
    self._draw_backup_manager_row(rl.Rectangle(summary_rect.x, summary_rect.y + self.ROW_HEIGHT, summary_rect.width, self.ROW_HEIGHT), "toggle", is_last=True)
    return y + summary_rect.height + self.SECTION_GAP

  def _draw_backup_manager_row(self, rect: rl.Rectangle, backup_kind: str, is_last: bool):
    target_id = f"backup:{backup_kind}"
    hovered, pressed = self._interactive_state(target_id, rect)
    if backup_kind == "system":
      title = tr("System Backups")
      subtitle = self._controller.latest_backup_summary()
      count = self._controller.backup_count()
    else:
      title = tr("Toggle Snapshots")
      subtitle = self._controller.latest_toggle_backup_summary()
      count = self._controller.toggle_backup_count()
    action_text = tr("Create") if count == 0 else tr("Manage")
    draw_selection_list_row(
      rect,
      title=title,
      subtitle=subtitle,
      action_text=action_text,
      hovered=hovered,
      pressed=pressed,
      is_last=is_last,
      action_width=188,
      action_pill=True,
      action_pill_height=44,
      action_pill_width=108 if count == 0 else self.ACTION_PILL_WIDTH,
      title_size=34,
      subtitle_size=22,
      action_text_size=18,
      row_separator=self.PANEL_STYLE.divider_color,
      action_fill=AetherListColors.CURRENT_BG,
      action_border=rl.Color(89, 116, 151, 42),
      action_text_color=AetherListColors.HEADER,
    )

  def _draw_maintenance_section(self, y: float, x: float, width: float):
    draw_section_header(rl.Rectangle(x, y, width, self.SECTION_HEADER_HEIGHT), tr("Support & Maintenance"), style=self.PANEL_STYLE)
    y += self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP

    support_rect = rl.Rectangle(x, y, width, self._section_height(len(self._support_rows), self.ROW_HEIGHT))
    draw_list_group_shell(support_rect)
    for index, row in enumerate(self._support_rows):
      row_rect = rl.Rectangle(support_rect.x, support_rect.y + index * self.ROW_HEIGHT, support_rect.width, self.ROW_HEIGHT)
      self._draw_action_row(row_rect, row, is_last=index == len(self._support_rows) - 1)
    y += support_rect.height + 12

    danger_title_rect = rl.Rectangle(x, y, width, 22)
    gui_label(danger_title_rect, tr("Danger Zone"), 20, AetherListColors.DANGER, FontWeight.MEDIUM)
    y += 30

    danger_rect = rl.Rectangle(x, y, width, self._section_height(len(self._danger_rows), self.ROW_HEIGHT))
    draw_list_group_shell(danger_rect, fill=rl.Color(173, 78, 90, 10), border=rl.Color(173, 78, 90, 30))
    for index, row in enumerate(self._danger_rows):
      row_rect = rl.Rectangle(danger_rect.x, danger_rect.y + index * self.ROW_HEIGHT, danger_rect.width, self.ROW_HEIGHT)
      self._draw_action_row(row_rect, row, is_last=index == len(self._danger_rows) - 1, danger=True)

  def _draw_action_row(self, rect: rl.Rectangle, row: dict, is_last: bool, *, danger: bool = False):
    target_id = f"action:{row['id']}"
    hovered, pressed = self._interactive_state(target_id, rect)
    action_fill = rl.Color(173, 78, 90, 22) if danger else rl.Color(255, 255, 255, 8)
    action_border = rl.Color(173, 78, 90, 48) if danger else rl.Color(255, 255, 255, 24)
    action_text_color = AetherListColors.HEADER if not danger else rl.Color(244, 214, 219, 255)
    draw_selection_list_row(
      rect,
      title=row["title"],
      subtitle=row["subtitle"],
      action_text=row["action"],
      hovered=hovered,
      pressed=pressed,
      is_last=is_last,
      action_width=188,
      action_pill=True,
      action_pill_height=44,
      action_pill_width=self.DANGER_PILL_WIDTH if danger else self.ACTION_PILL_WIDTH,
      title_size=34,
      subtitle_size=22,
      action_text_size=18,
      row_separator=self.PANEL_STYLE.divider_color,
      action_fill=action_fill,
      action_border=action_border,
      action_text_color=action_text_color,
      title_color=AetherListColors.HEADER if not danger else rl.Color(249, 229, 233, 255),
      subtitle_color=AetherListColors.SUBTEXT if not danger else rl.Color(203, 171, 178, 255),
    )

class StarPilotSystemLayout(_SettingsPage):
  _BACKUP_NAME_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")

  def __init__(self):
    super().__init__()
    self._keyboard = Keyboard(min_text_size=0)
    self._storage_text = "0 MB"
    self._storage_updated_at = 0.0
    self._storage_refresh_pending = False
    self._storage_refresh_generation = 0
    self._pending_storage_text: tuple[int, str] | None = None
    self._manager_view = SystemSettingsManagerView(self)
    self._refresh_storage_cache(force=True)

  def show_event(self):
    self._refresh_storage_cache(force=True)
    super().show_event()

  def _render(self, rect: rl.Rectangle):
    if self._pending_storage_text is not None:
      generation, storage_text = self._pending_storage_text
      self._pending_storage_text = None
      if generation == self._storage_refresh_generation:
        self._storage_text = storage_text
        self._storage_updated_at = rl.get_time()
      self._storage_refresh_pending = False
    self._refresh_storage_cache()
    super()._render(rect)

  def _refresh_storage_cache(self, force: bool = False):
    now = rl.get_time()
    if self._storage_refresh_pending:
      return
    if not force and (now - self._storage_updated_at) < 5.0:
      return

    generation = self._storage_refresh_generation + 1
    self._storage_refresh_generation = generation

    def refresh_worker():
      result: str | None = None
      try:
        result = self._get_storage()
      finally:
        if result is None:
          self._storage_refresh_pending = False
        else:
          self._pending_storage_text = (generation, result)

    self._storage_refresh_pending = True
    self._storage_updated_at = now
    threading.Thread(target=refresh_worker, daemon=True).start()

  def storage_summary(self) -> str:
    return self._storage_text

  def backup_count_text(self) -> str:
    count = len(self._get_backups("backups"))
    return tr("None") if count == 0 else tr("{} saved").format(count)

  def backup_count(self) -> int:
    return len(self._get_backups("backups"))

  def toggle_backup_count_text(self) -> str:
    count = len(self._get_backups("toggle_backups"))
    return tr("None") if count == 0 else tr("{} saved").format(count)

  def toggle_backup_count(self) -> int:
    return len(self._get_backups("toggle_backups"))

  def latest_backup_summary(self) -> str:
    backups = self._get_backups("backups")
    if not backups:
      return tr("No full-system backups saved yet.")
    return backups[-1]

  def latest_toggle_backup_summary(self) -> str:
    backups = self._get_backups("toggle_backups")
    if not backups:
      return tr("No toggle snapshots saved yet.")
    return backups[-1]

  def backup_status_text(self) -> str:
    system_count = len(self._get_backups("backups"))
    toggle_count = len(self._get_backups("toggle_backups"))
    return tr("{} full • {} toggle").format(system_count, toggle_count)

  def open_backup_manager(self, backup_kind: str):
    if backup_kind == "system":
      options = [tr("Create Backup"), tr("Restore Backup"), tr("Delete Backup")]
      title = tr("System Backups")
    else:
      options = [tr("Save Toggle Snapshot"), tr("Restore Toggle Snapshot"), tr("Delete Toggle Snapshot")]
      title = tr("Toggle Snapshots")

    def on_select(res):
      if res != DialogResult.CONFIRM or not dialog.selection:
        return
      selection = dialog.selection
      if selection == options[0]:
        if backup_kind == "system":
          self._on_create_backup()
        else:
          self._on_create_toggle_backup()
      elif selection == options[1]:
        if backup_kind == "system":
          self._on_restore_backup()
        else:
          self._on_restore_toggle_backup()
      elif selection == options[2]:
        if backup_kind == "system":
          self._on_delete_backup()
        else:
          self._on_delete_toggle_backup()

    dialog = MultiOptionDialog(title, options, callback=on_select)
    gui_app.push_widget(dialog)

  def handle_action(self, action_id: str):
    if action_id == "ScreenManagement":
      self._params.put_bool("ScreenManagement", not self._params.get_bool("ScreenManagement"))
    elif action_id == "DeviceManagement":
      self._params.put_bool("DeviceManagement", not self._params.get_bool("DeviceManagement"))
    elif action_id == "Storage":
      self._on_delete_driving_data()
    elif action_id == "ErrorLogs":
      self._on_delete_error_logs()
    elif action_id == "CreateBackup":
      self._on_create_backup()
    elif action_id == "RestoreBackup":
      self._on_restore_backup()
    elif action_id == "DeleteBackup":
      self._on_delete_backup()
    elif action_id == "CreateToggleBackup":
      self._on_create_toggle_backup()
    elif action_id == "RestoreToggleBackup":
      self._on_restore_toggle_backup()
    elif action_id == "DeleteToggleBackup":
      self._on_delete_toggle_backup()
    elif action_id == "DriveDefault":
      self._params.put_bool("ForceOffroad", False)
      self._params.put_bool("ForceOnroad", False)
    elif action_id == "DriveOnroad":
      self._params.put_bool("ForceOnroad", True)
      self._params.put_bool("ForceOffroad", False)
    elif action_id == "DriveOffroad":
      self._params.put_bool("ForceOffroad", True)
      self._params.put_bool("ForceOnroad", False)
    elif action_id == "FlashPanda":
      self._on_flash_panda()
    elif action_id == "ReportIssue":
      self._on_report_issue()
    elif action_id == "ResetDefaults":
      self._on_reset_defaults()
    elif action_id == "ResetStock":
      self._on_reset_stock()

  def _set_brightness(self, key, val):
    self._params.put_int(key, int(val))
    if key in ("ScreenBrightnessOnroad", "ScreenBrightness") and hasattr(HARDWARE, 'set_brightness'):
        HARDWARE.set_brightness(int(val))

  def _get_konik_state(self):
    if Path("/data/not_vetted").exists():
      return True
    return self._params.get_bool("UseKonikServer")

  def _on_konik_toggle(self, state):
    self._params.put_bool("UseKonikServer", state)
    cache_path = Path("/cache/use_konik")
    if state:
      cache_path.parent.mkdir(parents=True, exist_ok=True)
      cache_path.touch()
    else:
      if cache_path.exists():
        cache_path.unlink()
    if ui_state.started:
      gui_app.push_widget(
        ConfirmDialog(
          tr("Reboot required. Reboot now?"), tr("Reboot"), tr("Cancel"), callback=lambda res: HARDWARE.reboot() if res == DialogResult.CONFIRM else None
        )
      )

  def _on_higher_bitrate_toggle(self, state):
    self._params.put_bool("HigherBitrate", state)
    cache_path = Path("/cache/use_HD")
    if state:
      cache_path.parent.mkdir(parents=True, exist_ok=True)
      cache_path.touch()
    else:
      if cache_path.exists():
        cache_path.unlink()
    if ui_state.started:
      gui_app.push_widget(
        ConfirmDialog(
          tr("Reboot required. Reboot now?"), tr("Reboot"), tr("Cancel"), callback=lambda res: HARDWARE.reboot() if res == DialogResult.CONFIRM else None
        )
      )

  def _get_storage(self):
    paths = ["/data/media/0/osm/offline", "/data/media/0/realdata", "/data/backups"]
    total = 0
    for p in paths:
      pp = Path(p)
      if pp.exists():
        total += sum(f.stat().st_size for f in pp.rglob('*') if f.is_file())
    mb = total / (1024 * 1024)
    if mb > 1024:
      return f"{(mb / 1024):.2f} GB"
    return f"{mb:.2f} MB"

  def _on_delete_driving_data(self):
    def _do_delete(res):
      if res == DialogResult.CONFIRM:
        def _task():
          drive_paths = ["/data/media/0/realdata/", "/data/media/0/realdata_HD/", "/data/media/0/realdata_konik/"]
          for path in drive_paths:
            p = Path(path)
            if p.exists():
              for entry in p.iterdir():
                if entry.is_dir():
                  shutil.rmtree(entry, ignore_errors=True)
        threading.Thread(target=_task, daemon=True).start()
        gui_app.push_widget(alert_dialog(tr("Driving data deletion started.")))
    gui_app.push_widget(ConfirmDialog(tr("Delete all driving data and footage?"), tr("Delete"), callback=_do_delete))

  def _on_delete_error_logs(self):
    def _do_delete(res):
      if res == DialogResult.CONFIRM:
        shutil.rmtree("/data/error_logs", ignore_errors=True)
        os.makedirs("/data/error_logs", exist_ok=True)
        gui_app.push_widget(alert_dialog(tr("Error logs deleted.")))
    gui_app.push_widget(ConfirmDialog(tr("Delete all error logs?"), tr("Delete"), callback=_do_delete))

  def _get_backups(self, folder="backups"):
    b_dir = Path(f"/data/{folder}")
    if not b_dir.exists():
      return []
    if folder == "backups":
      entries = [f for f in b_dir.glob("*.tar.zst") if "in_progress" not in f.name]
    else:
      entries = [d for d in b_dir.iterdir() if d.is_dir() and "in_progress" not in d.name]
    entries.sort(key=lambda item: item.stat().st_mtime if item.exists() else 0.0, reverse=True)
    return [entry.name for entry in entries]

  def _sanitize_backup_name(self, raw_name: str, prefix: str) -> str:
    sanitized = self._BACKUP_NAME_SANITIZE_RE.sub("_", raw_name.strip())
    sanitized = sanitized.strip("._-")
    if not sanitized:
      sanitized = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return sanitized

  def _on_create_backup(self):
    def on_name(res, name):
      if res == DialogResult.CONFIRM:
        safe_name = self._sanitize_backup_name(name or "", "backup")
        backup_path = f"/data/backups/{safe_name}.tar.zst"
        if Path(backup_path).exists():
          gui_app.push_widget(alert_dialog(tr("A backup with this name already exists.")))
          return
        gui_app.push_widget(alert_dialog(tr("Backup creation started.")))
        def _task():
          os.makedirs("/data/backups", exist_ok=True)
          subprocess.run(["tar", "--use-compress-program=zstd", "-cf", backup_path, "/data/openpilot"])
        threading.Thread(target=_task, daemon=True).start()
    self._keyboard.reset(min_text_size=0)
    self._keyboard.set_title(tr("Name your backup"), "")
    self._keyboard.set_text("")
    self._keyboard.set_callback(lambda result: on_name(result, self._keyboard.text))
    gui_app.push_widget(self._keyboard)

  def _on_restore_backup(self):
    backups = self._get_backups("backups")
    if not backups:
      gui_app.push_widget(alert_dialog(tr("No backups found.")))
      return

    def _on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        gui_app.push_widget(alert_dialog(tr("Restoring... device will reboot.")))
        def _task():
          shutil.rmtree("/data/openpilot", ignore_errors=True)
          os.makedirs("/data/openpilot", exist_ok=True)
          subprocess.run(["tar", "--use-compress-program=zstd", "-xf", f"/data/backups/{dialog.selection}", "-C", "/"])
          os.system("reboot")
        threading.Thread(target=_task, daemon=True).start()

    dialog = MultiOptionDialog(tr("Select Backup"), backups, callback=_on_select)
    gui_app.push_widget(dialog)

  def _on_delete_backup(self):
    backups = self._get_backups("backups")
    if not backups:
      gui_app.push_widget(alert_dialog(tr("No backups found.")))
      return

    def _on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        backup_name = dialog.selection

        def _on_confirm(confirm_res):
          if confirm_res == DialogResult.CONFIRM:
            os.remove(f"/data/backups/{backup_name}")
            gui_app.push_widget(alert_dialog(tr("Backup deleted.")))

        gui_app.push_widget(ConfirmDialog(tr("Delete backup '{}'?").format(backup_name), tr("Delete"), callback=_on_confirm))

    dialog = MultiOptionDialog(tr("Delete Backup"), backups, callback=_on_select)
    gui_app.push_widget(dialog)

  def _on_create_toggle_backup(self):
    def on_name(res, name):
      if res == DialogResult.CONFIRM:
        safe_name = self._sanitize_backup_name(name or "", "toggle_backup")
        backup_path = Path(f"/data/toggle_backups/{safe_name}")
        if backup_path.exists():
          gui_app.push_widget(alert_dialog(tr("A toggle backup with this name already exists.")))
          return
        os.makedirs(backup_path, exist_ok=True)
        shutil.copytree("/data/params/d", str(backup_path), dirs_exist_ok=True)
        gui_app.push_widget(alert_dialog(tr("Toggle backup created.")))
    self._keyboard.reset(min_text_size=0)
    self._keyboard.set_title(tr("Name your toggle backup"), "")
    self._keyboard.set_text("")
    self._keyboard.set_callback(lambda result: on_name(result, self._keyboard.text))
    gui_app.push_widget(self._keyboard)

  def _on_restore_toggle_backup(self):
    backups = self._get_backups("toggle_backups")
    if not backups:
      gui_app.push_widget(alert_dialog(tr("No toggle backups found.")))
      return

    def _on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        def on_confirm(r2):
          if r2 == DialogResult.CONFIRM:
            src = Path(f"/data/toggle_backups/{dialog.selection}")
            params_dir = Path("/data/params/d")
            for old_key, new_key in LEGACY_STARPILOT_PARAM_RENAMES.items():
              if (src / old_key).exists():
                (params_dir / new_key).unlink(missing_ok=True)
            shutil.copytree(str(src), "/data/params/d", dirs_exist_ok=True)
            for old_key, new_key in LEGACY_STARPILOT_PARAM_RENAMES.items():
              old_path = params_dir / old_key
              new_path = params_dir / new_key
              if old_path.exists():
                old_path.replace(new_path)
            gui_app.push_widget(alert_dialog(tr("Toggles restored.")))
        gui_app.push_widget(ConfirmDialog(tr("This will overwrite your current toggles."), tr("Restore"), callback=on_confirm))

    dialog = MultiOptionDialog(tr("Select Toggle Backup"), backups, callback=_on_select)
    gui_app.push_widget(dialog)

  def _on_delete_toggle_backup(self):
    backups = self._get_backups("toggle_backups")
    if not backups:
      gui_app.push_widget(alert_dialog(tr("No toggle backups found.")))
      return

    def _on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        backup_name = dialog.selection

        def _on_confirm(confirm_res):
          if confirm_res == DialogResult.CONFIRM:
            shutil.rmtree(f"/data/toggle_backups/{backup_name}", ignore_errors=True)
            gui_app.push_widget(alert_dialog(tr("Toggle backup deleted.")))

        gui_app.push_widget(ConfirmDialog(tr("Delete toggle backup '{}'?").format(backup_name), tr("Delete"), callback=_on_confirm))

    dialog = MultiOptionDialog(tr("Delete Toggle Backup"), backups, callback=_on_select)
    gui_app.push_widget(dialog)

  def _get_force_drive_state(self):
    if self._params.get_bool("ForceOnroad"):
      return tr("Onroad")
    if self._params.get_bool("ForceOffroad"):
      return tr("Offroad")
    return tr("Default")

  def _on_flash_panda(self):
    def _do_flash(res):
      if res == DialogResult.CONFIRM:
        self._params_memory.put_bool("FlashPanda", True)
        gui_app.push_widget(alert_dialog(tr("Panda flashing started. Device will reboot when finished.")))
    gui_app.push_widget(ConfirmDialog(tr("Flash Panda firmware?"), tr("Flash"), callback=_do_flash))

  def _on_report_issue(self):
    def on_category(res):
      if res != DialogResult.CONFIRM or not dialog.selection:
        return
      discord_user = self._params.get("DiscordUsername", encoding='utf-8') or ""
      def on_discord(res2, username):
        if res2 == DialogResult.CONFIRM and username:
          self._params.put("DiscordUsername", username)
          report = json.dumps({"DiscordUser": username, "Issue": dialog.selection})
          self._params_memory.put("IssueReported", report)
          gui_app.push_widget(alert_dialog(tr("Issue reported. Thank you!")))
      self._keyboard.reset(min_text_size=1)
      self._keyboard.set_title(tr("Discord Username"), "")
      self._keyboard.set_text(discord_user or "")
      self._keyboard.set_callback(lambda result: on_discord(result, self._keyboard.text))
      gui_app.push_widget(self._keyboard)
    dialog = MultiOptionDialog(tr("Select Issue"), REPORT_CATEGORIES, callback=on_category)
    gui_app.push_widget(dialog)

  def _on_reset_defaults(self):
    def _do_reset(res):
      if res == DialogResult.CONFIRM:
        all_keys = self._params.all_keys()
        for k in all_keys:
          if k in EXCLUDED_KEYS:
            continue
          default = self._params.get_default_value(k)
          if default is not None:
            self._params.put(k, default)
        gui_app.push_widget(alert_dialog(tr("Toggles reset to defaults.")))
    gui_app.push_widget(ConfirmDialog(tr("Reset all toggles to defaults?"), tr("Reset"), callback=_do_reset))

  def _on_reset_stock(self):
    def _do_reset(res):
      if res == DialogResult.CONFIRM:
        all_keys = self._params.all_keys()
        for k in all_keys:
          if k in EXCLUDED_KEYS:
            continue
          stock = self._params.get_stock_value(k)
          if stock is not None:
            self._params.put(k, stock)
        gui_app.push_widget(alert_dialog(tr("Toggles reset to stock openpilot.")))
    gui_app.push_widget(ConfirmDialog(tr("Reset all toggles to stock openpilot?"), tr("Reset"), callback=_do_reset))
