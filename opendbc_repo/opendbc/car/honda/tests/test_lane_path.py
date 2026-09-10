import math
import unittest
from types import SimpleNamespace

import numpy as np

from opendbc.car.honda import lane_path


def model_at(center_y):
  """Fake modelV2 with both ego lane lines fully confident and the lane center at center_y (m, +left)."""
  x = list(np.linspace(0.0, 110.0, 23))

  def line(y):
    return SimpleNamespace(x=x, y=[y] * len(x))
  return SimpleNamespace(laneLines=[line(center_y + 3.3), line(center_y + 1.65), line(center_y - 1.65), line(center_y - 3.3)],
                         laneLineProbs=[0.0, 1.0, 1.0, 0.0])


V_EGO = 30.0


class TestLanePathSlew(unittest.TestCase):
  def test_first_fit_shown_unslewed(self):
    # nothing on the dash yet: start at the fit, no ramp-in from center
    fitter = lane_path.LanePathFitter()
    dl = fitter.update(model_at(-2.0), V_EGO, 0.0)
    assert dl.offsets == lane_path.encode_lane_path(*_lane_xy(-2.0))

  def test_step_is_rate_limited(self):
    fitter = lane_path.LanePathFitter()
    prev = fitter.update(model_at(0.0), V_EGO, 0.0).offsets
    assert all(o == 0 for o in prev)

    target = lane_path.encode_lane_path(*_lane_xy(-2.0))
    max_step = math.ceil(lane_path.SLEW_MAX_STEP)
    for _ in range(10):
      cur = fitter.update(model_at(-2.0), V_EGO, 0.0).offsets
      for p, c, t in zip(prev, cur, target, strict=True):
        assert abs(c - p) <= max_step
        assert abs(t - c) <= abs(t - p)  # monotonic approach
      prev = cur
    assert prev == target  # |target| ~ 60 raw: converged well within 10 updates

  def test_full_scale_takes_two_seconds(self):
    # center -> full-scale (max turn) must take SLEW_FULL_SCALE_SECONDS at the 50 Hz update rate
    fitter = lane_path.LanePathFitter()
    fitter.update(model_at(0.0), V_EGO, 0.0)
    target = lane_path.encode_lane_path(*_lane_xy(-100.0))  # saturates every offset at OFFSET_VALID_MAX
    assert all(t == lane_path.OFFSET_VALID_MAX for t in target)

    n_updates = round(lane_path.SLEW_FULL_SCALE_SECONDS * lane_path.SLEW_UPDATE_RATE_HZ)
    for i in range(n_updates):
      dl = fitter.update(model_at(-100.0), V_EGO, 0.0)
      if i < n_updates - 1:
        assert dl.offsets != target
    assert dl.offsets == target

  def test_blank_resets_slew(self):
    # once the lane blanks off the dash, the next fit is shown directly (no slew across the gap)
    fitter = lane_path.LanePathFitter()
    fitter.update(model_at(0.0), V_EGO, 0.0)
    dl = fitter.update(None, V_EGO, 0.0)
    assert dl.offsets == [lane_path.OFFSET_UNAVAILABLE] * lane_path.NUM_PTS
    dl = fitter.update(model_at(-2.0), V_EGO, 0.0)
    assert dl.offsets == lane_path.encode_lane_path(*_lane_xy(-2.0))

  def test_short_path_passthrough_and_reset(self):
    # a fit that doesn't reach D_MAX encodes all-sentinel: pass it through and reset the slew state
    fitter = lane_path.LanePathFitter()
    fitter.update(model_at(0.0), V_EGO, 0.0)

    short = model_at(-2.0)
    for ll in short.laneLines:
      ll.x = ll.x[:10]  # max ~50 m < D_MAX
      ll.y = ll.y[:10]
    dl = fitter.update(short, V_EGO, 0.0)
    assert dl.offsets == [lane_path.OFFSET_UNAVAILABLE] * lane_path.NUM_PTS

    dl = fitter.update(model_at(-2.0), V_EGO, 0.0)
    assert dl.offsets == lane_path.encode_lane_path(*_lane_xy(-2.0))


def _lane_xy(center_y):
  m = model_at(center_y)
  return m.laneLines[1].x, [(a + b) / 2.0 for a, b in zip(m.laneLines[1].y, m.laneLines[2].y, strict=True)]


if __name__ == "__main__":
  unittest.main()
