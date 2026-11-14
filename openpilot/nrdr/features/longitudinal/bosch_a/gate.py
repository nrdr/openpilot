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


def active_for(CP) -> bool:
  """honda_bosch_a_long gate: Bosch-A Honda, radar on, openpilot longitudinal (same as is_honda_bosch_a_radar and
  openpilotLongitudinalControl)."""
  return vehicle_supported(CP) and not bool(getattr(CP, "radarUnavailable", True))


def human_following_enabled(CP) -> bool:
  """SOURCE human_following.enabled_for with the toggle always on: Bosch-A Honda with openpilot longitudinal, radar
  on or off (vision-only shares it)."""
  return vehicle_supported(CP)
