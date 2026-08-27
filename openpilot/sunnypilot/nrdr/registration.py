"""Compatibility exports for the canonical NRDR registration service."""

from openpilot.nrdr.features.services.registration import (
  PATH_ENV,
  UNREGISTERED_DONGLE_ID,
  Paths,
  _read,
  _valid,
  _validate,
  commit,
  identity_path,
  is_enabled,
  persist,
  resolve,
)


__all__ = (
  "PATH_ENV",
  "UNREGISTERED_DONGLE_ID",
  "Paths",
  "_read",
  "_valid",
  "_validate",
  "commit",
  "identity_path",
  "is_enabled",
  "persist",
  "resolve",
)
