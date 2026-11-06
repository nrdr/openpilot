"""Exercise the real controlsd method and receiver fade with live snapshots."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

from opendbc.car.honda.engine_braking import EngineBrakeFade, fresh_context
from opendbc.car.honda.values import CAR, HondaFlags
from openpilot.nrdr.features.longitudinal.engine_braking import EngineBrakeSettingsReporter, engine_brake_context
from opendbc.car.honda.civic_pcm import uses_civic_pcm
from openpilot.nrdr.params import read_bool, read_float
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LIVE_LATERAL_KEYS, LiveParams, REFRESH_PERIOD
from openpilot.nrdr.tests.test_engine_braking_context import Messages


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

  path = Path(__file__).resolve().parents[2] / 'sunnypilot/selfdrive/controls/controlsd_ext.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ControlsExt')
  init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == '__init__')
  assert key not in ast.unparse(init), 'Do not cache this preference at startup'
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'state_control_ext')
  method.returns = None
  for arg in method.args.args:
    arg.annotation = None
  tree.body = [method]
  env = {
    'custom': NS(CarControlSP=NS(new_message=lambda: NS(leadOne=NS(), leadTwo=NS(), mads=NS(), intelligentCruiseButtonManagement=NS()))),
    'pcm_reference': lambda *_: (False, 0., 0), 'engine_brake_context': engine_brake_context,
    'read_bool': read_bool, 'read_float': read_float, 'uses_civic_pcm': uses_civic_pcm,
  }
  exec(compile(tree, str(path), 'exec'), env)
  counted = CountingSnapshot()
  controls = NS(CP=NS(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=HondaFlags.NIDEC),
                CP_SP=NS(enableGasInterceptor=False, flags=0), nrdr_live_params=counted, get_lead_data=lambda *_: None,
                engine_brake_settings_reporter=EngineBrakeSettingsReporter())
  sm = Messages()
  sm['selfdriveStateSP'] = NS(mads=NS(state=0, enabled=False, active=False, available=False),
                            intelligentCruiseButtonManagement=NS(state=0, sendButton=0, vTarget=0))
  sm['longitudinalPlan'].speeds = []
  fade = EngineBrakeFade()

  def frame(index):
    now = 1_000_000_000 + index * 20_000_000
    sm.logMonoTime = dict.fromkeys(sm, now)
    reads_before, count_before = len(storage_reads), counted.count
    wire = env['state_control_ext'](controls, sm)
    assert len(storage_reads) == reads_before, 'No storage polling from the actuation loop'
    assert counted.count == count_before + 1, 'Enable flag and allowance must share one snapshot'
    output = fade.apply(25., 100, now_nanos=now, permitted=fresh_context(wire, now), request=wire.pcmEngineBrakeRequest)
    return wire, output

  def save(value):
    values[key] = value
    # One normal worker polling cycle; no controlsd restart or disengagement.
    for _ in CONTROL_GROUPS:
      live.poll_once()

  wire, output = frame(0)
  assert not wire.pcmEngineBrakeAllowed and output == (25., 100)
  save(True)
  wire, output = frame(1)
  assert wire.pcmEngineBrakeAllowed and wire.pcmEngineBrakeRequest and output == (25., 100)
  for index in range(2, 102):
    wire, output = frame(index)
  assert .6 < fade.weight < .7 and output[0] < 10 and output[1] < 40
  save(False)
  wire, output = frame(102)
  assert not wire.pcmEngineBrakeAllowed and not wire.pcmEngineBrakeRequest and wire.pcmEngineBrakeMonoTime == 0
  assert output == (25., 100) and fade.weight == 0 and fade.last_time is None
  save(True)
  _, output = frame(103)
  assert output == (25., 100) and fade.weight == 0  # No stale weight on re-enable.
  _, output = frame(104)
  assert 0 < fade.weight < .01 and output[0] > 24
  sm['radarState'].leadOne.present = True
  wire, output = frame(105)
  assert not wire.pcmEngineBrakeAllowed and output == (25., 100) and fade.weight == 0
  assert [report[1]['configured_enabled'] for report in counted.reports] == [False, True, False, True]
  assert all(report[1]['allowance_mph'] == 5 for report in counted.reports)
