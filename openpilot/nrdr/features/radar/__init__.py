"""Public API for NRDR radar tracking features."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.features.radar.radar import NrdrRadar
  from openpilot.nrdr.features.radar.radar_core import CivicBoschKalmanParams, CivicBoschTrack


__all__ = (
  "CivicBoschKalmanParams",
  "CivicBoschTrack",
  "NrdrRadar",
)
_EXPORT_MODULES = {
  "CivicBoschKalmanParams": "openpilot.nrdr.features.radar.radar_core",
  "CivicBoschTrack": "openpilot.nrdr.features.radar.radar_core",
  "NrdrRadar": "openpilot.nrdr.features.radar.radar",
}


def __getattr__(name: str):
  module_name = _EXPORT_MODULES.get(name)
  if module_name is None:
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

  value = getattr(import_module(module_name), name)
  globals()[name] = value
  return value


def __dir__() -> list[str]:
  return sorted((*globals(), *_EXPORT_MODULES))
