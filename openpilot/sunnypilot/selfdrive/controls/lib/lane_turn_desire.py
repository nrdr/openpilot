"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import custom

from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.lateral import turn_desire_refresh
from openpilot.nrdr.features.lateral.turn_desire_refresh import TurnDesireRefresh

TurnDirection = custom.ModelDataV2SP.TurnDirection

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS


class LaneTurnController:
  def __init__(self, desire_helper):
    self.DH = desire_helper
    self.turn_direction = TurnDirection.none
    self.params = Params()
    self.lane_turn_value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.param_read_counter = 0
    self.enabled = self.params.get_bool("LaneTurnDesire")
    self.refresh = TurnDesireRefresh(TurnDirection.none, DT_MDL)
    self.refresh_enabled = turn_desire_refresh.enabled(self.params)
    self.held = False

  def read_params(self):
    self.enabled = self.params.get_bool("LaneTurnDesire")
    self.refresh_enabled = turn_desire_refresh.enabled(self.params)
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def update_lane_turn(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float,
                       steering_angle_deg: float = 0.0) -> None:
    if left_blinker and not right_blinker and v_ego < self.lane_turn_value and not blindspot_left:
      requested, wheel_toward = TurnDirection.turnLeft, steering_angle_deg
    elif right_blinker and not left_blinker and v_ego < self.lane_turn_value and not blindspot_right:
      requested, wheel_toward = TurnDirection.turnRight, -steering_angle_deg
    else:
      requested, wheel_toward = TurnDirection.none, 0.0
    # The request itself; the published direction may drop for one frame to re-issue the model's pulse.
    self.held = self.enabled and requested != TurnDirection.none
    self.turn_direction = self.refresh.update(requested, v_ego, wheel_toward, self.refresh_enabled and self.enabled)

  def get_turn_direction(self):
    if not self.enabled:
      return TurnDirection.none
    return self.turn_direction
