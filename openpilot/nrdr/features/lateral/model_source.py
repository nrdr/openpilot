"""Model-source metadata and PTM timing shared by both model runners and controlsd."""
from openpilot.common.realtime import DT_CTRL, DT_MDL

PTM_LAT_SMOOTH_SECONDS = 0.1
CMD_DELAY_RAMP_S = 1.0

ACTION_HEAD = "actionHead"
CURVATURE_HEAD = "curvatureHead"
PLAN = "plan"
UNKNOWN = "unknown"


def lateral_source(model_output, mlsim: bool) -> str:
  """The source, exactly as get_action_from_model / get_curvature_from_output choose it."""
  if "action" in model_output:
    return ACTION_HEAD
  # Match get_curvature_from_output, including its zero-output plan fallback.
  if not mlsim and model_output.get("desired_curvature"):
    return CURVATURE_HEAD
  return PLAN


def delay_input(numpy_inputs) -> str:
  if "action_t" in numpy_inputs:
    return "actionT"
  if "lateral_control_params" in numpy_inputs:
    return "lateralControlParams"
  return "none"


class ModelActionRamp:
  """Biscuit-Labs 45e5b91fae: interpolate the 20 Hz model action across each control frame."""

  def __init__(self):
    self.reset(0.0)

  def reset(self, curvature: float) -> None:
    self.output = self.start = self.target = float(curvature)
    self.elapsed = 0.0

  def update(self, curvature: float, new_frame: bool, active: bool) -> float:
    if not active:
      self.reset(curvature)
      return self.output
    if new_frame:
      self.start, self.target, self.elapsed = self.output, float(curvature), 0.0
    else:
      self.elapsed += DT_CTRL
    self.output = self.start + min(self.elapsed / DT_MDL, 1.0) * (self.target - self.start)
    return self.output
