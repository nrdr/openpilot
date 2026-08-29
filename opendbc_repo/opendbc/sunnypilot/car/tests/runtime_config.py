from dataclasses import replace

from opendbc.sunnypilot.car.runtime_config import (
  HondaCarConfig,
  HondaLiveTuning,
  HyundaiCarConfig,
  SubaruCarConfig,
  SunnypilotCarConfig,
  TeslaCarConfig,
  ToyotaCarConfig,
)


class StaticHondaConfigProvider:
  def __init__(self):
    self.live_tuning = HondaLiveTuning(
      generation=1,
      override_fade_down_s=0.1,
      override_fade_up_s=0.1,
      override_torque_scale=0.0,
      driver_assist_during_override=True,
      live_learning_gas=True,
      torque_lpf_enabled=True,
      lpf_tau_low=0.1,
      lpf_tau_standard=0.1,
      lpf_tau_highway=0.05,
      steer_delta_limiter_enabled=False,
      steer_delta_up=3.0,
      steer_delta_down=3.0,
      stopping_decel_rate=0.3,
      increase_override_tolerance=False,
      driver_override_threshold=1400.0,
      center_override_threshold=1000.0,
      center_boost_angle=0.0,
      alt_dashboard_speed=0,
      alt_dashboard_distance=0,
      clear_dash_faults=True,
      spoof_camera_messages=False,
      sub_mode_enabled=False,
      sub_mode_until=0.0,
      ecu_matched_long=False,
      full_brake_authority=True,
      roen_acceleration_limits=True,
    )
    self.enable_gas_interceptor = None
    self.persisted = []

  def initialize_live_learning_gas(self, enable_gas_interceptor: bool) -> None:
    self.enable_gas_interceptor = enable_gas_interceptor

  def get_live_tuning(self) -> HondaLiveTuning:
    return self.live_tuning

  def load_longitudinal_factors(self, car_fingerprint: str) -> tuple[float, float]:
    return 1.0, 1.0

  def persist_longitudinal_factors(self, gas_factor: float, wind_factor: float, car_fingerprint: str) -> None:
    self.persisted.append((gas_factor, wind_factor, car_fingerprint))


def make_test_car_config(*, bosch_a_radar: bool = True, honda_stock_longitudinal: bool = False) -> SunnypilotCarConfig:
  return SunnypilotCarConfig(
    honda=HondaCarConfig(
      bosch_a_radar=bosch_a_radar,
      enforce_stock_longitudinal=honda_stock_longitudinal,
      provider=StaticHondaConfigProvider(),
    ),
    hyundai=HyundaiCarConfig(longitudinal_tuning=0),
    subaru=SubaruCarConfig(stop_and_go=False, stop_and_go_manual_parking_brake=False),
    tesla=TeslaCarConfig(cooperative_steering=False, mads_screen_button=0),
    toyota=ToyotaCarConfig(enforce_stock_longitudinal=False, stop_and_go_hack=False),
  )


def with_honda_config(config: SunnypilotCarConfig, **changes) -> SunnypilotCarConfig:
  return replace(config, honda=replace(config.honda, **changes))
