from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from queue import Empty, SimpleQueue
from threading import Event, Lock, Thread
import time
from types import MappingProxyType
from typing import Any

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import STEER_RATIO_ENDPOINT_PROFILES


REFRESH_PERIOD = 10.0


@dataclass(frozen=True)
class ParamGroup:
  keys: tuple[str, ...]


@dataclass(frozen=True)
class ParamSnapshot:
  generation: int
  values: Mapping[str, Any]

  def get(self, key: str, block: bool = False, encoding: str | None = None, **kwargs):
    value = self.values.get(key)
    if encoding is not None and isinstance(value, bytes):
      return value.decode(encoding)
    return value

  def get_bool(self, key: str) -> bool:
    return _bool_value(self.values.get(key))


_STEER_RATIO_GROUPS = tuple(ParamGroup((profile.center_param, profile.outer_param))
                            for profile in STEER_RATIO_ENDPOINT_PROFILES)

CONTROL_GROUPS = (
  ParamGroup(("LatPScaleLowSpeed", "LatPScaleStandard", "LatPScaleHighway",
              "LatIScaleLowSpeed", "LatIScaleStandard", "LatIScaleHighway",
              "LatFScaleLowSpeed", "LatFScaleStandard", "LatFScaleHighway")),
  ParamGroup(("HondaCenterScale", "HondaCenterBoostThreshold", "HondaCenterBoostMinSpeed")),
  ParamGroup(("NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed")),
  ParamGroup(("HondaInjectionTest", "NrdrStarPilotPid", "NrdrLatStiction", "NrdrLaneChangeEndpointSteerRatio")),
  *_STEER_RATIO_GROUPS,
  ParamGroup(("NrdrTuneLearner", "NrdrTuneLearnerStrength", "NrdrTuneLearnerRate", "NrdrTuneLearnerReset")),
  ParamGroup(("NrdrNnlcEnabled", "NrdrNnlcActivationSpeed", "NrdrNnlcKpGain", "NrdrNnlcKfGain", "NrdrNnlcKiGain")),
  ParamGroup(("LongPidTuneScaleAggressive", "LongPidTuneScaleStandard", "LongPidTuneScaleRelaxed",
              "LongPidTuneScaleEcon", "HondaLiveLearningGas", "StaticFeedforwardLong", "HondaStopAccel",
              "HondaStoppingDecelRateLong", "HondaVEgoStarting", "HondaVEgoStopping",
              "NrdrRoenAccelerationLimits")),
  ParamGroup(("NrdrLearnSteerRatio", "NrdrLearnStiffness", "NrdrLearnAngleOffset")),
)

PLANNER_GROUPS = (
  ParamGroup(("HondaVEgoStopping", "NrdrCruiseMismatchCorrection", "NrdrCruiseOverspeedAllowance",
              "NrdrRoenAccelerationLimits")),
)


def _bool_value(value: Any, default: bool = False) -> bool:
  if value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


class LiveParams:
  def __init__(self, groups: tuple[ParamGroup, ...], params=None, refresh_period: float = REFRESH_PERIOD,
               start_worker: bool = True):
    if not groups:
      raise ValueError("at least one parameter group is required")
    if params is None:
      from openpilot.common.params import Params
      params = Params()
    self._params = params
    self._groups = groups
    self._slot_period = refresh_period / len(groups)
    self._snapshot = ParamSnapshot(0, MappingProxyType({}))
    self._slot = 0
    self._poll_lock = Lock()
    self._writes: SimpleQueue[tuple[str, Any, bool]] = SimpleQueue()
    self._stop = Event()
    self._wake = Event()
    self._thread: Thread | None = None
    self.refresh_all()
    if start_worker:
      self._thread = Thread(target=self._run, name="nrdr-live-params", daemon=True)
      self._thread.start()

  @property
  def snapshot(self) -> ParamSnapshot:
    return self._snapshot

  @property
  def generation(self) -> int:
    return self._snapshot.generation

  @property
  def groups(self) -> tuple[ParamGroup, ...]:
    return self._groups

  def get(self, key: str, block: bool = False, encoding: str | None = None, **kwargs):
    value = self._snapshot.values.get(key)
    if encoding is not None and isinstance(value, bytes):
      return value.decode(encoding)
    return value

  def get_bool(self, key: str) -> bool:
    return _bool_value(self._snapshot.values.get(key))

  def put_async(self, key: str, value: Any, *, is_bool: bool = False) -> None:
    self._writes.put((key, value, is_bool))
    self._wake.set()

  def refresh_all(self) -> bool:
    with self._poll_lock:
      values = dict(self._snapshot.values)
      for group in self._groups:
        if not self._read_group(group, values):
          return False
      self._publish(values)
      self._slot = 0
      return True

  def poll_once(self) -> bool:
    with self._poll_lock:
      values = dict(self._snapshot.values)
      group = self._groups[self._slot]
      self._slot = (self._slot + 1) % len(self._groups)
      if not self._read_group(group, values) or values == self._snapshot.values:
        return False
      self._publish(values)
      return True

  def close(self) -> None:
    self._stop.set()
    self._wake.set()
    if self._thread is not None:
      self._thread.join(timeout=2.0)

  def _read_group(self, group: ParamGroup, values: dict[str, Any]) -> bool:
    try:
      updated = {key: self._params.get(key) for key in group.keys}
    except Exception as error:
      self._warn("nrdr live parameter refresh failed: %s", error)
      return False
    if any(value is None and values.get(key) is not None for key, value in updated.items()):
      return False
    values.update(updated)
    return True

  def _publish(self, values: Mapping[str, Any]) -> None:
    self._snapshot = ParamSnapshot(self._snapshot.generation + 1, MappingProxyType(dict(values)))

  def _drain_writes(self) -> None:
    while True:
      try:
        key, value, is_bool = self._writes.get_nowait()
      except Empty:
        return
      try:
        if is_bool:
          self._params.put_bool(key, bool(value), block=True)
        else:
          self._params.put(key, value, block=True)
      except Exception:
        self._warn("nrdr async parameter write failed for %s", key)
        self._writes.put((key, value, is_bool))
        return

  def _run(self) -> None:
    try:
      from openpilot.common.realtime import drop_realtime, set_core_affinity
      drop_realtime()
      set_core_affinity(list(range(os.cpu_count() or 1)))
    except (ImportError, OSError):
      pass

    next_poll = time.monotonic() + self._slot_period
    while not self._stop.is_set():
      self._wake.wait(max(0.0, next_poll - time.monotonic()))
      self._wake.clear()
      self._drain_writes()
      now = time.monotonic()
      if now >= next_poll:
        self.poll_once()
        next_poll = time.monotonic() + self._slot_period

  @staticmethod
  def _warn(message: str, *args) -> None:
    try:
      from openpilot.common.swaglog import cloudlog
      cloudlog.warning(message, *args)
    except ImportError:
      pass


_instances: dict[str, LiveParams] = {}
_instances_lock = Lock()


def get_live_params(profile: str = "controlsd") -> LiveParams:
  groups = CONTROL_GROUPS if profile == "controlsd" else PLANNER_GROUPS if profile == "plannerd" else None
  if groups is None:
    raise ValueError(f"unknown live parameter profile: {profile}")
  with _instances_lock:
    if profile not in _instances:
      _instances[profile] = LiveParams(groups)
    return _instances[profile]


def reset_live_params_for_tests() -> None:
  with _instances_lock:
    for instance in _instances.values():
      instance.close()
    _instances.clear()
