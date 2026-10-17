"""Small bare-only settings contract; read once before a drive, never in a frame loop."""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any
from collections.abc import Mapping


@dataclass(frozen=True)
class ParamDefinition:
  kind: str
  default: str


PARAMS = MappingProxyType({
  "NrdrLateralController": ParamDefinition("INT", "0"),
  "NrdrFirmwareImage": ParamDefinition("STRING", ""),
  "NrdrSteerRatioMode": ParamDefinition("INT", "1"),
  "NrdrSteerRatioManualCenter": ParamDefinition("FLOAT", "15.38"),
  "NrdrSteerRatioManualFinal": ParamDefinition("FLOAT", "10.93"),
  "NrdrSteerRatioHybrid": ParamDefinition("BOOL", "0"),
  "NrdrSteerRatioSourceB": ParamDefinition("INT", "3"),
  "NrdrSteerRatioBlendStart": ParamDefinition("FLOAT", "25"),
  "NrdrOptimizedLaneChanges": ParamDefinition("BOOL", "1"),
  "NrdrYawCommandDelayLow": ParamDefinition("FLOAT", "0.145"),
  "NrdrYawCommandDelayHigh": ParamDefinition("FLOAT", "0.025"),
})


def read_settings(source) -> Mapping[str, Any]:
  values = {}
  for key, definition in PARAMS.items():
    value = source.get(key)
    values[key] = definition.default if value is None else value
  return MappingProxyType(values)


def registry_lines() -> str:
  return "\n".join(f'    {{"{key}", {{PERSISTENT, {definition.kind}, "{definition.default}"}}}},'
                   for key, definition in PARAMS.items())
