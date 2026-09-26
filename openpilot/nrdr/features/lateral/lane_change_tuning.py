"""Lane-change request shaping, not a change to measured steering geometry."""

from dataclasses import dataclass
import math


ENTRY_RAMP_SECONDS = 0.15
CANCEL_RETURN_SECONDS = 0.20
MIN_EFFECTIVE_RATIO = 8.0


def bounded_setting(settings, key: str, default: float, minimum: float, maximum: float) -> float:
  try:
    value = float(settings.get(key)) if settings is not None else default
  except (TypeError, ValueError, OverflowError):
    value = default
  return min(max(value, minimum), maximum) if math.isfinite(value) else default


def _smoothstep(value: float) -> float:
  value = min(max(value, 0.0), 1.0)
  return value * value * (3.0 - 2.0 * value)


@dataclass
class LaneChangeEntry:
  """One bounded envelope per starting edge; edits take effect next maneuver.

  LaneChangeState: off=0, pre=1, starting=2, finishing=3. Waiting for a nudge
  must not shape steering. A signal held after completion must not retrigger.
  """

  was_starting: bool = False
  elapsed: float | None = None
  reduction: float = 0.0
  return_seconds: float = 1.0
  direction: int = 0
  applied: float = 0.0
  cancel_elapsed: float | None = None
  cancel_from: float = 0.0

  def update(self, *, active: bool, valid: bool, state: int, direction: int,
             driver_override: bool, settings, dt: float) -> float:
    starting = state == 2
    requested = bounded_setting(settings, "NrdrLaneChangeEntrySrReduction", 0.0, 0.0, 5.0)
    onset = starting and not self.was_starting
    self.was_starting = starting
    if not active or not valid:
      self.elapsed = self.cancel_elapsed = None
      self.applied = 0.0
      return 0.0

    dt = min(max(dt, 0.0), 0.1) if math.isfinite(dt) else 0.0
    if onset and direction in (1, 2) and not driver_override and requested > 0.0:
      self.elapsed = 0.0
      self.cancel_elapsed = None
      self.reduction = requested
      self.return_seconds = bounded_setting(settings, "NrdrLaneChangeEntryReturnTime", 1.0, 0.2, 3.0)
      self.direction = direction

    cancelled = not starting or direction != self.direction or driver_override or requested == 0.0
    if self.elapsed is not None and cancelled:
      self.elapsed = None
      self.cancel_elapsed = 0.0
      self.cancel_from = self.applied

    if self.cancel_elapsed is not None:
      self.cancel_elapsed += dt
      self.applied = self.cancel_from * (1.0 - _smoothstep(self.cancel_elapsed / CANCEL_RETURN_SECONDS))
      if self.cancel_elapsed >= CANCEL_RETURN_SECONDS:
        self.cancel_elapsed = None
        self.applied = 0.0
    elif self.elapsed is not None:
      self.elapsed += dt
      if self.elapsed <= ENTRY_RAMP_SECONDS:
        weight = _smoothstep(self.elapsed / ENTRY_RAMP_SECONDS)
      else:
        weight = 1.0 - _smoothstep((self.elapsed - ENTRY_RAMP_SECONDS) / self.return_seconds)
      self.applied = self.reduction * weight
      if self.elapsed >= ENTRY_RAMP_SECONDS + self.return_seconds:
        self.elapsed = None
        self.applied = 0.0
    return self.applied


def shape_lane_change_curvature(selection, VM, measured_angle: float, speed: float, roll: float,
                                desired_curvature: float, reduction: float) -> float:
  """Reduce the request using the resolved source, including Hybrid/Firmware.

  The current effective SR is the selected physical-to-linear mapping at the
  current wheel angle. Apply its fractional reduction to the requested physical
  angle relative to the zero-curvature angle, preserving road-roll compensation.
  Convert back using the SAME geometry. Feedback and learners remain unchanged.
  The caller must still run normal curvature/actuator safety limits afterward.
  """
  if reduction <= 0.0 or desired_curvature == 0.0:
    return desired_curvature
  if not all(math.isfinite(v) for v in (measured_angle, speed, roll, desired_curvature, reduction)):
    return desired_curvature

  previous_ratio = VM.sR
  try:
    ratio = selection.ratio_at(measured_angle, previous_ratio)
    reference = max(abs(measured_angle), 1e-3)
    linear_reference = selection.linearize_measured_angle(reference)
    if linear_reference <= 0.0:
      return desired_curvature
    effective_ratio = ratio * reference / linear_reference
    if not math.isfinite(effective_ratio) or effective_ratio <= MIN_EFFECTIVE_RATIO:
      return desired_curvature
    reduction = min(reduction, 5.0, effective_ratio - MIN_EFFECTIVE_RATIO)
    scale = 1.0 - reduction / effective_ratio
    zero_angle = selection.desired_angle_no_offset(VM, measured_angle, speed, roll, 0.0)
    target_angle = selection.desired_angle_no_offset(VM, measured_angle, speed, roll, desired_curvature)
    shaped_angle = zero_angle + scale * (target_angle - zero_angle)
    linear_angle = selection.linearize_measured_angle(shaped_angle)
    shaped = -VM.calc_curvature(math.radians(linear_angle), speed, roll)
    if not math.isfinite(shaped):
      return desired_curvature
    # A reduction must never amplify or reverse the requested curvature.
    return min(max(shaped, min(0.0, desired_curvature)), max(0.0, desired_curvature))
  finally:
    VM.sR = previous_ratio
