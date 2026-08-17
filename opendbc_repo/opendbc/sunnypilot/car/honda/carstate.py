from opendbc.car.honda.values import CAR, STEER_THRESHOLD
from opendbc.sunnypilot.car.honda.live_params import get_honda_live_params


class HondaCarStateFeatures:
  def __init__(self, CP):
    self.CP = CP
    self.params = get_honda_live_params()
    self.settings_generation = -1
    self.stock_threshold = STEER_THRESHOLD.get(CP.carFingerprint, 1200)
    self.sensitive_eps = CP.carFingerprint in (CAR.HONDA_CLARITY, CAR.HONDA_CIVIC, CAR.HONDA_CIVIC_BOSCH)
    self.driver_threshold = self.stock_threshold
    self.center_threshold = self.stock_threshold
    self.center_angle = 0.0
    self.increase_override_tolerance = False
    self._refresh_settings()

  def steering_pressed(self, steering_torque: float, steering_angle: float) -> bool:
    if self.settings_generation != self.params.snapshot.generation:
      self._refresh_settings()
    threshold = self.driver_threshold

    if self.center_angle > 0.0 and abs(steering_angle) <= self.center_angle:
      threshold = self.center_threshold

    if self.sensitive_eps and self.increase_override_tolerance:
      threshold *= 2
    return abs(steering_torque) > threshold

  def _refresh_settings(self) -> None:
    snapshot = self.params.snapshot
    self.driver_threshold = self._scaled_threshold(snapshot, "NrdrDriverOverrideThreshold", 1400)
    self.center_threshold = self._scaled_threshold(snapshot, "NrdrOverrideThresholdCenterBoost", 1000)
    try:
      self.center_angle = max(0.0, float(snapshot.get("HondaCenterBoostThreshold")))
    except (TypeError, ValueError):
      self.center_angle = 0.0
    self.increase_override_tolerance = snapshot.get_bool("NrdrIncreaseOverrideTolerance")
    self.settings_generation = snapshot.generation

  def _scaled_threshold(self, snapshot, key: str, default: float) -> float:
    try:
      value = int(snapshot.get(key))
    except (TypeError, ValueError):
      value = default
    if value <= 0:
      value = default
    return value if self.stock_threshold == 1200 else self.stock_threshold * value / 1200.0
