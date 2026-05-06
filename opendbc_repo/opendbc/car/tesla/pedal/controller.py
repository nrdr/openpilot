from numpy import clip, interp

from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.tesla.preap.nap_conf import (
  ACCEL_MAX,
  PEDAL_BP,
  PEDAL_DI_MIN,
  PEDAL_DI_ZERO,
  PEDAL_MAX_VALUES,
  REGEN_MAX,
  nap_conf,
)

PEDAL_RAMP_RATE_UP = 5.0
PEDAL_RAMP_RATE_DOWN = 2.5
ACCEL_DEADBAND = 0.15
PEDAL_HYST_GAP = 1.0
TORQUE_LEVEL_ACC = 0.0
TORQUE_LEVEL_DECEL = -30.0
ZERO_TORQUE_MIN_SPEED = 10.0 * CV.MPH_TO_MS


class PedalZeroTorque:
  def __init__(self):
    self.value = PEDAL_DI_ZERO
    self._best_torque = TORQUE_LEVEL_DECEL

  def update(self, torque_level: float, current_pedal_di: float, v_ego: float) -> None:
    if v_ego < ZERO_TORQUE_MIN_SPEED:
      return

    if TORQUE_LEVEL_DECEL < torque_level < TORQUE_LEVEL_ACC and abs(torque_level) < abs(self._best_torque):
      self.value = current_pedal_di
      self._best_torque = torque_level

  def get(self, v_ego: float) -> float:
    if v_ego < 5.0 * CV.MPH_TO_MS:
      return PEDAL_DI_ZERO
    return self.value


_zero_torque = PedalZeroTorque()


def get_zero_torque() -> PedalZeroTorque:
  return _zero_torque


def compute_pedal_command(accel_request: float, v_ego: float, prev_pedal_di: float) -> tuple[float, float]:
  max_pedal_value = float(interp(v_ego, PEDAL_BP, PEDAL_MAX_VALUES))
  zero_torque_di = _zero_torque.get(v_ego)

  if abs(accel_request) < ACCEL_DEADBAND:
    accel_request = 0.0

  pedal_di = float(interp(accel_request, [REGEN_MAX, 0.0, ACCEL_MAX], [PEDAL_DI_MIN, zero_torque_di, max_pedal_value]))
  pedal_di = float(clip(pedal_di, PEDAL_DI_MIN, max_pedal_value))
  pedal_di = float(clip(pedal_di, prev_pedal_di - PEDAL_RAMP_RATE_DOWN, prev_pedal_di + PEDAL_RAMP_RATE_UP))

  if abs(pedal_di - prev_pedal_di) < PEDAL_HYST_GAP:
    pedal_di = prev_pedal_di

  return nap_conf.di_to_pedal(pedal_di), pedal_di

