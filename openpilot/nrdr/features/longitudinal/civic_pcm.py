"""Planner-speed handoff for the Civic's non-interceptor PCM controller."""
import math

from opendbc.car.honda.civic_pcm import uses_civic_pcm
from opendbc.car.honda.values import HondaFlags


def pcm_coast_eligible(plan, radar, cruise_kph: float, valid: bool, force_decel: bool) -> tuple[bool, float]:
  """Never infer permission to defer a brake from a missing lead/plan message."""
  cruise = cruise_kph / 3.6
  # 255 kph is the unset sentinel; no normal cruise selection exceeds 169 kph.
  eligible = bool(valid and not force_decel and math.isfinite(cruise) and 18.0 < cruise_kph <= 169.0
                  and str(plan.longitudinalPlanSource) == "cruise" and not (plan.hasLead or plan.shouldStop or plan.fcw)
                  and not (radar.leadOne.present or radar.leadTwo.present))
  return eligible, cruise if eligible else 0.0


def pcm_reference(CP, CP_SP, speeds, mono_time: int, valid: bool) -> tuple[bool, float, int]:
  if not uses_civic_pcm(CP, CP_SP) or not CP.flags & HondaFlags.NIDEC_PCM_EXPERIMENTAL:
    return False, 0.0, 0
  # Mode selection is independent of freshness. Missing data must remove
  # propulsion, not silently switch command laws while longitudinal is active.
  if not valid or not speeds or mono_time <= 0:
    return True, 0.0, 0
  speed = float(speeds[0])
  if not math.isfinite(speed) or not 0.0 <= speed <= 100.0:
    return True, 0.0, 0
  return True, speed, int(mono_time)
