"""Compatibility imports for the renamed Firmware Controller."""
from openpilot.nrdr.features.lateral.latcontrol_fw import (
  ANGLE_RATE_LIMIT, GAIN_BP, KI, KP, VFN_SOURCE_COMMIT, LatControlFirmware,
)

LatControlVfnEps = LatControlFirmware

__all__ = ("ANGLE_RATE_LIMIT", "GAIN_BP", "KI", "KP", "VFN_SOURCE_COMMIT", "LatControlVfnEps")
