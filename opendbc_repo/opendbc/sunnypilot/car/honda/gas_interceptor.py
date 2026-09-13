"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car import structs
from opendbc.car.can_definitions import CanData
from opendbc.sunnypilot.car import create_gas_interceptor_command


def gas_multiplier(v_ego: float, roen_acceleration_limits: bool) -> float:
  return 1.0 if roen_acceleration_limits else float(np.interp(v_ego, [0.0, 10.0], [0.4, 1.0]))


class GasInterceptorCarController:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.gas = 0.
    self.interceptor_gas_cmd = 0.

  def update(self, CC: structs.CarControl, CS: structs.CarState, gas: float, brake: float, wind_brake: float,
             packer, frame: int, roen_acceleration_limits: bool = False) -> list[CanData]:
    can_sends = []

    if self.CP_SP.enableGasInterceptor:
      # Taper low-speed gas and send an exact zero while longitudinal control is inactive.
      gas_mult = gas_multiplier(CS.out.vEgo, roen_acceleration_limits)
      if CC.longActive:
        self.gas = float(np.clip(gas_mult * (gas - brake + wind_brake * 3 / 4), 0., 1.))
      else:
        self.gas = 0.0
      can_sends.append(create_gas_interceptor_command(packer, self.gas, frame // 2))

    return can_sends
