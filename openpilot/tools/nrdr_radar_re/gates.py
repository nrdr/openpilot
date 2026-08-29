"""Compatibility exports for canonical NRDR radar hypothesis gates."""

from openpilot.nrdr.tools.radar_re.gates import (
    COMPETING_MARGIN,
    HOLDOUT_FRAC,
    MIN_ABS_R_TO_REPLICATE,
    MIN_R2_TO_REPLICATE,
    MIN_SEGMENTS,
    SIGN_CONSISTENCY,
    GateResult,
    _same_window_results,
    apply,
    apply_batch,
    apply_with_holdout,
)


__all__ = (
    "COMPETING_MARGIN",
    "HOLDOUT_FRAC",
    "MIN_ABS_R_TO_REPLICATE",
    "MIN_R2_TO_REPLICATE",
    "MIN_SEGMENTS",
    "SIGN_CONSISTENCY",
    "GateResult",
    "_same_window_results",
    "apply",
    "apply_batch",
    "apply_with_holdout",
)
