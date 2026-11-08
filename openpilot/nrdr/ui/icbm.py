"""ICBM presentation and saved preferences; runtime retains controller ownership."""
from opendbc.car.honda.values import CAR


ICBM_DESCRIPTION = (
  "Adjusts factory ACC set speed using cruise-button commands. Factory ACC controls gas, brakes and following distance. " +
  "Applies next drive; no device reboot."
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
