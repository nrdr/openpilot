import numpy as np

from openpilot.common.parameterized import parameterized

from cereal import car, log
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.nissan.values import CAR as NISSAN
from opendbc.car.gm.values import CAR as GM
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_pid import (
  LatControlPID,
  NRDR_CLARITY_SR_CURVE_BP,
  NRDR_CLARITY_SR_CURVE_V,
  NRDR_SR_CURVE_BY_FP,
)
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.controls.lib.latcontrol_angle import LatControlAngle
from openpilot.selfdrive.locationd.helpers import Pose
from openpilot.common.mock.generators import generate_livePose
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces


class TestLatControl:

  def test_nrdr_steer_ratio_curves_are_well_formed(self):
    for breakpoints, values in NRDR_SR_CURVE_BY_FP.values():
      assert len(breakpoints) == len(values)
      assert all(left < right for left, right in zip(breakpoints[:-1], breakpoints[1:], strict=True))
      assert all(left >= right for left, right in zip(values[:-1], values[1:], strict=True))

  def test_nrdr_clarity_monotonic_learned_curve_restores_original_tail(self):
    assert NRDR_CLARITY_SR_CURVE_BP == [
      0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5,
      62.5, 67.5, 70., 75., 80., 85., 90., 100., 140., 200., 300., 450.,
    ]
    assert NRDR_CLARITY_SR_CURVE_V == [
      19.680, 19.680, 19.680, 19.680, 19.344, 19.344, 19.307, 19.151, 18.406, 18.406,
      18.406, 18.087, 17.999, 17.999, 17.710, 17.604, 17.222, 16.706, 16.308, 16.093333333333334,
      15.940, 15.400, 14.300, 13.400, 12.720,
    ]

    # The 70-90 degree transition must remain monotonic and rejoin the old
    # 70-100 degree segment at its exact interpolated 90 degree value.
    assert np.interp(70., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 17.604
    assert np.interp(90., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 16.093333333333334
    assert np.interp(100., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 15.940

  @parameterized.expand([
    (HONDA.HONDA_CLARITY, "HONDA_CLARITY"),
    (HONDA.HONDA_CRV_5G, "HONDA_CRV_5G"),
    (HONDA.HONDA_CIVIC_BOSCH, "HONDA_CIVIC_BOSCH"),
    (HONDA.HONDA_CIVIC, "HONDA_CIVIC"),
    (HONDA.HONDA_CIVIC_BOSCH_DIESEL, None),
  ])
  def test_nrdr_steer_ratio_curve_is_fingerprint_scoped(self, car_name, expected_fingerprint):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)

    controller = LatControlPID(CP.as_reader(), convert_to_capnp(CP_SP).as_reader(), CI, DT_CTRL)

    if expected_fingerprint is None:
      assert controller.sr_curve is None
    else:
      assert str(CP.carFingerprint) == expected_fingerprint
      assert controller.sr_curve is not None

  @parameterized.expand([(HONDA.HONDA_CIVIC, LatControlPID), (TOYOTA.TOYOTA_RAV4, LatControlTorque),
                         (NISSAN.NISSAN_LEAF, LatControlAngle), (GM.CHEVROLET_BOLT_EUV, LatControlTorque)])
  def test_saturation(self, car_name, controller):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)
    sunnypilot_interfaces.setup_interfaces(CI)
    CP_SP = convert_to_capnp(CP_SP)
    VM = VehicleModel(CP)

    controller = controller(CP.as_reader(), CP_SP.as_reader(), CI, DT_CTRL)

    CS = car.CarState.new_message()
    CS.vEgo = 30
    CS.steeringPressed = False

    params = log.LiveParametersData.new_message()

    lp = generate_livePose()
    pose = Pose.from_live_pose(lp.livePose)

    # Saturate for curvature limited and controller limited
    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 0, pose, True, 0.2)
    assert lac_log.saturated

    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 0, pose, False, 0.2)
    assert not lac_log.saturated

    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 1, pose, False, 0.2)
    assert lac_log.saturated
