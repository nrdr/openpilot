from openpilot.common.pid import Gain, PIDController


__all__ = ("FeedforwardPIDController",)


class FeedforwardPIDController(PIDController):
  def __init__(self, k_p: Gain, k_i: Gain, k_d: Gain = 0.0, k_f: float = 1.0,
               pos_limit: float = 1e308, neg_limit: float = -1e308, rate: float = 100):
    super().__init__(k_p, k_i, k_d, pos_limit=pos_limit, neg_limit=neg_limit, rate=rate)
    self.k_f = k_f

  def update(self, error, error_rate=0.0, speed=0.0, feedforward=0.0, freeze_integrator=False):
    return super().update(error, error_rate=error_rate, speed=speed, feedforward=feedforward * self.k_f,
                          freeze_integrator=freeze_integrator)
