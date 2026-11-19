"""Development model inputs, latched at process start, not polled in the inference loop."""
import numpy as np


def model_fidx(params) -> float:
  value = params.get("NrdrModelFidx", return_default=True)
  return float(value) if value in (1, 2, 3, 4, 5, 6) else 3.0


def action_time_input(lateral: float, longitudinal: float, cap: bool) -> np.ndarray:
  pair = np.array([lateral, longitudinal], dtype=np.float32)
  if cap:
    np.minimum(pair, 0.4, out=pair)
  return pair
