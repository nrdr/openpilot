"""Decode Bosch ACC_CONTROL during a stop/release transition; no vehicle I/O."""
import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.honda.tests.test_civic_pcm import control, interface
from opendbc.car.honda.values import CAR, DBC


@pytest.mark.parametrize("car,has_release_bit", [(CAR.HONDA_CIVIC_BOSCH, True), (CAR.HONDA_CIVIC_2022, False)])
def test_bosch_stop_follows_sent_acceleration_not_just_planner_state(car, has_release_bit):
  ci, _ = interface(car)
  decoder = CANParser(DBC[car][Bus.pt], [("ACC_CONTROL", 50)], ci.CC.CAN.pt)
  # Planner requests braking while the stopping ramp is still sending positive accel.
  # Then check zero, negative, release without a state change, and pid with negative accel.
  cases = [("pid", .003, .003, 0), ("stopping", -.1, .001, 0), ("stopping", 0., 0., 1),
           ("stopping", -.1, -.002, 2), ("stopping", .25, .25, 0), ("pid", -.1, -.1, 0)]
  if car == CAR.HONDA_CIVIC_BOSCH:
    # Owner decision (Bosch-A port): on Bosch-A cars Testing's BoschLongitudinal replaces nrdr's brake_pid/stopping
    # ramp, so the planner accel is sent as-is (and the last case runs through its brake onset/edge smoothing).
    # The counter follows Testing's rule (SOURCE carcontroller l.257): every stopping frame counts, whatever the
    # accel, so standstill holds through the positive-accel stopping frame. The last case's sent accel was observed.
    cases = [("pid", .003, .003, 0), ("stopping", -.1, -.1, 1), ("stopping", 0., 0., 2),
             ("stopping", -.1, -.1, 3), ("stopping", .25, .25, 4), ("pid", -.1, -0.07445255585395508, 0)]
  for frame, (state, accel, sent, expected_counter) in enumerate(cases):
    cc = control(accel)
    cc.actuators.longControlState = state
    # ACC_CONTROL is sent on even frames.
    for tick in (2 * frame, 2 * frame + 1):
      now = tick * 10_000_000
      _, msgs = ci.apply(cc.as_reader(), structs.CarControlSP(), now)
      updated = decoder.update([(now, msgs)])
      if tick % 2 == 0:
        assert updated
        assert ci.CC.accel == pytest.approx(sent)
        assert ci.CC.stopping_counter == expected_counter
        wire = decoder.vl["ACC_CONTROL"]
        assert wire["STANDSTILL"] == int(expected_counter > 0)
        if has_release_bit:
          assert wire["STANDSTILL_RELEASE"] == int(expected_counter == 0)
