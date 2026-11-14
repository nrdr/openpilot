"""Civic Bosch live gas learner, ported from openpilot-radar ns-bosch-radar-testing (LongGasLearner).

What it adds over the shared star7 learner in bosch_longitudinal.py:
  - learns against the command from 0.5 s ago, not the current one (the gas pedal lags);
  - learns only on quasi-steady commands (|d accel| < 0.3 m/s^3) on flat road (|pitch - 0.013| < 0.02 rad);
  - hard range 0.6-1.6, decays back toward 1.0 at 0.01/min while outside 0.8-1.25;
  - the applied factor follows the learned one through a 7.5 s filter;
  - the gas factor scales the flat-road request only, anchored at the gas-on threshold, and the hill term is added
    on top with a 1.1 gain about the mount's 0.013 rad pitch bias.

Tuned on ns against the Civic gas table [0, 2] -> [0, 1600]. star7 keeps its own Civic table [-0.2, 2] -> [0, 750]
(Peter's call, 2026-10-22). That pairing has never been driven. Evidence here: static and unit tests only.
Not ported: the starpilotCarState.gasLearner* log fields (they need cereal changes).
"""
import math
from collections import deque

import numpy as np

from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, DT_CTRL

# Bump when the learner's meaning changes, so saved factors from older math are dropped once.
LEARN_VERSION = 1

LEARNER_DT = 2 * DT_CTRL  # update() runs on the 50 Hz gas frames
LAG_TICKS = 25  # 0.5 s
ACCEL_RATE_THRESH = 0.3  # m/s^3

HARD_LO = 0.6
HARD_HI = 1.6
SOFT_LO = 0.8
SOFT_HI = 1.25
DECAY_PER_TICK = 0.01 / 60.0 * LEARNER_DT

FACTOR_FILTER_RC = 7.5
FACTOR_FILTER_ALPHA = LEARNER_DT / (FACTOR_FILTER_RC + LEARNER_DT)

PITCH_DEADBAND = 0.02  # rad
CIVIC_PITCH_BIAS = 0.013  # rad; this device mount, 18/18 ns routes
CIVIC_HILL_GAS_GAIN = 1.1  # ns: offline fit said 1.2, shipped 1.1 after the hill sim doubled crest overshoot at 1.2
CIVIC_GAS_LEARN_SPEED = 150.0  # the Civic gas pedal reacts slowly
WIND_LEARN_SPEED = 1000.0


def safe_clamp(v: float) -> float:
  if not math.isfinite(v):
    return 1.0
  return float(np.clip(v, HARD_LO, HARD_HI))


def decay_toward_nominal(v: float) -> float:
  if v < SOFT_LO or v > SOFT_HI:
    v = min(1.0, v + DECAY_PER_TICK) if v < 1.0 else max(1.0, v - DECAY_PER_TICK)
  return v


def gas_lookup_accel(gas_pedal_force: float, hill_brake: float, gasfactor: float, min_gas: float) -> float:
  """Input to the gas table. The factor scales the flat-road offset from the gas-on threshold; the hill term is
  added unscaled, with the Civic hill gain about the pitch bias so flat-road gas is unchanged."""
  hill_level = math.sin(CIVIC_PITCH_BIAS) * ACCELERATION_DUE_TO_GRAVITY
  return ((gas_pedal_force - hill_brake - min_gas) * gasfactor + min_gas + hill_brake +
          (CIVIC_HILL_GAS_GAIN - 1.0) * (hill_brake - hill_level))


class CivicGasLearner:
  def __init__(self, gasfactor: float = 1.0, windfactor: float = 1.0):
    self.load(gasfactor, windfactor)
    self._accel_deque: deque = deque(maxlen=LAG_TICKS + 1)
    self._was_engaged = False
    self.learning = False
    self.last_gas_error = 0.0

  def load(self, gasfactor: float, windfactor: float):
    """Saved values start both the learned and the applied factor, so there is no startup transient."""
    self.raw_gasfactor = self.gasfactor = safe_clamp(gasfactor)
    self.raw_windfactor = self.windfactor = safe_clamp(windfactor)
    self.gasfactor_before_maxgas = self.raw_gasfactor
    self.windfactor_before_maxgas = self.raw_windfactor
    self.windfactor_before_brake = self.raw_windfactor

  def _reset_deque(self, accel_cmd: float):
    self._accel_deque.clear()
    self._accel_deque.extend([accel_cmd] * (LAG_TICKS + 1))

  def update(self, accel_cmd: float, a_ego: float, gas_pedal_force: float, wind_brake_ms2: float, engaged: bool,
             gas_pressed: bool, brake_pressed: bool, v_ego: float, pitch: float, at_accel_max: bool):
    self.learning = False
    if (engaged and not self._was_engaged) or gas_pressed:
      self._reset_deque(accel_cmd)
    self._was_engaged = engaged
    self._accel_deque.append(accel_cmd)

    if engaged and not gas_pressed and not brake_pressed and v_ego > 0.0 and len(self._accel_deque) == LAG_TICKS + 1:
      lagged = self._accel_deque[0]
      quasi_steady = abs(self._accel_deque[-1] - lagged) / (LAG_TICKS * LEARNER_DT) < ACCEL_RATE_THRESH
      if quasi_steady and abs(pitch - CIVIC_PITCH_BIAS) < PITCH_DEADBAND:
        self.learning = True
        gas_error = lagged - a_ego
        self.last_gas_error = float(gas_error)
        if gas_error != 0.0 and gas_pedal_force > 0.0:
          self.raw_gasfactor = float(np.clip(self.raw_gasfactor + gas_error / CIVIC_GAS_LEARN_SPEED * gas_pedal_force,
                                             HARD_LO, HARD_HI))
        if gas_error != 0.0:
          wind_adjust = 1.0 + wind_brake_ms2 / WIND_LEARN_SPEED
          self.raw_windfactor = float(np.clip(self.raw_windfactor * (wind_adjust if gas_error > 0.0 else 1.0 / wind_adjust),
                                              HARD_LO, HARD_HI))

    # Anti-windup: braking never lowers the wind factor; at the accel limit neither factor may rise.
    if gas_pedal_force <= 0.0:
      self.raw_windfactor = max(self.raw_windfactor, self.windfactor_before_brake)
    else:
      self.windfactor_before_brake = self.raw_windfactor
    if at_accel_max:
      self.raw_gasfactor = max(HARD_LO, min(self.raw_gasfactor, self.gasfactor_before_maxgas) - DECAY_PER_TICK)
      self.raw_windfactor = min(self.raw_windfactor, self.windfactor_before_maxgas)
    else:
      self.gasfactor_before_maxgas = self.raw_gasfactor
      self.windfactor_before_maxgas = self.raw_windfactor

    if not math.isfinite(self.raw_gasfactor):
      self.raw_gasfactor = self.gasfactor_before_maxgas = 1.0
    if not math.isfinite(self.raw_windfactor):
      self.raw_windfactor = self.windfactor_before_maxgas = self.windfactor_before_brake = 1.0

    self.raw_gasfactor = safe_clamp(decay_toward_nominal(self.raw_gasfactor))
    self.raw_windfactor = safe_clamp(decay_toward_nominal(self.raw_windfactor))

    self.gasfactor = FACTOR_FILTER_ALPHA * self.raw_gasfactor + (1.0 - FACTOR_FILTER_ALPHA) * self.gasfactor
    self.windfactor = FACTOR_FILTER_ALPHA * self.raw_windfactor + (1.0 - FACTOR_FILTER_ALPHA) * self.windfactor
    if not math.isfinite(self.gasfactor):
      self.gasfactor = 1.0
    if not math.isfinite(self.windfactor):
      self.windfactor = 1.0
    return self.gasfactor, self.windfactor
