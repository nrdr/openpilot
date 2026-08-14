"""Firmware-derived Honda variable-gear-ratio position maps.

These tables and the position/rate-path distinction were traced from the EPS
firmware by vote_for_nobody. VehicleModel's scalar steer ratio remains the
learned or configured centre anchor; these maps only convert between the
centre-equivalent (linear) coordinate and the angle published by the EPS.
"""

import math

from opendbc.car.honda.values import HondaFlags


HONDA_VGR_CLARITY_TRW_A020 = "clarity_trw_a020"
HONDA_VGR_CIVIC_TBA_C020 = "civic_tba_c020"
HONDA_VGR_INSIGHT_TXM_A040 = "insight_txm_a040"


# Modified EPS images replace one hyphen with a comma. Normalize that spelling,
# but only match the exact firmware whose position table was traced.
HONDA_VGR_PROFILE_BY_FW = {
  "39990-TRW-A020": HONDA_VGR_CLARITY_TRW_A020,
  "39990-TBA-C020": HONDA_VGR_CIVIC_TBA_C020,
  "39990-TXM-A040": HONDA_VGR_INSIGHT_TXM_A040,
}

HONDA_VGR_PROFILE_FLAGS = {
  HONDA_VGR_CLARITY_TRW_A020: HondaFlags.VGR_CLARITY_TRW_A020,
  HONDA_VGR_CIVIC_TBA_C020: HondaFlags.VGR_CIVIC_TBA_C020,
  HONDA_VGR_INSIGHT_TXM_A040: HondaFlags.VGR_INSIGHT_TXM_A040,
}


def normalize_honda_eps_fw(version) -> str:
  if isinstance(version, bytes):
    version = version.split(b"\0", 1)[0].decode("ascii", errors="ignore")
  return str(version).split("\0", 1)[0].replace(",", "-")


def get_honda_vgr_profile(car_fw):
  for fw in car_fw:
    if fw.ecu == "eps":
      profile = HONDA_VGR_PROFILE_BY_FW.get(normalize_honda_eps_fw(fw.fwVersion))
      if profile is not None:
        return profile
  return None


def _build_vgr_position_inverse(raw_x, raw_y, raw_units_per_degree=10.0, max_raw_step=20):
  """Reproduce the EPS position conversion as linear -> published angle.

  Firmware interpolates a Q14 divisor and then divides the raw position by it.
  Subdividing long source intervals preserves that interpolate-then-divide
  behavior instead of drawing a biased chord between transformed knots.
  """
  linear_bp = []
  angle_bp = []
  relative_ratio = []
  center_divisor = raw_y[0]

  for raw0, raw1, divisor0, divisor1 in zip(raw_x, raw_x[1:], raw_y, raw_y[1:], strict=False):
    steps = max(1, math.ceil((raw1 - raw0) / max_raw_step))
    for step in range(steps):
      fraction = step / steps
      raw = raw0 + (raw1 - raw0) * fraction
      divisor = divisor0 + (divisor1 - divisor0) * fraction
      linear_bp.append(raw * (1 << 14) / center_divisor / raw_units_per_degree)
      angle_bp.append(raw * (1 << 14) / divisor / raw_units_per_degree)
      relative_ratio.append(center_divisor / divisor)

  raw = raw_x[-1]
  divisor = raw_y[-1]
  linear_bp.append(raw * (1 << 14) / center_divisor / raw_units_per_degree)
  angle_bp.append(raw * (1 << 14) / divisor / raw_units_per_degree)
  relative_ratio.append(center_divisor / divisor)
  return linear_bp, angle_bp, relative_ratio


# Primary POSITION tables. The neighboring B tables affect the rate path and
# must not be integrated or used as steering-position maps.
_CLARITY_POSITION_X = [
  0, 40, 80, 119, 158, 198, 237, 277, 317, 398,
  604, 820, 1047, 1164, 1210, 1257, 1305, 1352, 1398, 1447,
  1493, 1540, 1588, 1634, 1989, 2344, 2700, 3056, 3413, 5020,
]
_CLARITY_POSITION_Y = [
  16384, 16174, 16173, 16247, 16179, 16220, 16180, 16209, 16231, 16303,
  16506, 16812, 17177, 17352, 17411, 17473, 17538, 17600, 17644, 17705,
  17749, 17792, 17843, 17885, 18130, 18303, 18439, 18547, 18645, 18952,
]

_CIVIC_C020_POSITION_X = [
  0, 52, 103, 153, 203, 254, 305, 357, 407, 511,
  771, 1046, 1334, 1482, 1542, 1602, 1661, 1722, 1782, 1844,
  1904, 1965, 2025, 2086, 2540, 2997, 3451, 3907, 4363, 5731,
]
_CIVIC_C020_POSITION_Y = [
  20647, 20647, 20597, 20720, 20637, 20769, 20786, 20795, 20784, 20850,
  21053, 21413, 21856, 22060, 22150, 22243, 22306, 22380, 22450, 22546,
  22605, 22672, 22724, 22780, 23110, 23379, 23550, 23708, 23827, 24070,
]

_INSIGHT_TXM_A040_POSITION_X = [
  0, 43, 88, 130, 175, 219, 263, 306, 351, 441,
  671, 914, 1166, 1297, 1348, 1401, 1454, 1507, 1559, 1613,
  1664, 1718, 1771, 1823, 2217, 2610, 3005, 3402, 3798, 5515,
]
_INSIGHT_TXM_A040_POSITION_Y = [
  17613, 17613, 18022, 17886, 17971, 17981, 17988, 17964, 18022, 18084,
  18269, 18631, 19026, 19226, 19313, 19387, 19442, 19523, 19583, 19636,
  19692, 19745, 19798, 19839, 20113, 20317, 20474, 20593, 20702, 20989,
]


CLARITY_VGR_LINEAR_BP, CLARITY_VGR_ANGLE_BP, CLARITY_VGR_RELATIVE_SR = _build_vgr_position_inverse(
  _CLARITY_POSITION_X, _CLARITY_POSITION_Y,
)
CIVIC_C020_VGR_LINEAR_BP, CIVIC_C020_VGR_ANGLE_BP, CIVIC_C020_VGR_RELATIVE_SR = _build_vgr_position_inverse(
  _CIVIC_C020_POSITION_X, _CIVIC_C020_POSITION_Y,
)
INSIGHT_TXM_A040_VGR_LINEAR_BP, INSIGHT_TXM_A040_VGR_ANGLE_BP, INSIGHT_TXM_A040_VGR_RELATIVE_SR = _build_vgr_position_inverse(
  _INSIGHT_TXM_A040_POSITION_X, _INSIGHT_TXM_A040_POSITION_Y,
)


HONDA_VGR_INVERSE_BY_PROFILE = {
  HONDA_VGR_CLARITY_TRW_A020: (CLARITY_VGR_LINEAR_BP, CLARITY_VGR_ANGLE_BP),
  HONDA_VGR_CIVIC_TBA_C020: (CIVIC_C020_VGR_LINEAR_BP, CIVIC_C020_VGR_ANGLE_BP),
  HONDA_VGR_INSIGHT_TXM_A040: (INSIGHT_TXM_A040_VGR_LINEAR_BP, INSIGHT_TXM_A040_VGR_ANGLE_BP),
}
HONDA_VGR_INVERSE_BY_FLAG = {
  int(flag): HONDA_VGR_INVERSE_BY_PROFILE[profile]
  for profile, flag in HONDA_VGR_PROFILE_FLAGS.items()
}


def get_honda_vgr_inverse(flags):
  for flag, inverse in HONDA_VGR_INVERSE_BY_FLAG.items():
    if int(flags) & flag:
      return inverse
  return None


# The road-tested Honda controller profiles now use direct two-point measured-
# angle SR curves in latcontrol. Keep paramsd in its original published-angle
# coordinate so those profiles match the restored Clarity behavior exactly.
# The traced maps also remain unvalidated for learner-coordinate changes.
HONDA_VGR_LEARNING_FLAGS = ()


def get_honda_vgr_learning_inverse(flags):
  for flag in HONDA_VGR_LEARNING_FLAGS:
    if int(flags) & int(flag):
      return HONDA_VGR_INVERSE_BY_FLAG[int(flag)]
  return None


def vgr_linear_to_physical(linear_deg: float, inverse) -> float:
  if inverse is None:
    return linear_deg
  linear_bp, angle_bp = inverse
  return math.copysign(float(_interp(abs(linear_deg), linear_bp, angle_bp)), linear_deg)


def vgr_physical_to_linear(physical_deg: float, inverse) -> float:
  if inverse is None:
    return physical_deg
  linear_bp, angle_bp = inverse
  return math.copysign(float(_interp(abs(physical_deg), angle_bp, linear_bp)), physical_deg)


def _interp(x, xp, fp):
  if x <= xp[0]:
    return fp[0]
  if x >= xp[-1]:
    return fp[-1]
  lo, hi = 0, len(xp) - 1
  while hi - lo > 1:
    mid = (lo + hi) // 2
    if xp[mid] <= x:
      lo = mid
    else:
      hi = mid
  span = xp[hi] - xp[lo]
  if span <= 0:
    return fp[lo]
  return fp[lo] + (fp[hi] - fp[lo]) * (x - xp[lo]) / span
