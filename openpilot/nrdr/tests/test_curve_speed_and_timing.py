from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.features.longitudinal.curve_speed import CurveSpeed
from openpilot.nrdr.features.model_inputs import action_time_input, model_fidx


def plan(yaw=.4):
  t = np.array([0., .5, 1., 2., 6.])
  return NS(position=NS(t=t), velocity=NS(x=np.full(5, 20.)), orientationRate=NS(z=np.full(5, yaw)))


def test_input_cap_applies_to_each_axis_only_above_threshold():
  for lat, lon in ((.26, .38), (.75, .22), (.21, .6), (.4, .4), (.7, .9)):
    old = np.array([lat, lon], dtype=np.float32)
    np.testing.assert_array_equal(action_time_input(lat, lon, False), old)
    np.testing.assert_array_equal(action_time_input(lat, lon, True), np.minimum(old, .4))


@pytest.mark.parametrize('value,expected', [(1, 1.), (3, 3.), (6, 6.), (None, 3.), (7, 3.), (0, 3.)])
def test_fidx_range(value, expected):
  assert model_fidx(NS(get=lambda key, *, return_default: value)) == expected


def test_curve_speed_only_reduces_candidate_and_preserves_stronger_braking():
  c = CurveSpeed(.05)
  model = plan()
  for accel in [1., 0., -.6, -2., -3.]*25:
    prev = c.correction
    out = c.update(model, 0., accel)
    assert min(accel, -2.) <= out <= accel
    assert abs(prev - c.correction) <= .100001
  assert c.update(model, 0., .2) == -2.
  c.reset()
  assert c.gap.x == c.correction == 0.
  assert c.update(plan(0.), 0., .7) == .7


def test_bank_direction_and_window():
  def steady(roll, yaw):
    c = CurveSpeed(.05)
    for _ in range(120):
      c.update(plan(yaw), roll, .1)
    return c.correction
  assert steady(.04, .18) == steady(-.04, -.18) < steady(-.04, .18)
  m = plan(0.)
  m.orientationRate.z[[0, 1, 4]] = 1.
  assert CurveSpeed(.05).update(m, 0., .3) == .3


@pytest.mark.parametrize('bad', ['shape', 'nan', 'time', 'roll'])
def test_invalid_data_clears_correction(bad):
  c, m = CurveSpeed(.05), plan()
  assert c.update(m, 0., .8) < .8
  if bad == 'shape':
    m.velocity.x = []
  elif bad == 'nan':
    m.orientationRate.z[2] = np.nan
  elif bad == 'time':
    m.position.t[2] = .4
  assert c.update(m, np.inf if bad == 'roll' else 0., .8) == .8
  assert c.gap.x == c.correction == 0.
