"""Vehicle-scoped authorization for NRDR longitudinal behavior.

This is deliberately not inferred from persisted tuning values: a device can
move between cars. Non-Honda support requires an explicit, reviewed car profile
and regression tests before adding its exact (brand, fingerprint) pair below.
"""

TUNED_NON_HONDA_CARS: frozenset[tuple[str, str]] = frozenset()


def nrdr_longitudinal_enabled(CP) -> bool:
  brand = str(getattr(CP, "brand", "")).lower()
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  return brand == "honda" or (brand, fingerprint) in TUNED_NON_HONDA_CARS


def longitudinal_personality(personality, nrdr_enabled: bool) -> int:
  """Keep baseline cars in their three-personality domain, including stale Econ.

  Econ maps to Relaxed (the baseline's longest following distance). Invalid
  values use Standard. Never wrap a stale fourth setting into Aggressive.
  """
  value = getattr(personality, "raw", personality)
  if isinstance(value, bool) or not isinstance(value, int) or value not in range(4):
    return 1
  return value if nrdr_enabled else min(value, 2)
