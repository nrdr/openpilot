import datetime
import glob
import os
import shutil
import subprocess
from collections.abc import Callable
from decimal import Decimal
from enum import IntEnum
import pyray as rl

from opendbc.car.car_helpers import interfaces
from opendbc.car.structs import car
from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.nrdr.handcrafted_lateral import get_handcrafted_lateral_profile
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.list_view import (BUTTON_BORDER_RADIUS, BUTTON_FONT_SIZE, BUTTON_FONT_WEIGHT, BUTTON_HEIGHT,
                                                   BUTTON_WIDTH, RIGHT_ITEM_PADDING, ItemAction, ListItem, button_item)
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.html_render import HtmlModalSP
from openpilot.system.ui.sunnypilot.widgets.list_view import LineSeparatorSP, simple_button_item_sp, toggle_item_sp
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.pidf_ground import PidfGroundLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.vehicle_model_learning import VehicleModelLearningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.override_tuning import OverrideTuningLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.steer_filters import SteerFiltersLayout

TUNE_REPORT_PATH = "/data/nrdr_tune_report.txt"
TUNE_REPORT_TMP = TUNE_REPORT_PATH + ".tmp"
MEDIA_ROOT = "/data/media/0"
RLOG_GLOBS = (f"{MEDIA_ROOT}/realdata/*/rlog.zst", f"{MEDIA_ROOT}/realdata/*/rlog.bz2")


class LateralPanel(IntEnum):
  HUB = 0
  VEHICLE_MODEL = 1
  PIDF = 2
  OVERRIDE = 3
  STEER_FILTERS = 4


class _TuneReportAction(ItemAction):
  def __init__(self, scan_text: Callable[[], str], scan_enabled: Callable[[], bool],
               scan_callback: Callable[[], None], view_callback: Callable[[], None],
               delete_callback: Callable[[], None]):
    super().__init__(width=3 * BUTTON_WIDTH + 2 * RIGHT_ITEM_PADDING, enabled=True)
    self._scan_text = scan_text
    self._scan_enabled = scan_enabled
    self._scan_button = Button("", font_size=BUTTON_FONT_SIZE, font_weight=BUTTON_FONT_WEIGHT,
                               button_style=ButtonStyle.LIST_ACTION, border_radius=BUTTON_BORDER_RADIUS,
                               click_callback=scan_callback, text_padding=0)
    self._view_button = Button(tr("VIEW"), font_size=BUTTON_FONT_SIZE, font_weight=BUTTON_FONT_WEIGHT,
                               button_style=ButtonStyle.LIST_ACTION, border_radius=BUTTON_BORDER_RADIUS,
                               click_callback=view_callback, text_padding=0)
    self._delete_button = Button(tr("DELETE"), font_size=BUTTON_FONT_SIZE, font_weight=BUTTON_FONT_WEIGHT,
                                 button_style=ButtonStyle.LIST_ACTION, border_radius=BUTTON_BORDER_RADIUS,
                                 click_callback=delete_callback, text_padding=0)

  def set_touch_valid_callback(self, touch_callback: Callable[[], bool]) -> None:
    super().set_touch_valid_callback(touch_callback)
    self._scan_button.set_touch_valid_callback(touch_callback)
    self._view_button.set_touch_valid_callback(touch_callback)
    self._delete_button.set_touch_valid_callback(touch_callback)

  def _render(self, rect: rl.Rectangle) -> bool:
    self._scan_button.set_text(self._scan_text())
    self._scan_button.set_enabled(self._scan_enabled())

    button_y = rect.y + (rect.height - BUTTON_HEIGHT) / 2
    delete_rect = rl.Rectangle(rect.x + rect.width - BUTTON_WIDTH, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    view_rect = rl.Rectangle(delete_rect.x - RIGHT_ITEM_PADDING - BUTTON_WIDTH, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    scan_rect = rl.Rectangle(view_rect.x - RIGHT_ITEM_PADDING - BUTTON_WIDTH, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    self._scan_button.render(scan_rect)
    self._view_button.render(view_rect)
    self._delete_button.render(delete_rect)
    return False


class LateralTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._scan_proc: subprocess.Popen | None = None
    self._scan_fh = None

    self._current_panel = LateralPanel.HUB
    vehicle_items = self._initialize_vehicle_items()
    self._vehicle_model_layout = VehicleModelLearningLayout(
      lambda: self._set_panel(LateralPanel.HUB),
      vehicle_items,
    )
    self._pidf_layout = PidfGroundLayout(lambda: self._set_panel(LateralPanel.HUB))
    self._override_layout = OverrideTuningLayout(lambda: self._set_panel(LateralPanel.HUB))
    self._steer_filters_layout = SteerFiltersLayout(lambda: self._set_panel(LateralPanel.HUB))

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _set_panel(self, panel: LateralPanel):
    self._current_panel = panel

  def _scanning(self) -> bool:
    return self._scan_proc is not None

  def _on_tune_report_scan(self):
    if self._scanning():
      return

    paths = []
    for pattern in RLOG_GLOBS:
      paths.extend(sorted(glob.glob(pattern)))
    if not paths:
      gui_app.push_widget(HtmlModalSP(text=tr("No drive logs found in /data/media/0/realdata.")))
      return

    try:
      self._scan_fh = open(TUNE_REPORT_TMP, "w")
      self._scan_proc = subprocess.Popen(
        ["python3", os.path.join(BASEDIR, "tune_report.py"), *paths],
        stdout=self._scan_fh,
        stderr=subprocess.STDOUT,
        cwd=BASEDIR,
      )
    except Exception as e:
      if self._scan_fh is not None:
        self._scan_fh.close()
        self._scan_fh = None
      self._scan_proc = None
      gui_app.push_widget(HtmlModalSP(text=tr("Could not start the tune report scan.") + f"<br><br>{e}"))

  def _poll_tune_report_scan(self):
    if self._scan_proc is None or self._scan_proc.poll() is None:
      return

    if self._scan_fh is not None:
      self._scan_fh.close()
      self._scan_fh = None
    self._scan_proc = None

    try:
      os.replace(TUNE_REPORT_TMP, TUNE_REPORT_PATH)
    except OSError:
      pass

    self._show_tune_report()

  def _show_tune_report(self):
    if not os.path.exists(TUNE_REPORT_PATH):
      gui_app.push_widget(HtmlModalSP(text=tr("No tune report yet. Press SCAN to analyze the drive logs on this device.")))
      return

    text = f"<b>{datetime.datetime.fromtimestamp(os.path.getmtime(TUNE_REPORT_PATH)).strftime('%d-%b-%Y %H:%M:%S').upper()}</b><br><br>"
    try:
      with open(TUNE_REPORT_PATH) as f:
        text += f.read().replace("\n", "<br>")
    except Exception:
      pass
    gui_app.push_widget(HtmlModalSP(text=text))

  def _on_tune_report_delete(self):
    dialog = ConfirmDialog(
      tr("Delete ALL dashcam media in /data/media/0? This permanently erases every recorded drive on the device and cannot be undone."),
      tr("Delete"),
      tr("Cancel"),
      callback=self._on_tune_report_delete_confirmed,
    )
    gui_app.push_widget(dialog)

  def _on_tune_report_delete_confirmed(self, result: DialogResult):
    if result != DialogResult.CONFIRM:
      return
    try:
      entries = os.listdir(MEDIA_ROOT)
    except OSError:
      entries = []
    for entry in entries:
      path = os.path.join(MEDIA_ROOT, entry)
      try:
        if os.path.isdir(path) and not os.path.islink(path):
          shutil.rmtree(path, ignore_errors=True)
        else:
          os.remove(path)
      except OSError:
        pass
    gui_app.push_widget(HtmlModalSP(text=tr("Dashcam media in /data/media/0 has been deleted.")))

  @staticmethod
  def _fmt_vals(vals) -> str:
    return ", ".join(f"{float(v):g}" for v in vals)

  @staticmethod
  def _fmt_decimal(value) -> str:
    number = Decimal(f"{float(value):g}")
    return "0" if number == 0 else format(number, "f")

  @classmethod
  def _fmt_decimal_vals(cls, vals) -> str:
    return ", ".join(cls._fmt_decimal(value) for value in vals)

  @staticmethod
  def _fmt_bp_mph(bps) -> str:
    return ", ".join(f"{float(v) * 2.23694:.0f}" for v in bps)

  def _build_pid_tune_info(self) -> str:
    try:
      cp_bytes = ui_state.params.get("CarParamsPersistent") or ui_state.params.get("CarParams")
    except Exception:
      cp_bytes = None
    if not cp_bytes:
      return tr("No car fingerprinted yet. Drive the car once so it can identify itself, then check back here.")

    try:
      with car.CarParams.from_bytes(cp_bytes) as CP:
        return self._format_pid_tune_lines(CP)
    except Exception as e:
      return tr("Could not read the stored car parameters.") + f"<br><br>{e}"

  def _format_pid_tune_lines(self, CP) -> str:
    lines = [f"<b>{CP.carFingerprint}</b>", ""]

    lines.append("<b>" + tr("CAR") + "</b>")
    try:
      eps_fw = next((bytes(fw.fwVersion).decode("latin-1", "replace").strip("\x00").strip()
                     for fw in CP.carFw if fw.ecu == "eps"), "")
      lines.append(tr("EPS firmware: {}").format(eps_fw) if eps_fw else tr("EPS firmware: (not reported)"))
    except Exception:
      lines.append(tr("EPS firmware: unavailable"))
    try:
      interceptor = str(bool(ui_state.CP_SP.enableGasInterceptor)).lower() if ui_state.CP_SP is not None else tr("unavailable")
    except Exception:
      interceptor = tr("unavailable")
    lines.append(f"gas pedal interceptor: {interceptor}")
    lines.append(f"radar messages used: {str(not CP.radarUnavailable).lower()}")
    lines.append("")

    try:
      pid_source = CP
      hybrid_base = False
      if CP.lateralTuning.which() != "pid":
        CarInterface = interfaces[CP.carFingerprint]
        reconstructed = CarInterface.get_non_essential_params(CP.carFingerprint)
        CarInterface.get_non_essential_params_sp(reconstructed, CP.carFingerprint)
        if reconstructed.lateralTuning.which() == "pid":
          pid_source = reconstructed
          hybrid_base = True

      if pid_source.lateralTuning.which() == "pid":
        pid = pid_source.lateralTuning.pid
        heading = tr("LATERAL PID (HYBRID BASE)") if hybrid_base else tr("LATERAL PID")
        lines.append("<b>" + heading + "</b>")
        lines.append(f"kp: [{self._fmt_vals(pid.kpV)}] @ [{self._fmt_bp_mph(pid.kpBP)}] mph")
        lines.append(f"ki: [{self._fmt_vals(pid.kiV)}] @ [{self._fmt_bp_mph(pid.kiBP)}] mph")
        if len(pid.kfV):
          lines.append(f"kf: [{self._fmt_decimal_vals(pid.kfV)}] @ [{self._fmt_bp_mph(pid.kfBP)}] mph")
        else:
          lines.append(f"kf: {self._fmt_decimal(pid.kf)}")
      else:
        lines.append(tr("Lateral tuning type: {} (not PID)").format(CP.lateralTuning.which()))
    except Exception:
      lines.append(tr("Lateral tuning: unavailable"))
    lines.append("")

    try:
      lt = CP.longitudinalTuning
      lt_deprecated = lt.deprecated
      lines.append("<b>" + tr("LONGITUDINAL PID") + "</b>")
      lines.append(f"kp: [{self._fmt_vals(lt_deprecated.kpV)}] @ [{self._fmt_bp_mph(lt_deprecated.kpBP)}] mph")
      lines.append(f"ki: [{self._fmt_vals(lt.kiV)}] @ [{self._fmt_bp_mph(lt.kiBP)}] mph")
      lines.append(f"kf: {self._fmt_decimal(lt_deprecated.kf)}")
    except Exception:
      lines.append(tr("Longitudinal tuning: unavailable"))
    lines.append("")

    try:
      lines.append("<b>" + tr("RELATED") + "</b>")
      lines.append(f"steerRatio: {float(CP.steerRatio):g}")
      lines.append(f"steerActuatorDelay: {float(CP.steerActuatorDelay):g} s")
      lines.append(f"wheelbase: {float(CP.wheelbase):g} m")
      lines.append(f"mass: {float(CP.mass):.0f} kg")
    except Exception:
      pass

    return "<br>".join(lines)

  def _show_pid_tune_info(self):
    gui_app.push_widget(HtmlModalSP(text=self._build_pid_tune_info()))

  def _initialize_vehicle_items(self):
    self._tune_report_item = ListItem(
      title=lambda: tr("Run Tune Report Scan"),
      description=lambda: tr(
        "Analyze the drive logs on this device and report, per speed band and turn direction, how well the lateral tune is tracking. " +
        "Scanning a full day of logs can take a few minutes. DELETE permanently wipes all dashcam media in /data/media/0."
      ),
      action_item=_TuneReportAction(
        scan_text=lambda: tr("SCANNING") if self._scanning() else tr("SCAN"),
        scan_enabled=lambda: not self._scanning(),
        scan_callback=self._on_tune_report_scan,
        view_callback=self._show_tune_report,
        delete_callback=self._on_tune_report_delete,
      ),
    )

    self._pid_tune_info_item = button_item(
      lambda: tr("Loaded Vehicle & Tune"),
      lambda: tr("VIEW"),
      lambda: tr(
        "Your car's full profile: fingerprint, EPS firmware, gas interceptor and radar status, plus the lateral/longitudinal " +
        "kp/ki/kf and geometry currently loaded for it."
      ),
      callback=self._show_pid_tune_info,
    )
    return [self._tune_report_item, self._pid_tune_info_item]

  def _initialize_items(self):
    self._handcrafted_tune = toggle_item_sp(
      title=lambda: tr("Handcrafted Lateral Tuning"),
      description=lambda: tr("Off by default. Enable this to load NRDR's Clarity-derived, road-tested controller settings. " +
                             "Steer Ratio Tuning is separate, so you can choose Manual, Comma, NRDR Raw, or Firmware geometry " +
                             "without this profile changing it. Other controller settings are locked while enabled."),
      param="NrdrHandcraftedLateralTune",
    )

    self._vehicle_model_button = simple_button_item_sp(
      button_text=lambda: tr("Vehicle Model & Learning"),
      button_width=800,
      callback=lambda: self._set_panel(LateralPanel.VEHICLE_MODEL),
    )

    self._pidf_button = simple_button_item_sp(
      button_text=lambda: tr("Controller Tuning Dungeon"),
      button_width=800,
      callback=lambda: self._set_panel(LateralPanel.PIDF),
    )
    self._override_button = simple_button_item_sp(
      button_text=lambda: tr("Override Tuning"),
      button_width=800,
      callback=lambda: self._set_panel(LateralPanel.OVERRIDE),
    )
    self._steer_filters_button = simple_button_item_sp(
      button_text=lambda: tr("Steer Filters"),
      button_width=800,
      callback=lambda: self._set_panel(LateralPanel.STEER_FILTERS),
    )
    return [
      self._handcrafted_tune,
      LineSeparatorSP(40),
      self._vehicle_model_button,
      LineSeparatorSP(40),
      self._pidf_button,
      LineSeparatorSP(40),
      self._override_button,
      LineSeparatorSP(40),
      self._steer_filters_button,
    ]

  def _update_state(self):
    super()._update_state()
    self._poll_tune_report_scan()
    fingerprint = str(ui_state.CP.carFingerprint) if ui_state.CP is not None else ""
    self._handcrafted_tune.set_visible(get_handcrafted_lateral_profile(fingerprint) is not None)
    self._handcrafted_tune.action_item.set_enabled(ui_state.is_offroad())

  def _render(self, rect):
    if self._current_panel == LateralPanel.VEHICLE_MODEL:
      self._vehicle_model_layout.render(rect)
      return
    if self._current_panel == LateralPanel.PIDF:
      self._pidf_layout.render(rect)
      return
    if self._current_panel == LateralPanel.OVERRIDE:
      self._override_layout.render(rect)
      return
    if self._current_panel == LateralPanel.STEER_FILTERS:
      self._steer_filters_layout.render(rect)
      return
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._set_panel(LateralPanel.HUB)
    self._scroller.show_event()
