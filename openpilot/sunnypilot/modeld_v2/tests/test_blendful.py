"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.blendful import Blendful
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

X = np.array(ModelConstants.X_IDXS)
BUILD, RELEASE = 0.5, 2.0


def frame(center=0.0, plan=0.0, k=0.0, probs=(0.9, 0.9), stds=(0.1, 0.1), width=3.5):
  road = k * X ** 2 / 2
  lines = np.zeros((1, 4, 33, 2))
  lane_stds = np.ones((1, 4, 33, 2))
  for i, off in enumerate((-1.5 * width, -width / 2, width / 2, 1.5 * width)):
    lines[0, i, :, 0] = road + center + off
  lane_stds[0, 1, :, 0], lane_stds[0, 2, :, 0] = stds
  lane_probs = np.zeros((1, 8))
  lane_probs[0, 3], lane_probs[0, 5] = probs
  path = np.zeros((1, 33, 3))
  path[0, :, 0] = X
  path[0, :, 1] = road + plan * np.clip(X / 10, 0, 1)
  return {'lane_lines': lines, 'lane_lines_stds': lane_stds, 'lane_lines_prob': lane_probs, 'plan': path}


def drive(bf, seconds, v=20.0, k=0.0, **kw):
  out = [bf.update(frame(k=k, **kw), v, True, k) for _ in range(int(seconds / DT_MDL))]
  return np.array(out) * v ** 2  # m/s^2


class TestBlendful(unittest.TestCase):
  def setUp(self):
    self.bf = Blendful()

  def test_centered_adds_nothing(self):
    push = drive(self.bf, 5.0)
    assert self.bf.trust > 0.9
    assert np.abs(push).max() < 1e-3

  def test_pulls_toward_lane_center(self):
    push = drive(self.bf, 5.0, center=0.5)
    assert push[-1] > 0.02
    assert self.bf.trust > 0.9
    assert np.all(np.diff(push) <= BUILD * DT_MDL + 1e-9)

  def test_flipping_sides_builds_slowly(self):
    k = 0.002
    drive(self.bf, 5.0, k=k, center=0.5)
    push = drive(self.bf, 5.0, k=k, center=-0.5)
    rate = np.diff(push) / DT_MDL
    assert push[-1] < 0
    assert np.all(rate >= -RELEASE - 1e-6)
    assert np.all(rate[push[:-1] <= 0] >= -BUILD - 1e-6)
    crossing = push[1:][(push[:-1] > 0) & (push[1:] <= 0)]
    assert len(crossing) and np.all(crossing >= -BUILD * DT_MDL - 1e-9)

  def test_weak_lines_drive_laneless(self):
    clear = drive(Blendful(), 5.0, center=0.5)[-1]
    faint = Blendful()
    push = drive(faint, 5.0, center=0.5, probs=(0.1, 0.1))
    assert faint.trust < 0.25 and abs(push[-1]) < 0.25 * clear
    blurry = Blendful()
    push = drive(blurry, 5.0, center=0.5, stds=(0.8, 0.8))
    assert blurry.trust == 0.0 and np.abs(push).max() < 1e-6

  def test_lone_line_holds_through_a_blink_in_a_curve(self):
    k, v = 1 / 20, 6.0
    drive(self.bf, 6.0, v=v, k=k, plan=0.4, probs=(0.9, 0.05))
    before = self.bf.trust
    drive(self.bf, 0.25, v=v, k=k, plan=0.4, probs=(0.1, 0.05), stds=(1.0, 0.1))
    bottom = self.bf.trust
    drive(self.bf, 2.0, v=v, k=k, plan=0.4, probs=(0.9, 0.05))
    assert before > 0.5
    assert bottom > 0.5 * before
    assert self.bf.trust > 0.85 * before

  def test_yields_when_the_model_goes_around(self):
    drive(self.bf, 6.0)
    push = drive(self.bf, 3.0, plan=0.8)
    assert self.bf.going_around
    assert self.bf.trust < 0.05
    assert abs(push[-1]) < 0.01

  def test_fit_does_not_grow_while_trust_falls(self):
    drive(self.bf, 5.0, center=0.3)
    for i in range(40):
      dk, trust = self.bf.dk, self.bf.trust
      p = 0.9 - 0.02 * i
      self.bf.update(frame(center=0.3, plan=-0.02 * i, probs=(p, p)), 20.0, True, 0.0)
      if self.bf.trust < trust:
        assert abs(self.bf.dk) <= abs(dk) + 1e-12

  def test_toggle_off_returns_zero_and_resets(self):
    drive(self.bf, 5.0, center=0.5)
    assert self.bf.curvature != 0.0
    assert self.bf.update(frame(center=0.5), 20.0, True, 0.0, enabled=False) == 0.0
    assert self.bf.curvature == 0.0 and self.bf.trust == 0.0

  def test_fades_below_min_speed(self):
    drive(self.bf, 5.0, v=10.0, center=0.5)
    start = self.bf.curvature
    out = np.array([self.bf.update(frame(center=0.5), 4.0, True, 0.0) for _ in range(100)])
    assert self.bf.trust == 0.0
    assert abs(out[0]) < abs(start)
    assert abs(out[-1]) < 1e-6

  def test_nonfinite_model_inputs_fail_closed_and_reset(self):
    corruptions = (
      ("lane line", lambda output: output['lane_lines'].__setitem__((0, 1, 4, 0), np.nan)),
      ("lane std", lambda output: output['lane_lines_stds'].__setitem__((0, 1, 4, 0), np.inf)),
      ("lane probability", lambda output: output['lane_lines_prob'].__setitem__((0, 3), np.nan)),
      ("plan", lambda output: output['plan'].__setitem__((0, 4, 1), np.nan)),
    )
    for name, corrupt in corruptions:
      with self.subTest(name=name):
        bf = Blendful()
        drive(bf, 3.0, center=0.5)
        output = frame(center=0.5)
        corrupt(output)
        assert bf.update(output, 20.0, True, 0.0) == 0.0
        assert all(np.isfinite(value) for value in (bf.curvature, bf.trust, bf.dk, bf.l_prob, bf.r_prob))

    for name, v_ego, curvature in (("speed", np.nan, 0.0), ("curvature", 20.0, np.inf)):
      with self.subTest(name=name):
        bf = Blendful()
        drive(bf, 3.0, center=0.5)
        assert bf.update(frame(center=0.5), v_ego, True, curvature) == 0.0
        assert bf.curvature == 0.0 and bf.trust == 0.0

  def test_malformed_shapes_and_missing_tensors_fail_closed(self):
    malformed = (
      {},
      {**frame(), 'lane_lines': np.zeros((1, 2, 33, 2))},
      {**frame(), 'lane_lines_stds': np.zeros((1, 4, 2, 2))},
      {**frame(), 'lane_lines_prob': np.zeros((1, 4))},
      {**frame(), 'plan': np.zeros((1, 1, 2))},
    )
    for output in malformed:
      with self.subTest(keys=tuple(output)):
        bf = Blendful()
        drive(bf, 3.0, center=0.5)
        assert bf.update(output, 20.0, True, 0.0) == 0.0
        assert bf.curvature == 0.0 and bf.trust == 0.0

  def test_unsupported_tensor_and_scalar_types_fail_closed(self):
    for dtype in (object, bool):
      for key in ('lane_lines', 'lane_lines_stds', 'lane_lines_prob', 'plan'):
        with self.subTest(tensor=key, dtype=dtype):
          bf = Blendful()
          drive(bf, 3.0, center=0.5)
          output = frame(center=0.5)
          output[key] = output[key].astype(dtype)
          assert bf.update(output, 20.0, True, 0.0) == 0.0
          assert bf.curvature == 0.0 and bf.trust == 0.0

    for name, v_ego, curvature in (
      ('string speed', '20', 0.0),
      ('none speed', None, 0.0),
      ('bool speed', True, 0.0),
      ('string curvature', 20.0, '0'),
      ('none curvature', 20.0, None),
      ('bool curvature', 20.0, np.bool_(True)),
    ):
      with self.subTest(scalar=name):
        bf = Blendful()
        drive(bf, 3.0, center=0.5)
        assert bf.update(frame(center=0.5), v_ego, True, curvature) == 0.0
        assert bf.curvature == 0.0 and bf.trust == 0.0

  def test_zero_lane_std_stays_finite(self):
    output = frame(center=0.25, stds=(0.0, 0.0))
    values = np.array([self.bf.update(output, 20.0, True, 0.0) for _ in range(100)])
    assert np.isfinite(values).all()
    assert np.isfinite(self.bf.trust) and np.isfinite(self.bf.dk)
