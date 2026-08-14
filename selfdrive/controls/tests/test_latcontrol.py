from itertools import pairwise

import numpy as np
import pytest
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
  NRDR_ACCORD_FINAL_SR,
  NRDR_ACCORD_LOCK_ANGLE,
  NRDR_ACCORD_TWO_POINT_SR_BP,
  NRDR_ACCORD_TWO_POINT_SR_V,
  NRDR_CIVIC_BOSCH_SR_CURVE_BP,
  NRDR_CIVIC_BOSCH_SR_CURVE_V,
  NRDR_CIVIC_BOSCH_CENTER_SR,
  NRDR_CIVIC_BOSCH_INNER_SR_BP,
  NRDR_CIVIC_BOSCH_INNER_SR_V,
  NRDR_CIVIC_BOSCH_VGR_SOURCE_ANGLE_BP,
  NRDR_CIVIC_BOSCH_VGR_SOURCE_REL_LOCAL,
  NRDR_CIVIC_BOSCH_VGR_LINEAR_BP,
  NRDR_CIVIC_FINAL_SR,
  NRDR_CIVIC_LOCK_ANGLE,
  NRDR_CIVIC_NIDEC_CENTER_SR,
  NRDR_CIVIC_NIDEC_EFFECTIVE_SR_V,
  NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR,
  NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_BP,
  NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V,
  NRDR_CIVIC_NIDEC_LINEAR_BP,
  NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V,
  NRDR_CIVIC_NIDEC_SOURCE_EFFECTIVE_SR_V,
  NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
  NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP,
  NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR,
  NRDR_CIVIC_TWO_POINT_SR_BP,
  NRDR_CIVIC_TWO_POINT_SR_V,
  NRDR_CLARITY_FINAL_SR,
  NRDR_CLARITY_CENTER_SR,
  NRDR_CLARITY_INNER_SR_BP,
  NRDR_CLARITY_INNER_SR_V,
  NRDR_CLARITY_LOCK_ANGLE,
  NRDR_CLARITY_SR_CURVE_BP,
  NRDR_CLARITY_SR_CURVE_V,
  NRDR_CLARITY_TWO_POINT_SR_BP,
  NRDR_CLARITY_TWO_POINT_SR_V,
  NRDR_CLARITY_VGR_SOURCE_ANGLE_BP,
  NRDR_CLARITY_VGR_SOURCE_REL_LOCAL,
  NRDR_CLARITY_VGR_LINEAR_BP,
  NRDR_CRV_5G_CENTER_SR,
  NRDR_CRV_5G_FINAL_SR,
  NRDR_CRV_5G_LOCK_ANGLE,
  NRDR_CRV_5G_SR_CURVE_BP,
  NRDR_CRV_5G_SR_CURVE_V,
  NRDR_CRV_5G_TWO_POINT_SR_BP,
  NRDR_CRV_5G_TWO_POINT_SR_V,
  NRDR_CRV_5G_VGR_LINEAR_BP,
  NRDR_INSIGHT_CENTER_SR,
  NRDR_INSIGHT_FINAL_SR,
  NRDR_INSIGHT_LOCK_ANGLE,
  NRDR_INSIGHT_BASE_ANGLE_BP,
  NRDR_INSIGHT_BASE_REL_EFFECTIVE_SR,
  NRDR_INSIGHT_VGR_ANGLE_BP,
  NRDR_INSIGHT_VGR_LINEAR_BP,
  NRDR_INSIGHT_VGR_REL_EFFECTIVE_SR_V,
  NRDR_INSIGHT_VGR_SOURCE_ANGLE_BP,
  NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL,
  NRDR_INSIGHT_TWO_POINT_SR_BP,
  NRDR_INSIGHT_TWO_POINT_SR_V,
  NRDR_SR_CURVE_BY_FP,
  NRDR_TWO_POINT_OUTER_FRACTION,
  NRDR_VGR_INVERSE_BY_FP,
  VGR_FIXED_FULL_ANGLE_DEG,
  VGR_LEARNED_FULL_ANGLE_DEG,
  _center_boost_scale,
  _freeze_integrator_during_unwind,
  _hybrid_vgr_desired_angles,
  _learned_vgr_weight,
  LatControlPID,
)
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.locationd.helpers import Pose
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  STEER_RATIO_ENDPOINT_PROFILES,
  STEER_RATIO_ENDPOINT_PROFILE_BY_FP,
)


class TestLatControl:

  def test_learned_vgr_is_limited_to_the_paramsd_observation_region(self):
    assert VGR_LEARNED_FULL_ANGLE_DEG == 45.0
    assert VGR_FIXED_FULL_ANGLE_DEG == 100.0
    assert _learned_vgr_weight(0.0) == 1.0
    assert _learned_vgr_weight(45.0) == 1.0
    assert _learned_vgr_weight(72.5) == pytest.approx(0.5)
    assert _learned_vgr_weight(100.0) == 0.0
    assert _learned_vgr_weight(450.0) == 0.0

  def test_hybrid_vgr_uses_learned_center_then_fixed_outer_anchor(self):
    identity_inverse = ([0.0, 600.0], [0.0, 600.0])

    # Inside 45 degrees, the learned path has full authority.
    no_offset, desired = _hybrid_vgr_desired_angles(
      30.0, 1.0, 18.0, 20.0, identity_inverse, identity_inverse, False,
    )
    assert no_offset == pytest.approx(30.0)
    assert desired == pytest.approx(31.0)

    # Above 100 degrees, two different learned anchors produce the same fixed
    # outer request for the same road-wheel demand.
    outer_requests = []
    for learned_sr in (17.0, 19.0):
      linear_des = 8.0 * learned_sr
      no_offset, _ = _hybrid_vgr_desired_angles(
        linear_des, 0.0, learned_sr, 20.0, identity_inverse, identity_inverse, False,
      )
      outer_requests.append(no_offset)
    np.testing.assert_allclose(outer_requests, [160.0, 160.0], rtol=0.0, atol=1e-12)

  def test_hybrid_vgr_applies_dewarped_offset_before_the_map(self):
    quickening_inverse = ([0.0, 100.0, 200.0], [0.0, 90.0, 160.0])
    no_offset, desired = _hybrid_vgr_desired_angles(
      30.0, 2.0, 18.0, 18.0, quickening_inverse, quickening_inverse, True,
    )
    assert no_offset == pytest.approx(np.interp(30.0, *quickening_inverse))
    assert desired == pytest.approx(np.interp(32.0, *quickening_inverse))

  def test_unwind_integrator_only_freezes_growth(self):
    # During unwind, same-sign error would grow the stored I magnitude.
    assert _freeze_integrator_during_unwind(-0.1, 0.05, 0.2)
    assert _freeze_integrator_during_unwind(-0.1, -0.05, -0.2)
    # Opposite-sign error must remain live so stale I can decay through zero.
    assert not _freeze_integrator_during_unwind(-0.1, 0.05, -0.2)
    assert not _freeze_integrator_during_unwind(-0.1, -0.05, 0.2)
    assert not _freeze_integrator_during_unwind(0.1, 0.05, 0.2)

  def test_center_boost_has_highway_support_and_smooth_speed_gate(self):
    min_speed = 50.0 * 0.44704
    assert _center_boost_scale(0.0, min_speed - 0.1, center_taper_high=1.0,
                               center_boost_min_speed_ms=min_speed) == 1.0
    assert _center_boost_scale(0.0, min_speed + 2.5 * 0.44704, center_taper_high=1.0,
                               center_boost_min_speed_ms=min_speed) == pytest.approx(1.5)
    assert _center_boost_scale(0.0, 100.0 * 0.44704, center_taper_high=1.0,
                               center_boost_min_speed_ms=min_speed) == 2.0
    assert _center_boost_scale(3.5, 100.0 * 0.44704, center_taper_high=1.0,
                               center_boost_threshold_deg=3.0,
                               center_boost_min_speed_ms=min_speed) == pytest.approx(1.5)
    assert _center_boost_scale(4.0, 100.0 * 0.44704, center_taper_high=1.0,
                               center_boost_threshold_deg=3.0,
                               center_boost_min_speed_ms=min_speed) == 1.0

  def test_nrdr_steer_ratio_curves_are_well_formed(self):
    assert NRDR_SR_CURVE_BY_FP == {
      "HONDA_CLARITY": (NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V),
      "HONDA_CIVIC": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
      "HONDA_CIVIC_BOSCH": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
      "HONDA_CIVIC_BOSCH_DIESEL": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
      "HONDA_ACCORD": (NRDR_ACCORD_TWO_POINT_SR_BP, NRDR_ACCORD_TWO_POINT_SR_V),
      "HONDA_CRV_5G": (NRDR_CRV_5G_TWO_POINT_SR_BP, NRDR_CRV_5G_TWO_POINT_SR_V),
      "HONDA_CRV_HYBRID": (NRDR_CRV_5G_TWO_POINT_SR_BP, NRDR_CRV_5G_TWO_POINT_SR_V),
      "HONDA_INSIGHT": (NRDR_INSIGHT_TWO_POINT_SR_BP, NRDR_INSIGHT_TWO_POINT_SR_V),
    }
    assert NRDR_CLARITY_TWO_POINT_SR_BP == [0.0, 250.0]
    assert NRDR_CLARITY_TWO_POINT_SR_V == [18.50, 12.72]
    assert np.interp(0.0, NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V) == 18.50
    assert np.interp(125.0, NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V) == pytest.approx(15.61)
    assert np.interp(250.0, NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V) == 12.72
    assert np.interp(450.0, NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V) == 12.72

    two_point_profiles = (
      (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V,
       NRDR_CIVIC_LOCK_ANGLE, 17.24, NRDR_CIVIC_FINAL_SR),
      (NRDR_ACCORD_TWO_POINT_SR_BP, NRDR_ACCORD_TWO_POINT_SR_V,
       NRDR_ACCORD_LOCK_ANGLE, 18.31, NRDR_ACCORD_FINAL_SR),
      (NRDR_CRV_5G_TWO_POINT_SR_BP, NRDR_CRV_5G_TWO_POINT_SR_V,
       NRDR_CRV_5G_LOCK_ANGLE, 17.94, NRDR_CRV_5G_FINAL_SR),
      (NRDR_INSIGHT_TWO_POINT_SR_BP, NRDR_INSIGHT_TWO_POINT_SR_V,
       NRDR_INSIGHT_LOCK_ANGLE, 16.82, NRDR_INSIGHT_FINAL_SR),
    )
    for breakpoints, values, lock_angle, center_sr, outer_sr in two_point_profiles:
      assert breakpoints[0] == 0.0
      assert breakpoints[1] / lock_angle == pytest.approx(NRDR_TWO_POINT_OUTER_FRACTION)
      assert values == [center_sr, outer_sr]
      assert np.interp(breakpoints[1], breakpoints, values) == outer_sr
      assert np.interp(lock_angle, breakpoints, values) == outer_sr

    assert set(STEER_RATIO_ENDPOINT_PROFILE_BY_FP) == set(NRDR_SR_CURVE_BY_FP)
    endpoint_params = []
    for profile in STEER_RATIO_ENDPOINT_PROFILES:
      endpoint_params.extend((profile.center_param, profile.outer_param))
      for fingerprint in profile.fingerprints:
        assert NRDR_SR_CURVE_BY_FP[fingerprint][1] == list(profile.default_values)
    assert len(endpoint_params) == len(set(endpoint_params))

    assert NRDR_CIVIC_TWO_POINT_SR_BP[1] == pytest.approx(230.2904564)
    assert NRDR_ACCORD_TWO_POINT_SR_BP[1] == pytest.approx(238.5892116)
    assert NRDR_CRV_5G_TWO_POINT_SR_BP[1] == pytest.approx(238.5892116)
    assert NRDR_INSIGHT_TWO_POINT_SR_BP[1] == pytest.approx(263.4854772)
    for breakpoints, values in (
        (NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V),
        (NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_SR_CURVE_V),
        (NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V),
    ):
      assert len(breakpoints) == len(values)
      assert all(left < right for left, right in pairwise(breakpoints))
      assert all(value > 0.0 for value in values)

  def test_nrdr_clarity_firmware_tail_reaches_spec_at_physical_lock(self):
    assert NRDR_CLARITY_INNER_SR_BP == [
      0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5,
      62.5, 67.5, 70.,
    ]
    assert NRDR_CLARITY_INNER_SR_V == [
      20.114, 20.114, 20.114, 20.052, 19.407, 19.398, 19.398, 19.240, 18.452, 18.250,
      18.250, 18.178, 17.940, 17.940, 17.625, 17.584,
    ]
    assert NRDR_CLARITY_VGR_SOURCE_ANGLE_BP == [
      0.000, 4.052, 8.104, 12.102, 16.201, 20.205, 24.299, 28.299, 32.296, 40.194,
      59.571, 78.095, 95.805, 104.440, 450.000,
    ]
    assert NRDR_CLARITY_VGR_SOURCE_REL_LOCAL == [
      1.000000, 1.000000, 1.000000, 1.000000, 0.999938, 0.998460, 0.995087, 0.989980,
      0.983193, 0.965501, 0.909060, 0.858900, 0.834355, 0.833325, 0.833325,
    ]

    assert np.interp(70., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == 17.584
    assert np.interp(90., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) > NRDR_CLARITY_FINAL_SR
    assert np.interp(NRDR_CLARITY_LOCK_ANGLE, NRDR_CLARITY_SR_CURVE_BP,
                     NRDR_CLARITY_SR_CURVE_V) == pytest.approx(NRDR_CLARITY_FINAL_SR)
    assert np.interp(450., NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V) == pytest.approx(NRDR_CLARITY_FINAL_SR)
    clarity_outer = [value for angle, value in zip(NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V, strict=True)
                     if angle >= 104.440]
    assert all(left >= right for left, right in pairwise(clarity_outer))

  def test_nrdr_civic_families_use_firmware_specific_curves(self):
    assert NRDR_CIVIC_BOSCH_INNER_SR_BP == [
      0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5,
      62.5, 70.,
    ]
    assert NRDR_CIVIC_BOSCH_INNER_SR_V == [
      19.095, 19.095, 18.276, 16.335, 16.335, 16.335, 16.246, 15.291, 15.291, 14.675,
      14.393, 13.596, 13.596,
    ]
    assert NRDR_CIVIC_BOSCH_VGR_SOURCE_ANGLE_BP[-2:] == [111.269, 450.000]
    assert NRDR_CIVIC_BOSCH_VGR_SOURCE_REL_LOCAL[-2:] == [0.829, 0.829]
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_CIVIC_BOSCH"] == (
      NRDR_CIVIC_BOSCH_VGR_LINEAR_BP,
      NRDR_CIVIC_BOSCH_SR_CURVE_BP,
      NRDR_CIVIC_BOSCH_CENTER_SR,
    )
    assert NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP == [
      0.000, 3.125, 6.400, 9.524, 12.698, 15.748, 19.047, 22.222, 25.397, 31.746,
      47.243, 62.017, 76.336, 83.333, 86.363, 88.721, 91.728, 94.028, 97.013, 99.998,
      102.224, 105.187, 107.354, 110.295, 131.387, 152.173, 170.216, 188.812, 208.333, 596.023,
    ]
    assert NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR == [
      1.000, 1.000, 1.024, 1.016, 1.016, 1.008, 1.016, 1.016, 1.016, 1.016,
      1.008, 0.992, 0.977, 0.970, 0.970, 0.962, 0.962, 0.955, 0.955, 0.955,
      0.948, 0.948, 0.941, 0.941, 0.934, 0.928, 0.908, 0.895, 0.889, 0.848,
    ]
    assert NRDR_SR_CURVE_BY_FP["HONDA_CIVIC"] == (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V)
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_CIVIC"] == (
      NRDR_CIVIC_NIDEC_LINEAR_BP,
      NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
      NRDR_CIVIC_NIDEC_CENTER_SR,
    )
    assert np.interp(70., NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V) == 13.596
    assert np.interp(90., NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V) > NRDR_CIVIC_FINAL_SR
    assert np.interp(NRDR_CIVIC_LOCK_ANGLE, NRDR_CIVIC_BOSCH_SR_CURVE_BP,
                     NRDR_CIVIC_BOSCH_SR_CURVE_V) == pytest.approx(NRDR_CIVIC_FINAL_SR)
    assert np.interp(NRDR_CIVIC_LOCK_ANGLE, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
                     NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V) * NRDR_CIVIC_NIDEC_CENTER_SR == pytest.approx(NRDR_CIVIC_FINAL_SR)

    # Only the low-angle overlay changes. The learned road-effective values hand
    # back to the original firmware-derived absolute curve at 9.524 degrees.
    assert NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR == 15.38
    assert NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_BP == [0.000, 3.125, 6.400, 9.524]
    np.testing.assert_allclose(
      NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V,
      [18.270, 18.270, 17.460, 15.62608],
      rtol=0.0,
      atol=1e-12,
    )
    assert NRDR_CIVIC_NIDEC_CENTER_SR == 18.270
    np.testing.assert_allclose(
      NRDR_CIVIC_NIDEC_SOURCE_EFFECTIVE_SR_V[:4],
      NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V,
      rtol=0.0,
      atol=1e-12,
    )
    np.testing.assert_allclose(
      NRDR_CIVIC_NIDEC_SOURCE_EFFECTIVE_SR_V[4:],
      np.multiply(NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR[4:], NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR),
      rtol=0.0,
      atol=1e-12,
    )
    assert all(left < right for left, right in pairwise(NRDR_CIVIC_NIDEC_LINEAR_BP))
    np.testing.assert_allclose(
      NRDR_CIVIC_NIDEC_LINEAR_BP,
      np.divide(NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V),
      rtol=0.0,
      atol=1e-12,
    )
    legacy_effective_sr = np.multiply(NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR,
                                      NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR)
    for angle in (60., 100., 160., 200.):
      assert np.isclose(
        np.interp(angle, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_EFFECTIVE_SR_V),
        np.interp(angle, NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP, legacy_effective_sr),
        atol=5e-7,
      )

    # LINEAR_BP is the pre-solved inverse coordinate: each constant-ratio
    # model angle must map back to the real steering-wheel angle that produced it.
    for real_angle in (0., 45., 70., 90., 200., NRDR_CIVIC_LOCK_ANGLE):
      model_angle = np.interp(real_angle, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_LINEAR_BP)
      recovered_angle = np.interp(model_angle, NRDR_CIVIC_NIDEC_LINEAR_BP, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP)
      assert np.isclose(recovered_angle, real_angle, atol=1e-12)

  def test_nrdr_insight_preserves_fixed_outer_curve(self):
    assert NRDR_INSIGHT_VGR_SOURCE_ANGLE_BP == [
      0.000, 3.721, 7.302, 10.972, 14.610, 18.228, 21.864, 25.517, 29.156, 36.296,
      53.978, 70.999, 87.308, 95.243, 450.000,
    ]
    assert NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL == [
      1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.998445, 0.995081, 0.989922,
      0.983180, 0.965570, 0.909063, 0.858696, 0.833564, 0.833141, 0.833141,
    ]
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_INSIGHT"] == (
      NRDR_INSIGHT_VGR_LINEAR_BP,
      NRDR_INSIGHT_VGR_ANGLE_BP,
      NRDR_INSIGHT_CENTER_SR,
    )
    assert NRDR_SR_CURVE_BY_FP["HONDA_INSIGHT"] == (NRDR_INSIGHT_TWO_POINT_SR_BP, NRDR_INSIGHT_TWO_POINT_SR_V)

    assert len(NRDR_INSIGHT_VGR_ANGLE_BP) == len(NRDR_INSIGHT_VGR_LINEAR_BP)
    assert len(NRDR_INSIGHT_VGR_ANGLE_BP) == len(NRDR_INSIGHT_VGR_REL_EFFECTIVE_SR_V)
    assert all(left < right for left, right in pairwise(NRDR_INSIGHT_VGR_ANGLE_BP))
    assert all(left < right for left, right in pairwise(NRDR_INSIGHT_VGR_LINEAR_BP))
    assert all(left >= right for left, right in pairwise(NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL))

    # The local curve is flat through 14.61 degrees, so the inverse is an exact
    # no-op there. It then gets progressively quicker and holds its local tail.
    for angle in (0., 3., 7., 10., 14.610):
      assert np.interp(angle, NRDR_INSIGHT_VGR_LINEAR_BP, NRDR_INSIGHT_VGR_ANGLE_BP) == pytest.approx(angle)
    assert NRDR_INSIGHT_VGR_LINEAR_BP[NRDR_INSIGHT_VGR_ANGLE_BP.index(95.243)] == pytest.approx(103.506417, abs=1e-6)
    assert np.interp(NRDR_INSIGHT_LOCK_ANGLE, NRDR_INSIGHT_VGR_ANGLE_BP,
                     NRDR_INSIGHT_VGR_REL_EFFECTIVE_SR_V) * NRDR_INSIGHT_CENTER_SR == pytest.approx(NRDR_INSIGHT_FINAL_SR)
    assert NRDR_INSIGHT_VGR_LINEAR_BP[-1] == pytest.approx(
      NRDR_INSIGHT_VGR_ANGLE_BP[-1] / (NRDR_INSIGHT_FINAL_SR / NRDR_INSIGHT_CENTER_SR), abs=1e-6,
    )

    # Guard the local-vs-effective distinction: pointwise division would put
    # the tail near 540 degrees and repeat the earlier Clarity conversion bug.
    assert 95.243 / NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL[-2] > 95.243 / np.interp(
      95.243, NRDR_INSIGHT_BASE_ANGLE_BP, NRDR_INSIGHT_BASE_REL_EFFECTIVE_SR,
    ) + 10.

    for real_angle in (0., 15., 45., 70., 90., 200., 400., NRDR_INSIGHT_LOCK_ANGLE):
      model_angle = np.interp(real_angle, NRDR_INSIGHT_VGR_ANGLE_BP, NRDR_INSIGHT_VGR_LINEAR_BP)
      recovered_angle = np.interp(model_angle, NRDR_INSIGHT_VGR_LINEAR_BP, NRDR_INSIGHT_VGR_ANGLE_BP)
      assert recovered_angle == pytest.approx(real_angle, abs=1e-12)

  def test_nrdr_crv_reaches_spec_at_physical_lock(self):
    assert np.interp(200., NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_SR_CURVE_V) == 14.60
    assert np.interp(NRDR_CRV_5G_LOCK_ANGLE, NRDR_CRV_5G_SR_CURVE_BP,
                     NRDR_CRV_5G_SR_CURVE_V) == pytest.approx(NRDR_CRV_5G_FINAL_SR)
    assert np.interp(450., NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_SR_CURVE_V) == pytest.approx(NRDR_CRV_5G_FINAL_SR)
    crv_outer = [value for angle, value in zip(NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_SR_CURVE_V, strict=True)
                 if angle >= 200.]
    assert all(left >= right for left, right in pairwise(crv_outer))

  def test_nrdr_absolute_curves_use_pre_solved_desired_angle_inverse(self):
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_CLARITY"] == (
      NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_CENTER_SR,
    )
    assert NRDR_VGR_INVERSE_BY_FP["HONDA_CRV_5G"] == (
      NRDR_CRV_5G_VGR_LINEAR_BP, NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_CENTER_SR,
    )
    for fingerprint in ("HONDA_CLARITY", "HONDA_CRV_5G", "HONDA_CIVIC_BOSCH"):
      linear_bp, real_angle_v, _ = NRDR_VGR_INVERSE_BY_FP[fingerprint]
      assert all(left < right for left, right in pairwise(linear_bp))
      for real_angle in (0., 45., 70., 90., 200.):
        model_angle = np.interp(real_angle, real_angle_v, linear_bp)
        recovered_angle = np.interp(model_angle, linear_bp, real_angle_v)
        assert recovered_angle == pytest.approx(real_angle, abs=1e-12)

  @parameterized.expand([
    (HONDA.HONDA_CLARITY, "HONDA_CLARITY", None),
    (HONDA.HONDA_CIVIC, "HONDA_CIVIC", None),
    (HONDA.HONDA_CIVIC_BOSCH, "HONDA_CIVIC_BOSCH", None),
    (HONDA.HONDA_CIVIC_BOSCH_DIESEL, "HONDA_CIVIC_BOSCH_DIESEL", None),
    (HONDA.HONDA_ACCORD, "HONDA_ACCORD", None),
    (HONDA.HONDA_CRV_5G, "HONDA_CRV_5G", None),
    (HONDA.HONDA_CRV_HYBRID, "HONDA_CRV_HYBRID", None),
    (HONDA.HONDA_INSIGHT, "HONDA_INSIGHT", None),
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
    assert (controller.sr_endpoint_profile is not None) == (expected_curve_fp is not None)
    assert (controller.vgr_inverse is not None) == (expected_inverse_fp is not None)

  def test_clarity_two_point_curve_is_authoritative_over_learner(self):
    CarInterface = interfaces[HONDA.HONDA_CLARITY]
    CP = CarInterface.get_non_essential_params(HONDA.HONDA_CLARITY)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CLARITY)
    CI = CarInterface(CP, CP_SP)
    controller = LatControlPID(CP.as_reader(), convert_to_capnp(CP_SP).as_reader(), CI, DT_CTRL)
    controller.learn_steer_ratio = True

    VM = VehicleModel(CP)
    VM.sR = 99.0  # prove the learned/model value is replaced
    CS = car.CarState.new_message()
    CS.vEgo = 30.0
    CS.steeringAngleDeg = 125.0
    params = log.LiveParametersData.new_message()
    pose = Pose.from_live_pose(generate_livePose().livePose)

    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert controller.vgr_inverse is None
    assert VM.sR == pytest.approx(15.61)

    # The two controls are absolute endpoint values, not a uniform offset.
    controller.sr_values[:] = [19.50, 12.00]
    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert VM.sR == pytest.approx(15.75)
    CS.steeringAngleDeg = 0.0
    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert VM.sR == pytest.approx(19.50)
    CS.steeringAngleDeg = 250.0
    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert VM.sR == pytest.approx(12.00)

    # The lane-change option follows the planner lifecycle, not the blinkers:
    # pre-change through finishing use the outer endpoint, then `off` restores
    # the normal measured-angle curve.
    CS.steeringAngleDeg = 0.0
    model_v2 = log.ModelDataV2.new_message()
    controller.update_model_v2(model_v2)
    for lane_change_state in (
      log.LaneChangeState.preLaneChange,
      log.LaneChangeState.laneChangeStarting,
      log.LaneChangeState.laneChangeFinishing,
    ):
      model_v2.meta.laneChangeState = lane_change_state
      controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
      assert VM.sR == pytest.approx(12.00)

    model_v2.meta.laneChangeState = log.LaneChangeState.off
    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert VM.sR == pytest.approx(19.50)

    # Turning the option off keeps the normal curve during planner lane changes.
    controller.lane_change_endpoint_sr = False
    model_v2.meta.laneChangeState = log.LaneChangeState.laneChangeStarting
    controller.update(False, CS, VM, params, False, 0.0, pose, False, 0.2)
    assert VM.sR == pytest.approx(19.50)

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
