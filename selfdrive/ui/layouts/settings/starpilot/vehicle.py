from __future__ import annotations

import pyray as rl

from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import FontWeight, MouseEvent, MousePos, gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.selfdrive.ui.layouts.settings.starpilot.panel import StarPilotPanel
from openpilot.selfdrive.ui.layouts.settings.starpilot.aethergrid import (
  AETHER_LIST_METRICS,
  AetherListColors,
  AetherScrollbar,
  AetherSliderDialog,
  DEFAULT_PANEL_STYLE,
  _point_hits,
  draw_list_group_shell,
  draw_list_scroll_fades,
  draw_metric_strip,
  draw_section_header,
  draw_selection_list_row,
  draw_settings_list_row,
  draw_settings_panel_header,
  draw_soft_card,
  draw_tab_card,
  init_list_panel,
)
from openpilot.selfdrive.ui.lib.starpilot_state import starpilot_state
from openpilot.selfdrive.ui.mici.layouts.settings.fingerprint_catalog import (
  FingerprintModelOption,
  get_fingerprint_catalog,
  shorten_model_label,
)


ACTION_OPTIONS = [
  {"id": 0, "name": "No Action"},
  {"id": 1, "name": "Change Personality", "requires_longitudinal": True},
  {"id": 2, "name": "Force Coast", "requires_longitudinal": True},
  {"id": 3, "name": "Pause Steering"},
  {"id": 4, "name": "Pause Accel/Brake", "requires_longitudinal": True},
  {"id": 5, "name": "Toggle Experimental", "requires_longitudinal": True},
  {"id": 6, "name": "Toggle Traffic", "requires_longitudinal": True},
  {"id": 7, "name": "Toggle Switchback"},
  {"id": 8, "name": "Create Bookmark"},
]
ACTION_NAMES = [o["name"] for o in ACTION_OPTIONS]
ACTION_IDS = {o["name"]: o["id"] for o in ACTION_OPTIONS}
ACTION_NAME_BY_ID = {o["id"]: o["name"] for o in ACTION_OPTIONS}


def _lock_doors_timer_labels():
  labels: dict[float, str] = {0.0: tr("Never")}
  for i in range(5, 305, 5):
    labels[float(i)] = f"{i}s"
  return labels


class VehicleSettingsManagerView(Widget):
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

  PANEL_STYLE = DEFAULT_PANEL_STYLE

  def __init__(self, controller: "StarPilotVehicleSettingsLayout"):
    super().__init__()
    self._controller = controller
    self._scroll_panel = GuiScrollPanel2(horizontal=False)
    self._scrollbar = AetherScrollbar()
    self._content_height = 0.0
    self._scroll_offset = 0.0
    self._interactive_rects: dict[str, rl.Rectangle] = {}
    self._pressed_target: str | None = None
    self._can_click = True
    self._active_tab_key = "identity"
    self._shell_rect = rl.Rectangle(0, 0, 0, 0)
    self._scroll_rect = rl.Rectangle(0, 0, 0, 0)

    self._tab_defs = [
      {"id": "identity", "title": tr("Identity")},
      {"id": "features", "title": tr("Features")},
      {"id": "controls", "title": tr("Controls")},
    ]

  def _uses_two_columns(self, width: float) -> bool:
    return width >= self.TWO_COLUMN_BREAKPOINT

  def _column_width(self, width: float) -> float:
    return (width - self.COLUMN_GAP) / 2 if self._uses_two_columns(width) else width

  def _section_height(self, count: int, row_height: float) -> float:
    return 0.0 if count <= 0 else count * row_height

  def _section_block_height(self, content_height: float) -> float:
    if content_height <= 0:
      return 0.0
    return self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP + content_height + self.SECTION_GAP

  def _stacked_section_height(self, sections: list[float]) -> float:
    if not sections:
      return 0.0
    return max(0.0, sum(sections) - self.SECTION_GAP)

  def _interactive_state(self, target_id: str, rect: rl.Rectangle, *, pad_y: float = 0) -> tuple[bool, bool]:
    self._interactive_rects[target_id] = rect
    hovered = _point_hits(gui_app.last_mouse_event.pos, rect, self._scroll_rect, pad_x=6, pad_y=pad_y)
    return hovered, self._pressed_target == target_id

  def _clear_state(self):
    self._pressed_target = None
    self._can_click = True

  def show_event(self):
    super().show_event()
    self._clear_state()

  def hide_event(self):
    super().hide_event()
    self._clear_state()

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
      return
    if prefix == "toggle":
      self._controller._on_toggle(value)
    elif prefix == "select":
      self._controller._on_select(value)

  def _tab_subtitle(self, tab_id: str) -> str:
    cs = starpilot_state.car_state
    if tab_id == "identity":
      return tr("Make, model, and fingerprint")
    if tab_id == "features":
      count = 1
      if cs.isGM: count += 4
      if cs.isGM and cs.isVolt and not cs.hasSNG: count += 1
      if cs.isHKG and cs.isHKGCanFd: count += 2
      if cs.isSubaru: count += 1
      if cs.isToyota: count += 4
      if cs.isToyota and not cs.hasSNG: count += 1
      if cs.isToyota and cs.hasOpenpilotLongitudinal: count += 1
      if cs.isHKGCanFd and cs.hasOpenpilotLongitudinal: count += 1
      return tr("{} settings").format(count)
    if tab_id == "controls":
      count = 7
      if not cs.isSubaru and not (cs.lkasAllowedForAOL and self._controller._params.get_bool("AlwaysOnLateral") and self._controller._params.get_bool("AlwaysOnLateralLKAS")):
        count += 1
      if cs.hasModeStarButtons: count += 6
      return tr("{} buttons").format(count)
    return ""

  def _render(self, rect: rl.Rectangle):
    self.set_rect(rect)
    self._interactive_rects.clear()

    frame, scroll_rect, content_width = init_list_panel(rect, self.PANEL_STYLE)
    self._shell_rect = frame.shell
    self._scroll_rect = scroll_rect

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
    draw_settings_panel_header(rect, tr("Vehicle Settings"),
                                tr("Configure vehicle fingerprint, driving features, and steering controls."),
                                subtitle_size=22)

    summary_y = rect.y + 48 + self.HEADER_SUBTITLE_HEIGHT + self.HEADER_SUMMARY_GAP
    summary_rect = rl.Rectangle(rect.x, summary_y, rect.width, min(self.HEADER_CARD_HEIGHT, rect.y + rect.height - summary_y))
    self._draw_summary_card(summary_rect)

  def _draw_summary_card(self, rect: rl.Rectangle):
    draw_soft_card(rect, self.PANEL_STYLE.surface_fill, self.PANEL_STYLE.surface_border)
    inset = 18
    left_x = rect.x + inset
    left_w = rect.width * 0.40

    make = self._controller._get_display_make()
    model = self._controller._get_display_model()
    vehicle_name = f"{make} {model}" if make != tr("None") else tr("No vehicle selected")

    gui_label(rl.Rectangle(left_x, rect.y + 10, left_w, 22), tr("Current Vehicle"), 20, AetherListColors.MUTED, FontWeight.MEDIUM)
    gui_label(rl.Rectangle(left_x, rect.y + 34, left_w, 30), vehicle_name, 26, AetherListColors.HEADER, FontWeight.BOLD)

    cs = starpilot_state.car_state
    metrics = []
    if cs.hasRadar:
      metrics.append((tr("Radar"), tr("Yes")))
    if cs.hasOpenpilotLongitudinal:
      metrics.append((tr("Long"), tr("Yes")))
    if cs.hasBSM:
      metrics.append((tr("BSM"), tr("Yes")))
    if cs.hasSNG:
      metrics.append((tr("SNG"), tr("Yes")))

    if metrics:
      draw_metric_strip(
        rl.Rectangle(left_x, rect.y + 72, max(240.0, rect.width * 0.38), 30),
        metrics,
        style=self.PANEL_STYLE,
        label_top_offset=0,
        value_top_offset=14,
        divider_top_offset=2,
        divider_bottom_offset=16,
      )

    right_x = rect.x + rect.width * 0.42
    right_w = rect.width * 0.58 - inset

    hardware_items = []
    if cs.canUsePedal:
      hardware_items.append(tr("Pedal"))
    if cs.hasSASCM:
      hardware_items.append(tr("SASCM"))
    if cs.canUseSDSU:
      hardware_items.append(tr("SDSU"))
    if cs.hasZSS:
      hardware_items.append(tr("ZSS"))

    hw_text = ", ".join(hardware_items) if hardware_items else tr("Standard")
    gui_label(rl.Rectangle(right_x, rect.y + 10, right_w, 22), tr("Hardware"), 20, AetherListColors.MUTED, FontWeight.MEDIUM)
    gui_label(rl.Rectangle(right_x, rect.y + 34, right_w, 26), hw_text, 24, AetherListColors.HEADER, FontWeight.MEDIUM)

    fingerprint_state = tr("Forced") if self._controller._params.get_bool("ForceFingerprint") else tr("Auto")
    gui_label(rl.Rectangle(right_x, rect.y + 66, right_w, 20), tr("Fingerprint"), 18, AetherListColors.MUTED, FontWeight.MEDIUM)
    gui_label(rl.Rectangle(right_x, rect.y + 84, right_w, 20), fingerprint_state, 18, AetherListColors.HEADER, FontWeight.MEDIUM)

  def _measure_content_height(self, width: float) -> float:
    content_height = self._measure_active_tab_height(width)
    return self.TAB_HEIGHT + self.TAB_BOTTOM_GAP + content_height

  def _measure_active_tab_height(self, width: float) -> float:
    if self._active_tab_key == "identity":
      return self._section_block_height(self._section_height(3, self.ROW_HEIGHT))
    if self._active_tab_key == "features":
      rows = self._build_driving_rows()
      if self._uses_two_columns(width):
        max_per_col = (len(rows) + 1) // 2
        return self._section_block_height(self._section_height(max_per_col, self.ROW_HEIGHT))
      return self._section_block_height(self._section_height(len(rows), self.ROW_HEIGHT))
    if self._active_tab_key == "controls":
      rows = self._build_steering_rows()
      if self._uses_two_columns(width):
        max_per_col = (len(rows) + 1) // 2
        return self._section_block_height(self._section_height(max_per_col, self.ROW_HEIGHT))
      return self._section_block_height(self._section_height(len(rows), self.ROW_HEIGHT))
    return 0

  def _draw_scroll_content(self, rect: rl.Rectangle, width: float):
    self._interactive_rects.clear()
    y = rect.y + self._scroll_offset
    self._draw_tabs(rl.Rectangle(rect.x, y, width, self.TAB_HEIGHT))
    y += self.TAB_HEIGHT + self.TAB_BOTTOM_GAP

    if self._active_tab_key == "identity":
      self._draw_identity_tab(y, rect.x, width)
    elif self._active_tab_key == "features":
      self._draw_features_tab(y, rect.x, width)
    else:
      self._draw_controls_tab(y, rect.x, width)

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

  def _draw_identity_tab(self, y: float, x: float, width: float):
    rows = [
      {"target_id": "select:CarMake", "type": "select", "title": tr("Car Make"),
       "get_value": self._controller._get_display_make, "pill_width": 160},
      {"target_id": "select:CarModel", "type": "select", "title": tr("Car Model"),
       "get_value": self._controller._get_display_model, "pill_width": 160},
      {"target_id": "toggle:ForceFingerprint", "type": "toggle", "title": tr("Disable Fingerprinting"),
       "subtitle": tr("Manually select vehicle instead of auto-detecting."),
       "get_state": lambda: self._controller._params.get_bool("ForceFingerprint")},
    ]
    draw_section_header(rl.Rectangle(x, y, width, self.SECTION_HEADER_HEIGHT), tr("Vehicle Identity"), style=self.PANEL_STYLE)
    y += self.SECTION_HEADER_HEIGHT + self.SECTION_HEADER_GAP
    container_rect = rl.Rectangle(x, y, width, len(rows) * self.ROW_HEIGHT)
    draw_list_group_shell(container_rect)
    for index, row in enumerate(rows):
      row_rect = rl.Rectangle(x, y + index * self.ROW_HEIGHT, width, self.ROW_HEIGHT)
      self._draw_row(row_rect, row, is_last=index == len(rows) - 1)

  def _draw_features_tab(self, y: float, x: float, width: float):
    rows = self._build_driving_rows()
    if not rows:
      return
    if self._uses_two_columns(width):
      column_w = self._column_width(width)
      mid = len(rows) // 2
      self._draw_row_group(y, x, column_w, rows[:mid])
      self._draw_row_group(y, x + column_w + self.COLUMN_GAP, column_w, rows[mid:])
    else:
      self._draw_row_group(y, x, width, rows)

  def _draw_controls_tab(self, y: float, x: float, width: float):
    rows = self._build_steering_rows()
    if not rows:
      return
    if self._uses_two_columns(width):
      column_w = self._column_width(width)
      mid = len(rows) // 2
      self._draw_row_group(y, x, column_w, rows[:mid])
      self._draw_row_group(y, x + column_w + self.COLUMN_GAP, column_w, rows[mid:])
    else:
      self._draw_row_group(y, x, width, rows)

  def _draw_row_group(self, y: float, x: float, width: float, rows: list[dict]):
    if not rows:
      return y
    container_rect = rl.Rectangle(x, y, width, len(rows) * self.ROW_HEIGHT)
    draw_list_group_shell(container_rect)
    for index, row in enumerate(rows):
      row_rect = rl.Rectangle(x, y + index * self.ROW_HEIGHT, width, self.ROW_HEIGHT)
      self._draw_row(row_rect, row, is_last=index == len(rows) - 1)
    return y + len(rows) * self.ROW_HEIGHT + self.SECTION_GAP

  def _draw_row(self, rect: rl.Rectangle, row: dict, is_last: bool):
    target_id = row["target_id"]
    hovered, pressed = self._interactive_state(target_id, rect)
    row_type = row.get("type", "toggle")

    if row_type == "toggle":
      draw_settings_list_row(
        rect, title=row["title"], subtitle=row.get("subtitle", ""),
        toggle_value=row["get_state"](), hovered=hovered, pressed=pressed,
        is_last=is_last, show_chevron=False, title_size=34, subtitle_size=22,
        style=self.PANEL_STYLE,
      )
    elif row_type == "select":
      draw_selection_list_row(
        rect, title=row["title"], subtitle=row.get("subtitle", ""),
        action_text=row["get_value"](), hovered=hovered, pressed=pressed,
        is_last=is_last, action_width=188, action_pill=True,
        action_pill_width=row.get("pill_width", 108), action_pill_height=44,
        title_size=34, subtitle_size=22, action_text_size=18,
        row_separator=self.PANEL_STYLE.divider_color,
        action_fill=self.PANEL_STYLE.current_fill,
        action_border=self.PANEL_STYLE.current_border,
        action_text_color=AetherListColors.HEADER,
      )
    elif row_type == "info":
      draw_settings_list_row(
        rect, title=row["title"], value=row["get_value"](),
        hovered=False, pressed=False, is_last=is_last,
        show_chevron=False, title_size=34, subtitle_size=22,
        style=self.PANEL_STYLE,
      )

  def _build_driving_rows(self) -> list[dict]:
    cs = starpilot_state.car_state
    rows = []
    rows.append({"target_id": "toggle:DisableOpenpilotLongitudinal", "type": "toggle",
                  "title": tr("Disable openpilot Long"), "subtitle": tr("Revert to stock longitudinal control."),
                  "get_state": lambda: self._controller._params.get_bool("DisableOpenpilotLongitudinal")})

    if cs.isGM and (cs.hasPedal or cs.canUsePedal):
      rows.append({"target_id": "toggle:GMPedalLongitudinal", "type": "toggle",
                    "title": tr("Pedal for Long"), "get_state": lambda: self._controller._params.get_bool("GMPedalLongitudinal")})
      rows.append({"target_id": "toggle:GMDashSpoofOffsets", "type": "toggle",
                    "title": tr("Offsets on Dash Spoof"), "get_state": lambda: self._controller._params.get_bool("GMDashSpoofOffsets")})
    if cs.isGM:
      rows.append({"target_id": "toggle:LongPitch", "type": "toggle",
                    "title": tr("Smooth Pedal on Hills"), "get_state": lambda: self._controller._params.get_bool("LongPitch")})
      rows.append({"target_id": "toggle:RemoteStartBootsComma", "type": "toggle",
                    "title": tr("Remote Start Panda"), "get_state": lambda: self._controller._params.get_bool("RemoteStartBootsComma")})
    if cs.isGM and cs.isVolt and not cs.hasSNG:
      rows.append({"target_id": "toggle:VoltSNG", "type": "toggle",
                    "title": tr("Volt SNG Hack"), "get_state": lambda: self._controller._params.get_bool("VoltSNG")})
    if cs.isHKG and cs.isHKGCanFd:
      rows.append({"target_id": "toggle:TacoTuneHacks", "type": "toggle",
                    "title": tr("Taco Bell Torque Hack"), "get_state": lambda: self._controller._params.get_bool("TacoTuneHacks")})
    if cs.isSubaru:
      rows.append({"target_id": "toggle:SubaruSNG", "type": "toggle",
                    "title": tr("Stop and Go"), "get_state": lambda: self._controller._params.get_bool("SubaruSNG")})
    if cs.isToyota:
      rows.append({"target_id": "toggle:LockDoors", "type": "toggle",
                    "title": tr("Auto Lock Doors"), "get_state": lambda: self._controller._params.get_bool("LockDoors")})
      rows.append({"target_id": "toggle:UnlockDoors", "type": "toggle",
                    "title": tr("Auto Unlock Doors"), "get_state": lambda: self._controller._params.get_bool("UnlockDoors")})
      rows.append({"target_id": "select:LockDoorsTimer", "type": "select",
                    "title": tr("Lock Doors Timer"),
                    "get_value": lambda: _lock_doors_timer_labels().get(float(self._controller._params.get_int("LockDoorsTimer")), f"{self._controller._params.get_int('LockDoorsTimer')}s"),
                    "pill_width": 100})
      rows.append({"target_id": "select:ClusterOffset", "type": "select",
                    "title": tr("Dashboard Speed Offset"),
                    "get_value": lambda: f"{self._controller._params.get_float('ClusterOffset'):.3f}x",
                    "pill_width": 120})
    if cs.isToyota and not cs.hasSNG:
      rows.append({"target_id": "toggle:SNGHack", "type": "toggle",
                    "title": tr("Stop-and-Go Hack"), "get_state": lambda: self._controller._params.get_bool("SNGHack")})
    if cs.isToyota and cs.hasOpenpilotLongitudinal:
      rows.append({"target_id": "toggle:FrogsGoMoosTweak", "type": "toggle",
                    "title": tr("FrogsGoMoo Tweak"), "get_state": lambda: self._controller._params.get_bool("FrogsGoMoosTweak")})

    rows.append({"target_id": "toggle:RemapCancelToDistance", "type": "toggle",
                  "title": tr("Remap Cancel Button"), "subtitle": tr("Remap the Cancel button to act as the Distance button."),
                  "get_state": lambda: self._controller._params.get_bool("RemapCancelToDistance")})
    if cs.isHKGCanFd:
      rows.append({"target_id": "toggle:AlwaysIPedal", "type": "toggle",
                    "title": tr("Always I-Pedal"),
                    "subtitle": tr("Spoof the left paddle after shifting into Drive until i-Pedal latches."),
                    "get_state": lambda: self._controller._params.get_bool("AlwaysIPedal")})
    if cs.isHKGCanFd and cs.hasOpenpilotLongitudinal:
      rows.append({"target_id": "toggle:NostalgiaMode", "type": "toggle",
                    "title": tr("Nostalgia Mode"),
                    "subtitle": tr("Use the left paddle to pause openpilot acceleration and braking."),
                    "get_state": lambda: self._controller._params.get_bool("NostalgiaMode")})
    return rows

  def _build_steering_rows(self) -> list[dict]:
    cs = starpilot_state.car_state
    rows = []
    for key in ("DistanceButtonControl", "LongDistanceButtonControl", "VeryLongDistanceButtonControl"):
      rows.append({"target_id": f"select:{key}", "type": "select", "title": tr(self._controller._action_title(key)),
                    "get_value": lambda k=key: self._controller._get_action_name(k), "pill_width": 140})
    if not cs.isSubaru and not (cs.lkasAllowedForAOL and self._controller._params.get_bool("AlwaysOnLateral") and self._controller._params.get_bool("AlwaysOnLateralLKAS")):
      rows.append({"target_id": "select:LKASButtonControl", "type": "select", "title": tr("LKAS Button"),
                    "get_value": lambda: self._controller._get_action_name("LKASButtonControl"), "pill_width": 140})
    if cs.hasModeStarButtons:
      for key in ("ModeButtonControl", "LongModeButtonControl", "VeryLongModeButtonControl",
                   "StarButtonControl", "LongStarButtonControl", "VeryLongStarButtonControl"):
        rows.append({"target_id": f"select:{key}", "type": "select", "title": tr(self._controller._action_title(key)),
                      "get_value": lambda k=key: self._controller._get_action_name(k), "pill_width": 140})
    return rows


class StarPilotVehicleSettingsLayout(StarPilotPanel):
  def __init__(self):
    super().__init__()
    self._make_options, self._models_by_make, self._models_by_value, self._make_by_model = get_fingerprint_catalog()
    self._manager_view = VehicleSettingsManagerView(self)

  def _render(self, rect: rl.Rectangle):
    self._manager_view.render(rect)

  def show_event(self):
    super().show_event()
    self._manager_view.show_event()

  def hide_event(self):
    super().hide_event()
    self._manager_view.hide_event()

  def _action_title(self, key: str) -> str:
    titles = {
      "DistanceButtonControl": "Distance Button",
      "LongDistanceButtonControl": "Distance (Long Press)",
      "VeryLongDistanceButtonControl": "Distance (Very Long)",
      "LKASButtonControl": "LKAS Button",
      "ModeButtonControl": "Mode Button",
      "LongModeButtonControl": "Mode (Long Press)",
      "VeryLongModeButtonControl": "Mode (Very Long)",
      "StarButtonControl": "Star Button",
      "LongStarButtonControl": "Star (Long Press)",
      "VeryLongStarButtonControl": "Star (Very Long)",
    }
    return titles.get(key, key)

  def _get_action_name(self, key: str) -> str:
    if key == "LKASButtonControl" and self._params.get_bool("RemapCancelToDistance"):
      if self._params.get_int("LKASButtonControl") != 0:
        self._params.put_int("LKASButtonControl", 0)
      return ACTION_NAME_BY_ID[0]
    idx = self._params.get_int(key)
    return ACTION_NAME_BY_ID.get(idx, ACTION_NAMES[0])

  def _get_available_actions(self, key: str | None = None) -> list[str]:
    if key == "LKASButtonControl" and self._params.get_bool("RemapCancelToDistance"):
      return [ACTION_NAME_BY_ID[0]]
    cs = starpilot_state.car_state
    return [o["name"] for o in ACTION_OPTIONS if cs.hasOpenpilotLongitudinal or not o.get("requires_longitudinal", False)]

  def _on_toggle(self, param_key: str):
    if param_key == "DisableOpenpilotLongitudinal":
      current = self._params.get_bool("DisableOpenpilotLongitudinal")
      if not current:
        def on_confirm(res):
          if res == DialogResult.CONFIRM:
            self._params.put_bool("DisableOpenpilotLongitudinal", True)
            if starpilot_state.started:
              HARDWARE.reboot()
        gui_app.push_widget(ConfirmDialog(tr("Disable openpilot longitudinal control?"), tr("Disable"), callback=on_confirm))
      else:
        self._params.put_bool("DisableOpenpilotLongitudinal", False)
      return
    if param_key == "RemapCancelToDistance":
      new_state = not self._params.get_bool("RemapCancelToDistance")
      self._params.put_bool("RemapCancelToDistance", new_state)
      if new_state and self._params.get_int("LKASButtonControl") != 0:
        self._params.put_int("LKASButtonControl", 0)
      return
    current = self._params.get_bool(param_key) if self._params.get(param_key, encoding="utf-8") is not None else False
    self._params.put_bool(param_key, not current)

  def _on_select(self, key: str):
    if key == "CarMake":
      self._on_select_make()
    elif key == "CarModel":
      self._on_select_model()
    elif key == "LockDoorsTimer":
      self._show_lock_timer_selector()
    elif key == "ClusterOffset":
      self._show_offset_selector()
    else:
      self._show_action_picker(key)

  def _on_select_make(self):
    makes = list(self._make_options)
    if not makes:
      gui_app.push_widget(ConfirmDialog(tr("No fingerprint list available."), tr("OK")))
      return
    current_make = self._params.get("CarMake", encoding="utf-8") or ""
    default_make = current_make if current_make in makes else makes[0]

    def on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        self._params.put("CarMake", dialog.selection)
        current_model = self._params.get("CarModel", encoding="utf-8") or ""
        available = {o.value for o in self._models_by_make.get(dialog.selection, ())}
        if current_model not in available:
          self._params.remove("CarModel")
          self._params.remove("CarModelName")

    dialog = MultiOptionDialog(tr("Select Make"), makes, default_make, callback=on_select)
    gui_app.push_widget(dialog)

  def _on_select_model(self):
    make = self._params.get("CarMake", encoding="utf-8") or ""
    if not make:
      gui_app.push_widget(ConfirmDialog(tr("Please select a Car Make first!"), tr("OK")))
      return
    model_options = self._models_by_make.get(make, ())
    if not model_options:
      gui_app.push_widget(ConfirmDialog(tr("No models available for this make."), tr("OK")))
      return
    option_labels = [o.option_label for o in model_options]
    selected_by_label = {o.option_label: o for o in model_options}
    current_model = self._params.get("CarModel", encoding="utf-8") or ""
    current_model_name = self._params.get("CarModelName", encoding="utf-8") or ""
    default_option = next((o.option_label for o in model_options if o.value == current_model and o.label == current_model_name), None)
    if default_option is None:
      default_option = next((o.option_label for o in model_options if o.value == current_model), option_labels[0])

    def on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        opt = selected_by_label[dialog.selection]
        self._params.put("CarModel", opt.value)
        self._params.put("CarModelName", opt.label)
        self._params.put("CarMake", make)

    dialog = MultiOptionDialog(tr("Select Model"), option_labels, default_option, callback=on_select)
    gui_app.push_widget(dialog)

  def _show_action_picker(self, key: str):
    if key == "LKASButtonControl" and self._params.get_bool("RemapCancelToDistance"):
      if self._params.get_int("LKASButtonControl") != 0:
        self._params.put_int("LKASButtonControl", 0)
      return
    actions = self._get_available_actions(key)
    current = self._get_action_name(key)
    if current not in actions:
      current = actions[0]

    def on_select(res):
      if res == DialogResult.CONFIRM and dialog.selection:
        self._params.put_int(key, ACTION_IDS.get(dialog.selection, 0))

    dialog = MultiOptionDialog(tr(key), actions, current, callback=on_select)
    gui_app.push_widget(dialog)

  def _show_lock_timer_selector(self):
    def on_close(res, val):
      if res == DialogResult.CONFIRM:
        self._params.put_int("LockDoorsTimer", int(val))

    gui_app.push_widget(AetherSliderDialog(tr("Lock Doors Timer"), 0, 300, 5,
                                            self._params.get_int("LockDoorsTimer"), on_close, labels=_lock_doors_timer_labels()))

  def _show_offset_selector(self):
    def on_close(res, val):
      if res == DialogResult.CONFIRM:
        self._params.put_float("ClusterOffset", float(val))

    gui_app.push_widget(AetherSliderDialog(tr("Dashboard Speed Offset"), 1.000, 1.050, 0.001,
                                            self._params.get_float("ClusterOffset"), on_close, unit="x"))

  def _get_display_make(self) -> str:
    make = self._params.get("CarMake", encoding="utf-8") or ""
    if make:
      return make
    model = self._params.get("CarModel", encoding="utf-8") or ""
    if model:
      return self._make_by_model.get(model, tr("None"))
    return tr("None")

  def _get_display_model(self) -> str:
    selected = self._get_selected_model_option()
    if selected is not None:
      return selected.button_label
    model = self._params.get("CarModel", encoding="utf-8") or ""
    model_name = self._params.get("CarModelName", encoding="utf-8") or ""
    make = self._params.get("CarMake", encoding="utf-8") or self._make_by_model.get(model, "")
    if model_name:
      return shorten_model_label(make, model_name) if make else model_name
    if model and model in self._models_by_value:
      return self._models_by_value[model].button_label
    return tr("None")

  def _get_selected_model_option(self) -> FingerprintModelOption | None:
    model = self._params.get("CarModel", encoding="utf-8") or ""
    if not model:
      return None
    model_name = self._params.get("CarModelName", encoding="utf-8") or ""
    make = self._params.get("CarMake", encoding="utf-8") or self._make_by_model.get(model, "")
    if make and model_name:
      for option in self._models_by_make.get(make, ()):
        if option.value == model and option.label == model_name:
          return option
    return self._models_by_value.get(model)
