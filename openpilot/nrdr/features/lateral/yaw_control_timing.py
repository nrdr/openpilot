"""Timing for the Clarity Yaw Control."""
import numpy as np

# Lateral delay the model is told in place of lagd/SteerDelay, scheduled on speed.
DELAY_SCHEDULE_BP = (3.5, 7.0, 12.0, 20.0, 30.0)  # m/s
DELAY_SCHEDULE_V = (0.12, 0.12, 0.15, 0.20, 0.30)  # s


def clarity_lateral_delay(speed: float) -> float:
  return float(np.interp(speed, DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V))
