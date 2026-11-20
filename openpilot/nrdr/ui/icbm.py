"""ICBM presentation and saved preferences; runtime retains controller ownership."""
from opendbc.car.honda.values import CAR


ICBM_DESCRIPTION = (
  "Automatically adjusts factory ACC's set speed while the car controls acceleration, braking, and following distance. Off leaves set-speed changes to you."
)


def icbm_available(CP, CP_SP) -> bool:
  if CP is None or CP_SP is None:
    return False
  # Ignore stale availability cached by the retired Nidec Civic port.
  return bool(CP.carFingerprint != CAR.HONDA_CIVIC and CP_SP.intelligentCruiseButtonManagementAvailable)


def save_icbm_choice(state, value) -> bool:
  if type(value) is not bool or not state.is_offroad() or not icbm_available(state.CP, state.CP_SP):
    return False
  state.params.put_bool("IntelligentCruiseButtonManagement", value, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True
