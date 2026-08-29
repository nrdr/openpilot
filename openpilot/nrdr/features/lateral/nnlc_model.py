import os

from opendbc.car import structs

from openpilot.common.basedir import BASEDIR


__all__ = ("MODEL_PATHS", "get_forced_nnlc_model", "is_nnlc_forced")


MODEL_PATHS = {
  "HONDA_CLARITY": os.path.join(
    BASEDIR,
    "openpilot",
    "nrdr",
    "features",
    "lateral",
    "neural_network_lateral_control",
    "HONDA_CLARITY.json",
  ),
}


def get_forced_nnlc_model(CP: structs.CarParams) -> str | None:
  if CP.steerControlType == structs.CarParams.SteerControlType.angle:
    return None
  return MODEL_PATHS.get(str(CP.carFingerprint))


def is_nnlc_forced(CP: structs.CarParams) -> bool:
  return get_forced_nnlc_model(CP) is not None
