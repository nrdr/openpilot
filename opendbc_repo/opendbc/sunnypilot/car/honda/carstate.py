from opendbc.car.honda.values import CAR, STEER_THRESHOLD
from opendbc.sunnypilot.car.runtime_config import HondaCarConfig


class HondaCarStateFeatures:
  def __init__(self, CP, config: HondaCarConfig):
    self.CP = CP
    self.config = config
    self.settings_generation = -1
    self.stock_threshold = STEER_THRESHOLD.get(CP.carFingerprint, 1200)
    self.sensitive_eps = CP.carFingerprint in (CAR.HONDA_CLARITY, CAR.HONDA_CIVIC, CAR.HONDA_CIVIC_BOSCH)
    self.driver_threshold = self.stock_threshold
    self.center_threshold = self.stock_threshold
    self.center_angle = 0.0
    self.increase_override_tolerance = False
    self._refresh_settings()

  def steering_pressed(self, steering_torque: float, steering_angle: float) -> bool:
    if self.settings_generation != self.config.provider.get_live_tuning().generation:
      self._refresh_settings()
    threshold = self.driver_threshold

    if self.center_angle > 0.0 and abs(steering_angle) <= self.center_angle:
      threshold = self.center_threshold

    if self.sensitive_eps and self.increase_override_tolerance:
      threshold *= 2
    return abs(steering_torque) > threshold

  def _refresh_settings(self) -> None:
    tuning = self.config.provider.get_live_tuning()
    self.driver_threshold = self._scaled_threshold(tuning.driver_override_threshold)
    self.center_threshold = self._scaled_threshold(tuning.center_override_threshold)
    self.center_angle = tuning.center_boost_angle
    self.increase_override_tolerance = tuning.increase_override_tolerance
    self.settings_generation = tuning.generation

  def _scaled_threshold(self, value: float) -> float:
    return value if self.stock_threshold == 1200 else self.stock_threshold * value / 1200.0
