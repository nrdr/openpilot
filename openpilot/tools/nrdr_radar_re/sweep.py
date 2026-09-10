"""Compatibility exports for canonical NRDR radar bit-window sweeps."""

from openpilot.nrdr.tools.radar_re.sweep import (
    DECLARED_BYTES,
    WINDOW_SIZES,
    BitWindow,
    HypothesisResult,
    _extract_window,
    _pearson_r_r2,
    enumerate_windows,
    score_windows,
)


__all__ = (
    "DECLARED_BYTES",
    "WINDOW_SIZES",
    "BitWindow",
    "HypothesisResult",
    "_extract_window",
    "_pearson_r_r2",
    "enumerate_windows",
    "score_windows",
)
