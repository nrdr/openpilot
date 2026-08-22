import importlib.util
from pathlib import Path

import pytest

from openpilot.cereal import log
from opendbc.car import structs
from openpilot.sunnypilot.nrdr.events import allow_longitudinal, filter_car_events, is_drivable_gear, keep_lateral_active


EventName = log.OnroadEvent.EventName
GearShifter = structs.CarState.GearShifter
FORWARD_GEAR_CASES = (
  (GearShifter.drive, (), "mock"),
  (GearShifter.sport, (GearShifter.sport,), "honda"),
  (GearShifter.low, (), "honda"),
  (GearShifter.brake, (GearShifter.brake,), "honda"),
  (GearShifter.eco, (GearShifter.eco,), "mock"),
  (GearShifter.manumatic, (GearShifter.manumatic,), "mock"),
)


def make_car_state(gear=GearShifter.drive, *, door_open=False, seatbelt_unlatched=False, parking_brake=False):
  cs = structs.CarState()
  cs.gearShifter = gear
  cs.doorOpen = door_open
  cs.seatbeltUnlatched = seatbelt_unlatched
  cs.parkingBrake = parking_brake
  return cs


def make_event(name):
  event = log.OnroadEvent.new_message()
  event.name = name
  return event


def test_car_events_remain_visible_and_reverse_is_never_suppressed():
  names = (EventName.doorOpen, EventName.seatbeltNotLatched, EventName.wrongGear,
           EventName.reverseGear, EventName.brakeHold, EventName.parkBrake)
  events = [make_event(name) for name in names]
  assert [event.name for event in filter_car_events(events)] == list(names)
  assert not keep_lateral_active(EventName.reverseGear)


@pytest.mark.parametrize("event_name", [
  EventName.doorOpen,
  EventName.seatbeltNotLatched,
  EventName.wrongGear,
  EventName.brakeHold,
  EventName.belowEngageSpeed,
])
def test_development_events_keep_lateral_active(event_name):
  assert keep_lateral_active(event_name)


def test_historical_below_steer_speed_suppression_is_preserved():
  events = [make_event(EventName.speedTooHigh), make_event(EventName.belowSteerSpeed), make_event(EventName.canError)]
  assert [event.name for event in filter_car_events(events)] == [EventName.speedTooHigh, EventName.canError]


@pytest.mark.parametrize("gear,platform_gears,brand", FORWARD_GEAR_CASES)
def test_validated_forward_gears_are_drivable_and_allow_longitudinal(gear, platform_gears, brand):
  assert is_drivable_gear(gear, platform_gears, brand)
  assert allow_longitudinal(make_car_state(gear), platform_gears, brand)


@pytest.mark.parametrize("gear", [GearShifter.unknown, GearShifter.park, GearShifter.neutral, GearShifter.reverse])
def test_non_forward_gears_inhibit_longitudinal(gear):
  assert not is_drivable_gear(gear, (), "honda")
  assert not allow_longitudinal(make_car_state(gear), (), "honda")


@pytest.mark.parametrize("condition", ["door_open", "seatbelt_unlatched", "parking_brake"])
def test_stationary_safety_conditions_inhibit_longitudinal_only(condition):
  assert not allow_longitudinal(make_car_state(**{condition: True}), (), "honda")


def test_combined_longitudinal_inhibitors_do_not_mask_each_other():
  cs = make_car_state(door_open=True, seatbelt_unlatched=True)
  assert not allow_longitudinal(cs, (), "honda")
  cs.doorOpen = False
  assert not allow_longitudinal(cs, (), "honda")
  cs.seatbeltUnlatched = False
  assert allow_longitudinal(cs, (), "honda")


def test_brake_hold_does_not_disable_longitudinal():
  cs = make_car_state()
  cs.brakeHoldActive = True
  assert allow_longitudinal(cs, (), "honda")


def test_clean_overlay_retains_stock_policy():
  overlay_path = Path(__file__).parents[3] / "release" / "clean_overlay" / "events.py"
  spec = importlib.util.spec_from_file_location("clean_events", overlay_path)
  assert spec is not None and spec.loader is not None
  clean_events = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(clean_events)

  assert not clean_events.keep_lateral_active(EventName.doorOpen)
  assert clean_events.allow_longitudinal(make_car_state(door_open=True), (), "honda")
  assert clean_events.is_drivable_gear(GearShifter.drive, ())
  assert not clean_events.is_drivable_gear(GearShifter.low, ())
  assert clean_events.is_drivable_gear(GearShifter.low, (GearShifter.low,))
