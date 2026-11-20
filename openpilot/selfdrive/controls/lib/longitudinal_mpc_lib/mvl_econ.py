"""Fixed, gentler Econ acceleration, following distance and jerk.

No Params, LongTune, model/lead shaping, stop thresholds or hill compensation.
The curves are the pre-mode NRDR Eco and cruise ceilings; MPC uses the existing
2.25 second headway and 1.5 jerk/a-change factors.
"""
import numpy as np

ECON_T_FOLLOW = 2.25
ECON_JERK_FACTOR = 1.5
ECON_ACCEL_BP = (0.0, 1.0, 6.0, 8.0, 11.0, 15.0, 20.0, 25.0, 30.0, 55.0)
ECON_ACCEL_VALUES = (2.0, 2.0, 2.0, 1.4, 0.80, 0.68, 0.53, 0.32, 0.20, 0.085)
ECON_CRUISE_BP = (0.0, 10.0, 25.0, 40.0)
ECON_CRUISE_VALUES = (2.0, 1.6, 0.8, 0.6)
ECON_CRUISE_JERK = (1.6, 1.2, 0.8, 0.6)


def econ_cruise_accel(v_cruise, v_ego, a_cruise_prev, dt):
  # Positive acceleration and jerk only: keep MVL's -0.5 cruise braking limit.
  maximum = min(np.interp(v_ego, ECON_ACCEL_BP, ECON_ACCEL_VALUES),
                np.interp(v_ego, ECON_CRUISE_BP, ECON_CRUISE_VALUES))
  target_accel = np.clip(v_cruise - v_ego, -0.5, maximum)
  jerk = np.interp(v_ego, ECON_CRUISE_BP, ECON_CRUISE_JERK)
  return float(np.clip(target_accel, a_cruise_prev - jerk * dt, a_cruise_prev + jerk * dt))
