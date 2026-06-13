"""BP-styled BluePilot settings panel — port of selfdrive/ui/bp/mici/layouts/settings/bluepilot.py.

Renders the existing BluePilot toggle/button list as a paged carousel of BP
cards. Float controls (predicted-curvature blend, lane-change factor, etc.)
are deferred to a future BP slider widget — for v1 they're shown as read-only
StatCards so the user can at least see current values. Toggles and buttons
keep full functionality and the same Params keys.
"""
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.wifi_manager import WifiManager, Network
from openpilot.selfdrive.ui.ui_state import ui_state

from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import (
  BigToggleCard, BigMultiToggleCard, BigButtonCard, StatCard,
)
from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPInfoDialog
from openpilot.selfdrive.ui.bp.mici.widgets.web_server_qr_dialog_bp import BPWebServerQRDialog
from openpilot.selfdrive.ui.bp.mici.widgets.preferred_network_select import PreferredNetworkSelectMici


def _read_param_text(key: str, default: str = "—") -> str:
  v = Params().get(key)
  if v is None:
    return default
  if isinstance(v, bytes):
    v = v.decode("utf-8", errors="replace").strip("\x00")
  return str(v).strip() or default


def _read_param_float(key: str) -> str:
  try:
    return f"{float(_read_param_text(key, '0')):.2f}"
  except (ValueError, TypeError):
    return "—"


class BluePilotLayoutBP(BPSubPanel):
  TITLE = "BluePilot"

  def __init__(self, back_callback: Callable | None = None):
    self._params = Params()
    self._wifi_manager = WifiManager()
    self._wifi_manager.set_active(False)
    self._saved_networks: list[Network] = []
    self._wifi_manager.add_callbacks(networks_updated=self._on_networks_updated)
    super().__init__(back_callback=back_callback)

  # ---- lifecycle ----
  def show_event(self):
    super().show_event()
    self._wifi_manager.set_active(True)

  def hide_event(self):
    super().hide_event()
    self._wifi_manager.set_active(False)

  def _on_networks_updated(self, networks: list[Network]):
    self._saved_networks = [n for n in networks if self._wifi_manager.is_connection_saved(n.ssid)]

  # ---- callbacks ----
  def _open_qr(self):
    if not self._params.get_bool("EnableWebRoutesServer"):
      gui_app.push_widget(BPInfoDialog("Web routes off",
                                        "Enable web routes server first."))
      return
    try:
      gui_app.push_widget(BPWebServerQRDialog(back_callback=gui_app.pop_widget))
    except Exception:
      pass

  def _open_preferred_network(self):
    if not self._saved_networks:
      gui_app.push_widget(BPInfoDialog("No saved networks",
                                        "Connect to a Wi-Fi network first."))
      return
    gui_app.push_widget(PreferredNetworkSelectMici(
      self._wifi_manager, self._saved_networks, on_dismiss=lambda: None,
    ))

  def _clear_model_cache(self):
    self._params.remove("ModelRunnerTypeCache")
    self._params.remove("ModelManager_ActiveBundle")
    self._params.put_bool("DoReboot", True)

  # ---- pages ----
  def _build_pages(self):
    return [
      # ---- Web routes / preferred network ----
      BigToggleCard("Web Routes Server",
                    "Run the on-device web server for diagnostics.",
                    param_key="EnableWebRoutesServer"),
      BigButtonCard("Show QR Code", on_click=self._open_qr),
      BigButtonCard("Preferred Wi-Fi", on_click=self._open_preferred_network),

      # ---- Onroad UI ----
      BigToggleCard("Hands-free Cluster UI",
                    "Show BlueCruise UI on the instrument cluster.",
                    param_key="send_hands_free_cluster_msg"),
      BigMultiToggleCard("Lower Right Display", "What to show in the lower-right corner onroad.",
                         options=["off", "lead car speed", "speed", "lead car distance", "time to lead"],
                         param_key="mici_complication"),
      BigToggleCard("Show Brake Status", "Color the path when braking.",
                    param_key="ShowBrakeStatus"),
      BigToggleCard("Show Blindspot Overlay", "Highlight blindspot vehicles.",
                    param_key="ShowBlindspotOverlay"),
      BigToggleCard("Hybrid/EV Power Flow", "Show energy flow diagram for hybrids/EVs.",
                    param_key="FordPrefHybridPowerFlow"),
      BigMultiToggleCard("Power Flow Style", "Visual style for the power flow widget.",
                         options=["flat", "round"],
                         param_key="FordPrefHybridPowerFlowAlternate"),
      BigToggleCard("Rainbow Mode", "Cycle path colors over time.",
                    param_key="RainbowMode"),
      BigToggleCard("Animate Steering Wheel", "Rotate the steering wheel icon onroad.",
                    param_key="BPAnimateSteeringWheel"),
      BigToggleCard("Hide Onroad Fade", "Skip the fade-in transition onroad.",
                    param_key="mici_hide_onroad_fade"),
      BigToggleCard("Hide Screen Border", "Remove the dark border around the onroad view.",
                    param_key="mici_hide_onroad_border"),

      # ---- Lateral / lane positioning ----
      BigToggleCard("Human Turn Detection", "Pause control when the driver makes a turn.",
                    param_key="enable_human_turn_detection"),
      BigToggleCard("Disable ALC Under Speed", "Block auto lane change below a min speed.",
                    param_key="BlinkerPauseLaneChange"),
      BigToggleCard("Lane Positioning", "Bias the path within the lane based on conditions.",
                    param_key="enable_lane_positioning"),
      BigToggleCard("Lanefull Mode", "Stay near the lane center even with weak lines.",
                    param_key="enable_lane_full_mode"),
      BigToggleCard("Custom Tuning Profile", "Use a hand-tuned curvature blend.",
                    param_key="custom_profile"),
      StatCard("Lane Change Factor (high)", lambda: _read_param_float("lane_change_factor_high")),
      StatCard("In-Lane Offset",            lambda: _read_param_float("custom_path_offset")),
      StatCard("Blend Ratio (high curve)",  lambda: _read_param_float("pc_blend_ratio_high_C_UI")),
      StatCard("Blend Ratio (low curve)",   lambda: _read_param_float("pc_blend_ratio_low_C_UI")),
      StatCard("Low-Curve PID Gain",        lambda: _read_param_float("LC_PID_gain_UI")),
      StatCard("Min Lane Change Speed",     lambda: _read_param_text("BlinkerMinLateralControlSpeed", "—")),

      # ---- BP overrides ----
      BigToggleCard("Disable BP Lateral",   "Bypass BP lateral control.",
                    param_key="disable_BP_lat_UI"),
      BigToggleCard("Disable BP Long",      "Bypass BP longitudinal control.",
                    param_key="disable_BP_long_UI"),
      BigToggleCard("Disable Downhill Comp", "Disable downhill speed compensation.",
                    param_key="disable_downhill_comp_UI"),
      BigToggleCard("UI Debug Logging",     "Verbose BP UI logging.",
                    param_key="BPUIDebugLog"),
      StatCard("12V Battery Limit",         lambda: _read_param_float("vbatt_pause_charging")),

      # ---- Maintenance ----
      BigButtonCard("Clear Crashed Model", on_click=self._clear_model_cache, danger=True),
    ]
