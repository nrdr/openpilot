"""Planner-speed handoff for the Civic's non-interceptor PCM controller."""
import math

from opendbc.car.honda.civic_pcm import uses_civic_pcm


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
