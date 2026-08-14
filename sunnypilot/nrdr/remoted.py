#!/usr/bin/env python3
"""
nrdr_remoted: consumes remote action trigger params written from the Sunnylink
website. The website has no real buttons, so a toggle is flipped remotely, this
daemon performs the action, and clears the toggle (the website seeing it flip
back off is the acknowledgment).

Triggers:
  NrdrRemoteForceUpdate -> drive the real updater chain (check/download/install),
                           same flow as the FORCE UPDATE button in
                           selfdrive/ui/layouts/home.py (SIGUSR1 = check,
                           SIGHUP = fetch/download, DoReboot = install).
  NrdrRemoteTuneScan    -> run tune_report.py over the drive logs; the full report
                           goes to /data/nrdr_tune_report.txt (grab it via
                           copyparty), and the PER-SPEED SUMMARY table goes into
                           NrdrTuneReportSummary for remote viewing.

Status text for the website is mirrored into NrdrRemoteStatus (info widget).
Offroad-only (see process_config): force update is offroad-only anyway, and a
tune scan while driving would steal CPU from the controls stack.
"""
import glob
import os
import subprocess
import time

from cereal import car, custom, messaging
from opendbc.car.car_helpers import interfaces
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  is_handcrafted_lateral_enabled,
)
from openpilot.sunnypilot.nrdr.ssh_key_refresh import refresh_github_ssh_keys
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import get_steer_ratio_endpoint_profile

POLL_INTERVAL_S = 2.0
UPDATER_WAKE_TIMEOUT_S = 15.0
UPDATER_PHASE_TIMEOUT_S = 900.0
TUNE_SCAN_TIMEOUT_S = 1800
TUNE_REPORT_PATH = "/data/nrdr_tune_report.txt"
RLOG_GLOBS = ("/data/media/0/realdata/*/rlog.zst", "/data/media/0/realdata/*/rlog.bz2")
SUMMARY_MAX_CHARS = 4000
SSH_KEY_REFRESH_RETRY_S = 60.0
SSH_KEY_REFRESH_INTERVAL_S = 24 * 60 * 60.0


def _set_status(params, text: str) -> None:
  try:
    params.put("NrdrRemoteStatus", text)
  except Exception:
    cloudlog.exception("nrdr_remoted: failed to set NrdrRemoteStatus")


def _wait_for(predicate, timeout_s: float) -> bool:
  deadline = time.monotonic() + timeout_s
  while time.monotonic() < deadline:
    if predicate():
      return True
    time.sleep(1.0)
  return False


def run_force_update(params) -> None:
  def state() -> str:
    return (params.get("UpdaterState") or "idle").strip()

  def fetch_available() -> bool:
    return params.get_bool("UpdaterFetchAvailable")

  def update_available() -> bool:
    return params.get_bool("UpdateAvailable")

  def failed_count() -> int:
    return params.get("UpdateFailedCount") or 0

  def install() -> None:
    _set_status(params, "update: rebooting to install")
    params.put_bool("DoReboot", True)

  def run_phase(signal: str, label: str) -> bool:
    # Poke updated, wait for it to wake up, then wait for it to finish.
    baseline = failed_count()
    _set_status(params, f"update: {label}")
    os.system(f"pkill -{signal} -f system.updated.updated")
    woke = _wait_for(lambda: state() != "idle" or fetch_available() or update_available() or failed_count() > baseline,
                     UPDATER_WAKE_TIMEOUT_S)
    if not woke:
      _set_status(params, "update: updater not responding")
      return False
    if not _wait_for(lambda: state() == "idle", UPDATER_PHASE_TIMEOUT_S):
      _set_status(params, "update: timed out")
      return False
    if failed_count() > baseline:
      _set_status(params, "update: check failed")
      return False
    return True

  if update_available():
    install()
    return

  if not fetch_available():
    if not run_phase("SIGUSR1", "checking"):
      return
    if update_available():
      install()
      return
    if not fetch_available():
      _set_status(params, "update: up to date " + time.strftime("%H:%M"))
      return

  if not run_phase("SIGHUP", "downloading"):
    return
  if update_available():
    install()
  else:
    _set_status(params, "update: download failed")


def _extract_summary(path: str) -> str:
  # Pull the friendly TUNE SCORE section (score + findings + suggestions) out of
  # the full report for remote viewing; fall back to the per-speed table.
  try:
    with open(path) as f:
      text = f.read()
  except OSError:
    return ""
  start = text.find("TUNE SCORE")
  end_marker = "PER-SPEED SUMMARY"
  if start == -1:
    start = text.find(end_marker)
    end_marker = "PER-SPEED x DIRECTION"
  if start == -1:
    return text.strip()[:SUMMARY_MAX_CHARS]
  end = text.find(end_marker, start + 20)
  chunk = text[start:end] if end > start else text[start:]
  return chunk.strip().strip("=").strip()[:SUMMARY_MAX_CHARS]


def run_tune_scan(params) -> None:
  paths: list[str] = []
  for pattern in RLOG_GLOBS:
    paths.extend(sorted(glob.glob(pattern)))
  if not paths:
    _set_status(params, "scan: no drive logs found")
    return

  _set_status(params, f"scan: running on {len(paths)} logs...")
  tmp = TUNE_REPORT_PATH + ".tmp"
  try:
    with open(tmp, "w") as fh:
      ret = subprocess.run(["python3", os.path.join(BASEDIR, "tune_report.py"), *paths],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=BASEDIR, timeout=TUNE_SCAN_TIMEOUT_S).returncode
  except Exception:
    cloudlog.exception("nrdr_remoted: tune scan failed to run")
    _set_status(params, "scan: failed to run")
    return

  # Keep the output either way: on failure it contains the traceback.
  try:
    os.replace(tmp, TUNE_REPORT_PATH)
  except OSError:
    pass

  try:
    params.put("NrdrTuneReportSummary", _extract_summary(TUNE_REPORT_PATH))
  except Exception:
    cloudlog.exception("nrdr_remoted: failed to set NrdrTuneReportSummary")

  suffix = "" if ret == 0 else " (with errors, see full report)"
  _set_status(params, "scan: done " + time.strftime("%H:%M") + suffix)


def _fmt_vals(vals) -> str:
  return "/".join(f"{float(value):g}" for value in vals)


def _param(params, key):
  return params.get(key, return_default=True)


def _on(params, key) -> str:
  return "ON" if bool(_param(params, key)) else "OFF"


def _write_cached(params, cache: dict, values: dict[str, str]) -> None:
  for key, value in values.items():
    if value == cache.get(key):
      continue
    params.put(key, value)
    cache[key] = value


def write_car_tune_info(params, cache: dict) -> None:
  """Publish a live, screenshot-friendly controller/tune report to Sunnylink."""
  try:
    cp_bytes = params.get("CarParamsPersistent") or params.get("CarParams")
    if not cp_bytes:
      return
    with car.CarParams.from_bytes(cp_bytes) as CP:
      changed = apply_handcrafted_lateral_profile(CP.carFingerprint, params)
      if changed:
        cloudlog.warning({"event": "handcrafted lateral profile restored offroad", "carFingerprint": str(CP.carFingerprint),
                          "changedParams": changed})
      eps = next((bytes(fw.fwVersion).decode("latin-1", "replace").strip("\x00").strip()
                  for fw in CP.carFw if fw.ecu == "eps"), "") or "n/a"
      interceptor = "n/a"
      cp_sp_bytes = params.get("CarParamsSPPersistent")
      if cp_sp_bytes:
        cp_sp = messaging.log_from_bytes(cp_sp_bytes, custom.CarParamsSP)
        interceptor = str(bool(cp_sp.enableGasInterceptor)).lower()
      eps_short = eps.rsplit(",", 1)[-1].strip() if "," in eps else eps
      controller = "PID/NNLC" if str(CP.carFingerprint) == "HONDA_CLARITY" else CP.lateralTuning.which().upper()
      gas = "gas" if interceptor == "true" else "no gas"
      radar = "radar" if not CP.radarUnavailable else "no radar"
      info = " | ".join((str(CP.carFingerprint), f"EPS {eps_short}", gas, radar, controller))

      pid_source = CP
      if CP.lateralTuning.which() != "pid":
        CarInterface = interfaces[CP.carFingerprint]
        reconstructed = CarInterface.get_non_essential_params(CP.carFingerprint)
        CarInterface.get_non_essential_params_sp(reconstructed, CP.carFingerprint)
        if reconstructed.lateralTuning.which() == "pid":
          pid_source = reconstructed

      if pid_source.lateralTuning.which() == "pid":
        pid = pid_source.lateralTuning.pid
        pid_base = f"P {_fmt_vals(pid.kpV)} | I {_fmt_vals(pid.kiV)}"
        pid_ff = (_fmt_vals([float(value) * 1e6 for value in pid.kfV]) + " x10^-6"
                  if len(pid.kfV) else f"{float(pid.kf):g}")
        pid_base_speeds = "0 / <25 / 25 / 50 mph" if str(CP.carFingerprint) == "HONDA_CLARITY" else "0 / 25 / 50 mph"
      else:
        pid_base = f"{CP.lateralTuning.which().upper()} (no PID base)"
        pid_ff = "n/a"
        pid_base_speeds = "n/a"

      lt = CP.longitudinalTuning
      long_base = f"P {_fmt_vals(lt.kpV)} | I {_fmt_vals(lt.kiV)}"
      try:
        long_base += f" | F {float(lt.kf):g}"
      except Exception:
        pass

      p_low, i_low, f_low = (_param(params, key) for key in ("LatPScaleLowSpeed", "LatIScaleLowSpeed", "LatFScaleLowSpeed"))
      p_mid, i_mid, f_mid = (_param(params, key) for key in ("LatPScaleStandard", "LatIScaleStandard", "LatFScaleStandard"))
      p_high, i_high, f_high = (_param(params, key) for key in ("LatPScaleHighway", "LatIScaleHighway", "LatFScaleHighway"))
      damping, damping_speed = _param(params, "NrdrLatRateDamping"), _param(params, "NrdrLatRateDampingFadeSpeed")
      center = float(_param(params, "HondaCenterScale")) * 100.0
      center_threshold = float(_param(params, "HondaCenterBoostThreshold"))
      center_speed = _param(params, "HondaCenterBoostMinSpeed")
      nnlc_speed = _param(params, "NrdrNnlcActivationSpeed")
      nnlc_kp = float(_param(params, "NrdrNnlcKpGain")) / 100.0
      nnlc_kf = float(_param(params, "NrdrNnlcKfGain")) / 100.0
      nnlc_ki = float(_param(params, "NrdrNnlcKiGain")) / 100.0
      sr_profile = get_steer_ratio_endpoint_profile(CP.carFingerprint)
      if sr_profile is not None:
        sr_center = float(_param(params, sr_profile.center_param))
        sr_outer = float(_param(params, sr_profile.outer_param))
        sr_lc = _on(params, "NrdrLaneChangeEndpointSteerRatio")
        sr_info = f"direct {sr_center:.2f} center -> {sr_outer:.2f} outer | lane-change endpoint {sr_lc}"
      else:
        sr_info = f"Auto {_on(params, 'NrdrLearnSteerRatio')} | base {float(CP.steerRatio):g}"
      nnlc_on = _on(params, "NrdrNnlcEnabled")
      controller_info = controller
      if controller == "PID/NNLC":
        controller_info = "PID/NNLC hybrid | PID for lane changes" if nnlc_on == "ON" else "PID only | NNLC disabled"
      profile = get_handcrafted_lateral_profile(CP.carFingerprint)
      handcrafted_on = is_handcrafted_lateral_enabled(CP.carFingerprint, params)
      handcrafted_info = f"{profile.name} (v{profile.version})" if handcrafted_on and profile is not None else "OFF"
      if handcrafted_on:
        controller_info = f"Handcrafted v{profile.version} | {controller_info}"

      rows = {
        "NrdrCarTuneInfo": info,
        "NrdrCarControllerInfo": controller_info,
        "NrdrCarHandcraftedInfo": handcrafted_info,
        "NrdrCarPidLowInfo": f"P {p_low}% | I {i_low}% | F {f_low}%",
        "NrdrCarPidMidInfo": f"P {p_mid}% | I {i_mid}% | F {f_mid}%",
        "NrdrCarPidHighInfo": f"P {p_high}% | I {i_high}% | F {f_high}%",
        "NrdrCarDampingInfo": f"{damping}% | fades by {damping_speed} mph",
        "NrdrCarCenterInfo": f"P-only {center:g}% | +/-{center_threshold:g} deg | above {center_speed} mph",
        "NrdrCarNnlcInfo": f"{nnlc_on} | {nnlc_speed} mph | KP {nnlc_kp:g} | KF {nnlc_kf:g} | KI {nnlc_ki:g}",
        "NrdrCarSteerRatioInfo": sr_info,
        "NrdrCarLearningInfo": f"stiffness {_on(params, 'NrdrLearnStiffness')} | angle {_on(params, 'NrdrLearnAngleOffset')}",
        "NrdrCarHelpersInfo": f"stiction {_on(params, 'NrdrLatStiction')} | StarPilot {_on(params, 'NrdrStarPilotPid')}",
      }

      details = "\n".join((
        "VEHICLE",
        f"Fingerprint: {CP.carFingerprint}",
        f"EPS firmware: {eps}",
        f"Gas pedal interceptor: {interceptor}",
        f"Radar messages used: {str(not CP.radarUnavailable).lower()}",
        "",
        "CONTROLLER",
        rows["NrdrCarControllerInfo"],
        f"Handcrafted profile: {rows['NrdrCarHandcraftedInfo']}",
        f"NNLC: {rows['NrdrCarNnlcInfo']}",
        "",
        f"LATERAL PID BASE ({pid_base_speeds})",
        pid_base,
        f"F {pid_ff}",
        "",
        "LIVE TUNING KNOBS",
        f"PID low: {rows['NrdrCarPidLowInfo']}",
        f"PID mid: {rows['NrdrCarPidMidInfo']}",
        f"PID highway: {rows['NrdrCarPidHighInfo']}",
        f"Damping: {rows['NrdrCarDampingInfo']}",
        f"Center: {rows['NrdrCarCenterInfo']}",
        f"Steer ratio: {rows['NrdrCarSteerRatioInfo']}",
        f"Learning: {rows['NrdrCarLearningInfo']}",
        f"Helpers: {rows['NrdrCarHelpersInfo']}",
        "",
        "LONGITUDINAL PID",
        long_base,
        "",
        "GEOMETRY",
        f"Steer ratio base: {float(CP.steerRatio):g}",
        f"Actuator delay: {float(CP.steerActuatorDelay):g} s",
        f"Wheelbase: {float(CP.wheelbase):g} m | mass: {float(CP.mass):.0f} kg",
      ))
      rows["NrdrCarTuneDetails"] = details
  except Exception:
    cloudlog.exception("nrdr_remoted: failed to build car/tune info")
    return
  try:
    _write_cached(params, cache, rows)
  except Exception:
    cloudlog.exception("nrdr_remoted: failed to publish car/tune info")


def main():
  params = Params()

  # If this build's params lib was not rebuilt with the new keys, reading them
  # raises. Park instead of crash-looping (same defensive posture as home.py).
  try:
    params.get_bool("NrdrRemoteForceUpdate")
    params.get_bool("NrdrRemoteTuneScan")
  except Exception:
    cloudlog.exception("nrdr_remoted: trigger params unavailable (params not rebuilt?); parking")
    while True:
      time.sleep(3600)

  _set_status(params, "idle")
  info_cache: dict = {}
  next_ssh_key_refresh = 0.0

  while True:
    try:
      now = time.monotonic()
      if now >= next_ssh_key_refresh:
        refreshed = refresh_github_ssh_keys(params)
        next_ssh_key_refresh = now + (SSH_KEY_REFRESH_INTERVAL_S if refreshed else SSH_KEY_REFRESH_RETRY_S)
      write_car_tune_info(params, info_cache)
      if params.get_bool("NrdrRemoteForceUpdate"):
        params.put_bool("NrdrRemoteForceUpdate", False)
        cloudlog.info("nrdr_remoted: remote force update triggered")
        run_force_update(params)
      if params.get_bool("NrdrRemoteTuneScan"):
        params.put_bool("NrdrRemoteTuneScan", False)
        cloudlog.info("nrdr_remoted: remote tune scan triggered")
        run_tune_scan(params)
    except Exception:
      cloudlog.exception("nrdr_remoted: loop error")
    time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
  main()
