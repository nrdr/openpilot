"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import log

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.sunnypilot.livedelay.helpers import get_lat_delay


class LagdToggle:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.params = Params()
    self.lag = 0.0

  def update(self, lag_msg: log.LateralDelay, cache: bool = True) -> None:
    self.lag = get_lat_delay(self.params, lag_msg.lateralDelay.lateralDelay, self.CP.steerActuatorDelay)
    lag_msg.lateralDelay.lateralDelay = self.lag
    if cache:
      self.params.put("LagdValueCache", self.lag)
