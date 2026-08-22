import glob
import os
import subprocess
import time

from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog


UPDATER_WAKE_TIMEOUT_S = 15.0
UPDATER_PHASE_TIMEOUT_S = 900.0
TUNE_SCAN_TIMEOUT_S = 1800.0
TUNE_REPORT_PATH = "/data/nrdr_tune_report.txt"
RLOG_GLOBS = ("/data/media/0/realdata/*/rlog.zst", "/data/media/0/realdata/*/rlog.bz2")
SUMMARY_MAX_CHARS = 4000


def _wait_for(predicate, timeout_s: float) -> bool:
  deadline = time.monotonic() + timeout_s
  while time.monotonic() < deadline:
    if predicate():
      return True
    time.sleep(1.0)
  return False


def extract_tune_summary(path: str) -> str:
  try:
    with open(path) as report:
      text = report.read()
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
  section = text[start:end] if end > start else text[start:]
  return section.strip().strip("=").strip()[:SUMMARY_MAX_CHARS]


class RemoteActions:
  def __init__(self, params):
    self.params = params

  def set_status(self, text: str) -> None:
    try:
      self.params.put("NrdrRemoteStatus", text)
    except Exception:
      cloudlog.exception("nrdr_remoted: failed to set status")

  def _updater_state(self) -> str:
    return str(self.params.get("UpdaterState") or "idle").strip()

  def _failed_update_count(self) -> int:
    return int(self.params.get("UpdateFailedCount") or 0)

  def _run_update_phase(self, signal: str, status: str) -> bool:
    baseline = self._failed_update_count()
    self.set_status(f"update: {status}")
    subprocess.run(["pkill", f"-{signal}", "-f", "system.updated.updated"], check=False)

    woke = _wait_for(
      lambda: self._updater_state() != "idle"
      or self.params.get_bool("UpdaterFetchAvailable")
      or self.params.get_bool("UpdateAvailable")
      or self._failed_update_count() > baseline,
      UPDATER_WAKE_TIMEOUT_S,
    )
    if not woke:
      self.set_status("update: updater not responding")
      return False
    if not _wait_for(lambda: self._updater_state() == "idle", UPDATER_PHASE_TIMEOUT_S):
      self.set_status("update: timed out")
      return False
    if self._failed_update_count() > baseline:
      self.set_status("update: check failed")
      return False
    return True

  def _install_update(self) -> None:
    self.set_status("update: rebooting to install")
    self.params.put_bool("DoReboot", True)

  def force_update(self) -> None:
    if self.params.get_bool("UpdateAvailable"):
      self._install_update()
      return

    if not self.params.get_bool("UpdaterFetchAvailable"):
      if not self._run_update_phase("SIGUSR1", "checking"):
        return
      if self.params.get_bool("UpdateAvailable"):
        self._install_update()
        return
      if not self.params.get_bool("UpdaterFetchAvailable"):
        self.set_status("update: up to date " + time.strftime("%H:%M"))
        return

    if not self._run_update_phase("SIGHUP", "downloading"):
      return
    if self.params.get_bool("UpdateAvailable"):
      self._install_update()
    else:
      self.set_status("update: download failed")

  def tune_scan(self) -> None:
    paths = sorted(path for pattern in RLOG_GLOBS for path in glob.glob(pattern))
    if not paths:
      self.set_status("scan: no drive logs found")
      return

    self.set_status(f"scan: running on {len(paths)} logs...")
    temporary_path = f"{TUNE_REPORT_PATH}.tmp"
    try:
      with open(temporary_path, "w") as report:
        result = subprocess.run(
          ["python3", os.path.join(BASEDIR, "tune_report.py"), *paths],
          stdout=report,
          stderr=subprocess.STDOUT,
          cwd=BASEDIR,
          timeout=TUNE_SCAN_TIMEOUT_S,
          check=False,
        )
    except Exception:
      cloudlog.exception("nrdr_remoted: tune scan failed")
      self.set_status("scan: failed to run")
      return

    try:
      os.replace(temporary_path, TUNE_REPORT_PATH)
    except OSError:
      cloudlog.exception("nrdr_remoted: failed to publish tune report")

    try:
      self.params.put("NrdrTuneReportSummary", extract_tune_summary(TUNE_REPORT_PATH))
    except Exception:
      cloudlog.exception("nrdr_remoted: failed to publish tune summary")

    suffix = "" if result.returncode == 0 else " (with errors, see full report)"
    self.set_status("scan: done " + time.strftime("%H:%M") + suffix)
