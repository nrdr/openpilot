"""
nrdr Learned Parameters sub-panel: openpilot's live-learned vehicle params (read-only)
plus the Auto toggles that decide whether to use them or fall back to static base values.
"""
from collections.abc import Callable
import datetime
import glob
import os
import subprocess

import pyray as rl

from cereal import log
from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.html_render import HtmlModalSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, ListItemSP, LineSeparatorSP

SR_CURVE_FIT_PATH = "/data/nrdr_sr_curve_fit.txt"
SR_CURVE_FIT_TMP = SR_CURVE_FIT_PATH + ".tmp"
RLOG_GLOBS = ("/data/media/0/realdata/*/rlog.zst", "/data/media/0/realdata/*/rlog.bz2")


class LearnedParametersLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._fit_proc = None
    self._fit_fh = None

    # Read-only display of openpilot's learned live parameters + applied SR + curve guide.
    self._lp_text = {
      "steerRatio": tr("learning..."),
      "stiffnessFactor": tr("learning..."),
      "angleOffsetAverageDeg": tr("learning..."),
      "angleOffsetDeg": tr("learning..."),
      "appliedSr": tr("—"),
      "curveGuide": tr("—"),
    }

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _fitting(self) -> bool:
    return self._fit_proc is not None

  def _initialize_items(self):
    self._lp_steer_ratio = ListItemSP(
      title=lambda: f"{tr('Learned Steer Ratio')}: {self._lp_text['steerRatio']}",
    )
    self._applied_sr = ListItemSP(
      title=lambda: f"{tr('Applied Steer Ratio')}: {self._lp_text['appliedSr']}",
    )
    self._learn_steer_ratio = toggle_item_sp(
      param="NrdrLearnSteerRatio",
      title=lambda: tr("Learn Steer Ratio (Auto)"),
      description=lambda: tr("When ON, uses paramsd's live-learned scalar steer ratio (wins over the curve). When OFF: Curve Auto can apply device→seed blend→nearest; Clarity Min/Max and CR-V seed still available. OFF by default — on VGR racks the scalar averages the rack."),
      initial_state=False,
    )
    self._curve_auto = toggle_item_sp(
      param="NrdrSteerRatioCurve",
      title=lambda: tr("Steer Ratio Curve (Auto)"),
      description=lambda: tr("Learn and apply an angle-dependent steer-ratio curve together. Samples hands-off turns (yaw vs wheel angle), promotes confident bins, blends device with fingerprint seed until trusted. Recommend Learn Steer Ratio OFF. ON by default."),
      initial_state=True,
    )
    self._curve_rate = option_item_sp(
      param="NrdrSteerRatioCurveRate",
      title=lambda: tr("Curve Learning Speed (Default: 50%)"),
      min_value=0,
      max_value=100,
      value_change_step=5,
      description=lambda: tr("How fast promoted bins may chase new evidence (max step per update). 0 freezes the applied curve while bins keep accumulating. Large sample pools stay sticky — thin new drives cannot yank bins overnight."),
      label_callback=lambda value: f"{value}%",
    )
    self._curve_calibrate = toggle_item_sp(
      param="NrdrSteerRatioCalibrate",
      title=lambda: tr("SR Calibrate (guided)"),
      description=lambda: tr("Lot/cul-de-sac wizard: holds coach the next incomplete |SWA| bin (L then R), ≥7 mph, wheel still. Relaxes lat/hands-off gates. Completes at lock coverage, times out at 45 min, or clears on ignition. Partial bins still promote."),
      initial_state=False,
    )
    self._curve_guide = ListItemSP(
      title=lambda: f"{tr('Curve / Calibrate')}: {self._lp_text['curveGuide']}",
    )
    self._curve_reset = toggle_item_sp(
      param="NrdrSteerRatioCurveReset",
      title=lambda: tr("Reset Steer Ratio Curve"),
      description=lambda: tr("Clears the device-learned curve and bin stats on the next control cycle. Fingerprint seeds remain."),
      initial_state=False,
    )
    self._curve_fit = button_item(
      title=lambda: tr("Fit Steer Ratio Curve from Logs"),
      button_text=lambda: tr("…") if self._fitting() else tr("SCAN"),
      description=lambda: tr("Offroad: scan drive logs and merge into the device curve (same gates as Curve Auto). Prefer when parked — a full day of logs can take a few minutes. Does not wipe history unless you Reset first."),
      callback=self._on_curve_fit,
    )
    self._curve_fit_view = button_item(
      title=lambda: tr("Last SR Curve Fit Result"),
      button_text=lambda: tr("VIEW"),
      description=lambda: tr("Shows the table from the last SCAN (also saved under /data/nrdr_sr_curve_fit.txt)."),
      callback=self._show_curve_fit,
    )
    self._lp_stiffness = ListItemSP(
      title=lambda: f"{tr('Learned Tire Stiffness Factor')}: {self._lp_text['stiffnessFactor']}",
    )
    self._learn_stiffness = toggle_item_sp(
      param="NrdrLearnStiffness",
      title=lambda: tr("Learn Tire Stiffness (Auto)"),
      description=lambda: tr("When ON (Auto), uses the live-learned tire stiffness factor. When OFF, uses the static base value of 1.0."),
      initial_state=True,
    )
    self._lp_angle_avg = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Average)')}: {self._lp_text['angleOffsetAverageDeg']}",
    )
    self._lp_angle_inst = ListItemSP(
      title=lambda: f"{tr('Learned Angle Offset (Instant)')}: {self._lp_text['angleOffsetDeg']}",
    )
    self._learn_angle_offset = toggle_item_sp(
      param="NrdrLearnAngleOffset",
      title=lambda: tr("Learn Angle Offset (Auto)"),
      description=lambda: tr("When ON (Auto), uses the live-learned steering angle offset. When OFF, uses a static 0.0 offset. Turn OFF if a bad learned offset is pulling the car to one side."),
      initial_state=True,
    )

    return [
      self._lp_steer_ratio,
      self._applied_sr,
      self._learn_steer_ratio,
      LineSeparatorSP(40),
      self._curve_auto,
      self._curve_rate,
      self._curve_calibrate,
      self._curve_guide,
      self._curve_reset,
      self._curve_fit,
      self._curve_fit_view,
      LineSeparatorSP(40),
      self._lp_stiffness,
      self._learn_stiffness,
      self._lp_angle_avg,
      self._lp_angle_inst,
      self._learn_angle_offset,
    ]

  def _on_curve_fit(self):
    if self._fitting():
      return
    paths = []
    for pattern in RLOG_GLOBS:
      paths.extend(sorted(glob.glob(pattern)))
    if not paths:
      gui_app.push_widget(HtmlModalSP(text=tr("No drive logs found in /data/media/0/realdata.")))
      return
    try:
      self._fit_fh = open(SR_CURVE_FIT_TMP, "w")
      self._fit_proc = subprocess.Popen(
        ["python3", os.path.join(BASEDIR, "sr_curve_fit.py"), "fit", *paths, "--apply"],
        stdout=self._fit_fh,
        stderr=subprocess.STDOUT,
        cwd=BASEDIR,
      )
    except Exception as e:
      if self._fit_fh is not None:
        self._fit_fh.close()
        self._fit_fh = None
      self._fit_proc = None
      gui_app.push_widget(HtmlModalSP(text=tr("Could not start the SR curve fit.") + f"<br><br>{e}"))

  def _poll_curve_fit(self):
    if self._fit_proc is None or self._fit_proc.poll() is None:
      return
    if self._fit_fh is not None:
      self._fit_fh.close()
      self._fit_fh = None
    self._fit_proc = None
    try:
      os.replace(SR_CURVE_FIT_TMP, SR_CURVE_FIT_PATH)
    except OSError:
      pass
    try:
      with open(SR_CURVE_FIT_PATH) as f:
        text = f.read().strip()
      ui_state.params.put("NrdrSrCurveFitSummary", text[:4000])
    except Exception:
      pass
    self._show_curve_fit()

  def _show_curve_fit(self):
    if not os.path.exists(SR_CURVE_FIT_PATH):
      gui_app.push_widget(HtmlModalSP(
        text=tr("No SR curve fit yet. Press SCAN (offroad) to analyze drive logs and merge into the device curve.")))
      return
    text = f"<b>{datetime.datetime.fromtimestamp(os.path.getmtime(SR_CURVE_FIT_PATH)).strftime('%d-%b-%Y %H:%M:%S').upper()}</b><br><br>"
    try:
      with open(SR_CURVE_FIT_PATH) as f:
        text += f.read().replace("\n", "<br>")
    except Exception:
      pass
    gui_app.push_widget(HtmlModalSP(text=text))

  def _format_curve_guide(self, snap: dict | None) -> str:
    if not snap:
      return tr("—")
    if snap.get("calibrate"):
      side = snap.get("curveTargetSide", "?")
      tgt = snap.get("curveTargetDeg", "?")
      n = snap.get("curveBinN", 0)
      nmin = snap.get("curveBinNMin", 0)
      ready = snap.get("curveBinsReady", 0)
      total = snap.get("curveBinsTotal", 0)
      st = snap.get("curveStatus", "")
      hints = []
      if not snap.get("curveSpeedOk", True):
        hints.append(tr("need ≥7 mph"))
      elif not snap.get("curveHoldOk", True):
        hints.append(tr("hold still"))
      elif not snap.get("curveInBand", True):
        hints.append(tr("aim target"))
      elif st == "accumulating":
        hints.append(tr("accumulating"))
      elif st:
        hints.append(str(st))
      hint = f" · {', '.join(hints)}" if hints else ""
      return tr("Hold ~{}° {} · n={}/{} · bins {}/{}{}").format(tgt, side, n, nmin, ready, total, hint)
    ready = snap.get("curveBinsReady", 0)
    total = snap.get("curveBinsTotal", 0)
    promo = snap.get("curvePromotedCount", 0)
    st = snap.get("curveStatus", "—")
    auto = tr("ON") if snap.get("curveAuto") else tr("OFF")
    return tr("Auto {} · promoted {} · coverage {}/{} · {}").format(auto, promo, ready, total, st)

  def _refresh_live_params(self):
    vals = None
    try:
      if ui_state.started:
        lp = ui_state.sm['liveParameters']
        vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
      else:
        raw = ui_state.params.get("LiveParametersV2")
        if raw is not None:
          with log.Event.from_bytes(raw) as msg:
            lp = msg.liveParameters
            vals = (lp.steerRatio, lp.stiffnessFactor, lp.angleOffsetAverageDeg, lp.angleOffsetDeg)
    except Exception:
      vals = None

    applied = tr("—")
    snap = None
    try:
      snap = ui_state.params.get("NrdrAppliedTuneSnapshot")
      if isinstance(snap, bytes):
        import json
        snap = json.loads(snap.decode("utf-8"))
      if isinstance(snap, dict) and "appliedSteerRatio" in snap:
        mode = snap.get("srMode", "?")
        applied = f"{float(snap['appliedSteerRatio']):.2f} ({mode})"
      elif not isinstance(snap, dict):
        snap = None
    except Exception:
      snap = None

    guide = self._format_curve_guide(snap if isinstance(snap, dict) else None)

    if vals is None:
      self._lp_text = {
        "steerRatio": tr("learning..."),
        "stiffnessFactor": tr("learning..."),
        "angleOffsetAverageDeg": tr("learning..."),
        "angleOffsetDeg": tr("learning..."),
        "appliedSr": applied,
        "curveGuide": guide,
      }
    else:
      sr, sf, aoa, ao = vals
      self._lp_text = {
        "steerRatio": f"{sr:.2f}",
        "stiffnessFactor": f"{sf:.2f}",
        "angleOffsetAverageDeg": f"{aoa:.2f}°",
        "angleOffsetDeg": f"{ao:.2f}°",
        "appliedSr": applied,
        "curveGuide": guide,
      }

  def _update_state(self):
    super()._update_state()
    self._poll_curve_fit()
    self._refresh_live_params()

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
