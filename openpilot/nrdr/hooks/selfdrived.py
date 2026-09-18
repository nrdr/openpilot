import time

from openpilot.cereal import log, custom
from opendbc.car.structs import car
from openpilot.nrdr.features.driver_policy.hud_submode import consume_button_press
from openpilot.nrdr.features.longitudinal.policy import longitudinal_personality, nrdr_longitudinal_enabled


ButtonType = car.CarState.ButtonEvent.Type


class NrdrSelfdrive:
  def __init__(self, CP=None):
    self.longitudinal_enabled = nrdr_longitudinal_enabled(CP)
    self.sla_button_reserved_until = 0.0

  def reserve_distance_button(self, sla_state) -> bool:
    if not self.longitudinal_enabled:
      return False
    now = time.monotonic()
    if sla_state == custom.LongitudinalPlanSP.SpeedLimit.AssistState.preActive:
      self.sla_button_reserved_until = now + 0.75
    if now <= self.sla_button_reserved_until:
      return True
    self.sla_button_reserved_until = 0.0
    return False

  @staticmethod
  def update_personality(selfdrive, CS, button_reserved: bool) -> bool:
    if not selfdrive.CP.openpilotLongitudinalControl or button_reserved:
      return False

    changed = False
    distance_released = any(not event.pressed and event.type == ButtonType.gapAdjustCruise for event in CS.buttonEvents)
    enabled = nrdr_longitudinal_enabled(selfdrive.CP)
    selfdrive.personality = longitudinal_personality(selfdrive.personality, enabled)
    if distance_released and not selfdrive.experimental_mode_switched and (not enabled or consume_button_press(selfdrive.params)):
      count = len(log.LongitudinalPersonality.schema.enumerants) if enabled else 3
      selfdrive.personality = (selfdrive.personality - 1) % count
      selfdrive.params.put("LongitudinalPersonality", selfdrive.personality)
      changed = True

    if distance_released:
      selfdrive.experimental_mode_switched = False
    return changed
