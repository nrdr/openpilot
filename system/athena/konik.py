#!/usr/bin/env python3
"""Compatibility entry point for the UI's "Register with Konik" action."""

from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID, is_registered_device, register

__all__ = ["UNREGISTERED_DONGLE_ID", "is_registered_device", "register"]


if __name__ == "__main__":
  print(register())
