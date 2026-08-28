"""Explicit, auditable steer-ratio modes shared by controlsd and lateral PID."""

from dataclasses import dataclass, field
from enum import IntEnum
import math
from typing import Any

import numpy as np

from openpilot.nrdr.features.lateral.honda_vgr import HondaVgrProfile, get_honda_vgr_profile


MANUAL_CENTER_DEFAULT = 15.38
MANUAL_FINAL_DEFAULT = 10.93
GENERIC_MANUAL_OUTER_ANGLE_DEG = 250.0
STEER_RATIO_MIN = 8.0
STEER_RATIO_MAX = 25.0


@dataclass(frozen=True)
class SteerRatioMetadata:
  family: str
  fingerprints: tuple[str, ...]
  outer_angle: float


# Only physical rack metadata remains active. Retired per-family Param names
# and defaults live exclusively in the migration/offline compatibility layer.
STEER_RATIO_METADATA = (
  SteerRatioMetadata("Clarity", ("HONDA_CLARITY",), 250.0),
  SteerRatioMetadata("10th-gen Civic", ("HONDA_CIVIC", "HONDA_CIVIC_BOSCH", "HONDA_CIVIC_BOSCH_DIESEL"),
                     2.22 * 250.0 / 2.41),
  SteerRatioMetadata("10th-gen Accord", ("HONDA_ACCORD",), 2.30 * 250.0 / 2.41),
  SteerRatioMetadata("5th-gen CR-V", ("HONDA_CRV_5G", "HONDA_CRV_HYBRID"), 2.30 * 250.0 / 2.41),
  SteerRatioMetadata("3rd-gen Insight", ("HONDA_INSIGHT",), 2.54 * 250.0 / 2.41),
)
STEER_RATIO_METADATA_BY_FP = {
  fingerprint: metadata
  for metadata in STEER_RATIO_METADATA
  for fingerprint in metadata.fingerprints
}


def get_steer_ratio_metadata(fingerprint: str) -> SteerRatioMetadata | None:
  return STEER_RATIO_METADATA_BY_FP.get(str(fingerprint))


class SteerRatioMode(IntEnum):
  MANUAL = 0
  COMMA = 1
  NRDR_RAW = 2
  FIRMWARE = 3


@dataclass(frozen=True)
class RawSteerRatioProfile:
  name: str
  fingerprint: str
  angles_deg: tuple[float, ...]
  ratios: tuple[float, ...]
  provenance: str

  def __post_init__(self) -> None:
    if len(self.angles_deg) != len(self.ratios) or len(self.angles_deg) < 2:
      raise ValueError("raw steer-ratio curves require matching angle and ratio arrays")
    if self.angles_deg[0] != 0.0 or any(b <= a for a, b in zip(self.angles_deg, self.angles_deg[1:], strict=False)):
      raise ValueError("raw steer-ratio angles must start at zero and increase")
    if any(not math.isfinite(value) or value <= 0.0 for value in self.ratios):
      raise ValueError("raw steer-ratio samples must be finite and positive")

  def ratio_at(self, measured_angle_deg: float) -> float:
    # np.interp deliberately endpoint-clamps. The historical data has real
    # non-monotonic bins, so do not smooth or manufacture a firmware tail.
    return float(np.interp(abs(measured_angle_deg), self.angles_deg, self.ratios))


_CLARITY_RAW_ANGLES = (
  0.0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5,
  57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5,
)
_CLARITY_RAW_RATIOS = (
  19.679678, 19.679678, 20.665984, 19.948804, 19.330348, 19.362985,
  19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309,
  17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118,
  17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368,
)

CLARITY_RAW_STEER_RATIO = RawSteerRatioProfile(
  name="Clarity measured-angle raw bins",
  fingerprint="HONDA_CLARITY",
  angles_deg=_CLARITY_RAW_ANGLES,
  ratios=_CLARITY_RAW_RATIOS,
  provenance="54f74ae3e5973aa681904780f8cac140870a2b5f:sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv" +
             "@8a96cab2b8d5fcfa055709e997bea38e3f5724b0",
)

RAW_STEER_RATIO_PROFILES = {CLARITY_RAW_STEER_RATIO.fingerprint: CLARITY_RAW_STEER_RATIO}


@dataclass(frozen=True)
class SteerRatioSelection:
  requested_mode: SteerRatioMode
  effective_mode: SteerRatioMode | None
  fingerprint: str
  cp_ratio: float
  manual_center: float
  manual_final: float
  manual_outer_angle_deg: float
  raw_profile: RawSteerRatioProfile | None = None
  firmware_profile: HondaVgrProfile | None = None
  unavailable_reason: str = ""

  @property
  def available(self) -> bool:
    return self.effective_mode is not None

  @property
  def requested_label(self) -> str:
    return steer_ratio_mode_label(self.requested_mode)

  @property
  def effective_label(self) -> str:
    return "Stock car ratio (safe fallback)" if self.effective_mode is None else steer_ratio_mode_label(self.effective_mode)

  @property
  def firmware_vgr_selected(self) -> bool:
    return self.effective_mode is SteerRatioMode.FIRMWARE and self.firmware_profile is not None

  def ratio_at(self, measured_angle_deg: float, live_comma_ratio: float | None = None) -> float:
    if self.effective_mode is SteerRatioMode.COMMA:
      return _safe_positive_ratio(live_comma_ratio, self.cp_ratio)
    if self.effective_mode is SteerRatioMode.NRDR_RAW and self.raw_profile is not None:
      return self.raw_profile.ratio_at(measured_angle_deg)
    if self.effective_mode is SteerRatioMode.MANUAL:
      return float(np.interp(
        abs(measured_angle_deg),
        (0.0, self.manual_outer_angle_deg),
        (self.manual_center, self.manual_final),
      ))
    return self.cp_ratio

  def linearize_measured_angle(self, measured_angle_deg: float) -> float:
    if self.firmware_vgr_selected:
      return self.firmware_profile.physical_to_linear(measured_angle_deg)
    return measured_angle_deg

  def physicalize_desired_angle(self, linear_angle_deg: float) -> float:
    if self.firmware_vgr_selected:
      return self.firmware_profile.linear_to_physical(linear_angle_deg)
    return linear_angle_deg

  def configure_vehicle_model(self, VM, measured_angle_deg: float) -> float:
    live_comma_ratio = VM.sR if self.effective_mode is SteerRatioMode.COMMA else None
    VM.sR = self.ratio_at(measured_angle_deg, live_comma_ratio)
    return VM.sR

  def measured_curvature(self, VM, measured_angle_deg: float, speed: float, roll: float,
                         angle_offset_deg: float = 0.0) -> float:
    self.configure_vehicle_model(VM, measured_angle_deg)
    linear_angle = self.linearize_measured_angle(measured_angle_deg - angle_offset_deg)
    return -VM.calc_curvature(math.radians(linear_angle), speed, roll)

  def curvature_deadzone(self, VM, measured_angle_deg: float, deadzone_deg: float, speed: float,
                         angle_offset_deg: float = 0.0) -> float:
    """Map a physical steering-angle deadzone through the selected geometry."""
    deadzone_deg = abs(float(deadzone_deg))
    center_curvature = self.measured_curvature(VM, measured_angle_deg, speed, 0.0, angle_offset_deg)
    positive_curvature = self.measured_curvature(VM, measured_angle_deg + deadzone_deg, speed, 0.0, angle_offset_deg)
    negative_curvature = self.measured_curvature(VM, measured_angle_deg - deadzone_deg, speed, 0.0, angle_offset_deg)
    self.configure_vehicle_model(VM, measured_angle_deg)
    return max(abs(positive_curvature - center_curvature), abs(negative_curvature - center_curvature))

  def measured_curvature_rate(self, VM, measured_angle_deg: float, steering_rate_deg: float,
                              speed: float, dt: float, angle_offset_deg: float = 0.0) -> float:
    """Finite-difference the selected physical geometry for torque/NNLC jerk."""
    dt = max(float(dt), 1e-3)
    half_step = float(steering_rate_deg) * dt * 0.5
    if abs(half_step) < 1e-12:
      self.configure_vehicle_model(VM, measured_angle_deg)
      return 0.0
    before = self.measured_curvature(VM, measured_angle_deg - half_step, speed, 0.0, angle_offset_deg)
    after = self.measured_curvature(VM, measured_angle_deg + half_step, speed, 0.0, angle_offset_deg)
    self.configure_vehicle_model(VM, measured_angle_deg)
    return (after - before) / dt

  def desired_angle_no_offset(self, VM, measured_angle_deg: float, speed: float, roll: float,
                              desired_curvature: float) -> float:
    self.configure_vehicle_model(VM, measured_angle_deg)
    linear_angle = math.degrees(VM.get_steer_from_curvature(-desired_curvature, speed, roll))
    return self.physicalize_desired_angle(linear_angle)


@dataclass
class SteerRatioModeLatch:
  selection: SteerRatioSelection
  pending: SteerRatioSelection | None = field(init=False, default=None)

  def update(self, candidate: SteerRatioSelection, active: bool) -> SteerRatioSelection:
    if active:
      self.pending = candidate if candidate != self.selection else None
      return self.selection
    self.selection = candidate
    self.pending = None
    return self.selection


def steer_ratio_mode_label(mode: SteerRatioMode) -> str:
  return {
    SteerRatioMode.MANUAL: "Manual override",
    SteerRatioMode.COMMA: "Comma steer-ratio learner",
    SteerRatioMode.NRDR_RAW: "NRDR measured-angle curve",
    SteerRatioMode.FIRMWARE: "Firmware steer ratio",
  }[mode]


def _value(settings: Any, key: str) -> Any:
  try:
    return settings.get(key)
  except (AttributeError, KeyError, TypeError):
    return None


def _mode_value(value: Any) -> SteerRatioMode:
  try:
    if isinstance(value, bytes):
      value = value.decode()
    return SteerRatioMode(int(value))
  except (TypeError, ValueError, UnicodeDecodeError):
    return SteerRatioMode.MANUAL


def _bounded_ratio(value: Any, default: float) -> float:
  try:
    result = float(value)
  except (TypeError, ValueError):
    result = float(default)
  if not math.isfinite(result):
    result = float(default)
  return float(np.clip(result, STEER_RATIO_MIN, STEER_RATIO_MAX))


def _safe_positive_ratio(value: Any, default: float) -> float:
  try:
    result = float(value)
  except (TypeError, ValueError):
    result = float(default)
  return result if math.isfinite(result) and result >= 0.1 else max(float(default), 0.1)


def resolve_steer_ratio_selection(CP, settings: Any) -> SteerRatioSelection:
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  is_honda = str(getattr(CP, "brand", "")).lower() == "honda"
  cp_ratio = _safe_positive_ratio(getattr(CP, "steerRatio", MANUAL_CENTER_DEFAULT), MANUAL_CENTER_DEFAULT)
  mode = _mode_value(_value(settings, "NrdrSteerRatioMode"))
  center = _bounded_ratio(_value(settings, "NrdrSteerRatioManualCenter"), MANUAL_CENTER_DEFAULT)
  final = _bounded_ratio(_value(settings, "NrdrSteerRatioManualFinal"), MANUAL_FINAL_DEFAULT)
  metadata = get_steer_ratio_metadata(fingerprint) if is_honda else None
  outer_angle = metadata.outer_angle if metadata is not None else GENERIC_MANUAL_OUTER_ANGLE_DEG
  raw_profile = RAW_STEER_RATIO_PROFILES.get(fingerprint) if is_honda else None
  firmware_profile = get_honda_vgr_profile(CP)

  effective_mode: SteerRatioMode | None = mode
  unavailable_reason = ""
  if mode is SteerRatioMode.MANUAL and metadata is None:
    effective_mode = None
    unavailable_reason = f"Manual endpoint geometry is not supported for {fingerprint or 'this car'}"
  elif mode is SteerRatioMode.NRDR_RAW and raw_profile is None:
    effective_mode = None
    unavailable_reason = f"No exact audited NRDR raw curve exists for {fingerprint or 'this car'}"
  elif mode is SteerRatioMode.FIRMWARE and firmware_profile is None:
    effective_mode = None
    unavailable_reason = f"No exact recognized EPS firmware profile exists for {fingerprint or 'this car'}"

  return SteerRatioSelection(
    requested_mode=mode,
    effective_mode=effective_mode,
    fingerprint=fingerprint,
    cp_ratio=cp_ratio,
    manual_center=center,
    manual_final=final,
    manual_outer_angle_deg=outer_angle,
    raw_profile=raw_profile,
    firmware_profile=firmware_profile,
    unavailable_reason=unavailable_reason,
  )


def stock_steer_ratio_selection(CP) -> SteerRatioSelection:
  """Safe controller-construction default until controlsd supplies its latched selection."""
  resolved = resolve_steer_ratio_selection(CP, {
    "NrdrSteerRatioMode": SteerRatioMode.MANUAL,
    "NrdrSteerRatioManualCenter": MANUAL_CENTER_DEFAULT,
    "NrdrSteerRatioManualFinal": MANUAL_FINAL_DEFAULT,
  })
  return SteerRatioSelection(
    requested_mode=SteerRatioMode.MANUAL,
    effective_mode=None,
    fingerprint=resolved.fingerprint,
    cp_ratio=resolved.cp_ratio,
    manual_center=resolved.manual_center,
    manual_final=resolved.manual_final,
    manual_outer_angle_deg=resolved.manual_outer_angle_deg,
    raw_profile=resolved.raw_profile,
    firmware_profile=resolved.firmware_profile,
    unavailable_reason="controlsd has not supplied a steer-ratio selection yet",
  )


__all__ = (
  "CLARITY_RAW_STEER_RATIO",
  "GENERIC_MANUAL_OUTER_ANGLE_DEG",
  "MANUAL_CENTER_DEFAULT",
  "MANUAL_FINAL_DEFAULT",
  "RAW_STEER_RATIO_PROFILES",
  "STEER_RATIO_METADATA",
  "STEER_RATIO_METADATA_BY_FP",
  "RawSteerRatioProfile",
  "SteerRatioMetadata",
  "SteerRatioMode",
  "SteerRatioModeLatch",
  "SteerRatioSelection",
  "get_steer_ratio_metadata",
  "resolve_steer_ratio_selection",
  "stock_steer_ratio_selection",
  "steer_ratio_mode_label",
)
