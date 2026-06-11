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

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

POLL_INTERVAL_S = 2.0
UPDATER_WAKE_TIMEOUT_S = 15.0
UPDATER_PHASE_TIMEOUT_S = 900.0
TUNE_SCAN_TIMEOUT_S = 1800
TUNE_REPORT_PATH = "/data/nrdr_tune_report.txt"
RLOG_GLOBS = ("/data/media/0/realdata/*/rlog.zst", "/data/media/0/realdata/*/rlog.bz2")
SUMMARY_MAX_CHARS = 4000


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
  # Pull the PER-SPEED SUMMARY table out of the full report for remote viewing.
  try:
    with open(path) as f:
      text = f.read()
  except OSError:
    return ""
  start = text.find("PER-SPEED SUMMARY")
  if start == -1:
    return text.strip()[:SUMMARY_MAX_CHARS]
  end = text.find("PER-SPEED x DIRECTION", start)
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

  while True:
    try:
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
