from types import SimpleNamespace
import ast
from pathlib import Path

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.honda.tests.test_civic_pcm import interface
from openpilot.nrdr.features.longitudinal.civic_pcm import pcm_reference, pcm_coast_eligible
from openpilot.cereal import custom
from openpilot.cereal import log
from openpilot.selfdrive.car.helpers import convert_carControlSP


@pytest.mark.parametrize('car,interceptor', [(CAR.HONDA_CLARITY, False), (CAR.HONDA_CLARITY, True),
                                          (CAR.HONDA_CIVIC, True), (CAR.HONDA_CIVIC_BOSCH, False)])
def test_reference_handoff_is_civic_pcm_only(car, interceptor):
  ci, _ = interface(car, interceptor=interceptor)
  assert pcm_reference(ci.CP, ci.CP_SP, [20.0], 100, True) == (False, 0.0, 0)


@pytest.mark.parametrize('speed,valid,mono', [(float('nan'), True, 100), (float('inf'), True, 100),
                                           (-1.0, True, 100), (101.0, True, 100),
                                           (20.0, False, 100), (20.0, True, 0)])
def test_invalid_reference_does_not_change_mode(speed, valid, mono):
  cp = SimpleNamespace(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=HondaFlags.NIDEC_PCM_EXPERIMENTAL)
  sp = SimpleNamespace(enableGasInterceptor=False, flags=0)
  assert pcm_reference(cp, sp, [speed], mono, valid) == (True, 0.0, 0)
  assert pcm_reference(cp, sp, [], 100, True) == (True, 0.0, 0)


@pytest.mark.parametrize('mode', [0, 1, 2])
def test_reference_is_only_published_for_experimental(mode):
  ci, _ = interface(pcm_mode=mode)
  expected = (True, 20.0, 100) if mode == 2 else (False, 0.0, 0)
  assert pcm_reference(ci.CP, ci.CP_SP, [20.0], 100, True) == expected


@pytest.mark.parametrize('demand', [.8, -.8])
def test_experimental_ceiling_change_reaches_host_accel_output_without_retuning(demand):
  from opendbc.car import structs
  from openpilot.selfdrive.controls.lib.longcontrol import LongControl

  outputs = []
  for mode in (0, 2):
    ci, _ = interface(pcm_mode=mode, mvl=True)
    controller = LongControl(ci.CP, ci.CP_SP)
    state = structs.CarState(vEgo=30., aEgo=0.)
    limits = ci.get_pid_accel_limits(ci.CP, ci.CP_SP, state.vEgo, 30.)
    outputs.append(controller.update(True, state, demand, False, limits))
    # This experiment does not add Kp/Ki correction or change feedforward gain.
    assert controller.pid.p == controller.pid.i == 0.
  assert outputs == pytest.approx([.2, demand] if demand > 0. else [demand, demand])


@pytest.mark.parametrize('speed', [0.0, 20.0, 100.0])
def test_reference_survives_capnp_and_card_conversion(speed):
  ci, _ = interface()
  enabled, target, stamp = pcm_reference(ci.CP, ci.CP_SP, [speed], 10_000_000_000, True)
  message = custom.CarControlSP.new_message(civicPcmEnabled=enabled, civicPcmReferenceSpeed=target,
                                            civicPcmReferenceMonoTime=stamp,
                                            civicPcmCoastEligible=True, civicPcmCruiseSpeed=20.0)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    converted = convert_carControlSP(reader)
  assert converted.civicPcmEnabled
  assert converted.civicPcmReferenceSpeed == speed
  assert converted.civicPcmReferenceMonoTime == stamp
  assert converted.civicPcmCoastEligible
  assert converted.civicPcmCruiseSpeed == 20.0


@pytest.mark.parametrize('reason', ['none', 'invalid', 'force', 'lead', 'leadOne', 'leadTwo',
                                  'stop', 'fcw', 'planner', 'unset', 'nan', 'zero', 'too_fast'])
def test_only_observed_free_cruise_is_coast_eligible(reason):
  plan = SimpleNamespace(longitudinalPlanSource="cruise", hasLead=False, shouldStop=False, fcw=False)
  radar = SimpleNamespace(leadOne=SimpleNamespace(present=False), leadTwo=SimpleNamespace(present=False))
  cruise = 72.0
  if reason in ('leadOne', 'leadTwo'):
    getattr(radar, reason).present = True
  elif reason in ('lead', 'stop', 'fcw'):
    setattr(plan, {'lead': 'hasLead', 'stop': 'shouldStop', 'fcw': 'fcw'}[reason], True)
  elif reason == 'planner':
    plan.longitudinalPlanSource = "lead0"
  elif reason in ('unset', 'nan', 'zero', 'too_fast'):
    cruise = {'unset': 255.0, 'nan': float('nan'), 'zero': 0.0, 'too_fast': 170.0}[reason]
  assert pcm_coast_eligible(plan, radar, cruise, reason != 'invalid', reason == 'force') == (
    (True, 20.0) if reason == 'none' else (False, 0.0))


def test_controlsd_handoff_uses_subscribed_inputs_not_its_own_output():
  # Exercise the actual producer without loading model/UI runtimes. In particular,
  # controlsd publishes controlsState but does not subscribe to it.
  path = Path(__file__).parents[2] / 'sunnypilot/selfdrive/controls/controlsd_ext.py'
  tree = ast.parse(path.read_text())
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ControlsExt')
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'state_control_ext')
  namespace = dict(custom=custom, messaging=SimpleNamespace(SubMaster=object),
                   pcm_reference=pcm_reference, pcm_coast_eligible=pcm_coast_eligible)
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), namespace)
  ci, _ = interface()
  host = SimpleNamespace(CP=ci.CP, CP_SP=ci.CP_SP,
                         get_lead_data=lambda dst, src: setattr(dst, 'status', src.present))
  plan = log.LongitudinalPlan.new_message(speeds=[20.], longitudinalPlanSource='cruise')
  radar = log.RadarState.new_message()
  from opendbc.car import structs
  state = structs.CarState(vCruise=72.)

  class SM(dict):
    logMonoTime = {'longitudinalPlan': 10_000_000_000}

    def all_checks(self, names):
      assert set(names) <= self.keys()
      return True

  sm = SM(longitudinalPlan=plan, radarState=radar, carState=state,
          driverMonitoringState=SimpleNamespace(noResponseForceDecel=False),
          selfdriveState=SimpleNamespace(state='enabled'),
          selfdriveStateSP=custom.SelfdriveStateSP.new_message())
  out = namespace['state_control_ext'](host, sm)
  assert out.civicPcmCoastEligible and out.civicPcmCruiseSpeed == 20.
  sm['selfdriveState'].state = 'softDisabling'
  assert not namespace['state_control_ext'](host, sm).civicPcmCoastEligible
