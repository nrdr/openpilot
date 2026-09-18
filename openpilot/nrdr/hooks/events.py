from openpilot.cereal import log
from opendbc.car import structs


EventName = log.OnroadEvent.EventName
GearShifter = structs.CarState.GearShifter

_LATERAL_ONLY_CAR_EVENTS = frozenset({
  EventName.doorOpen,
  EventName.seatbeltNotLatched,
  EventName.wrongGear,
  EventName.brakeHold,
  EventName.belowEngageSpeed,
})
_SUPPRESSED_CAR_EVENTS = frozenset({
  EventName.belowSteerSpeed,
})
_HONDA_ADDITIONAL_GEARS = frozenset({GearShifter.low})


def filter_car_events(events):
  return [event for event in events if getattr(event.name, "raw", event.name) not in _SUPPRESSED_CAR_EVENTS]


def keep_lateral_active(event_name: int) -> bool:
  return getattr(event_name, "raw", event_name) in _LATERAL_ONLY_CAR_EVENTS


def is_drivable_gear(gear: int, platform_gears: tuple[int, ...], brand: str = "") -> bool:
  gear_value = getattr(gear, "raw", gear)
  platform_allowed = any(gear_value == getattr(platform_gear, "raw", platform_gear) for platform_gear in platform_gears)
  return gear_value == GearShifter.drive or platform_allowed or (brand == "honda" and gear_value in _HONDA_ADDITIONAL_GEARS)


def allow_longitudinal(CS: structs.CarState, platform_gears: tuple[int, ...], brand: str) -> bool:
  safe_state = not (CS.doorOpen or CS.seatbeltUnlatched or CS.parkingBrake)
  return safe_state and is_drivable_gear(CS.gearShifter, platform_gears, brand)
