"""Bosch-A longitudinal gates for NRDR.

Replaces the SOURCE bosch_a_toggles.py. The BoschAStockBrakeFeel / BoschAHumanFollowing owner toggles are gone: both
features are permanently on, so the only question is whether the car qualifies. There are no Params reads here.

Detection uses the same Honda platform set as nrdr.features.radar.radar.is_honda_bosch_a_radar (HONDA_BOSCH_A); the
radarUnavailable test is applied exactly where SOURCE applied it (active_for and the per-module radar-on checks), so a
Bosch-A car with the radar off still gets the radar-independent tuning (smooth, onset ramp, human following).

The MVL-off condition for the planner chain is NOT decided here; the planner wiring adds it.
"""
from opendbc.car.honda.values import HONDA_BOSCH_A


def _bosch_a_platform(CP) -> bool:
  if CP is None:
    return False
  try:
    return bool(CP.brand == "honda" and CP.carFingerprint in HONDA_BOSCH_A)
  except Exception:
    return False


def vehicle_supported(CP) -> bool:
  """Bosch-A Honda platform with openpilot longitudinal active. Radar on or off (SOURCE vehicle_supported semantics,
  minus the alphaLongitudinalAvailable settings-row allowance, which has no meaning without toggles)."""
  return _bosch_a_platform(CP) and bool(getattr(CP, "openpilotLongitudinalControl", False))


def long_tuning_active(CP) -> bool:
  """The one gate for every radar-dependent Bosch-A longitudinal part (PTM bosch_a_toggles.long_tuning_active): verified
  Bosch-A Honda (HONDA_BOSCH_A, 14 cars), openpilot longitudinal, radar on."""
  return vehicle_supported(CP) and not bool(getattr(CP, "radarUnavailable", True))


# Kept so existing nrdr callers (and the nrdr gate tests) keep working; identical to long_tuning_active.
active_for = long_tuning_active


def human_following_enabled(CP) -> bool:
  """SOURCE human_following.enabled_for with the toggle always on: Bosch-A Honda with openpilot longitudinal, radar
  on or off (vision-only shares it)."""
  return vehicle_supported(CP)
