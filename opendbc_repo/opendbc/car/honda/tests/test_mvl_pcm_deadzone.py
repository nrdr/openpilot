"""Optional acceleration-feedback experiment; no vehicle or host Params I/O."""
import math
from dataclasses import replace

import pytest

from opendbc.car import structs
from opendbc.car.honda import mvl_longitudinal as mvl
from opendbc.car.honda.tests.test_mvl_priority import build, command, drive_state, state
from opendbc.car.honda.values import CAR, HONDA_BOSCH, HondaFlags


@pytest.mark.parametrize("maximum", [0.0, 0.02, 0.05, 0.10])
@pytest.mark.parametrize("speed,fraction", [(-1., 0.), (0., 0.), (2.3, 0.), (5.65, .5), (9., 1.), (35., 1.)])
def test_continuous_deadzone(maximum, speed, fraction):
  width = maximum * fraction
  for error in (-.3, -width - 1e-8, -width, -.5 * width, 0., .5 * width, width, width + 1e-8, .3):
    expected = math.copysign(max(abs(error) - width, 0.), error)
    actual = mvl.acceleration_deadzone(error, speed, maximum)
    assert actual == pytest.approx(expected, abs=1e-16)
    assert abs(actual) <= abs(error) + 1e-16


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_feedback_is_not_hidden(value):
  actual = mvl.acceleration_deadzone(value, 20., .05)
  assert math.isnan(actual) if math.isnan(value) else actual == value
  assert mvl.acceleration_deadzone(.02, value, .05) == .02


@pytest.mark.parametrize("value", [None, True, False, "0.05", b"5", -1, 2, 5, 10, .03, .1000001,
                                    float("nan"), float("inf"), [], {}])
def test_invalid_config_falls_back_to_exact_off(value):
  ci, config, _ = build(deadzone=value)
  baseline, reference, _ = build()
  assert ci.CC.mvl_pcm_deadzone == 0.
  for tick in range(160):
    for item in (ci, baseline):
      drive_state(item.CS, tick + 500)
    cc = command(tick).as_reader()
    a = ci.CC.update(cc, structs.CarControlSP(), ci.CS, tick * 10_000_000)
    b = baseline.CC.update(cc, structs.CarControlSP(), baseline.CS, tick * 10_000_000)
    assert a[0].to_dict() == b[0].to_dict()
    assert a[1] == b[1]
    assert state(ci.CC) == state(baseline.CC)
  assert config.honda.provider.persisted == reference.honda.provider.persisted


@pytest.mark.parametrize("car", list(CAR))
def test_all_platforms_scope_and_output_isolation(car):
  for interceptor in (False,) if car in HONDA_BOSCH else (False, True):
    ci, _, _ = build(car, interceptor, deadzone=.10)
    eligible = car == CAR.HONDA_CIVIC and not interceptor
    assert ci.CC.mvl_pcm_deadzone == (.10 if eligible else 0.)
    if eligible:
      continue
    baseline, _, _ = build(car, interceptor)
    for tick in range(12):
      for item in (ci, baseline):
        drive_state(item.CS, tick + 500)
      cc = command(tick).as_reader()
      a = ci.CC.update(cc, structs.CarControlSP(), ci.CS, tick * 10_000_000)
      b = baseline.CC.update(cc, structs.CarControlSP(), baseline.CS, tick * 10_000_000)
      assert a[0].to_dict() == b[0].to_dict()
      assert a[1] == b[1]
      assert state(ci.CC) == state(baseline.CC)


@pytest.mark.parametrize("kwargs", [{"mvl": False}, {"stock": True}])
def test_legacy_and_stock_are_ineligible(kwargs):
  ci, _, _ = build(deadzone=.10, **kwargs)
  baseline, _, _ = build(**kwargs)
  assert ci.CC.mvl_pcm_deadzone == 0.
  for tick in range(100):
    for item in (ci, baseline):
      drive_state(item.CS, tick + 500)
    cc = command(tick).as_reader()
    a = ci.CC.update(cc, structs.CarControlSP(), ci.CS, tick * 10_000_000)
    b = baseline.CC.update(cc, structs.CarControlSP(), baseline.CS, tick * 10_000_000)
    assert a[0].to_dict() == b[0].to_dict()
    assert a[1] == b[1]


def test_inconsistent_hardware_flags_fail_closed():
  ci, _, _ = build(deadzone=.05)
  assert ci.CC.mvl_pcm_deadzone == .05
  ci.CP.flags = int(ci.CP.flags & ~HondaFlags.NIDEC)
  assert mvl.pcm_deadzone_config(ci.CP, ci.CP_SP, True, .05) == 0.
  ci.CP.flags = int(ci.CP.flags | HondaFlags.NIDEC | HondaFlags.BOSCH)
  assert mvl.pcm_deadzone_config(ci.CP, ci.CP_SP, True, .05) == 0.


def feedback_fixture(width=.05):
  ci, config, _ = build(deadzone=width)
  ci.CS.out.vEgo = 20.
  ci.CS.out.aEgo = .23
  ci.CC.nidec_pid.i = ci.CC.nidec_pid_factor = -.05
  cc = command(0)
  cc.actuators.accel = .20
  cc.orientationNED = [0., 0., 0.]
  return ci, config, cc


@pytest.mark.parametrize("reason", ["zero", "negative", "off", "stopping", "starting", "inactive", "launch", "gas", "brake",
                                      "aeb", "fcw", "previous_brake", "pending_brake", "applied_brake", "integral", "grade", "low_speed"])
def test_every_bypass_preserves_existing_update_skip_and_reset(reason):
  ci, _, cc = feedback_fixture()
  baseline, _, _ = feedback_fixture(0.)
  if reason == "zero":
    cc.actuators.accel = 0.
  elif reason == "negative":
    cc.actuators.accel = -1e-8
  elif reason in ("off", "stopping", "starting"):
    cc.actuators.longControlState = reason
  elif reason == "inactive":
    cc.longActive = False
  elif reason == "grade":
    cc.orientationNED = [0., -.04, 0.]
  for item in (ci, baseline):
    if reason == "launch":
      item.CC.launch_active = True
    elif reason in ("gas", "brake", "aeb", "fcw"):
      setattr(item.CS.out, {"gas": "gasPressed", "brake": "brakePressed", "aeb": "stockAeb", "fcw": "stockFcw"}[reason], True)
    elif reason in ("previous_brake", "pending_brake", "applied_brake"):
      setattr(item.CC, {"previous_brake": "apply_brake_last", "pending_brake": "brake_last", "applied_brake": "last_applied_brake"}[reason], 1)
    elif reason == "integral":
      item.CC.nidec_pid.i = item.CC.nidec_pid_factor = -.30
    elif reason == "low_speed":
      item.CS.out.vEgo = 2.3
  # prepare() alone leaves the chosen guard active; compare sustained bypass.
  calls = [[], []]
  for index, item in enumerate((ci, baseline)):
    original = item.CC.nidec_pid.update
    def record(*args, _original=original, _calls=calls[index], **kwargs):
      _calls.append(kwargs["error"])
      return _original(*args, **kwargs)
    item.CC.nidec_pid.update = record
  before = cc.to_dict()
  for _ in range(8):
    assert mvl.prepare(ci.CC, cc, ci.CS) == mvl.prepare(baseline.CC, cc, baseline.CS)
    assert state(ci.CC) == state(baseline.CC)
  assert calls[0] == calls[1]
  assert cc.to_dict() == before


@pytest.mark.parametrize("width", [.02, .05, .10])
@pytest.mark.parametrize("integral", [0., -.05, -.3, -4.])
def test_integral_history_is_not_reset_and_braking_correction_bypasses(width, integral):
  ci, _, cc = feedback_fixture(width)
  ci.CC.nidec_pid.i = ci.CC.nidec_pid_factor = integral
  ci.CS.out.aEgo = .20 + width / 2
  raw = cc.actuators.accel - ci.CS.out.aEgo
  expected = 0. if integral > -.20 else raw
  assert mvl.pcm_feedback_error(ci.CC, cc, ci.CS, 0.) == expected
  for _ in range(20):
    mvl.prepare(ci.CC, cc, ci.CS)
  if integral > -.20:
    assert ci.CC.nidec_pid.i == integral
  else:
    assert ci.CC.nidec_pid.i <= integral


def test_positive_in_band_error_can_hold_a_negative_integral():
  ci, _, cc = feedback_fixture()
  ci.CS.out.aEgo = .17
  for _ in range(20):
    mvl.prepare(ci.CC, cc, ci.CS)
  assert ci.CC.nidec_pid.i == -.05  # Deadzone also slows integral unwind; it is not a delay model.
  ci.CS.out.aEgo = .10
  mvl.prepare(ci.CC, cc, ci.CS)
  assert ci.CC.nidec_pid.i > -.05


def test_latched_config_and_actual_enabled_effect_without_request_mutation():
  ci, config, cc = feedback_fixture()
  baseline, _, _ = feedback_fixture(0.)
  changed = replace(config.honda, mvl_pcm_deadzone=.10)
  assert changed.mvl_pcm_deadzone == .10 and ci.CC.mvl_pcm_deadzone == .05
  before = cc.to_dict()
  a = ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, 0)
  b = baseline.CC.update(cc.as_reader(), structs.CarControlSP(), baseline.CS, 0)
  assert ci.CC.nidec_pid.i == -.05
  assert baseline.CC.nidec_pid.i < -.05
  assert a[0].accel != b[0].accel
  assert cc.to_dict() == before


def test_enabled_learning_persists_and_off_restart_uses_that_same_history():
  ci, config, cc = feedback_fixture()
  for tick in range(6200):
    ci.CS.out.aEgo = .23 + .12 * math.sin(tick / 200.)
    ci.CS.car_gas_available = True
    ci.CS.car_gas = 30. + 5. * math.sin(tick / 150.)
    ci.CS.engine_rpm = 1500
    # Enter and leave deceleration/stopping on both 50 Hz command phases.
    cc.actuators.accel = -.3 if 1000 <= tick % 2000 < 1101 else .2
    cc.actuators.longControlState = "stopping" if 1050 <= tick % 2000 < 1101 else "pid"
    ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, tick * 10_000_000)
  assert len(config.honda.provider.persisted) >= 2
  saved = {}
  for snapshot in config.honda.provider.persisted:
    assert all(math.isfinite(value) for value in snapshot.values())
    saved.update(snapshot)
  restored, restored_config, _ = build(saved=saved, deadzone=0.)
  baseline, baseline_config, _ = build(saved=saved)
  assert state(restored.CC) == state(baseline.CC)
  for tick in range(6200):
    for item in (restored, baseline):
      drive_state(item.CS, tick)
    request = command(tick).as_reader()
    a = restored.CC.update(request, structs.CarControlSP(), restored.CS, tick * 10_000_000)
    b = baseline.CC.update(request, structs.CarControlSP(), baseline.CS, tick * 10_000_000)
    assert a[0].to_dict() == b[0].to_dict()
    assert a[1] == b[1]
    assert state(restored.CC) == state(baseline.CC)
  assert restored_config.honda.provider.persisted == baseline_config.honda.provider.persisted
