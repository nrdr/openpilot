"""Compatibility facade for the canonical NRDR steer-ratio mode API."""

from openpilot.nrdr.features.lateral import steer_ratio_tuning as _canonical


__all__ = _canonical.__all__
globals().update({name: getattr(_canonical, name) for name in __all__})
