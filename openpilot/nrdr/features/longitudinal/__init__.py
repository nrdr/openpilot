"""Public API for NRDR longitudinal control and planning features.

Runtime-heavy implementations are loaded lazily so importing the package does
not initialize controller dependencies during prebuild and source tooling.
"""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.features.longitudinal.long_tune import LongTune, write_tune
  from openpilot.nrdr.features.longitudinal.longcontrol import NrdrLongControl
  from openpilot.nrdr.features.longitudinal.longitudinal_mpc import MpcPolicyResult, NrdrLongitudinalMpc
  from openpilot.nrdr.features.longitudinal.longitudinal_planner import NrdrLongitudinalPlanner, apply_cruise_overspeed_allowance
  from openpilot.nrdr.features.longitudinal.longitudinal_stopping import compute_stopping_accel


__all__ = (
  "LongTune",
  "MpcPolicyResult",
  "NrdrLongControl",
  "NrdrLongitudinalMpc",
  "NrdrLongitudinalPlanner",
  "apply_cruise_overspeed_allowance",
  "compute_stopping_accel",
  "write_tune",
)
_EXPORT_MODULES = {
  "LongTune": "openpilot.nrdr.features.longitudinal.long_tune",
  "write_tune": "openpilot.nrdr.features.longitudinal.long_tune",
  "NrdrLongControl": "openpilot.nrdr.features.longitudinal.longcontrol",
  "MpcPolicyResult": "openpilot.nrdr.features.longitudinal.longitudinal_mpc",
  "NrdrLongitudinalMpc": "openpilot.nrdr.features.longitudinal.longitudinal_mpc",
  "NrdrLongitudinalPlanner": "openpilot.nrdr.features.longitudinal.longitudinal_planner",
  "apply_cruise_overspeed_allowance": "openpilot.nrdr.features.longitudinal.longitudinal_planner",
  "compute_stopping_accel": "openpilot.nrdr.features.longitudinal.longitudinal_stopping",
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
