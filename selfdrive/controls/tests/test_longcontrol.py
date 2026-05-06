from types import SimpleNamespace

from cereal import car

import openpilot.selfdrive.controls.lib.longcontrol as longcontrol
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState, long_control_state_trans


def make_toggles(**overrides):
  defaults = {
    "custom_accel_profile": False,
    "human_acceleration": False,
    "startAccel": 1.5,
    "stopAccel": -0.5,
    "stoppingDecelRate": 0.8,
    "vEgoStarting": 0.5,
    "vEgoStopping": 0.5,
  }
  defaults.update(overrides)
  return SimpleNamespace(**defaults)


class TestLongControlStateTransition:

  def test_stay_stopped(self):
    CP = car.CarParams.new_message()
    toggles = make_toggles()
    active = True
    current_state = LongCtrlState.stopping
    next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=True, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=True, cruise_standstill=False, starpilot_toggles=toggles)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=False, cruise_standstill=True, starpilot_toggles=toggles,
                             allow_stopping_release=False)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP, active, current_state, v_ego=1.0,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
    assert next_state == LongCtrlState.pid
    active = False
    next_state = long_control_state_trans(CP, active, current_state, v_ego=1.0,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
    assert next_state == LongCtrlState.off


def test_engage():
  CP = car.CarParams.new_message()
  toggles = make_toggles()
  active = True
  current_state = LongCtrlState.off
  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=True, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.stopping
  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=True, cruise_standstill=False, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.stopping
  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=False, cruise_standstill=True, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.stopping
  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.pid


def test_starting():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  toggles = make_toggles(vEgoStarting=0.5)
  active = True
  current_state = LongCtrlState.starting
  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.1,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.starting
  next_state = long_control_state_trans(CP, active, current_state, v_ego=1.0,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles)
  assert next_state == LongCtrlState.pid


def test_stopping_release_hysteresis_blocks_immediate_launch():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  toggles = make_toggles(vEgoStarting=0.5)
  active = True
  current_state = LongCtrlState.stopping

  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.0,
                             should_stop=False, brake_pressed=False, cruise_standstill=False, starpilot_toggles=toggles,
                             allow_stopping_release=False)
  assert next_state == LongCtrlState.stopping


def test_stopping_release_allows_launch_while_cruise_standstill_latched():
  CP = car.CarParams.new_message()
  toggles = make_toggles(vEgoStarting=0.5)
  active = True
  current_state = LongCtrlState.stopping

  next_state = long_control_state_trans(CP, active, current_state, v_ego=0.0,
                             should_stop=False, brake_pressed=False, cruise_standstill=True, starpilot_toggles=toggles,
                             allow_stopping_release=True)
  assert next_state == LongCtrlState.pid


def test_starting_accel_unchanged_when_custom_profile_disabled():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  lc = LongControl(CP)
  CS = car.CarState.new_message(vEgo=0.0, aEgo=0.0, brakePressed=False)
  CS.cruiseState.standstill = False

  output_accel = lc.update(
    active=True,
    CS=CS,
    a_target=0.1,
    should_stop=False,
    accel_limits=(-3.0, 2.0),
    starpilot_toggles=make_toggles(startAccel=1.5),
  )

  assert lc.long_control_state == LongCtrlState.starting
  assert output_accel == 1.5


def test_starting_accel_obeys_a_target_cap_when_custom_profile_enabled():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  lc = LongControl(CP)
  CS = car.CarState.new_message(vEgo=0.0, aEgo=0.0, brakePressed=False)
  CS.cruiseState.standstill = False

  output_accel = lc.update(
    active=True,
    CS=CS,
    a_target=0.1,
    should_stop=False,
    accel_limits=(-3.0, 2.0),
    starpilot_toggles=make_toggles(startAccel=1.5, custom_accel_profile=True),
  )

  assert lc.long_control_state == LongCtrlState.starting
  assert output_accel == 0.1


def test_update_requires_sustained_positive_target_to_leave_stopping():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  lc = LongControl(CP)
  lc.long_control_state = LongCtrlState.stopping
  CS = car.CarState.new_message(vEgo=0.0, aEgo=0.0, brakePressed=False)
  CS.cruiseState.standstill = False

  release_frames = int(round(longcontrol.STOPPING_RELEASE_HYSTERESIS / longcontrol.DT_CTRL))
  for _ in range(release_frames - 1):
    output_accel = lc.update(
      active=True,
      CS=CS,
      a_target=0.5,
      should_stop=False,
      accel_limits=(-3.0, 2.0),
      starpilot_toggles=make_toggles(startAccel=1.5),
    )
    assert lc.long_control_state == LongCtrlState.stopping
    assert output_accel <= 0.0

  lc.update(
    active=True,
    CS=CS,
    a_target=0.5,
    should_stop=False,
    accel_limits=(-3.0, 2.0),
    starpilot_toggles=make_toggles(startAccel=1.5),
  )

  assert lc.long_control_state == LongCtrlState.starting


def test_update_releases_stopping_with_cruise_standstill_latched():
  CP = car.CarParams.new_message(vEgoStarting=0.5)
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  lc = LongControl(CP)
  lc.long_control_state = LongCtrlState.stopping
  lc.last_output_accel = -2.003
  CS = car.CarState.new_message(vEgo=0.0, aEgo=0.0, brakePressed=False)
  CS.cruiseState.standstill = True

  release_frames = int(round(longcontrol.STOPPING_RELEASE_HYSTERESIS / longcontrol.DT_CTRL))
  for _ in range(release_frames - 1):
    output_accel = lc.update(
      active=True,
      CS=CS,
      a_target=0.5,
      should_stop=False,
      accel_limits=(-3.0, 2.0),
      starpilot_toggles=make_toggles(startAccel=1.5),
    )
    assert lc.long_control_state == LongCtrlState.stopping
    assert output_accel <= 0.0

  output_accel = lc.update(
    active=True,
    CS=CS,
    a_target=0.5,
    should_stop=False,
    accel_limits=(-3.0, 2.0),
    starpilot_toggles=make_toggles(startAccel=1.5),
  )

  assert lc.long_control_state == LongCtrlState.pid
  assert output_accel > 0.0


def test_volt_testing_ground_handoff_freezes_integrator(monkeypatch):
  CP = car.CarParams.new_message()
  CP.brand = "gm"
  CP.enableGasInterceptorDEPRECATED = True
  CP.carFingerprint = "CHEVROLET_VOLT_ASCM"
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  monkeypatch.setattr(longcontrol, "testing_ground", SimpleNamespace(use_2=True))

  lc = LongControl(CP)
  freeze = lc._get_pedal_long_freeze(a_target=0.7, error=0.7, v_ego=8.0, accel_limits=(-3.0, 2.0))

  assert freeze
  assert lc.integrator_hold_frames > 0


def test_non_interceptor_volt_testing_ground_handoff_freezes_integrator(monkeypatch):
  CP = car.CarParams.new_message()
  CP.brand = "gm"
  CP.enableGasInterceptorDEPRECATED = False
  CP.carFingerprint = "CHEVROLET_VOLT_ASCM"
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  monkeypatch.setattr(longcontrol, "testing_ground", SimpleNamespace(use_2=True))

  lc = LongControl(CP)
  freeze = lc._get_pedal_long_freeze(a_target=0.7, error=0.7, v_ego=8.0, accel_limits=(-3.0, 2.0))

  assert freeze
  assert lc.integrator_hold_frames > 0


def test_negative_target_unwinds_positive_accel_command_after_sign_flip():
  CP = car.CarParams.new_message(startingState=True, vEgoStarting=0.5)
  CP.longitudinalTuning.kpBP = [0.0]
  CP.longitudinalTuning.kpV = [0.1]
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.03]

  lc = LongControl(CP)
  lc.long_control_state = LongCtrlState.pid
  lc.last_output_accel = 1.2
  lc.pid.i = 1.2
  CS = car.CarState.new_message(vEgo=30.0, aEgo=0.9, brakePressed=False, gasPressed=False)
  CS.cruiseState.standstill = False

  output_accel = lc.update(
    active=True,
    CS=CS,
    a_target=-0.5,
    should_stop=False,
    accel_limits=(-3.0, 2.0),
    starpilot_toggles=make_toggles(),
  )

  assert lc.long_control_state == LongCtrlState.pid
  assert output_accel <= 0.01
