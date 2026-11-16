"""Off/fallback MVL learning versus startup-frozen ECU and Civic trial modes."""
from collections import deque
from dataclasses import replace

import pytest

from opendbc.car import structs
from opendbc.car.honda.carcontroller import NIDEC_SERVO_LAG_FRAMES
from opendbc.car.honda.tests.test_civic_pcm import control, interface
from opendbc.car.honda.tests.test_mvl_nrdr_integration import learned_state
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.tests.runtime_config import StaticHondaConfigProvider


def settled(car=CAR.HONDA_CRV, *, mode=0, speed=20., factor=4., lagged=.7, learning=True, interceptor=False):
  ci, config = interface(car, learning=learning, interceptor=interceptor, pcm_mode=mode)
  ci.CS.out.vEgo = speed
  ci.CS.out.cruiseState.speed = 33.
  ci.CC.long_active_prev = True
  ci.CC.speed_cmd_hist = deque([(lagged, True, True)] * NIDEC_SERVO_LAG_FRAMES, maxlen=NIDEC_SERVO_LAG_FRAMES)
  ci.CC.speed_factors = dict.fromkeys(ci.CC.speed_factors, factor)
  return ci, config.honda.provider


def step(ci, accel=.7, tick=0, sp=None):
  return ci.apply(control(accel).as_reader(), sp if sp is not None else structs.CarControlSP(), tick * 10_000_000)


@pytest.mark.parametrize("speed", [30.99, 31., 32.4, 34.])
@pytest.mark.parametrize("car,mode,frozen", [
  (CAR.HONDA_CIVIC, 0, False), (CAR.HONDA_CRV, 0, False), (CAR.HONDA_CRV, 2, False),
  (CAR.HONDA_CIVIC, 1, True), (CAR.HONDA_CRV, 1, True), (CAR.HONDA_CIVIC, 2, True),
])
def test_mode_freeze_and_mvl_governor_guard_control_deficit_learning(speed, car, mode, frozen):
  ci, _ = settled(car, mode=mode, speed=speed, factor=16.)
  ci.CC.sat_deficit_frames = 150  # one more eligible, maxed sample would lower the ceiling
  before = learned_state(ci.CC)
  step(ci)
  after = learned_state(ci.CC)
  assert ci.CC.guard_pcm_learner
  governed = speed >= 31.  # cruiseState.speed (33 m/s) minus the MVL margin.
  assert (after["sat_accel"] == before["sat_accel"]) == (frozen or governed)
  assert (after["speed_factors"] == before["speed_factors"]) == (frozen or governed)
  if frozen:
    assert after == before
  else:
    assert ci.CC.sat_deficit_frames == (0 if governed else 151)
    if governed:
      assert after["speed_alphas"] == before["speed_alphas"]


@pytest.mark.parametrize("speed", [30.99, 31., 33.])
@pytest.mark.parametrize("car,mode,frozen", [
  (CAR.HONDA_CIVIC, 0, False), (CAR.HONDA_CRV, 2, False),
  (CAR.HONDA_CRV, 1, True), (CAR.HONDA_CIVIC, 2, True),
])
def test_off_and_fallback_keep_mvl_governor_gate_for_wind_and_speed_learning(speed, car, mode, frozen):
  ci, _ = settled(car, mode=mode, speed=speed, lagged=.2)
  before = learned_state(ci.CC)
  step(ci)
  after = learned_state(ci.CC)
  for field in ("windfactor", "speed_alphas", "speed_factors"):
    assert (before[field] == after[field]) == (frozen or speed >= 31.)


@pytest.mark.parametrize("car,mode", [(CAR.HONDA_CIVIC, 0), (CAR.HONDA_CRV, 0), (CAR.HONDA_CRV, 2)])
def test_off_and_fallback_apply_mvl_cap_only_when_learning_resumes_below_governor(car, mode):
  ci, _ = settled(car, mode=mode, speed=32., factor=43.)
  step(ci)
  assert set(ci.CC.speed_factors.values()) == {43.}
  ci.CS.out.cruiseState.speed = 36.
  step(ci, tick=1)
  assert max(ci.CC.speed_factors.values()) == 16.


@pytest.mark.parametrize("factor,pinned", [(4., False), (5., False), (6., True)])
@pytest.mark.parametrize("measured", [-.4, -.6])
@pytest.mark.parametrize("car,mode", [(CAR.HONDA_CIVIC, 0), (CAR.HONDA_CRV, 0), (CAR.HONDA_CRV, 2)])
def test_off_and_fallback_coast_floor_allows_reductions_but_not_growth(car, mode, factor, pinned, measured):
  # At factor 5 the lagged -0.5 request is exactly the -2.5 m/s boundary.
  # Beyond it, MVL blocks growth but still admits reductions.
  ci, _ = settled(car, mode=mode, factor=factor, lagged=-.5)
  ci.CS.out.aEgo = measured
  before = learned_state(ci.CC)
  step(ci, accel=-.5)
  for key, would_grow in (("speed_factors", measured > -.5), ("speed_alphas", measured < -.5)):
    deltas = [v - before[key][k] for k, v in getattr(ci.CC, key).items()]
    if would_grow and pinned:
      assert not any(deltas)
    elif would_grow:
      assert max(deltas) > 0
    else:
      assert min(deltas) < 0


@pytest.mark.parametrize("mode", [0, 1, 2])
@pytest.mark.parametrize("car,interceptor,learning", [
  (CAR.HONDA_CRV, False, True), (CAR.HONDA_CIVIC, False, True),
  (CAR.HONDA_CLARITY, False, True), (CAR.HONDA_CLARITY, True, True),
  (CAR.HONDA_CIVIC, True, True), (CAR.HONDA_CRV, False, False),
])
def test_saved_state_not_clipped_on_load_or_on_ineligible_learning_paths(monkeypatch, car, interceptor, learning, mode):
  monkeypatch.setattr(StaticHondaConfigProvider, "load_mvl_param",
                      lambda self, key, default: 43. if key.startswith("speed_factor") else default)
  ci, _ = interface(car, interceptor=interceptor, learning=learning, pcm_mode=mode)
  assert set(ci.CC.speed_factors.values()) == {43.}
  frozen = not interceptor and (mode == 1 or (car == CAR.HONDA_CIVIC and mode == 2))
  eligible = learning and not interceptor and not frozen
  # Rolling engagement has its own 200-frame recovery window, then a servo delay.
  for tick in range(200 + NIDEC_SERVO_LAG_FRAMES + 2):
    if tick < 200:
      assert set(ci.CC.speed_factors.values()) == {43.}
    step(ci, tick=tick)
  if eligible:
    assert max(ci.CC.speed_factors.values()) == 16.
  else:
    assert set(ci.CC.speed_factors.values()) == {43.}


@pytest.mark.parametrize("factor,admitted", [(20., True), (99., True), (100., False)])
def test_civic_speed_reference_keeps_its_own_admission_bound(factor, admitted):
  ci, _ = settled(CAR.HONDA_CIVIC, mode=2, factor=factor)
  before = learned_state(ci.CC)
  for tick in range(1, 101):
    sp = structs.CarControlSP(civicPcmEnabled=True, civicPcmReferenceSpeed=20., civicPcmReferenceMonoTime=tick * 10_000_000)
    step(ci, tick=tick, sp=sp)
  assert (ci.CC.pcm_speed_sent > ci.CS.out.vEgo) == admitted
  assert learned_state(ci.CC) == before


@pytest.mark.parametrize("car,mode", [(CAR.HONDA_CRV, 1), (CAR.HONDA_CIVIC, 1), (CAR.HONDA_CIVIC, 2)])
def test_legacy_bool_cannot_unfreeze_learning_but_off_restart_can(car, mode):
  ci, provider = settled(car, mode=mode, factor=43.)
  before = learned_state(ci.CC)
  provider.live_tuning = replace(provider.live_tuning, ecu_matched_long=True)
  for tick in range(100):
    step(ci, tick=tick)
  provider.live_tuning = replace(provider.live_tuning, ecu_matched_long=False)
  for tick in range(100, 100 + NIDEC_SERVO_LAG_FRAMES):
    step(ci, tick=tick)
  assert learned_state(ci.CC) == before
  assert all(all(key.startswith("lat_accel_factor_") for key in entry) for entry in provider.persisted)
  step(ci, tick=100 + NIDEC_SERVO_LAG_FRAMES)
  assert learned_state(ci.CC) == before
  # A new interface is the startup boundary, not a live-toggle washout timer.
  restarted, restarted_provider = settled(car, mode=0, factor=43.)
  assert learned_state(restarted.CC) == before
  step(restarted)
  assert learned_state(restarted.CC) != before
  assert max(restarted.CC.speed_factors.values()) == 16.
  assert any("wind_factor" in entry for entry in restarted_provider.persisted)
