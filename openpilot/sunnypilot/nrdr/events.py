from openpilot.cereal import log


EventName = log.OnroadEvent.EventName
_SUPPRESSED_CAR_EVENTS = frozenset({
  EventName.doorOpen,
  EventName.seatbeltNotLatched,
  EventName.wrongGear,
  EventName.reverseGear,
  EventName.speedTooHigh,
  EventName.brakeHold,
  EventName.parkBrake,
  EventName.belowSteerSpeed,
})


def filter_car_events(events):
  return [event for event in events if event.name not in _SUPPRESSED_CAR_EVENTS]
