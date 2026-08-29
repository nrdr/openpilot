from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from opendbc.sunnypilot.car.runtime_config import (
  HondaCarConfig,
  HyundaiCarConfig,
  SubaruCarConfig,
  SunnypilotCarConfig,
  TeslaCarConfig,
  ToyotaCarConfig,
)

from openpilot.nrdr.car.opendbc import LEARNER_META_PATH, build_nrdr_honda_config


class SunnypilotCarParamKey(StrEnum):
  """Pre-existing SunnyPilot settings used to compose the opendbc boundary."""

  HONDA_ENFORCE_STOCK_LONGITUDINAL = "HondaEnforceStockLongitudinal"
  HYUNDAI_LONGITUDINAL_TUNING = "HyundaiLongitudinalTuning"
  SUBARU_STOP_AND_GO = "SubaruStopAndGo"
  SUBARU_STOP_AND_GO_MANUAL_PARKING_BRAKE = "SubaruStopAndGoManualParkingBrake"
  TESLA_COOPERATIVE_STEERING = "TeslaCoopSteering"
  TESLA_MADS_SCREEN_BUTTON = "TeslaMadsScreenButton"
  TOYOTA_ENFORCE_STOCK_LONGITUDINAL = "ToyotaEnforceStockLongitudinal"
  TOYOTA_STOP_AND_GO_HACK = "ToyotaStopAndGoHack"


_UNKNOWN = object()


def _read_param(params, key: SunnypilotCarParamKey):
  try:
    return params.get(str(key), return_default=True)
  except KeyError:
    return _UNKNOWN
  except Exception as error:
    if type(error).__name__ == "UnknownKeyName":
      return _UNKNOWN
    raise


def _bool_value(value: Any, default: bool = False) -> bool:
  if value is _UNKNOWN or value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def _float_value(value: Any, default: float) -> float:
  try:
    if isinstance(value, bytes):
      value = value.decode("utf-8")
    return default if value is _UNKNOWN or value is None else float(value)
  except (AttributeError, TypeError, ValueError):
    return default


def build_sunnypilot_car_config(params, *, start_worker: bool = True,
                                 metadata_path: Path = LEARNER_META_PATH) -> SunnypilotCarConfig:
  """Compose SunnyPilot's generic settings with NRDR's Honda-only policy."""

  nrdr_honda = build_nrdr_honda_config(params, start_worker=start_worker, metadata_path=metadata_path)
  honda_stock_longitudinal = _bool_value(
    _read_param(params, SunnypilotCarParamKey.HONDA_ENFORCE_STOCK_LONGITUDINAL),
  )
  return SunnypilotCarConfig(
    honda=HondaCarConfig(
      bosch_a_radar=nrdr_honda.bosch_a_radar,
      enforce_stock_longitudinal=honda_stock_longitudinal,
      provider=nrdr_honda.provider,
    ),
    hyundai=HyundaiCarConfig(
      longitudinal_tuning=int(_float_value(
        _read_param(params, SunnypilotCarParamKey.HYUNDAI_LONGITUDINAL_TUNING),
        0.0,
      )),
    ),
    subaru=SubaruCarConfig(
      stop_and_go=_bool_value(_read_param(params, SunnypilotCarParamKey.SUBARU_STOP_AND_GO)),
      stop_and_go_manual_parking_brake=_bool_value(
        _read_param(params, SunnypilotCarParamKey.SUBARU_STOP_AND_GO_MANUAL_PARKING_BRAKE),
      ),
    ),
    tesla=TeslaCarConfig(
      cooperative_steering=_bool_value(_read_param(params, SunnypilotCarParamKey.TESLA_COOPERATIVE_STEERING)),
      mads_screen_button=int(_float_value(
        _read_param(params, SunnypilotCarParamKey.TESLA_MADS_SCREEN_BUTTON),
        0.0,
      )),
    ),
    toyota=ToyotaCarConfig(
      enforce_stock_longitudinal=_bool_value(
        _read_param(params, SunnypilotCarParamKey.TOYOTA_ENFORCE_STOCK_LONGITUDINAL),
      ),
      stop_and_go_hack=_bool_value(_read_param(params, SunnypilotCarParamKey.TOYOTA_STOP_AND_GO_HACK)),
    ),
  )


__all__ = (
  "SunnypilotCarParamKey",
  "build_sunnypilot_car_config",
)
