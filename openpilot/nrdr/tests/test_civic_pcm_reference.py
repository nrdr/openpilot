import ast
import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.car.honda.values import CAR
from opendbc.car.honda.tests.test_civic_pcm import interface
from opendbc.car import structs
from opendbc.car.honda.civic_pcm import REFERENCE_MAX_AGE_NS
from openpilot.nrdr.features.longitudinal.civic_pcm import pcm_plan_ready, pcm_reference
from openpilot.cereal import custom
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
  cp = SimpleNamespace(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=0)
  sp = SimpleNamespace(enableGasInterceptor=False, flags=0)
  assert pcm_reference(cp, sp, [speed], mono, valid) == (True, 0.0, 0)
  assert pcm_reference(cp, sp, [], 100, True) == (True, 0.0, 0)


@pytest.mark.parametrize('speed', [0.0, 20.0, 100.0])
def test_reference_survives_capnp_and_card_conversion(speed):
  ci, _ = interface()
  enabled, target, stamp = pcm_reference(ci.CP, ci.CP_SP, [speed], 10_000_000_000, True)
  message = custom.CarControlSP.new_message(civicPcmEnabled=enabled, civicPcmReferenceSpeed=target,
                                            civicPcmReferenceMonoTime=stamp)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    converted = convert_carControlSP(reader)
  assert converted.civicPcmEnabled
  assert converted.civicPcmReferenceSpeed == speed
  assert converted.civicPcmReferenceMonoTime == stamp


@pytest.mark.parametrize('car,interceptor', [(CAR.HONDA_CLARITY, False), (CAR.HONDA_CLARITY, True),
                                          (CAR.HONDA_CIVIC, True), (CAR.HONDA_CIVIC_BOSCH, False)])
def test_acceleration_plan_guard_does_not_change_other_platforms(car, interceptor):
  ci, _ = interface(car, interceptor=interceptor)
  assert pcm_plan_ready(ci.CP, ci.CP_SP, float('nan'), 0, 1_000_000_000, False)


@pytest.mark.parametrize('age', [0, REFERENCE_MAX_AGE_NS])
@pytest.mark.parametrize('acceleration', [-3., 0., 2.])
def test_fresh_civic_acceleration_plan_is_authorized(age, acceleration):
  ci, _ = interface()
  stamp = 10_000_000_000
  assert pcm_plan_ready(ci.CP, ci.CP_SP, acceleration, stamp, stamp + age, True)


@pytest.mark.parametrize('age,valid,stamp,acceleration', [
  (REFERENCE_MAX_AGE_NS + 1, True, 10_000_000_000, -.7),
  (-1, True, 10_000_000_000, -.7),
  (0, False, 10_000_000_000, -.7),
  (0, True, 0, -.7),
  (0, True, 10_000_000_000, float('nan')),
  (0, True, 10_000_000_000, float('inf')),
])
def test_bad_civic_plan_revokes_authority(age, valid, stamp, acceleration):
  ci, _ = interface()
  assert not pcm_plan_ready(ci.CP, ci.CP_SP, acceleration, stamp, stamp + age, valid)


@pytest.fixture(scope='module')
def control_activity_source():
  # Execute the real controlsd statements from plan selection through LoC's
  # update, without importing unrelated model/device/lateral dependencies.
  path = Path(__file__).resolve().parents[2] / 'selfdrive/controls/controlsd.py'
  cls = next(node for node in ast.parse(path.read_text(encoding='utf-8')).body
             if isinstance(node, ast.ClassDef) and node.name == 'Controls')
  method = copy.deepcopy(next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'state_control'))
  start = next(index for index, node in enumerate(method.body) if isinstance(node, ast.Assign) and
               any(isinstance(target, ast.Name) and target.id == 'long_plan' for target in node.targets))
  end = next(index for index, node in enumerate(method.body) if isinstance(node, ast.Assign) and
             any(isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and
                 target.value.id == 'actuators' and target.attr == 'accel' for target in node.targets))
  method.body = method.body[start:end + 1] + [ast.Return(value=ast.Name(id='CC', ctx=ast.Load()))]
  method.args.args.append(ast.arg(arg='CS'))
  method.args.args.append(ast.arg(arg='lat_active'))
  tree = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))

  def execute(controls, now_nanos, replay=False):
    namespace = {'car': structs, 'pcm_plan_ready': pcm_plan_ready, 'REPLAY': replay,
                 'time': SimpleNamespace(monotonic_ns=lambda: now_nanos),
                 'allow_longitudinal': lambda *_: True, 'LaneChangeState': SimpleNamespace(off=0),
                 'CV': SimpleNamespace(KPH_TO_MS=1 / 3.6), 'stopping_inputs': lambda *_: (0., 0.)}
    exec(compile(tree, str(path), 'exec'), namespace)
    return namespace['state_control'](controls, controls.sm['carState'], True)
  return execute


class ActivityServices(dict):
  def __init__(self, stamp, valid):
    super().__init__(carState=SimpleNamespace(vEgo=23., vCruise=90.),
                     modelV2=SimpleNamespace(meta=SimpleNamespace(laneChangeState=0)),
                     longitudinalPlan=SimpleNamespace(aTarget=-.7, shouldStop=False),
                     selfdriveState=SimpleNamespace(enabled=True, personality=1), onroadEvents=[])
    self.logMonoTime = {'longitudinalPlan': stamp, 'selfdriveState': stamp}
    self.checks_valid = valid

  def all_checks(self, services):
    assert services == ['longitudinalPlan']
    return self.checks_valid


class ActivityLongControl:
  long_control_state = structs.CarControl.Actuators.LongControlState.pid

  def __init__(self):
    self.reset_called = False
    self.active = None

  def reset(self):
    self.reset_called = True

  def update(self, active, *_args, **_kwargs):
    self.active = active
    return -.7 if active else 0.


@pytest.mark.parametrize('replay', [False, True])
@pytest.mark.parametrize('valid,age', [(True, 0), (True, REFERENCE_MAX_AGE_NS),
                                     (True, REFERENCE_MAX_AGE_NS + 1), (True, -1), (False, 0)])
@pytest.mark.parametrize('car,interceptor', [(CAR.HONDA_CIVIC, False), (CAR.HONDA_CLARITY, False), (CAR.HONDA_CIVIC, True)])
def test_controlsd_applies_plan_guard_before_longitudinal_pid(control_activity_source, replay, valid, age, car, interceptor):
  ci, _ = interface(car, interceptor=interceptor)
  ci.CP_SP.pcmCruiseSpeed = False
  stamp = 10_000_000_000
  sm = ActivityServices(stamp, valid)
  sm.logMonoTime['selfdriveState'] = stamp + age
  loc = ActivityLongControl()
  controls = SimpleNamespace(CP=ci.CP, CP_SP=ci.CP_SP, LoC=loc, sm=sm, calibrated_pose=None,
                             CI=SimpleNamespace(DRIVABLE_GEARS=[], get_pid_accel_limits=lambda *_: (-3., 2.)))
  cc = control_activity_source(controls, stamp + age, replay)
  expected = car != CAR.HONDA_CIVIC or interceptor or (valid and 0 <= age <= REFERENCE_MAX_AGE_NS)
  assert cc.longActive == loc.active == expected
  assert loc.reset_called == (not expected)
  assert cc.actuators.accel == pytest.approx(-.7 if expected else 0.)
