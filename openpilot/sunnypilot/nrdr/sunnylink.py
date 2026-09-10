"""Compatibility exports for the canonical NRDR Sunnylink service helpers."""

from openpilot.nrdr.features.services.sunnylink import (
  HONDA_TUNING_WRITE_KEYS,
  ONROAD_WRITE_BLOCKLIST,
  UNREGISTERED,
  _identity_path,
  allow_param_write,
  inject_car_tune_details,
  persist_dongle_id,
  restore_dongle_id,
)


__all__ = (
  "HONDA_TUNING_WRITE_KEYS",
  "ONROAD_WRITE_BLOCKLIST",
  "UNREGISTERED",
  "_identity_path",
  "allow_param_write",
  "inject_car_tune_details",
  "persist_dongle_id",
  "restore_dongle_id",
)
