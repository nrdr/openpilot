from numpy import searchsorted

from roenpilot.common.numpy_fast import interp
from roenpilot.common.roenpilot_variables import A_CRUISE_MAX_BP_CUSTOM, A_CRUISE_MAX_VALS_ECO, A_CRUISE_MAX_VALS_SPORT, ISO_MAX_BP, ISO_MAX_VALS


def akima_interp(x, xp, fp):
     """Akima-inspired interpolation with reduced overshoot characteristics."""
     if x <= xp[0]:
         return fp[0]
     elif x >= xp[-1]:
         return fp[-1]

     i = searchsorted(xp, x) - 1
     i = max(0, min(i, len(xp)-2))  # clamp the index

     t = (x - xp[i]) / float(xp[i+1] - xp[i])

     # Quintic polynomial to reduce overshoot
     t2 = t*t
     t4 = t2*t2
     t3 = t2*t
     return (fp[i]*(1 - 10*t3 + 15*t4 - 6*t3*t2) + fp[i+1]*(10*t3 - 15*t4 + 6*t3*t2))


def get_max_accel_eco(v_ego):
  return float(akima_interp(v_ego, A_CRUISE_MAX_BP_CUSTOM, A_CRUISE_MAX_VALS_ECO))

def get_max_accel_sport(v_ego):
  return interp(v_ego, A_CRUISE_MAX_BP_CUSTOM, A_CRUISE_MAX_VALS_SPORT)

def get_max_allowed_accel(v_ego):
  # ISO 15622:2018
  return interp(v_ego, ISO_MAX_BP, ISO_MAX_VALS)
