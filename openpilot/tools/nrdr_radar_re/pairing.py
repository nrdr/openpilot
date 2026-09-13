"""Compatibility exports for canonical NRDR radar sweep pairing."""

from openpilot.nrdr.tools.radar_re.pairing import (
    SweepRecord,
    TruthProvider,
    _decode_range_frame,
    assemble_sweeps,
    attach_truth,
    build_csv_truth_channels,
    build_matched_table,
    derive_vrel,
)


__all__ = (
    "SweepRecord",
    "TruthProvider",
    "_decode_range_frame",
    "assemble_sweeps",
    "attach_truth",
    "build_csv_truth_channels",
    "build_matched_table",
    "derive_vrel",
)
