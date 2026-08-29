from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class HondaLiveTuning:
  generation: int
  override_fade_down_s: float
  override_fade_up_s: float
  override_torque_scale: float
  driver_assist_during_override: bool
  live_learning_gas: bool
  torque_lpf_enabled: bool
  lpf_tau_low: float
  lpf_tau_standard: float
  lpf_tau_highway: float
  steer_delta_limiter_enabled: bool
  steer_delta_up: float
  steer_delta_down: float
  stopping_decel_rate: float
  increase_override_tolerance: bool
  driver_override_threshold: float
  center_override_threshold: float
  center_boost_angle: float
  alt_dashboard_speed: int
  alt_dashboard_distance: int
  clear_dash_faults: bool
  spoof_camera_messages: bool
  sub_mode_enabled: bool
  sub_mode_until: float
  ecu_matched_long: bool
  full_brake_authority: bool
  roen_acceleration_limits: bool


class HondaConfigProvider(Protocol):
  """Runtime services owned by the embedding application, not opendbc."""

  def initialize_live_learning_gas(self, enable_gas_interceptor: bool) -> None: ...

  def get_live_tuning(self) -> HondaLiveTuning: ...

  def load_longitudinal_factors(self, car_fingerprint: str) -> tuple[float, float]: ...

  def persist_longitudinal_factors(self, gas_factor: float, wind_factor: float, car_fingerprint: str) -> None: ...


@dataclass(frozen=True, slots=True)
class HondaCarConfig:
  bosch_a_radar: bool
  enforce_stock_longitudinal: bool
  provider: HondaConfigProvider


@dataclass(frozen=True, slots=True)
class HyundaiCarConfig:
  longitudinal_tuning: int


@dataclass(frozen=True, slots=True)
class SubaruCarConfig:
  stop_and_go: bool
  stop_and_go_manual_parking_brake: bool


@dataclass(frozen=True, slots=True)
class TeslaCarConfig:
  cooperative_steering: bool
  mads_screen_button: int


@dataclass(frozen=True, slots=True)
class ToyotaCarConfig:
  enforce_stock_longitudinal: bool
  stop_and_go_hack: bool


@dataclass(frozen=True, slots=True)
class SunnypilotCarConfig:
  """Immutable, typed configuration passed into opendbc by its host."""

  honda: HondaCarConfig
  hyundai: HyundaiCarConfig
  subaru: SubaruCarConfig
  tesla: TeslaCarConfig
  toyota: ToyotaCarConfig


__all__ = (
  "HondaCarConfig",
  "HondaConfigProvider",
  "HondaLiveTuning",
  "HyundaiCarConfig",
  "SubaruCarConfig",
  "SunnypilotCarConfig",
  "TeslaCarConfig",
  "ToyotaCarConfig",
)
