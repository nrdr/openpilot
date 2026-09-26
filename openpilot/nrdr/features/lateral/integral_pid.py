"""VFN-style integral gain scheduling, scoped to NRDR's lateral PID.

Adapted from JamesL787/openpilot 662933847fcad19625dcfb8a6549331222087155.
Keep upstream accumulation/anti-windup intact; scale Ki, not the stored state.
"""

from openpilot.common.pid import PIDController


class IntegralScaledPIDController(PIDController):
  integrator_gain_scale = 1.0

  @property
  def k_i(self):
    return super().k_i * self.integrator_gain_scale

  def update(self, error, error_rate=0.0, speed=0.0, feedforward=0.0, freeze_integrator=False,
             integrator_gain_scale=1.0, reset_integrator=False):
    self.integrator_gain_scale = float(integrator_gain_scale)
    if reset_integrator:
      self.i = 0.0
    return super().update(error, error_rate, speed, feedforward, freeze_integrator)

  def update_lateral(self, error, *, feedforward, speed, i_scale, eps_modified,
                     steer_limited, steering_pressed, stiction_freeze):
    freeze_speed = 2.0 if eps_modified else 5.0
    return self.update(
      error, feedforward=feedforward, speed=speed,
      freeze_integrator=steer_limited or steering_pressed or speed < freeze_speed or stiction_freeze,
      integrator_gain_scale=i_scale,
      reset_integrator=i_scale <= 0.0 or (eps_modified and speed < freeze_speed),
    )
