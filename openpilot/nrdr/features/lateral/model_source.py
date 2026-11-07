"""Where the model's steering comes from, and the command delay that follows from it.

modeld attaches the source to modelV2.action next to lateralActionTime (set_lateral_action_timing), decided where
get_action_from_model decides it:
  actionHead     the model has an action output (e.g. Cinque Terre V3). It follows the told delay only in part: Cinque's
                 aim moves ~0.53 s per 1 s of action_t.
  curvatureHead  a non-tinygrad model's desired_curvature output.
  plan           everything else (e.g. Pop v2, The Cool Peoples Model v3): the curvature that reaches the plan's heading at
                 lateralActionTime, read no earlier than MIN_STABLE_DELAY (0.3 s).

On a plan model the floor is the whole timing story. When the told delay is the car's measured lag (a profile with a
prediction schedule), the plan should be read at lateralActionTime; the floor reads it at 0.3 s instead, so the curvature
it hands over is meant for MIN_STABLE_DELAY - lateralActionTime later than the car will reach it. Holding it back that
long (plan_floor_command_delay) lands it on time, and above the floor it needs no delay at all.
"""
from openpilot.selfdrive.controls.lib.drive_helpers import MIN_STABLE_DELAY

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


def plan_floor_command_delay(lateral_action_time: float) -> float | None:
  """The command delay that cancels the MIN_STABLE_DELAY floor; None without a published action time."""
  if not lateral_action_time > 0.0:
    return None
  return max(MIN_STABLE_DELAY - float(lateral_action_time), 0.0)


class CommandDelaySlew:
  """Moves the applied command delay at most rate seconds per second, so a model change (or the speed fade) never steps
  the executed curvature."""

  def __init__(self, dt: float, rate: float = 0.3):
    self.step = dt * rate
    self.value: float | None = None

  def update(self, target: float) -> float:
    if self.value is None:
      self.value = float(target)
    else:
      self.value += max(min(float(target) - self.value, self.step), -self.step)
    return self.value
