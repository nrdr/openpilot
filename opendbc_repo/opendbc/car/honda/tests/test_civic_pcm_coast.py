"""Free-cruise release blend: scope, continuity and actual controller arbitration."""
import math

import pytest

from opendbc.car import structs
from opendbc.car.honda.civic_pcm import coast_blend, REFERENCE_MAX_AGE_NS
from opendbc.car.honda.tests.test_civic_pcm import interface, control
from opendbc.car.honda.tests.test_civic_pcm_speed_control import START, reference


@pytest.mark.parametrize('speed', [0., 5., 5.01, 9., 13., 20., 30., 40., 50., float('nan')])
@pytest.mark.parametrize('demand', [-3., -.5, -.3, -.15, 0., .1, 2.])
def test_credit_bounded_and_negative_request_never_extended(speed, demand):
  credit, fraction = coast_blend(demand, -.2, speed, 30., True)
  assert 0. <= credit <= .3 and 0. <= fraction <= 1.
  if demand <= -.5 or not 5. < speed < 50.:
    assert (credit, fraction) == (0., 1.)
  assert coast_blend(demand, -.2, speed, 30., False) == (0., 1.)


@pytest.mark.parametrize('argument', range(4))
@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_input_no_credit(argument, bad):
  inputs = [.05, -.15, 20., 20.]
  inputs[argument] = bad
  assert coast_blend(*inputs, True) == (0., 1.)


def test_credit_tapers_with_overspeed_and_demand():
  speeds = [20. + x / 1000 for x in range(751)]
  credit = [coast_blend(.05, -.15, v, 20., True)[0] for v in speeds]
  # Up to +.25 the drag curve grows slightly; thereafter the overspeed taper dominates.
  assert all(a >= b for a, b in zip(credit[250:], credit[251:]))
  assert credit[-1] == 0.
  demand = [coast_blend(-.15 - x / 1000, -.15, 20., 20., True)[0] for x in range(351)]
  assert all(a >= b for a, b in zip(demand, demand[1:]))
  assert demand[-1] == 0.
  fractions = [coast_blend(.05, -x / 1000, 20., 20., True)[1] for x in range(501)]
  assert all(a >= b for a, b in zip(fractions, fractions[1:]))
  assert max(abs(a-b) for a, b in zip(fractions, fractions[1:])) < .005
  # Credit disappearing must not restore acceleration at the overspeed edge,
  # including a negative wheel demand too small to trigger brake hysteresis.
  for v in (20.749, 20.75, 20.751, 21.):
    assert coast_blend(.1, -.12, v, 20., True)[1] == 0.


def run_case(eligible, reason='none', request=.05, ticks=100):
  ci, _ = interface()
  ci.CS.out.canValid = True
  ci.CS.out.vEgo = 20.
  for tick in range(ticks):
    now = START + tick * 10_000_000
    cc = control(request)
    cc.orientationNED = [0., math.asin(-.15 / 9.81), 0.]
    sp = reference(20., now)
    sp.civicPcmCoastEligible, sp.civicPcmCruiseSpeed = eligible, 20.
    if reason in ('gasPressed', 'brakePressed', 'stockAeb', 'stockFcw', 'accFaulted'):
      setattr(ci.CS.out, reason, True)
    elif reason == 'invalid':
      ci.CS.out.canValid = False
    elif reason in ('leadOne', 'leadTwo'):
      getattr(sp, reason).status = True
    elif reason == 'hudLead':
      cc.hudControl.leadVisible = True
    elif reason == 'cancel':
      cc.cruiseControl.cancel = True
    elif reason == 'dm':
      cc.driverMonitoringEscalation = True
    elif reason == 'stopping':
      cc.actuators.longControlState = structs.CarControl.Actuators.LongControlState.stopping
    elif reason == 'off':
      cc.enabled = cc.longActive = False
    elif reason == 'stale':
      sp.civicPcmReferenceMonoTime = now - REFERENCE_MAX_AGE_NS - 1
    elif reason == 'future':
      sp.civicPcmReferenceMonoTime = now + 1
    elif reason == 'missingPitch':
      cc.orientationNED = []
    ci.apply(cc.as_reader(), sp, now)
  return ci


def test_small_grade_crossing_coasts_instead_of_applying_friction_and_zeroing_pcm():
  baseline, candidate = run_case(False), run_case(True)
  assert baseline.CC.apply_brake_last > 0
  assert baseline.CC.pcm_speed_sent == baseline.CC.pcm_gas_sent == 0.
  assert candidate.CC.apply_brake_last == 0
  assert 20. <= candidate.CC.pcm_speed_sent < 20. + 4. * .05
  assert candidate.CC.nidec_pid.i == 0.


@pytest.mark.parametrize('reason', ['gasPressed', 'brakePressed', 'stockAeb', 'stockFcw', 'accFaulted',
                                  'invalid', 'leadOne', 'leadTwo', 'hudLead', 'cancel', 'dm',
                                  'stopping', 'off', 'stale', 'future', 'missingPitch'])
def test_veto_preserves_existing_controller_output(reason):
  baseline, candidate = run_case(False, reason), run_case(True, reason)
  for name in ('apply_brake_last', 'pcm_speed_sent', 'pcm_gas_sent', 'brake_pid_factor'):
    assert getattr(candidate.CC, name) == pytest.approx(getattr(baseline.CC, name))


@pytest.mark.parametrize('demand', [-.5, -1., -3.])
def test_material_braking_unchanged(demand):
  baseline, candidate = run_case(False, request=demand), run_case(True, request=demand)
  assert candidate.CC.apply_brake_last == baseline.CC.apply_brake_last > 0
  assert candidate.CC.pcm_speed_sent == candidate.CC.pcm_gas_sent == 0.


def test_lead_arrival_has_no_coast_hold_timer():
  ci = run_case(True)
  assert ci.CC.apply_brake_last == 0
  now = START + 1_000_000_000
  cc = control(-.8)
  cc.orientationNED = [0., math.asin(-.15 / 9.81), 0.]
  sp = reference(19.9, now)
  sp.civicPcmCoastEligible, sp.civicPcmCruiseSpeed = True, 20.
  sp.leadOne.status = True  # Even a stale producer permission cannot override this.
  _, packets = ci.apply(cc.as_reader(), sp, now)
  assert ci.CC.apply_brake_last > 0
  assert all(payload[:3] == bytes(3) for address, payload, _ in packets if address == 0x30C)


def test_grade_blend_does_not_train_speed_gain_on_modified_feedforward():
  ci, cfg = interface(learning=True)
  ci.CS.out.canValid = True
  gains = ci.CC.speed_factors.copy()
  for tick in range(500):
    now = START + tick * 10_000_000
    cc = control(.3)
    cc.orientationNED = [0., math.asin(-.4 / 9.81), 0.]
    sp = reference(20., now)
    sp.civicPcmCoastEligible, sp.civicPcmCruiseSpeed = True, 20.
    ci.apply(cc.as_reader(), sp, now)
  assert ci.CC.speed_factors == gains
