"""UI-side admission preview. Runtime independently checks the latched selection."""
from openpilot.nrdr.params import read_settings
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile


FIRMWARE_DESCRIPTION = (
  "Use the matching modified-EPS firmware controller. Requires a separately confirmed EPS build. " +
  "Family/version detection cannot verify the flashed image. Configure while offroad; applies next drive."
)


def firmware_ready(CP, source) -> bool:
  settings = dict(read_settings(source))
  settings["NrdrLateralController"] = 1
  return firmware_controller_profile(CP, settings) is not None
