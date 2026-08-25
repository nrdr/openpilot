"""Public parameter access and metadata for NRDR.

Runtime readers are loaded lazily so build tools can import the standard-library
only parameter catalog before native Params dependencies have been compiled.
"""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.params.generated.keys import NrdrParamKey
  from openpilot.nrdr.params.store import ParamReader, ParamValue, read_bool, read_float


__all__ = ("NrdrParamKey", "ParamReader", "ParamValue", "read_bool", "read_float")
_EXPORT_MODULES = {
  "NrdrParamKey": "openpilot.nrdr.params.generated.keys",
  "ParamReader": "openpilot.nrdr.params.store",
  "ParamValue": "openpilot.nrdr.params.store",
  "read_bool": "openpilot.nrdr.params.store",
  "read_float": "openpilot.nrdr.params.store",
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
