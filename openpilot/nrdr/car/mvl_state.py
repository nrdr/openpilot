"""Host-owned, paced persistence for the MVL Honda multi-band learner.

Keep filesystem operations out of opendbc and off the control thread. The
one-key/second schedule follows MVL 657358074; queued snapshots coalesce.
"""
import math
from threading import Event, Lock, Thread


MVL_STATE_KEYS = {
  "brake_pid": "HondaBrakePIDParams",
  "feedforward": "HondaFeedForwardParams",
  "car_gas_scale": "HondaCarGasScaleParams",
  "creep_factor": "HondaCreepFactorParams",
  "wind_factor": "HondaWindFactorParams",
  "sat_accel": "HondaSatAccelParams",
  "launch_dv": "HondaLaunchDvParams",
  "launch_gas": "HondaLaunchGasParams",
  "launch_dv_break": "HondaLaunchDvBreakParams",
  "gas_factor": "HondaGasFactorParams",
  "gas_factor_low": "HondaGasFactorLowParams",
  "gas_factor_00": "HondaGasFactor00Params",
  "gas_factor_10": "HondaGasFactor10Params",
  "gas_factor_20": "HondaGasFactor20Params",
  "gas_factor_30": "HondaGasFactor30Params",
  "gas_alpha": "HondaGasAlphaParams",
  "gas_alpha_low": "HondaGasAlphaLowParams",
  "gas_alpha_00": "HondaGasAlpha00Params",
  "gas_alpha_10": "HondaGasAlpha10Params",
  "gas_alpha_20": "HondaGasAlpha20Params",
  "gas_alpha_30": "HondaGasAlpha30Params",
  "speed_factor": "HondaSpeedFactorParams",
  "speed_factor_low": "HondaSpeedFactorLowParams",
  "speed_factor_05": "HondaSpeedFactor05Params",
  "speed_factor_15": "HondaSpeedFactor15Params",
  "speed_factor_25": "HondaSpeedFactor25Params",
  "speed_factor_35": "HondaSpeedFactor35Params",
  "speed_alpha": "HondaSpeedAlphaParams",
  "speed_alpha_low": "HondaSpeedAlphaLowParams",
  "speed_alpha_05": "HondaSpeedAlpha05Params",
  "speed_alpha_15": "HondaSpeedAlpha15Params",
  "speed_alpha_25": "HondaSpeedAlpha25Params",
  "speed_alpha_35": "HondaSpeedAlpha35Params",
  "lat_accel_factor_05": "HondaLatAccelFactor05Params",
  "lat_accel_factor_10": "HondaLatAccelFactor10Params",
  "lat_accel_factor_15": "HondaLatAccelFactor15Params",
  "lat_accel_factor_20": "HondaLatAccelFactor20Params",
  "lat_accel_factor_25": "HondaLatAccelFactor25Params",
  "lat_accel_factor_30": "HondaLatAccelFactor30Params",
  "lat_accel_factor_35": "HondaLatAccelFactor35Params",
  "lat_accel_factor_40": "HondaLatAccelFactor40Params",
  "lat_accel_factor_45": "HondaLatAccelFactor45Params",
  "lat_accel_factor_50": "HondaLatAccelFactor50Params",
  "lat_accel_factor_55": "HondaLatAccelFactor55Params",
  "lat_accel_factor_60": "HondaLatAccelFactor60Params",
}


class MvlStateStore:
  def __init__(self, params, *, start_worker=True):
    self._params = params
    self._start_worker = start_worker
    self._pending = {}
    self._written = {}
    self._lock = Lock()
    self._wake = Event()
    self._stop = Event()
    self._thread = None

  def load(self, key: str, default: float) -> float:
    if key not in MVL_STATE_KEYS:
      raise ValueError(f"Unsupported MVL learner key: {key}")
    try:
      value = float(self._params.get(MVL_STATE_KEYS[key]))
      return value if math.isfinite(value) else float(default)
    except (KeyError, TypeError, ValueError, OSError):
      return float(default)

  def put_many(self, values) -> None:
    pending = {}
    for key, raw in values.items():
      if key not in MVL_STATE_KEYS:
        raise ValueError(f"Unsupported MVL learner key: {key}")
      try:
        value = float(raw)
      except (TypeError, ValueError, OverflowError):
        continue
      if math.isfinite(value):
        pending[key] = value
    with self._lock:
      self._pending.update(pending)
      if pending and self._start_worker and self._thread is None:
        self._thread = Thread(target=self._run, name="nrdr-mvl-persistence", daemon=True)
        self._thread.start()
    self._wake.set()

  def flush_one(self) -> bool:
    """Write at most one changed key. Called by the paced worker, or tests."""
    while True:
      with self._lock:
        if not self._pending:
          return False
        key = next(iter(self._pending))
        value = self._pending.pop(key)
      if self._written.get(key) == value:
        continue
      try:
        self._params.put(MVL_STATE_KEYS[key], value, block=True)
      except Exception:
        # Retry later, without replacing a newer queued value.
        with self._lock:
          self._pending.setdefault(key, value)
        return True
      self._written[key] = value
      return True

  def _run(self) -> None:
    from openpilot.nrdr.car.opendbc import HondaParamsProvider
    HondaParamsProvider._drop_realtime()
    while not self._stop.is_set():
      if self.flush_one():
        self._stop.wait(1.0)
      else:
        self._wake.wait(1.0)
        self._wake.clear()

  def close(self) -> None:
    self._stop.set()
    self._wake.set()
    if self._thread is not None:
      self._thread.join(timeout=2.0)
