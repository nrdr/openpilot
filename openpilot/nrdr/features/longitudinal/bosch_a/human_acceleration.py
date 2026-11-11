"""HumanAcceleration: throttle shaping by set speed, ported from openpilot-radar (STATUS 68/118), which follows
FrogPilot-Testing 728f65472 frogpilot_acceleration.py.

Only the throttle side: `cap()` never goes below 0, so braking targets pass through. Enabled with
gate.human_following_enabled(CP) (radar on or vision-only; permanently on, no toggle).
FrogPilot's launch half (the starting state outputs a_target instead of startAccel) is not ported: Honda has no
CP.startingState, so it never affected the Civic, and it would change other cars. Unit-test and replay evidence only; not road-validated on this tree.
"""
import numpy as np

from openpilot.cereal import log

CITY_SPEED_LIMIT = 25.  # m/s, FrogPilot CITY_SPEED_LIMIT


def applies(personality) -> bool:
  """Relaxed, Standard and Econ (Biscuit-Labs#78; Econ by owner decision 2026-11-10): Aggressive keeps the planner's
  own max accel. Takes the raw int or the capnp enum (the planner passes the longitudinal_personality() value);
  anything else is not capped."""
  value = getattr(personality, "raw", personality)
  return not isinstance(value, bool) and value in (log.LongitudinalPersonality.standard, log.LongitudinalPersonality.relaxed,
                                                     log.LongitudinalPersonality.econ)


def get_max_accel_low_speeds(max_accel: float, v_cruise: float) -> float:
  """Scale max accel by the set speed: 1/4 at 0, 1/2 at 12.5 m/s, full from 25 m/s."""
  return float(np.interp(v_cruise, [0., CITY_SPEED_LIMIT / 2, CITY_SPEED_LIMIT], [max_accel / 4, max_accel / 2, max_accel]))


def get_max_accel_ramp_off(max_accel: float, v_cruise: float, v_ego: float) -> float:
  """Ease off as v_ego nears the set speed: 0 at it, 0.5 at 1 m/s below, full at 5 m/s below."""
  return float(np.interp(v_cruise - v_ego, [0., 1., 5.], [0., 0.5, max_accel]))


def cap(max_accel: float, v_cruise: float, v_ego: float) -> float:
  """HumanAcceleration max accel (>= 0) from the planner's own max accel."""
  max_accel = get_max_accel_low_speeds(max(float(max_accel), 0.0), float(v_cruise))
  return max(0.0, min(get_max_accel_ramp_off(max_accel, float(v_cruise), float(v_ego)), max_accel))
