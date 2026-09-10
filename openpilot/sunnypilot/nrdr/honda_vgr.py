"""Compatibility exports for canonical NRDR Honda variable-gear-ratio behavior."""

from openpilot.nrdr.features.lateral.honda_vgr import (
  HONDA_VGR_PROFILES,
  Q14,
  RAW_UNITS_PER_DEGREE,
  HondaVgrProfile,
  get_honda_vgr_profile,
  normalize_honda_eps_firmware,
)


__all__ = (
  "HONDA_VGR_PROFILES",
  "Q14",
  "RAW_UNITS_PER_DEGREE",
  "HondaVgrProfile",
  "get_honda_vgr_profile",
  "normalize_honda_eps_firmware",
)
