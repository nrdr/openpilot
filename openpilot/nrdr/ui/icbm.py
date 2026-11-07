"""ICBM presentation and saved preferences; runtime retains controller ownership."""
from opendbc.sunnypilot.car.honda.icbm_eligibility import civic_icbm_available


ICBM_DESCRIPTION = (
  "Adjusts factory ACC set speed using cruise-button commands. Factory ACC controls gas, brakes and following distance. " +
  "Civic: enable Honda Nidec Factory Longitudinal Control too. Applies next drive; no device reboot."
)


def icbm_available(CP, CP_SP) -> bool:
  if CP is None or CP_SP is None:
    return False
  # Old persistent CP_SP predates Civic admission. Refresh presentation without
  # pretending the controller for the previous drive has changed ownership.
  return bool(CP_SP.intelligentCruiseButtonManagementAvailable or civic_icbm_available(CP, CP_SP))


def save_icbm_choice(state, value) -> bool:
  if type(value) is not bool or not state.is_offroad() or not icbm_available(state.CP, state.CP_SP):
    return False
  state.params.put_bool("IntelligentCruiseButtonManagement", value, block=True)
  state.params.put_bool("OnroadCycleRequested", True, block=True)
  return True
