"""Planner-speed handoff for the Civic's non-interceptor PCM controller."""
import math

from opendbc.car.honda.civic_pcm import REFERENCE_MAX_AGE_NS, uses_civic_pcm


def pcm_plan_ready(CP, CP_SP, requested_accel: float, mono_time: int, now_nanos: int, valid: bool) -> bool:
  """Do not republish stale plan acceleration as a live Civic control request.

  Brake tracking trusts CarControl's longitudinal authority independently of
  the optional speed-reference transport. That requires the host to revoke
  authority when its actual acceleration plan is missing, invalid or stale.
  Other platforms retain their existing activity policy.
  """
  if not uses_civic_pcm(CP, CP_SP):
    return True
  return bool(valid and mono_time > 0 and 0 <= now_nanos - mono_time <= REFERENCE_MAX_AGE_NS and
              math.isfinite(requested_accel))


def pcm_reference(CP, CP_SP, speeds, mono_time: int, valid: bool) -> tuple[bool, float, int]:
  if not uses_civic_pcm(CP, CP_SP):
    return False, 0.0, 0
  # Mode selection is independent of freshness. Missing data must remove
  # propulsion, not silently switch command laws while longitudinal is active.
  if not valid or not speeds or mono_time <= 0:
    return True, 0.0, 0
  speed = float(speeds[0])
  if not math.isfinite(speed) or not 0.0 <= speed <= 100.0:
    return True, 0.0, 0
  return True, speed, int(mono_time)
