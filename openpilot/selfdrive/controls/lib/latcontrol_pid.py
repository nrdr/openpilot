import math
from itertools import pairwise

import numpy as np
from openpilot.cereal import log
from opendbc.car.honda.carcontroller import get_eps_modified_steering_pressed
from opendbc.car.honda.steer_ratio import (get_honda_vgr_inverse, get_honda_vgr_learning_inverse,
                                           vgr_linear_to_physical)
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params, UnknownKeyName
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.nrdr_lat_stiction import LatStiction
from openpilot.selfdrive.controls.lib.nrdr_tune_learner import TuneLearner
from openpilot.selfdrive.modeld.constants import ModelConstants


def _effective_sr_from_local_curve(angle_bp, relative_local_sr, center_sr, output_bp=None):
  """Convert a local VGR ratio shape into the cumulative ratio VehicleModel expects."""
  if len(angle_bp) != len(relative_local_sr) or len(angle_bp) < 2:
    raise ValueError("local steer-ratio breakpoints and values must have matching lengths")
  if angle_bp[0] != 0.0 or center_sr <= 0.0:
    raise ValueError("local steer-ratio curve must start at zero with a positive center ratio")
  if not all(left < right for left, right in pairwise(angle_bp)):
    raise ValueError("local steer-ratio breakpoints must be strictly increasing")
  if not all(value > 0.0 for value in relative_local_sr):
    raise ValueError("local steer-ratio values must be positive")
  if output_bp is None:
    output_bp = angle_bp
  if (not output_bp or output_bp[0] != 0.0 or output_bp[-1] > angle_bp[-1] or
      not all(left < right for left, right in pairwise(output_bp))):
    raise ValueError("effective steer-ratio output breakpoints must be ordered within the local curve")

  # Road-wheel angle is the integral of steering-wheel travel divided by the
  # instantaneous/local ratio. The effective ratio at each knot is therefore
  # wheel angle divided by that accumulated road-wheel angle. Integrate each
  # piecewise-linear local-ratio segment analytically.
  effective_sr = []
  for output_angle in output_bp:
    if output_angle == 0.0:
      effective_sr.append(center_sr * relative_local_sr[0])
      continue

    road_wheel_angle = 0.0
    for left_angle, right_angle, left_rel, right_rel in zip(
        angle_bp[:-1], angle_bp[1:], relative_local_sr[:-1], relative_local_sr[1:], strict=True):
      if output_angle <= left_angle:
        break
      segment_right_angle = min(output_angle, right_angle)
      segment_fraction = (segment_right_angle - left_angle) / (right_angle - left_angle)
      segment_right_rel = left_rel + segment_fraction * (right_rel - left_rel)
      left_sr = center_sr * left_rel
      segment_right_sr = center_sr * segment_right_rel
      angle_delta = segment_right_angle - left_angle
      if math.isclose(left_sr, segment_right_sr, rel_tol=0.0, abs_tol=1e-12):
        road_wheel_angle += angle_delta / left_sr
      else:
        road_wheel_angle += angle_delta * math.log(segment_right_sr / left_sr) / (segment_right_sr - left_sr)
      if output_angle <= right_angle:
        break
    effective_sr.append(output_angle / road_wheel_angle)

  return effective_sr


def _curve_breakpoints(source_bp, lock_angle, guard_angle, sample_step=10.0):
  """Densify a source curve through physical lock and append an interpolation guard."""
  if lock_angle <= 0.0 or guard_angle < lock_angle or sample_step <= 0.0:
    raise ValueError("steer-ratio lock, guard, and sample step must be positive and ordered")

  sample_count = int(math.ceil(lock_angle / sample_step))
  return sorted(set(
    [float(angle) for angle in source_bp if angle <= lock_angle] +
    [min(index * sample_step, lock_angle) for index in range(sample_count + 1)] +
    [float(lock_angle), float(guard_angle)]
  ))


def _endpoint_constrained_effective_sr_curve(angle_bp, effective_sr, fade_start_angle,
                                             lock_angle, final_sr, guard_angle, sample_step=10.0):
  """Preserve the evidenced curve, then smoothly land on the published full-off-center ratio."""
  if len(angle_bp) != len(effective_sr) or len(angle_bp) < 2:
    raise ValueError("effective steer-ratio breakpoints and values must have matching lengths")
  if angle_bp[0] != 0.0 or not all(left < right for left, right in pairwise(angle_bp)):
    raise ValueError("effective steer-ratio breakpoints must start at zero and be strictly increasing")
  if not all(value > 0.0 for value in effective_sr):
    raise ValueError("effective steer-ratio values must be positive")
  if not 0.0 <= fade_start_angle < lock_angle:
    raise ValueError("outer steer-ratio fade must start before physical lock")

  output_bp = _curve_breakpoints(angle_bp, lock_angle, guard_angle, sample_step)
  base_at_lock = float(np.interp(lock_angle, angle_bp, effective_sr))
  if final_sr <= 0.0 or final_sr > base_at_lock:
    raise ValueError("published outer ratio must be positive and may only reduce the evidenced curve")
  endpoint_scale = final_sr / base_at_lock

  output_sr = []
  for angle in output_bp:
    base_sr = float(np.interp(min(angle, lock_angle), angle_bp, effective_sr))
    fade = min(max((angle - fade_start_angle) / (lock_angle - fade_start_angle), 0.0), 1.0)
    smoothstep = fade * fade * (3.0 - 2.0 * fade)
    output_sr.append(base_sr * (1.0 + smoothstep * (endpoint_scale - 1.0)))

  # The firmware curve may contain a genuine near-center rise. Only the outer
  # correction is required to be non-increasing.
  outer_sr = [value for angle, value in zip(output_bp, output_sr, strict=True) if angle >= fade_start_angle]
  if not all(left >= right for left, right in pairwise(outer_sr)):
    raise ValueError("endpoint-constrained steer-ratio tail must not increase")
  return output_bp, output_sr


def _absolute_sr_curve_with_local_firmware_tail(inner_angle_bp, inner_sr, join_angle,
                                                local_angle_bp, relative_local_sr,
                                                fade_start_angle, lock_angle, final_sr,
                                                guard_angle, sample_step=10.0):
  """Join a road-validated inner curve to a firmware-local VGR shape and physical endpoint."""
  if not inner_angle_bp or inner_angle_bp[0] != 0.0 or inner_angle_bp[-1] != join_angle:
    raise ValueError("inner steer-ratio curve must run from zero through the requested join angle")
  if local_angle_bp[-1] < lock_angle:
    raise ValueError("firmware-local curve must cover physical steering lock")

  base_bp = _curve_breakpoints(
    sorted({*inner_angle_bp, *local_angle_bp}), lock_angle, lock_angle, sample_step,
  )
  firmware_effective_sr = _effective_sr_from_local_curve(
    local_angle_bp, relative_local_sr, 1.0, output_bp=base_bp,
  )
  firmware_at_join = float(np.interp(join_angle, base_bp, firmware_effective_sr))
  inner_at_join = float(np.interp(join_angle, inner_angle_bp, inner_sr))
  base_sr = [
    float(np.interp(angle, inner_angle_bp, inner_sr)) if angle <= join_angle
    else inner_at_join * firmware_sr / firmware_at_join
    for angle, firmware_sr in zip(base_bp, firmware_effective_sr, strict=True)
  ]
  return _endpoint_constrained_effective_sr_curve(
    base_bp, base_sr, fade_start_angle, lock_angle, final_sr, guard_angle, sample_step,
  )


def _inverse_vgr_from_effective_sr_curve(angle_bp, effective_sr):
  """Pre-solve an effective SR curve into model-angle -> real-angle coordinates."""
  if len(angle_bp) != len(effective_sr) or not angle_bp or angle_bp[0] != 0.0:
    raise ValueError("inverse VGR source curve must contain matching values starting at zero")
  center_sr = effective_sr[0]
  if center_sr <= 0.0:
    raise ValueError("inverse VGR source curve must have a positive center ratio")
  linear_bp = [
    0.0 if angle == 0.0 else angle / (steer_ratio / center_sr)
    for angle, steer_ratio in zip(angle_bp, effective_sr, strict=True)
  ]
  if not all(left < right for left, right in pairwise(linear_bp)):
    raise ValueError("inverse VGR model-angle breakpoints must be strictly increasing")
  return linear_bp


# Effective steer-ratio curves, keyed explicitly by fingerprint.
#
# paramsd estimates one near-center scalar (it only observes steering angles below
# 45 degrees), so it cannot learn a rack's off-center taper. Legacy absolute
# curves replace that scalar when learning is off; firmware-derived inverse maps
# instead reshape the scalar model output and can follow paramsd as it relearns.
# Every unmapped car keeps its normal CP.steerRatio behavior.
# Honda publishes final full-off-center ratios rather than center ratios. Keep
# each car's road-validated/effective inner calibration and firmware VGR shape,
# then remove the remaining model compensation gradually so the published ratio
# is reached at physical lock -- never at an arbitrary 80-90 degree breakpoint.
NRDR_CIVIC_LOCK_ANGLE = 2.22 * 180.0
NRDR_CIVIC_FINAL_SR = 10.93
NRDR_ACCORD_LOCK_ANGLE = 2.30 * 180.0
NRDR_ACCORD_FINAL_SR = 11.82
NRDR_CLARITY_LOCK_ANGLE = 2.41 * 180.0
NRDR_CLARITY_FINAL_SR = 12.72
NRDR_CRV_5G_LOCK_ANGLE = 2.30 * 180.0
NRDR_CRV_5G_FINAL_SR = 12.30
NRDR_INSIGHT_LOCK_ANGLE = 2.54 * 180.0
NRDR_INSIGHT_FINAL_SR = 12.58

# Legacy Clarity fixed path. Its tail was historically shaped from the EPS B
# table, which vote_for_nobody later proved belongs to the rate path rather than
# the steering-position conversion. Retain it as Brett's road-tested outer
# envelope and published-endpoint path; the exact A position table used by the
# learned inner path now lives in opendbc.car.honda.steer_ratio.
NRDR_CLARITY_INNER_SR_BP = [
  0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5,
  62.5, 67.5, 70.,
]
NRDR_CLARITY_INNER_SR_V = [
  20.114, 20.114, 20.114, 20.052, 19.407, 19.398, 19.398, 19.240, 18.452, 18.250,
  18.250, 18.178, 17.940, 17.940, 17.625, 17.584,
]
NRDR_CLARITY_VGR_SOURCE_ANGLE_BP = [
  0.000, 4.052, 8.104, 12.102, 16.201, 20.205, 24.299, 28.299, 32.296, 40.194,
  59.571, 78.095, 95.805, 104.440, 450.000,
]
NRDR_CLARITY_VGR_SOURCE_REL_LOCAL = [
  1.000000, 1.000000, 1.000000, 1.000000, 0.999938, 0.998460, 0.995087, 0.989980,
  0.983193, 0.965501, 0.909060, 0.858900, 0.834355, 0.833325, 0.833325,
]
NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_SR_CURVE_V = _absolute_sr_curve_with_local_firmware_tail(
  NRDR_CLARITY_INNER_SR_BP,
  NRDR_CLARITY_INNER_SR_V,
  70.0,
  NRDR_CLARITY_VGR_SOURCE_ANGLE_BP,
  NRDR_CLARITY_VGR_SOURCE_REL_LOCAL,
  104.440,
  NRDR_CLARITY_LOCK_ANGLE,
  NRDR_CLARITY_FINAL_SR,
  450.0,
)
NRDR_CLARITY_CENTER_SR = NRDR_CLARITY_SR_CURVE_V[0]

# The 5th-gen CR-V curve is evidenced through 200 deg. Hold that base value
# outside the measured region, then remove the remaining compensation through
# the published 12.30 ratio at its 2.30-turn physical lock.
NRDR_CRV_5G_BASE_SR_BP = [0., 50., 100., 150., 175., 200., NRDR_CRV_5G_LOCK_ANGLE]
NRDR_CRV_5G_BASE_SR_V = [18.10, 17.80, 16.30, 15.30, 14.90, 14.60, 14.60]
NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_SR_CURVE_V = _endpoint_constrained_effective_sr_curve(
  NRDR_CRV_5G_BASE_SR_BP,
  NRDR_CRV_5G_BASE_SR_V,
  200.0,
  NRDR_CRV_5G_LOCK_ANGLE,
  NRDR_CRV_5G_FINAL_SR,
  450.0,
)
NRDR_CRV_5G_CENTER_SR = NRDR_CRV_5G_SR_CURVE_V[0]

# Legacy Civic Bosch fixed path. Peter's telemetry remains the absolute truth
# through 70 deg and the existing road-tested tail lands on the non-Sport 10.93
# Honda endpoint. The B table below is retained only as that fixed tail's
# historical shape; vote_for_nobody's correct A position map is used separately.
# Sport/Sport Touring share this fingerprint but publish 11.12; selecting that
# endpoint requires a verified EPS-firmware-to-trim mapping, not a guess.
NRDR_CIVIC_BOSCH_INNER_SR_BP = [
  0., 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 62.5, 70.,
]
NRDR_CIVIC_BOSCH_INNER_SR_V = [
  19.095, 19.095, 18.276, 16.335, 16.335, 16.335, 16.246, 15.291, 15.291, 14.675,
  14.393, 13.596, 13.596,
]
NRDR_CIVIC_BOSCH_VGR_SOURCE_ANGLE_BP = [
  0.000, 3.174, 6.357, 9.526, 12.659, 15.874, 18.966, 22.079, 25.220, 31.530,
  46.992, 62.146, 76.730, 83.840, 86.641, 89.426, 92.125, 94.948, 97.686, 100.413,
  103.150, 105.874, 108.584, 111.269, 450.000,
]
NRDR_CIVIC_BOSCH_VGR_SOURCE_REL_LOCAL = [
  1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 0.992, 0.992, 0.992, 0.984,
  0.955, 0.913, 0.881, 0.863, 0.857, 0.852, 0.852, 0.846, 0.840, 0.840,
  0.835, 0.835, 0.835, 0.829, 0.829,
]
NRDR_CIVIC_BOSCH_SR_CURVE_BP, NRDR_CIVIC_BOSCH_SR_CURVE_V = _absolute_sr_curve_with_local_firmware_tail(
  NRDR_CIVIC_BOSCH_INNER_SR_BP,
  NRDR_CIVIC_BOSCH_INNER_SR_V,
  70.0,
  NRDR_CIVIC_BOSCH_VGR_SOURCE_ANGLE_BP,
  NRDR_CIVIC_BOSCH_VGR_SOURCE_REL_LOCAL,
  111.269,
  NRDR_CIVIC_LOCK_ANGLE,
  NRDR_CIVIC_FINAL_SR,
  450.0,
)
NRDR_CIVIC_BOSCH_CENTER_SR = NRDR_CIVIC_BOSCH_SR_CURVE_V[0]

# Civic TBA-A030 / TEG-A010 Nidec EPS position table, re-indexed to the
# steering-angle coordinate published on CAN. Firmware computes published
# angle as raw_position / gain(raw_position), so center_gain / gain is already
# the cumulative/effective SR multiplier; it must not be integrated again.
# 596.023 degrees is the firmware's interpolation guard, not a claimed lock.
NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP = [
  0.000, 3.125, 6.400, 9.524, 12.698, 15.748, 19.047, 22.222, 25.397, 31.746,
  47.243, 62.017, 76.336, 83.333, 86.363, 88.721, 91.728, 94.028, 97.013, 99.998,
  102.224, 105.187, 107.354, 110.295, 131.387, 152.173, 170.216, 188.812, 208.333, 596.023,
]
NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR = [
  1.000, 1.000, 1.024, 1.016, 1.016, 1.008, 1.016, 1.016, 1.016, 1.016,
  1.008, 0.992, 0.977, 0.970, 0.970, 0.962, 0.962, 0.955, 0.955, 0.955,
  0.948, 0.948, 0.941, 0.941, 0.934, 0.928, 0.908, 0.895, 0.889, 0.848,
]
# The position map remains authoritative through its final real knot at
# 208.333 deg. The 596.023-deg value is only a firmware guard, so use that open
# interval to land on Honda's 10.93 ratio at the actual 399.6-deg lock.
NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR = 15.38
# The 2026-08-11 Civic route consistently required more effective ratio close
# to center: 18.27 in the 2-4 deg bin and 17.46 across the adjacent 4-8 deg
# bins. Blend back to the original firmware-derived absolute curve at 9.524
# degrees. Every higher-angle effective-SR value remains bit-for-bit unchanged.
NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_BP = [0.000, 3.125, 6.400, 9.524]
NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V = [
  18.270,
  18.270,
  17.460,
  NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR * 1.016,
]
NRDR_CIVIC_NIDEC_CENTER_SR = NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V[0]
NRDR_CIVIC_NIDEC_SOURCE_EFFECTIVE_SR_V = [
  float(np.interp(angle, NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_BP, NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_V))
  if angle <= NRDR_CIVIC_NIDEC_LEARNED_LOW_ANGLE_SR_BP[-1]
  else NRDR_CIVIC_NIDEC_FIRMWARE_CENTER_SR * multiplier
  for angle, multiplier in zip(
    NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP,
    NRDR_CIVIC_NIDEC_VGR_SOURCE_REL_EFFECTIVE_SR,
    strict=True,
  )
]
NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_EFFECTIVE_SR_V = _endpoint_constrained_effective_sr_curve(
  NRDR_CIVIC_NIDEC_VGR_SOURCE_ANGLE_BP,
  NRDR_CIVIC_NIDEC_SOURCE_EFFECTIVE_SR_V,
  208.333,
  NRDR_CIVIC_LOCK_ANGLE,
  NRDR_CIVIC_FINAL_SR,
  596.023,
)
NRDR_CIVIC_NIDEC_RELATIVE_EFFECTIVE_SR_V = [
  effective_sr / NRDR_CIVIC_NIDEC_CENTER_SR
  for effective_sr in NRDR_CIVIC_NIDEC_EFFECTIVE_SR_V
]
# Pre-solve the nonlinear inverse. VehicleModel first produces the steering
# angle it would request with its current scalar ratio (CP or paramsd). Mapping
# that normalized constant-ratio coordinate back to the real wheel angle avoids
# a measured-angle dependency and automatically follows scalar relearning.
NRDR_CIVIC_NIDEC_LINEAR_BP = _inverse_vgr_from_effective_sr_curve(
  NRDR_CIVIC_NIDEC_VGR_ANGLE_BP,
  NRDR_CIVIC_NIDEC_EFFECTIVE_SR_V,
)

# Legacy Insight fixed outer path, retained to preserve nrdr's previous endpoint
# behavior. This secondary rate-table shape is not used as the learned physical
# position map; the exact TXM-A040 A position table lives in steer_ratio.py.
NRDR_INSIGHT_VGR_SOURCE_ANGLE_BP = [
  0.000, 3.721, 7.302, 10.972, 14.610, 18.228, 21.864, 25.517, 29.156, 36.296,
  53.978, 70.999, 87.308, 95.243, 450.000,
]
NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL = [
  1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.998445, 0.995081, 0.989922,
  0.983180, 0.965570, 0.909063, 0.858696, 0.833564, 0.833141, 0.833141,
]
# The published 2.54-turn lock is 457.2 deg, just beyond the 450-deg firmware
# guard. Extend the already-flat local tail by those final 7.2 degrees, then
# apply the small endpoint correction from the end of the firmware transition.
NRDR_INSIGHT_VGR_INTEGRATION_ANGLE_BP = [
  *NRDR_INSIGHT_VGR_SOURCE_ANGLE_BP,
  NRDR_INSIGHT_LOCK_ANGLE,
]
NRDR_INSIGHT_VGR_INTEGRATION_REL_LOCAL = [
  *NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL,
  NRDR_INSIGHT_VGR_SOURCE_REL_LOCAL[-1],
]
NRDR_INSIGHT_BASE_ANGLE_BP = _curve_breakpoints(
  NRDR_INSIGHT_VGR_INTEGRATION_ANGLE_BP,
  NRDR_INSIGHT_LOCK_ANGLE,
  NRDR_INSIGHT_LOCK_ANGLE,
)
NRDR_INSIGHT_BASE_REL_EFFECTIVE_SR = _effective_sr_from_local_curve(
  NRDR_INSIGHT_VGR_INTEGRATION_ANGLE_BP,
  NRDR_INSIGHT_VGR_INTEGRATION_REL_LOCAL,
  1.0,
  output_bp=NRDR_INSIGHT_BASE_ANGLE_BP,
)
NRDR_INSIGHT_CENTER_SR = 15.0
NRDR_INSIGHT_VGR_ANGLE_BP, NRDR_INSIGHT_EFFECTIVE_SR_V = _endpoint_constrained_effective_sr_curve(
  NRDR_INSIGHT_BASE_ANGLE_BP,
  [NRDR_INSIGHT_CENTER_SR * multiplier for multiplier in NRDR_INSIGHT_BASE_REL_EFFECTIVE_SR],
  95.243,
  NRDR_INSIGHT_LOCK_ANGLE,
  NRDR_INSIGHT_FINAL_SR,
  500.0,
)
NRDR_INSIGHT_VGR_REL_EFFECTIVE_SR_V = [
  effective_sr / NRDR_INSIGHT_CENTER_SR
  for effective_sr in NRDR_INSIGHT_EFFECTIVE_SR_V
]
NRDR_INSIGHT_VGR_LINEAR_BP = _inverse_vgr_from_effective_sr_curve(
  NRDR_INSIGHT_VGR_ANGLE_BP,
  NRDR_INSIGHT_EFFECTIVE_SR_V,
)

# Brett's road testing found the original two-point measured-angle behavior
# uniquely effective on the Clarity. Use that simple profile as the first-pass
# baseline for the other modified-EPS Hondas too: each car has its own center
# anchor and Honda-published full-off-center ratio, while its second breakpoint
# is placed at the same fraction of physical lock as 250 deg is on the Clarity.
# These direct curves intentionally supersede the more elaborate inverse maps
# below for the explicitly listed fingerprints; the source maps remain here for
# reference and future validation.
NRDR_TWO_POINT_OUTER_FRACTION = 250.0 / NRDR_CLARITY_LOCK_ANGLE


def _equivalent_two_point_sr_bp(lock_angle: float) -> list[float]:
  return [0.0, lock_angle * NRDR_TWO_POINT_OUTER_FRACTION]


NRDR_CLARITY_TWO_POINT_SR_BP = [0.0, 250.0]
NRDR_CLARITY_TWO_POINT_SR_V = [18.50, 12.72]
NRDR_CIVIC_TWO_POINT_SR_BP = _equivalent_two_point_sr_bp(NRDR_CIVIC_LOCK_ANGLE)
NRDR_CIVIC_TWO_POINT_SR_V = [17.24, 10.93]
NRDR_ACCORD_TWO_POINT_SR_BP = _equivalent_two_point_sr_bp(NRDR_ACCORD_LOCK_ANGLE)
NRDR_ACCORD_TWO_POINT_SR_V = [18.31, 11.82]
NRDR_CRV_5G_TWO_POINT_SR_BP = _equivalent_two_point_sr_bp(NRDR_CRV_5G_LOCK_ANGLE)
NRDR_CRV_5G_TWO_POINT_SR_V = [17.94, 12.30]
NRDR_INSIGHT_TWO_POINT_SR_BP = _equivalent_two_point_sr_bp(NRDR_INSIGHT_LOCK_ANGLE)
NRDR_INSIGHT_TWO_POINT_SR_V = [16.82, 12.58]
NRDR_SR_CURVE_BY_FP = {
  "HONDA_CLARITY": (NRDR_CLARITY_TWO_POINT_SR_BP, NRDR_CLARITY_TWO_POINT_SR_V),
  "HONDA_CIVIC": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
  "HONDA_CIVIC_BOSCH": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
  "HONDA_CIVIC_BOSCH_DIESEL": (NRDR_CIVIC_TWO_POINT_SR_BP, NRDR_CIVIC_TWO_POINT_SR_V),
  "HONDA_ACCORD": (NRDR_ACCORD_TWO_POINT_SR_BP, NRDR_ACCORD_TWO_POINT_SR_V),
  "HONDA_CRV_5G": (NRDR_CRV_5G_TWO_POINT_SR_BP, NRDR_CRV_5G_TWO_POINT_SR_V),
  "HONDA_CRV_HYBRID": (NRDR_CRV_5G_TWO_POINT_SR_BP, NRDR_CRV_5G_TWO_POINT_SR_V),
  "HONDA_INSIGHT": (NRDR_INSIGHT_TWO_POINT_SR_BP, NRDR_INSIGHT_TWO_POINT_SR_V),
}

NRDR_CLARITY_VGR_LINEAR_BP = _inverse_vgr_from_effective_sr_curve(
  NRDR_CLARITY_SR_CURVE_BP,
  NRDR_CLARITY_SR_CURVE_V,
)
NRDR_CRV_5G_VGR_LINEAR_BP = _inverse_vgr_from_effective_sr_curve(
  NRDR_CRV_5G_SR_CURVE_BP,
  NRDR_CRV_5G_SR_CURVE_V,
)
NRDR_CIVIC_BOSCH_VGR_LINEAR_BP = _inverse_vgr_from_effective_sr_curve(
  NRDR_CIVIC_BOSCH_SR_CURVE_BP,
  NRDR_CIVIC_BOSCH_SR_CURVE_V,
)

# (constant-ratio/model angle breakpoints, real steering-wheel angle values,
# fixed effective center ratio used when steer-ratio learning is disabled)
NRDR_VGR_INVERSE_BY_FP = {
  "HONDA_CLARITY": (NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_SR_CURVE_BP, NRDR_CLARITY_CENTER_SR),
  "HONDA_CRV_5G": (NRDR_CRV_5G_VGR_LINEAR_BP, NRDR_CRV_5G_SR_CURVE_BP, NRDR_CRV_5G_CENTER_SR),
  "HONDA_CIVIC_BOSCH": (NRDR_CIVIC_BOSCH_VGR_LINEAR_BP, NRDR_CIVIC_BOSCH_SR_CURVE_BP,
                         NRDR_CIVIC_BOSCH_CENTER_SR),
  "HONDA_CIVIC": (NRDR_CIVIC_NIDEC_LINEAR_BP, NRDR_CIVIC_NIDEC_VGR_ANGLE_BP, NRDR_CIVIC_NIDEC_CENTER_SR),
  "HONDA_INSIGHT": (NRDR_INSIGHT_VGR_LINEAR_BP, NRDR_INSIGHT_VGR_ANGLE_BP, NRDR_INSIGHT_CENTER_SR),
}


CENTER_TAPER_FADE_TAU = 0.25

# Model-trajectory unwind lookahead: read the model's planned lateral-accel profile
# to anticipate the turn release before the instantaneous desired curvature drops.
UNWIND_LOOKAHEAD_MIN_IDX = 5            # skip samples inside the actuator delay window
UNWIND_LOOKAHEAD_SECONDS = 1.0         # how far ahead in the plan to look
UNWIND_LOOKAHEAD_MIN_LAT_ACCEL = 0.3   # m/s^2; ignore near-center noise


_MPH_TO_MS = 0.44704
_LAT_SCALE_LOW_MAX = 25.0 * _MPH_TO_MS    # below this -> low-speed scale
_LAT_SCALE_STD_MAX = 50.0 * _MPH_TO_MS    # below this -> standard scale, else highway

# Center boost speed gate: boost ramps in over this many mph above the min-speed floor,
# so it engages smoothly instead of stepping in the moment the car crosses the threshold.
CENTER_BOOST_SPEED_FADE_MS = 5.0 * _MPH_TO_MS

# A learned scalar is useful close to centre, where paramsd has observations.
# It must not rescale the entire physical rack: smoothly hand authority back to
# the fixed, road-tested/published-endpoint curve after the learner's +/-45 deg
# observation window. The two Clarity paths naturally converge by ~90-100 deg.
VGR_LEARNED_FULL_ANGLE_DEG = 45.0
VGR_FIXED_FULL_ANGLE_DEG = 100.0

# Unwind FF boost fades out over this many seconds approaching its time cap, so the boost
# doesn't drop as a torque step the instant the cap is reached.
UNWIND_BOOST_FADE_S = 0.3

# Rate-damping (D) reference gain: output torque per (deg/s) of steering-wheel rate at 100%
# strength. The wheel is torque-commanded, so the plant is a double integrator that pure P
# can't damp at low speed (tire self-aligning torque and the v^2 feedforward both vanish);
# this is the derivative term that flattens it. 0.010 -> 1.0 torque at 100 deg/s @ 100%.
RATE_DAMPING_REF = 0.010

# Derivative Tuning Experiment: during winddown the D term fights the pullback we want at high
# angle, but helps the wheel settle cleanly at center. So while unwinding, fade D out above this
# wheel angle (deg) and back in below it. Full D for normal driving and windup.
D_UNWIND_FADE_ANGLE = 30.0


def _lat_pid_scale_banded(v_ego: float, low: float, standard: float, highway: float) -> float:
  # Speed-banded lateral PID output scale. Hard bands mirror carcontroller.torque_lpf_tau
  # so the scale and tau bands line up at the same 25/50 mph boundaries.
  if v_ego < _LAT_SCALE_LOW_MAX:
    return low
  if v_ego < _LAT_SCALE_STD_MAX:
    return standard
  return highway


def _freeze_integrator_during_unwind(phase: float, integral: float, error: float) -> bool:
  """Block integral growth during unwind while always allowing stale I to decay toward zero."""
  return phase < 0.0 and integral * error > 0.0


def _sign(x: float) -> float:
  return 1.0 if x > 0.0 else (-1.0 if x < 0.0 else 0.0)


def _lookahead_release(future_vals, current_val) -> float:
  # If any future planned value flips sign vs. the current command, the plan shows a
  # release coming -> return 0.0. Otherwise return the smallest-magnitude same-sign value.
  if not future_vals:
    return current_val
  same_sign = [v for v in future_vals if _sign(v) == _sign(current_val)]
  if len(same_sign) < len(future_vals):
    return 0.0
  return min(same_sign + [current_val], key=lambda x: abs(x))


def get_param_bool(params, key, default=False):
  # A removed/unregistered key must never crash the card. Params.get() raises
  # UnknownKeyName on an unregistered key (it does NOT return None), so catch it.
  try:
    if params.get(key) is None:
      return default
    return params.get_bool(key)
  except UnknownKeyName:
    return default


def get_param_float(params, key, default, min_value=None, max_value=None, scale=1.0):
  try:
    value = params.get(key)
  except UnknownKeyName:
    value = None
  if value is None:
    ret = default
  else:
    try:
      # sunnypilot Params.get() auto-casts by declared key type, so an INT param
      # comes back as a python int (not bytes). Handle bytes/str/number uniformly.
      if isinstance(value, bytes):
        value = value.decode("utf-8")
      ret = float(value) / scale
    except (AttributeError, TypeError, ValueError):
      ret = default

  if min_value is not None:
    ret = max(min_value, ret)
  if max_value is not None:
    ret = min(max_value, ret)
  return ret


def _center_boost_scale(
  desired_angle_deg: float,
  v_ego: float,
  center_taper_scale: float = 1.0,
  center_taper_high: float = 2.0,
  center_boost_threshold_deg: float = 3.0,
  center_boost_min_speed_ms: float = 0.0,
) -> float:
  """Return the P-only near-center multiplier; the speed gate has no upper cutoff."""
  abs_angle = abs(desired_angle_deg)
  center_fade_deg = 1.0
  center_weight = min(max((center_boost_threshold_deg + center_fade_deg - abs_angle) / center_fade_deg, 0.0), 1.0)
  if center_boost_min_speed_ms > 0.0:
    center_speed_weight = min(max((v_ego - center_boost_min_speed_ms) / CENTER_BOOST_SPEED_FADE_MS, 0.0), 1.0)
  else:
    center_speed_weight = 1.0
  center_taper = center_taper_high * center_taper_scale * center_speed_weight
  return 1.0 + center_weight * center_taper


def _learned_vgr_weight(physical_angle_deg: float) -> float:
  """Learned-path authority: 1 through 45 deg, smoothstep to 0 at 100 deg."""
  fade = min(max((abs(physical_angle_deg) - VGR_LEARNED_FULL_ANGLE_DEG) /
                 (VGR_FIXED_FULL_ANGLE_DEG - VGR_LEARNED_FULL_ANGLE_DEG), 0.0), 1.0)
  smoothstep = fade * fade * (3.0 - 2.0 * fade)
  return 1.0 - smoothstep


def _hybrid_vgr_desired_angles(linear_des_no_offset: float, angle_offset_deg: float,
                               learned_center_sr: float, fixed_center_sr: float,
                               learned_inverse, fixed_inverse, offset_is_linear: bool) -> tuple[float, float]:
  """Blend a learned low-angle VGR request into a fixed outer-rack request.

  ``linear_des_no_offset`` was produced with ``learned_center_sr``. Rescaling it
  reconstructs the model angle the fixed centre anchor would have produced,
  while each inverse map supplies its corresponding physical steering angle.
  """
  safe_learned_sr = learned_center_sr if learned_center_sr > 0.1 else fixed_center_sr
  fixed_linear_no_offset = linear_des_no_offset * fixed_center_sr / safe_learned_sr

  learned_physical_no_offset = vgr_linear_to_physical(linear_des_no_offset, learned_inverse)
  fixed_physical_no_offset = vgr_linear_to_physical(fixed_linear_no_offset, fixed_inverse)
  learned_weight = _learned_vgr_weight(learned_physical_no_offset)

  physical_no_offset = (learned_weight * learned_physical_no_offset +
                        (1.0 - learned_weight) * fixed_physical_no_offset)
  if offset_is_linear:
    learned_physical = vgr_linear_to_physical(linear_des_no_offset + angle_offset_deg, learned_inverse)
    fixed_physical = vgr_linear_to_physical(fixed_linear_no_offset + angle_offset_deg, fixed_inverse)
    physical = learned_weight * learned_physical + (1.0 - learned_weight) * fixed_physical
  else:
    physical = physical_no_offset + angle_offset_deg
  return physical_no_offset, physical


def _pid_output_scale(
  desired_angle_deg: float,
  desired_angle_delta_deg: float,
  steering_rate_deg: float,
  v_ego: float,
  starpilot_enabled: bool = True,
) -> float:
  abs_angle = abs(desired_angle_deg)
  speed_weight = min(max((v_ego - 4.0) / 10.0, 0.0), 1.0)
  mid_turn_weight = min(max((abs_angle - 10.0) / 10.0, 0.0), 1.0)
  angle_weight = min(max((abs_angle - 16.0) / 12.0, 0.0), 1.0)
  phase = desired_angle_deg * desired_angle_delta_deg
  is_left = desired_angle_deg > 0.0

  # At very low speeds, steering angle changes more slowly during unwind,
  # which can delay phase detection and cause late steering release.
  low_speed_unwind_weight = min(max(1.0 - (v_ego / (15.0 * 0.44704)), 0.0), 1.0)
  steering_rate_unwind = desired_angle_deg * steering_rate_deg < -1.0
  low_speed_unwind = low_speed_unwind_weight > 0.0 and steering_rate_unwind

  mid_turn_scale = 0.1200 if is_left else 0.0150
  mid_turn_turn_in_scale = -0.5500 if is_left else -0.0524
  mid_turn_unwind_scale = -0.0743 if is_left else -0.0842
  base_scale = 0.0722 if is_left else 0.0972
  turn_in_scale = -0.0799 if is_left else 0.0888
  unwind_scale = 0.1600 if is_left else 0.2000

  scale = 1.0

  if not starpilot_enabled:
    # The borrowed StarPilot turn-in/unwind/per-direction scaling is gated off.
    return scale

  scale += speed_weight * mid_turn_weight * mid_turn_scale
  scale += speed_weight * angle_weight * base_scale

  # Blend smoothly between turn-in and unwind modifiers instead of hard branches.
  # Binary if/elif caused a step change in scale the moment phase crossed +-0.2,
  # which felt like an abrupt torque drop at the start of unwind.
  # Ramp from 0 at phase=0 to full modifier at |phase|=0.5.
  turn_in_weight = min(max(phase / 0.5, 0.0), 1.0)
  unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)

  if low_speed_unwind and speed_weight < 0.1:
    # Low-speed unwind: EPS won't self-center, actively boost output
    scale += low_speed_unwind_weight * mid_turn_weight * 0.18
  else:
    scale += speed_weight * mid_turn_weight * (turn_in_weight * mid_turn_turn_in_scale + unwind_weight * mid_turn_unwind_scale)
    scale += speed_weight * angle_weight * (turn_in_weight * turn_in_scale - unwind_weight * unwind_scale)

  return max(scale, 0.6863)


class LatControlPID(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    self.pid = PIDController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                             (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                             pos_limit=self.steer_max, neg_limit=-self.steer_max)

    self.ff_factor = CP.lateralTuning.pid.kf
    # Speed-banded feedforward (kfBP/kfV): interpolate kf by speed like kp/ki when present, else
    # fall back to the scalar kf above. getattr stays safe against a stale capnp without the fields.
    self.kf_bp = list(getattr(CP.lateralTuning.pid, "kfBP", []) or [])
    self.kf_v = list(getattr(CP.lateralTuning.pid, "kfV", []) or [])
    self.CI = CI
    self.get_steer_feedforward = CI.get_steer_feedforward_function()

    self.is_eps_modified = bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value)
    # Live-tunable center boost (replaces the old per-car lookup). Static across
    # all speeds; active only within the Center Boost Threshold of dead-center.
    self.center_taper_high = 0.5
    self.center_boost_threshold = 3.0
    self.center_boost_min_speed = 50.0  # mph; below this (with a short ramp) center boost is gated off
    # Unwind FF boost: peak multiplier (strongest at a standstill) + a real time cap that
    # holds the boost only for the first N seconds of each unwind, then fades it out.
    self.dt = dt
    self.unwind_ff_multiplier = 2.0
    self.unwind_boost_cap_s = 1.0
    self.unwind_boost_elapsed = 0.0
    # Rate damping (the missing "D"): live-tunable strength (0 = off) and the speed at which
    # it fades out (above which tire self-aligning torque damps the steering on its own).
    self.rate_damping_scale = 0.3
    self.rate_damping_fade_speed_ms = 30.0 * _MPH_TO_MS

    self.eps_modified_steering_pressed_filter_s = 0.0
    self.eps_modified_steering_pressed_prev = False
    self.center_taper_scale = FirstOrderFilter(1.0, CENTER_TAPER_FADE_TAU, dt)
    self.prev_output_torque = 0.0
    self.prev_angle_steers_des_no_offset = 0.0
    self.params = Params()
    # 2D online lateral auto-tuner: bounded, gated, per-(speed, angle) learned FF trim. Off by default.
    self.tune_learner = TuneLearner(dt, self.steer_max)
    # Optional per-fingerprint VGR transformations. There is deliberately no
    # global fallback: applying one rack's shape to another PID car is unsafe.
    self.sr_curve = NRDR_SR_CURVE_BY_FP.get(str(CP.carFingerprint))
    # A direct measured-angle curve and a desired-angle inverse are mutually
    # exclusive. The road-test two-point family deliberately uses the former;
    # applying both would double-correct a variable rack.
    self.vgr_profile = None if self.sr_curve is not None else NRDR_VGR_INVERSE_BY_FP.get(str(CP.carFingerprint))
    if self.vgr_profile is None:
      self.vgr_inverse = None
      self.vgr_center_sr = None
    else:
      linear_bp, real_angle_v, self.vgr_center_sr = self.vgr_profile
      self.vgr_inverse = (linear_bp, real_angle_v)
    # vote_for_nobody's exact EPS position table is the preferred low-angle
    # shape when the firmware is known. Unknown images retain our existing
    # fingerprint-scoped inverse, so this remains a safe behavioral fallback.
    self.firmware_vgr_inverse = get_honda_vgr_inverse(CP.flags) if CP.brand == "honda" and self.sr_curve is None else None
    self.learned_vgr_inverse = self.firmware_vgr_inverse or self.vgr_inverse
    # paramsd dewarps only the road-validated Clarity profile. This also tells
    # us whether its learned angle offset belongs before or after the VGR map.
    self.vgr_offset_is_linear = get_honda_vgr_learning_inverse(CP.flags) is not None if CP.brand == "honda" and self.sr_curve is None else False
    self.sr_offset = 0.0
    self.learn_steer_ratio = False
    self.frame = -1
    # Independent speed-banded P / I / F output scales (multiplier units; 1.0 = neutral).
    self.lat_p_scale_low = 1.0
    self.lat_p_scale_standard = 1.0
    self.lat_p_scale_highway = 1.0
    self.lat_i_scale_low = 1.0
    self.lat_i_scale_standard = 1.0
    self.lat_i_scale_highway = 1.0
    self.lat_f_scale_low = 1.0
    self.lat_f_scale_standard = 1.0
    self.lat_f_scale_highway = 1.0
    self.unwind_lookahead_enabled = False
    self.starpilot_enabled = False  # borrowed _pid_output_scale; off by default (param NrdrStarPilotPid)
    self.injection_test_enabled = False  # Party Tricks: x9.99 PID scale stress test
    self.lat_stiction = LatStiction(dt, self.steer_max)
    self.lat_stiction_enabled = False
    self.prev_saturated = False
    self.model_v2 = None
    self.model_valid = False

  def update_model_v2(self, model_v2):
    self.model_v2 = model_v2
    self.model_valid = model_v2 is not None and len(model_v2.acceleration.y) >= CONTROL_N

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)

    # nrdr: measured SR(|angle|) curve (+ live offset), keyed on measured wheel
    # angle to avoid a desired-angle circular dependency. Only the explicitly
    # mapped cars override VehicleModel; all other cars retain normal behavior.
    if self.sr_curve is not None:
      VM.sr_curve = None
      # Restore the original two-point behavior: measured wheel angle selects
      # the effective SR before curvature->angle conversion. These handcrafted
      # profiles are authoritative regardless of the global learner toggle.
      bp, values = self.sr_curve
      VM.sR = float(np.interp(abs(CS.steeringAngleDeg), bp, values)) + self.sr_offset
    elif self.vgr_inverse is not None and not self.learn_steer_ratio:
      # Use the profile's road-validated effective center anchor. The inverse
      # then removes that artificial/model compensation toward physical lock.
      # With learning enabled, controlsd's paramsd scalar remains the anchor.
      VM.sR = self.vgr_center_sr + self.sr_offset

    linear_des_no_offset = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))
    if self.vgr_inverse is not None and self.learn_steer_ratio:
      # paramsd only observes the centre region. Use its scalar and the traced
      # firmware shape there, fade from 45-100 deg, then pin the request to the
      # existing road-tested curve and published full-off-centre endpoint.
      angle_steers_des_no_offset, angle_steers_des = _hybrid_vgr_desired_angles(
        linear_des_no_offset,
        params.angleOffsetDeg,
        VM.sR,
        self.vgr_center_sr,
        self.learned_vgr_inverse,
        self.vgr_inverse,
        self.vgr_offset_is_linear,
      )
    elif self.vgr_inverse is not None:
      angle_steers_des_no_offset = vgr_linear_to_physical(linear_des_no_offset, self.vgr_inverse)
      if self.vgr_offset_is_linear:
        angle_steers_des = vgr_linear_to_physical(linear_des_no_offset + params.angleOffsetDeg, self.vgr_inverse)
      else:
        angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg
    else:
      angle_steers_des_no_offset = linear_des_no_offset
      angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg
    error = angle_steers_des - CS.steeringAngleDeg

    pid_log.steeringAngleDesiredDeg = angle_steers_des
    pid_log.angleError = error

    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.eps_modified_steering_pressed_filter_s = 0.0
      self.eps_modified_steering_pressed_prev = False
      self.center_taper_scale.x = 1.0
      self.prev_output_torque = 0.0
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset
      self.unwind_boost_elapsed = 0.0
      self.prev_saturated = False
      self.lat_stiction.reset()
    else:
      desired_angle_delta = angle_steers_des_no_offset - self.prev_angle_steers_des_no_offset
      phase = angle_steers_des_no_offset * desired_angle_delta

      # Offset does not contribute to resistive torque. Speed-banded kf (kfBP/kfV) when present,
      # else the scalar kf.
      ff_factor = float(np.interp(CS.vEgo, self.kf_bp, self.kf_v)) if self.kf_v else self.ff_factor
      ff = ff_factor * self.get_steer_feedforward(angle_steers_des_no_offset, CS.vEgo)
      ff_scale = 1.0

      # Low-speed unwind needs extra feedforward to overcome EPS/tire stiction. The peak
      # multiplier is live-tunable and fades to 1x (no boost) by ~22 mph; a separate time
      # cap (applied below) limits how long the boost is held into each unwind.
      unwind_ff_boost = float(np.interp(CS.vEgo, [0.0, 10.0], [self.unwind_ff_multiplier, 1.0]))

      # Smooth FF blend: ramp from ff_scale at phase=0 to unwind_ff_boost at phase=-0.5.
      abs_angle_des = abs(angle_steers_des_no_offset)
      steering_rate_unwind_ff = (angle_steers_des_no_offset * float(CS.steeringRateDeg)) < -1.0

      ff_unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)
      # Stable floor: if steering rate confirms wheel is still returning and angle is
      # meaningful, hold at least half the boost so we don't drop prematurely.
      if steering_rate_unwind_ff and abs_angle_des > 5.0:
        ff_unwind_weight = max(ff_unwind_weight, 0.5)

      # Forward-looking unwind: read the model's planned lateral-accel profile to see if
      # the turn is about to release, and ramp the unwind weight early. predicted_unwind_*
      # stay zero/False unless the lookahead toggle is on AND the model frame is valid,
      # so default behavior falls back to the backward-difference phase logic above.
      predicted_unwind_weight = 0.0
      if self.unwind_lookahead_enabled and self.model_valid:
        lat_accels = list(self.model_v2.acceleration.y)
        if len(lat_accels) > UNWIND_LOOKAHEAD_MIN_IDX:
          current_la = float(lat_accels[0])
          upper_idx = next((i for i, t in enumerate(ModelConstants.T_IDXS) if t > UNWIND_LOOKAHEAD_SECONDS), len(lat_accels))
          future = [float(v) for v in lat_accels[UNWIND_LOOKAHEAD_MIN_IDX:upper_idx]]
          lookahead_la = _lookahead_release(future, current_la)
          if abs(current_la) > UNWIND_LOOKAHEAD_MIN_LAT_ACCEL:
            predicted_unwind_weight = min(max(1.0 - abs(lookahead_la) / abs(current_la), 0.0), 1.0)

      ff_unwind_weight = max(ff_unwind_weight, predicted_unwind_weight)

      # Time cap: hold the boost only for the first unwind_boost_cap_s of each unwind event.
      # Accumulate elapsed while the (pre-cap) unwind weight is active and reset when the
      # unwind ends, so the timer tracks the real event; fade out over UNWIND_BOOST_FADE_S
      # approaching the cap so the boost doesn't drop as a torque step. cap == 0 -> no boost.
      if ff_unwind_weight > 0.0:
        self.unwind_boost_elapsed += self.dt
      else:
        self.unwind_boost_elapsed = 0.0
      if self.unwind_boost_cap_s > 0.0:
        fade = min(UNWIND_BOOST_FADE_S, self.unwind_boost_cap_s)
        time_gate = min(max((self.unwind_boost_cap_s - self.unwind_boost_elapsed) / fade, 0.0), 1.0)
      else:
        time_gate = 0.0
      ff_unwind_weight *= time_gate

      ff_multiplier = ff_scale + ff_unwind_weight * max(unwind_ff_boost - ff_scale, 0.0)
      ff *= ff_multiplier

      steering_pressed = CS.steeringPressed
      if self.is_eps_modified:
        self.eps_modified_steering_pressed_filter_s, steering_pressed = get_eps_modified_steering_pressed(
          bool(CS.steeringPressed),
          float(getattr(CS, "steeringTorque", 0.0)),
          float(self.prev_output_torque),
          self.eps_modified_steering_pressed_filter_s,
          self.eps_modified_steering_pressed_prev,
        )
        self.eps_modified_steering_pressed_prev = steering_pressed

      freeze_threshold = 2.0 if self.is_eps_modified else 5.0
      freeze_integrator = steer_limited_by_safety or steering_pressed or CS.vEgo < freeze_threshold

      # During unwind, block only integration that would grow the existing I magnitude.
      # Opposite-sign error is always allowed to drain stale I toward zero; this avoids
      # carrying a previous turn's torque into the next small correction.
      if _freeze_integrator_during_unwind(phase, self.pid.i, error):
        freeze_integrator = True

      self.frame += 1
      if self.frame % 300 == 0:
        # Independent speed-banded P / I / F scales. default/min/max are runtime
        # multipliers; scale converts the stored percent (100 -> 1.0x). Band selection
        # by vEgo happens every frame below. Defaults are a neutral 100% across the board --
        # the per-car tune lives in interface.py and these act as fine-trim on top.
        self.lat_p_scale_low = get_param_float(self.params, "LatPScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_p_scale_standard = get_param_float(self.params, "LatPScaleStandard", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_p_scale_highway = get_param_float(self.params, "LatPScaleHighway", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_low = get_param_float(self.params, "LatIScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_standard = get_param_float(self.params, "LatIScaleStandard", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_i_scale_highway = get_param_float(self.params, "LatIScaleHighway", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_low = get_param_float(self.params, "LatFScaleLowSpeed", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_standard = get_param_float(self.params, "LatFScaleStandard", 1.0, 0.0, 5.0, scale=100.0)
        self.lat_f_scale_highway = get_param_float(self.params, "LatFScaleHighway", 1.0, 0.0, 5.0, scale=100.0)
        # Center boost target. FLOAT param stored as the real value
        # (UI use_float_scaling), so no scale. Unset -> 0.5 (old generic default).
        self.center_taper_high = get_param_float(
          self.params,
          "HondaCenterScale",
          0.5,
          0.0,
          5.0,
        )
        # Degrees from dead-center within which the center boost is active.
        self.center_boost_threshold = get_param_float(
          self.params,
          "HondaCenterBoostThreshold",
          3.0,
          0.0,
          10.0,
        )
        # mph floor below which center boost is disabled (low-speed center-oscillation fix).
        self.center_boost_min_speed = get_param_float(
          self.params,
          "HondaCenterBoostMinSpeed",
          50.0,
          0.0,
          90.0,
        )
        self.unwind_lookahead_enabled = get_param_bool(self.params, "HondaUnwindLookahead")
        # Unwind FF boost: peak multiplier + time cap (both FLOAT, stored as real values).
        self.unwind_ff_multiplier = get_param_float(self.params, "HondaUnwindFfMultiplier", 2.0, 1.0, 10.0)
        self.unwind_boost_cap_s = get_param_float(self.params, "HondaUnwindBoostSeconds", 1.0, 0.0, 3.0)
        # Rate damping (D): strength (stored 0-300% -> 0.0-3.0) and fade-out speed (mph).
        self.rate_damping_scale = get_param_float(self.params, "NrdrLatRateDamping", 0.3, 0.0, 3.0, scale=100.0)
        self.rate_damping_fade_speed_ms = get_param_float(self.params, "NrdrLatRateDampingFadeSpeed", 30.0, 0.0, 60.0) * _MPH_TO_MS
        self.injection_test_enabled = get_param_bool(self.params, "HondaInjectionTest")
        self.starpilot_enabled = get_param_bool(self.params, "NrdrStarPilotPid")
        self.lat_stiction_enabled = get_param_bool(self.params, "NrdrLatStiction")
        self.sr_offset = get_param_float(self.params, "NrdrSteerRatioOffset", 0.0, -5.0, 5.0)
        self.learn_steer_ratio = get_param_bool(self.params, "NrdrLearnSteerRatio")

      output_torque = self.pid.update(
        error,
        feedforward=ff,
        speed=CS.vEgo,
        freeze_integrator=freeze_integrator,
      )

      # Independently scale each PID term by its own speed-banded multiplier (P / I / F).
      # Defaults are a neutral 100% (the per-car tune lives in interface.py); these act as trim.
      p_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_p_scale_low, self.lat_p_scale_standard, self.lat_p_scale_highway)
      i_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_i_scale_low, self.lat_i_scale_standard, self.lat_i_scale_highway)
      f_scale = _lat_pid_scale_banded(CS.vEgo, self.lat_f_scale_low, self.lat_f_scale_standard, self.lat_f_scale_highway)
      p_term = self.pid.p * p_scale
      i_term = self.pid.i * i_scale
      d_term = self.pid.d
      f_term = self.pid.f * f_scale

      if self.is_eps_modified:
        lane_change = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))

        if lane_change:
          self.center_taper_scale.x = 0.0
          center_taper_scale = 0.0
        else:
          center_taper_scale = float(self.center_taper_scale.update(1.0))

        # Center boost is deliberately P-only. I must remain free to unwind, and F
        # already represents the planned angle; multiplying either reproduced the
        # road-test failure where stale I/F committed harder to a bad placement.
        p_term *= _center_boost_scale(
          angle_steers_des_no_offset,
          CS.vEgo,
          center_taper_scale,
          self.center_taper_high,
          self.center_boost_threshold,
          self.center_boost_min_speed * _MPH_TO_MS,
        )

      output_torque = p_term + i_term + d_term + f_term

      # Party Tricks: Injection Test multiplies the PID scale by 999% (diagnostic only).
      if self.injection_test_enabled:
        output_torque *= 9.99

      if self.is_eps_modified:
        # Optional borrowed StarPilot turn-in/unwind/per-direction scaling remains
        # a separate whole-output experiment and is off by default.
        output_torque *= _pid_output_scale(
          angle_steers_des_no_offset,
          desired_angle_delta,
          float(CS.steeringRateDeg),
          CS.vEgo,
          self.starpilot_enabled,
        )

        # Rate damping (the missing "D"): torque opposing how fast the wheel is moving, applied
        # after the output scale so it's a clean physical term. Strongest at low speed (where the
        # plant is an undamped double integrator) and faded to zero by rate_damping_fade_speed,
        # where tire self-aligning torque resumes damping. Relies on this EPS being precise + low-lag.
        rate_damp_fade = 0.0
        if self.rate_damping_fade_speed_ms > 0.0:
          rate_damp_fade = min(max((self.rate_damping_fade_speed_ms - CS.vEgo) / self.rate_damping_fade_speed_ms, 0.0), 1.0)
        # Unwind/angle scheduling: during winddown, D resists the pullback we want at high angle
        # but helps the wheel settle at center, so fade D out above D_UNWIND_FADE_ANGLE and in
        # below it. Blend by the unwind phase weight so D doesn't step when phase crosses zero;
        # full D for normal driving and windup.
        unwind_weight = min(max(-phase / 0.5, 0.0), 1.0)
        d_angle_fade = min(max((D_UNWIND_FADE_ANGLE - abs(CS.steeringAngleDeg)) / D_UNWIND_FADE_ANGLE, 0.0), 1.0)
        d_unwind_factor = (1.0 - unwind_weight) + unwind_weight * d_angle_fade
        output_torque += -self.rate_damping_scale * RATE_DAMPING_REF * float(CS.steeringRateDeg) * rate_damp_fade * d_unwind_factor

        # 2D learned tune trim (error-gated): the learned per-(speed, angle) surface is only a
        # ceiling - torque is applied in proportion to the PRESENT tracking error and only when it
        # agrees with the learned direction, i.e. scheduled proportional help rather than blind
        # feedforward. Added in front of the steer_max clamp. No-op unless NrdrTuneLearner.
        output_torque += self.tune_learner.apply(CS.vEgo, angle_steers_des, error)

        output_torque = float(max(min(output_torque, self.steer_max), -self.steer_max))

        # Online learning step for the trim map: this frame's steady-state error, gated inside the learner
        # to clean hands-off quasi-steady driving. Updates the learned map only -- never the torque above.
        # paramsd_ok = the kinematic estimator vouches for its own estimate (valid + per-field valid flags),
        # so the trim learner stays in its lane and never chases steer-ratio/offset/stiffness mid-adaptation.
        paramsd_ok = bool(params.valid and params.angleOffsetValid and params.steerRatioValid and params.stiffnessFactorValid)
        self.tune_learner.learn(CS.vEgo, angle_steers_des, error, float(CS.steeringRateDeg), steering_pressed, paramsd_ok, self.frame)

      # nrdr stiction output stage:
      if self.lat_stiction_enabled:
        des_rate_degs = desired_angle_delta / self.dt
        lane_change_mh = bool(getattr(CS, "leftBlinker", False) or getattr(CS, "rightBlinker", False))
        output_torque = float(self.lat_stiction.update(
          active, CS.vEgo, error, des_rate_degs, float(CS.steeringRateDeg), output_torque,
          steering_pressed, lane_change_mh, self.prev_saturated))
      else:
        self.lat_stiction.reset()

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(output_torque)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output_torque) < 1e-3,
        CS,
        steer_limited_by_safety,
        curvature_limited,
      ))

      self.prev_output_torque = float(output_torque)
      self.prev_angle_steers_des_no_offset = angle_steers_des_no_offset
      self.prev_saturated = bool(pid_log.saturated)

    return output_torque, angle_steers_des, pid_log
