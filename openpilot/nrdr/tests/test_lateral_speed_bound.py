import math

import numpy as np

from openpilot.nrdr.features.lateral import lateral_speed_bound as lsb
from openpilot.nrdr.features.lateral.lateral_speed_bound import LateralSpeedBound, plan_speed


def learned(ratio=1.12):
  bound = LateralSpeedBound()
  for _ in range(lsb.LEARN_MIN_FRAMES):
    bound.update(11.0, 0.0, 11.0 * ratio, 1.0, True)
  assert bound.ready and abs(bound.ratio - ratio) < 1e-9
  return bound


def test_inactive_until_the_usual_ratio_is_learned():
  bound = LateralSpeedBound()
  for _ in range(lsb.LEARN_MIN_FRAMES - 1):
    assert bound.update(11.0, 0.0, 12.3, 1.0, True) == 11.0
  # slow, braking and implausible samples never count toward learning
  fresh = LateralSpeedBound()
  for v, a, vp in ((5.0, 0.0, 9.0), (11.0, -1.5, 16.0), (11.0, 0.0, 30.0), (11.0, 0.0, 2.0)):
    for _ in range(1000):
      assert fresh.update(v, a, vp, 1.0, True) == max(v, 1.0)
  assert not fresh.ready


def test_never_lowers_the_speed_and_is_idle_when_plan_and_car_agree():
  bound = learned()
  for v in (0.0, 0.5, 2.0, 4.5, 6.5, 11.0, 30.0):
    for floor in (1.0, 2.5):
      base = max(v, floor)
      for vp in (0.0, 0.5 * v, v, 1.12 * v, 1.12 * (1 + lsb.MARGIN) * v):
        assert bound.update(v, -2.0, vp, floor, True) == base


def test_bounds_the_speed_when_the_car_is_slower_than_the_plan():
  bound = learned()
  # NO OUTLET, route 09, 0.5 s into the brake: car 4.46 m/s, plan 6.35 m/s
  used = bound.update(4.46, -2.4, 6.35, 2.5, True)
  assert abs(used - 6.35 / (1.12 * (1 + lsb.MARGIN))) < 1e-6
  assert 4.46 < used < 4.46 * lsb.MAX_RATIO
  # the reduction is capped, including at the floor when nearly stopped
  assert bound.update(1.7, -1.0, 6.6, 1.0, True) == 1.7 * lsb.MAX_RATIO
  assert bound.update(0.2, 0.5, 6.0, 2.5, True) == 2.5 * lsb.MAX_RATIO


def test_off_when_openpilot_controls_speed_and_on_bad_inputs():
  bound = learned()
  assert bound.update(4.46, -2.4, 6.35, 2.5, False) == 4.46
  for bad in (math.nan, math.inf, -1.0, 0.0):
    assert bound.update(4.46, 0.0, bad, 2.5, True) == 4.46
  assert bound.update(4.46, math.nan, 6.35, 2.5, True) == 4.46


def test_plan_speed_is_the_mean_over_the_action_horizon():
  t = 10.0 * (np.arange(33) / 32) ** 2
  assert abs(plan_speed(t, np.full(33, 7.0)) - 7.0) < 1e-9
  ramp = 5.0 + 2.0 * t
  assert abs(plan_speed(t, ramp) - (5.0 + 2.0 * 0.15)) < 0.02


def test_option_reads_as_off_when_the_key_is_missing():
  class Missing:
    def get_bool(self, key):
      raise KeyError(key)
  class Stored:
    def __init__(self, value):
      self.value = value
    def get_bool(self, key):
      assert key == "NrdrLateralSpeedBound"
      return self.value
  assert lsb.enabled(Missing()) is False
  assert lsb.enabled(Stored(True)) is True and lsb.enabled(Stored(False)) is False
