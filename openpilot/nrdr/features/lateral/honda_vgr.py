from bisect import bisect_right
from dataclasses import dataclass, field
import math

import numpy as np


__all__ = (
  "HONDA_VGR_PROFILES",
  "Q14",
  "RAW_UNITS_PER_DEGREE",
  "HondaVgrProfile",
  "get_honda_vgr_profile",
  "normalize_honda_eps_firmware",
)


Q14 = 1 << 14
RAW_UNITS_PER_DEGREE = 10.0


@dataclass(frozen=True)
class HondaVgrProfile:
  name: str
  fingerprints: tuple[str, ...]
  firmware: tuple[str, ...]
  position_x: tuple[int, ...]
  position_y: tuple[int, ...]
  physical_knots: tuple[float, ...] = field(init=False)

  def __post_init__(self) -> None:
    if len(self.position_x) != len(self.position_y) or len(self.position_x) < 2:
      raise ValueError("Honda VGR position tables must contain matching X/Y values")
    if self.position_x[0] != 0 or any(b <= a for a, b in zip(self.position_x, self.position_x[1:], strict=False)):
      raise ValueError("Honda VGR position breakpoints must start at zero and increase")
    if any(value <= 0 for value in self.position_y):
      raise ValueError("Honda VGR position divisors must be positive")

    physical = tuple(raw * Q14 / (divisor * RAW_UNITS_PER_DEGREE)
                     for raw, divisor in zip(self.position_x, self.position_y, strict=True))
    if any(b <= a for a, b in zip(physical, physical[1:], strict=False)):
      raise ValueError("Honda VGR physical-angle map must increase")
    object.__setattr__(self, "physical_knots", physical)

  @property
  def center_divisor(self) -> int:
    return self.position_y[0]

  @property
  def tail_scale(self) -> float:
    return self.center_divisor / self.position_y[-1]

  def linear_to_physical(self, angle_deg: float) -> float:
    raw = abs(angle_deg) * self.center_divisor * RAW_UNITS_PER_DEGREE / Q14
    divisor = float(np.interp(raw, self.position_x, self.position_y))
    physical = raw * Q14 / (divisor * RAW_UNITS_PER_DEGREE)
    return math.copysign(physical, angle_deg)

  def linear_to_physical_slope(self, angle_deg: float) -> float:
    """Return d(physical angle) / d(linear angle) for the active table segment."""
    raw = abs(angle_deg) * self.center_divisor * RAW_UNITS_PER_DEGREE / Q14
    if raw >= self.position_x[-1]:
      return self.tail_scale

    index = min(bisect_right(self.position_x, raw) - 1, len(self.position_x) - 2)
    x0, x1 = self.position_x[index:index + 2]
    y0, y1 = self.position_y[index:index + 2]
    divisor_slope = (y1 - y0) / (x1 - x0)
    divisor = y0 + divisor_slope * (raw - x0)
    divisor_intercept = y0 - divisor_slope * x0
    return self.center_divisor * divisor_intercept / divisor ** 2

  def physical_to_linear(self, angle_deg: float) -> float:
    physical = abs(angle_deg)
    if physical == 0.0:
      return 0.0

    if physical >= self.physical_knots[-1]:
      raw = physical * self.position_y[-1] * RAW_UNITS_PER_DEGREE / Q14
    else:
      index = min(bisect_right(self.physical_knots, physical) - 1, len(self.position_x) - 2)
      x0, x1 = self.position_x[index:index + 2]
      y0, y1 = self.position_y[index:index + 2]
      slope = (y1 - y0) / (x1 - x0)
      intercept = y0 - slope * x0
      raw = physical * RAW_UNITS_PER_DEGREE * intercept / (Q14 - physical * RAW_UNITS_PER_DEGREE * slope)

    linear = raw * Q14 / (self.center_divisor * RAW_UNITS_PER_DEGREE)
    return math.copysign(linear, angle_deg)

# Table-A position maps extracted and traced by vote_for_nobody; Table B is the independent EPS rate path.
_TRW_A020_X = (0, 40, 80, 119, 158, 198, 237, 277, 317, 398, 604, 820, 1047, 1164, 1210,
               1257, 1305, 1352, 1398, 1447, 1493, 1540, 1588, 1634, 1989, 2344, 2700, 3056, 3413, 5020)
_TRW_A020_Y = (16384, 16174, 16173, 16247, 16179, 16220, 16180, 16209, 16231, 16303, 16506, 16812,
               17177, 17352, 17411, 17473, 17538, 17600, 17644, 17705, 17749, 17792, 17843, 17885,
               18130, 18303, 18439, 18547, 18645, 18952)

_CIVIC_C120_X = (0, 40, 80, 120, 160, 200, 240, 280, 320, 400, 600, 800, 1000, 1100, 1140,
                  1180, 1220, 1260, 1300, 1340, 1380, 1420, 1460, 1500, 1800, 2100, 2400, 2700, 3000, 9000)
_CIVIC_C120_Y = (20972, 20972, 20480, 20644, 20644, 20808, 20644, 20644, 20644, 20644, 20808, 21135,
                  21463, 21627, 21627, 21791, 21791, 21955, 21955, 21955, 22118, 22118, 22282, 22282,
                  22446, 22610, 23101, 23429, 23593, 24740)

_CIVIC_C020_X = (0, 52, 103, 153, 203, 254, 305, 357, 407, 511, 771, 1046, 1334, 1482, 1542,
                  1602, 1661, 1722, 1782, 1844, 1904, 1965, 2025, 2086, 2540, 2997, 3451, 3907, 4363, 5731)
_CIVIC_C020_Y = (20647, 20647, 20597, 20720, 20637, 20769, 20786, 20795, 20784, 20850, 21053, 21413,
                  21856, 22060, 22150, 22243, 22306, 22380, 22450, 22546, 22605, 22672, 22724, 22780,
                  23110, 23379, 23550, 23708, 23827, 24070)

_TLA_A040_X = (0, 42, 84, 125, 167, 209, 251, 292, 335, 419, 636, 864, 1102, 1227, 1276,
               1326, 1376, 1426, 1476, 1526, 1578, 1628, 1680, 1729, 2108, 2488, 2869, 3248, 3626, 5130)
_TLA_A040_Y = (16783, 16783, 16790, 16795, 16979, 16979, 17100, 17086, 17100, 17110, 17300, 17597,
               17964, 18170, 18247, 18322, 18378, 18460, 18521, 18566, 18651, 18697, 18761, 18803,
               19129, 19345, 19527, 19657, 19756, 19989)

_TXM_A040_X = (0, 43, 88, 130, 175, 219, 263, 306, 351, 441, 671, 914, 1166, 1297, 1348,
               1401, 1454, 1507, 1559, 1613, 1664, 1718, 1771, 1823, 2217, 2610, 3005, 3402, 3798, 5515)
_TXM_A040_Y = (17613, 17613, 18022, 17886, 17971, 17981, 17988, 17964, 18022, 18084, 18269, 18631,
               19026, 19226, 19313, 19387, 19442, 19523, 19583, 19636, 19692, 19745, 19798, 19839,
               20113, 20317, 20474, 20593, 20702, 20989)


HONDA_VGR_PROFILES = (
  HondaVgrProfile("Clarity TRW-A020", ("HONDA_CLARITY",), ("39990-TRW-A020",), _TRW_A020_X, _TRW_A020_Y),
  HondaVgrProfile("Civic C120/A030/TEG", ("HONDA_CIVIC", "HONDA_CIVIC_BOSCH"),
                  ("39990-TBA-C120", "39990-TBA-A030", "39990-TEG-A010"), _CIVIC_C120_X, _CIVIC_C120_Y),
  HondaVgrProfile("Civic C020/TGG-A120", ("HONDA_CIVIC_BOSCH",),
                  ("39990-TBA-C020", "39990-TGG-A120"), _CIVIC_C020_X, _CIVIC_C020_Y),
  HondaVgrProfile("CR-V TLA-A040", ("HONDA_CRV_5G",), ("39990-TLA-A040",), _TLA_A040_X, _TLA_A040_Y),
  HondaVgrProfile("Insight TXM-A040", ("HONDA_INSIGHT",), ("39990-TXM-A040",), _TXM_A040_X, _TXM_A040_Y),
)

_PROFILE_BY_CAR_FIRMWARE = {
  ("HONDA_CLARITY", "39990-TRW-A020"): HONDA_VGR_PROFILES[0],
  ("HONDA_CIVIC", "39990-TBA-A030"): HONDA_VGR_PROFILES[1],
  ("HONDA_CIVIC", "39990-TEG-A010"): HONDA_VGR_PROFILES[1],
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C120"): HONDA_VGR_PROFILES[1],
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C020"): HONDA_VGR_PROFILES[2],
  ("HONDA_CIVIC_BOSCH", "39990-TGG-A120"): HONDA_VGR_PROFILES[2],
  ("HONDA_CRV_5G", "39990-TLA-A040"): HONDA_VGR_PROFILES[3],
  ("HONDA_INSIGHT", "39990-TXM-A040"): HONDA_VGR_PROFILES[4],
}


def normalize_honda_eps_firmware(version) -> str:
  if not isinstance(version, (bytes, str)):
    try:
      version = bytes(version)
    except (TypeError, ValueError):
      pass
  if isinstance(version, bytes):
    version = version.split(b"\0", 1)[0].decode("ascii", errors="ignore")
  return str(version).split("\0", 1)[0].strip().replace(",", "-")


def get_honda_vgr_profile(CP) -> HondaVgrProfile | None:
  if str(getattr(CP, "brand", "")) != "honda":
    return None
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  for firmware in getattr(CP, "carFw", ()):
    if firmware.ecu != "eps":
      continue
    profile = _PROFILE_BY_CAR_FIRMWARE.get((fingerprint, normalize_honda_eps_firmware(firmware.fwVersion)))
    if profile is not None:
      return profile
  return None
