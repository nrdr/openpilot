"""Honda VSA yaw rate (0x94 KINEMATICS YAW_RATE) with each car's zero learned at standstill.

The DBC decodes against the nominal zero, 512 counts, but every unit sits a few counts off it (2018 Clarity 508,
2019 Civic Bosch 513) and holds that offset exactly at every stop. With the wheels stopped the true yaw rate is
zero, so the average reading there is the zero. The scale is not learnable that way and is measured per model
against GPS heading, using only stretches that start and end driving straight (there the ~0.4 s lag of the 1 Hz
GPS bearing and the car's sideslip cancel; fits over arbitrary windows are biased by both).

The Clarity's sensor also under-reads clockwise (right) turns by ~0.24 deg/s from about 1 deg/s up, while left
turns and small rates read true (mechanism unknown). Measured on GPS windows where the yaw rate is steady at
both ends: straights +0.007 +/- 0.004, right 0.75-1.5 deg/s +0.17..0.18, right 1.5-2.5 deg/s +0.21..0.23
(at 0.25/count; ~0.02 more at 0.246), left 0.75-2.5 deg/s +0.03..0.06, which the scale below accounts for.
It ramps in across +3..+5 counts.

Clarity scale 0.246 (not 0.25): 12 whole turns, straight before and after, 0.2456-0.2470; 1670 straight-to-
straight GPS pairs on 9 routes, 0.2468 +/- 0.0008 with the clockwise correction (every route 0.244-0.250). Left
and right turns agree only with the correction (without it, 0.2514 right vs 0.2447 left). On those pairs the
heading error falls from 1.81 deg rms (0.25, no correction) to ~0.9 deg.
"""
# Adapted from JamesL787/openpilot f837ca86a639b1c20a0ce23bb8acf0ebbc6a05d4.
# NRDR deliberately enables only the Clarity calibration in this release.
from opendbc.car.honda.values import CAR

DBC_SCALE = 0.25   # deg/s per count, as the DBC decodes it
DBC_ZERO = 512.0   # counts

# (deg/s per count, standstill zero in counts until this drive's own standstill replaces it, clockwise
# under-read in deg/s)
YAW_RATE_CALIBRATION = {
  CAR.HONDA_CLARITY: (0.246, 508.0, 0.24),      # see above; 508.00 at every stop on 19 routes
}
RIGHT_LOSS_BP = (3.0, 5.0)  # counts from zero over which the clockwise under-read comes in

SETTLE_FRAMES = 50    # 0.5 s after the wheels stop before readings count
LEARN_FRAMES = 200    # 2 s of standstill readings before the zero is replaced
MAX_ZERO_OFFSET = 8.0  # counts (2 deg/s) from nominal; anything further is a fault, not a zero


def yaw_rate_deg_s(counts_from_zero: float, scale: float, right_loss: float = 0.0) -> float:
  """Yaw rate in deg/s, clockwise-positive, from counts relative to the zero."""
  lo, hi = RIGHT_LOSS_BP
  return counts_from_zero * scale + right_loss * min(max((counts_from_zero - lo) / (hi - lo), 0.0), 1.0)


class YawRateCalibration:
  def __init__(self, scale: float, zero: float, right_loss: float = 0.0):
    self.scale = scale
    self.zero = zero
    self.right_loss = right_loss
    self.stopped_frames = 0
    self.total = 0.0
    self.samples = 0

  def update(self, dbc_yaw_rate_deg_s: float, standstill: bool) -> float:
    """Returns the yaw rate in deg/s, clockwise-positive like the DBC signal."""
    counts = DBC_ZERO + dbc_yaw_rate_deg_s / DBC_SCALE
    if standstill:
      self.stopped_frames += 1
      if self.stopped_frames > SETTLE_FRAMES:
        self.total += counts
        self.samples += 1
        zero = self.total / self.samples
        if self.samples >= LEARN_FRAMES and abs(zero - DBC_ZERO) <= MAX_ZERO_OFFSET:
          self.zero = zero
    else:
      self.stopped_frames, self.total, self.samples = 0, 0.0, 0
    return yaw_rate_deg_s(counts - self.zero, self.scale, self.right_loss)


def get_yaw_rate_calibration(car_fingerprint) -> YawRateCalibration | None:
  calibration = YAW_RATE_CALIBRATION.get(car_fingerprint)
  return YawRateCalibration(*calibration) if calibration is not None else None
