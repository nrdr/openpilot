"""Opt-in bound on the speed that turns the model's lateral output into curvature.

openpilot divides the model's lateral output by the measured speed: plan yaw rate / v for plan models,
lateral acceleration / v^2 for action-head models. The model produced that output for the speed it
expected. When the driver, not openpilot, controls speed and the car is slower than the model expects
(coasting or braking through a turn), the same output becomes a tighter curvature than the path the
model drew. Measured on the Clarity, 2026-11-20: 16-38% over-request with OPM10V3 in four turns and
about 2x with TSFDOM at one corner. See openpilot/nrdr/docs/lateral_speed_bound_2026-11-20.md.

The bound replaces the measured speed with the model's own planned speed, scaled by the ratio the two
normally have on this car, when and only when that is higher. It never lowers the speed used, so it
can only reduce a curvature request, and by a limited factor. It stays out of the way until the usual
ratio has been learned in steady driving, and whenever openpilot controls speed.
"""
import math

import numpy as np

PARAM = "NrdrLateralSpeedBound"

HORIZON_S = 0.3              # the lateral action reads this far into the plan
LEARN_MIN_SPEED = 8.0        # m/s; the usual plan/car speed ratio is learned only in steady driving
LEARN_MAX_ACCEL = 0.5        # m/s^2
LEARN_RATIO_RANGE = (0.8, 1.4)
LEARN_MIN_FRAMES = 400       # 20 s at 20 Hz before the bound may act
LEARN_HORIZON_FRAMES = 2400  # then a two-minute running average
MARGIN = 0.08                # plan speed must exceed the usual ratio by this much before the bound acts
MAX_RATIO = 1.5              # the speed used never exceeds this multiple of the floored measured speed


def enabled(params) -> bool:
  """Latched by the caller at process start. A missing key reads as off."""
  try:
    return bool(params.get_bool(PARAM))
  except Exception:
    return False


def plan_speed(t_idxs, plan_velocity) -> float:
  """Mean planned speed over the action horizon."""
  return 0.5 * (float(plan_velocity[0]) + float(np.interp(HORIZON_S, t_idxs, plan_velocity)))


class LateralSpeedBound:
  def __init__(self):
    self.ratio: float | None = None
    self.frames = 0

  @property
  def ready(self) -> bool:
    return self.ratio is not None and self.frames >= LEARN_MIN_FRAMES

  def _learn(self, v_ego: float, a_ego: float, v_plan: float) -> None:
    if v_ego < LEARN_MIN_SPEED or abs(a_ego) > LEARN_MAX_ACCEL:
      return
    ratio = v_plan / v_ego
    if not LEARN_RATIO_RANGE[0] < ratio < LEARN_RATIO_RANGE[1]:
      return
    self.frames += 1
    gain = 1.0 / min(self.frames, LEARN_HORIZON_FRAMES)
    self.ratio = ratio if self.ratio is None else self.ratio + gain * (ratio - self.ratio)

  def update(self, v_ego: float, a_ego: float, v_plan: float, floor: float, lateral_only: bool) -> float:
    """Speed to divide the lateral output by. `floor` is the conversion's own minimum speed."""
    base = max(float(v_ego), float(floor))
    if not all(math.isfinite(x) for x in (v_ego, a_ego, v_plan)) or v_plan <= 0.0:
      return base
    self._learn(v_ego, a_ego, v_plan)
    if not lateral_only or not self.ready:
      return base
    bound = v_plan / (self.ratio * (1.0 + MARGIN))
    return min(max(base, bound), base * MAX_RATIO)
