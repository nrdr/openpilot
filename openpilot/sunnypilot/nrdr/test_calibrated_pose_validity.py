from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.locationd.helpers import (
  Measurement,
  Pose,
  PoseCalibrator,
  gate_calibrated_pose_angular_velocity,
)


def _xyz(valid=True, z=0.0):
  return SimpleNamespace(x=0.0, y=0.0, z=z, xStd=0.0, yStd=0.0, zStd=0.0, valid=valid)


def _device_motion(*, angular_valid=True, inputs_ok=True, posenet_ok=True, sensors_ok=True, yaw_rate=0.08):
  return SimpleNamespace(
    orientationNED=_xyz(),
    velocityDevice=_xyz(),
    accelerationDevice=_xyz(),
    angularVelocityDevice=_xyz(angular_valid, yaw_rate),
    inputsOK=inputs_ok,
    posenetOK=posenet_ok,
    sensorsOK=sensors_ok,
  )


@pytest.mark.parametrize("invalid_field", ["angular_valid", "inputs_ok", "posenet_ok", "sensors_ok"])
def test_pose_keeps_device_motion_angular_velocity_quality(invalid_field):
  values = {
    "angular_valid": True,
    "inputs_ok": True,
    "posenet_ok": True,
    "sensors_ok": True,
  }
  values[invalid_field] = False
  assert not Pose.from_device_motion(_device_motion(**values)).angular_velocity_valid

  values[invalid_field] = True
  assert Pose.from_device_motion(_device_motion(**values)).angular_velocity_valid


def test_pose_calibrator_requires_valid_extrinsics_and_preserves_source_quality():
  calibrator = PoseCalibrator()
  source = Pose.from_device_motion(_device_motion())

  assert not calibrator.build_calibrated_pose(source).angular_velocity_valid

  calibrator.calib_valid = True
  assert calibrator.build_calibrated_pose(source).angular_velocity_valid

  source.angular_velocity_valid = False
  assert not calibrator.build_calibrated_pose(source).angular_velocity_valid


def test_direct_pose_constructor_fails_closed_unless_validity_is_explicit():
  measurement = Measurement(np.zeros(3), np.zeros(3))
  assert not Pose(measurement, measurement, measurement, measurement).angular_velocity_valid
  assert Pose(
    measurement, measurement, measurement, measurement, angular_velocity_valid=True,
  ).angular_velocity_valid


def test_held_pose_validity_gate_is_one_way_until_a_new_pose_replaces_it():
  measurement = Measurement(np.zeros(3), np.zeros(3))
  pose = Pose(measurement, measurement, measurement, measurement, angular_velocity_valid=True)

  gate_calibrated_pose_angular_velocity(pose, service_valid=True, calibration_valid=True)
  assert pose.angular_velocity_valid

  gate_calibrated_pose_angular_velocity(pose, service_valid=False, calibration_valid=True)
  assert not pose.angular_velocity_valid

  gate_calibrated_pose_angular_velocity(pose, service_valid=True, calibration_valid=True)
  assert not pose.angular_velocity_valid


class FakeSubMaster:
  def __init__(self):
    self.updated = {"extrinsicsCalibration": False, "deviceMotion": False}
    self.device_motion_healthy = True
    self.device_motion = _device_motion()

  def update(self, _timeout):
    pass

  def __getitem__(self, service):
    assert service == "deviceMotion"
    return self.device_motion

  def all_checks(self, services):
    assert services == ["deviceMotion"]
    return self.device_motion_healthy


def test_controlsd_holds_healthy_20hz_pose_but_invalidates_stale_pose_until_replaced():
  from openpilot.selfdrive.controls.controlsd import Controls

  controls = Controls.__new__(Controls)
  controls.sm = FakeSubMaster()
  controls.pose_calibrator = PoseCalibrator()
  controls.pose_calibrator.calib_valid = True
  controls.calibrated_pose = controls.pose_calibrator.build_calibrated_pose(
    Pose.from_device_motion(_device_motion()),
  )

  # A healthy held 20 Hz sample stays valid on intervening 100 Hz controls frames.
  Controls.update(controls)
  assert controls.calibrated_pose.angular_velocity_valid

  controls.sm.device_motion_healthy = False
  Controls.update(controls)
  assert not controls.calibrated_pose.angular_velocity_valid

  # A stale sample cannot become valid again merely because service health
  # recovers. A newly received, source-valid sample is required.
  controls.sm.device_motion_healthy = True
  Controls.update(controls)
  assert not controls.calibrated_pose.angular_velocity_valid

  controls.sm.updated["deviceMotion"] = True
  Controls.update(controls)
  assert controls.calibrated_pose.angular_velocity_valid


def test_controlsd_invalidates_held_pose_when_calibration_becomes_invalid():
  from openpilot.selfdrive.controls.controlsd import Controls

  controls = Controls.__new__(Controls)
  controls.sm = FakeSubMaster()
  controls.pose_calibrator = PoseCalibrator()
  controls.pose_calibrator.calib_valid = True
  controls.calibrated_pose = controls.pose_calibrator.build_calibrated_pose(
    Pose.from_device_motion(_device_motion()),
  )

  controls.pose_calibrator.calib_valid = False
  Controls.update(controls)
  assert not controls.calibrated_pose.angular_velocity_valid

  controls.pose_calibrator.calib_valid = True
  Controls.update(controls)
  assert not controls.calibrated_pose.angular_velocity_valid

  controls.sm.updated["deviceMotion"] = True
  Controls.update(controls)
  assert controls.calibrated_pose.angular_velocity_valid
