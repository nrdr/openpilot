#!/usr/bin/env python3
"""Compatibility exports and entrypoint for the canonical NRDR remote service."""

from openpilot.nrdr.features.services.remoted import (
  POLL_INTERVAL_S,
  SSH_KEY_REFRESH_INTERVAL_S,
  SSH_KEY_REFRESH_RETRY_S,
  _park,
  _validate_params,
  run,
)
from openpilot.system.manager.nrdr_remoted import main


__all__ = (
  "POLL_INTERVAL_S",
  "SSH_KEY_REFRESH_INTERVAL_S",
  "SSH_KEY_REFRESH_RETRY_S",
  "_park",
  "_validate_params",
  "main",
  "run",
)


if __name__ == "__main__":
  main()
