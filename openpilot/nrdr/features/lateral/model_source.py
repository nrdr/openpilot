"""Model-source metadata and PTM timing shared by both model runners and controlsd."""
from openpilot.common.realtime import DT_CTRL, DT_MDL
from openpilot.selfdrive.controls.lib.drive_helpers import MIN_STABLE_DELAY

PTM_LAT_SMOOTH_SECONDS = 0.1
CMD_DELAY_RAMP_S = 1.0

ACTION_HEAD = "actionHead"
CURVATURE_HEAD = "curvatureHead"
PLAN = "plan"
UNKNOWN = "unknown"


def ptm_timing_restored(action) -> bool:
  return bool(getattr(action, "ptmTimingRestored", True))


class PtmTimingMode:
  """Apply a saved comparison mode only while stopped with lateral control off.

  The model publisher owns this decision. Consumers use the mode attached to
  that exact model action, never an independently polled parameter.
  """

  def __init__(self, settings):
    self.restored = self._requested(settings)

  @staticmethod
  def _requested(settings) -> bool:
    # Missing/invalid values retain the existing, restored timing.
    return settings.get("NrdrPtmTimingRestoration") not in (False, 0, "0", b"0")

  def update(self, settings, car_state, car_control, valid: bool) -> bool:
    if valid and car_state.standstill and abs(car_state.vEgo) < 0.1 and not car_control.latActive:
      self.restored = self._requested(settings)
    return self.restored


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


def model_uses_plan(output_names, mlsim: bool) -> bool:
  """Select the prediction horizon from declared outputs before inference."""
  return "action" not in output_names and (mlsim or "desired_curvature" not in output_names)


def plan_floor_command_delay(lateral_action_time: float) -> float | None:
  """Compensate for reading the trajectory no earlier than MIN_STABLE_DELAY."""
  if not lateral_action_time > 0.0:
    return None
  return max(MIN_STABLE_DELAY - float(lateral_action_time), 0.0)


class CommandDelaySlew:
  """Keep the pre-November-13 delay transition rate of 0.3 seconds per second."""

  def __init__(self, dt: float, rate: float = 0.3):
    self.step = dt * rate
    self.value: float | None = None

  def update(self, target: float) -> float:
    if self.value is None:
      self.value = float(target)
    else:
      self.value += max(min(float(target) - self.value, self.step), -self.step)
    return self.value


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
