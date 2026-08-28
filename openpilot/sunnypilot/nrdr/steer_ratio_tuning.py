from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum
import math

import numpy as np

from openpilot.sunnypilot.nrdr.honda_vgr import HondaVgrProfile, get_honda_vgr_profile


MANUAL_CENTER_DEFAULT = 15.38
MANUAL_FINAL_DEFAULT = 10.93
GENERIC_OUTER_ANGLE_DEG = 250.0
MIN_STEER_RATIO = 8.0
MAX_STEER_RATIO = 25.0

# Literal atan-domain medians from the Clarity road-learning CSV in nrdr/openpilot commit
# 54f74ae3e5973aa681904780f8cac140870a2b5f (blob
# 8a96cab2b8d5fcfa055709e997bea38e3f5724b0). These are intentionally not smoothed or forced to be
# monotonic: NRDR Raw means the measured data, including its local rises. The final 435.7-degree
# value is a bilateral near-lock anchor extracted with the same geometry estimator from the audited
# synchronized cache. Runtime interpolates these raw estimator values before converting them to the
# effective scalar expected by VehicleModel.
CLARITY_RAW_SOURCE_COMMIT = "54f74ae3e5973aa681904780f8cac140870a2b5f"
CLARITY_RAW_SOURCE_BLOB = "8a96cab2b8d5fcfa055709e997bea38e3f5724b0"
CLARITY_RAW_SYNCED_CSV_SHA256 = "861D8E00B286D5412C6C6D3908564789270A2026EC824EB6F49BD11793D96672"
CLARITY_RAW_EXTRACTOR_SHA256 = "5CE250872F7607409E3562FECC323CC1FF69F3F20351F46BA72FA5887A7185C6"
CLARITY_RAW_TAIL_CACHE_SHA256 = "1A633B31B91EDFFF9CE9D4F83B240566F21476B028D02960E7B14E44839E725B"
CLARITY_RAW_TAIL_CACHE_META_SHA256 = "FAC9AB6F9C4E4DDACDBFC43911F7694DD8E7B07759C8C150F6F4DA12DBAF1CAE"
CLARITY_RAW_TAIL_SEGMENTS = (
  "0000007e--d4a413c4c4--296",
  "00000080--ddc219bb73--4",
  "00000081--49da42be4e--18",
  "0000008a--91b97700bb--5",
  "0000008a--91b97700bb--6",
)
CLARITY_RAW_NEAR_LOCK_ANGLE_DEG = 435.7
CLARITY_RAW_NEAR_LOCK_RAW_DOMAIN_RATIO = 15.435171905851
CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT = 825
CLARITY_RAW_NEAR_LOCK_LEFT_COUNT = 598
CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT = 227
CLARITY_RAW_ANGLE_BP = (
  0.0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5,
  57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5,
  CLARITY_RAW_NEAR_LOCK_ANGLE_DEG,
)
CLARITY_RAW_STEER_RATIO = (
  19.679678, 19.679678, 20.665984, 19.948804, 19.330348, 19.362985,
  19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309,
  17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118,
  17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368,
  CLARITY_RAW_NEAR_LOCK_RAW_DOMAIN_RATIO,
)


def _clarity_raw_clamped_angle_deg(measured_angle_deg: float) -> float:
  angle_deg = abs(float(measured_angle_deg))
  if math.isnan(angle_deg):
    return 0.0
  return min(angle_deg, CLARITY_RAW_ANGLE_BP[-1])


def clarity_raw_domain_ratio_at(measured_angle_deg: float) -> float:
  """Interpolate the archived theta/atan(wheel-angle) ratio domain."""
  clamped_angle_deg = _clarity_raw_clamped_angle_deg(measured_angle_deg)
  return float(np.interp(clamped_angle_deg, CLARITY_RAW_ANGLE_BP, CLARITY_RAW_STEER_RATIO))


def clarity_raw_steer_ratio_at(measured_angle_deg: float) -> float:
  """Convert the interpolated logged atan-domain ratio into VehicleModel's scalar domain."""
  clamped_angle_deg = _clarity_raw_clamped_angle_deg(measured_angle_deg)
  raw_domain_ratio = clarity_raw_domain_ratio_at(clamped_angle_deg)
  if clamped_angle_deg == 0.0:
    return raw_domain_ratio

  theta_rad = math.radians(clamped_angle_deg)
  return theta_rad / math.tan(theta_rad / raw_domain_ratio)


class SteerRatioMode(IntEnum):
  MANUAL = 0
  COMMA = 1
  NRDR_RAW = 2
  FIRMWARE = 3


@dataclass(frozen=True)
class SteerRatioMetadata:
  family: str
  fingerprints: tuple[str, ...]
  outer_angle: float


# The old per-family controls are retired, but their physical outer-angle
# metadata is still needed to give the two global manual controls a meaningful
# shape for a known rack.
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


@dataclass(frozen=True)
class SteerRatioSettings:
  mode: SteerRatioMode
  manual_center: float
  manual_final: float


def parse_steer_ratio_mode(value) -> SteerRatioMode:
  try:
    if isinstance(value, bytes):
      value = value.decode()
    return SteerRatioMode(int(value))
  except (TypeError, ValueError, UnicodeDecodeError):
    return SteerRatioMode.MANUAL


def _bounded_ratio(value, default: float) -> float:
  try:
    if isinstance(value, bytes):
      value = value.decode()
    ratio = float(value)
  except (TypeError, ValueError):
    return default
  if not math.isfinite(ratio):
    return default
  return float(np.clip(ratio, MIN_STEER_RATIO, MAX_STEER_RATIO))


def steer_ratio_settings_from_params(params) -> SteerRatioSettings:
  return SteerRatioSettings(
    parse_steer_ratio_mode(params.get("NrdrSteerRatioMode")),
    _bounded_ratio(params.get("NrdrSteerRatioManualCenter"), MANUAL_CENTER_DEFAULT),
    _bounded_ratio(params.get("NrdrSteerRatioManualFinal"), MANUAL_FINAL_DEFAULT),
  )


def _validated_comma_steer_ratio(live_params, cp_ratio: float, service_valid: bool = True) -> float | None:
  valid = bool(service_valid and getattr(live_params, "steerRatioValid", False))
  try:
    value = float(live_params.steerRatio)
  except (AttributeError, TypeError, ValueError):
    return None
  lower_bound = 0.5 * cp_ratio
  upper_bound = 2.0 * cp_ratio
  return value if valid and math.isfinite(value) and lower_bound <= value <= upper_bound else None


class SteerRatioResolver:
  """One latched steer-ratio policy shared by current and desired geometry."""

  def __init__(self, CP, params) -> None:
    self.brand = str(getattr(CP, "brand", "")).lower()
    self.fingerprint = str(getattr(CP, "carFingerprint", ""))
    try:
      cp_ratio = float(getattr(CP, "steerRatio", MANUAL_CENTER_DEFAULT))
    except (TypeError, ValueError):
      cp_ratio = MANUAL_CENTER_DEFAULT
    self.cp_steer_ratio = cp_ratio if math.isfinite(cp_ratio) and cp_ratio >= 0.1 else MANUAL_CENTER_DEFAULT
    self.metadata = STEER_RATIO_METADATA_BY_FP.get(self.fingerprint)
    self.vgr_profile: HondaVgrProfile | None = get_honda_vgr_profile(CP)
    self._active = steer_ratio_settings_from_params(params)
    self._pending = self._active
    self._comma_ratio = self.cp_steer_ratio

  @property
  def settings(self) -> SteerRatioSettings:
    return self._active

  @property
  def mode(self) -> SteerRatioMode:
    return self._active.mode

  @property
  def available(self) -> bool:
    if self.mode is SteerRatioMode.MANUAL:
      return self.brand == "honda" and self.metadata is not None
    if self.mode is SteerRatioMode.NRDR_RAW:
      return self.brand == "honda" and self.fingerprint == "HONDA_CLARITY"
    if self.mode is SteerRatioMode.FIRMWARE:
      return self.vgr_profile is not None
    return True

  @property
  def firmware_vgr_selected(self) -> bool:
    return self.mode is SteerRatioMode.FIRMWARE and self.available

  @property
  def outer_angle(self) -> float:
    return self.metadata.outer_angle if self.metadata is not None else GENERIC_OUTER_ANGLE_DEG

  def refresh(self, params, lateral_active: bool) -> bool:
    """Read one atomic snapshot and defer a changed tuple until disengagement."""
    requested = steer_ratio_settings_from_params(params)
    self._pending = requested
    if lateral_active:
      return False
    changed = requested != self._active
    self._active = requested
    return changed

  def update_comma_ratio(self, live_params, service_valid: bool = True) -> None:
    # A one-frame validity flicker must not step the geometry back to CP in the
    # middle of a turn. Use CP only until the first good scalar, then hold the
    # last validated value for the life of this resolver/controlsd process.
    value = _validated_comma_steer_ratio(live_params, self.cp_steer_ratio, service_valid)
    if value is not None:
      self._comma_ratio = value

  def effective_ratio(self, measured_angle_deg: float, live_params=None) -> float:
    if self.mode is SteerRatioMode.COMMA:
      return self._comma_ratio
    if self.mode is SteerRatioMode.NRDR_RAW:
      if not self.available:
        return self.cp_steer_ratio
      return clarity_raw_steer_ratio_at(measured_angle_deg)
    if self.mode is SteerRatioMode.FIRMWARE:
      return self.cp_steer_ratio
    if not self.available:
      return self.cp_steer_ratio
    return float(np.interp(
      abs(measured_angle_deg),
      (0.0, self.outer_angle),
      (self.settings.manual_center, self.settings.manual_final),
    ))

  @contextmanager
  def _scalar_vehicle_model(self, VM, ratio: float) -> Iterator[None]:
    previous_ratio = VM.sR
    had_curve = hasattr(VM, "sr_curve")
    try:
      VM.sR = ratio
      # The development opendbc has a fingerprint curve in VehicleModel. Mode
      # selection is authoritative, so never let that hidden curve compose with
      # the selected resolver policy.
      if had_curve:
        VM.sr_curve = None
      yield
    finally:
      VM.sR = previous_ratio
      if had_curve:
        # The explicit selection replaces the development submodule's implicit
        # fingerprint curve for the remainder of this VehicleModel's lifetime.
        VM.sr_curve = None

  def calc_curvature_for_angle(self, VM, steering_angle_deg: float, measured_angle_deg: float,
                               angle_offset_deg: float, v_ego: float, roll: float) -> float:
    angle_no_offset = steering_angle_deg - angle_offset_deg
    if self.firmware_vgr_selected:
      angle_no_offset = self.vgr_profile.physical_to_linear(angle_no_offset)
    ratio = self.effective_ratio(measured_angle_deg)
    with self._scalar_vehicle_model(VM, ratio):
      return -VM.calc_curvature(math.radians(angle_no_offset), v_ego, roll)

  def calc_curvature(self, VM, measured_angle_deg: float, angle_offset_deg: float,
                     v_ego: float, roll: float, live_params=None) -> float:
    return self.calc_curvature_for_angle(
      VM, measured_angle_deg, measured_angle_deg, angle_offset_deg, v_ego, roll,
    )

  def curvature_deadzone(self, VM, measured_angle_deg: float, deadzone_deg: float, v_ego: float,
                         angle_offset_deg: float = 0.0) -> float:
    """Map a physical steering-angle deadzone through the local selected geometry."""
    deadzone_deg = abs(float(deadzone_deg))
    center = self.calc_curvature(VM, measured_angle_deg, angle_offset_deg, v_ego, 0.0)
    positive = self.calc_curvature(VM, measured_angle_deg + deadzone_deg, angle_offset_deg, v_ego, 0.0)
    negative = self.calc_curvature(VM, measured_angle_deg - deadzone_deg, angle_offset_deg, v_ego, 0.0)
    return max(abs(positive - center), abs(negative - center))

  def measured_curvature_rate(self, VM, measured_angle_deg: float, steering_rate_deg: float,
                              v_ego: float, dt: float, angle_offset_deg: float = 0.0) -> float:
    """Finite-difference the full physical geometry, including ratio/VGR slope."""
    dt = max(float(dt), 1e-3)
    half_step = float(steering_rate_deg) * dt * 0.5
    if abs(half_step) < 1e-12:
      return 0.0
    before = self.calc_curvature(VM, measured_angle_deg - half_step, angle_offset_deg, v_ego, 0.0)
    after = self.calc_curvature(VM, measured_angle_deg + half_step, angle_offset_deg, v_ego, 0.0)
    return (after - before) / dt

  def calc_curvature_rate(self, VM, steering_rate_deg: float, measured_angle_deg: float,
                          v_ego: float, dt: float = 0.01, angle_offset_deg: float = 0.0) -> float:
    return self.measured_curvature_rate(VM, measured_angle_deg, steering_rate_deg, v_ego, dt, angle_offset_deg)

  def desired_angle_no_offset(self, VM, measured_angle_deg: float, v_ego: float,
                              roll: float, desired_curvature: float, live_params=None) -> float:
    ratio = self.effective_ratio(measured_angle_deg, live_params)
    with self._scalar_vehicle_model(VM, ratio):
      angle = math.degrees(VM.get_steer_from_curvature(-desired_curvature, v_ego, roll))
    if self.firmware_vgr_selected:
      angle = self.vgr_profile.linear_to_physical(angle)
    return angle


def get_steer_ratio_metadata(fingerprint: str) -> SteerRatioMetadata | None:
  return STEER_RATIO_METADATA_BY_FP.get(str(fingerprint))
