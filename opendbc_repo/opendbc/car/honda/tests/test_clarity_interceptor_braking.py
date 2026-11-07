"""Clarity interceptor regressions through CarState, CarController and the actual CAN DBC."""
from dataclasses import replace

import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car import Bus, gen_empty_fingerprint, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, DBC, HondaSafetyFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaSafetyFlagsSP as SafetySP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


BRAKE, PEDAL, HUD = 0x1FA, 0x200, 0x30C
DT_NS = 10_000_000
# At 0–0.3 m/s, 0.33 pre-hysteresis minus the 0.01 gap and unit-factor
# wind leaves ~0.319: 1.53 m/s² on the hybrid map, truncated to 97 counts.
HOLD_COUNTS = 97
CLARITY_SAFETY = SafetySP.CLARITY_INTERCEPTOR_BRAKE | SafetySP.NIDEC_HYBRID | SafetySP.GAS_INTERCEPTOR


class Rig:
  def __init__(self, car=CAR.HONDA_CLARITY, *, interceptor=True, hybrid=True, stock=False, full_authority=True,
               dashboard_speed=0, alter_params=None):
    config = make_test_car_config(honda_stock_longitudinal=stock)
    config = replace(config, honda=replace(config.honda, clarity_interceptor_brake_bench=True))
    provider = config.honda.provider
    provider.live_tuning = replace(provider.live_tuning, live_learning_gas=False, full_brake_authority=full_authority,
                                   alt_dashboard_speed=dashboard_speed)
    fp = gen_empty_fingerprint()
    if hybrid:
      fp[0][0x184] = 8
    if interceptor:
      fp[0][0x201] = 6
    cp = CarInterface.get_params(car, fp, [], True, False, False, config)
    sp = CarInterface.get_params_sp(cp, car, fp, [], True, False, False)
    setup_interfaces(CarInterface, cp, sp, config)
    if alter_params is not None:
      alter_params(cp, sp)
    self.ci = CarInterface(cp, sp, config)
    self.ci.update([])
    dbc = DBC[car][Bus.pt]
    self.packer = CANPacker(dbc)
    self.decoder = CANParser(dbc, [('BRAKE_COMMAND', 50), ('GAS_COMMAND', 50), ('ACC_HUD', 10)], 0)
    self.now = 1_000_000_000

  def pcm_status(self, active):
    frame = self.packer.make_can_msg('POWERTRAIN_DATA', 0, {'ACC_STATUS': int(active)})
    state, _ = self.ci.update([(self.now, [frame])])
    return state.cruiseState.enabled

  def update_camera_and_pt(self, camera_brake, speed, driver):
    # Camera 0x1FA is on bus 2, distinct from the host's 0x1FA on bus 0. Decode
    # the hybrid field (standard brake stays zero); do not set CS.out.stockAeb.
    frames = []
    if self.now // DT_NS % 2 == 0:
      make = self.packer.make_can_msg
      kph = speed * CV.MS_TO_KPH
      gas_sensor = 600 if driver == 'gasPressed' else 0
      frames = [make('BRAKE_COMMAND', 2, {'AEB_REQ_1': int(camera_brake > 0), 'COMPUTER_BRAKE_HYBRID': camera_brake}),
                make('POWERTRAIN_DATA', 0, {'ACC_STATUS': 1, 'BRAKE_PRESSED': int(driver == 'brakePressed')}),
                make('GAS_SENSOR', 0, {'INTERCEPTOR_GAS': gas_sensor, 'INTERCEPTOR_GAS2': gas_sensor}),
                make('ENGINE_DATA', 0, {'XMISSION_SPEED': kph}),
                make('WHEEL_SPEEDS', 0, {f'WHEEL_SPEED_{s}': kph for s in ('FL', 'FR', 'RL', 'RR')})]
    state, _ = self.ci.update([(self.now, frames)])
    assert state.stockAeb == (camera_brake > 0)
    assert state.brakePressed == (driver == 'brakePressed')
    assert state.gasPressed == (driver == 'gasPressed')
    assert state.standstill == (speed == 0.)
    assert self.ci.CS.pcm_acc_active and not state.cruiseState.enabled

  def apply(self, accel=0., *, speed=10., stopped=False, state='pid', enabled=True, long_active=True, cancel=False, ticks=10,
            reference_speed=None, lead_speed=None, camera_brake=None, driver=None):
    if camera_brake is None:
      self.ci.CS.out.vEgo = speed
      self.ci.CS.out.standstill = stopped
    cc = structs.CarControl(enabled=enabled, longActive=long_active)
    cc.cruiseControl.cancel = cancel
    cc.actuators.accel = accel
    cc.actuators.longControlState = state
    if lead_speed is not None:
      cc.hudControl.leadVisible = True
      cc.hudControl.leadVLead = lead_speed
    packets = {}
    for _ in range(ticks):
      if camera_brake is not None:
        self.update_camera_and_pt(camera_brake, speed, driver)
      cc_sp = structs.CarControlSP()
      if reference_speed is not None:
        cc_sp.civicPcmEnabled = True
        cc_sp.civicPcmReferenceSpeed = reference_speed
        cc_sp.civicPcmReferenceMonoTime = self.now
      self.output, frames = self.ci.apply(cc.as_reader(), cc_sp, self.now)
      decoded = self.decoder.update([(self.now, frames)])
      for address, payload, bus in frames:
        if bus == 0 and address in (BRAKE, PEDAL, HUD):
          assert address in decoded, f'DBC rejected {address:#x}'
          packets.setdefault(address, []).append((bytes(payload), dict(self.decoder.vl[address])))
      self.now += DT_NS
    return packets


def field(packets, address, signal):
  # Only frames emitted in THIS call, never the previous value held by the parser.
  return [signals[signal] for _, signals in packets[address]]


def test_raw_acc_status_is_hidden_from_cruise_but_drives_wire_cancel():
  rig = Rig()
  assert rig.ci.CP_SP.safetyParam == CLARITY_SAFETY
  assert len(rig.ci.CP.safetyConfigs) == 1
  assert rig.ci.CP.safetyConfigs[0].safetyModel == structs.CarParams.SafetyModel.hondaNidec
  assert rig.ci.CP.safetyConfigs[0].safetyParam == 0
  assert not rig.ci.CP.dashcamOnly
  assert not rig.pcm_status(True)
  assert rig.ci.CS.pcm_acc_active
  engaged = rig.apply(.5)
  assert field(engaged, BRAKE, 'CRUISE_CANCEL_CMD') == [0] * 5
  # First scheduled brake packet after disengagement cancels even without a host cancel.
  off = rig.apply(enabled=False, long_active=False, state='off', ticks=2)
  assert field(off, BRAKE, 'CRUISE_CANCEL_CMD') == [1]
  assert not rig.pcm_status(False)
  assert not rig.ci.CS.pcm_acc_active
  assert field(rig.apply(enabled=False, long_active=False, state='off', ticks=2), BRAKE, 'CRUISE_CANCEL_CMD') == [0]
  assert field(rig.apply(cancel=True, ticks=2), BRAKE, 'CRUISE_CANCEL_CMD') == [1]  # explicit cancel survives even with raw PCM off


def test_enabled_but_long_inactive_releases_pcm_and_interceptor():
  rig = Rig()
  rig.pcm_status(True)
  assert field(rig.apply(1., ticks=40), PEDAL, 'ENABLE')[-1] == 1
  released = rig.apply(enabled=True, long_active=False, state='off')
  assert field(released, BRAKE, 'CRUISE_CANCEL_CMD') == [1] * 5
  assert field(released, HUD, 'PCM_SPEED') == [0]
  assert field(released, HUD, 'PCM_GAS') == [0]
  assert field(released, PEDAL, 'ENABLE') == [0] * 5
  assert all(payload[:4] == bytes(4) for payload, _ in released[PEDAL])


@pytest.mark.parametrize('camera_brake', [0, 60], ids=['aeb-clear', 'aeb-active'])
@pytest.mark.parametrize('override', ['disabled-stale-long', 'long-inactive', 'brakePressed', 'gasPressed', 'cancel'])
def test_override_relinquishes_latched_brake_and_cancels_live_pcm(override, camera_brake):
  rig = Rig()
  holding = rig.apply(speed=0., state='stopping', camera_brake=0, ticks=100)
  assert field(holding, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == HOLD_COUNTS
  released = rig.apply(1.5, speed=0., state='stopping', enabled=override != 'disabled-stale-long', camera_brake=camera_brake,
                       long_active=override != 'long-inactive', cancel=override == 'cancel', driver=override, ticks=2)
  assert field(released, BRAKE, 'CRUISE_CANCEL_CMD') == [1]
  assert field(released, BRAKE, 'COMPUTER_BRAKE_HYBRID') == [0]
  assert field(released, BRAKE, 'BRAKE_PUMP_REQUEST_HYBRID') == [0]
  assert field(released, BRAKE, 'COMPUTER_BRAKE_REQUEST') == [0]
  assert field(released, HUD, 'PCM_GAS') == [0]
  assert field(released, PEDAL, 'ENABLE') == [0]
  assert released[PEDAL][0][0][:4] == bytes(4)


def assert_aeb_propulsion_inhibited(packets):
  assert set(field(packets, HUD, 'PCM_SPEED')) == {0}
  assert set(field(packets, HUD, 'PCM_GAS')) == {0}
  assert set(field(packets, PEDAL, 'ENABLE')) == {0}
  assert all(payload[:4] == bytes(4) for payload, _ in packets[PEDAL])
  assert set(field(packets, BRAKE, 'CRUISE_CANCEL_CMD')) == {0}
  assert set(field(packets, BRAKE, 'AEB_REQ_1')) == {0}  # output is the host's request, not an echo of camera AEB


def test_camera_aeb_preserves_preexisting_hold_across_loss_of_standstill():
  rig = Rig()
  holding = rig.apply(speed=0., state='stopping', camera_brake=0, ticks=100)
  assert field(holding, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == HOLD_COUNTS
  # No standstill bit available to re-latch, and accel requests propulsion.
  # Even a camera request stronger than hold does not change the host command.
  aeb = rig.apply(1.5, speed=.3, state='stopping', camera_brake=180, ticks=60)
  assert_aeb_propulsion_inhibited(aeb)
  assert set(field(aeb, BRAKE, 'COMPUTER_BRAKE_HYBRID')) == {HOLD_COUNTS}
  assert set(field(aeb, BRAKE, 'BRAKE_PUMP_REQUEST_HYBRID')) == {1}
  cleared = rig.apply(1.5, speed=.3, state='stopping', camera_brake=0, ticks=20)
  assert set(field(cleared, BRAKE, 'COMPUTER_BRAKE_HYBRID')) == {HOLD_COUNTS}


def test_weaker_camera_aeb_does_not_release_or_cap_host_service_brake():
  rig, reference = Rig(), Rig()
  for car in (rig, reference):
    initial = car.apply(-1.7, camera_brake=0, ticks=100)
    assert field(initial, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] > 40
  # Identical stronger host request with/without camera AEB. Compare every
  # scheduled host brake frame; Panda forwarding is a separate safety test.
  aeb = rig.apply(-3.2, camera_brake=40, ticks=100)
  clear = reference.apply(-3.2, camera_brake=0, ticks=100)
  assert_aeb_propulsion_inhibited(aeb)
  counts = field(aeb, BRAKE, 'COMPUTER_BRAKE_HYBRID')
  assert counts == field(clear, BRAKE, 'COMPUTER_BRAKE_HYBRID')
  assert min(counts) > 40 and counts[-1] > counts[0]
  assert set(field(aeb, BRAKE, 'COMPUTER_BRAKE_REQUEST')) == {1}


def test_camera_aeb_cuts_both_positive_gas_paths_until_camera_clears():
  rig = Rig()
  before = rig.apply(1.5, camera_brake=0, ticks=60)
  assert field(before, HUD, 'PCM_GAS')[-1] > 0
  assert field(before, PEDAL, 'ENABLE')[-1] == 1 and before[PEDAL][-1][0][:4] != bytes(4)
  aeb = rig.apply(1.5, camera_brake=80, ticks=40)
  assert_aeb_propulsion_inhibited(aeb)
  assert set(field(aeb, BRAKE, 'COMPUTER_BRAKE_HYBRID')) == {0}  # no independent host brake request
  cleared = rig.apply(1.5, camera_brake=0, ticks=60)
  assert field(cleared, HUD, 'PCM_GAS')[-1] == field(before, HUD, 'PCM_GAS')[-1]
  assert field(cleared, PEDAL, 'ENABLE')[-1] == 1 and cleared[PEDAL][-1][0][:4] != bytes(4)


@pytest.mark.parametrize('mph,expected', [(0, 38), (3, 43), (6.5, 62), (22, 74), (27, 94), (45, 98)])
def test_active_hud_uses_stock_gas_curve_but_zero_pcm_speed(mph, expected):
  packets = Rig().apply(-.5, speed=mph * CV.MPH_TO_MS)
  assert field(packets, HUD, 'PCM_GAS') == [expected]
  assert field(packets, HUD, 'PCM_SPEED') == [0]
  assert 252 not in field(packets, HUD, 'CRUISE_SPEED')
  assert 8 not in field(packets, BRAKE, 'CRUISE_STATES')


@pytest.mark.parametrize('interceptor,expected', [(True, 255), (False, 252)])
def test_stopped_lead_dashboard_does_not_request_factory_hold_on_qualified_clarity(interceptor, expected):
  # Same real lead-speed HUD design on both cars: 252 is an intentional
  # positive control on the legacy path. Only qualified Clarity sanitizes it.
  rig = Rig(interceptor=interceptor, dashboard_speed=1)
  packets = rig.apply(speed=0., state='stopping', stopped=True, lead_speed=0., ticks=100)
  assert set(field(packets, HUD, 'HUD_LEAD')) == {2}
  assert set(field(packets, HUD, 'CRUISE_SPEED')) == {expected}
  if interceptor:
    assert 8 not in field(packets, BRAKE, 'CRUISE_STATES')
    assert field(packets, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == HOLD_COUNTS


@pytest.mark.parametrize('speed,brake_fraction,expected', [(10., 1. / 4.8, 38), (10., 1.7 / 4.8, 112),
                                                          (10., 2.55 / 4.8, 170), (10., 3.4 / 4.8, 320),
                                                          (1., .1, 25), (1.725, .1, 19), (10., .1, 14)])
@pytest.mark.parametrize('full_authority', [True, False])
def test_brake_map_and_low_speed_floor_reach_hybrid_field(speed, brake_fraction, expected, full_authority):
  # The Clarity map takes the ordinary (/4.8) split with either setting of the
  # generic full-authority option. Account for existing creep, 0.01 rising hysteresis
  # gap and the fixture's unit wind factor. Expected wire counts are independent
  # of the implementation of hybrid_brake_command; allow one truncation count.
  rig = Rig(full_authority=full_authority)
  creep = .15 * max(0., 1. - speed / 2.3)
  wind = (.001 + .001 * speed / 2.3) if speed < 2.3 else (.002 + .148 * (speed - 2.3) / 32.7)
  accel = 4.8 * (creep - brake_fraction - .01 - wind)
  packets = rig.apply(accel, speed=speed, ticks=100)
  assert rig.output.brake == pytest.approx(brake_fraction, abs=1.e-4)  # normalized, not hybrid counts / 256
  counts = field(packets, BRAKE, 'COMPUTER_BRAKE_HYBRID')
  assert counts[-1] == pytest.approx(expected, abs=1 if expected < 320 else 0)
  assert max(counts) <= 320
  assert max(field(packets, BRAKE, 'COMPUTER_BRAKE')) == 0
  assert field(packets, BRAKE, 'BRAKE_PUMP_REQUEST_HYBRID')[-1] == 1
  assert field(packets, BRAKE, 'COMPUTER_BRAKE_REQUEST')[-1] == 1


def test_hold_latches_only_after_standstill_and_releases_on_pid():
  rig = Rig()
  # Same weak request and wheel speed throughout. Only the stop bit and host
  # state change; a brief stop-bit dropout must not pump the brake on and off.
  rolling = rig.apply(speed=.3, state='stopping', ticks=140)
  assert field(rolling, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] < 90
  holding = rig.apply(speed=.3, stopped=True, state='stopping', ticks=160)
  level = field(holding, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1]
  assert level == HOLD_COUNTS
  flicker = rig.apply(speed=.3, stopped=False, state='stopping', ticks=50)
  assert set(field(flicker, BRAKE, 'COMPUTER_BRAKE_HYBRID')) == {level}
  # The hold floor alone may own brake even with a positive accel input. The
  # pedal wire must then be disabled, not just the ACC_HUD speed field zeroed.
  conflict = rig.apply(1.5, speed=.3, state='stopping', ticks=40)
  assert set(field(conflict, BRAKE, 'COMPUTER_BRAKE_HYBRID')) == {level}
  assert all(payload[:4] == bytes(4) and sig['ENABLE'] == 0 for payload, sig in conflict[PEDAL])
  released = rig.apply(1.5, speed=.3, state='pid', ticks=100)
  assert field(released, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == 0
  assert field(released, PEDAL, 'ENABLE')[-1] == 1


def test_disengage_clears_hold_before_next_rolling_stopping_request():
  rig = Rig()
  assert field(rig.apply(speed=0., stopped=True, state='stopping', ticks=160), BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == HOLD_COUNTS
  off = rig.apply(speed=0., stopped=True, state='off', enabled=False, long_active=False, ticks=20)
  assert field(off, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] == 0
  rolling = rig.apply(speed=.3, stopped=False, state='stopping', ticks=140)
  assert field(rolling, BRAKE, 'COMPUTER_BRAKE_HYBRID')[-1] < 90


def test_passive_reports_actual_pcm_cruise_state():
  rig = Rig()
  assert not rig.pcm_status(True)
  rig.ci.CP.passive = True  # card sets this after constructing the interface
  assert rig.pcm_status(True)
  assert field(rig.apply(enabled=False, long_active=False, state='off'), BRAKE, 'CRUISE_CANCEL_CMD') == [0] * 5
  assert not rig.pcm_status(False)


@pytest.mark.parametrize('target,attr,value', [
  pytest.param('sp', 'safetyParam', CLARITY_SAFETY & ~SafetySP.CLARITY_INTERCEPTOR_BRAKE, id='missing-clarity-bit'),
  pytest.param('sp', 'safetyParam', CLARITY_SAFETY & ~SafetySP.NIDEC_HYBRID, id='missing-hybrid-bit'),
  pytest.param('sp', 'safetyParam', CLARITY_SAFETY & ~SafetySP.GAS_INTERCEPTOR, id='missing-interceptor-bit'),
  pytest.param('sp', 'safetyParam', CLARITY_SAFETY | SafetySP.GAS_INTERCEPTOR_THRESHOLD_512, id='extra-threshold-bit'),
  pytest.param('sp', 'safetyParam', CLARITY_SAFETY | SafetySP.STOCK_LONGITUDINAL, id='extra-stock-bit'),
  pytest.param('standard', 'safetyParam', HondaSafetyFlags.ALT_BRAKE.value, id='nonzero-standard-param'),
  pytest.param('standard', 'safetyModel', structs.CarParams.SafetyModel.hondaBosch, id='wrong-safety-model'),
  pytest.param('cp', 'dashcamOnly', True, id='dashcam'),
])
def test_mismatched_safety_contract_cannot_enable_clarity_state_or_wire_map(target, attr, value):
  def alter(cp, sp):
    # Begin with genuine negotiated flags, then break exactly one condition
    # before CarState and CarController are constructed.
    assert sp.safetyParam == CLARITY_SAFETY
    setattr({'cp': cp, 'sp': sp, 'standard': cp.safetyConfigs[0]}[target], attr, value)

  rig = Rig(alter_params=alter)
  assert rig.pcm_status(True)
  packets = rig.apply(-4., ticks=150)
  # Do not require actuation for malformed configurations. If the controller
  # emits legacy frames, they must not carry the Clarity map or HUD allowance.
  if BRAKE in packets:
    assert max(field(packets, BRAKE, 'COMPUTER_BRAKE_HYBRID')) <= 255
  if HUD in packets:
    assert set(field(packets, HUD, 'PCM_GAS')) == {0}


@pytest.mark.parametrize('car,hybrid,interceptor', [(CAR.HONDA_CIVIC, False, True), (CAR.HONDA_CIVIC, True, True),
                                                   (CAR.HONDA_CLARITY, True, False), (CAR.HONDA_CLARITY, False, True)])
def test_unqualified_nidec_retains_visibility_cancel_and_brake_limit(car, hybrid, interceptor):
  rig = Rig(car, hybrid=hybrid, interceptor=interceptor)
  assert rig.pcm_status(True)
  packets = rig.apply(-4., speed=10., cancel=True, ticks=150)
  assert set(field(packets, BRAKE, 'CRUISE_CANCEL_CMD')) == {1}
  used, unused = ('COMPUTER_BRAKE_HYBRID', 'COMPUTER_BRAKE') if hybrid else ('COMPUTER_BRAKE', 'COMPUTER_BRAKE_HYBRID')
  assert 0 < max(field(packets, BRAKE, used)) <= 255
  assert max(field(packets, BRAKE, unused)) == 0
  assert field(packets, HUD, 'PCM_GAS')[-1] == 0
  assert (PEDAL in packets) == interceptor


def test_normal_civic_still_uses_pcm_speed_not_clarity_coasting_hud():
  rig = Rig(CAR.HONDA_CIVIC, hybrid=False, interceptor=False)
  assert rig.pcm_status(True)
  packets = rig.apply(.5, speed=20., reference_speed=20., ticks=160)
  assert field(packets, HUD, 'PCM_SPEED')[-1] > 20. * CV.MS_TO_KPH
  assert field(packets, HUD, 'PCM_GAS')[-1] > 0
  assert max(field(packets, BRAKE, 'COMPUTER_BRAKE')) == 0
  assert PEDAL not in packets


def test_forced_stock_keeps_pcm_visible_and_does_not_author_longitudinal_frames():
  rig = Rig(stock=True)
  assert not rig.ci.CP.openpilotLongitudinalControl
  assert not rig.ci.CP_SP.safetyParam & SafetySP.CLARITY_INTERCEPTOR_BRAKE
  assert rig.pcm_status(True)
  assert not rig.apply(enabled=True, long_active=False, stopped=True, state='off')
