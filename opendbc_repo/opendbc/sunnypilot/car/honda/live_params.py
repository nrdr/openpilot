from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from threading import Event, Lock, Thread
import time
from types import MappingProxyType
from typing import Any


REFRESH_PERIOD = 10.0
FAST_REFRESH_PERIOD = 0.25
PARAM_GROUPS = (
  ("HondaOverrideFadeDownSecs", "HondaOverrideFadeUpSecs", "HondaOverrideTorqueScale", "HondaDriverAssistDuringOverride"),
  ("HondaTorqueLowPassFilter", "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway"),
  ("HondaSteerDeltaLimiter", "HondaSteerDeltaUp", "HondaSteerDeltaDown"),
  ("HondaLiveLearningGas", "HondaStoppingDecelRate", "NrdrHondaEcuMatchedLong",
   "NrdrHondaFullBrakeAuthority", "NrdrRoenAccelerationLimits"),
  ("HondaAltDashboardSpeed", "HondaAltDashboardDistance", "NrdrClearDashFaults", "HondaSpoofCameraMessages"),
  ("NrdrCruiseButtonSubMode",),
  ("NrdrDriverOverrideThreshold", "HondaCenterBoostThreshold", "NrdrOverrideThresholdCenterBoost",
   "NrdrIncreaseOverrideTolerance"),
)
FAST_PARAM_GROUP = ("NrdrHudSubModeUntil",)


def _bool_value(value: Any, default: bool = False) -> bool:
  if value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


@dataclass(frozen=True)
class HondaParamSnapshot:
  generation: int
  values: Mapping[str, Any]

  def get(self, key: str, **kwargs):
    return self.values.get(key)

  def get_bool(self, key: str, default: bool = False) -> bool:
    return _bool_value(self.values.get(key), default)


class HondaLiveParams:
  def __init__(self, params=None, refresh_period: float = REFRESH_PERIOD, start_worker: bool = True):
    if params is None:
      from openpilot.common.params import Params
      params = Params()
    self._params = params
    self._slot_period = refresh_period / len(PARAM_GROUPS)
    self._snapshot = HondaParamSnapshot(0, MappingProxyType({}))
    self._slot = 0
    self._lock = Lock()
    self._stop = Event()
    self._thread: Thread | None = None
    self.refresh_all()
    if start_worker:
      self._thread = Thread(target=self._run, name="honda-live-params", daemon=True)
      self._thread.start()

  @property
  def snapshot(self) -> HondaParamSnapshot:
    return self._snapshot

  def refresh_all(self) -> bool:
    with self._lock:
      values = dict(self._snapshot.values)
      for group in PARAM_GROUPS:
        if not self._read_group(group, values):
          return False
      if not self._read_group(FAST_PARAM_GROUP, values, allow_none=True):
        return False
      self._publish(values)
      self._slot = 0
      return True

  def poll_once(self) -> bool:
    with self._lock:
      group = PARAM_GROUPS[self._slot]
      self._slot = (self._slot + 1) % len(PARAM_GROUPS)
      return self._refresh_group(group)

  def poll_fast(self) -> bool:
    with self._lock:
      return self._refresh_group(FAST_PARAM_GROUP, allow_none=True)

  def close(self) -> None:
    self._stop.set()
    if self._thread is not None:
      self._thread.join(timeout=2.0)

  def _read_group(self, group: tuple[str, ...], values: dict[str, Any], allow_none: bool = False) -> bool:
    try:
      updated = {key: self._params.get(key) for key in group}
    except Exception:
      return False
    if not allow_none and any(value is None and values.get(key) is not None for key, value in updated.items()):
      return False
    values.update(updated)
    return True

  def _refresh_group(self, group: tuple[str, ...], allow_none: bool = False) -> bool:
    values = dict(self._snapshot.values)
    if not self._read_group(group, values, allow_none) or values == self._snapshot.values:
      return False
    self._publish(values)
    return True

  def _publish(self, values: Mapping[str, Any]) -> None:
    self._snapshot = HondaParamSnapshot(self._snapshot.generation + 1, MappingProxyType(dict(values)))

  def _run(self) -> None:
    try:
      from openpilot.common.realtime import drop_realtime, set_core_affinity
      drop_realtime()
      set_core_affinity(list(range(os.cpu_count() or 1)))
    except (ImportError, OSError):
      pass

    next_slow = time.monotonic() + self._slot_period
    next_fast = time.monotonic() + FAST_REFRESH_PERIOD
    while not self._stop.is_set():
      if self._stop.wait(max(0.0, min(next_slow, next_fast) - time.monotonic())):
        break
      now = time.monotonic()
      if now >= next_fast:
        self.poll_fast()
        next_fast = time.monotonic() + FAST_REFRESH_PERIOD
      if now >= next_slow:
        self.poll_once()
        next_slow = time.monotonic() + self._slot_period


_instance: HondaLiveParams | None = None
_instance_lock = Lock()


def get_honda_live_params() -> HondaLiveParams:
  global _instance
  with _instance_lock:
    if _instance is None:
      _instance = HondaLiveParams()
    return _instance


def reset_honda_live_params_for_tests() -> None:
  global _instance
  with _instance_lock:
    if _instance is not None:
      _instance.close()
    _instance = None
