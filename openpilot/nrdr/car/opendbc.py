from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import math
import os
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Lock, Thread
import time
from types import MappingProxyType
from typing import Any

from opendbc.sunnypilot.car.honda.longitudinal import LEARN_VERSION
from opendbc.sunnypilot.car.runtime_config import HondaLiveTuning

from openpilot.nrdr.params.generated.keys import NrdrParamKey


REFRESH_PERIOD = 10.0
FAST_REFRESH_PERIOD = 0.25
LEARNER_META_PATH = Path("/data/honda_learner_meta.json")
LONG_FACTOR_MIN = 0.6
LONG_FACTOR_MAX = 1.6
GAS_ALPHA_MIN = 0.0
GAS_ALPHA_MAX = 0.4
LONG_STATE_DIGEST_VERSION = 1
LONG_STATE_LEGACY_METADATA_KEYS = frozenset(("car_fingerprint", "learn_version"))
LONG_STATE_METADATA_KEYS = LONG_STATE_LEGACY_METADATA_KEYS | frozenset((
  "longitudinal_state_sha256", "pending", "state_digest_version",
))


class NrdrHondaParamKey(StrEnum):
  """NRDR-owned Honda keys consumed across the openpilot-to-opendbc boundary."""

  HONDA_BOSCH_A_RADAR = NrdrParamKey.HONDA_BOSCH_A_RADAR
  HONDA_GAS_ALPHA = "HondaGasAlphaParams"
  HONDA_GAS_FACTOR = "HondaGasFactorParams"
  HONDA_WIND_FACTOR = "HondaWindFactorParams"
  HONDA_OVERRIDE_FADE_DOWN_SECS = NrdrParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS
  HONDA_OVERRIDE_FADE_UP_SECS = NrdrParamKey.HONDA_OVERRIDE_FADE_UP_SECS
  HONDA_OVERRIDE_TORQUE_SCALE = NrdrParamKey.HONDA_OVERRIDE_TORQUE_SCALE
  HONDA_DRIVER_ASSIST_DURING_OVERRIDE = NrdrParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE
  HONDA_LIVE_LEARNING_GAS = NrdrParamKey.HONDA_LIVE_LEARNING_GAS
  HONDA_TORQUE_LOW_PASS_FILTER = NrdrParamKey.HONDA_TORQUE_LOW_PASS_FILTER
  HONDA_LPF_TAU_LOW_SPEED = NrdrParamKey.HONDA_LPF_TAU_LOW_SPEED
  HONDA_LPF_TAU_STANDARD = NrdrParamKey.HONDA_LPF_TAU_STANDARD
  HONDA_LPF_TAU_HIGHWAY = NrdrParamKey.HONDA_LPF_TAU_HIGHWAY
  HONDA_STEER_DELTA_LIMITER = NrdrParamKey.HONDA_STEER_DELTA_LIMITER
  HONDA_STEER_DELTA_UP = NrdrParamKey.HONDA_STEER_DELTA_UP
  HONDA_STEER_DELTA_DOWN = NrdrParamKey.HONDA_STEER_DELTA_DOWN
  HONDA_STOPPING_DECEL_RATE = NrdrParamKey.HONDA_STOPPING_DECEL_RATE
  NRDR_INCREASE_OVERRIDE_TOLERANCE = NrdrParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE
  NRDR_DRIVER_OVERRIDE_THRESHOLD = NrdrParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD
  HONDA_CENTER_BOOST_THRESHOLD = NrdrParamKey.HONDA_CENTER_BOOST_THRESHOLD
  NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST = NrdrParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST
  HONDA_ALT_DASHBOARD_SPEED = NrdrParamKey.HONDA_ALT_DASHBOARD_SPEED
  HONDA_ALT_DASHBOARD_DISTANCE = NrdrParamKey.HONDA_ALT_DASHBOARD_DISTANCE
  NRDR_CLEAR_DASH_FAULTS = NrdrParamKey.NRDR_CLEAR_DASH_FAULTS
  HONDA_SPOOF_CAMERA_MESSAGES = NrdrParamKey.HONDA_SPOOF_CAMERA_MESSAGES
  NRDR_CRUISE_BUTTON_SUB_MODE = NrdrParamKey.NRDR_CRUISE_BUTTON_SUB_MODE
  NRDR_HUD_SUB_MODE_UNTIL = NrdrParamKey.NRDR_HUD_SUB_MODE_UNTIL
  NRDR_HONDA_ECU_MATCHED_LONG = NrdrParamKey.NRDR_HONDA_ECU_MATCHED_LONG
  NRDR_HONDA_FULL_BRAKE_AUTHORITY = NrdrParamKey.NRDR_HONDA_FULL_BRAKE_AUTHORITY
  NRDR_ROEN_ACCELERATION_LIMITS = NrdrParamKey.NRDR_ROEN_ACCELERATION_LIMITS


# Compatibility name for the typed key enum introduced with the first boundary.
# Its membership is now deliberately limited to NRDR-owned Honda policy.
OpendbcParamKey = NrdrHondaParamKey


SLOW_PARAM_GROUPS = (
  (
    OpendbcParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS,
    OpendbcParamKey.HONDA_OVERRIDE_FADE_UP_SECS,
    OpendbcParamKey.HONDA_OVERRIDE_TORQUE_SCALE,
    OpendbcParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE,
  ),
  (
    OpendbcParamKey.HONDA_TORQUE_LOW_PASS_FILTER,
    OpendbcParamKey.HONDA_LPF_TAU_LOW_SPEED,
    OpendbcParamKey.HONDA_LPF_TAU_STANDARD,
    OpendbcParamKey.HONDA_LPF_TAU_HIGHWAY,
  ),
  (
    OpendbcParamKey.HONDA_STEER_DELTA_LIMITER,
    OpendbcParamKey.HONDA_STEER_DELTA_UP,
    OpendbcParamKey.HONDA_STEER_DELTA_DOWN,
  ),
  (
    OpendbcParamKey.HONDA_LIVE_LEARNING_GAS,
    OpendbcParamKey.HONDA_STOPPING_DECEL_RATE,
    OpendbcParamKey.NRDR_HONDA_ECU_MATCHED_LONG,
    OpendbcParamKey.NRDR_HONDA_FULL_BRAKE_AUTHORITY,
    OpendbcParamKey.NRDR_ROEN_ACCELERATION_LIMITS,
  ),
  (
    OpendbcParamKey.HONDA_ALT_DASHBOARD_SPEED,
    OpendbcParamKey.HONDA_ALT_DASHBOARD_DISTANCE,
    OpendbcParamKey.NRDR_CLEAR_DASH_FAULTS,
    OpendbcParamKey.HONDA_SPOOF_CAMERA_MESSAGES,
  ),
  (OpendbcParamKey.NRDR_CRUISE_BUTTON_SUB_MODE,),
  (
    OpendbcParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD,
    OpendbcParamKey.HONDA_CENTER_BOOST_THRESHOLD,
    OpendbcParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST,
    OpendbcParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE,
  ),
)
FAST_PARAM_GROUP = (OpendbcParamKey.NRDR_HUD_SUB_MODE_UNTIL,)


_UNKNOWN = object()


def _longitudinal_value_digest(*values: float) -> str:
  payload = "|".join(format(float(value), ".17g") for value in values).encode("ascii")
  return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class _RawSnapshot:
  generation: int
  values: Mapping[OpendbcParamKey, Any]


def _read_param(params, key: OpendbcParamKey, *, return_default: bool = False):
  try:
    return params.get(str(key), return_default=return_default)
  except KeyError:
    return _UNKNOWN
  except Exception as error:
    if type(error).__name__ == "UnknownKeyName":
      return _UNKNOWN
    raise


def _bool_value(value: Any, default: bool) -> bool:
  if value is _UNKNOWN or value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def _float_value(value: Any, default: float, min_value: float | None = None,
                 max_value: float | None = None, scale: float = 1.0) -> float:
  try:
    if isinstance(value, bytes):
      value = value.decode("utf-8")
    result = default if value is _UNKNOWN or value is None else float(value) / scale
  except (AttributeError, TypeError, ValueError):
    result = default
  if min_value is not None:
    result = max(min_value, result)
  if max_value is not None:
    result = min(max_value, result)
  return result


def _positive_threshold(value: Any, default: float) -> float:
  try:
    result = int(value)
  except (TypeError, ValueError):
    result = int(default)
  return float(result if result > 0 else default)


class HondaParamsProvider:
  """Owns Honda Params I/O and publishes immutable typed snapshots to opendbc."""

  def __init__(self, params, *, refresh_period: float = REFRESH_PERIOD, start_worker: bool = True,
               metadata_path: Path = LEARNER_META_PATH):
    self._params = params
    self._metadata_path = Path(metadata_path)
    self._slot_period = refresh_period / len(SLOW_PARAM_GROUPS)
    self._snapshot = _RawSnapshot(0, MappingProxyType({}))
    self._slot = 0
    self._poll_lock = Lock()
    self._worker_lock = Lock()
    self._stop = Event()
    self._poll_thread: Thread | None = None
    self._write_thread: Thread | None = None
    self._write_queue: Queue[tuple[float, float, float, str] | None] = Queue()
    self._live_learning_default = True
    self._tuning_cache: HondaLiveTuning | None = None
    self._workers_enabled = start_worker
    self._workers_started = False

  def close(self) -> None:
    self._stop.set()
    self._write_queue.put(None)
    if self._poll_thread is not None:
      self._poll_thread.join(timeout=2.0)
    if self._write_thread is not None:
      self._write_thread.join(timeout=2.0)

  def initialize_live_learning_gas(self, enable_gas_interceptor: bool) -> None:
    self._live_learning_default = not enable_gas_interceptor
    value = _read_param(self._params, OpendbcParamKey.HONDA_LIVE_LEARNING_GAS)
    if value is None:
      self._params.put_bool(
        str(OpendbcParamKey.HONDA_LIVE_LEARNING_GAS),
        self._live_learning_default,
        block=True,
      )
    self.refresh_all()
    self._start_workers()

  def get_live_tuning(self) -> HondaLiveTuning:
    if self._snapshot.generation == 0:
      self.refresh_all()
    snapshot = self._snapshot
    cached = self._tuning_cache
    if cached is not None and cached.generation == snapshot.generation:
      return cached

    values = snapshot.values
    tuning = HondaLiveTuning(
      generation=snapshot.generation,
      override_fade_down_s=_float_value(values.get(OpendbcParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS), 0.1, 0.0, 10.0),
      override_fade_up_s=_float_value(values.get(OpendbcParamKey.HONDA_OVERRIDE_FADE_UP_SECS), 0.1, 0.0, 10.0),
      override_torque_scale=_float_value(values.get(OpendbcParamKey.HONDA_OVERRIDE_TORQUE_SCALE), 0.0, 0.0, 100.0, 100.0),
      driver_assist_during_override=_bool_value(values.get(OpendbcParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE), True),
      live_learning_gas=_bool_value(values.get(OpendbcParamKey.HONDA_LIVE_LEARNING_GAS), self._live_learning_default),
      torque_lpf_enabled=_bool_value(values.get(OpendbcParamKey.HONDA_TORQUE_LOW_PASS_FILTER), True),
      lpf_tau_low=_float_value(values.get(OpendbcParamKey.HONDA_LPF_TAU_LOW_SPEED), 0.1, 0.0, 5.0),
      lpf_tau_standard=_float_value(values.get(OpendbcParamKey.HONDA_LPF_TAU_STANDARD), 0.1, 0.0, 5.0),
      lpf_tau_highway=_float_value(values.get(OpendbcParamKey.HONDA_LPF_TAU_HIGHWAY), 0.05, 0.0, 5.0),
      steer_delta_limiter_enabled=_bool_value(values.get(OpendbcParamKey.HONDA_STEER_DELTA_LIMITER), False),
      steer_delta_up=_float_value(values.get(OpendbcParamKey.HONDA_STEER_DELTA_UP), 3.0, 0.0, 100.0),
      steer_delta_down=_float_value(values.get(OpendbcParamKey.HONDA_STEER_DELTA_DOWN), 3.0, 0.0, 100.0),
      stopping_decel_rate=_float_value(values.get(OpendbcParamKey.HONDA_STOPPING_DECEL_RATE), 0.3, 0.0, 1.0, 100.0),
      increase_override_tolerance=_bool_value(values.get(OpendbcParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE), False),
      driver_override_threshold=_positive_threshold(values.get(OpendbcParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD), 1400.0),
      center_override_threshold=_positive_threshold(values.get(OpendbcParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST), 1000.0),
      center_boost_angle=_float_value(values.get(OpendbcParamKey.HONDA_CENTER_BOOST_THRESHOLD), 0.0, 0.0),
      alt_dashboard_speed=int(_float_value(values.get(OpendbcParamKey.HONDA_ALT_DASHBOARD_SPEED), 0.0, 0.0, 3.0)),
      alt_dashboard_distance=int(_float_value(values.get(OpendbcParamKey.HONDA_ALT_DASHBOARD_DISTANCE), 0.0, 0.0, 2.0)),
      clear_dash_faults=_bool_value(values.get(OpendbcParamKey.NRDR_CLEAR_DASH_FAULTS), True),
      spoof_camera_messages=_bool_value(values.get(OpendbcParamKey.HONDA_SPOOF_CAMERA_MESSAGES), False),
      sub_mode_enabled=_bool_value(values.get(OpendbcParamKey.NRDR_CRUISE_BUTTON_SUB_MODE), False),
      sub_mode_until=_float_value(values.get(OpendbcParamKey.NRDR_HUD_SUB_MODE_UNTIL), 0.0, 0.0),
      ecu_matched_long=_bool_value(values.get(OpendbcParamKey.NRDR_HONDA_ECU_MATCHED_LONG), False),
      full_brake_authority=_bool_value(values.get(OpendbcParamKey.NRDR_HONDA_FULL_BRAKE_AUTHORITY), True),
      roen_acceleration_limits=_bool_value(values.get(OpendbcParamKey.NRDR_ROEN_ACCELERATION_LIMITS), True),
    )
    self._tuning_cache = tuning
    return tuning

  def refresh_all(self) -> bool:
    with self._poll_lock:
      values = dict(self._snapshot.values)
      for group in SLOW_PARAM_GROUPS:
        if not self._read_group(group, values):
          return False
      if not self._read_group(FAST_PARAM_GROUP, values, allow_none=True):
        return False
      self._publish(values)
      self._slot = 0
      return True

  def poll_once(self) -> bool:
    with self._poll_lock:
      values = dict(self._snapshot.values)
      group = SLOW_PARAM_GROUPS[self._slot]
      self._slot = (self._slot + 1) % len(SLOW_PARAM_GROUPS)
      if not self._read_group(group, values) or values == self._snapshot.values:
        return False
      self._publish(values)
      return True

  def poll_fast(self) -> bool:
    with self._poll_lock:
      values = dict(self._snapshot.values)
      if not self._read_group(FAST_PARAM_GROUP, values, allow_none=True) or values == self._snapshot.values:
        return False
      self._publish(values)
      return True

  def load_longitudinal_factors(self, car_fingerprint: str) -> tuple[float, float]:
    _, gas, wind = self._load_longitudinal_state(car_fingerprint)
    return gas, wind

  def load_gas_alpha(self, car_fingerprint: str) -> float:
    alpha, _, _ = self._load_longitudinal_state(car_fingerprint)
    return alpha

  def _load_longitudinal_state(self, car_fingerprint: str) -> tuple[float, float, float]:
    default = (GAS_ALPHA_MIN, 1.0, 1.0)
    try:
      metadata = json.loads(self._metadata_path.read_text(encoding="utf-8"))
      if not isinstance(metadata, Mapping):
        return default
      if metadata.get("car_fingerprint") != car_fingerprint or metadata.get("learn_version") != LEARN_VERSION:
        return default

      digest_version = metadata.get("state_digest_version")
      if digest_version is None:
        if frozenset(metadata) != LONG_STATE_LEGACY_METADATA_KEYS:
          return default
      elif (type(digest_version) is not int or digest_version != LONG_STATE_DIGEST_VERSION or
            frozenset(metadata) != LONG_STATE_METADATA_KEYS or metadata.get("pending") is not False):
        return default

      raw_alpha = _read_param(self._params, OpendbcParamKey.HONDA_GAS_ALPHA)
      raw_gas = _read_param(self._params, OpendbcParamKey.HONDA_GAS_FACTOR)
      raw_wind = _read_param(self._params, OpendbcParamKey.HONDA_WIND_FACTOR)
      if raw_gas is _UNKNOWN or raw_wind is _UNKNOWN or raw_gas is None or raw_wind is None:
        return default

      if type(digest_version) is int and digest_version == LONG_STATE_DIGEST_VERSION:
        if raw_alpha is _UNKNOWN or raw_alpha is None:
          return default

      alpha = (
        GAS_ALPHA_MIN if raw_alpha is _UNKNOWN or raw_alpha is None else
        float(raw_alpha.decode("utf-8") if isinstance(raw_alpha, bytes) else raw_alpha)
      )
      gas = float(raw_gas.decode("utf-8") if isinstance(raw_gas, bytes) else raw_gas)
      wind = float(raw_wind.decode("utf-8") if isinstance(raw_wind, bytes) else raw_wind)
      if not all(math.isfinite(value) for value in (alpha, gas, wind)):
        return default

      # An intent commit always precedes Param writes. Re-reading metadata closes
      # the race where a legacy reader saw old metadata immediately before that
      # transition and would otherwise accept a partially written state.
      committed_metadata = json.loads(self._metadata_path.read_text(encoding="utf-8"))
      if not isinstance(committed_metadata, Mapping) or committed_metadata != metadata:
        return default
      if type(digest_version) is int and digest_version == LONG_STATE_DIGEST_VERSION:
        expected = metadata.get("longitudinal_state_sha256")
        if not isinstance(expected, str) or expected != _longitudinal_value_digest(alpha, gas, wind):
          return default
      return (
        min(GAS_ALPHA_MAX, max(GAS_ALPHA_MIN, alpha)),
        min(LONG_FACTOR_MAX, max(LONG_FACTOR_MIN, gas)),
        min(LONG_FACTOR_MAX, max(LONG_FACTOR_MIN, wind)),
      )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
      return default

  def persist_longitudinal_state(self, gas_alpha: float, gas_factor: float, wind_factor: float,
                                 car_fingerprint: str) -> None:
    try:
      values = tuple(float(value) for value in (gas_alpha, gas_factor, wind_factor))
    except (TypeError, ValueError):
      return
    if not car_fingerprint or not all(math.isfinite(value) for value in values):
      return

    gas_alpha = min(GAS_ALPHA_MAX, max(GAS_ALPHA_MIN, values[0]))
    gas_factor = min(LONG_FACTOR_MAX, max(LONG_FACTOR_MIN, values[1]))
    wind_factor = min(LONG_FACTOR_MAX, max(LONG_FACTOR_MIN, values[2]))
    self._start_workers()
    self._write_queue.put((gas_alpha, gas_factor, wind_factor, car_fingerprint))

  def persist_longitudinal_factors(self, gas_factor: float, wind_factor: float, car_fingerprint: str) -> None:
    """Compatibility shim for callers predating gas-alpha persistence."""
    self.persist_longitudinal_state(self.load_gas_alpha(car_fingerprint), gas_factor, wind_factor, car_fingerprint)

  def _start_workers(self) -> None:
    if not self._workers_enabled or self._workers_started:
      return
    with self._worker_lock:
      if self._workers_started:
        return
      self._poll_thread = Thread(target=self._run_polling, name="nrdr-honda-config", daemon=True)
      self._write_thread = Thread(target=self._run_persistence, name="nrdr-honda-persistence", daemon=True)
      self._poll_thread.start()
      self._write_thread.start()
      self._workers_started = True

  def _read_group(self, group: tuple[OpendbcParamKey, ...], values: dict[OpendbcParamKey, Any],
                  allow_none: bool = False) -> bool:
    try:
      updated = {key: self._params.get(str(key)) for key in group}
    except Exception:
      return False
    if not allow_none and any(value is None and values.get(key) is not None for key, value in updated.items()):
      return False
    values.update(updated)
    return True

  def _publish(self, values: Mapping[OpendbcParamKey, Any]) -> None:
    self._snapshot = _RawSnapshot(self._snapshot.generation + 1, MappingProxyType(dict(values)))
    self._tuning_cache = None

  def _run_polling(self) -> None:
    self._drop_realtime()
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

  def _run_persistence(self) -> None:
    self._drop_realtime()
    while not self._stop.is_set():
      pending = self._write_queue.get()
      if pending is None:
        break
      try:
        while True:
          newer = self._write_queue.get_nowait()
          if newer is None:
            self._stop.set()
            break
          pending = newer
      except Empty:
        pass
      self._write_longitudinal_state(*pending)

  def _write_longitudinal_state(self, gas_alpha: float, gas_factor: float, wind_factor: float,
                                car_fingerprint: str) -> None:
    metadata = {
      "car_fingerprint": car_fingerprint,
      "learn_version": LEARN_VERSION,
      "longitudinal_state_sha256": _longitudinal_value_digest(gas_alpha, gas_factor, wind_factor),
      "pending": True,
      "state_digest_version": LONG_STATE_DIGEST_VERSION,
    }
    if not self._commit_longitudinal_metadata(metadata):
      return

    try:
      self._params.put(str(OpendbcParamKey.HONDA_GAS_ALPHA), gas_alpha, block=True)
      self._params.put(str(OpendbcParamKey.HONDA_GAS_FACTOR), gas_factor, block=True)
      self._params.put(str(OpendbcParamKey.HONDA_WIND_FACTOR), wind_factor, block=True)
    except Exception:
      return

    try:
      persisted = tuple(
        float(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        for raw in (
          _read_param(self._params, OpendbcParamKey.HONDA_GAS_ALPHA),
          _read_param(self._params, OpendbcParamKey.HONDA_GAS_FACTOR),
          _read_param(self._params, OpendbcParamKey.HONDA_WIND_FACTOR),
        )
      )
    except (AttributeError, TypeError, ValueError):
      return
    if not all(math.isfinite(value) for value in persisted):
      return
    if _longitudinal_value_digest(*persisted) != metadata["longitudinal_state_sha256"]:
      return

    self._commit_longitudinal_metadata({**metadata, "pending": False})

  def _commit_longitudinal_metadata(self, metadata: Mapping[str, Any]) -> bool:
    temporary_path = self._metadata_path.with_suffix(self._metadata_path.suffix + ".tmp")
    try:
      temporary_path.parent.mkdir(parents=True, exist_ok=True)
      with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, sort_keys=True)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
      temporary_path.replace(self._metadata_path)
      if hasattr(os, "O_DIRECTORY"):
        directory_fd = os.open(temporary_path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
          os.fsync(directory_fd)
        finally:
          os.close(directory_fd)
      return True
    except OSError:
      try:
        temporary_path.unlink(missing_ok=True)
      except OSError:
        pass
      return False

  @staticmethod
  def _drop_realtime() -> None:
    try:
      from openpilot.common.realtime import drop_realtime, set_core_affinity
      drop_realtime()
      set_core_affinity(list(range(os.cpu_count() or 1)))
    except (ImportError, OSError):
      pass


@dataclass(frozen=True, slots=True)
class NrdrHondaConfig:
  """NRDR-owned values which the SunnyPilot host composes into its typed config."""

  bosch_a_radar: bool
  provider: HondaParamsProvider


def build_nrdr_honda_config(params, *, start_worker: bool = True,
                            metadata_path: Path = LEARNER_META_PATH) -> NrdrHondaConfig:
  """Build only NRDR's Bosch-A choice and live Honda tuning provider."""

  provider = HondaParamsProvider(params, start_worker=start_worker, metadata_path=metadata_path)
  # The historical Honda interface used Params.get_bool directly, which is false
  # when the registered key has no stored value (it does not consult registry defaults).
  radar_value = _read_param(params, OpendbcParamKey.HONDA_BOSCH_A_RADAR)

  return NrdrHondaConfig(
    bosch_a_radar=_bool_value(radar_value, False),
    provider=provider,
  )


__all__ = (
  "FAST_PARAM_GROUP",
  "FAST_REFRESH_PERIOD",
  "HondaParamsProvider",
  "LEARNER_META_PATH",
  "NrdrHondaConfig",
  "NrdrHondaParamKey",
  "OpendbcParamKey",
  "REFRESH_PERIOD",
  "SLOW_PARAM_GROUPS",
  "build_nrdr_honda_config",
)
