import math
import struct
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.constants import CV
from openpilot.sunnypilot.nrdr.interpolated_torque import (
  FRICTION_DEFAULT,
  InterpolatedTorqueSettings,
  LegacyTorqueController,
  LegacyPIDController,
  blend_commands,
  is_interpolated_torque_pif_supported,
  maybe_blend_interpolated_torque_pif,
  resolve_interpolated_torque_pif_settings,
  select_classic_torque_measurement,
  speed_banded_friction,
  settings_from_params,
)
from openpilot.sunnypilot.nrdr.latcontrol_pid import NrdrLatControlPID


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})

  def get(self, key, **_kwargs):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.values.get(key, False))


class FakeLiveParams:
  def __init__(self, values=None):
    self.snapshot = FakeParams(values)


def _cp(brand="honda", fingerprint="HONDA_CLARITY", tuning="pid"):
  return SimpleNamespace(
    brand=brand,
    carFingerprint=fingerprint,
    lateralTuning=SimpleNamespace(which=lambda: tuning),
  )


def _cp_sp(modified=True):
  flags = HondaFlagsSP.EPS_MODIFIED.value if modified else 0
  return SimpleNamespace(flags=flags)


def test_settings_defaults_bounds_and_friction_independence():
  defaults = settings_from_params(FakeParams())
  assert defaults == InterpolatedTorqueSettings(
    False, 0.5, 5.0, FRICTION_DEFAULT, FRICTION_DEFAULT, FRICTION_DEFAULT,
  )
  assert defaults.friction == defaults.friction_low

  bounded = settings_from_params(FakeParams({
    "NrdrInterpolatedTorquePifBlend": True,
    "NrdrInterpolatedTorqueShare": 200,
    "NrdrInterpolatedTorqueLatAccelFactor": 0.0,
    "NrdrInterpolatedTorqueFriction": 5.0,
    "NrdrInterpolatedTorqueFrictionStandard": -1.0,
    "NrdrInterpolatedTorqueFrictionHighway": 0.75,
  }))
  assert bounded == InterpolatedTorqueSettings(True, 1.0, 0.1, 1.0, 0.0, 0.75)
  assert resolve_interpolated_torque_pif_settings(FakeParams({
    "NrdrInterpolatedTorquePifBlend": True,
  }), supported=False).enabled is False


@pytest.mark.parametrize(("speed_mph", "expected"), [
  (-1.0, 0.10),
  (24.0, 0.10),
  (24.5, 0.20),
  (25.0, 0.30),
  (25.5, 0.40),
  (26.0, 0.50),
  (49.0, 0.50),
  (49.5, 0.60),
  (50.0, 0.70),
  (50.5, 0.80),
  (51.0, 0.90),
  (80.0, 0.90),
])
def test_speed_banded_friction_plateaus_and_one_mph_handoffs(speed_mph, expected):
  assert speed_banded_friction(speed_mph * CV.MPH_TO_MS, 0.10, 0.50, 0.90) == pytest.approx(expected)


@pytest.mark.parametrize("speed", [float("nan"), float("inf"), -float("inf")])
def test_speed_banded_friction_nonfinite_speed_fails_safe_to_low(speed):
  assert speed_banded_friction(speed, 0.10, 0.50, 0.90) == 0.10


@pytest.mark.parametrize("speed", [-1e9, 0.0, 25.0 * CV.MPH_TO_MS, 1e9, float("nan"), float("inf")])
def test_all_equal_speed_banded_friction_returns_legacy_value_bit_exact(speed):
  legacy = -0.0
  selected = speed_banded_friction(speed, legacy, legacy, legacy)
  assert struct.pack("!d", selected) == struct.pack("!d", legacy)


@pytest.mark.parametrize(("CP", "CP_SP", "expected"), [
  (_cp(), _cp_sp(), True),
  (_cp(tuning="torque"), _cp_sp(), True),
  (_cp(fingerprint="HONDA_CIVIC", tuning="torque"), _cp_sp(), False),
  (_cp(), _cp_sp(False), False),
  (_cp(brand="toyota"), _cp_sp(), False),
  (_cp(), None, False),
])
def test_support_is_modified_eps_honda_pid_or_clarity_hybrid_only(CP, CP_SP, expected):
  assert is_interpolated_torque_pif_supported(CP, CP_SP) is expected


def test_convex_blend_preserves_endpoints_and_bounds_final_command():
  assert blend_commands(0.2, -0.6, 0.0) == pytest.approx(0.2)
  assert blend_commands(0.2, -0.6, 1.0) == pytest.approx(-0.6)
  assert blend_commands(0.2, -0.6, 0.25) == pytest.approx(0.0)
  assert blend_commands(4.0, 2.0, 0.5) == 1.0
  assert blend_commands(-4.0, -2.0, 0.5) == -1.0

  pif_endpoint = blend_commands(-0.0, float("nan"), 0.0)
  torque_endpoint = blend_commands(float("nan"), -0.0, 1.0)
  assert math.isfinite(pif_endpoint) and math.copysign(1.0, pif_endpoint) == -1.0
  assert math.isfinite(torque_endpoint) and math.copysign(1.0, torque_endpoint) == -1.0


def _candidate_result(*, output=-0.6, yaw_feedback_valid=True):
  return SimpleNamespace(
    output=output,
    yaw_feedback_valid=yaw_feedback_valid,
    measurement_source="yaw" if yaw_feedback_valid else "yaw_unavailable",
  )


def test_blend_wrapper_is_lazy_off_and_returns_exact_pif_when_required_yaw_is_unavailable():
  pif_output = -0.0

  def forbidden_candidate():
    raise AssertionError("classic candidate was evaluated while master OFF")

  output, result = maybe_blend_interpolated_torque_pif(
    pif_output, InterpolatedTorqueSettings(enabled=False), forbidden_candidate,
  )
  assert struct.pack("!d", output) == struct.pack("!d", pif_output)
  assert result is None

  unavailable = _candidate_result(output=float("nan"), yaw_feedback_valid=False)
  output, result = maybe_blend_interpolated_torque_pif(
    pif_output, InterpolatedTorqueSettings(enabled=True), lambda: unavailable,
  )
  assert struct.pack("!d", output) == struct.pack("!d", pif_output)
  assert result is unavailable


class FakeResolver:
  def __init__(self, actual_curvature):
    self.actual_curvature = actual_curvature
    self.calc_calls = 0

  def calc_curvature(self, *_args):
    self.calc_calls += 1
    return self.actual_curvature

  def curvature_deadzone(self, *_args):
    raise AssertionError("the f13 useSteeringAngle=False path has zero deadzone")


def _cs(v_ego):
  return SimpleNamespace(vEgo=v_ego, aEgo=0.0, steeringAngleDeg=0.0, steeringPressed=False)


def _pose(yaw_rate, valid=True):
  return SimpleNamespace(
    angular_velocity=SimpleNamespace(yaw=yaw_rate, z=yaw_rate),
    angular_velocity_valid=valid,
  )


def test_f13_normal_path_math_sign_and_direct_friction():
  controller = LegacyTorqueController(0.01)
  CS = _cs(10.0)
  vehicle_params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  settings = InterpolatedTorqueSettings(True, 0.5, 5.0, 0.5, 0.5, 0.5)
  resolver = FakeResolver(99.0)

  result = controller.update(
    CS, object(), vehicle_params, False, 0.01, _pose(0.08), resolver, settings,
  )

  # f13: low-speed factor is 17^2 at 10 m/s. Error and base FF are
  # divided by LAF; the direct friction term is not.
  setpoint = 1.0 + 17.0 ** 2 * 0.01
  measurement = 0.8 + 17.0 ** 2 * 0.008
  torque_error = (setpoint - measurement) / 5.0
  direct_friction = 0.5 * (0.2 / 0.3)
  expected_internal = 0.5 * torque_error + 0.1 * 0.01 * torque_error + 1.0 / 5.0 + direct_friction
  assert result.output == pytest.approx(-expected_internal)
  assert resolver.calc_calls == 0, "valid yaw feedback above 5 m/s must not inspect steer-ratio geometry"
  assert result.actual_curvature == pytest.approx(0.008)
  assert result.measurement_source == "yaw"
  assert result.yaw_feedback_weight == 1.0
  assert result.yaw_feedback_valid
  assert result.yaw_feedback_fallback_reason == ""

  assert controller._direct_friction(1.0, 0.0, 0.5) == pytest.approx(0.5)
  assert controller._direct_friction(-1.0, 0.0, 0.5) == pytest.approx(-0.5)


@pytest.mark.parametrize(("speed_mph", "expected_friction"), [
  (24.0, 0.10),
  (25.0, 0.30),
  (26.0, 0.50),
  (49.0, 0.50),
  (50.0, 0.70),
  (51.0, 0.90),
])
def test_legacy_torque_controller_uses_speed_banded_direct_friction(speed_mph, expected_friction):
  v_ego = speed_mph * CV.MPH_TO_MS
  controller = LegacyTorqueController(0.01)
  settings = InterpolatedTorqueSettings(True, 0.5, 5.0, 0.10, 0.50, 0.90)

  result = controller.update(
    _cs(v_ego),
    object(),
    SimpleNamespace(roll=0.0, angleOffsetDeg=0.0),
    False,
    1.0 / v_ego ** 2,
    _pose(0.4 / v_ego),
    FakeResolver(99.0),
    settings,
  )

  assert result.f == pytest.approx(1.0 / settings.lat_accel_factor + expected_friction)


def test_curvature_feedback_uses_angle_low_speed_and_blends_from_two_to_five_mps():
  resolver = FakeResolver(0.006)

  low_speed = select_classic_torque_measurement(resolver.calc_curvature, 2.0, _pose(8.0))
  assert low_speed.actual_curvature == pytest.approx(0.006)
  assert low_speed.source == "angle_low_speed"
  assert low_speed.yaw_feedback_weight == 0.0
  assert low_speed.yaw_feedback_valid

  blended = select_classic_torque_measurement(resolver.calc_curvature, 3.5, _pose(0.035))
  assert blended.actual_curvature == pytest.approx(0.008)
  assert blended.source == "angle_yaw_blend"
  assert blended.yaw_feedback_weight == pytest.approx(0.5)
  assert blended.yaw_feedback_valid is True


@pytest.mark.parametrize(("pose", "reason"), [
  (None, "pose_unavailable"),
  (_pose(0.08, valid=False), "pose_invalid_or_stale"),
  (SimpleNamespace(angular_velocity_valid=True), "yaw_unavailable"),
  (_pose(float("nan")), "yaw_nonfinite"),
  (_pose(float("inf")), "yaw_nonfinite"),
])
def test_missing_invalid_stale_or_nonfinite_required_yaw_skips_angle_and_is_unavailable(pose, reason):
  resolver = FakeResolver(0.0123)

  feedback = select_classic_torque_measurement(resolver.calc_curvature, 10.0, pose)

  assert math.isnan(feedback.actual_curvature)
  assert feedback.source == "yaw_unavailable"
  assert feedback.yaw_feedback_weight == 1.0
  assert feedback.yaw_feedback_valid is False
  assert feedback.fallback_reason == reason
  assert resolver.calc_calls == 0


@pytest.mark.parametrize(("speed", "expected_weight"), [
  (2.1, pytest.approx(1.0 / 30.0)),
  (3.5, pytest.approx(0.5)),
  (5.0, pytest.approx(1.0)),
])
def test_invalid_yaw_never_substitutes_angle_anywhere_yaw_is_requested(speed, expected_weight):
  resolver = FakeResolver(0.0123)
  feedback = select_classic_torque_measurement(resolver.calc_curvature, speed, _pose(0.08, valid=False))

  assert math.isnan(feedback.actual_curvature)
  assert feedback.source == "yaw_unavailable"
  assert feedback.yaw_feedback_weight == expected_weight
  assert not feedback.yaw_feedback_valid
  assert resolver.calc_calls == 0


def test_valid_high_speed_yaw_is_invariant_to_steer_ratio_mode():
  settings = InterpolatedTorqueSettings(True, 0.5, 5.0, 0.5, 0.5, 0.5)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  outputs = []
  for angle_curvature in (-10.0, 10.0):
    controller = LegacyTorqueController(0.01)
    resolver = FakeResolver(angle_curvature)
    outputs.append(controller.update(
      _cs(10.0), object(), params, False, 0.01, _pose(0.08), resolver, settings,
    ).output)
    assert resolver.calc_calls == 0

  assert outputs[0] == pytest.approx(outputs[1])


def test_invalid_high_speed_yaw_holds_all_classic_pid_state_and_recovery_is_sr_invariant():
  settings = InterpolatedTorqueSettings(True, 0.5, 5.0, 0.5, 0.5, 0.5)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  controllers = [LegacyTorqueController(0.01), LegacyTorqueController(0.01)]
  resolvers = [FakeResolver(-0.05), FakeResolver(0.05)]

  for controller, resolver in zip(controllers, resolvers, strict=True):
    controller.update(_cs(10.0), object(), params, False, 0.01, _pose(0.08), resolver, settings)
  integral_before_fallback = [controller.pid.i for controller in controllers]

  pid_state_before = [(controller.pid.p, controller.pid.i, controller.pid.d, controller.pid.f, controller.pid.control)
                      for controller in controllers]
  unavailable_results = [
    controller.update(_cs(10.0), object(), params, False, 0.01, _pose(0.08, valid=False), resolver, settings)
    for controller, resolver in zip(controllers, resolvers, strict=True)
  ]
  assert [controller.pid.i for controller in controllers] == pytest.approx(integral_before_fallback)
  assert [(controller.pid.p, controller.pid.i, controller.pid.d, controller.pid.f, controller.pid.control)
          for controller in controllers] == pid_state_before
  assert all(result.measurement_source == "yaw_unavailable" for result in unavailable_results)
  assert all(math.isnan(result.output) and math.isnan(result.error) for result in unavailable_results)
  assert all(resolver.calc_calls == 0 for resolver in resolvers)

  recovered_outputs = [
    controller.update(_cs(10.0), object(), params, False, 0.01, _pose(0.08), resolver, settings).output
    for controller, resolver in zip(controllers, resolvers, strict=True)
  ]
  assert recovered_outputs[0] == pytest.approx(recovered_outputs[1])
  assert controllers[0].pid.i == pytest.approx(controllers[1].pid.i)


def test_f13_pid_allows_integral_to_unwind_while_output_remains_saturated():
  pid = LegacyPIDController(0.5, 0.1, k_f=1.0, pos_limit=1.0, neg_limit=-1.0, rate=100.0)

  pid.i = -0.5
  assert pid.update(1.0, feedforward=2.0) == 1.0
  assert pid.i == pytest.approx(-0.499)

  pid.i = 0.5
  assert pid.update(-1.0, feedforward=-2.0) == -1.0
  assert pid.i == pytest.approx(0.499)

  pid.i = 0.5
  pid.update(1.0, feedforward=2.0)
  assert pid.i == pytest.approx(0.5), "same-sign integral must not wind farther into saturation"


class ResetSpy:
  def __init__(self):
    self.reset_count = 0

  def reset(self):
    self.reset_count += 1


def _latch_controller(values, classic=None):
  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.params = FakeLiveParams(values)
  controller._interpolated_torque_supported = True
  controller._interpolated_torque_controller = classic
  controller._interpolated_torque_settings = InterpolatedTorqueSettings()
  controller._interpolated_torque_pif_effective = False
  controller._interpolated_torque_was_active = False
  controller.dt = 0.01
  controller.steer_max = 1.0
  return controller


def test_all_six_values_latch_for_engagement_then_classic_resets_inactive():
  classic = ResetSpy()
  controller = _latch_controller({
    "NrdrInterpolatedTorquePifBlend": True,
    "NrdrInterpolatedTorqueShare": 25,
    "NrdrInterpolatedTorqueLatAccelFactor": 6.0,
    "NrdrInterpolatedTorqueFriction": 0.4,
    "NrdrInterpolatedTorqueFrictionStandard": 0.5,
    "NrdrInterpolatedTorqueFrictionHighway": 0.6,
  }, classic)

  controller._update_interpolated_torque_latch(True)
  assert controller.interpolated_torque_pif_effective
  assert controller._interpolated_torque_settings == InterpolatedTorqueSettings(True, 0.25, 6.0, 0.4, 0.5, 0.6)

  controller.params.snapshot.values.update({
    "NrdrInterpolatedTorquePifBlend": False,
    "NrdrInterpolatedTorqueShare": 99,
    "NrdrInterpolatedTorqueLatAccelFactor": 9.0,
    "NrdrInterpolatedTorqueFriction": 0.9,
    "NrdrInterpolatedTorqueFrictionStandard": 0.8,
    "NrdrInterpolatedTorqueFrictionHighway": 0.7,
  })
  controller._update_interpolated_torque_latch(True)
  assert controller.interpolated_torque_pif_effective
  assert controller._interpolated_torque_settings == InterpolatedTorqueSettings(True, 0.25, 6.0, 0.4, 0.5, 0.6)

  controller._update_interpolated_torque_latch(False)
  assert not controller.interpolated_torque_pif_effective
  assert classic.reset_count >= 2


def test_master_off_keeps_classic_candidate_inactive_and_resets_its_state():
  classic = ResetSpy()
  controller = _latch_controller({"NrdrInterpolatedTorquePifBlend": False}, classic)
  controller._update_interpolated_torque_latch(True)
  assert not controller.interpolated_torque_pif_effective
  assert classic.reset_count == 1


def test_blend_pauses_learner_samples_but_keeps_learner_maintenance_running():
  class LearnerSpy:
    def __init__(self):
      self.calls = []

    def learn(self, *args):
      self.calls.append(args)

  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.is_eps_modified = True
  controller._interpolated_torque_pif_effective = True
  controller.stiction_enabled = False
  controller.stiction = SimpleNamespace(freeze_integrator=False)
  controller.tune_learner = LearnerSpy()
  controller.frame = 123
  CS = SimpleNamespace(vEgo=10.0, steeringRateDeg=0.5)

  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 1
  assert controller.tune_learner.calls[-1][5] is False

  controller._interpolated_torque_pif_effective = False
  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 2
  assert controller.tune_learner.calls[-1][5] is True
