"""Exercise the real PID update with in-memory settings, never device Params."""
from types import MappingProxyType, SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral import latcontrol_pid
from openpilot.nrdr.features.lateral.interpolated_torque_pif import ClassicTorqueCandidate, ClassicTorqueCandidateResult
from openpilot.nrdr.params.snapshots import ParamSnapshot


class NoOpLearner:
  def __init__(self, *args):
    pass

  def apply(self, *args):
    return 0.0

  def learn(self, *args):
    pass


class VehicleModel:
  sR = 15.38

  def get_steer_from_curvature(self, curvature, speed, roll):
    return curvature * self.sR


def make_snapshot(generation, **changes):
  values = {
    "NrdrSteerRatioMode": 0,
    "NrdrSteerRatioManualCenter": 15.38, "NrdrSteerRatioManualFinal": 15.38,
    "NrdrInterpolatedTorquePifBlend": True, "NrdrInterpolatedTorqueShare": 10,
    "NrdrInterpolatedTorqueLatAccelFactor": 10.0,
    "NrdrInterpolatedTorqueFriction": 1.0, "NrdrInterpolatedTorqueFrictionStandard": 1.0,
    "NrdrInterpolatedTorqueFrictionHighway": 1.0,
    "HondaCenterScale": 0.0, "NrdrLatRateDamping": 0,
    **changes,
  }
  return ParamSnapshot(generation, MappingProxyType(values))


def make_live_pid(monkeypatch, live, mock_candidate=True):
  monkeypatch.setattr(latcontrol_pid, "get_live_params", lambda: live)
  monkeypatch.setattr(latcontrol_pid, "TuneLearner", NoOpLearner)
  tuning = SimpleNamespace(kpBP=[0.0], kpV=[0.03], kiBP=[0.0], kiV=[0.0], kf=0.00001)
  cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC", carFw=[], steerRatio=15.38,
                       steerLimitTimer=0.8, lateralTuning=SimpleNamespace(pid=tuning, which=lambda: "pid"))
  cp_sp = SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value)
  ci = SimpleNamespace(get_steer_feedforward_function=lambda: lambda angle, speed: angle * speed ** 2)
  controller = latcontrol_pid.NrdrLatControlPID(cp, cp_sp, ci, 0.01)
  candidate = ClassicTorqueCandidateResult(0.8, 0.0, 0.0, 0.0, 0.0, 0.0,
                                          0.0, 0.0, 0.0, "yaw", 1.0, True, "")
  if mock_candidate:
    monkeypatch.setattr(controller.classic_torque_candidate, "update", lambda *args: candidate)
  cs = SimpleNamespace(vEgo=25.0, steeringAngleDeg=0.0, steeringRateDeg=0.0,
                       steeringPressed=False, steeringTorque=0.0, leftBlinker=False, rightBlinker=False)
  vehicle = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0, valid=True,
                            angleOffsetValid=True, steerRatioValid=True, stiffnessFactorValid=True)

  def update(active=True, pose=None):
    return controller.update(active, cs, VehicleModel(), vehicle, False, -0.001, pose, False, 0.2)[0]

  return controller, live, update


@pytest.fixture
def live_pid(monkeypatch):
  return make_live_pid(monkeypatch, SimpleNamespace(snapshot=make_snapshot(1)))


def test_blend_share_and_pid_scale_change_during_continuous_engagement(live_pid):
  controller, live, update = live_pid
  first = update()
  assert controller.interpolated_torque_pif_settings.torque_share == 0.1
  live.snapshot = make_snapshot(2, NrdrInterpolatedTorqueShare=5, LatPScaleHighway=120)
  second = update()
  assert controller.interpolated_torque_pif_settings.torque_share == 0.05
  assert controller.p_scales[2] == 1.2
  assert second != first
  assert controller.frame == 1  # Two active updates; no inactive/reset call.


def test_pid_uses_the_frame_snapshot_even_if_worker_publishes_mid_frame(live_pid):
  controller, live, update = live_pid
  captured = live.snapshot
  controller.set_live_tuning_snapshot(captured)
  live.snapshot = make_snapshot(2, NrdrInterpolatedTorqueShare=5)
  update()
  assert controller.interpolated_torque_pif_settings.torque_share == 0.1
  controller.set_live_tuning_snapshot(live.snapshot)
  update()
  assert controller.interpolated_torque_pif_settings.torque_share == 0.05


def test_blend_can_be_disabled_and_reenabled_without_disengaging(live_pid):
  controller, live, update = live_pid
  update()
  live.snapshot = make_snapshot(2, NrdrInterpolatedTorquePifBlend=False)
  update()
  assert not controller.interpolated_torque_pif_enabled
  assert controller.last_classic_torque_result is None
  live.snapshot = make_snapshot(3, NrdrInterpolatedTorquePifBlend=True)
  update()
  assert controller.interpolated_torque_pif_enabled
  assert controller.last_classic_torque_result.output == 0.8


def test_highway_friction_changes_real_yaw_branch_without_resetting_integral(live_pid):
  controller, live, update = live_pid
  controller.classic_torque_candidate = ClassicTorqueCandidate(0.01)
  controller.classic_torque_candidate.pid.i = 0.02
  pose = SimpleNamespace(angular_velocity_valid=True, angular_velocity=SimpleNamespace(z=-0.02))
  update(pose=pose)
  first = controller.last_classic_torque_result
  live.snapshot = make_snapshot(2, NrdrInterpolatedTorqueFrictionHighway=0.3)
  update(pose=pose)
  second = controller.last_classic_torque_result
  settings = controller.interpolated_torque_pif_settings
  assert settings.torque_share == 0.1
  assert settings.friction_low == settings.friction_standard == 1.0
  assert settings.friction_highway == 0.3
  assert 0.019 < second.i <= first.i < 0.02  # Evolves normally; not reset on the edit.
  assert second.output < first.output
  assert first.yaw_feedback_valid and second.yaw_feedback_valid


@pytest.mark.parametrize("sign", (-1.0, 1.0))
def test_highway_unwind_does_not_freeze_remaining_angle_error(live_pid, monkeypatch, sign):
  controller, live, update = live_pid
  live.snapshot = make_snapshot(2, NrdrInterpolatedTorquePifBlend=False)
  controller.pid._k_i = ([0.0], [0.2])
  controller.pid.i = sign * 0.1
  controller.previous_desired_angle = sign * 5.0
  monkeypatch.setattr(controller, "_desired_angles", lambda *args: (sign * 4.99, sign * 4.99))
  update()
  assert controller.phase_direction < 0.0
  assert controller.pid.i == pytest.approx(sign * (0.1 + 0.2 * 0.01 * 4.99))


def test_live_zero_i_clears_correction_and_reenable_starts_fresh(live_pid):
  controller, live, update = live_pid
  controller.pid._k_i = ([0.0], [0.2])
  controller.pid.i = 0.25
  live.snapshot = make_snapshot(2, LatIScaleHighway=0, NrdrInterpolatedTorquePifBlend=False)
  update()
  assert controller.pid.i == 0.0
  live.snapshot = make_snapshot(3, LatIScaleHighway=100, NrdrInterpolatedTorquePifBlend=False)
  update()
  assert 0.0 < controller.pid.i < 0.01


def test_scheduled_i_is_not_multiplied_twice_at_the_output(live_pid):
  controller, _, _ = live_pid
  controller.pid.i = 0.25
  controller.i_scales = [0.2, 1.35, 2.0]
  for speed in (5.0, 15.0, 27.0):
    cs = SimpleNamespace(vEgo=speed, steeringRateDeg=0.0, steeringAngleDeg=0.0)
    assert controller._scaled_pid_output(cs, 0.0, 0.0, 0.0) == pytest.approx(0.25)


def test_disengagement_clears_pid_integral_before_reengagement(live_pid):
  controller, _, update = live_pid
  controller.pid.i = 0.3
  assert update(active=False) == 0.0
  assert controller.pid.i == 0.0
