"""TJB-A220 Route-A: measured position map, not a Honda firmware Table A.

JamesL787/openpilot 6c3432036109101fcff3d967298406e1d362fdc0, Honda steer_ratio.py.
The measured pinion-rate word divided by its centre value gives d(linear)/d(wheel).
"""
from bisect import bisect_right
from dataclasses import dataclass
import math

import numpy as np


def _integrated_linear_knots(angles):
  rate = np.interp(angles, (0, 15, 30, 45, 60, 75, 90, 105, 480),
                   (7.80, 7.83, 7.94, 8.24, 8.64, 9.06, 9.41, 9.60, 9.58))
  gain = rate[0] / rate
  linear = [0.0]
  for a, b, g0, g1 in zip(angles[:-1], angles[1:], gain[:-1], gain[1:], strict=True):
    area = 1 / g0 if abs(g1 - g0) < 1e-12 else math.log(g1 / g0) / (g1 - g0)
    linear.append(linear[-1] + (b - a) * area)
  return tuple(linear)


@dataclass(frozen=True)
class RdxMeasuredPosition:
  name = "RDX TJB-A220 measured pinion"
  center_divisor = 1 << 14  # no firmware angle table; published and linear agree at centre
  physical_knots = tuple(range(0, 481, 5))
  linear_knots = _integrated_linear_knots(physical_knots)
  # The donor rack-map extrapolates its final path in proportion to wheel angle.
  tail_scale = physical_knots[-1] / linear_knots[-1]

  def physical_to_linear(self, angle_deg: float) -> float:
    a = abs(angle_deg)
    v = a / self.tail_scale if a > self.physical_knots[-1] else np.interp(a, self.physical_knots, self.linear_knots)
    return math.copysign(v, angle_deg)

  def linear_to_physical(self, angle_deg: float) -> float:
    a = abs(angle_deg)
    v = a * self.tail_scale if a > self.linear_knots[-1] else np.interp(a, self.linear_knots, self.physical_knots)
    return math.copysign(v, angle_deg)

  def linear_to_physical_slope(self, angle_deg: float) -> float:
    i = bisect_right(self.linear_knots, abs(angle_deg))
    return self.tail_scale if i == len(self.linear_knots) else 5 / (self.linear_knots[i] - self.linear_knots[i - 1])


RDX_POSITION = RdxMeasuredPosition()
