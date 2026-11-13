"""Lane-change request shaping, not a change to measured steering geometry."""

from dataclasses import dataclass
from functools import cache
import math


ENTRY_RAMP_SECONDS = 0.15
CANCEL_RETURN_SECONDS = 0.20
MIN_EFFECTIVE_RATIO = 8.0
OPTIMIZED_VALUES = {
  "NrdrLaneChangeMinTime": 0.5,
  "NrdrLaneChangeEntrySrReduction": 5.0,
  "NrdrLaneChangeEntryReturnTime": 1.0,
  "NrdrLaneChangeTorqueFactor": 2.0,
  "NrdrLaneChangeFrictionPercent": 0.0,
}
BASELINE_VALUES = {**OPTIMIZED_VALUES, "NrdrLaneChangeMinTime": 1.0,
                   "NrdrLaneChangeEntrySrReduction": 0.0, "NrdrLaneChangeTorqueFactor": 1.0,
                   "NrdrLaneChangeFrictionPercent": 100.0}

# Catalog families, not generation numbers: World and Deep RL both use generation 12.
OPTIMIZED_MODEL_FAMILIES = frozenset(("Legacy Models", "2025 Pre World Models", "2025 World Models", "2026 World Models"))
# Older World/Pre-World models filed under Release, Master, or Custom Merge instead.
OPTIMIZED_MODEL_REFS = frozenset((
  "d807b5c476658dba7760d30949baa619074c4a4e",  # Filet o Fish
  "d134fdd7d51ba84848866c0265e37508c38f9366",  # SP Vikander
  "d3a0378ae601f61307a53d1173c251ee36c56317",  # Space Lab 2
  "659898d553eb68c981036811e1b92f6557d4e494",  # Space Lab 3
  "a6cf39c07a67dbc346af03010093fe4788c402d0",  # Down to Ride v6
  "f1b8f510b2c554191ca15cebe35f2c5b304cf23c",  # Steam Powered
  "b74f5189a74446015c0cf78a4a9f0134a347ae3b",  # Firehose
  "3193eac5e385aa010694a8ac192ff38ffe000193",  # Nevada
  "83b81b83cdf76a577946a1567f4644e1a018443c",  # North Nevada v2
  "5eb912c025a2207c7d428deee74ded49e5905527",  # Cool Peoples v3
  "ba783b9f913de089816598aa367a30499727a0ce",  # Dark Souls
  "5ff0e48f90d662d8c9d5061adc63e90c198c9b81",  # Dark Souls v2
  "7e3fd7a63c5a09c3fabe108b1b62bba3cf684878",  # WMI v12
  "5b6436a90cf6902b8aaa71c2b6f3d7164d8ae391",  # CD210 (default small model)
  "cb327933002bc1a00bf60a3c20af2eb7a5f653e5",  # OP Model, April 01
  "052692b25d63c5ddda276b5c2271383b6aff129f",  # OP Model 7
))


def model_supports_optimized_lane_changes(bundle: dict | None, *, chestnut: bool = False) -> bool:
  if chestnut:
    return False
  if not bundle:
    from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL_REF
    return DEFAULT_MODEL_REF in OPTIMIZED_MODEL_REFS
  if bundle.get("is_big", False):
    return False
  overrides = bundle.get("overrides", [])
  if not isinstance(overrides, dict):
    overrides = {item["key"]: item["value"] for item in overrides}
  return overrides.get("folder") in OPTIMIZED_MODEL_FAMILIES or bundle.get("ref") in OPTIMIZED_MODEL_REFS


@cache
def active_model_supports_optimized_lane_changes() -> bool:
  # Model selection is fixed for an onroad process lifetime. Warm this during
  # live-parameter initialization; never poll Params/USB in the control loop.
  from openpilot.common.params import Params
  from openpilot.selfdrive.modeld.helpers import chestnut_present
  return model_supports_optimized_lane_changes(Params().get("ModelManager_ActiveBundle"), chestnut=chestnut_present())


def optimized_lane_changes_enabled(settings) -> bool:
  value = settings.get("NrdrOptimizedLaneChanges") if settings is not None else None
  requested = value is None or str(value).strip().lower() in ("1", "true", "b'1'", "b'true'")
  return requested and active_model_supports_optimized_lane_changes()


def optimized_lane_change_active(settings, state) -> bool:
  # Waiting for a nudge is not yet a lane change. Keep normal steering then.
  return optimized_lane_changes_enabled(settings) and int(getattr(state, "raw", state)) in (2, 3)


def bounded_setting(settings, key: str, default: float, minimum: float, maximum: float) -> float:
  if key in OPTIMIZED_VALUES:
    return (OPTIMIZED_VALUES if optimized_lane_changes_enabled(settings) else BASELINE_VALUES)[key]
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
    if (rack_map := getattr(selection, "rack_map", None)) is not None:
      # The rack map carries its own slip factor; convert back through it, as the angles above were.
      shaped = -rack_map.curvature_from_angle(shaped_angle, speed, roll)
    else:
      linear_angle = selection.linearize_measured_angle(shaped_angle)
      shaped = -VM.calc_curvature(math.radians(linear_angle), speed, roll)
    if not math.isfinite(shaped):
      return desired_curvature
    # A reduction must never amplify or reverse the requested curvature.
    return min(max(shaped, min(0.0, desired_curvature)), max(0.0, desired_curvature))
  finally:
    VM.sR = previous_ratio
