"""Pure coast admission and real wire-schema tests; no Params or vehicle I/O."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.cereal import custom, log
from openpilot.nrdr.features.longitudinal.cruise_coast import DENIED, SERVICES, State, TARGET_EPSILON_MS, cruise_coast_context


ROOT = Path(__file__).resolve().parents[3]


class Messages(dict):
  def __init__(self):
    super().__init__(carState=NS(vCruise=72., vEgo=21., gasPressed=False, brakePressed=False, stockAeb=False),
                     selfdriveState=NS(experimentalMode=False, state=State.enabled),
                     radarState=NS(leadOne=NS(present=False), leadTwo=NS(present=False)),
                     longitudinalPlan=NS(shouldStop=False, aTarget=0., allowThrottle=True, longitudinalPlanSource='cruise', speeds=[]),
                     longitudinalPlanSP=NS(vTarget=20., longitudinalPlanSource='cruise'),
                     driverMonitoringState=NS(noResponseForceDecel=False))
    self.logMonoTime = dict.fromkeys(self, 1_000_000_000)
    self.failed_checks = {check: set() for check in ('valid', 'alive', 'freq')}
    self.checked = []

  def all_checks(self, services):
    self.checked.append(tuple(services))
    return all(name in self and all(name not in failed for failed in self.failed_checks.values()) for name in services)


def vehicle(car=CAR.HONDA_CIVIC, interceptor=False, stock=False, openlong=True, bosch=False):
  cp = NS(carFingerprint=car, openpilotLongitudinalControl=openlong, flags=HondaFlags.BOSCH if bosch else HondaFlags.NIDEC)
  sp = NS(enableGasInterceptor=interceptor, flags=HondaFlagsSP.STOCK_LONGITUDINAL if stock else 0)
  return cp, sp


def context(sm=None, allowance=5., **kwargs):
  return cruise_coast_context(*vehicle(**kwargs), sm if sm is not None else Messages(), allowance)


@pytest.mark.parametrize('speed', [5.0001, 19., 20., 21., 20. + 5. * .44704])
def test_permission_covers_recovery_setpoint_and_full_allowance(speed):
  sm = Messages()
  sm['carState'].vEgo = speed
  assert context(sm) == (True, 20., 22.2352, 1_000_000_000)
  assert sm.checked == [SERVICES]
  assert 'controlsState' not in SERVICES


@pytest.mark.parametrize('allowance', [.001, 1., 5., 10.])
def test_upper_bound_is_exact_and_never_tolerates_overshoot_beyond_allowance(allowance):
  sm = Messages()
  upper = 20. + allowance * .44704
  sm['carState'].vEgo = upper
  assert context(sm, allowance)[2] == upper
  sm['carState'].vEgo = math.nextafter(upper, math.inf)
  assert context(sm, allowance) == DENIED


@pytest.mark.parametrize('car', list(CAR))
def test_exact_existing_civic_eligibility(car):
  assert context(car=car)[0] == (car == CAR.HONDA_CIVIC)


@pytest.mark.parametrize('kwargs', [{'car': 'UNKNOWN'}, {'interceptor': True}, {'stock': True}, {'openlong': False}, {'bosch': True}])
def test_ineligible_configurations(kwargs):
  assert context(**kwargs) == DENIED


@pytest.mark.parametrize('service', SERVICES)
@pytest.mark.parametrize('check', ['valid', 'alive', 'freq'])
def test_each_required_service_must_pass_all_checks(service, check):
  sm = Messages()
  sm.failed_checks[check].add(service)
  assert context(sm) == DENIED
  assert sm.checked == [SERVICES]


@pytest.mark.parametrize('service', SERVICES)
def test_each_missing_service_denies_before_access(service):
  sm = Messages()
  del sm[service]
  assert context(sm) == DENIED


@pytest.mark.parametrize('service,field,value', [
  ('selfdriveState', 'experimentalMode', True), ('longitudinalPlan', 'shouldStop', True),
  ('carState', 'gasPressed', True), ('carState', 'brakePressed', True), ('carState', 'stockAeb', True),
  ('carState', 'vEgo', 5.), ('carState', 'vEgo', 0.), ('carState', 'vEgo', -1.),
  ('carState', 'vCruise', 18.), ('carState', 'vCruise', 252.),
])
def test_operating_and_override_exclusions(service, field, value):
  sm = Messages()
  setattr(sm[service], field, value)
  assert context(sm) == DENIED


@pytest.mark.parametrize('lead', ['leadOne', 'leadTwo'])
def test_either_lead_denies_permission(lead):
  sm = Messages()
  getattr(sm['radarState'], lead).present = True
  assert context(sm) == DENIED


@pytest.mark.parametrize('accel', [-1e-9, -.01, -4.])
def test_negative_acceleration_denies_even_with_throttle_allowed(accel):
  sm = Messages()
  sm['longitudinalPlan'].aTarget = accel
  assert sm['longitudinalPlan'].allowThrottle
  assert context(sm) == DENIED


@pytest.mark.parametrize('accel', [0., .1, 2.])
def test_throttle_false_denies_even_with_nonnegative_acceleration(accel):
  sm = Messages()
  sm['longitudinalPlan'].aTarget = accel
  sm['longitudinalPlan'].allowThrottle = False
  assert context(sm) == DENIED


@pytest.mark.parametrize('allowance', [0., -1., 10.0001, 100., math.nan, math.inf, -math.inf])
def test_invalid_allowance_does_not_become_valid_by_clamping(allowance):
  assert context(allowance=allowance) == DENIED


@pytest.mark.parametrize('service,field', [('carState', 'vCruise'), ('carState', 'vEgo'),
  ('longitudinalPlan', 'aTarget'), ('longitudinalPlanSP', 'vTarget')])
@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_nonfinite_inputs_deny(service, field, value):
  sm = Messages()
  setattr(sm[service], field, value)
  assert context(sm) == DENIED


@pytest.mark.parametrize('offset,allowed', [(0., True), (1., True), (-TARGET_EPSILON_MS / 2, True),
                                          (-2 * TARGET_EPSILON_MS, False), (-.01, False), (-1., False)])
def test_selected_target_only_has_float_conversion_tolerance(offset, allowed):
  sm = Messages()
  sm['longitudinalPlanSP'].vTarget = 20. + offset
  assert context(sm)[0] is allowed


@pytest.mark.parametrize('source', ['lead0', 'lead1', 'lead2', 'e2e'])
def test_real_host_source_enum_excludes_noncruise(source):
  sm = Messages()
  sm['longitudinalPlan'] = log.LongitudinalPlan.new_message(longitudinalPlanSource=source, allowThrottle=True).as_reader()
  assert context(sm) == DENIED


@pytest.mark.parametrize('source', ['sccVision', 'sccMap', 'speedLimitAssist'])
def test_real_selected_source_enum_excludes_noncruise(source):
  sm = Messages()
  sm['longitudinalPlanSP'] = custom.LongitudinalPlanSP.new_message(longitudinalPlanSource=source, vTarget=20.).as_reader()
  assert context(sm) == DENIED


@pytest.mark.parametrize('service', SERVICES)
@pytest.mark.parametrize('age', [1, 300_000_000, 300_000_001, 999_999_999])
def test_oldest_dependency_timestamp_is_forwarded_for_receiver_freshness_check(service, age):
  sm = Messages()
  sm.logMonoTime[service] -= age
  assert context(sm)[3] == 1_000_000_000 - age


@pytest.mark.parametrize('service', SERVICES)
@pytest.mark.parametrize('stamp', [None, 0, -1])
def test_missing_or_nonpositive_timestamp_denies(service, stamp):
  sm = Messages()
  if stamp is None:
    del sm.logMonoTime[service]
  else:
    sm.logMonoTime[service] = stamp
  assert context(sm) == DENIED


@pytest.mark.parametrize('state', ['disabled', 'preEnabled', 'enabled', 'softDisabling', 'overriding'])
@pytest.mark.parametrize('dm_decel', [False, True])
def test_force_decel_matches_native_controls_expression_exactly(state, dm_decel):
  sm = Messages()
  sm['selfdriveState'] = log.SelfdriveState.new_message(state=state, experimentalMode=False).as_reader()
  sm['driverMonitoringState'] = log.DriverMonitoringState.new_message(noResponseForceDecel=dm_decel).as_reader()
  tree = ast.parse((ROOT / 'openpilot/selfdrive/controls/controlsd.py').read_text())
  assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign) and
                    any(isinstance(target, ast.Attribute) and target.attr == 'forceDecel' for target in node.targets))
  native_force_decel = eval(compile(ast.Expression(assignment.value), 'native-force-decel', 'eval'), {'self': NS(sm=sm), 'State': State})
  assert context(sm)[0] is not native_force_decel
  coast = ast.parse((ROOT / 'openpilot/nrdr/features/longitudinal/cruise_coast.py').read_text())
  coast_assignment = next(node for node in ast.walk(coast) if isinstance(node, ast.Assign) and
                          any(isinstance(target, ast.Name) and target.id == 'force_decel' for target in node.targets))
  assert ast.unparse(coast_assignment.value) == ast.unparse(assignment.value).replace('self.sm', 'sm')


@pytest.mark.parametrize('enabled', [False, True])
@pytest.mark.parametrize('speed', [19., 20., 21.])
def test_real_schema_round_trip_preserves_independent_permission_and_raw_choice(enabled, speed):
  from opendbc.car.structs import car
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  sm = Messages()
  sm['carState'] = car.CarState.new_message(vCruise=72., vEgo=speed).as_reader()
  sm['selfdriveState'] = log.SelfdriveState.new_message(state='enabled').as_reader()
  sm['radarState'] = log.RadarState.new_message().as_reader()
  sm['longitudinalPlan'] = log.LongitudinalPlan.new_message(longitudinalPlanSource='cruise', aTarget=0., allowThrottle=True).as_reader()
  sm['longitudinalPlanSP'] = custom.LongitudinalPlanSP.new_message(longitudinalPlanSource='cruise', vTarget=20.).as_reader()
  sm['driverMonitoringState'] = log.DriverMonitoringState.new_message(noResponseForceDecel=False).as_reader()
  allowed, set_speed, max_speed, stamp = context(sm)
  assert allowed
  message = custom.CarControlSP.new_message(pcmCruiseCoastAllowed=allowed, pcmCruiseCoastSetSpeed=set_speed,
                                            pcmCruiseCoastMaxSpeed=max_speed, pcmCruiseCoastMonoTime=stamp,
                                            pcmEngineBrakeEnabled=enabled, pcmCruiseCoastVersion=1)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    native = convert_carControlSP(reader)
  assert native.pcmCruiseCoastAllowed
  assert native.pcmCruiseCoastSetSpeed == pytest.approx(20.)
  assert native.pcmCruiseCoastMaxSpeed == pytest.approx(22.2352)
  assert native.pcmCruiseCoastMonoTime == 1_000_000_000
  assert native.pcmEngineBrakeEnabled is enabled
  assert native.pcmCruiseCoastVersion == 1
  assert not native.pcmEngineBrakeAllowed  # Legacy fields do not convey the choice.


def test_absent_wire_metadata_remains_version_zero_and_disabled():
  message = custom.CarControlSP.new_message()
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    assert not reader.pcmCruiseCoastAllowed and not reader.pcmEngineBrakeEnabled
    assert reader.pcmCruiseCoastSetSpeed == reader.pcmCruiseCoastMaxSpeed == 0.
    assert reader.pcmCruiseCoastMonoTime == reader.pcmCruiseCoastVersion == 0


def test_wire_field_ordinals_and_types_are_append_only():
  expected = {
    'pcmCruiseCoastAllowed': (11, 'bool'), 'pcmCruiseCoastSetSpeed': (12, 'float32'),
    'pcmCruiseCoastMaxSpeed': (13, 'float32'), 'pcmCruiseCoastMonoTime': (14, 'uint64'),
    'pcmEngineBrakeEnabled': (15, 'bool'), 'pcmCruiseCoastVersion': (16, 'uint8'),
  }
  for name, (ordinal, kind) in expected.items():
    field = custom.CarControlSP.schema.fields[name].proto
    assert field.ordinal.explicit == ordinal
    assert field.slot.type.which() == kind


@pytest.mark.parametrize('service', SERVICES)
@pytest.mark.parametrize('age,permitted', [(300_000_000, True), (300_000_001, False)])
def test_real_wire_oldest_timestamp_controls_receiver_freshness(service, age, permitted):
  from opendbc.car.honda.cruise_coast import coast_permission
  from opendbc.car.structs import car
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  now = 2_000_000_000
  sm = Messages()
  sm.logMonoTime = dict.fromkeys(SERVICES, now)
  sm.logMonoTime[service] = now - age
  allowed, set_speed, max_speed, stamp = context(sm)
  message = custom.CarControlSP.new_message(pcmCruiseCoastAllowed=allowed, pcmCruiseCoastSetSpeed=set_speed,
                                            pcmCruiseCoastMaxSpeed=max_speed, pcmCruiseCoastMonoTime=stamp,
                                            pcmEngineBrakeEnabled=False, pcmCruiseCoastVersion=1)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    native = convert_carControlSP(reader)
  cc = car.CarControl.new_message(enabled=True, longActive=True,
                                  actuators={'accel': 0., 'longControlState': 'pid'}).as_reader()
  cs = NS(out=car.CarState.new_message(vCruise=72., vEgo=21., canValid=True).as_reader(), stock_brake={})
  assert coast_permission(*vehicle(), cc, native, cs, now, launching=False) is permitted
  native.pcmCruiseCoastMonoTime = now + 1
  assert not coast_permission(*vehicle(), cc, native, cs, now, launching=False)
