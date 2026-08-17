import json
import math
import os
import threading
from collections import deque
from queue import Empty, Queue

import numpy as np
from openpilot.common.params import Params

from opendbc.car import DT_CTRL


LEARNER_META_PATH = "/data/honda_learner_meta.json"
LEARN_VERSION = 2

_LEARNER_DT = 2 * DT_CTRL
_LAG_TICKS = 25
_ACCEL_RATE_THRESH = 0.3
_HARD_LO = 0.6
_HARD_HI = 1.6
_SOFT_LO = 0.8
_SOFT_HI = 1.25
_DECAY_PER_TICK = 0.01 / 60.0 * _LEARNER_DT
_FACTOR_FILTER_RC = 7.5
_FACTOR_FILTER_ALPHA = _LEARNER_DT / (_FACTOR_FILTER_RC + _LEARNER_DT)
_PITCH_DEADBAND = 0.02
_BRAKE_ADDON_DEADBAND = 1.0


class LongGasLearner:
  def __init__(self, init_gasfactor: float, init_windfactor: float, car_fingerprint: str):
    init_gasfactor = self._safe_clamp(init_gasfactor)
    init_windfactor = self._safe_clamp(init_windfactor)
    self.raw_gasfactor = init_gasfactor
    self.raw_windfactor = init_windfactor
    self.gasfactor = init_gasfactor
    self.windfactor = init_windfactor
    self.car_fingerprint = car_fingerprint
    self.last_gas_error = 0.0
    self._accel_deque = deque(maxlen=_LAG_TICKS + 1)
    self.gasfactor_before_maxgas = init_gasfactor
    self.windfactor_before_maxgas = init_windfactor
    self.windfactor_before_brake = init_windfactor
    self._was_engaged = False

  @staticmethod
  def _safe_clamp(value: float) -> float:
    if not math.isfinite(value):
      return 1.0
    return float(np.clip(value, _HARD_LO, _HARD_HI))

  @staticmethod
  def _decay_toward_nominal(value: float) -> float:
    if value < _SOFT_LO:
      return min(1.0, value + _DECAY_PER_TICK)
    if value > _SOFT_HI:
      return max(1.0, value - _DECAY_PER_TICK)
    return value

  def reset_deque(self, accel_cmd: float):
    self._accel_deque.clear()
    self._accel_deque.extend([accel_cmd] * (_LAG_TICKS + 1))

  def update(self,
             accel_cmd: float,
             a_ego: float,
             gas_pedal_force: float,
             wind_brake_ms2: float,
             long_active: bool,
             long_pid: bool,
             gas_pressed: bool,
             brake_pressed: bool,
             v_ego: float,
             at_standstill: bool,
             pitch: float,
             brake_addon: float,
             at_accel_max: bool):
    engaged = long_active and long_pid
    if (engaged and not self._was_engaged) or gas_pressed:
      self.reset_deque(accel_cmd)
    self._was_engaged = engaged
    self._accel_deque.append(accel_cmd)

    can_learn = engaged and not gas_pressed and not brake_pressed and not at_standstill
    if can_learn and len(self._accel_deque) == _LAG_TICKS + 1:
      lagged_accel = self._accel_deque[0]
      accel_rate = abs(self._accel_deque[-1] - lagged_accel) / (_LAG_TICKS * _LEARNER_DT)
      conditions_valid = (
        accel_rate < _ACCEL_RATE_THRESH
        and abs(pitch) < _PITCH_DEADBAND
        and abs(brake_addon) < _BRAKE_ADDON_DEADBAND
      )
      if conditions_valid:
        gas_error = lagged_accel - a_ego
        self.last_gas_error = float(gas_error)
        if gas_error != 0.0 and gas_pedal_force > 0.0:
          if self.car_fingerprint in ("HONDA_INSIGHT", "HONDA_CIVIC_BOSCH"):
            learn_speed = 150.0
          elif self.car_fingerprint in ("ACURA_RDX_3G", "ACURA_RDX_3G_MMR"):
            learn_speed = 300.0
          else:
            learn_speed = 50.0
          self.raw_gasfactor = np.clip(
            self.raw_gasfactor + gas_error / learn_speed * gas_pedal_force,
            _HARD_LO,
            _HARD_HI,
          )

        if gas_error != 0.0 and v_ego > 0.0:
          wind_learn_speed = 100.0 if self.car_fingerprint in ("ACURA_RDX_3G", "ACURA_RDX_3G_MMR") else 1000.0
          wind_adjust = 1.0 + wind_brake_ms2 / wind_learn_speed
          self.raw_windfactor = np.clip(
            self.raw_windfactor * (wind_adjust if gas_error > 0.0 else 1.0 / wind_adjust),
            _HARD_LO,
            _HARD_HI,
          )

    if gas_pedal_force <= 0.0:
      self.raw_windfactor = max(self.raw_windfactor, self.windfactor_before_brake)
    else:
      self.windfactor_before_brake = self.raw_windfactor

    if at_accel_max:
      self.raw_gasfactor = min(self.raw_gasfactor, self.gasfactor_before_maxgas)
      self.raw_windfactor = min(self.raw_windfactor, self.windfactor_before_maxgas)
      self.raw_gasfactor = max(_HARD_LO, self.raw_gasfactor - _DECAY_PER_TICK)
    else:
      self.gasfactor_before_maxgas = self.raw_gasfactor
      self.windfactor_before_maxgas = self.raw_windfactor

    if not math.isfinite(self.raw_gasfactor):
      self.raw_gasfactor = 1.0
      self.gasfactor_before_maxgas = 1.0
    if not math.isfinite(self.raw_windfactor):
      self.raw_windfactor = 1.0
      self.windfactor_before_maxgas = 1.0
      self.windfactor_before_brake = 1.0

    self.raw_gasfactor = float(np.clip(self._decay_toward_nominal(self.raw_gasfactor), _HARD_LO, _HARD_HI))
    self.raw_windfactor = float(np.clip(self._decay_toward_nominal(self.raw_windfactor), _HARD_LO, _HARD_HI))
    self.gasfactor = _FACTOR_FILTER_ALPHA * self.raw_gasfactor + (1.0 - _FACTOR_FILTER_ALPHA) * self.gasfactor
    self.windfactor = _FACTOR_FILTER_ALPHA * self.raw_windfactor + (1.0 - _FACTOR_FILTER_ALPHA) * self.windfactor

    if not math.isfinite(self.gasfactor):
      self.gasfactor = 1.0
    if not math.isfinite(self.windfactor):
      self.windfactor = 1.0
    return self.gasfactor, self.windfactor


def load_factors(car_fingerprint: str) -> tuple[float, float]:
  try:
    params = Params()
    raw_gas = params.get("HondaGasFactorParams")
    raw_wind = params.get("HondaWindFactorParams")
    if raw_gas is None or raw_wind is None:
      return 1.0, 1.0

    with open(LEARNER_META_PATH, encoding="utf-8") as file:
      metadata = json.load(file)
    if metadata.get("car_fingerprint") != car_fingerprint or metadata.get("learn_version") != LEARN_VERSION:
      return 1.0, 1.0

    gas = float(raw_gas.decode("utf-8") if isinstance(raw_gas, bytes) else raw_gas)
    wind = float(raw_wind.decode("utf-8") if isinstance(raw_wind, bytes) else raw_wind)
    if not math.isfinite(gas) or not math.isfinite(wind):
      return 1.0, 1.0
    return float(np.clip(gas, _HARD_LO, _HARD_HI)), float(np.clip(wind, _HARD_LO, _HARD_HI))
  except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
    return 1.0, 1.0


def write_metadata(car_fingerprint: str):
  try:
    temporary_path = LEARNER_META_PATH + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
      json.dump({"car_fingerprint": car_fingerprint, "learn_version": LEARN_VERSION}, file, sort_keys=True)
      file.write("\n")
      file.flush()
      os.fsync(file.fileno())
    os.replace(temporary_path, LEARNER_META_PATH)
  except OSError:
    pass


class HondaParamWriter:
  def __init__(self):
    self._params = Params()
    self._queue = Queue()
    threading.Thread(target=self._run, name="honda-param-writer", daemon=True).start()

  def put_many(self, values, car_fingerprint: str):
    self._queue.put(({key: float(value) for key, value in values.items()}, car_fingerprint))

  def _run(self):
    try:
      from openpilot.common.realtime import drop_realtime, set_core_affinity
      drop_realtime()
      set_core_affinity(list(range(os.cpu_count() or 1)))
    except (ImportError, OSError):
      pass

    while True:
      pending, car_fingerprint = self._queue.get()
      try:
        while True:
          newer, car_fingerprint = self._queue.get_nowait()
          pending.update(newer)
      except Empty:
        pass

      for key, value in pending.items():
        self._params.put(key, value, block=True)
      write_metadata(car_fingerprint)
