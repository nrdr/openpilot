"""Explicit, auditable steer-ratio modes shared by controlsd and lateral PID."""

from dataclasses import dataclass, field, replace
from enum import IntEnum
import math
from typing import Any

import numpy as np

from openpilot.nrdr.features.lateral.honda_vgr import HondaVgrProfile, get_honda_vgr_profile, normalize_honda_eps_firmware
from openpilot.nrdr.features.lateral.hybrid_steer_ratio import AngleSource, HybridGeometry, BLEND_START_DEFAULT, build_hybrid


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
  # Keep the legacy name/API for Clarity and stored mode 2. New profiles must
  # state their domain: a model-normalized ratio must not be converted twice.
  ratio_domain: str = "raw-angle"
  eps_firmware: tuple[str, ...] = ()
  provisional: bool = False
  observed_angle_range: tuple[float, float] | None = None

  def __post_init__(self) -> None:
    if len(self.angles_deg) != len(self.ratios) or len(self.angles_deg) < 2:
      raise ValueError("raw steer-ratio curves require matching angle and ratio arrays")
    if (any(not math.isfinite(value) for value in self.angles_deg) or self.angles_deg[0] != 0.0
        or any(b <= a for a, b in zip(self.angles_deg, self.angles_deg[1:], strict=False))):
      raise ValueError("raw steer-ratio angles must start at zero and increase")
    if any(not math.isfinite(value) or value <= 0.0 for value in self.ratios):
      raise ValueError("raw steer-ratio samples must be finite and positive")
    if self.ratio_domain not in ("raw-angle", "vehicle-model"):
      raise ValueError("unknown steer-ratio domain")
    if self.ratio_domain == "vehicle-model":
      normalized = [angle / ratio for angle, ratio in zip(self.angles_deg, self.ratios, strict=True)]
      if any(b <= a for a, b in zip(normalized, normalized[1:], strict=False)):
        raise ValueError("vehicle-model curve must preserve increasing angle-to-curvature mapping")
    if self.provisional and self.observed_angle_range is None:
      raise ValueError("provisional profiles must disclose their observed range")
    if self.observed_angle_range is not None:
      lower, upper = self.observed_angle_range
      if not 0.0 <= lower < upper <= self.angles_deg[-1]:
        raise ValueError("observed range must be inside the profile anchors")

  def _clamped_angle_deg(self, measured_angle_deg: float) -> float:
    angle_deg = abs(float(measured_angle_deg))
    if math.isnan(angle_deg):
      return 0.0
    return min(angle_deg, self.angles_deg[-1])

  def raw_domain_ratio_at(self, measured_angle_deg: float) -> float:
    """Interpolate stored ratios in the profile's explicitly declared domain."""
    angle_deg = self._clamped_angle_deg(measured_angle_deg)
    return float(np.interp(angle_deg, self.angles_deg, self.ratios))

  def ratio_at(self, measured_angle_deg: float) -> float:
    """Return the equivalent small-angle ratio expected by VehicleModel."""
    angle_deg = self._clamped_angle_deg(measured_angle_deg)
    raw_domain_ratio = self.raw_domain_ratio_at(angle_deg)
    if self.ratio_domain == "vehicle-model" or angle_deg == 0.0:
      return raw_domain_ratio
    theta_rad = math.radians(angle_deg)
    return theta_rad / math.tan(theta_rad / raw_domain_ratio)


_CLARITY_54F_RAW_ANGLES = (
  0.0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5,
  57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5,
)
_CLARITY_54F_RAW_DOMAIN_RATIOS = (
  19.679678, 19.679678, 20.665984, 19.948804, 19.330348, 19.362985,
  19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309,
  17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118,
  17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368,
)
_CLARITY_NEAR_LOCK_ANGLE_DEG = 435.7
_CLARITY_NEAR_LOCK_RAW_DOMAIN_RATIO = 15.435171905851

CLARITY_RAW_STEER_RATIO = RawSteerRatioProfile(
  name="Clarity measured-angle raw-to-VM curve",
  fingerprint="HONDA_CLARITY",
  angles_deg=_CLARITY_54F_RAW_ANGLES + (_CLARITY_NEAR_LOCK_ANGLE_DEG,),
  ratios=_CLARITY_54F_RAW_DOMAIN_RATIOS + (_CLARITY_NEAR_LOCK_RAW_DOMAIN_RATIO,),
  provenance="54f74ae3e5973aa681904780f8cac140870a2b5f:sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv" +
             "@8a96cab2b8d5fcfa055709e997bea38e3f5724b0 + audited bilateral near-lock anchor; " +
             "see openpilot/nrdr/features/lateral/CLARITY_RAW_STEER_RATIO_EVIDENCE.md",
)

CIVIC_TEG_PROVISIONAL_STEER_RATIO = RawSteerRatioProfile(
  name="Civic TEG-A010 provisional v0 (2026-09-13)",
  fingerprint="HONDA_CIVIC",
  angles_deg=(0.0, 3.292, 8.783, 19.289, 35.669, 58.671),
  ratios=(15.8207, 15.8207, 15.6557, 15.5427, 15.1964, 14.7617),
  provenance="2026-09-13 routes 00000059--23041ba9e2, 0000005a--8cecadb216, 0000005b--b351e105bb; " +
             "sr_samples.csv.gz SHA256 15c8c34551eb6dd9d31e09a9959225dbe1c0e2dbdff5522e62dc1ac9daedec5a; " +
             "see openpilot/nrdr/features/lateral/CIVIC_TEG_PROVISIONAL_STEER_RATIO_EVIDENCE.md",
  ratio_domain="vehicle-model",
  eps_firmware=("39990-TEG-A010",),
  provisional=True,
  observed_angle_range=(3.292, 58.671),
)

RAW_STEER_RATIO_PROFILES = {
  profile.fingerprint: profile for profile in (CLARITY_RAW_STEER_RATIO, CIVIC_TEG_PROVISIONAL_STEER_RATIO)
}


def get_raw_steer_ratio_profile(CP) -> RawSteerRatioProfile | None:
  """Resolve data profiles without borrowing evidence from a different EPS."""
  if str(getattr(CP, "brand", "")).lower() != "honda":
    return None
  profile = RAW_STEER_RATIO_PROFILES.get(str(getattr(CP, "carFingerprint", "")))
  if profile is None or not profile.eps_firmware:
    return profile
  versions = {normalize_honda_eps_firmware(fw.fwVersion) for fw in getattr(CP, "carFw", ()) if fw.ecu == "eps"}
  return profile if versions and versions.issubset(profile.eps_firmware) else None


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
  hybrid_requested: bool = False
  hybrid: HybridGeometry | None = None

  @property
  def available(self) -> bool:
    return self.effective_mode is not None

  @property
  def requested_label(self) -> str:
    return "Hybrid steer ratio" if self.hybrid_requested else steer_ratio_mode_label(self.requested_mode)

  @property
  def effective_label(self) -> str:
    if self.hybrid is not None:
      return f"Hybrid: {self.hybrid.a.label} → {self.hybrid.b.label} ({self.hybrid.start:g}–{self.hybrid.end:g}°)"
    if self.effective_mode is SteerRatioMode.NRDR_RAW and self.raw_profile is not None and self.raw_profile.provisional:
      return "NRDR measured-angle curve (provisional)"
    return "Stock car ratio (safe fallback)" if self.effective_mode is None else steer_ratio_mode_label(self.effective_mode)

  @property
  def firmware_vgr_selected(self) -> bool:
    if self.hybrid is not None:
      return SteerRatioMode.FIRMWARE in (self.hybrid.a.mode, self.hybrid.b.mode)
    return self.effective_mode is SteerRatioMode.FIRMWARE and self.firmware_profile is not None

  def ratio_at(self, measured_angle_deg: float, live_comma_ratio: float | None = None) -> float:
    if self.hybrid is not None:
      return self.cp_ratio
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
    if self.hybrid is not None:
      return self.hybrid.forward(measured_angle_deg)
    if self.firmware_vgr_selected:
      return self.firmware_profile.physical_to_linear(measured_angle_deg)
    return measured_angle_deg

  def physicalize_desired_angle(self, linear_angle_deg: float) -> float:
    if self.hybrid is not None:
      return self.hybrid.inverse(linear_angle_deg)
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
  """Capture one complete geometry selection for the current control frame."""
  selection: SteerRatioSelection
  pending: SteerRatioSelection | None = field(init=False, default=None)
  rejected_reason: str = field(init=False, default="")

  def update(self, candidate: SteerRatioSelection, active: bool) -> SteerRatioSelection:
    self.rejected_reason = candidate.unavailable_reason if candidate.hybrid_requested and not candidate.available else ""
    if self.rejected_reason and active:
      # Invalid live edits must not switch an engaged controller to an unrelated
      # geometry. Startup's existing stock selection remains the safe baseline.
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
  except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
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


def resolve_steer_ratio_selection(CP, settings: Any, live_comma_ratio: float | None = None) -> SteerRatioSelection:
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  is_honda = str(getattr(CP, "brand", "")).lower() == "honda"
  cp_ratio = _safe_positive_ratio(getattr(CP, "steerRatio", MANUAL_CENTER_DEFAULT), MANUAL_CENTER_DEFAULT)
  mode = _mode_value(_value(settings, "NrdrSteerRatioMode"))
  center = _bounded_ratio(_value(settings, "NrdrSteerRatioManualCenter"), MANUAL_CENTER_DEFAULT)
  final = _bounded_ratio(_value(settings, "NrdrSteerRatioManualFinal"), MANUAL_FINAL_DEFAULT)
  metadata = get_steer_ratio_metadata(fingerprint) if is_honda else None
  outer_angle = metadata.outer_angle if metadata is not None else GENERIC_MANUAL_OUTER_ANGLE_DEG
  raw_profile = get_raw_steer_ratio_profile(CP)
  firmware_profile = get_honda_vgr_profile(CP)

  effective_mode: SteerRatioMode | None = mode
  unavailable_reason = ""
  if mode is SteerRatioMode.MANUAL and metadata is None:
    effective_mode = None
    unavailable_reason = f"Manual endpoint geometry is not supported for {fingerprint or 'this car'}"
  elif mode is SteerRatioMode.NRDR_RAW and raw_profile is None:
    effective_mode = None
    unavailable_reason = f"No matching NRDR measured curve exists for {fingerprint or 'this car'} and its reported EPS"
  elif mode is SteerRatioMode.FIRMWARE and firmware_profile is None:
    effective_mode = None
    unavailable_reason = f"No exact recognized EPS firmware profile exists for {fingerprint or 'this car'}"

  selection = SteerRatioSelection(
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
  enabled = _value(settings, "NrdrSteerRatioHybrid")
  if str(enabled).lower() not in ("1", "true", "b'1'", "b'true'"):
    return selection
  selection = replace(selection, hybrid_requested=True)
  try:
    mode = SteerRatioMode(int(_value(settings, "NrdrSteerRatioMode")))
    mode_b_value = _value(settings, "NrdrSteerRatioSourceB")
    start_value = _value(settings, "NrdrSteerRatioBlendStart")
    mode_b = SteerRatioMode(3 if mode_b_value is None else int(mode_b_value))
    start = BLEND_START_DEFAULT if start_value is None else float(start_value)
    if not selection.available:
      raise ValueError(selection.unavailable_reason)
    if not is_honda or metadata is None:
      raise ValueError("Hybrid requires supported Honda geometry metadata")
    if SteerRatioMode.NRDR_RAW in (mode, mode_b) and raw_profile is None:
      raise ValueError("Hybrid source has no matching measured car/EPS profile")
    if SteerRatioMode.FIRMWARE in (mode, mode_b) and firmware_profile is None:
      raise ValueError("Hybrid source has no recognized EPS firmware profile")
    comma = _safe_positive_ratio(live_comma_ratio, cp_ratio) if SteerRatioMode.COMMA in (mode, mode_b) else cp_ratio
    def source(source_mode):
      label = steer_ratio_mode_label(source_mode)
      if source_mode is SteerRatioMode.NRDR_RAW and raw_profile.provisional:
        label += " (provisional)"
      return AngleSource(int(source_mode), label, cp_ratio,
                         center, final, outer_angle, comma, raw_profile, firmware_profile)
    return replace(selection, hybrid=build_hybrid(source(mode), source(mode_b), start))
  except (TypeError, ValueError, OverflowError) as error:
    return replace(selection, effective_mode=None, unavailable_reason=f"Hybrid unavailable: {error}")


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
  "CIVIC_TEG_PROVISIONAL_STEER_RATIO",
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
  "get_raw_steer_ratio_profile",
  "resolve_steer_ratio_selection",
  "stock_steer_ratio_selection",
  "steer_ratio_mode_label",
)
