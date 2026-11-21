"""Typed, read-only access to NRDR parameter values.

This module contains conversions only.  It never constructs ``Params`` and
does not perform writes, which keeps storage lifetime and refresh policy in the
calling process.  On-road features should pass an already-cached reader or
immutable snapshot rather than call persistent storage from their update loop.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from openpilot.common.params import UnknownKeyName


type ParamValue = bytes | str | bool | int | float | None


@runtime_checkable
class ParamReader(Protocol):
  """Smallest read-only interface accepted by the typed conversion helpers."""

  def get(self, key: str) -> ParamValue: ...


def read_bool(params: ParamReader, key: str, default: bool = False) -> bool:
  """Read a bool while preserving NRDR's historical coercion semantics."""

  try:
    value = params.get(key)
  except UnknownKeyName:
    return default
  if value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def read_float(params: ParamReader, key: str, default: float, min_value: float | None = None, max_value: float | None = None, scale: float = 1.0) -> float:
  """Read, scale, and clamp a float using NRDR's historical fallbacks."""

  try:
    value = params.get(key)
  except UnknownKeyName:
    value = None

  try:
    value = default if value is None else float(value.decode() if isinstance(value, bytes) else value) / scale
  except (TypeError, ValueError):
    value = default

  if min_value is not None:
    value = max(min_value, value)
  if max_value is not None:
    value = min(max_value, value)
  return value
