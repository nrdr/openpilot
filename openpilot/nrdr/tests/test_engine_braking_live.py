"""Exercise the real controlsd producer, legacy fade and v1 wire contract."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.engine_braking import EngineBrakeFade, fresh_context
from opendbc.car.honda.values import CAR, HondaFlags
from openpilot.cereal import custom, log
from openpilot.nrdr.features.longitudinal.cruise_coast import cruise_coast_context
from openpilot.nrdr.features.longitudinal.engine_braking import EngineBrakeSettingsReporter, engine_brake_context
from opendbc.car.honda.civic_pcm import uses_civic_pcm
from openpilot.nrdr.params import read_bool, read_float
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LIVE_LATERAL_KEYS, LiveParams, REFRESH_PERIOD
from openpilot.nrdr.tests.test_cruise_coast_context import Messages


def control_method():
  path = Path(__file__).resolve().parents[2] / 'sunnypilot/selfdrive/controls/controlsd_ext.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ControlsExt')
  init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == '__init__')
  assert 'NrdrExperimentalEngineBraking' not in ast.unparse(init), 'Do not cache this preference at startup'
  assert 'controlsState' not in ast.unparse(init), 'Do not subscribe to this process\'s controlsState output'
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'state_control_ext')
  method.returns = None
  for arg in method.args.args:
    arg.annotation = None
  tree.body = [method]
  env = {
    'custom': custom, 'pcm_reference': lambda *_: (False, 0., 0), 'engine_brake_context': engine_brake_context,
    'cruise_coast_context': cruise_coast_context,
    'read_bool': read_bool, 'read_float': read_float, 'uses_civic_pcm': uses_civic_pcm,
  }
  exec(compile(tree, str(path), 'exec'), env)
  return env['state_control_ext']


def messages():
  sm = Messages()
  sm['selfdriveStateSP'] = NS(mads=NS(state=0, enabled=False, active=False, available=False),
                            intelligentCruiseButtonManagement=NS(state=0, sendButton=0, vTarget=0))
  return sm


def controls(live):
  return NS(CP=NS(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=HondaFlags.NIDEC),
            CP_SP=NS(enableGasInterceptor=False, flags=0), nrdr_live_params=live, get_lead_data=lambda *_: None,
            engine_brake_settings_reporter=EngineBrakeSettingsReporter())


def test_same_controls_instance_consumes_live_choice_and_resets_receiver_fade():
  key = 'NrdrExperimentalEngineBraking'
  assert key not in LIVE_LATERAL_KEYS
  assert REFRESH_PERIOD == .5
  group = next(group for group in CONTROL_GROUPS if key in group.keys)
  assert 'NrdrCruiseOverspeedAllowance' in group.keys
  values = {key: False, 'NrdrCruiseOverspeedAllowance': 5}
  storage_reads = []

  def get(name):
    storage_reads.append(name)
    return values.get(name)

  live = LiveParams(CONTROL_GROUPS, params=NS(get=get), start_worker=False)

  class CountingSnapshot:
    count = 0
    reports = []

    def record_applied_settings(self, *args, **kwargs):
      self.reports.append((args, kwargs))

    @property
    def snapshot(self):
      self.count += 1
      return live.snapshot

  method = control_method()
  counted = CountingSnapshot()
  instance = controls(counted)
  sm = messages()
  fade = EngineBrakeFade()

  def frame(index):
    now = 1_000_000_000 + index * 20_000_000
    sm.logMonoTime = dict.fromkeys(sm, now)
    reads_before, count_before = len(storage_reads), counted.count
    wire = method(instance, sm)
    assert len(storage_reads) == reads_before, 'No storage polling from the actuation loop'
    assert counted.count == count_before + 1, 'Enable flag and allowance must share one snapshot'
    assert wire.pcmCruiseCoastVersion == 1
    assert wire.pcmEngineBrakeEnabled is values[key]
    output = fade.apply(25., 100, now_nanos=now, permitted=fresh_context(wire, now), request=wire.pcmEngineBrakeRequest)
    return wire, output

  def save(value):
    values[key] = value
    # One normal worker polling cycle; no controlsd restart or disengagement.
    for _ in CONTROL_GROUPS:
      live.poll_once()

  wire, output = frame(0)
  assert not wire.pcmEngineBrakeAllowed and output == (25., 100)
  assert wire.pcmCruiseCoastAllowed  # Engine Off still authorizes throttle-only coast.
  assert wire.pcmCruiseCoastSetSpeed == 20.
  assert wire.pcmCruiseCoastMaxSpeed == pytest.approx(22.2352)
  save(True)
  wire, output = frame(1)
  assert wire.pcmEngineBrakeAllowed and wire.pcmEngineBrakeRequest and output == (25., 100)
  assert wire.pcmCruiseCoastAllowed
  for index in range(2, 102):
    wire, output = frame(index)
  assert .6 < fade.weight < .7 and output[0] < 10 and output[1] < 40
  save(False)
  wire, output = frame(102)
  assert not wire.pcmEngineBrakeAllowed and not wire.pcmEngineBrakeRequest and wire.pcmEngineBrakeMonoTime == 0
  assert wire.pcmCruiseCoastAllowed  # Switching Off is not a denial of v1 coast permission.
  assert output == (25., 100) and fade.weight == 0 and fade.last_time is None
  save(True)
  _, output = frame(103)
  assert output == (25., 100) and fade.weight == 0  # No stale weight on re-enable.
  _, output = frame(104)
  assert 0 < fade.weight < .01 and output[0] > 24
  sm['radarState'].leadOne.present = True
  wire, output = frame(105)
  assert not wire.pcmEngineBrakeAllowed and output == (25., 100) and fade.weight == 0
  assert not wire.pcmCruiseCoastAllowed and wire.pcmCruiseCoastMonoTime == 0
  assert [report[1]['configured_enabled'] for report in counted.reports] == [False, True, False, True]
  assert all(report[1]['allowance_mph'] == 5 for report in counted.reports)


@pytest.mark.parametrize('engine_enabled', [False, True])
@pytest.mark.parametrize('case', ['negative_accel', 'throttle_false', 'driver_force_decel', 'soft_disabling',
                                'driver_stale', 'driver_missing_stamp', 'allowance_zero', 'allowance_above_ten', 'lead', 'ineligible'])
def test_denied_v1_round_trip_preserves_raw_choice_and_never_becomes_legacy_version(engine_enabled, case):
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  values = {'NrdrExperimentalEngineBraking': engine_enabled, 'NrdrCruiseOverspeedAllowance': 5}
  sm = messages()
  if case == 'negative_accel':
    sm['longitudinalPlan'].aTarget = -.001
  elif case == 'throttle_false':
    sm['longitudinalPlan'].allowThrottle = False
  elif case == 'driver_force_decel':
    sm['driverMonitoringState'].noResponseForceDecel = True
  elif case == 'soft_disabling':
    sm['selfdriveState'].state = log.SelfdriveState.OpenpilotState.softDisabling
  elif case == 'driver_stale':
    sm.failed_checks['alive'].add('driverMonitoringState')
  elif case == 'driver_missing_stamp':
    sm.logMonoTime['driverMonitoringState'] = 0
  elif case in ('allowance_zero', 'allowance_above_ten'):
    values['NrdrCruiseOverspeedAllowance'] = 0 if case == 'allowance_zero' else 11
  elif case == 'lead':
    sm['radarState'].leadTwo.present = True
  live = LiveParams(CONTROL_GROUPS, params=NS(get=values.get), start_worker=False)
  instance = controls(live)
  if case == 'ineligible':
    instance.CP_SP.enableGasInterceptor = True
  message = control_method()(instance, sm)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    native = convert_carControlSP(reader)
  assert native.pcmCruiseCoastVersion == 1
  assert native.pcmEngineBrakeEnabled is engine_enabled
  assert not native.pcmCruiseCoastAllowed
  assert native.pcmCruiseCoastSetSpeed == native.pcmCruiseCoastMaxSpeed == 0.
  assert native.pcmCruiseCoastMonoTime == 0
  if engine_enabled and case in ('negative_accel', 'throttle_false', 'driver_force_decel', 'soft_disabling',
                                 'driver_stale', 'driver_missing_stamp'):
    assert native.pcmEngineBrakeAllowed  # Why v1 receivers MUST NOT fall back on a denial.
  assert values['NrdrExperimentalEngineBraking'] is engine_enabled


def test_allowance_and_engine_choice_use_one_generation_and_diagnostics_stay_change_only():
  from openpilot.nrdr.params.snapshots import ParamSnapshot

  reports = []

  class AlternatingSnapshots:
    reads = 0

    def record_applied_settings(self, *args, **kwargs):
      reports.append((args, kwargs))

    @property
    def snapshot(self):
      self.reads += 1
      enabled = self.reads % 2 == 0
      return ParamSnapshot(self.reads, {'NrdrExperimentalEngineBraking': enabled,
                                       'NrdrCruiseOverspeedAllowance': 10 if enabled else 5})

  live = AlternatingSnapshots()
  instance = controls(live)
  method = control_method()
  for index in range(1, 5):
    wire = method(instance, messages())
    assert live.reads == index
    assert wire.pcmCruiseCoastAllowed and wire.pcmCruiseCoastVersion == 1
    assert wire.pcmEngineBrakeEnabled is (index % 2 == 0)
    assert wire.pcmCruiseCoastMaxSpeed == pytest.approx(24.4704 if wire.pcmEngineBrakeEnabled else 22.2352)
    assert reports[-1] == (('pcm_engine_braking', index),
                          {'configured_enabled': wire.pcmEngineBrakeEnabled,
                           'allowance_mph': 10 if wire.pcmEngineBrakeEnabled else 5, 'supported': True})
