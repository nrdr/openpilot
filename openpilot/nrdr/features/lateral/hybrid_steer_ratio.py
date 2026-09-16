"""Opt-in angle-domain geometry composition, independent of Params and control IO."""
from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Any

import numpy as np


BLEND_WIDTH_DEG = 5.0
BLEND_START_DEFAULT = 25.0
BLEND_START_MAX = 180.0


@dataclass(frozen=True)
class AngleSource:
  mode: int
  label: str
  base: float
  center: float
  final: float
  outer: float
  comma: float
  measured: Any = None
  firmware: Any = None

  def forward(self, angle: float) -> float:
    """Physical degrees -> equivalent linear degrees at the common CP anchor."""
    a = abs(angle)
    if self.mode == 3:
      value = self.firmware.physical_to_linear(a)
    else:
      ratio = (self.comma if self.mode == 1 else self.measured.ratio_at(a) if self.mode == 2
               else float(np.interp(a, (0.0, self.outer), (self.center, self.final))))
      value = self.base * a / ratio
    return math.copysign(value, angle)

  def inverse(self, linear: float) -> float:
    q = abs(linear)
    if self.mode == 3:
      value = self.firmware.linear_to_physical(q)
    elif self.mode == 1:
      value = q * self.comma / self.base
    elif self.mode == 0:
      if q >= self.forward(self.outer):
        value = q * self.final / self.base
      else:
        slope = (self.final - self.center) / self.outer
        value = q * self.center / (self.base - q * slope)
    else:
      profile = self.measured
      knots = tuple(self.forward(a) for a in profile.angles_deg)
      if q >= knots[-1]:
        value = q * profile.ratio_at(profile.angles_deg[-1]) / self.base
      else:
        i = max(0, min(bisect_right(knots, q) - 1, len(knots) - 2))
        x0, x1 = profile.angles_deg[i:i + 2]
        r0, r1 = profile.ratios[i:i + 2]
        slope = (r1 - r0) / (x1 - x0)
        k = math.degrees(math.atan(math.radians(q / self.base))) if profile.ratio_domain == "raw-angle" else q / self.base
        value = k * (r0 - slope * x0) / (1.0 - k * slope)
    return math.copysign(value, linear)


@dataclass(frozen=True)
class HybridGeometry:
  a: AngleSource
  b: AngleSource
  angles: tuple[float, ...]
  linear: tuple[float, ...]

  @property
  def start(self) -> float:
    return self.angles[0]

  @property
  def end(self) -> float:
    return self.angles[-1]

  def forward(self, angle: float) -> float:
    a = abs(angle)
    if a <= self.start:
      return self.a.forward(angle)
    if a >= self.end:
      return self.b.forward(angle)
    return math.copysign(float(np.interp(a, self.angles, self.linear)), angle)

  def inverse(self, linear: float) -> float:
    q = abs(linear)
    if q <= self.linear[0]:
      return self.a.inverse(linear)
    if q >= self.linear[-1]:
      return self.b.inverse(linear)
    return math.copysign(float(np.interp(q, self.linear, self.angles)), linear)


@lru_cache(maxsize=32)
def _build_hybrid(a: AngleSource, b: AngleSource, start: float) -> HybridGeometry | str:
  if not math.isfinite(start) or not 0.0 <= start <= BLEND_START_MAX:
    return "Hybrid blend start must be between 0 and 180 degrees"
  # The shipped mapping IS this piecewise-linear table, not an unchecked
  # analytic interpolant between samples. Strictly increasing nodes therefore
  # guarantee an invertible blend. Smoothstep weights soften both endpoints.
  angles = tuple(float(v) for v in np.linspace(start, start + BLEND_WIDTH_DEG, 101))
  values = []
  for angle in angles:
    u = (angle - start) / BLEND_WIDTH_DEG
    w = u * u * (3.0 - 2.0 * u)
    values.append((1.0 - w) * a.forward(angle) + w * b.forward(angle))
  if any(not math.isfinite(v) for v in values) or any(y <= x + 1e-9 for x, y in zip(values, values[1:], strict=False)):
    return "Hybrid blend would reverse or flatten the angle-to-curvature mapping; choose another angle or source pair"
  return HybridGeometry(a, b, angles, tuple(values))


def build_hybrid(a: AngleSource, b: AngleSource, start: float) -> HybridGeometry:
  # Cache rejected configurations too: don't revalidate an unchanged invalid
  # request 100 times per second while retaining the last accepted geometry.
  result = _build_hybrid(a, b, start)
  if isinstance(result, str):
    raise ValueError(result)
  return result
