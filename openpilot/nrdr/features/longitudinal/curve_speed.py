"""Model curve-speed correction from commaai/openpilot #39242, 0b9989cc (MIT)."""
import numpy as np

from opendbc.car.lateral import AVERAGE_ROAD_ROLL
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter


class CurveSpeed:
  @classmethod
  def from_settings(cls, dt):
    from openpilot.common.params import Params
    return cls(dt) if Params().get_bool("NrdrCurveSpeed") else None

  def __init__(self, dt):
    self.gap = FirstOrderFilter(0., 0.2, dt)
    self.max_step = 2.0 * dt  # correction slew, m/s³ times seconds
    self.correction = 0.

  def reset(self):
    self.gap.x = self.correction = 0.

  def update(self, model, roll, accel):
    t, v, yaw = (np.asarray(x) for x in (model.position.t, model.velocity.x, model.orientationRate.z))
    if (t.size < 2 or t.shape != v.shape or t.shape != yaw.shape or not np.isfinite(roll) or
        not all(np.isfinite(x).all() for x in (t, v, yaw)) or not np.all(np.diff(t) > 0)):
      self.reset()
      return accel
    ahead = (t > .5) & (t < 6.)
    if not ahead.any():
      self.reset()
      return accel
    bank = np.clip(roll * np.sign(yaw[ahead]), -AVERAGE_ROAD_ROLL, AVERAGE_ROAD_ROLL)
    curvature = np.abs(yaw[ahead]) / np.maximum(v[ahead], 1.)
    v_max = np.sqrt((2.8 + ACCELERATION_DUE_TO_GRAVITY * bank) / np.maximum(curvature, 1e-4))
    gap = np.max((v[ahead] - v_max) / t[ahead], initial=0.)
    self.correction = float(np.clip(self.gap.update(gap), self.correction - self.max_step, self.correction + self.max_step))
    coast = max(accel, 0.) * np.interp(self.correction, [0., .3], [1., 0.]) + min(accel, 0.)
    return min(coast, max(accel - self.correction, -2.))
