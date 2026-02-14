import numpy as np
from numbers import Number


class PIDController:
  """
  PID controller with optional speed-scheduled gains.

  Supports:
    - k_p, k_i, k_d as scalars or [bp, values]
    - feedforward gain k_f
    - optional proportional clamps (pos_p_limit / neg_p_limit)
  """
  def __init__(self, k_p, k_i, k_f=0.0, k_d=0.0,
               pos_limit=1e308, neg_limit=-1e308, rate=100,
               pos_p_limit=None, neg_p_limit=None):
    self._k_p = [[0.0], [float(k_p)]] if isinstance(k_p, Number) else k_p
    self._k_i = [[0.0], [float(k_i)]] if isinstance(k_i, Number) else k_i
    self._k_d = [[0.0], [float(k_d)]] if isinstance(k_d, Number) else k_d

    self.k_f = float(k_f)

    self.pos_p_limit = pos_p_limit
    self.neg_p_limit = neg_p_limit

    self.set_limits(pos_limit, neg_limit)

    self.i_dt = 1.0 / float(rate)
    self.speed = 0.0

    self.reset()

  @property
  def k_p(self):
    return float(np.interp(self.speed, self._k_p[0], self._k_p[1]))

  @property
  def k_i(self):
    return float(np.interp(self.speed, self._k_i[0], self._k_i[1]))

  @property
  def k_d(self):
    return float(np.interp(self.speed, self._k_d[0], self._k_d[1]))

  def reset(self):
    self.p = 0.0
    self.i = 0.0
    self.d = 0.0
    self.f = 0.0
    self.control = 0.0

  def set_limits(self, pos_limit, neg_limit):
    self.pos_limit = float(pos_limit)
    self.neg_limit = float(neg_limit)

  def update(self, error, error_rate=0.0, speed=0.0, feedforward=0.0, freeze_integrator=False):
    self.speed = float(speed)

    self.p = float(error) * self.k_p
    if self.pos_p_limit is not None and self.p > self.pos_p_limit:
      self.p = float(self.pos_p_limit)
    elif self.neg_p_limit is not None and self.p < self.neg_p_limit:
      self.p = float(self.neg_p_limit)

    self.d = float(error_rate) * self.k_d
    self.f = float(feedforward) * self.k_f

    if not freeze_integrator:
      i_candidate = self.i + float(error) * self.k_i * self.i_dt

      # Prevent integrator windup when output would clip.
      test_control = self.p + i_candidate + self.d + self.f
      i_upperbound = self.i if test_control > self.pos_limit else self.pos_limit
      i_lowerbound = self.i if test_control < self.neg_limit else self.neg_limit
      self.i = float(np.clip(i_candidate, i_lowerbound, i_upperbound))

    control = self.p + self.i + self.d + self.f
    self.control = float(np.clip(control, self.neg_limit, self.pos_limit))
    return self.control
