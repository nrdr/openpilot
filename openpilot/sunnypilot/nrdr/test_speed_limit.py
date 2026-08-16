from types import SimpleNamespace

from openpilot.sunnypilot.nrdr.speed_limit import (
  SpeedLimitConfirmation,
  apply_map_limit,
  compare_cluster_target,
  quantize_set_speed,
)


class Button:
  gapAdjustCruise = 3


def test_distance_button_is_the_only_confirmation():
  confirmation = SpeedLimitConfirmation(Button)
  confirmation.update(1 << Button.gapAdjustCruise)
  assert confirmation.consume()
  confirmation.update(1 << 1)
  assert not confirmation.consume()


def test_honda_imperial_target_uses_cluster_ladder():
  CP = SimpleNamespace(brand="honda")
  target = quantize_set_speed(100.0, False, CP)
  assert compare_cluster_target(target / 3.6, 100.0 / 3.6, False, CP) == (False, False)


def test_upcoming_lower_map_limit_is_selected():
  resolver = SimpleNamespace(limit_solutions={}, distance_solutions={})
  map_data = SimpleNamespace(speedLimitAheadDistance=750.0)
  assert apply_map_limit(resolver, map_data, 30.0, 20.0, "map")
  assert resolver.limit_solutions["map"] == 20.0
  assert resolver.distance_solutions["map"] == 750.0
