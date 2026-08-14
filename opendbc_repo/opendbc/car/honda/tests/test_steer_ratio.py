from types import SimpleNamespace
from itertools import pairwise

import pytest

from opendbc.car.honda.steer_ratio import (
  CIVIC_C020_VGR_ANGLE_BP,
  CIVIC_C020_VGR_LINEAR_BP,
  CLARITY_VGR_ANGLE_BP,
  CLARITY_VGR_LINEAR_BP,
  HONDA_VGR_CIVIC_TBA_C020,
  HONDA_VGR_CLARITY_TRW_A020,
  HONDA_VGR_INSIGHT_TXM_A040,
  INSIGHT_TXM_A040_VGR_ANGLE_BP,
  INSIGHT_TXM_A040_VGR_LINEAR_BP,
  get_honda_vgr_inverse,
  get_honda_vgr_learning_inverse,
  get_honda_vgr_profile,
  vgr_linear_to_physical,
  vgr_physical_to_linear,
)
from opendbc.car.honda.values import HondaFlags


@pytest.mark.parametrize("linear_bp,angle_bp", [
  (CLARITY_VGR_LINEAR_BP, CLARITY_VGR_ANGLE_BP),
  (CIVIC_C020_VGR_LINEAR_BP, CIVIC_C020_VGR_ANGLE_BP),
  (INSIGHT_TXM_A040_VGR_LINEAR_BP, INSIGHT_TXM_A040_VGR_ANGLE_BP),
])
def test_position_maps_are_monotonic_and_invertible(linear_bp, angle_bp):
  assert len(linear_bp) == len(angle_bp)
  assert all(left < right for left, right in pairwise(linear_bp))
  assert all(left < right for left, right in pairwise(angle_bp))

  inverse = linear_bp, angle_bp
  for linear_angle in (0.0, 5.0, 20.0, 45.0, 90.0, 150.0):
    physical = vgr_linear_to_physical(linear_angle, inverse)
    assert vgr_physical_to_linear(physical, inverse) == pytest.approx(linear_angle, abs=1e-10)
    assert vgr_linear_to_physical(-linear_angle, inverse) == pytest.approx(-physical, abs=1e-10)


@pytest.mark.parametrize("version,profile", [
  (b"39990-TRW,A020\0\0", HONDA_VGR_CLARITY_TRW_A020),
  (b"39990-TBA,C020\0\0", HONDA_VGR_CIVIC_TBA_C020),
  (b"39990-TXM,A040\0\0", HONDA_VGR_INSIGHT_TXM_A040),
])
def test_exact_modified_eps_firmware_selects_profile(version, profile):
  assert get_honda_vgr_profile([SimpleNamespace(ecu="eps", fwVersion=version)]) == profile
  assert get_honda_vgr_profile([SimpleNamespace(ecu="eps", fwVersion=b"39990-XXX,A999\0\0")]) is None


def test_static_clarity_curve_leaves_paramsd_coordinate_unchanged():
  assert get_honda_vgr_learning_inverse(HondaFlags.VGR_CLARITY_TRW_A020) is None
  assert get_honda_vgr_learning_inverse(HondaFlags.VGR_CIVIC_TBA_C020) is None
  assert get_honda_vgr_learning_inverse(HondaFlags.VGR_INSIGHT_TXM_A040) is None
  assert get_honda_vgr_inverse(HondaFlags.VGR_CLARITY_TRW_A020) is not None
  assert get_honda_vgr_inverse(HondaFlags.VGR_CIVIC_TBA_C020) is not None
