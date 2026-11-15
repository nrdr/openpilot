"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car import structs
from opendbc.car.can_definitions import CanData
from opendbc.sunnypilot.car import create_gas_interceptor_command


class GasInterceptorCarController:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.gas = 0.
    self.interceptor_gas_cmd = 0.
    self.gasint_nolearn_ticks = 0
    self.last_gasint = 0.0

  def update(self, CC: structs.CarControl, CS: structs.CarState, gas: float, brake: float, wind_brake: float,
             packer, frame: int) -> list[CanData]:
    can_sends = []

    if self.CP_SP.enableGasInterceptor:
      # way too aggressive at low speed without this. The multiplier is the inverse of the measured
      # pedal -> accel gain relative to its value at 10 m/s: ACURA_ILX (routes 2752303cce1f0aba
      # 0000000c / 00000000) ~13 m/s2 per unit pedal below 3 m/s, ~8 at 6 m/s, ~5 at 10 m/s and
      # above. The old linear 0.4 -> 1.0 ramp sat 1.4-1.7x hot through 2-6 m/s, which is the
      # clutch-just-engaged regime where every launch overshot (2.6 m/s2 against a 1.5 plan at
      # 3 m/s); a scalar gasfactor cannot hold both that and the 10 m/s+ gain.
      gas_mult = np.interp(CS.out.vEgo, [0., 3., 6., 10.], [0.35, 0.4, 0.6, 1.0])
      # send exactly zero if apply_gas is zero. Interceptor will send the max between read value and apply_gas.
      # This prevents unexpected pedal range rescaling
      # Sending non-zero gas when OP is not enabled will cause the PCM not to respond to throttle as expected
      # when you do enable.
      if CC.longActive:
        self.gas = float(np.clip(gas_mult * (gas - brake + wind_brake * 3 / 4), 0., 1.))
      else:
        self.gas = 0.0
      send_gas = min(self.gas, self.last_gasint + 0.004)
      if send_gas != self.gas:
        self.gasint_nolearn_ticks = 25
        self.gas = send_gas
      self.last_gasint = self.gas
      can_sends.append(create_gas_interceptor_command(packer, self.gas, frame // 2))

    return can_sends
