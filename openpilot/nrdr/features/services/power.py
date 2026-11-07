"""NRDR ownership for the Prevent Automatic Shutdown runtime policy."""

from __future__ import annotations

from typing import Protocol

from openpilot.nrdr.params.generated.keys import NrdrParamKey


AUTOMATIC_POWER_DOWN_GRACE_S = 60


class _BoolParamReader(Protocol):
  def get_bool(self, key: str) -> bool: ...


class PreventAutomaticShutdownPolicy:
  """Gate automatic shutdowns while keeping manual power-off host-owned.

  The grace period starts only on a runtime ``True -> False`` transition.
  Starting with the setting disabled retains the host's normal shutdown
  behavior, and re-enabling it cancels any active grace period.
  """

  def __init__(self, params: _BoolParamReader):
    self._params = params
    self._disabled = self._read_disabled()
    self._grace_started_at: float | None = None

  def _read_disabled(self) -> bool:
    return self._params.get_bool(NrdrParamKey.DISABLE_POWER_DOWN)

  def allows_automatic_shutdown(self, now: float) -> bool:
    disabled = self._read_disabled()
    if disabled != self._disabled:
      self._grace_started_at = now if self._disabled else None
      self._disabled = disabled

    if self._grace_started_at is not None and now - self._grace_started_at >= AUTOMATIC_POWER_DOWN_GRACE_S:
      self._grace_started_at = None

    return not disabled and self._grace_started_at is None


__all__ = ("AUTOMATIC_POWER_DOWN_GRACE_S", "PreventAutomaticShutdownPolicy")
