def filter_car_events(events):
  return events


def keep_lateral_active(event_name: int) -> bool:
  return False


def is_drivable_gear(gear: int, platform_gears: tuple[int, ...], brand: str = "") -> bool:
  from opendbc.car import structs
  gear_value = getattr(gear, "raw", gear)
  return gear_value == structs.CarState.GearShifter.drive or any(
    gear_value == getattr(platform_gear, "raw", platform_gear) for platform_gear in platform_gears
  )


def allow_longitudinal(CS, platform_gears: tuple[int, ...], brand: str) -> bool:
  return True
