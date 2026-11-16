"""Honda Clarity (TRW A020 EPS) wheel angle <-> curvature map. Only numpy here, so offline tools can use it."""
import math

import numpy as np

# Wheel angle <-> curvature, identified against the car's own yaw sensor (0x94, GPS-verified) on routes 341-36b.
# VehicleModel's form is kept, lin = R * L * [k (1 - sf v^2) - g sf roll], with lin the firmware-VGR linear
# angle of the physical wheel angle. But its single ratio (paramsd's, one value for every wheel angle)
# and its slip factor (-0.00061 from the tyre stiffness defaults) are replaced by what the car does:
# - The effective ratio R still falls with angle after the firmware table, 17.3 near centre to 16.0 at 400 deg.
#   The rack is quicker off centre than the A table says.
# - The slip factor is -0.0005: fitted from how R changes with speed within one wheel-angle band, so R's angle
#   shape can't leak into it. Left turns alone give -0.00052, right turns -0.00045.
# Each value is the mean of the left and right medians, so an angle offset cancels. Fitted on the corrected yaw
# decode (opendbc honda/yaw_rate.py). The first fit used 0.25 deg/s per count and no clockwise correction, which
# made right turns read 19.6 near centre against 16.5 for lefts and put the centre 4-5% high. Fitted on routes
# 341-35d alone the table is within 0.04 of this one, and on held-out routes 363-36b it predicts the car's
# curvature within ~1% below 16 m/s (the first fit was 1-5% short at 9-16 m/s) and 1-5% above.
# The paramsd ratio with VM's slip factor over-predicted the angle needed by 3-6% in the city, the over-steer
# through tight turns.
CLARITY_RATIO_BP = [6.5, 15.0, 32.0, 57.0, 85.0, 125.0, 175.0, 230.0, 305.0, 400.0]  # physical wheel angle, deg
CLARITY_RATIO_V = [17.34, 17.08, 16.94, 16.78, 16.78, 16.65, 16.48, 16.37, 16.29, 16.02]
CLARITY_SLIP_FACTOR = -0.0005  # 1 / (m/s)^2
GRAVITY = 9.81


class ClarityRackMap:
  """Physical wheel angle (deg, left-positive) <-> curvature (1/m, openpilot's right-positive), see CLARITY_RATIO_*."""
  def __init__(self, wheelbase: float, vgr_inverse):
    linear_bp, angle_bp = (np.asarray(x, dtype=float) for x in vgr_inverse)
    self.wheelbase = float(wheelbase)
    self.angle_grid = np.unique(np.r_[angle_bp, np.linspace(0.0, angle_bp[-1], 1001)])
    linear = np.radians(np.interp(self.angle_grid, angle_bp, linear_bp))
    self.path_grid = linear / np.interp(self.angle_grid, CLARITY_RATIO_BP, CLARITY_RATIO_V)  # = L * k at zero roll/slip
    assert np.all(np.diff(self.path_grid) > 0), "rack map must be monotonic to invert"

  def angle_from_curvature(self, curvature: float, v_ego: float, roll: float) -> float:
    k = -curvature
    path = self.wheelbase * (k * (1.0 - CLARITY_SLIP_FACTOR * v_ego ** 2) - GRAVITY * CLARITY_SLIP_FACTOR * roll)
    return math.copysign(float(np.interp(abs(path), self.path_grid, self.angle_grid)), path)

  def curvature_from_angle(self, angle_deg: float, v_ego: float, roll: float) -> float:
    path = math.copysign(float(np.interp(abs(angle_deg), self.angle_grid, self.path_grid)), angle_deg)
    k = (path / self.wheelbase + GRAVITY * CLARITY_SLIP_FACTOR * roll) / (1.0 - CLARITY_SLIP_FACTOR * v_ego ** 2)
    return -k
