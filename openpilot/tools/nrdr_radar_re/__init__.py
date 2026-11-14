"""Compatibility exports for the canonical NRDR radar reverse-engineering tools."""

from openpilot.nrdr.tools.radar_re import (
    BOSCH_RADAR_ALL_IDS,
    BOSCH_RADAR_HDR_MSGS,
    BOSCH_RADAR_HDR_TAG,
    BOSCH_RADAR_LAT_SCALE_DEG_PER_LSB,
    __version__,
)


__all__ = (
    "BOSCH_RADAR_ALL_IDS",
    "BOSCH_RADAR_HDR_MSGS",
    "BOSCH_RADAR_HDR_TAG",
    "BOSCH_RADAR_LAT_SCALE_DEG_PER_LSB",
    "__version__",
)
