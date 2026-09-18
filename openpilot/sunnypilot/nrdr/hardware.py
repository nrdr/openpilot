"""Compatibility exports for the canonical NRDR hardware service helpers."""

from openpilot.nrdr.features.services.hardware import apply_startup_policy, initialize_onboarding


__all__ = ("apply_startup_policy", "initialize_onboarding")
