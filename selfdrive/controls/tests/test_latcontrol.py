from itertools import pairwise

import numpy as np
from cereal import car, log
from opendbc.car.car_helpers import interfaces
from opendbc.car.gm.values import CAR as GM
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.nissan.values import CAR as NISSAN
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.mock.generators import generate_livePose
from openpilot.common.parameterized import parameterized
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_angle import LatControlAngle
from openpilot.selfdrive.controls.lib.latcontrol_pid import (
  NRDR_CIVIC_BOSCH_SR_CURVE_BP,
  NRDR_CIVIC_BOSCH_SR_CURVE_V,
  NRDR_CIVIC_NIDEC_LINEAR_BP,
  NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V,
  NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
  NRDR_CLARITY_SR_CURVE_BP,
  NRDR_CLARITY_SR_CURVE_V,
  NRDR_SR_CURVE_BY_FP,
  NRDR_VGR_INVERSE_BY_FP,
  LatControlPID,
)
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.locationd.helpers import Pose
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces


class TestLatControl:

  def test_nrdr_steer_ratio_curves_are_well_formed(self):
    for breakpoints, values in NRDR_SR_CURVE_BY_FP.values():
      assert len(breakpoints) == len(values)
      assert all(left < right for left, right in pairwise(breakpoints))
      assert all(value > 0.0 for value in values)

  def test_nrdr_clarity_raw_curve_fades_to_manufacturer_spec(self):
    assert NRDR_CLARITY_SR_CURVE_BP == [
      0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5,
      62.5, 67.5, 70., 75., 80., 85., 90., 450.,
    ]
    assert NRDR_CLARITY_SR_CURVE_V == [
      20.114, 20.114, 20.114, 20.052, 19.407, 19.398, 19.398, 19.240, 18.452, 18.250,
      18.250, 18.178, 17.940, 17.940, 17.625, 17.584, 16.824, 15.152, 13.480, 12.720, 12.720,
    ]

    assert np.interp(70., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 17.584
    assert np.interp(90., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 12.720
    assert np.interp(450., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 12.720

  def test_nrdr_civic_families_use_firmware_specific_curves(self):
    assert NRDR_CIVIC_BOSCH_SR_CURVE_BP == [
      0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5,
      62.5, 70., 75., 80., 85., 90., 400.,
    ]
    assert NRDR_CIVIC_BOSCH_SR_CURVE_V == [
      19.095, 19.095, 18.276, 16.335, 16.335, 16.335, 16.246, 15.291, 15.291, 14.675,
      14.393, 13.596, 13.596, 13.179438, 12.263, 11.346562, 10.930, 10.930,
    ]
    assert NRDR_SR_CURVE_BY_FP["HONDA_CIVIC_BOSCH"] == (
      NRDR_CIVIC_BOSCH_SR_CURVE_BP,
      NRDR_CIVIC_BOSCH_SR_CURVE_V,
    )
    assert NRDR_CIVIC_NIDEC_VGR_ANGLE_BP == [
      0.000, 3.125, 6.400, 9.524, 12.698, 15.748, 19.047, 22.222, 25.397, 31.746,
      47.243, 62.017, 76.336, 83.333, 86.363, 88.721, 91.728, 94.028, 97.013, 99.998,
      102.224, 105.187, 107.354, 110.295, 131.387, 152.173, 170.216, 188.812, 208.333, 596.023,
    ]
    assert NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V == [
      1.000, 1.000, 1.024, 1.016, 1.016, 1.008, 1.016, 1.016, 1.016, 1.016,
      1.008, 0.992, 0.977, 0.970, 0.970, 0.962, 0.962, 0.955, 0.955, 0.955,
      0.948, 0.948, 0.941, 0.941, 0.934, 0.928, 0.908, 0.895, 0.889, 0.848,
    ]
    assert "HONDA_CIVIC" not in NRDR_SR_CURVE_BY_FP
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_CIVIC"] == (
      NRDR_CIVIC_NIDEC_LINEAR_BP,
      NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
    )
    assert np.interp(70., NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V) == 13.596
    assert np.interp(90., NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V) == 10.930
    assert np.interp(400., NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V) == 10.930

    # The Nidec A-table is already cumulative/effective and contains a genuine
    # near-center rise. Do not integrate it or flatten it with a monotonic rule.
    assert max(NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V) == 1.024
    assert all(left < right for left, right in pairwise(NRDR_CIVIC_NIDEC_LINEAR_BP))
    np.testing.assert_allclose(
      NRDR_CIVIC_NIDEC_LINEAR_BP,
      np.divide(NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V),
      rtol=0.0,
      atol=1e-12,
    )
    assert np.isclose(np.interp(60., NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
                                NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V), 0.994184, atol=5e-7)
    assert np.isclose(np.interp(100., NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
                                NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V), 0.954994, atol=5e-7)
    assert np.isclose(np.interp(160., NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
                                NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V), 0.919324, atol=5e-7)
    assert np.isclose(np.interp(200., NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
                                NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V), 0.891561, atol=5e-7)

    # LINEAR_BP is the pre-solved inverse coordinate: each constant-ratio
    # model angle must map back to the real steering-wheel angle that produced it.
    for real_angle in (0., 45., 70., 90., 200., 400.):
      model_angle = np.interp(real_angle, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_LINEAR_BP)
      recovered_angle = np.interp(model_angle, NRDR_CIVIC_NIDEC_LINEAR_BP, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP)
      assert np.isclose(recovered_angle, real_angle, atol=1e-12)

  @parameterized.expand([
    (HONDA.HONDA_CLARITY, "HONDA_CLARITY", None),
    (HONDA.HONDA_CRV_5G, "HONDA_CRV_5G", None),
    (HONDA.HONDA_CIVIC_BOSCH, "HONDA_CIVIC_BOSCH", None),
    (HONDA.HONDA_CIVIC, None, "HONDA_CIVIC"),
    (HONDA.HONDA_CIVIC_BOSCH_DIESEL, None, None),
  ])
  def test_nrdr_steer_ratio_curve_is_fingerprint_scoped(self, car_name, expected_curve_fp, expected_inverse_fp):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)

    controller = LatControlPID(CP.as_reader(), convert_to_capnp(CP_SP).as_reader(), CI, DT_CTRL)

    expected_fp = expected_curve_fp or expected_inverse_fp
    if expected_fp is not None:
      assert str(CP.carFingerprint) == expected_fp
    assert (controller.sr_curve is not None) == (expected_curve_fp is not None)
    assert (controller.vgr_inverse is not None) == (expected_inverse_fp is not None)

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
