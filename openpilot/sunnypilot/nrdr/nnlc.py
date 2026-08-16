from openpilot.common.constants import CV
from openpilot.common.realtime import DT_CTRL
from openpilot.sunnypilot.nrdr.nnlc_model import is_nnlc_forced
from openpilot.sunnypilot.nrdr.params import read_bool, read_float
from openpilot.sunnypilot.nrdr.pid import FeedforwardPIDController


class NrdrNnlc:
  REFRESH_FRAMES = 100
  DEFAULT_ACTIVATION_SPEED = 30.0

  def __init__(self, controller, CP):
    self.controller = controller
    self.base_enabled = controller.enabled or is_nnlc_forced(CP)
    self.frame = 0
    self.previous_curvature = 0.0
    controller.enabled = False
    controller.activation_speed_mps = self.DEFAULT_ACTIVATION_SPEED * CV.MPH_TO_MS
    controller._pid = FeedforwardPIDController(1.0, 0.1, k_f=0.5,
                                                pos_limit=controller.lac_torque.steer_max,
                                                neg_limit=-controller.lac_torque.steer_max)
    self.refresh()

  def refresh(self) -> None:
    controller = self.controller
    was_enabled = controller.enabled
    controller.enabled = self.base_enabled and read_bool(controller.params, "NrdrNnlcEnabled", False)
    if was_enabled and not controller.enabled:
      controller._pid.reset()
    activation_mph = read_float(controller.params, "NrdrNnlcActivationSpeed", self.DEFAULT_ACTIVATION_SPEED, 0.0, 100.0)
    controller.activation_speed_mps = activation_mph * CV.MPH_TO_MS
    controller._pid._k_p = [[0.0], [read_float(controller.params, "NrdrNnlcKpGain", 1.0, 0.0, 3.0, scale=100.0)]]
    controller._pid.k_f = read_float(controller.params, "NrdrNnlcKfGain", 0.5, 0.0, 3.0, scale=100.0)
    controller._pid._k_i = [[0.0], [read_float(controller.params, "NrdrNnlcKiGain", 0.1, 0.0, 3.0, scale=100.0)]]

  def update(self) -> None:
    if self.frame % self.REFRESH_FRAMES == 0:
      self.refresh()
    self.frame += 1

  def apply_curvature_model(self, CS, roll, past_lateral_accels, future_lateral_accels) -> bool:
    controller = self.controller
    if getattr(controller.model, "input_size", 18) != 12:
      return False

    speed_squared = max(CS.vEgo, 1.0) ** 2
    desired = controller._desired_curvature
    actual = controller._actual_curvature
    rate = (desired - self.previous_curvature) / DT_CTRL
    self.previous_curvature = desired
    past_curvatures = [accel / speed_squared for accel in past_lateral_accels]
    future_curvatures = [accel / speed_squared for accel in future_lateral_accels]

    def model_input(curvature):
      return [CS.vEgo, curvature, rate, curvature * speed_squared, *past_curvatures, *future_curvatures, roll]

    controller._ff = controller.model.evaluate(model_input(desired))
    controller._pid_log.error = controller._ff - controller.model.evaluate(model_input(actual))
    return True
