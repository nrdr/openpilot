import math
import struct
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.selfdrive.locationd.helpers import Pose, PoseCalibrator, gate_calibrated_pose_angular_velocity
from openpilot.nrdr.features.lateral.interpolated_torque_pif import (
  ClassicTorqueCandidate,
  InterpolatedTorquePifSettings,
  InterpolatedTorquePifSettingsLatch,
  LegacyTorquePid,
  convex_torque_pif_blend,
  maybe_blend_interpolated_torque_pif,
  resolve_interpolated_torque_pif_settings,
  select_classic_torque_measurement,
  should_run_pif_tune_learner,
  supports_interpolated_torque_pif,
)


class Settings:
  def __init__(self, **values):
    self.values = values

  def get(self, key):
    return self.values.get(str(key))


class FixedGeometry:
  def __init__(self, measured_curvature):
    self.measured = measured_curvature
    self.measured_calls = 0

  def measured_curvature(self, VM, measured_angle_deg, speed, roll, angle_offset_deg):
    self.measured_calls += 1
    return self.measured

  @staticmethod
  def curvature_deadzone(VM, measured_angle_deg, deadzone_deg, speed, angle_offset_deg):
    assert deadzone_deg == 0.0
    return 0.0


def _pose(yaw_rate=0.0, valid=True):
  return SimpleNamespace(
    angular_velocity=SimpleNamespace(z=yaw_rate),
    angular_velocity_valid=valid,
  )


def _device_motion(**overrides):
  def measurement(z=0.0, valid=True):
    return SimpleNamespace(x=0.0, y=0.0, z=z, xStd=0.01, yStd=0.01, zStd=0.01, valid=valid)

  values = {
    "orientationNED": measurement(valid=True),
    "velocityDevice": measurement(valid=True),
    "accelerationDevice": measurement(valid=True),
    "angularVelocityDevice": measurement(z=0.08, valid=True),
    "inputsOK": True,
    "posenetOK": True,
    "sensorsOK": True,
  }
  values.update(overrides)
  return SimpleNamespace(**values)


def _settings(**overrides):
  values = {
    "NrdrInterpolatedTorquePifBlend": True,
    "NrdrInterpolatedTorqueShare": 50,
    "NrdrInterpolatedTorqueLatAccelFactor": 5.0,
    "NrdrInterpolatedTorqueFriction": 0.5,
  }
  values.update(overrides)
  return Settings(**values)


def _car_params(kind="pid", fingerprint="HONDA_CLARITY", brand="honda"):
  return SimpleNamespace(
    brand=brand,
    carFingerprint=fingerprint,
    lateralTuning=SimpleNamespace(which=lambda: kind),
  )


def _modified_eps(enabled=True):
  return SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value if enabled else 0)


def test_feature_support_requires_modified_eps_honda_pid_or_clarity_hybrid():
  assert supports_interpolated_torque_pif(_car_params(), _modified_eps())
  assert supports_interpolated_torque_pif(_car_params(kind="torque"), _modified_eps())
  assert not supports_interpolated_torque_pif(_car_params(kind="angle"), _modified_eps())
  assert not supports_interpolated_torque_pif(_car_params(kind="torque", fingerprint="HONDA_CIVIC"), _modified_eps())
  assert not supports_interpolated_torque_pif(_car_params(), _modified_eps(False))
  assert not supports_interpolated_torque_pif(_car_params(brand="toyota"), _modified_eps())


def test_pose_manual_constructor_fails_closed_without_source_validity():
  measurement = SimpleNamespace()
  assert not Pose(measurement, measurement, measurement, measurement).angular_velocity_valid


@pytest.mark.parametrize("invalid_field", ("angular_velocity", "inputs", "posenet", "sensors"))
def test_pose_preserves_device_motion_yaw_source_validity(invalid_field):
  device_motion = _device_motion()
  if invalid_field == "angular_velocity":
    device_motion.angularVelocityDevice.valid = False
  else:
    setattr(device_motion, f"{invalid_field}OK", False)

  assert not Pose.from_device_motion(device_motion).angular_velocity_valid


def test_pose_calibrator_requires_valid_extrinsics_for_calibrated_yaw():
  raw_pose = Pose.from_device_motion(_device_motion())
  calibrator = PoseCalibrator()

  assert raw_pose.angular_velocity_valid
  assert not calibrator.build_calibrated_pose(raw_pose).angular_velocity_valid

  calibrator.calib_valid = True
  assert calibrator.build_calibrated_pose(raw_pose).angular_velocity_valid


def test_held_pose_validity_clears_on_calibration_loss_and_recovers_only_when_rebuilt():
  calibrator = PoseCalibrator()
  calibrator.calib_valid = True
  held_pose = calibrator.build_calibrated_pose(Pose.from_device_motion(_device_motion()))
  assert held_pose.angular_velocity_valid

  gate_calibrated_pose_angular_velocity(held_pose, service_valid=True, calibration_valid=False)
  assert not held_pose.angular_velocity_valid

  # One-way gating prevents an old finite value from becoming valid again.
  gate_calibrated_pose_angular_velocity(held_pose, service_valid=True, calibration_valid=True)
  assert not held_pose.angular_velocity_valid

  rebuilt_pose = calibrator.build_calibrated_pose(Pose.from_device_motion(_device_motion()))
  gate_calibrated_pose_angular_velocity(rebuilt_pose, service_valid=True, calibration_valid=True)
  assert rebuilt_pose.angular_velocity_valid


def test_settings_are_bounded_and_master_is_gated_by_support():
  settings = resolve_interpolated_torque_pif_settings(_settings(
    NrdrInterpolatedTorqueShare=150,
    NrdrInterpolatedTorqueLatAccelFactor=0,
    NrdrInterpolatedTorqueFriction=2,
  ), supported=False)

  assert not settings.enabled
  assert settings.torque_share == 1.0
  assert settings.lat_accel_factor == 0.1
  assert settings.friction == 1.0


def test_settings_latch_replaces_the_whole_tuple_only_while_inactive():
  latch = InterpolatedTorquePifSettingsLatch(
    resolve_interpolated_torque_pif_settings(_settings(), supported=True),
  )
  changed = _settings(
    NrdrInterpolatedTorquePifBlend=False,
    NrdrInterpolatedTorqueShare=80,
    NrdrInterpolatedTorqueLatAccelFactor=7.0,
    NrdrInterpolatedTorqueFriction=0.2,
  )

  engaged = latch.update(changed, supported=True, active=True)
  assert engaged == InterpolatedTorquePifSettings(True, 0.5, 5.0, 0.5)

  inactive = latch.update(changed, supported=True, active=False)
  assert inactive == InterpolatedTorquePifSettings(False, 0.8, 7.0, 0.2)


@pytest.mark.parametrize("share,expected", ((0.0, 0.25), (0.25, 0.125), (1.0, -0.25)))
def test_convex_blend_has_exact_endpoints_and_complementary_share(share, expected):
  assert convex_torque_pif_blend(0.25, -0.25, share) == pytest.approx(expected)


def test_convex_blend_clamps_share_and_final_actuator_request():
  assert convex_torque_pif_blend(0.25, -0.25, -1.0) == pytest.approx(0.25)
  assert convex_torque_pif_blend(0.25, -0.25, 2.0) == pytest.approx(-0.25)
  assert convex_torque_pif_blend(2.0, 2.0, 0.5, steer_max=1.0) == pytest.approx(1.0)


def test_convex_endpoints_ignore_nan_from_zero_weight_candidate_and_preserve_signed_zero():
  pif_endpoint = convex_torque_pif_blend(-0.0, float("nan"), 0.0)
  torque_endpoint = convex_torque_pif_blend(float("nan"), 0.25, 1.0)
  torque_signed_zero = convex_torque_pif_blend(float("nan"), -0.0, 1.0)

  assert struct.pack("!d", pif_endpoint) == struct.pack("!d", -0.0)
  assert torque_endpoint == 0.25
  assert struct.pack("!d", torque_signed_zero) == struct.pack("!d", -0.0)


@pytest.mark.parametrize("pif_output", (-0.0, 0.12345678901234568, -0.9876543210987654))
def test_master_off_returns_current_pif_bits_and_never_evaluates_classic(pif_output):
  def forbidden_candidate():
    raise AssertionError("classic torque candidate was evaluated while master was off")

  output, classic_result = maybe_blend_interpolated_torque_pif(
    pif_output,
    InterpolatedTorquePifSettings(enabled=False),
    forbidden_candidate,
  )

  assert struct.pack("!d", output) == struct.pack("!d", pif_output)
  assert classic_result is None


@pytest.mark.parametrize("pif_output", (-0.0, 0.12345678901234568, -0.9876543210987654))
def test_invalid_required_yaw_returns_current_pif_bits(pif_output):
  fallback = SimpleNamespace(output=float("nan"), yaw_feedback_valid=False)

  output, classic_result = maybe_blend_interpolated_torque_pif(
    pif_output,
    InterpolatedTorquePifSettings(enabled=True),
    lambda: fallback,
  )

  assert struct.pack("!d", output) == struct.pack("!d", pif_output)
  assert classic_result is fallback


def test_pif_learner_runs_normally_while_off_and_pauses_while_blend_is_effective():
  assert should_run_pif_tune_learner(True, InterpolatedTorquePifSettings(enabled=False))
  assert not should_run_pif_tune_learner(True, InterpolatedTorquePifSettings(enabled=True))
  assert not should_run_pif_tune_learner(False, InterpolatedTorquePifSettings(enabled=False))


@pytest.mark.parametrize("speed,expected_curvature,expected_source,expected_weight", (
  (1.0, 0.01, "angle_low_speed", 0.0),
  (2.0, 0.01, "angle_low_speed", 0.0),
  (3.5, 0.02, "angle_yaw_blend", 0.5),
  (5.0, 0.03, "yaw", 1.0),
  (10.0, 0.03, "yaw", 1.0),
))
def test_f13_yaw_measurement_transition_is_exact(speed, expected_curvature, expected_source, expected_weight):
  measurement = select_classic_torque_measurement(lambda: 0.01, speed, _pose(yaw_rate=speed * 0.03))

  assert measurement.actual_curvature == pytest.approx(expected_curvature)
  assert measurement.source == expected_source
  assert measurement.yaw_feedback_weight == pytest.approx(expected_weight)
  assert measurement.yaw_feedback_valid
  assert measurement.fallback_reason == ""


@pytest.mark.parametrize("pose,reason", (
  (None, "pose_unavailable"),
  (_pose(yaw_rate=0.2, valid=False), "pose_invalid_or_stale"),
  (_pose(yaw_rate=float("nan")), "yaw_nonfinite"),
  (SimpleNamespace(angular_velocity_valid=True), "yaw_unavailable"),
))
@pytest.mark.parametrize("speed,expected_weight", ((3.5, 0.5), (5.0, 1.0), (10.0, 1.0)))
def test_invalid_yaw_returns_unavailable_without_reading_angle(pose, reason, speed, expected_weight):
  def forbidden_angle_curvature():
    raise AssertionError("unavailable required yaw touched steer-ratio geometry")

  measurement = select_classic_torque_measurement(forbidden_angle_curvature, speed, pose)

  assert math.isnan(measurement.actual_curvature)
  assert measurement.source == "yaw_unavailable"
  assert measurement.yaw_feedback_weight == pytest.approx(expected_weight)
  assert not measurement.yaw_feedback_valid
  assert measurement.fallback_reason == reason


def test_low_speed_angle_path_does_not_require_or_read_yaw():
  measurement = select_classic_torque_measurement(
    lambda: 0.0123, 2.0, _pose(yaw_rate=float("nan"), valid=False),
  )

  assert measurement.actual_curvature == pytest.approx(0.0123)
  assert measurement.source == "angle_low_speed"
  assert measurement.fallback_reason == ""


@pytest.mark.parametrize("speed", (5.0, 10.0, 30.0))
def test_valid_high_speed_yaw_path_never_reads_angle_geometry(speed):
  def forbidden_angle_curvature():
    raise AssertionError("valid high-speed yaw feedback touched steer-ratio geometry")

  measurement = select_classic_torque_measurement(
    forbidden_angle_curvature, speed, _pose(yaw_rate=speed * 0.03),
  )

  assert measurement.actual_curvature == pytest.approx(0.03)
  assert measurement.source == "yaw"


def test_f13_normal_path_golden_vector_uses_y17_and_direct_friction():
  candidate = ClassicTorqueCandidate(dt=0.01)
  geometry = FixedGeometry(measured_curvature=0.008)
  CS = SimpleNamespace(vEgo=10.0, steeringAngleDeg=20.0, steeringPressed=False)
  vehicle_params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  settings = InterpolatedTorquePifSettings(True, 0.5, 5.0, 0.5)

  result = candidate.update(
    CS,
    object(),
    vehicle_params,
    False,
    0.01,
    _pose(yaw_rate=0.08),
    geometry,
    settings,
  )

  assert geometry.measured_calls == 0
  assert result.desired_lateral_accel == pytest.approx(1.0)
  assert result.actual_lateral_accel == pytest.approx(0.8)
  assert result.error == pytest.approx(0.1556)
  assert result.f == pytest.approx(0.2 + (0.2 / 0.3) * 0.5)
  assert result.p == pytest.approx(0.0778)
  assert result.i == pytest.approx(0.0001556)
  assert result.output == pytest.approx(-(result.p + result.i + result.f))
  assert result.measurement_source == "yaw"
  assert result.yaw_feedback_weight == 1.0
  assert result.yaw_feedback_valid
  assert result.yaw_feedback_fallback_reason == ""


def test_valid_high_speed_yaw_candidate_is_invariant_to_selected_steer_ratio():
  CS = SimpleNamespace(vEgo=10.0, steeringAngleDeg=20.0, steeringPressed=False)
  vehicle_params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  settings = InterpolatedTorquePifSettings(True, 0.5, 5.0, 0.5)

  left = ClassicTorqueCandidate(dt=0.01).update(
    CS, object(), vehicle_params, False, 0.01, _pose(yaw_rate=0.08),
    FixedGeometry(measured_curvature=-0.25), settings,
  )
  right = ClassicTorqueCandidate(dt=0.01).update(
    CS, object(), vehicle_params, False, 0.01, _pose(yaw_rate=0.08),
    FixedGeometry(measured_curvature=0.25), settings,
  )

  assert left.actual_curvature == pytest.approx(0.008)
  assert right.actual_curvature == pytest.approx(0.008)
  assert left.output == pytest.approx(right.output)
  assert left.error == pytest.approx(right.error)
  assert left.f == pytest.approx(right.f)


def test_invalid_high_speed_yaw_holds_classic_state_and_valid_recovery_is_sr_invariant():
  CS = SimpleNamespace(vEgo=10.0, steeringAngleDeg=20.0, steeringPressed=False)
  vehicle_params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  settings = InterpolatedTorquePifSettings(True, 0.5, 5.0, 0.0)
  recovered = ClassicTorqueCandidate(dt=0.01)
  uninterrupted = ClassicTorqueCandidate(dt=0.01)
  valid_pose = _pose(yaw_rate=0.008)

  for candidate in (recovered, uninterrupted):
    candidate.update(
      CS, object(), vehicle_params, False, 0.001, valid_pose,
      FixedGeometry(measured_curvature=0.02), settings,
    )
  state_before_unavailable = (
    recovered.pid.p, recovered.pid.i, recovered.pid.d, recovered.pid.f, recovered.pid.control,
  )
  unavailable_geometry = FixedGeometry(measured_curvature=0.05)

  unavailable = recovered.update(
    CS, object(), vehicle_params, False, 0.001, _pose(yaw_rate=0.008, valid=False),
    unavailable_geometry, settings,
  )
  assert unavailable.measurement_source == "yaw_unavailable"
  assert math.isnan(unavailable.output)
  assert unavailable_geometry.measured_calls == 0
  assert (recovered.pid.p, recovered.pid.i, recovered.pid.d, recovered.pid.f, recovered.pid.control) == state_before_unavailable

  recovered_result = recovered.update(
    CS, object(), vehicle_params, False, 0.001, valid_pose,
    FixedGeometry(measured_curvature=0.5), settings,
  )
  uninterrupted_result = uninterrupted.update(
    CS, object(), vehicle_params, False, 0.001, valid_pose,
    FixedGeometry(measured_curvature=-0.5), settings,
  )

  assert recovered_result.measurement_source == "yaw"
  assert recovered_result.i == pytest.approx(uninterrupted_result.i)
  assert recovered_result.output == pytest.approx(uninterrupted_result.output)


def test_friction_is_independent_of_lateral_acceleration_factor_and_clamps_at_slider():
  assert ClassicTorqueCandidate._friction(0.5, 0.0, 0.5) == pytest.approx(0.5)
  assert ClassicTorqueCandidate._friction(-0.5, 0.0, 0.5) == pytest.approx(-0.5)
  assert ClassicTorqueCandidate._friction(0.2, 0.1, 0.5) == pytest.approx(1.0 / 6.0)


def test_classic_pid_state_resets_on_disengagement_boundary():
  pid = LegacyTorquePid(dt=0.01, steer_max=1.0)
  pid.update(0.5, 0.0, freeze_integrator=False)
  assert pid.i > 0.0

  pid.reset()

  assert pid.i == 0.0
  assert pid.control == 0.0


@pytest.mark.parametrize("initial_i,error,feedforward,expected_i", (
  (-0.5, 1.0, 2.0, -0.499),
  (0.5, -1.0, -2.0, 0.499),
))
def test_f13_anti_windup_allows_opposite_integral_to_unwind_at_saturation(
  initial_i, error, feedforward, expected_i,
):
  pid = LegacyTorquePid(dt=0.01, steer_max=1.0)
  pid.i = initial_i

  pid.update(error, feedforward, freeze_integrator=False)

  assert pid.i == pytest.approx(expected_i)


@pytest.mark.parametrize("initial_i,error,feedforward", (
  (0.5, 1.0, 2.0),
  (-0.5, -1.0, -2.0),
))
def test_f13_anti_windup_blocks_same_sign_integral_at_saturation(initial_i, error, feedforward):
  pid = LegacyTorquePid(dt=0.01, steer_max=1.0)
  pid.i = initial_i

  pid.update(error, feedforward, freeze_integrator=False)

  assert pid.i == initial_i
