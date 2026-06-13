"""
nrdr Lateral Tuning sub-panel.
"""
import datetime
import glob
import os
import subprocess
from collections.abc import Callable
import pyray as rl

from cereal import car
from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.list_view import (BUTTON_BORDER_RADIUS, BUTTON_FONT_SIZE, BUTTON_FONT_WEIGHT, BUTTON_HEIGHT,
                                                   BUTTON_WIDTH, RIGHT_ITEM_PADDING, ItemAction, ListItem, button_item)
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.html_render import HtmlModalSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP

TUNE_REPORT_PATH = "/data/nrdr_tune_report.txt"
TUNE_REPORT_TMP = TUNE_REPORT_PATH + ".tmp"
RLOG_GLOBS = ("/data/media/0/realdata/*/rlog.zst", "/data/media/0/realdata/*/rlog.bz2")


class _TuneReportAction(ItemAction):
  """Two compact buttons (SCAN / VIEW) on the right side of a single list item."""

  def __init__(self, scan_text: Callable[[], str], scan_enabled: Callable[[], bool],
               scan_callback: Callable[[], None], view_callback: Callable[[], None]):
    super().__init__(width=2 * BUTTON_WIDTH + RIGHT_ITEM_PADDING, enabled=True)
    self._scan_text = scan_text
    self._scan_enabled = scan_enabled
    self._scan_button = Button("", font_size=BUTTON_FONT_SIZE, font_weight=BUTTON_FONT_WEIGHT,
                               button_style=ButtonStyle.LIST_ACTION, border_radius=BUTTON_BORDER_RADIUS,
                               click_callback=scan_callback, text_padding=0)
    self._view_button = Button(tr("VIEW"), font_size=BUTTON_FONT_SIZE, font_weight=BUTTON_FONT_WEIGHT,
                               button_style=ButtonStyle.LIST_ACTION, border_radius=BUTTON_BORDER_RADIUS,
                               click_callback=view_callback, text_padding=0)

  def set_touch_valid_callback(self, touch_callback: Callable[[], bool]) -> None:
    super().set_touch_valid_callback(touch_callback)
    self._scan_button.set_touch_valid_callback(touch_callback)
    self._view_button.set_touch_valid_callback(touch_callback)

  def _render(self, rect: rl.Rectangle) -> bool:
    self._scan_button.set_text(self._scan_text())
    self._scan_button.set_enabled(self._scan_enabled())

    button_y = rect.y + (rect.height - BUTTON_HEIGHT) / 2
    view_rect = rl.Rectangle(rect.x + rect.width - BUTTON_WIDTH, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    scan_rect = rl.Rectangle(view_rect.x - RIGHT_ITEM_PADDING - BUTTON_WIDTH, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    self._scan_button.render(scan_rect)
    self._view_button.render(view_rect)
    return False


class LateralTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._scan_proc: subprocess.Popen | None = None
    self._scan_fh = None

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  # --- Tune Report ---

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

    # Keep the output either way: on failure it contains the traceback, which is useful.
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

  # --- PID Tune Information ---

  @staticmethod
  def _fmt_vals(vals) -> str:
    return ", ".join(f"{float(v):g}" for v in vals)

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
      # pycapnp >= 2.x: from_bytes returns a context manager, not the message itself
      with car.CarParams.from_bytes(cp_bytes) as CP:
        return self._format_pid_tune_lines(CP)
    except Exception as e:
      return tr("Could not read the stored car parameters.") + f"<br><br>{e}"

  def _format_pid_tune_lines(self, CP) -> str:
    lines = [f"<b>{CP.carFingerprint}</b>", ""]

    # Lateral tuning (interface.py values, as actually loaded for this car)
    try:
      which = CP.lateralTuning.which()
      if which == "pid":
        pid = CP.lateralTuning.pid
        lines.append("<b>" + tr("LATERAL PID") + "</b>")
        lines.append(f"kp: [{self._fmt_vals(pid.kpV)}] @ [{self._fmt_bp_mph(pid.kpBP)}] mph")
        lines.append(f"ki: [{self._fmt_vals(pid.kiV)}] @ [{self._fmt_bp_mph(pid.kiBP)}] mph")
        lines.append(f"kf: {float(pid.kf):g}")
      else:
        lines.append(tr("Lateral tuning type: {} (not PID)").format(which))
    except Exception:
      lines.append(tr("Lateral tuning: unavailable"))
    lines.append("")

    # Longitudinal tuning
    try:
      lt = CP.longitudinalTuning
      lines.append("<b>" + tr("LONGITUDINAL PID") + "</b>")
      lines.append(f"kp: [{self._fmt_vals(lt.kpV)}] @ [{self._fmt_bp_mph(lt.kpBP)}] mph")
      lines.append(f"ki: [{self._fmt_vals(lt.kiV)}] @ [{self._fmt_bp_mph(lt.kiBP)}] mph")
      try:
        lines.append(f"kf: {float(lt.kf):g}")
      except Exception:
        pass
    except Exception:
      lines.append(tr("Longitudinal tuning: unavailable"))
    lines.append("")

    # Related interface.py geometry/actuator values that shape the same tune
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

  def _initialize_items(self):
    self._tune_report_item = ListItem(
      title=lambda: tr("Tune Report"),
      description=lambda: tr("Analyze the drive logs on this device and report, per speed band and turn direction, how well the lateral tune is tracking. Scanning a full day of logs can take a few minutes."),
      action_item=_TuneReportAction(
        scan_text=lambda: tr("SCANNING") if self._scanning() else tr("SCAN"),
        scan_enabled=lambda: not self._scanning(),
        scan_callback=self._on_tune_report_scan,
        view_callback=self._show_tune_report,
      ),
    )

    self._pid_tune_info_item = button_item(
      lambda: tr("PID Tune Information"),
      lambda: tr("VIEW"),
      lambda: tr("The kp/ki/kf values currently loaded for your car's fingerprint (what interface.py configured), plus the related geometry values."),
      callback=self._show_pid_tune_info,
    )

    self._lat_scale_low = option_item_sp(
      param="LatPidScaleLowSpeed",
      title=lambda: tr("Low Speed PID Scale (Below 25mph) (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output below 25 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_scale_standard = option_item_sp(
      param="LatPidScaleStandard",
      title=lambda: tr("Standard Speed PID Scale (25-50mph) (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output between 25 and 50 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_scale_highway = option_item_sp(
      param="LatPidScaleHighway",
      title=lambda: tr("Highway PID Scale (50mph+) (Default: 200%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output above 50 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._scale_exclude_kf = toggle_item_sp(
      param="StaticFeedforwardLateral",
      title=lambda: tr("Keep Feedforward Static (Default: ON)"),
      description=lambda: tr("When ON, the lateral PID scales above multiply only the feedback (P+I) terms; the feedforward (kf) keeps its tuned value instead of being scaled along with them. Turn this on if you raise a PID scale but don't want the feedforward boosted with it. The longitudinal PID scale has its own toggle in Longitudinal Tuning."),
    )

    self._center_scale = option_item_sp(
      param="HondaCenterScale",
      title=lambda: tr("Center Boost (Default: 50%)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Extra error correction added while driving straight, as a percentage boost on top of the normal output. One static value across all speed ranges. Sometimes the perfect lateral tune is too soft for driving in a straight line."),
      label_callback=lambda value: f"{value}%",
      use_float_scaling=True,
    )

    self._center_boost_threshold = option_item_sp(
      param="HondaCenterBoostThreshold",
      title=lambda: tr("Center Boost Threshold (°) (Default: 3°)"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("How centered should the steering wheel be when center boost is actually active?"),
      label_callback=lambda value: f"{value / 100:.1f}°",
      use_float_scaling=True,
    )

    self._unwind_freeze = toggle_item_sp(
      param="HondaUnwindFreeze",
      title=lambda: tr("Unwind Integrator Freeze (Default: OFF)"),
      description=lambda: tr("Freezes the PID integrator while the steering is returning toward center, so it doesn't hold torque through the unwind."),
    )

    self._unwind_lookahead = toggle_item_sp(
      param="HondaUnwindLookahead",
      title=lambda: tr("Unwind Lookahead (Default: ON)"),
      description=lambda: tr("Reads the model's planned path to start unwinding earlier, before the instantaneous desired curvature drops."),
    )

    self._low_pass_filter = toggle_item_sp(
      param="HondaTorqueLowPassFilter",
      title=lambda: tr("Low Pass Filter (tau) (Default: ON)"),
      description=lambda: tr("Filter that smooths steering response at the cost of adding lag. Tune to the least amount possible before oscillations begin. Live tests show that going above 0.1 tau rapidly increases the possibility of lag-induced oscillations."),
    )

    self._lpf_tau_low = option_item_sp(
      param="HondaLpfTauLowSpeed",
      title=lambda: tr("Low Pass Filter Tau (Below 25mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) below 25 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_standard = option_item_sp(
      param="HondaLpfTauStandard",
      title=lambda: tr("Standard Tau (25-50mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) between 25 and 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_highway = option_item_sp(
      param="HondaLpfTauHighway",
      title=lambda: tr("Highway Tau (50mph+) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) above 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._notch_enabled = toggle_item_sp(
      param="HondaNotchEnabled",
      title=lambda: tr("Notch Filter (Default: ON)"),
      description=lambda: tr("Removes a narrow EPS chatter band (around 7Hz) without the lag a low pass filter adds."),
    )

    self._notch_freq = option_item_sp(
      param="HondaNotchFreq",
      title=lambda: tr("Notch Frequency (Default: 7.5)"),
      min_value=100,
      max_value=2000,
      value_change_step=10,
      description=lambda: tr("Frequency (Hz) of the band eliminated from the controller. If you know what Hz your EPS growls at, this can help block that out without adding any extra lag into the controller. Best used in pair with a well-tuned low pass filter."),
      label_callback=lambda value: f"{value / 100:.1f} Hz",
      use_float_scaling=True,
    )

    self._notch_q = option_item_sp(
      param="HondaNotchQ",
      title=lambda: tr("Notch Q / Width (Default: 1.5)"),
      min_value=10,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Tolerance of the removed frequency. Higher = smaller portion removed, lower = wider (nearby frequencies will be removed as well)."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._steer_delta_limiter = toggle_item_sp(
      param="HondaSteerDeltaLimiter",
      title=lambda: tr("Legacy Steer Delta Rate Limiter (Default: OFF)"),
      description=lambda: tr("Limits how quickly requested steering torque can rise or fall. This is an older system of limiting and may no longer prove useful compared to the low pass and notch filters."),
    )

    self._steer_delta_up = option_item_sp(
      param="HondaSteerDeltaUp",
      title=lambda: tr("Steer Delta Up (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum upward steering torque rate when the rate limiter is enabled. Too low will add lag."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._steer_delta_down = option_item_sp(
      param="HondaSteerDeltaDown",
      title=lambda: tr("Steer Delta Down (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum downward steering torque rate when the rate limiter is enabled. Too low will add lag."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._min_steer_speed = option_item_sp(
      param="NrdrMinSteerSpeed",
      title=lambda: tr("Minimum Steer Speed (Default: 0mph)"),
      min_value=0,
      max_value=45,
      value_change_step=1,
      description=lambda: tr("Below this speed no steering torque is commanded at all. 0 = steer at any speed (stock). For those who don't want the wheel moving at a standstill or parking-lot speeds."),
      label_callback=lambda value: f"{value} mph",
    )

    return [
      self._tune_report_item,
      self._pid_tune_info_item,
      LineSeparatorSP(40),
      self._low_pass_filter,
      self._lat_scale_low,
      self._lpf_tau_low,
      self._lat_scale_standard,
      self._lpf_tau_standard,
      self._lat_scale_highway,
      self._lpf_tau_highway,
      self._scale_exclude_kf,
      LineSeparatorSP(40),
      self._center_scale,
      self._center_boost_threshold,
      LineSeparatorSP(40),
      self._unwind_freeze,
      self._unwind_lookahead,
      LineSeparatorSP(40),
      self._notch_enabled,
      self._notch_freq,
      self._notch_q,
      LineSeparatorSP(40),
      self._steer_delta_limiter,
      self._steer_delta_up,
      self._steer_delta_down,
      LineSeparatorSP(40),
      self._min_steer_speed,
    ]

  def _update_state(self):
    super()._update_state()

    self._poll_tune_report_scan()

    lpf_enabled = self._low_pass_filter.action_item.get_state()
    self._lpf_tau_low.set_visible(lpf_enabled)
    self._lpf_tau_standard.set_visible(lpf_enabled)
    self._lpf_tau_highway.set_visible(lpf_enabled)

    notch_enabled = self._notch_enabled.action_item.get_state()
    self._notch_freq.set_visible(notch_enabled)
    self._notch_q.set_visible(notch_enabled)

    steer_delta_limiter_enabled = self._steer_delta_limiter.action_item.get_state()
    self._steer_delta_up.set_visible(steer_delta_limiter_enabled)
    self._steer_delta_down.set_visible(steer_delta_limiter_enabled)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
