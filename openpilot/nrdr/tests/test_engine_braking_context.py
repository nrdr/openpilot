from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.longitudinal.engine_braking import engine_brake_context
from opendbc.car.honda.engine_braking import CONTEXT_MAX_AGE_NS, fresh_context


SERVICES = ('carState', 'selfdriveState', 'radarState', 'longitudinalPlan', 'longitudinalPlanSP')


class Messages(dict):
  def __init__(self):
    super().__init__(carState=NS(vCruise=72, vEgo=21., gasPressed=False, brakePressed=False, stockAeb=False),
                     selfdriveState=NS(experimentalMode=False), radarState=NS(leadOne=NS(present=False), leadTwo=NS(present=False)),
                     longitudinalPlan=NS(shouldStop=False, aTarget=0., longitudinalPlanSource='cruise'),
                     longitudinalPlanSP=NS(vTarget=20., longitudinalPlanSource='cruise'))
    self.logMonoTime = dict.fromkeys(self, 1_000_000_000)
    self.valid = True

  def all_checks(self, services):
    return self.valid and all(s in self for s in services)


def context(sm=None, enabled=True, allowance=5, car=CAR.HONDA_CIVIC, interceptor=False, stock=False):
  cp = NS(carFingerprint=car, openpilotLongitudinalControl=True, flags=HondaFlags.NIDEC)
  sp = NS(enableGasInterceptor=interceptor, flags=HondaFlagsSP.STOCK_LONGITUDINAL if stock else 0)
  return engine_brake_context(cp, sp, sm or Messages(), enabled, allowance)


def test_only_free_cruise_inside_allowance():
  sm = Messages()
  assert context(sm) == (True, True, 1_000_000_000)
  sm['carState'].vEgo = 19
  assert context(sm) == (True, False, 1_000_000_000)
  sm['carState'].vEgo = 23
  assert context(sm) == (False, False, 0)


@pytest.mark.parametrize('service,field,value', [('selfdriveState', 'experimentalMode', True),
  ('longitudinalPlan', 'shouldStop', True), ('longitudinalPlan', 'longitudinalPlanSource', 'lead0'),
  ('longitudinalPlanSP', 'longitudinalPlanSource', 'sccVision'), ('longitudinalPlanSP', 'vTarget', 19),
  ('carState', 'gasPressed', True), ('carState', 'brakePressed', True), ('carState', 'stockAeb', True),
  ('carState', 'vCruise', 0), ('carState', 'vCruise', 255), ('carState', 'vEgo', float('nan'))])
def test_safety_and_target_exclusions(service, field, value):
  sm = Messages()
  setattr(sm[service], field, value)
  assert context(sm) == (False, False, 0)


@pytest.mark.parametrize('which', ['leadOne', 'leadTwo'])
def test_any_lead_blocks_coast_fade(which):
  sm = Messages()
  getattr(sm['radarState'], which).present = True
  assert context(sm) == (False, False, 0)


@pytest.mark.parametrize('kwargs', [{'enabled': False}, {'allowance': 0}, {'allowance': float('nan')},
  {'car': CAR.HONDA_CLARITY}, {'car': CAR.HONDA_CIVIC_BOSCH}, {'interceptor': True}, {'stock': True}])
def test_off_and_other_platforms_unchanged(kwargs):
  assert context(**kwargs) == (False, False, 0)


def test_invalid_messages_remove_permission():
  sm = Messages()
  sm.valid = False
  assert context(sm) == (False, False, 0)


@pytest.mark.parametrize('service', SERVICES)
@pytest.mark.parametrize('age,expected', [(CONTEXT_MAX_AGE_NS, True), (CONTEXT_MAX_AGE_NS + 1, False)])
def test_oldest_dependency_controls_receiver_freshness(service, age, expected):
  sm = Messages()
  now = 2_000_000_000
  sm.logMonoTime = dict.fromkeys(SERVICES, now)
  sm.logMonoTime[service] = now - age
  allowed, request, stamp = context(sm)
  assert (allowed, request, stamp) == (True, True, now - age)
  wire = NS(pcmEngineBrakeAllowed=allowed, pcmEngineBrakeRequest=request, pcmEngineBrakeMonoTime=stamp)
  assert fresh_context(wire, now) is expected


@pytest.mark.parametrize('service', SERVICES)
def test_missing_dependency_timestamp_cannot_authorize_fade(service):
  sm = Messages()
  sm.logMonoTime[service] = 0
  allowed, request, stamp = context(sm)
  assert stamp == 0
  assert not fresh_context(NS(pcmEngineBrakeAllowed=allowed, pcmEngineBrakeMonoTime=stamp), 1_000_000_000)


@pytest.mark.parametrize('source', ['lead0', 'lead1', 'lead2', 'e2e'])
def test_real_host_plan_source_enum_excludes_noncruise(source):
  from openpilot.cereal import log
  sm = Messages()
  sm['longitudinalPlan'] = log.LongitudinalPlan.new_message(longitudinalPlanSource=source, aTarget=0., shouldStop=False).as_reader()
  assert context(sm) == (False, False, 0)


@pytest.mark.parametrize('source', ['sccVision', 'sccMap', 'speedLimitAssist'])
def test_real_sp_plan_source_enum_excludes_reduced_targets(source):
  from openpilot.cereal import custom
  sm = Messages()
  sm['longitudinalPlanSP'] = custom.LongitudinalPlanSP.new_message(longitudinalPlanSource=source, vTarget=20.).as_reader()
  assert context(sm) == (False, False, 0)


def test_real_schema_round_trip_preserves_permission_during_recovery():
  from openpilot.cereal import custom, log
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  sm = Messages()
  sm['carState'].vEgo = 19.
  sm['longitudinalPlan'] = log.LongitudinalPlan.new_message(longitudinalPlanSource='cruise', aTarget=0., shouldStop=False).as_reader()
  sm['longitudinalPlanSP'] = custom.LongitudinalPlanSP.new_message(longitudinalPlanSource='cruise', vTarget=20.).as_reader()
  allowed, request, stamp = context(sm)
  assert (allowed, request, stamp) == (True, False, 1_000_000_000)
  message = custom.CarControlSP.new_message(pcmEngineBrakeAllowed=allowed, pcmEngineBrakeRequest=request, pcmEngineBrakeMonoTime=stamp)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    native = convert_carControlSP(reader)
  assert native.pcmEngineBrakeAllowed
  assert not native.pcmEngineBrakeRequest
  assert native.pcmEngineBrakeMonoTime == stamp
  assert fresh_context(native, stamp + CONTEXT_MAX_AGE_NS)


def test_absent_metadata_round_trips_to_disabled():
  from openpilot.cereal import custom
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  message = custom.CarControlSP.new_message()
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    native = convert_carControlSP(reader)
  assert not native.pcmEngineBrakeAllowed
  assert not native.pcmEngineBrakeRequest
  assert native.pcmEngineBrakeMonoTime == 0
  assert not fresh_context(native, 1_000_000_000)
