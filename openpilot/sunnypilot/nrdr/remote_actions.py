"""Compatibility exports for the canonical NRDR remote-actions service."""

from openpilot.nrdr.features.services.remote_actions import (
  RLOG_GLOBS,
  SUMMARY_MAX_CHARS,
  TUNE_REPORT_PATH,
  TUNE_SCAN_TIMEOUT_S,
  UPDATER_PHASE_TIMEOUT_S,
  UPDATER_WAKE_TIMEOUT_S,
  RemoteActions,
  _wait_for,
  extract_tune_summary,
)


__all__ = (
  "RLOG_GLOBS",
  "SUMMARY_MAX_CHARS",
  "TUNE_REPORT_PATH",
  "TUNE_SCAN_TIMEOUT_S",
  "UPDATER_PHASE_TIMEOUT_S",
  "UPDATER_WAKE_TIMEOUT_S",
  "RemoteActions",
  "_wait_for",
  "extract_tune_summary",
)
