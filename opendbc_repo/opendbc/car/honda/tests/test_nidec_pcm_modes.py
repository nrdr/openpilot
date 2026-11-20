"""Startup mode isolation and the mmmorks-to-MVL shaping boundary."""
from dataclasses import replace

import pytest

from opendbc.car import structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.nidec_ecu_matched import EcuMatchedPCM
from opendbc.car.honda.tests.test_civic_pcm import control, interface
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC, CAR.HONDA_PILOT, CAR.HONDA_RIDGELINE, CAR.HONDA_ODYSSEY, CAR.HONDA_CLARITY])
@pytest.mark.parametrize("mode", [0, 1, 2])
def test_pcm_modes_are_exclusive(car, mode):
  ci, _ = interface(car, pcm_mode=mode)
  assert ci.CC.ecu_matched_pcm == (mode == 1)
  assert ci.CC.civic_pcm == (mode == 2 and car == CAR.HONDA_CIVIC)
  assert not (ci.CC.ecu_matched_pcm and ci.CC.civic_pcm)
  baseline, _ = interface(car, pcm_mode=0)
  assert [x.to_dict() for x in ci.CP.safetyConfigs] == [x.to_dict() for x in baseline.CP.safetyConfigs]
  assert ci.CP.minEnableSpeed == baseline.CP.minEnableSpeed


@pytest.mark.parametrize("car,interceptor", [(CAR.HONDA_CIVIC, True), (CAR.HONDA_CLARITY, True), (CAR.HONDA_CIVIC_BOSCH, False)])
@pytest.mark.parametrize("mode", [0, 1, 2])
def test_excluded_paths_ignore_both_settings(car, interceptor, mode):
  ci, _ = interface(car, interceptor=interceptor, pcm_mode=mode, wind_brake=False)
  assert not ci.CC.ecu_matched_pcm
  assert not ci.CC.civic_pcm
  assert ci.CC.nidec_wind_brake
  assert not ci.CP.flags & (HondaFlags.NIDEC_PCM_ECU_MATCHED | HondaFlags.NIDEC_PCM_EXPERIMENTAL)


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC, CAR.HONDA_CIVIC_BOSCH])
@pytest.mark.parametrize("mode", [0, 1, 2])
def test_live_pedal_wind_choice_does_not_change_pcm_or_bosch_commands(car, mode):
  reference, _ = interface(car, pcm_mode=mode)
  changed, config = interface(car, pcm_mode=mode)
  for tick in range(120):
    config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, pedal_wind_brake=tick < 30 or tick >= 90)
    cc = control(.5 if tick < 60 else -.5).as_reader()
    _, baseline = reference.apply(cc, structs.CarControlSP(), tick * 10_000_000)
    _, actual = changed.apply(cc, structs.CarControlSP(), tick * 10_000_000)
    assert actual == baseline


def test_off_ignores_retired_bool_and_experimental_reference():
  ci, config = interface(pcm_mode=0)
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, ecu_matched_long=True)
  sp = structs.CarControlSP(civicPcmEnabled=True, civicPcmReferenceSpeed=20., civicPcmReferenceMonoTime=1)
  ci.apply(control(-0.5).as_reader(), sp, 10_000_000)
  assert not ci.CC.civic_pcm_speed_control
  assert ci.CC.guard_pcm_learner  # Upstream MVL also protects learning near the PCM governor.
  assert ci.CC.nidec_pid_factor < 0  # Restore upstream's additive decel feedback.
  assert ci.CC.pcm_constraints.accel == 0


def test_original_ramps_sign_interval_and_reset():
  shaper = EcuMatchedPCM()
  assert shaper.update_accel(1., active=True) == pytest.approx(.05)
  for _ in range(20):
    shaper.update_accel(1., active=True)
    shaper.coast(1., 0., 20.)
  assert shaper.accel == 1.
  last = shaper.accel
  while shaper.last_sign != -1:
    current = shaper.update_accel(-1., active=True)
    assert current - last == pytest.approx(-.06)
    last = current
    if shaper.last_sign != -1:
      shaper.coast(0., 1., 20.)
  assert shaper.coast_frames == 20
  assert all(shaper.coast(0., 1., 20.) for _ in range(20))
  assert not shaper.coast(0., 1., 20.)
  assert shaper.update_accel(1., active=False) == 0
  assert (shaper.accel, shaper.last_sign, shaper.coast_frames) == (0., 0, 0)


@pytest.mark.parametrize("speed,deadband", [(2.5, .08), (10., .06), (20., .03), (30., .005)])
def test_original_deadband_is_normalized_not_pcm_bytes(speed, deadband):
  shaper = EcuMatchedPCM()
  assert shaper.coast(deadband / 2, 0., speed)
  assert shaper.coast(0., deadband / 2, speed)
  assert not shaper.coast(deadband, 0., speed)
  assert not shaper.coast(0., deadband, speed)


def test_ecu_matched_pid_limit_does_not_leak_to_off_or_interceptor():
  for mode, interceptor, expected in [(0, False, .2), (1, False, .4), (2, False, 2.), (1, True, 2.)]:
    ci, _ = interface(pcm_mode=mode, interceptor=interceptor)
    assert CarInterface.get_pid_accel_limits(ci.CP, ci.CP_SP, 30., 30.)[1] == pytest.approx(expected)


def test_ecu_coast_reaches_wire_and_later_brakes_are_not_permanently_blocked():
  ci, _ = interface(pcm_mode=1)
  ci.CS.out.vEgo = 10.
  for tick in range(100):
    ci.apply(control(.05).as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert ci.CC.new_accel == 0
  assert ci.CC.apply_brake_last == 0
  for tick in range(100, 300):
    ci.apply(control(-1.5).as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert ci.CC.apply_brake_last > 0
  assert ci.CC.new_accel == 0


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_wind_setting_changes_pcm_friction_credit_only(mode):
  on, _ = interface(pcm_mode=mode, wind_brake=True)
  off, _ = interface(pcm_mode=mode, wind_brake=False)
  for ci in (on, off):
    ci.CS.out.vEgo = 30.
    ci.CC.windfactor = 3.
  for tick in range(60):
    for ci in (on, off):
      ci.apply(control(-1.).as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert on.CC.windfactor == off.CC.windfactor == 3.
  if mode == 2:
    assert off.CC.apply_brake_last == on.CC.apply_brake_last > 0
  else:
    assert off.CC.apply_brake_last > on.CC.apply_brake_last
  assert on.CC.nidec_pid_factor == off.CC.nidec_pid_factor


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_wind_setting_does_not_change_propulsion_mapping(mode):
  on, _ = interface(pcm_mode=mode, wind_brake=True)
  off, _ = interface(pcm_mode=mode, wind_brake=False)
  for ci in (on, off):
    ci.CS.out.vEgo = 30.
    ci.CC.windfactor = 2.
  for tick in range(300):
    cc = control(1.)
    assert on.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)[1] == \
           off.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)[1]


@pytest.mark.parametrize("mode,expected_step", [(0, .03), (1, .01), (2, .001)])
def test_stop_ramp_setting_is_confined_to_experimental_pcm(mode, expected_step):
  ci, config = interface(pcm_mode=mode)
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, stopping_decel_rate=.1)
  cc = control(-4.)
  cc.actuators.longControlState = structs.CarControl.Actuators.LongControlState.stopping
  # Settle the ECU request ramp/deadband, then inspect its brake ramp alone.
  for tick in range(100):
    ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  ci.CC.brake_last = 0.
  ci.apply(cc.as_reader(), structs.CarControlSP(), 1_000_000_000)
  assert ci.CC.brake_last == pytest.approx(expected_step)


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_factory_acc_never_enables_pcm_experiments(mode):
  from opendbc.car.honda.carcontroller import CarController
  from opendbc.car.honda.values import DBC

  ci, config = interface(pcm_mode=mode, wind_brake=False)
  ci.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  ci.CC = CarController(DBC[CAR.HONDA_CIVIC], ci.CP, ci.CP_SP, config.honda)
  assert not ci.CC.nidec_pcm and not ci.CC.civic_pcm and not ci.CC.ecu_matched_pcm
  assert ci.CC.nidec_wind_brake
  for tick in range(100):
    _, packets = ci.apply(control(-1.).as_reader(), structs.CarControlSP(), tick * 10_000_000)
    assert not any(addr == 0x1FA for addr, _, _ in packets)


@pytest.mark.parametrize("reason", ["inactive", "gas", "brake", "aeb", "cancel"])
def test_ecu_rules_bypass_overrides_without_changing_upstream_arbitration(reason):
  upstream, _ = interface(pcm_mode=0)
  matched, _ = interface(pcm_mode=1)
  for ci in (upstream, matched):
    ci.CS.out.gasPressed = reason == "gas"
    ci.CS.out.brakePressed = reason == "brake"
    ci.CS.out.stockAeb = reason == "aeb"
  for tick in range(100):
    cc = control(-1. if tick > 50 else 1.)
    cc.longActive = reason != "inactive"
    cc.cruiseControl.cancel = reason == "cancel"
    a = upstream.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)[1]
    b = matched.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)[1]
    assert a == b
    assert matched.CC.ecu_constraints.accel == matched.CC.ecu_constraints.coast_frames == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_ecu_invalid_requests_reset_shaper(value):
  shaper = EcuMatchedPCM()
  shaper.update_accel(1., active=True)
  assert shaper.update_accel(value, active=True) == 0.
  assert (shaper.accel, shaper.last_sign, shaper.coast_frames) == (0., 0, 0)
