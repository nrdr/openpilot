"""Regressions for the planner-linked Civic PCM candidate."""
from dataclasses import replace

import pytest

from opendbc.car import structs
from opendbc.car.honda import civic_pcm
from opendbc.car.honda.nidec_pcm_constraints import taper_positive_accel
from opendbc.car.honda.tests.test_civic_pcm import interface, control
from opendbc.car.honda.tests.test_mvl_nrdr_integration import learned_state
from opendbc.car.honda.values import CAR

START = 10_000_000_000


def reference(speed=20.0, stamp=START):
  return structs.CarControlSP(civicPcmEnabled=True, civicPcmReferenceSpeed=speed, civicPcmReferenceMonoTime=stamp)


def apply(ci, accel, tick=0, speed=20.0):
  now = START + tick * 10_000_000
  return ci.apply(control(accel).as_reader(), reference(speed, now), now)


def gas_packets(messages):
  return [dat[2] for address, dat, _ in messages if address == 0x30C]


@pytest.mark.parametrize('preexisting_launch', [False, True])
def test_no_pcm_propulsion_while_waiting_at_a_stop(preexisting_launch):
  ci, _ = interface()
  ci.CS.out.vEgo = 0.0
  ci.CS.out.standstill = True
  ci.CS.engine_rpm = 1500
  states = structs.CarControl.Actuators.LongControlState
  if preexisting_launch:
    apply(ci, .8, speed=0.)
    assert ci.CC.launch_active
  packets = []
  for tick in range(1, 161):
    now = START + tick * 10_000_000
    cc = control(.10 if tick <= 10 else -.08)
    cc.actuators.longControlState = states.off if tick == 1 else states.stopping
    if tick == 96:
      ci.CS.out.standstill = False
      ci.CS.out.vEgo = .25   # wheel motion is not permission to restart
    _, msgs = ci.apply(cc.as_reader(), reference(.6, now), now)
    assert ci.CC.new_accel == 0
    assert not ci.CC.launch_active
    packets.extend(dat[:3] for addr, dat, _ in msgs if addr == 0x30C)
  assert packets == [bytes(3)] * 16

  # A genuine departure is still handled by the normal positive-plan path.
  ci.CS.out.vEgo = 0.
  ci.CS.out.standstill = True
  for tick in range(161, 191):
    apply(ci, .8, tick, speed=.1)
  assert ci.CC.launch_active
  assert ci.CC.pcm_gas_sent > 0 and ci.CC.pcm_speed_sent > 0


@pytest.mark.parametrize('accel', [.01, .1, .5, 1., 2.])
def test_full_acceleration_allowance_is_preserved(accel):
  ci, _ = interface()
  ci.CC.average_factor = .02
  for tick in range(100):
    _, messages = apply(ci, accel, tick)
  assert ci.CC.pcm_gas_sent == ci.CC.params.NIDEC_GAS_MAX == 198
  # Experimental includes the former opt-in positive-command taper. Tiny
  # requests can therefore become neutral without reducing the gas allowance.
  assert ci.CC.pcm_speed_sent == pytest.approx(20. + 4. * taper_positive_accel(accel, 20.))
  assert ci.CC.accel == pytest.approx(accel)


def test_positive_request_cannot_inherit_negative_integral_or_bias():
  ci, _ = interface()
  ci.CS.out.aEgo = .8
  ci.CC.nidec_pid.i = -1.5
  ci.CC.speed_alphas = dict.fromkeys(ci.CC.speed_alphas, -5.0)
  for tick in range(100):
    _, messages = apply(ci, .3, tick)
    assert ci.CC.apply_brake_last == 0
  assert ci.CC.accel == pytest.approx(.3)
  assert ci.CC.nidec_pid.i == ci.CC.nidec_pid_factor == 0.0
  assert ci.CC.pcm_speed_sent == pytest.approx(20. + 4. * taper_positive_accel(.3, 20.))


def test_zero_acceleration_tracks_reference_not_a_target_chasing_current_speed():
  ci, _ = interface()
  ci.CS.out.vEgo = 21.0
  ci.CC.speed_alphas = dict.fromkeys(ci.CC.speed_alphas, 1.5)
  _, messages = apply(ci, 0., speed=20.)
  assert ci.CC.pcm_speed_sent == 20.0
  assert gas_packets(messages)[0] <= 20


@pytest.mark.parametrize('accel', [-.5, -1., -3., -4.])
def test_material_slowdown_releases_gas_before_brake_hysteresis(accel):
  ci, _ = interface()
  for tick in range(100):
    apply(ci, 1.0, tick)
  _, messages = apply(ci, accel, 100)
  assert gas_packets(messages) == [0]
  for tick in range(101, 150):
    _, messages = apply(ci, accel, tick)
    assert all(gas == 0 for gas in gas_packets(messages))
  assert ci.CC.apply_brake_last > 0


@pytest.mark.parametrize('reason', ['disengage', 'brake', 'aeb', 'stale', 'future', 'nonfinite'])
def test_safety_release_does_not_get_a_comfort_fade(reason):
  ci, _ = interface()
  for tick in range(100):
    apply(ci, 1.0, tick)
  cc, sp, now = control(1.), reference(20., START + 1_000_000_000), START + 1_000_000_000
  if reason == 'disengage':
    cc.enabled = cc.longActive = False
  elif reason == 'brake':
    ci.CS.out.brakePressed = True
  elif reason == 'aeb':
    ci.CS.out.stockAeb = True
  elif reason == 'stale':
    sp.civicPcmReferenceMonoTime = now - civic_pcm.REFERENCE_MAX_AGE_NS - 1
  elif reason == 'future':
    sp.civicPcmReferenceMonoTime = now + 1
  elif reason == 'nonfinite':
    sp.civicPcmReferenceSpeed = float('nan')
  _, messages = ci.apply(cc.as_reader(), sp, now)
  assert gas_packets(messages) == [0]


@pytest.mark.parametrize('rpm,gas', [(1500, 110), (0, 198)])
def test_launch_seed_is_preserved_but_requires_fresh_reference(rpm, gas):
  ci, _ = interface()
  ci.CS.out.vEgo = 0.0
  ci.CS.out.standstill = True
  ci.CS.engine_rpm = rpm
  _, messages = apply(ci, .8, speed=0.)
  assert gas_packets(messages) == [gas]
  _, messages = ci.apply(control(.8).as_reader(), reference(0., START), START + 1_000_000_000)
  assert gas_packets(messages) == []  # no HUD send on tick 1
  assert ci.CC.new_accel == 0


@pytest.mark.parametrize('learning', [False, True])
def test_old_identifiers_are_not_retrained_or_persisted_for_a_different_command_law(learning):
  ci, config = interface(learning=learning)
  before = learned_state(ci.CC)
  for tick in range(6100):
    apply(ci, .5, tick)
  assert learned_state(ci.CC) == before
  assert all(all(key.startswith('lat_accel_factor_') for key in item) for item in config.honda.provider.persisted)


@pytest.mark.parametrize('car,interceptor', [(CAR.HONDA_CLARITY, False), (CAR.HONDA_CLARITY, True),
                                          (CAR.HONDA_CIVIC, True), (CAR.HONDA_CIVIC_BOSCH, False)])
def test_other_platforms_ignore_the_civic_mode(car, interceptor):
  ci, config = interface(car, interceptor=interceptor)
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, live_learning_gas=False)
  apply(ci, .5)
  assert not ci.CC.civic_pcm_speed_control


def test_overshoot_allowance_is_continuous_and_never_inverts_past_its_target():
  commands = [civic_pcm.gas_allowance(.1, .1 + k * .01, .1, 198) for k in range(150)]
  assert max(abs(a - b) for a, b in zip(commands, commands[1:], strict=False)) <= 2.23
  assert min(commands) >= 19.8 - 1e-8
  assert civic_pcm.allowance_command(98., 100, False, 198) == 98


@pytest.mark.parametrize('age,valid', [(-1, False), (0, True), (250_000_000, True), (250_000_001, False)])
def test_reference_age_boundaries(age, valid):
  target = civic_pcm.reference_speed(reference(20.), START + age, .5)
  assert (target is not None) is valid
  if valid:
    assert target == pytest.approx(20. + .5 * age / 1e9)


def test_missing_mode_metadata_does_not_switch_command_laws_mid_drive():
  ci, _ = interface()
  for tick in range(100):
    apply(ci, .5, tick)
  _, messages = ci.apply(control(.5).as_reader(), structs.CarControlSP(), START + 1_000_000_000)
  assert ci.CC.civic_pcm_speed_control
  assert gas_packets(messages) == [0]


@pytest.mark.parametrize('gain', [float('nan'), float('inf'), .1, 100.])
def test_frozen_invalid_gain_fails_closed_without_rewriting_saved_tuning(gain):
  ci, config = interface()
  ci.CC.speed_factors = dict.fromkeys(ci.CC.speed_factors, gain)
  _, messages = apply(ci, .5)
  assert gas_packets(messages) == [0]
  assert ci.CC.pcm_speed_sent == 0.
  assert not config.honda.provider.persisted


@pytest.mark.parametrize('gain', [1., 4., 4.697697847, 10.915992881, 99.])
@pytest.mark.parametrize('accel', [0., .01, .1, .2, .5, 1., 2.])
def test_slowdown_preview_does_not_reduce_positive_acceleration_headroom(gain, accel):
  assert civic_pcm.speed_target(20., accel, gain) == pytest.approx(min(20. + gain * accel, 100.))


@pytest.mark.parametrize('gain', [1., 4., 4.697697847, 10.915992881, 99.])
def test_gentle_release_does_not_use_the_propulsion_gain_as_a_coasting_inverse(gain):
  # Highway trigger: a modest negative acceleration must not move a ~60 mph
  # reference several mph down just because the propulsion identifier is high.
  assert civic_pcm.speed_target(26.9, -.15, gain) == pytest.approx(26.75)
  assert civic_pcm.speed_target(26.9, -.15, gain) <= 26.9
  assert civic_pcm.speed_target(26.9, -.15, gain) >= max(26.9 - .15 * gain, 0.)


def test_slowdown_preview_is_continuous_at_zero_and_follows_a_falling_reference_immediately():
  gain = 10.915992881
  assert abs(civic_pcm.speed_target(20., 1e-9, gain) - civic_pcm.speed_target(20., -1e-9, gain)) < 2e-8
  assert civic_pcm.speed_target(19., -.1, gain) == pytest.approx(18.9)
  assert civic_pcm.speed_target(18., -.1, gain) == pytest.approx(17.9)
  assert civic_pcm.speed_target(0., -.1, gain) == 0.


def test_slowdown_target_can_be_below_actual_speed_without_a_hold_timer():
  ci, _ = interface()
  ci.CC.speed_factors = dict.fromkeys(ci.CC.speed_factors, 10.915992881)
  for tick in range(100):
    apply(ci, .3, tick)
  # A mild slowdown still lowers the speed command below vEgo. Only the extra
  # negative feedforward is bounded; this is not an ego-speed clamp.
  apply(ci, -.1, 100, speed=19.9)
  assert ci.CC.pcm_speed_sent == pytest.approx(19.8)
  assert ci.CC.pcm_speed_sent < ci.CS.out.vEgo


@pytest.mark.parametrize('accel', [-.49, -.3, -.1, 0., .1, .5, 2.])
def test_speed_target_is_monotonic_in_request_and_reference(accel):
  target = civic_pcm.speed_target(20., accel, 10.915992881)
  assert civic_pcm.speed_target(20., accel - .001, 10.915992881) <= target
  assert civic_pcm.speed_target(19.9, accel, 10.915992881) == pytest.approx(target - .1)
