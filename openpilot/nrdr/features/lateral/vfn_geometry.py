"""VFN f837ca86 Clarity A020 discretized position map, kept exact for its EPS controller."""
import math

def _build_vgr_position_inverse(raw_x, raw_y, raw_units_per_degree=10.0, max_raw_step=20):
  """Reproduce the firmware's primary angle conversion as an inverse map.

  The primary path linearly interpolates a Q14 divisor from ``abs(raw)`` and
  publishes ``raw * 2**14 / divisor``.  VehicleModel's learned center steer
  ratio already includes the divisor at zero, so ``linear_bp`` expresses the
  same raw angle using that center divisor while ``angle_bp`` is the angle the
  EPS actually publishes.

  Subdividing the firmware intervals preserves its interpolate-then-divide
  behavior; connecting only the transformed firmware knots would introduce a
  chord approximation through the curved transition.
  """
  linear_bp = []
  angle_bp = []
  relative_ratio = []
  center_divisor = raw_y[0]

  for raw0, raw1, divisor0, divisor1 in zip(raw_x, raw_x[1:], raw_y, raw_y[1:], strict=False):
    steps = max(1, math.ceil((raw1 - raw0) / max_raw_step))
    for step in range(steps):
      fraction = step / steps
      raw = raw0 + (raw1 - raw0) * fraction
      divisor = divisor0 + (divisor1 - divisor0) * fraction
      linear_bp.append(raw * (1 << 14) / center_divisor / raw_units_per_degree)
      angle_bp.append(raw * (1 << 14) / divisor / raw_units_per_degree)
      relative_ratio.append(center_divisor / divisor)

  raw = raw_x[-1]
  divisor = raw_y[-1]
  linear_bp.append(raw * (1 << 14) / center_divisor / raw_units_per_degree)
  angle_bp.append(raw * (1 << 14) / divisor / raw_units_per_degree)
  relative_ratio.append(center_divisor / divisor)
  return linear_bp, angle_bp, relative_ratio


_CLARITY_POSITION_X = [0, 40, 80, 119, 158, 198, 237, 277, 317, 398,
                       604, 820, 1047, 1164, 1210, 1257, 1305, 1352, 1398, 1447,
                       1493, 1540, 1588, 1634, 1989, 2344, 2700, 3056, 3413, 5020]
_CLARITY_POSITION_Y = [16384, 16174, 16173, 16247, 16179, 16220, 16180, 16209, 16231, 16303,
                       16506, 16812, 17177, 17352, 17411, 17473, 17538, 17600, 17644, 17705,
                       17749, 17792, 17843, 17885, 18130, 18303, 18439, 18547, 18645, 18952]


NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_VGR_ANGLE_BP, _RELATIVE_RATIO = _build_vgr_position_inverse(
  _CLARITY_POSITION_X, _CLARITY_POSITION_Y)
