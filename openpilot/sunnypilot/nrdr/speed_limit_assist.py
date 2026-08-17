from openpilot.cereal import custom
from opendbc.car.structs import car
from openpilot.sunnypilot.nrdr.speed_limit import SpeedLimitConfirmation
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import (
  ACTIVE_STATES,
  CRUISE_BUTTON_CONFIRM_HOLD,
  SpeedLimitAssist,
)


ButtonType = car.CarState.ButtonEvent.Type
AssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState


class NrdrSpeedLimitAssist(SpeedLimitAssist):
  def __init__(self, CP, CP_SP):
    super().__init__(CP, CP_SP)
    self._confirmation = SpeedLimitConfirmation(ButtonType, CRUISE_BUTTON_CONFIRM_HOLD)

  def update_buttons(self, release_toggle: int) -> None:
    released = self._release_toggle_prev ^ release_toggle
    self._release_toggle_prev = release_toggle
    self._confirmation.update(released)

  @property
  def target_set_speed_confirmed(self) -> bool:
    if self.pcm_op_long and self.state not in ACTIVE_STATES:
      return self._confirmation.consume()
    return super().target_set_speed_confirmed

  @property
  def v_cruise_cluster_changed(self) -> bool:
    changed = super().v_cruise_cluster_changed
    expected = not self.pcm_op_long and self.state == AssistState.active and super().target_set_speed_confirmed
    return changed and not expected

  def _update_non_pcm_long_confirmed_state(self) -> bool:
    return self._confirmation.consume(self.state == AssistState.preActive)
