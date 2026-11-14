"""Saved longitudinal selection; -1 preserves pre-selector installations."""
from enum import IntEnum


CONTROLLER_KEY = "NrdrLongitudinalController"
CONTROLLER_DESCRIPTION = (
  "Choose Standard, MVL adaptive control, Bosch-A Radar, or Aragon's speed-feedback pedal tune. "
  "Personal Pedal uses fixed personality gains and resets learned gas/wind compensation; changes apply next drive."
)
BOSCH_RADAR_WARNING = "Bosch-A Radar with Alpha Long does not restore factory emergency braking (AEB/CMBS)."


class LongitudinalController(IntEnum):
  STANDARD = 0
  MVL = 1
  BOSCH_RADAR = 2
  PERSONAL_PEDAL = 3


CONTROLLER_LABELS = ("Standard", "MVL Live Learning Gas", "Bosch-A Radar", "Aragon's Personal Pedal")


def decode_controller(value):
  if isinstance(value, bytes):
    value = value.decode("utf-8", errors="replace")
  if type(value) is bool:
    return None
  return {str(mode.value): mode for mode in LongitudinalController}.get(str(value))


def saved_controller(params, *, bosch_radar_available=False):
  selected = decode_controller(params.get(CONTROLLER_KEY))
  if selected is not None:
    return selected
  # Display the existing configuration without migrating or rewriting it.
  if params.get_bool("HondaLiveLearningGas"):
    return LongitudinalController.MVL
  if bosch_radar_available and params.get_bool("HondaBoschARadar"):
    return LongitudinalController.BOSCH_RADAR
  return LongitudinalController.STANDARD
