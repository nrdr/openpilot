"""Offline regressions for Civic PCM timing, authority and platform isolation."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car import structs
from opendbc.car.honda import civic_pcm
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.honda.tests.test_mvl_nrdr_integration import learned_state
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


def interface(car=CAR.HONDA_CIVIC, *, interceptor=False, learning=False, wind_bench=False, pcm_mode=2, wind_brake=True, mvl=False, speed_deadzone=0.0):
  config = make_test_car_config()
  config = replace(config, honda=replace(config.honda, nidec_pcm_mode=pcm_mode, nidec_wind_brake=wind_brake,
                                         mvl_longitudinal=mvl, civic_pcm_speed_deadzone=speed_deadzone))
  if wind_bench:
    config = replace(config, honda=replace(config.honda, civic_pcm_wind_credit_bench=True))
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, live_learning_gas=learning)
  fingerprint = {i: {} for i in range(7)}
  if interceptor:
    fingerprint[0][0x201] = 6
  cp = CarInterface.get_params(car, fingerprint, [], alpha_long=True, is_release=False, docs=False, interface_config=config)
  sp = CarInterface.get_params_sp(cp, car, fingerprint, [], alpha_long=True, is_release_sp=False, docs=False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 20.0
  ci.CS.out.aEgo = 0.0
  ci.CS.out.cruiseState.speed = 30.0
  ci.CS.out.cruiseState.available = True
  ci.CS.out.standstill = False
  ci.CS.steer_control_active = True
  return ci, config


def control(accel):
  cc = structs.CarControl(enabled=True, longActive=True)
  cc.actuators.accel = float(accel)
  cc.actuators.longControlState = structs.CarControl.Actuators.LongControlState.pid
  return cc


@pytest.mark.parametrize("car,interceptor,expected", [
  (CAR.HONDA_CIVIC, False, True),
  (CAR.HONDA_CIVIC, True, False),
  (CAR.HONDA_CLARITY, False, False),
  (CAR.HONDA_CLARITY, True, False),
  (CAR.HONDA_CIVIC_BOSCH, False, False),
  (CAR.HONDA_RIDGELINE, False, False),
])
def test_exact_platform_scope(car, interceptor, expected):
  ci, _ = interface(car, interceptor=interceptor)
  assert ci.CC.civic_pcm is expected


@pytest.mark.parametrize("open_long,bosch,stock", [(False, False, False), (True, True, False), (True, False, True)])
def test_other_modes_do_not_enable_patch(open_long, bosch, stock):
  cp = SimpleNamespace(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=open_long,
                       flags=HondaFlags.BOSCH if bosch else 0)
  sp = SimpleNamespace(enableGasInterceptor=False, flags=HondaFlagsSP.STOCK_LONGITUDINAL if stock else 0)
  assert not civic_pcm.uses_civic_pcm(cp, sp)


@pytest.mark.parametrize("alpha", [0.02, 0.020000021206643934, 0.5, 1.0])
def test_small_target_reduction_never_becomes_zero_and_recovers_promptly(alpha):
  average, sensitivity, held, command = 100.0, 0.0, 100, 100
  sent = []
  for tick in range(120):
    target = 100.0 if tick < 20 else 98.0
    average, sensitivity = civic_pcm.advance_model(average, sensitivity, held, alpha)
    prior = command
    command = civic_pcm.gas_command(target, average, prior, alpha, False, 198)
    assert command <= prior + 2
    if tick % civic_pcm.PCM_GAS_TICKS == 0:
      held = command
      sent.append(command)
  assert min(sent) >= 88
  assert abs(sent[4] - 98) <= 2
  assert abs(sent[-1] - 98) <= 1


def test_fractional_slow_taper_does_not_quantize_into_gas_cuts():
  average, sensitivity, held, command = 100.0, 0.0, 100, 100
  sent = []
  for tick in range(200):
    target = max(100.0 - tick * 0.05, 90.0)
    average, sensitivity = civic_pcm.advance_model(average, sensitivity, held, 0.02)
    command = civic_pcm.gas_command(target, average, command, 0.02, False, 198)
    if tick % 10 == 0:
      held = command
      sent.append(command)
  assert min(sent) >= 87
  assert max(abs(a - b) for a, b in zip(sent, sent[1:], strict=False)) <= 4


@pytest.mark.parametrize("recovery,rise", [(False, 2), (True, 7)])
@pytest.mark.parametrize("alpha", [0.02, 0.5, 1.0])
def test_full_authority_and_existing_rise_envelope_are_preserved(recovery, rise, alpha):
  average, sensitivity, held, command = 0.0, 0.0, 0, 0
  for tick in range(250):
    average, sensitivity = civic_pcm.advance_model(average, sensitivity, held, alpha)
    previous = command
    command = civic_pcm.gas_command(198.0, average, previous, alpha, recovery, 198)
    assert 0 <= command <= min(previous + rise, 198)
    if tick % 10 == 0:
      held = command
  assert command == held == 198


@pytest.mark.parametrize("alpha", [float('nan'), float('inf'), -1.0, 0.0, 0.02, 0.5, 1.0, 3.0])
def test_response_bounds_and_immediate_zero_request(alpha):
  assert 0.02 <= civic_pcm.response_per_tick(alpha) <= 1.0
  assert civic_pcm.gas_command(0.0, 100.0, 198, alpha, False, 198) == 0


def test_model_uses_only_transmitted_command_between_sends():
  average, sensitivity = civic_pcm.advance_model(50.0, 0.0, 100, 0.02)
  assert average == 51.0
  assert sensitivity == 50.0


@pytest.mark.parametrize("rpm,expected_gas", [(1500, 110), (0, 198)])
def test_existing_launch_seed_and_breakaway_lead_are_preserved(rpm, expected_gas):
  ci, _ = interface()
  ci.CS.out.vEgo = 0.0
  ci.CS.out.standstill = True
  ci.CS.engine_rpm = rpm
  _, messages = ci.apply(control(0.8).as_reader(), structs.CarControlSP(), 0)
  assert ci.CC.launch_active
  gas = [dat[2] for address, dat, _ in messages if address == 0x30C]
  speed = [int.from_bytes(dat[:2], 'big') * 0.01 / 3.6 for address, dat, _ in messages if address == 0x30C]
  assert gas == [expected_gas]
  assert speed == pytest.approx([ci.CC.dv_break], abs=0.003)


def test_learning_off_freezes_coefficients_without_disabling_timing_fix():
  ci, config = interface(learning=False)
  ci.CC.average_factor = 0.02
  before = learned_state(ci.CC)
  for tick in range(400):
    ci.apply(control(0.5).as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert learned_state(ci.CC) == before
  assert ci.CC.civic_pcm
  assert all(all(key.startswith('lat_accel_factor_') for key in item) for item in config.honda.provider.persisted)


def test_compatibility_path_braking_takes_priority_when_wind_credit_is_disabled():
  ci, _ = interface()
  ci.CS.out.aEgo = 0.8
  ci.CC.nidec_pid.i = -0.5
  ci.CC.speed_factors = dict.fromkeys(ci.CC.speed_factors, 4.0)
  ci.CC.speed_alphas = dict.fromkeys(ci.CC.speed_alphas, 0.0)
  cc = control(0.3)
  out, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), 0)
  assert ci.CC.accel < 0  # The existing gas/brake feedback correction still runs.
  speed = [int.from_bytes(dat[:2], 'big') * 0.01 / 3.6 for address, dat, _ in messages if address == 0x30C]
  assert ci.CC.pcm_constraints.accel > 0  # comfort shaping still computed a positive request
  assert speed == [0.0] and out.brake > 0  # direct braking takes precedence; no wind credit
  assert ci.CC.speed_cmd_hist[-1][0] == pytest.approx(0.3)


def test_output_telemetry_matches_actual_gas_packet_and_holds_between_sends():
  ci, _ = interface()
  ci.CC.average_factor = 0.02
  last_sent = 0
  for tick in range(250):
    cc = control(0.4 + 0.2 * np.sin(tick / 25.0))
    out, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
    for address, dat, _ in messages:
      if address == 0x30C:
        last_sent = dat[2]
    assert out.gas == pytest.approx(last_sent / ci.CC.params.NIDEC_GAS_MAX, abs=1e-6)


@pytest.mark.parametrize("reason", ["brake", "disengage"])
def test_braking_and_disengagement_do_not_slew_gas_release(reason):
  ci, _ = interface()
  cc = control(1.0)
  for tick in range(100):
    ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  if reason == 'brake':
    cc.actuators.accel = -3.0
  else:
    cc.enabled = cc.longActive = False
  _, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), 1_000_000_000)
  gas = [dat[2] for address, dat, _ in messages if address == 0x30C]
  assert gas == [0]
  if reason == 'brake':
    # The existing brake hysteresis/rise limiter still applies. Once it sends
    # braking, the gas guard must remain exact zero, without a comfort fade.
    saw_brake = False
    for tick in range(101, 121):
      _, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
      saw_brake |= any(int.from_bytes(dat[:2], 'big') >> 6 > 0 for address, dat, _ in messages if address == 0x1FA)
      assert all(dat[2] == 0 for address, dat, _ in messages if address == 0x30C)
    assert saw_brake


def test_response_learner_does_not_fit_a_speed_limited_or_saturated_channel():
  ci, _ = interface(learning=True)
  ci.CS.car_gas_available = True
  ci.CS.engine_rpm = 1500
  ci.CS.car_gas = 0.0
  ci.CC.speed_factors = dict.fromkeys(ci.CC.speed_factors, 4.0)
  ci.CC.speed_alphas = dict.fromkeys(ci.CC.speed_alphas, 0.0)
  before = ci.CC.average_factor, ci.CC.car_gas_per_pcm_gas
  for tick in range(400):
    cc = control(0.05)
    ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert (ci.CC.average_factor, ci.CC.car_gas_per_pcm_gas) == before
