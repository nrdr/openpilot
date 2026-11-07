"""Legacy PI/reference/transport host tests; no live settings or device I/O."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.legacy_pcm import KP_BP, KP_V, KI_BP, KI_V, LegacyPCMCommand, LegacyPCMController, compute_gb
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.nrdr.features.longitudinal.legacy_pcm import (
  LegacyLongControl, LegacySpeedPI, SelectedPlanReference, legacy_pcm_enabled,
)


def state(**overrides):
  args = {'vEgo': 20., 'aEgo': 0., 'vCruise': 100., 'gasPressed': False, 'brakePressed': False,
          'standstill': False, 'cruiseState': NS(standstill=False)}
  args.update(overrides)
  return NS(**args)


def test_exact_civic_tune_and_units():
  assert KP_BP == (0., 5., 35.) and KP_V == (3.6, 2.4, 1.5)
  assert KI_BP == (0., 35.) and KI_V == (.54, .36)
  pid = LegacySpeedPI()
  pid.update(19., 20., -.5)
  assert pid.p == pytest.approx(-1.95)  # 1 m/s error -> m/s^2
  assert pid.i == pytest.approx(-np.interp(20., KI_BP, KI_V) / 100)
  assert pid.f == -.5


def donor_pi_step(integral, target, speed, accel):
  """Independent scalar transcription of pinned 05475df8 PI.update/compute_gb."""
  error = target - speed
  p = error * np.interp(speed, [0., 5., 35.], [3.6, 2.4, 1.5])
  i = integral + error * np.interp(speed, [0., 35.], [.54, .36]) / 100.
  creep = (2.3 - speed) / 2.3 * .15 if speed < 2.3 else 0.
  lower = -np.interp(speed, [5., 20.], [1., .8])
  trial = (p + accel + i) / 4.8 - creep
  if ((error >= 0 and (trial <= 0 or i < 0)) or (error <= 0 and (trial >= lower or i > 0))):
    integral = i
  return integral, np.clip((p + accel + integral) / 4.8 - creep, lower, 0)


def test_pi_matches_pinned_equations_through_saturation_and_recovery():
  pid, integral = LegacySpeedPI(), 0.
  for i in range(2000):
    speed = max(.3, 17.5 + 17.5 * np.sin(i * .019))
    target = max(0., speed + 4. * np.sin(i * .037))
    accel = 2. * np.cos(i * .031)
    integral, expected = donor_pi_step(integral, target, speed, accel)
    assert pid.update(target, speed, accel) == pytest.approx(expected, abs=1e-12)
    assert pid.i == pytest.approx(integral, abs=1e-12)


def test_anti_windup_is_in_converted_brake_domain():
  pid = LegacySpeedPI()
  for _ in range(200):
    assert pid.update(21., 20., 0.) == 0.
  assert pid.i == 0. and pid.saturated
  pid.reset()
  assert pid.update(.31, .3, 0.) < 0.
  assert pid.i > 0.  # Creep means positive accel-domain output is not saturated.


def test_reference_uses_selected_accel_and_stays_continuous_on_zero_set_speed():
  reference = SelectedPlanReference()
  first = reference.update(20., -1., (-4., 2.), 0.)
  assert first.speed == pytest.approx(19.99)  # not zero and not MPC speeds[0]
  assert first.accel == -1. and first.future_speed == 0.
  for _ in range(100):
    sample = reference.update(20., -1., (-4., 2.), 0.)
  assert 18. < sample.speed < 19.99
  reference.reset()
  positive = reference.update(10., 4., (-4., 2.), 100.)
  assert positive.accel == 2. and positive.speed == pytest.approx(10.02)
  assert positive.future_speed == pytest.approx(14.02)


def test_reference_does_not_accumulate_unbounded_speed_error():
  reference = SelectedPlanReference()
  for _ in range(10000):
    result = reference.update(10., 1., (-4., 2.), 150.)
  assert result.speed == pytest.approx(12.01, abs=1e-8)


def test_transport_separates_plan_acceleration_from_brake_feedback():
  controller = LegacyLongControl()
  cs = state(vEgo=.0, aEgo=0., standstill=True)
  accel = controller.update(True, cs, .1, False, (-4., 2.))
  assert accel == .1 and controller.target_accel == .1
  assert controller.brake > 0. and controller.pid.p < 0.
  expected = -compute_gb(controller.pid.p + controller.pid.i + .1, .3)
  assert controller.brake == pytest.approx(expected)


def test_historical_stop_hold_release_and_pid_reentry():
  controller = LegacyLongControl()
  cs = state(vEgo=0., standstill=True)
  controller.long_control_state = controller.states.stopping
  controller.last_output_gb = -.1
  controller.update(True, cs, 0., True, (-4., 2.))
  assert controller.brake == pytest.approx(.102)
  for _ in range(100):
    controller.update(True, cs, 0., True, (-4., 2.))
  assert .25 <= controller.brake < .2521
  previous = controller.brake
  controller.update(True, cs, 1., False, (-4., 2.))
  assert controller.long_control_state == controller.states.starting
  assert controller.brake == pytest.approx(previous - .008)
  for _ in range(20):
    controller.update(True, cs, 1., False, (-4., 2.))
  assert controller.long_control_state == controller.states.pid


@pytest.mark.parametrize('valid,active,overrides', [(False, True, {}), (True, False, {}),
                                                   (True, True, {'gasPressed': True}), (True, True, {'brakePressed': True}),
                                                   (True, True, {'aEgo': float('nan')})])
def test_invalid_plan_or_override_resets_reference_and_feedback(valid, active, overrides):
  controller = LegacyLongControl()
  controller.update(True, state(), -1., False, (-4., 2.))
  assert controller.update(active, state(**overrides), 1., False, (-4., 2.), valid) == 0.
  assert controller.brake == controller.v_pid == controller.target_accel == 0.
  assert controller.long_control_state == controller.states.off
  assert controller.reference.speed is None


@pytest.mark.parametrize('cruise_speed', [float('nan'), float('inf'), -float('inf'), 255., 256., -1.])
@pytest.mark.parametrize('already_active', [False, True])
def test_invalid_cruise_fails_closed_even_with_fresh_plan_and_finite_actuators(cruise_speed, already_active):
  controller, helper = LegacyLongControl(), LegacyPCMController()
  if already_active:
    controller.update(True, state(), 1., False, (-4., 2.), reference_valid=True)
    previous = helper.update(active=True, v_ego=20., a_ego=0., v_target=controller.v_pid,
                             a_target=controller.target_accel, brake=controller.brake)
    assert previous.pcm_accel == 198
    controller.pid.i = .2
  cs = state(vCruise=cruise_speed)
  assert controller.update(True, cs, 1., False, (-4., 2.), reference_valid=True) == 0.
  assert controller.long_control_state == controller.states.off
  assert controller.reference.speed is None
  assert controller.pid.p == controller.pid.i == controller.pid.f == 0.
  assert controller.brake == controller.v_pid == controller.target_accel == controller.last_output_gb == 0.
  command = helper.update(active=controller.long_control_state != controller.states.off,
                          v_ego=cs.vEgo, a_ego=cs.aEgo, v_target=controller.v_pid,
                          a_target=controller.target_accel, brake=controller.brake)
  assert command == LegacyPCMCommand()


def test_stale_plan_independently_removes_prior_pcm_authority_with_valid_cruise():
  controller, helper = LegacyLongControl(), LegacyPCMController()
  cs = state(vCruise=100.)
  controller.update(True, cs, 1., False, (-4., 2.), reference_valid=True)
  assert helper.update(active=True, v_ego=cs.vEgo, a_ego=cs.aEgo, v_target=controller.v_pid,
                       a_target=controller.target_accel, brake=controller.brake).pcm_accel == 198
  assert controller.update(True, cs, 1., False, (-4., 2.), reference_valid=False) == 0.
  assert controller.long_control_state == controller.states.off
  assert controller.reference.speed is None
  assert helper.update(active=controller.long_control_state != controller.states.off,
                       v_ego=cs.vEgo, a_ego=cs.aEgo, v_target=controller.v_pid,
                       a_target=controller.target_accel, brake=controller.brake) == LegacyPCMCommand()


@pytest.mark.parametrize('cruise_speed', [0., 144.84096, 169., 254.999])
def test_valid_internal_cruise_domain_remains_admitted(cruise_speed):
  controller = LegacyLongControl()
  controller.update(True, state(vCruise=cruise_speed), 0., False, (-4., 2.))
  assert controller.long_control_state == controller.states.pid


def test_qualification_is_default_off_and_independent_of_fixed_cruise():
  cp = NS(carFingerprint=CAR.HONDA_CIVIC, flags=HondaFlags.NIDEC, openpilotLongitudinalControl=True,
          passive=False, dashcamOnly=False)
  sp = NS(enableGasInterceptor=False, flags=0)
  assert not legacy_pcm_enabled(cp, sp)
  for fixed in (0, HondaFlags.NIDEC_PCM_FIXED_CRUISE):
    cp.flags = HondaFlags.NIDEC | HondaFlags.NIDEC_PCM_LEGACY | fixed
    assert legacy_pcm_enabled(cp, sp)
    sp.enableGasInterceptor = True
    assert not legacy_pcm_enabled(cp, sp)
    sp.enableGasInterceptor = False
  cp.carFingerprint = CAR.HONDA_CLARITY
  assert not legacy_pcm_enabled(cp, sp)


def test_longcontrol_dispatch_does_not_construct_nrdr_or_read_tunes():
  path = Path(__file__).resolve().parents[2] / 'selfdrive/controls/lib/longcontrol.py'
  tree = ast.parse(path.read_text())
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
  def forbidden(*_args):
    raise AssertionError('legacy mode constructed the live NRDR controller')
  env = {'car': car, 'LongCtrlState': car.CarControl.Actuators.LongControlState, 'np': np, 'DT_CTRL': .01,
         'PIDController': lambda *_args, **_kwargs: None, 'LegacyLongControl': LegacyLongControl,
         'legacy_pcm_enabled': lambda *_: True, 'NrdrLongControl': forbidden, 'nrdr_custom_longitudinal_enabled': forbidden}
  exec(compile(tree, str(path), 'exec'), env)
  cp = NS(longitudinalTuning=NS(kiBP=[0.], kiV=[1000.]))
  control = env['LongControl'](cp, object())
  assert control.nrdr_controller is None
  assert control.update(True, state(), -.5, False, (-4., 2.)) == -.5
  assert control.pid is control.legacy_controller.pid


def test_controlsd_assigns_separate_legacy_channels_after_update():
  path = Path(__file__).resolve().parents[2] / 'selfdrive/controls/controlsd.py'
  source = path.read_text()
  assert 'reference_valid=bool(self.sm.all_checks([\'longitudinalPlan\']))' in source
  assert 'actuators.speed = float(self.LoC.legacy_controller.v_pid)' in source
  assert 'actuators.brake = float(self.LoC.legacy_controller.brake)' in source
  assert 'actuators.longControlState = self.LoC.long_control_state' in source


def test_legacy_channels_survive_current_actuator_schema_roundtrip():
  controller = LegacyLongControl()
  controller.update(True, state(vEgo=0., standstill=True), .1, False, (-4., 2.))
  message = car.CarControl.new_message()
  message.actuators.speed = controller.v_pid
  message.actuators.accel = controller.target_accel
  message.actuators.brake = controller.brake
  message.actuators.gas = 0.
  message.actuators.longControlState = controller.long_control_state
  with car.CarControl.from_bytes(message.to_bytes()) as reader:
    assert reader.actuators.speed == pytest.approx(controller.v_pid)
    assert reader.actuators.accel == pytest.approx(.1)
    assert reader.actuators.brake == pytest.approx(controller.brake)
    assert reader.actuators.gas == 0.


def legacy_planner():
  from openpilot.nrdr.tests.test_non_honda_longitudinal import (
    CORE, ROOT, FakePlannerMpc, definitions, environment, forbidden,
  )
  env = environment(
    legacy_pcm_enabled=lambda *_: True, mvl_longitudinal_enabled=lambda *_: True,
    NrdrLongitudinalPlanner=forbidden, NrdrLongitudinalMpc=forbidden,
    nrdr_custom_longitudinal_enabled=forbidden,
    LongitudinalMpc=FakePlannerMpc, T_IDXS_MPC=np.linspace(0., 10., 13),
    EventsSP=lambda: NS(clear=lambda: None, to_msg=list),
    E2EAlertsHelper=lambda: NS(update=lambda *_: None, green_light_alert=False, lead_depart_alert=False),
    SmartCruiseControl=forbidden, SpeedLimitResolver=forbidden, SpeedLimitAssist=forbidden,
    NrdrSpeedLimitAssist=forbidden, AccelBoostSP=forbidden, get_active_bundle=forbidden,
  )
  env['custom'] = NS(LongitudinalPlanSP=NS(LongitudinalPlanSource=env['LongitudinalPlanSource']))
  helpers = definitions(ROOT / (CORE + 'drive_helpers.py'), env)
  env.update({key: helpers[key] for key in ('get_accel_from_plan', 'should_stop')})
  env['LongitudinalPlannerSP'] = definitions(
    ROOT / 'openpilot/sunnypilot/selfdrive/controls/lib/longitudinal_planner.py', env)['LongitudinalPlannerSP']
  cls = definitions(ROOT / (CORE + 'longitudinal_planner.py'), env)['LongitudinalPlanner']
  cp = NS(brand='honda', carFingerprint=CAR.HONDA_CIVIC, flags=int(HondaFlags.NIDEC_PCM_LEGACY),
          openpilotLongitudinalControl=True, longitudinalActuatorDelay=.3, steerRatio=15., wheelbase=2.7)
  return cls(cp, NS())


@pytest.mark.parametrize('experimental', [False, True])
def test_legacy_planner_has_no_mvl_nrdr_tunes_boost_or_scc_and_stops_at_zero(experimental):
  planner = legacy_planner()
  assert planner.legacy_pcm and not planner.mvl_enabled
  assert planner.nrdr is planner.mpc.nrdr is planner.mpc.tune is None
  assert planner.mpc.kwargs['nrdr_enabled'] is False
  assert planner.scc is planner.sla is planner.resolver is planner.accel_boost_sp is None
  sm = {'carState': NS(vEgo=0., aEgo=0., vCruise=0., standstill=True, steeringAngleDeg=0.),
        'carControl': NS(orientationNED=[]), 'controlsState': NS(forceDecel=False, longControlState=1),
        'selfdriveState': NS(enabled=True, personality=3, experimentalMode=experimental),
        'vehicleParameters': NS(angleOffsetDeg=0.),
        'modelV2': NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 1.])),
                     action=NS(desiredAcceleration=1., shouldStop=False)),
        'radarState': NS(accel=1., crash_cnt=0)}
  planner.update(sm)
  assert planner.output_a_target == 0.
  assert planner.output_should_stop
  assert planner.mpc.weights[1] == 2  # Econ maps to base Relaxed, not custom tune.


@pytest.mark.parametrize('model_accel,expected', [(-1., -1.), (1., .03)])
def test_modern_model_and_cruise_arbitration_feed_one_legacy_reference(model_accel, expected):
  planner = legacy_planner()
  cs = state(vEgo=20., vCruise=100., steeringAngleDeg=0.)
  sm = {'carState': cs, 'carControl': NS(orientationNED=[]),
        'controlsState': NS(forceDecel=False, longControlState=1),
        'selfdriveState': NS(enabled=True, personality=1, experimentalMode=True),
        'vehicleParameters': NS(angleOffsetDeg=0.),
        'modelV2': NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 1.])),
                     action=NS(desiredAcceleration=model_accel, shouldStop=False)),
        'radarState': NS(accel=2., crash_cnt=0)}
  planner.update(sm)
  # Cruise jerk at 20 m/s is interpolated, not the arbitrary model/MPC accel.
  if model_accel > 0:
    expected = float(np.interp(20., [0., 10., 25., 40.], [1.6, 1.2, .8, .6])) * .05
  assert planner.output_a_target == pytest.approx(expected)
  controller = LegacyLongControl()
  controller.update(True, cs, planner.output_a_target, planner.output_should_stop, (-4., 2.))
  assert controller.target_accel == pytest.approx(expected)
  assert controller.v_pid == pytest.approx(20. + expected * .01)


@pytest.mark.parametrize('fixed', [False, True])
@pytest.mark.parametrize('target_kph,curve_limit', [(72., 100.), (72., 15.), (0., 100.), (169., 100.)])
def test_fixed_target_ceiling_does_not_erase_lower_curve_reductions(fixed, target_kph, curve_limit):
  from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS
  from openpilot.nrdr.tests.test_non_honda_longitudinal import NS, SM, cp, planner_pair
  class CustomPlanner:
    # Deliberately polluted existing settings, including zero stop threshold.
    v_ego_stopping = 0.
    def __init__(self, *_):
      pass

    def refresh(self):
      pass

    def cruise_target(self, target):
      return target * 1.05

    def max_accel(self, _speed):
      return 2.

    def turn_accel_threshold(self):
      return 0.

    def stopped_gap(self, _reset):
      return 0.

    def launch_accel(self, *_args):
      return 2.

    def personality_accel_ceiling(self, *_args):
      return 2.

  current, _ = planner_pair(fixed_pcm_cruise_enabled=lambda *_: fixed,
                            NrdrLongitudinalPlanner=CustomPlanner, FIXED_CRUISE_MPS=FIXED_CRUISE_MPS)
  planner = current['LongitudinalPlanner'](cp('honda'), NS())
  speed = 0. if target_kph == 0. else 20.
  sm = SM(carState=NS(vEgo=speed, aEgo=0., vCruise=target_kph, standstill=speed == 0., steeringAngleDeg=0.),
          carControl=NS(orientationNED=[]), controlsState=NS(forceDecel=False, longControlState=1),
          selfdriveState=NS(enabled=True, personality=1, experimentalMode=False),
          vehicleParameters=NS(angleOffsetDeg=0.),
          modelV2=NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 1.])),
                     action=NS(desiredAcceleration=2., shouldStop=False)),
          radarState=NS(accel=2., crash_cnt=0))
  sm.target_limit = curve_limit
  seen_targets = []
  original_update = planner.mpc.update
  def capture_update(*args, **kwargs):
    seen_targets.append(kwargs['v_cruise'])
    original_update(*args, **kwargs)
  planner.mpc.update = capture_update
  planner.update(sm)
  raw_target = min(min(target_kph, current['V_CRUISE_MAX']) / 3.6, curve_limit)
  expected = min(raw_target, FIXED_CRUISE_MPS) if fixed else raw_target * 1.05
  assert seen_targets == pytest.approx([expected])
  # A target reduction enters the ordinary jerk-limited cruise path.
  assert abs(planner.a_cruise) <= .08 + 1e-9
  if target_kph == 0.:
    assert planner.output_should_stop is fixed
