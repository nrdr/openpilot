"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.cereal import custom
from opendbc.car.structs import car
from opendbc.car import structs
from openpilot.common.params import Params

ButtonType = car.CarState.ButtonEvent.Type
EventNameSP = custom.OnroadEventSP.EventName

DISTANCE_LONG_PRESS = 50


class CruiseHelper:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.params = Params()

    self.button_frame_counts = {ButtonType.gapAdjustCruise: 0}
    self._experimental_mode = False
    self.experimental_mode_switched = False
    self.distance_button_consumed = False

  def update(self, CS, events, experimental_mode, distance_button_reserved=False) -> None:
    # Always observe releases, including while SLA owns the button or cruise
    # is unavailable. Suppressing actions must not suppress button bookkeeping.
    if self.button_frame_counts[ButtonType.gapAdjustCruise] == 0 and any(
      b.pressed and b.type == ButtonType.gapAdjustCruise for b in CS.buttonEvents
    ):
      self.distance_button_consumed = False
    self.update_button_frame_counts(CS)
    held = self.button_frame_counts[ButtonType.gapAdjustCruise] > 0
    available = self.CP.openpilotLongitudinalControl and CS.cruiseState.available
    if held and (distance_button_reserved or not available):
      # Do not reinterpret the tail of an SLA confirmation as an experimental
      # hold when the reservation expires. Require a fresh press after release.
      self.distance_button_consumed = True

    if available and not distance_button_reserved and not self.distance_button_consumed:
      self.update_experimental_mode(events, experimental_mode)

  def update_button_frame_counts(self, CS) -> None:
    for button in self.button_frame_counts:
      if self.button_frame_counts[button] > 0:
        self.button_frame_counts[button] += 1

    for button_event in CS.buttonEvents:
      button = button_event.type.raw
      if button in self.button_frame_counts:
        self.button_frame_counts[button] = int(button_event.pressed)

  def update_experimental_mode(self, events, experimental_mode) -> None:
    if self.button_frame_counts[ButtonType.gapAdjustCruise] >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      self._experimental_mode = not experimental_mode
      self.params.put_bool("ExperimentalMode", self._experimental_mode)
      events.add(EventNameSP.experimentalModeSwitched)
      self.experimental_mode_switched = True
