"""Compatibility exports for canonical NRDR radar capture ingestion."""

from openpilot.nrdr.tools.radar_re.ingest import (
    FrameRecord,
    _RLOG_AVAILABLE,
    _addr_to_slot_sub,
    load,
    load_csv,
    load_rlog,
    rlog_available,
)


__all__ = (
    "FrameRecord",
    "_RLOG_AVAILABLE",
    "_addr_to_slot_sub",
    "load",
    "load_csv",
    "load_rlog",
    "rlog_available",
)
