from copy import deepcopy
import math

import pytest

from opendbc.car.honda.civic_pcm import speed_deadzone_target
from opendbc.car.honda.tests.test_civic_pcm import interface, control
from opendbc.car.honda.tests.test_civic_pcm_speed_control import apply, reference, START


@pytest.mark.parametrize("maximum", [0., .01, .05, .15, .20])
@pytest.mark.parametrize("speed", [0., 2.3, 4.5, 9., 20., 35.])
@pytest.mark.parametrize("error", [-1., -.2, -.15, -.01, 0., .01, .15, .2, 1.])
def test_speed_units_continuity_and_zero_to_nine_ramp(maximum, speed, error):
  width = maximum * min(speed / 9., 1.)
  actual = speed_deadzone_target(speed + error, speed, maximum)
  assert actual == pytest.approx(speed + math.copysign(max(abs(error) - width, 0.), error))
  assert abs(actual - speed) <= abs(error) + 1e-12


@pytest.mark.parametrize("bad", [True, False, None, -1., .21, float("nan"), float("inf"), ".15"])
def test_invalid_configuration_does_not_change_command(bad):
  assert speed_deadzone_target(20.1, 20., bad) == 20.1


@pytest.mark.parametrize("mvl", [False, True])
def test_deadband_preserves_friction_brakes_wind_bypass_and_saved_learning(mvl):
  off, _ = interface(mvl=mvl, learning=True, speed_deadzone=0.)
  on, _ = interface(mvl=mvl, learning=True, speed_deadzone=.15)
  assert not on.CC.nidec_wind_brake
  before = deepcopy(on.CC.speed_factors)
  changed = False
  for tick in range(750):
    accel = .5 if tick < 650 else -.3
    apply(off, accel, tick)
    apply(on, accel, tick)
    changed |= off.CC.pcm_speed_sent != on.CC.pcm_speed_sent
    assert off.CC.apply_brake_last == on.CC.apply_brake_last
  assert changed
  assert on.CC.speed_factors == before
  assert off.CC.speed_factors != before


@pytest.mark.parametrize("reason", ["inactive", "brake", "aeb", "stale"])
def test_deadband_does_not_hold_propulsion_through_release(reason):
  ci, _ = interface(mvl=True, learning=True, speed_deadzone=.2)
  for tick in range(100):
    apply(ci, .5, tick)
  cc, now = control(.5), START + 1_000_000_000
  sp = reference(20., now)
  if reason == "inactive":
    cc.enabled = cc.longActive = False
  elif reason == "brake":
    ci.CS.out.brakePressed = True
  elif reason == "aeb":
    ci.CS.out.stockAeb = True
  else:
    sp.civicPcmReferenceMonoTime = START
  ci.apply(cc.as_reader(), sp, now)
  assert ci.CC.new_accel == ci.CC.pcm_gas_sent == 0


def test_launch_and_off_mode_are_unchanged():
  for mode, speed in ((0, 20.), (1, 20.), (2, 0.)):
    a, _ = interface(pcm_mode=mode, speed_deadzone=0.)
    b, _ = interface(pcm_mode=mode, speed_deadzone=.2)
    for ci in (a, b):
      ci.CS.out.vEgo = speed
      ci.CS.out.standstill = speed == 0.
    for tick in range(50):
      assert apply(a, .5, tick, speed=speed)[1] == apply(b, .5, tick, speed=speed)[1]
