import time

from openpilot.common.constants import CV
from opendbc.car.structs import car


HONDA_MPH_PER_KPH = 0.6233
HONDA_MPH_OFFSET = 0.0995
LIMIT_AHEAD_PREEMPTIVE_DISTANCE = 1000.0


def is_honda(CP: car.CarParams) -> bool:
  return str(getattr(CP, "brand", getattr(CP, "carName", ""))).lower() == "honda"


def honda_kph_to_mph(kph: float) -> int:
  return int(round(kph * HONDA_MPH_PER_KPH + HONDA_MPH_OFFSET))


def honda_mph_to_kph(mph: float) -> float:
  return (mph - HONDA_MPH_OFFSET) / HONDA_MPH_PER_KPH


def compare_cluster_target(v_cruise_cluster: float, target_set_speed: float,
                           is_metric: bool, CP: car.CarParams) -> tuple[bool, bool]:
  if not is_metric and is_honda(CP):
    current = honda_kph_to_mph(v_cruise_cluster * CV.MS_TO_KPH)
    target = honda_kph_to_mph(target_set_speed * CV.MS_TO_KPH)
  else:
    speed_conv = CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH
    current = round(v_cruise_cluster * speed_conv)
    target = round(target_set_speed * speed_conv)
  return current < target, current > target


def quantize_set_speed(kph: float, is_metric: bool, CP: car.CarParams) -> float:
  if is_metric or not is_honda(CP):
    return round(kph, 1)
  return round(honda_mph_to_kph(honda_kph_to_mph(kph)), 1)


class SpeedLimitConfirmation:
  def __init__(self, button_type, hold_seconds: float = 0.5):
    self._button = button_type.gapAdjustCruise.raw
    self._hold_seconds = hold_seconds
    self._held_until = 0.0

  def update(self, released: int) -> None:
    if released & (1 << self._button):
      self._held_until = max(self._held_until, time.monotonic() + self._hold_seconds)

  def consume(self, allowed: bool = True) -> bool:
    if not allowed:
      return False
    held_until = self._held_until
    self._held_until = 0.0
    return time.monotonic() <= held_until

def apply_map_limit(resolver, map_data, speed_limit: float, next_speed_limit: float, source) -> bool:
  distance = max(0.0, map_data.speedLimitAheadDistance)
  resolver.limit_solutions[source] = speed_limit
  resolver.distance_solutions[source] = 0.0
  if 0.0 < next_speed_limit < speed_limit and distance <= LIMIT_AHEAD_PREEMPTIVE_DISTANCE:
    resolver.limit_solutions[source] = next_speed_limit
    resolver.distance_solutions[source] = distance
  return True


def pre_active_icon(alpha: float):
  return None, None, alpha, 0, 0
