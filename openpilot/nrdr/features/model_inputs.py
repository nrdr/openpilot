"""Development model inputs, latched at process start, not polled in the inference loop."""
import numpy as np


def clarity_manual_lookahead(params, CP) -> float | None:
  """Final lateral action horizon in seconds, or None to retain the runner's timing."""
  if CP.brand != "honda" or CP.carFingerprint != "HONDA_CLARITY" or CP.steerControlType != "angle":
    return None
  if params.get_bool("LagdToggle"):
    return None
  ms = params.get("NrdrClarityAngleLookaheadMs", return_default=True)
  return ms / 1000 if type(ms) is int and ms in range(5, 401, 5) else None


def lateral_model_times(manual: float | None, timed_action_head: bool, lat_delay: float,
                        frame_delay: float, action_delay: float) -> tuple[float, float]:
  """(lateral_control_params delay, action_t horizon) for the model running this frame."""
  if manual is not None and timed_action_head:
    return manual, manual
  return lat_delay, lat_delay + frame_delay + action_delay


def model_fidx(params) -> float:
  value = params.get("NrdrModelFidx", return_default=True)
  return float(value) if value in (1, 2, 3, 4, 5, 6) else 3.0


def action_time_input(lateral: float, longitudinal: float, cap: bool) -> np.ndarray:
  pair = np.array([lateral, longitudinal], dtype=np.float32)
  if cap:
    np.minimum(pair, 0.4, out=pair)
  return pair
