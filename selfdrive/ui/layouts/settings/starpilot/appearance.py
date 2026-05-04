from __future__ import annotations
import re
from pathlib import Path

from openpilot.system.hardware import HARDWARE
from openpilot.system.hardware.hw import Paths
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog

from openpilot.selfdrive.ui.lib.starpilot_state import starpilot_state
from openpilot.selfdrive.ui.layouts.settings.starpilot.panel import _SettingsPage
from openpilot.selfdrive.ui.layouts.settings.starpilot.aethergrid import (
    AetherSliderDialog,
    DEFAULT_PANEL_STYLE,
)
from openpilot.selfdrive.ui.layouts.settings.starpilot.longitudinal import (
    SettingRow,
    SettingSection,
    AetherSettingsView,
)

PANEL_STYLE = DEFAULT_PANEL_STYLE

# ── Theme paths & config (preserved from themes.py) ──

if HARDWARE.get_device_type() == "pc":
    THEME_SAVE_PATH = Path(Paths.comma_home()) / "starpilot" / "data" / "themes"
else:
    THEME_SAVE_PATH = Path("/data/themes")

HOLIDAY_THEME_NAMES = {
    "new_years": "New Year's",
    "valentines_day": "Valentine's Day",
    "st_patricks_day": "St. Patrick's Day",
    "world_frog_day": "World Frog Day",
    "april_fools": "April Fools",
    "easter_week": "Easter",
    "may_the_fourth": "May the Fourth",
    "cinco_de_mayo": "Cinco de Mayo",
    "stitch_day": "Stitch Day",
    "fourth_of_july": "Fourth of July",
    "halloween_week": "Halloween",
    "thanksgiving_week": "Thanksgiving",
    "christmas_week": "Christmas",
}

THEME_KEY_CONFIG = {
    "BootLogo": {
        "default": "starpilot",
        "kind": "files",
        "path": THEME_SAVE_PATH / "bootlogos",
        "extra": [],
    },
    "ColorScheme": {
        "default": "stock",
        "kind": "themes",
        "path": THEME_SAVE_PATH / "theme_packs",
        "subfolder": "colors",
        "extra": [("stock", "Stock"), *HOLIDAY_THEME_NAMES.items()],
    },
    "DistanceIconPack": {
        "default": "stock",
        "kind": "themes",
        "path": THEME_SAVE_PATH / "theme_packs",
        "subfolder": "distance_icons",
        "extra": [("stock", "Stock"), *HOLIDAY_THEME_NAMES.items()],
    },
    "IconPack": {
        "default": "stock",
        "kind": "themes",
        "path": THEME_SAVE_PATH / "theme_packs",
        "subfolder": "icons",
        "extra": [("stock", "Stock"), *HOLIDAY_THEME_NAMES.items()],
    },
    "SignalAnimation": {
        "default": "stock",
        "kind": "themes",
        "path": THEME_SAVE_PATH / "theme_packs",
        "subfolder": "signals",
        "extra": [("none", "None"), *HOLIDAY_THEME_NAMES.items()],
    },
    "SoundPack": {
        "default": "stock",
        "kind": "themes",
        "path": THEME_SAVE_PATH / "theme_packs",
        "subfolder": "sounds",
        "extra": [("stock", "Stock"), *HOLIDAY_THEME_NAMES.items()],
    },
    "WheelIcon": {
        "default": "stock",
        "kind": "files",
        "path": THEME_SAVE_PATH / "steering_wheels",
        "extra": [("none", "None"), ("stock", "Stock"), *HOLIDAY_THEME_NAMES.items()],
    },
}

COLOR_PRESETS = ["Stock", "#FFFFFF", "#178644", "#3B82F6", "#E63956", "#8B5CF6", "#F59E0B"]
CAMERA_VIEWS = ["Auto", "Driver", "Standard", "Wide"]


def _theme_display_name(value: str) -> str:
    if not value:
        return "Stock"
    lowered = value.lower()
    if lowered in HOLIDAY_THEME_NAMES:
        return HOLIDAY_THEME_NAMES[lowered]
    if lowered == "stock":
        return "Stock"
    if lowered == "none":
        return "None"
    base, creator = (value.split("~", 1) + [""])[:2] if "~" in value else (value, "")
    user_created_suffixes = ("-user_created", "_user_created", "-user-created", "_user-created")
    user_created = False
    for suffix in user_created_suffixes:
        if base.endswith(suffix):
            base = base[:-len(suffix)]
            user_created = True
            break
    parts = [part for part in re.split(r"[-_]+", base) if part]
    display = " ".join(part[:1].upper() + part[1:] for part in parts) if parts else value
    if user_created:
        display += " (User Created)"
    if creator:
        display += f" - by: {creator}"
    return display


# ═══════════════════════════════════════════════════════════════
# Theme Personalize sub-panel
# ═══════════════════════════════════════════════════════════════

class StarPilotAppearancePersonalizeLayout(_SettingsPage):
    def __init__(self):
        super().__init__()
        self._build_view()

    def _build_view(self):
        sections: list[SettingSection] = [
            SettingSection(tr_noop("Theme Components"), [
                SettingRow("BootLogo", "value", tr_noop("Boot Logo"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("BootLogo"),
                           on_click=lambda: self._show_theme_selector("BootLogo")),
                SettingRow("ColorScheme", "value", tr_noop("Color Scheme"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("ColorScheme"),
                           on_click=lambda: self._show_theme_selector("ColorScheme")),
                SettingRow("DistanceIconPack", "value", tr_noop("Distance Icons"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("DistanceIconPack"),
                           on_click=lambda: self._show_theme_selector("DistanceIconPack")),
                SettingRow("IconPack", "value", tr_noop("Icon Pack"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("IconPack"),
                           on_click=lambda: self._show_theme_selector("IconPack")),
                SettingRow("SignalAnimation", "value", tr_noop("Turn Signals"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("SignalAnimation"),
                           on_click=lambda: self._show_theme_selector("SignalAnimation")),
                SettingRow("SoundPack", "value", tr_noop("Sound Pack"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("SoundPack"),
                           on_click=lambda: self._show_theme_selector("SoundPack")),
                SettingRow("WheelIcon", "value", tr_noop("Steering Wheel"),
                           subtitle="",
                           get_value=lambda: self._get_theme_value("WheelIcon"),
                           on_click=lambda: self._show_theme_selector("WheelIcon")),
            ]),
        ]
        self._manager_view = AetherSettingsView(
            self, sections,
            header_title=tr_noop("Personalize"),
            header_subtitle=tr_noop("Customize the overall look and feel of openpilot."),
            panel_style=PANEL_STYLE,
        )

    def _get_downloaded_slugs(self, key: str) -> list[str]:
        config = THEME_KEY_CONFIG[key]
        path = config["path"]
        if not path.exists():
            return []
        slugs = set()
        if config["kind"] == "files":
            for entry in path.iterdir():
                if entry.is_file():
                    slugs.add(entry.stem)
        else:
            subfolder = config["subfolder"]
            for entry in path.iterdir():
                if entry.is_dir() and (entry / subfolder).exists():
                    slugs.add(entry.name)
        return sorted(slugs, key=str.casefold)

    def _build_theme_options(self, key: str) -> tuple[list[str], dict[str, str], str]:
        config = THEME_KEY_CONFIG[key]
        current_slug = self._params.get(key, encoding='utf-8') or config["default"]
        options_map = {}
        for slug in self._get_downloaded_slugs(key):
            display = _theme_display_name(slug)
            if display not in options_map:
                options_map[display] = slug
        for slug, display in config["extra"]:
            options_map[display] = slug
        current_display = _theme_display_name(current_slug)
        if current_display not in options_map:
            options_map[current_display] = current_slug
        options = sorted(options_map.keys(), key=str.casefold)
        return options, options_map, current_display

    def _get_theme_value(self, key: str) -> str:
        default = THEME_KEY_CONFIG[key]["default"]
        return _theme_display_name(self._params.get(key, encoding='utf-8') or default)

    def _show_theme_selector(self, key):
        themes, option_map, current = self._build_theme_options(key)
        if not themes:
            return

        def on_select(res):
            if res == DialogResult.CONFIRM and dialog.selection:
                selected_slug = option_map.get(dialog.selection)
                if selected_slug is None:
                    return
                self._params.put(key, selected_slug)

        dialog = MultiOptionDialog(tr(key), themes, current, callback=on_select)
        gui_app.push_widget(dialog)


# ═══════════════════════════════════════════════════════════════
# Unified Appearance panel
# ═══════════════════════════════════════════════════════════════

class StarPilotAppearanceLayout(_SettingsPage):
    def __init__(self):
        super().__init__()
        self._sub_panels = {
            "personalize": StarPilotAppearancePersonalizeLayout(),
        }
        self._wire_sub_panels()
        self._build_view()

    def _build_view(self):
        tab_defs = [
            {"id": "display", "title": tr_noop("Display"), "subtitle": tr_noop("Screen visibility")},
            {"id": "widgets", "title": tr_noop("Widgets"), "subtitle": tr_noop("Driving indicators")},
            {"id": "convenience", "title": tr_noop("Convenience"), "subtitle": tr_noop("QOL & navigation")},
            {"id": "model", "title": tr_noop("Model"), "subtitle": tr_noop("Path visualization")},
            {"id": "theme", "title": tr_noop("Theme"), "subtitle": tr_noop("Customization")},
        ]

        po = lambda: self._params.get_bool("PedalsOnUI")
        ol = lambda: starpilot_state.car_state.hasOpenpilotLongitudinal
        bsm = lambda: starpilot_state.car_state.hasBSM

        sections: list[SettingSection] = [
            # ═══ Tab 1: Display — screen visibility toggles ═══
            SettingSection(tr_noop("Screen Elements"), [
                SettingRow("AdvancedCustomUI", "toggle", tr_noop("Advanced UI Controls"),
                           subtitle=tr_noop("Fine-tune which elements appear on screen."),
                           get_state=lambda: self._params.get_bool("AdvancedCustomUI"),
                           set_state=lambda s: self._params.put_bool("AdvancedCustomUI", s)),
                SettingRow("HideSpeed", "toggle", tr_noop("Hide Speed"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HideSpeed"),
                           set_state=lambda s: self._params.put_bool("HideSpeed", s)),
                SettingRow("HideMaxSpeed", "toggle", tr_noop("Hide Max Speed"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HideMaxSpeed"),
                           set_state=lambda s: self._params.put_bool("HideMaxSpeed", s)),
                SettingRow("HideAlerts", "toggle", tr_noop("Hide Alerts"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HideAlerts"),
                           set_state=lambda s: self._params.put_bool("HideAlerts", s)),
            ], tab_key="display", column_pair="display"),

            SettingSection(tr_noop("Speed Info"), [
                SettingRow("HideSpeedLimit", "toggle", tr_noop("Hide Speed Limit"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HideSpeedLimit"),
                           set_state=lambda s: self._params.put_bool("HideSpeedLimit", s)),
                SettingRow("HideLeadMarker", "toggle", tr_noop("Hide Lead Marker"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HideLeadMarker"),
                           set_state=lambda s: self._params.put_bool("HideLeadMarker", s),
                           visible=ol),
                SettingRow("WheelSpeed", "toggle", tr_noop("Wheel Speed"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("WheelSpeed"),
                           set_state=lambda s: self._params.put_bool("WheelSpeed", s)),
            ], tab_key="display", column_pair="display"),

            # ═══ Tab 2: Widgets — driving screen widget toggles ═══
            SettingSection(tr_noop("Path Overlays"), [
                SettingRow("CustomUI", "toggle", tr_noop("Driving Screen Widgets"),
                           subtitle=tr_noop("Show interactive indicators on the driving screen."),
                           get_state=lambda: self._params.get_bool("CustomUI"),
                           set_state=lambda s: self._params.put_bool("CustomUI", s)),
                SettingRow("AccelerationPath", "toggle", tr_noop("Acceleration Path"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("AccelerationPath"),
                           set_state=lambda s: self._params.put_bool("AccelerationPath", s),
                           visible=ol),
                SettingRow("AdjacentPath", "toggle", tr_noop("Adjacent Lanes"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("AdjacentPath"),
                           set_state=lambda s: self._params.put_bool("AdjacentPath", s)),
                SettingRow("AdjacentPathMetrics", "toggle", tr_noop("Adjacent Lane Metrics"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("AdjacentPathMetrics"),
                           set_state=lambda s: self._params.put_bool("AdjacentPathMetrics", s)),
                SettingRow("BlindSpotPath", "toggle", tr_noop("Blind Spot Path"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("BlindSpotPath"),
                           set_state=lambda s: self._params.put_bool("BlindSpotPath", s),
                           visible=bsm),
            ], tab_key="widgets", column_pair="widgets"),

            SettingSection(tr_noop("Dashboard Controls"), [
                SettingRow("Compass", "toggle", tr_noop("Compass"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("Compass"),
                           set_state=lambda s: self._params.put_bool("Compass", s)),
                SettingRow("OnroadDistanceButton", "toggle", tr_noop("Personality Button"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("OnroadDistanceButton"),
                           set_state=lambda s: self._params.put_bool("OnroadDistanceButton", s)),
                SettingRow("PedalsOnUI", "toggle", tr_noop("Pedal Indicators"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("PedalsOnUI"),
                           set_state=lambda s: self._params.put_bool("PedalsOnUI", s),
                           visible=ol),
                SettingRow("DynamicPedalsOnUI", "toggle", tr_noop("Dynamic Pedals"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("DynamicPedalsOnUI"),
                           set_state=lambda s: self._set_exclusive_pedal("DynamicPedalsOnUI", "StaticPedalsOnUI", s),
                           visible=lambda: po() and ol()),
                SettingRow("StaticPedalsOnUI", "toggle", tr_noop("Static Pedals"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("StaticPedalsOnUI"),
                           set_state=lambda s: self._set_exclusive_pedal("StaticPedalsOnUI", "DynamicPedalsOnUI", s),
                           visible=lambda: po() and ol()),
                SettingRow("RotatingWheel", "toggle", tr_noop("Rotating Wheel"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("RotatingWheel"),
                           set_state=lambda s: self._params.put_bool("RotatingWheel", s)),
            ], tab_key="widgets", column_pair="widgets"),

            # ═══ Tab 3: Convenience — QOL + Navigation ═══
            SettingSection(tr_noop("Quality of Life"), [
                SettingRow("QOLVisuals", "toggle", tr_noop("Quality of Life"),
                           subtitle=tr_noop("Convenience features for everyday driving."),
                           get_state=lambda: self._params.get_bool("QOLVisuals"),
                           set_state=lambda s: self._params.put_bool("QOLVisuals", s)),
                SettingRow("CameraView", "value", tr_noop("Camera View"),
                           subtitle="",
                           get_value=lambda: tr(CAMERA_VIEWS[self._params.get_int("CameraView")]),
                           on_click=self._show_camera_view_selector),
                SettingRow("DriverCamera", "toggle", tr_noop("Driver Camera"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("DriverCamera"),
                           set_state=lambda s: self._params.put_bool("DriverCamera", s)),
                SettingRow("StoppedTimer", "toggle", tr_noop("Stopped Timer"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("StoppedTimer"),
                           set_state=lambda s: self._params.put_bool("StoppedTimer", s)),
            ], tab_key="convenience", column_pair="convenience"),

            SettingSection(tr_noop("Navigation"), [
                SettingRow("NavigationUI", "toggle", tr_noop("Navigation Widgets"),
                           subtitle=tr_noop("Show navigation info on the driving screen."),
                           get_state=lambda: self._params.get_bool("NavigationUI"),
                           set_state=lambda s: self._params.put_bool("NavigationUI", s)),
                SettingRow("RoadNameUI", "toggle", tr_noop("Road Name"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("RoadNameUI"),
                           set_state=lambda s: self._params.put_bool("RoadNameUI", s)),
                SettingRow("ShowSpeedLimits", "toggle", tr_noop("Speed Limits"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("ShowSpeedLimits"),
                           set_state=lambda s: self._params.put_bool("ShowSpeedLimits", s)),
                SettingRow("UseVienna", "toggle", tr_noop("Vienna Signs"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("UseVienna"),
                           set_state=lambda s: self._params.put_bool("UseVienna", s)),
            ], tab_key="convenience", column_pair="convenience"),

            # ═══ Tab 4: Model — path/lane visualization ═══
            SettingSection(tr_noop("Path & Lanes"), [
                SettingRow("ModelUI", "toggle", tr_noop("Model UI"),
                           subtitle=tr_noop("Display the driving model path, lanes, and road edges."),
                           get_state=lambda: self._params.get_bool("ModelUI"),
                           set_state=lambda s: self._params.put_bool("ModelUI", s)),
                SettingRow("DynamicPathWidth", "toggle", tr_noop("Dynamic Path"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("DynamicPathWidth"),
                           set_state=lambda s: self._params.put_bool("DynamicPathWidth", s)),
                SettingRow("LaneLinesWidth", "value", tr_noop("Lane Line Width"),
                           subtitle="",
                           get_value=lambda: self._get_lane_lines_display(),
                           on_click=lambda: self._show_int_selector("LaneLinesWidth", 0, 24, self._get_lane_lines_unit())),
                SettingRow("LaneLinesColor", "value", tr_noop("Lane Line Color"),
                           subtitle="",
                           get_value=lambda: self._get_color_display("LaneLinesColor"),
                           on_click=lambda: self._show_color_selector("LaneLinesColor")),
                SettingRow("PathWidth", "value", tr_noop("Path Width"),
                           subtitle="",
                           get_value=lambda: self._get_path_width_display(),
                           on_click=self._show_path_width_selector),
            ], tab_key="model", column_pair="model"),

            SettingSection(tr_noop("Edges & Colors"), [
                SettingRow("PathEdgeWidth", "value", tr_noop("Path Edge Width"),
                           subtitle="",
                           get_value=lambda: f"{self._params.get_int('PathEdgeWidth')}%",
                           on_click=lambda: self._show_int_selector("PathEdgeWidth", 0, 100, "%")),
                SettingRow("PathEdgesColor", "value", tr_noop("Path Edge Color"),
                           subtitle="",
                           get_value=lambda: self._get_color_display("PathEdgesColor"),
                           on_click=lambda: self._show_color_selector("PathEdgesColor")),
                SettingRow("PathColor", "value", tr_noop("Path Color"),
                           subtitle="",
                           get_value=lambda: self._get_color_display("PathColor"),
                           on_click=lambda: self._show_color_selector("PathColor")),
                SettingRow("RoadEdgesWidth", "value", tr_noop("Road Edge Width"),
                           subtitle="",
                           get_value=lambda: self._get_road_edges_display(),
                           on_click=lambda: self._show_int_selector("RoadEdgesWidth", 0, 24, self._get_road_edges_unit())),
                SettingRow("BorderWidth", "value", tr_noop("Border Width"),
                           subtitle="",
                           get_value=lambda: f"{int(round(self._params.get_float('BorderWidth')))}%",
                           on_click=lambda: self._show_float_selector("BorderWidth", 25, 250, 5, "%")),
            ], tab_key="model", column_pair="model"),

            # ═══ Tab 5: Theme — customization ═══
            SettingSection(tr_noop("Customization"), [
                SettingRow("CustomThemes", "toggle", tr_noop("Custom Themes"),
                           subtitle=tr_noop("Enable custom theme assets on the driving screen."),
                           get_state=lambda: self._params.get_bool("CustomThemes"),
                           set_state=lambda s: self._params.put_bool("CustomThemes", s)),
                SettingRow("Personalize", "value", tr_noop("Personalize openpilot"),
                           subtitle=tr_noop("Choose boot logo, color scheme, icons, sounds, and more."),
                           get_value=lambda: tr_noop("Customize"),
                           navigate_to="personalize"),
                SettingRow("HolidayThemes", "toggle", tr_noop("Holiday Themes"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("HolidayThemes"),
                           set_state=lambda s: self._params.put_bool("HolidayThemes", s)),
                SettingRow("RainbowPath", "toggle", tr_noop("Rainbow Path"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("RainbowPath"),
                           set_state=lambda s: self._params.put_bool("RainbowPath", s)),
            ], tab_key="theme", column_pair="theme"),

            SettingSection(tr_noop("Options"), [
                SettingRow("RandomEvents", "toggle", tr_noop("Random Events"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("RandomEvents"),
                           set_state=lambda s: self._params.put_bool("RandomEvents", s)),
                SettingRow("RandomThemes", "toggle", tr_noop("Random Themes"),
                           subtitle="",
                           get_state=lambda: self._params.get_bool("RandomThemes"),
                           set_state=lambda s: self._params.put_bool("RandomThemes", s)),
                SettingRow("StartupAlert", "value", tr_noop("Startup Alert"),
                           subtitle="",
                           get_value=self._get_startup_alert_display,
                           on_click=self._show_startup_alert_selector),
            ], tab_key="theme", column_pair="theme"),
        ]

        self._manager_view = AetherSettingsView(
            self, sections,
            header_title=tr_noop("Appearance"),
            header_subtitle=tr_noop("Customize your display, driving widgets, model visualization, and themes."),
            tab_defs=tab_defs,
            panel_style=PANEL_STYLE,
        )

    # ── Widget helpers ──

    def _set_exclusive_pedal(self, key, other_key, state):
        self._params.put_bool(key, state)
        if state:
            self._params.put_bool(other_key, False)

    # ── Camera view ──

    def _show_camera_view_selector(self):
        current = self._params.get_int("CameraView")

        def on_select(res):
            if res == DialogResult.CONFIRM and dialog.selection:
                idx = CAMERA_VIEWS.index(dialog.selection)
                self._params.put_int("CameraView", idx)

        dialog = MultiOptionDialog(tr("Camera View"), CAMERA_VIEWS, CAMERA_VIEWS[current], callback=on_select)
        gui_app.push_widget(dialog)

    # ── Color selectors ──

    def _get_color_display(self, key):
        val = self._params.get(key, encoding='utf-8') or ""
        if not val:
            return "Stock"
        return val.upper()

    def _show_color_selector(self, key):
        current = self._params.get(key, encoding='utf-8') or "Stock"

        def on_select(res):
            if res == DialogResult.CONFIRM and dialog.selection:
                if dialog.selection == "Stock":
                    self._params.remove(key)
                else:
                    self._params.put(key, dialog.selection)

        dialog = MultiOptionDialog(tr(key), COLOR_PRESETS, current, callback=on_select)
        gui_app.push_widget(dialog)

    # ── Numeric sliders (int / float) ──

    def _show_int_selector(self, key, min_v, max_v, unit=""):
        def on_close(res, val):
            if res == DialogResult.CONFIRM:
                self._params.put_int(key, int(val))
        gui_app.push_widget(AetherSliderDialog(tr(key), min_v, max_v, 1, self._params.get_int(key), on_close,
                                                 unit=unit, color="#8B5CF6"))

    def _show_float_selector(self, key, min_v, max_v, step, unit="", convert=None, unconvert=None):
        current = self._params.get_float(key)
        if convert:
            current = convert(current)

        def on_close(res, val):
            if res == DialogResult.CONFIRM:
                v = float(val)
                if unconvert:
                    v = unconvert(v)
                self._params.put_float(key, v)

        gui_app.push_widget(AetherSliderDialog(tr(key), min_v, max_v, step, current, on_close,
                                                 unit=unit, color="#8B5CF6"))

    # ── Unit-aware display helpers ──

    def _is_metric(self):
        return self._params.get_bool("IsMetric")

    def _get_lane_lines_unit(self):
        return "cm" if self._is_metric() else "in"

    def _get_lane_lines_display(self):
        val = self._params.get_int("LaneLinesWidth")
        if self._is_metric():
            return f"{int(val * 2.54)}cm"
        return f"{val}in"

    def _get_road_edges_unit(self):
        return "cm" if self._is_metric() else "in"

    def _get_road_edges_display(self):
        val = self._params.get_int("RoadEdgesWidth")
        if self._is_metric():
            return f"{int(val * 2.54)}cm"
        return f"{val}in"

    def _get_path_width_display(self):
        val = self._params.get_float("PathWidth")
        if self._is_metric():
            return f"{val / 3.28084:.1f}m"
        return f"{val:.1f}ft"

    def _show_path_width_selector(self):
        if self._is_metric():
            self._show_float_selector("PathWidth", 0, 10, 0.1, "m", convert=lambda v: v / 3.28084, unconvert=lambda v: v * 3.28084)
        else:
            self._show_float_selector("PathWidth", 0, 10, 0.1, "ft")

    # ── Startup alert ──

    def _get_startup_alert_display(self):
        current_top = self._params.get("StartupMessageTop", encoding='utf-8') or ""
        if current_top == "Be ready to take over at any time":
            return "Stock"
        if current_top == "Hop in and buckle up!":
            return "StarPilot"
        return "Clear"

    def _show_startup_alert_selector(self):
        options = ["Stock", "StarPilot", "Clear"]
        current = self._get_startup_alert_display()

        def on_select(res):
            if res == DialogResult.CONFIRM and dialog.selection:
                if dialog.selection == "Stock":
                    self._params.put("StartupMessageTop", "Be ready to take over at any time")
                    self._params.put("StartupMessageBottom", "Always keep hands on wheel and eyes on road")
                elif dialog.selection == "StarPilot":
                    self._params.put("StartupMessageTop", "Hop in and buckle up!")
                    self._params.put("StartupMessageBottom", "Human-tested, frog-approved")
                else:
                    self._params.remove("StartupMessageTop")
                    self._params.remove("StartupMessageBottom")

        dialog = MultiOptionDialog(tr("Startup Alert"), options, current, callback=on_select)
        gui_app.push_widget(dialog)
