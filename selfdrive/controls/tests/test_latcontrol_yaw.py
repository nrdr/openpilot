import numpy as np
import pytest

from cereal import car, log
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from openpilot.common.mock.generators import generate_livePose
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_yaw import (
  FRICTION,
  FRICTION_THRESHOLD,
  KI,
  KP,
  LAT_ACCEL_FACTOR,
  LOW_SPEED_X,
  LOW_SPEED_Y,
  LatControlYaw,
  friction_compensation,
  low_speed_factor,
  use_yaw_controller,
)
from openpilot.selfdrive.locationd.helpers import Pose
from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt


class ExplodingVehicleModel:
  def __getattribute__(self, name):
    raise AssertionError(f"LatControlYaw accessed VehicleModel.{name}")


def build_controller():
  CarInterface = interfaces[HONDA.HONDA_CIVIC]
  CP = CarInterface.get_non_essential_params(HONDA.HONDA_CIVIC)
  CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CIVIC)
  CI = CarInterface(CP, CP_SP)
  controller = LatControlYaw(CP.as_reader(), convert_to_capnp(CP_SP).as_reader(), CI, DT_CTRL)
  return controller, CP


def build_pose(yaw_rate: float, yaw_rate_std: float = 0.01):
  lp = generate_livePose()
  lp.livePose.angularVelocityDevice.z = yaw_rate
  lp.livePose.angularVelocityDevice.zStd = yaw_rate_std
  return Pose.from_live_pose(lp.livePose)


def build_car_state(v_ego: float):
  CS = car.CarState.new_message()
  CS.vEgo = v_ego
  CS.steeringPressed = False
  return CS


class TestLatControlYaw:
  def test_initial_tune_is_the_requested_baseline(self):
    assert (KP, KI, LAT_ACCEL_FACTOR) == (0.30, 0.10, 3.5)
    assert (FRICTION, FRICTION_THRESHOLD) == (0.5, 0.3)
    assert LOW_SPEED_X == [0.0, 10.0, 20.0, 30.0]
    assert LOW_SPEED_Y == [15.0, 13.0, 10.0, 5.0]

  def test_only_nidec_civic_is_selected(self):
    assert use_yaw_controller(HONDA.HONDA_CIVIC)
    assert not use_yaw_controller(HONDA.HONDA_CIVIC_BOSCH)
    assert not use_yaw_controller(HONDA.HONDA_CLARITY)

  def test_generic_force_torque_toggle_cannot_replace_yaw_controller(self):
    controller, CP = build_controller()
    controls_ext = ControlsExt.__new__(ControlsExt)
    controls_ext.CP = CP.as_reader()

    # LatControlYaw returns before the generic EnforceTorqueControl path reads
    # Params or tries to construct a legacy torque controller.
    assert controls_ext.initialize_lateral_control(controller, None, DT_CTRL) is controller

  @pytest.mark.parametrize(("speed", "factor"), zip(LOW_SPEED_X, LOW_SPEED_Y, strict=True))
  def test_low_speed_curve(self, speed, factor):
    assert low_speed_factor(speed) == factor ** 2

  def test_friction_matches_historical_high_friction_shape(self):
    assert friction_compensation(-1.0) == -FRICTION
    assert friction_compensation(-FRICTION_THRESHOLD) == -FRICTION
    assert friction_compensation(0.0) == 0.0
    assert friction_compensation(FRICTION_THRESHOLD) == FRICTION
    assert friction_compensation(1.0) == FRICTION

  def test_matching_yaw_has_no_feedback_error_and_never_reads_sr_model(self):
    controller, _ = build_controller()
    CS = build_car_state(10.0)
    params = log.LiveParametersData.new_message()
    desired_curvature = 0.01
    pose = build_pose(desired_curvature * CS.vEgo)

    torque, _, state = controller.update(
      True, CS, ExplodingVehicleModel(), params, False,
      desired_curvature, pose, False, 0.0,
    )

    assert state.error == pytest.approx(0.0, abs=1e-7)
    assert state.p == pytest.approx(0.0, abs=1e-7)
    assert state.f == pytest.approx(1.0 / LAT_ACCEL_FACTOR, abs=1e-6)
    assert torque == pytest.approx(-state.f, abs=1e-6)

  def test_raw_lateral_accel_error_drives_friction(self):
    controller, _ = build_controller()
    CS = build_car_state(10.0)
    params = log.LiveParametersData.new_message()

    _, _, state = controller.update(
      True, CS, ExplodingVehicleModel(), params, False,
      0.01, build_pose(0.0), False, 0.0,
    )

    assert state.actualLateralAccel == 0.0
    assert state.f == pytest.approx(1.0 / LAT_ACCEL_FACTOR + FRICTION, abs=1e-6)
    assert state.error > 0.0

  def test_standstill_prepositions_without_steer_ratio(self):
    controller, _ = build_controller()
    CS = build_car_state(0.0)
    params = log.LiveParametersData.new_message()

    torque, _, state = controller.update(
      True, CS, ExplodingVehicleModel(), params, False,
      0.01, build_pose(0.0), False, 0.0,
    )

    assert torque < 0.0
    assert state.p > 0.0
    assert state.i == 0.0

  def test_missing_pose_uses_feedforward_only(self):
    controller, _ = build_controller()
    CS = build_car_state(10.0)
    params = log.LiveParametersData.new_message()

    _, _, state = controller.update(
      True, CS, ExplodingVehicleModel(), params, False,
      0.01, None, False, 0.0,
    )

    assert state.error == 0.0
    assert state.p == 0.0
    assert state.i == 0.0
    assert state.f == pytest.approx(1.0 / LAT_ACCEL_FACTOR, abs=1e-6)

  def test_inactive_output_is_zero(self):
    controller, _ = build_controller()
    CS = build_car_state(10.0)
    params = log.LiveParametersData.new_message()

    torque, angle, state = controller.update(
      False, CS, ExplodingVehicleModel(), params, False,
      0.01, build_pose(0.0), False, 0.0,
    )

    assert (torque, angle, state.active) == (0.0, 0.0, False)
    assert np.isfinite(torque)
