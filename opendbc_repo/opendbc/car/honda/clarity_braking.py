"""Clarity pedal-interceptor calibration from Biscuit-Labs/openpilot 7edab57843."""
import numpy as np

from opendbc.car import structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, HondaSafetyFlagsSP


def qualified(CP, CP_SP) -> bool:
  return (CP.carFingerprint == CAR.HONDA_CLARITY and CP.openpilotLongitudinalControl and not CP.pcmCruise
          and not CP.dashcamOnly and len(CP.safetyConfigs) == 1
          and CP.safetyConfigs[0].safetyModel == structs.CarParams.SafetyModel.hondaNidec and CP.safetyConfigs[0].safetyParam == 0
          and CP_SP.safetyParam == (HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR | HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE)
          and bool(CP.flags & HondaFlags.NIDEC) and bool(CP.flags & HondaFlags.HYBRID)
          and not (CP.flags & HondaFlags.BOSCH) and CP_SP.enableGasInterceptor
          and bool(CP_SP.flags & HondaFlagsSP.NIDEC_HYBRID) and not (CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL))


PCM_GAS_BP = tuple(v * CV.MPH_TO_MS for v in (0., 2., 4., 6.5, 10., 18., 22., 27., 35.))
PCM_GAS_V = (38, 38, 48, 62, 66, 66, 74, 94, 98)
DECEL_BP = (0., 0.3, 0.7, 1.0, 1.27, 1.5, 1.7, 1.85, 2.2, 2.55, 2.7, 3.3)
BRAKE_V = (0, 8, 22, 38, 52, 95, 112, 130, 150, 170, 200, 320)
STANDSTILL_HOLD_BRAKE = 0.33


def hud_gas(v_ego: float) -> int:
  # Factory coasting/braking ACC_HUD allowance. Only valid with PCM_SPEED zero.
  return round(float(np.interp(v_ego, PCM_GAS_BP, PCM_GAS_V)))


def hybrid_brake_command(brake_fraction: float, v_ego: float) -> int:
  # Input is the post-wind brake fraction on Honda's accel/4.8 scale.
  measured = np.interp(brake_fraction * 4.8, DECEL_BP, BRAKE_V)
  linear_floor = brake_fraction * 256 * np.interp(v_ego, (1.3, 3.0), (1., 0.))
  return int(np.clip(max(measured, linear_floor), 0, BRAKE_V[-1]))


class StandstillHold:
  def __init__(self):
    self.latched = False

  def update(self, brake: float, standstill: bool, stopping: bool) -> float:
    self.latched = stopping and (standstill or self.latched)
    return max(brake, STANDSTILL_HOLD_BRAKE) if self.latched else brake
