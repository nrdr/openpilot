#!/usr/bin/env python3
"""
steerratio_by_angle.py - measure the REAL (variable) steer ratio vs steering angle.

openpilot models steerRatio as a single scalar; a variable-ratio rack (Clarity) isn't
one number. This bins hands-off, lat-active frames by |steering-wheel angle| and computes
the effective ratio at each, using an INDEPENDENT measure of how much the car actually
turned (IMU yaw rate from livePose) - NOT the steering angle itself, so it exposes the
true rack:

    curvature_achieved = yawRate / vEgo                  # 1/m   (independent of steering)
    road_wheel_angle   = atan(wheelbase * curvature)     # rad
    steerRatio_eff     = radians(steeringAngleDeg) / road_wheel_angle

The taper of steerRatio_eff vs angle is exactly the curve openpilot's single scalar misses.
Feed it a route with real cornering (your switchback) - highway frames are all near-center
and won't populate the large-angle bins.

Gate: lat active, hands off (not steeringPressed), moving, hold-still, and actually turning.

For writing device CurveData / exporting NRDR_STEER_RATIO_CURVES seeds, prefer:
  python3 sr_curve_fit.py fit <rlogs> [--apply] [--export --fingerprint HONDA_CRV_5G]

Usage:
  python3 steerratio_by_angle.py /data/media/0/realdata/<switchback-route>--*/rlog.zst
Read-only. Touches nothing on the device.
"""
import sys
import math
from collections import defaultdict

from openpilot.tools.lib.logreader import LogReader

ANGLE_BIN = 25.0      # deg per bin
MIN_ANGLE = 5.0       # deg: ratio is pure noise below this
MIN_YAW = 0.03        # rad/s: ignore near-straight
MIN_V = 7.0 * 0.44704 # ~7 mph (author protocol; yaw/v blows up at crawl)
RATE_GATE = 20.0      # deg/s: hold still
MIN_N = 15            # frames a bin needs before it's trusted


def main(paths):
  wheelbase = None
  v = a = yaw = rate = 0.0
  pressed = True
  lat = False
  bins = defaultdict(list)

  for p in paths:
    try:
      lr = LogReader(p)
    except Exception as e:
      print(f"!! could not open {p}: {e}", file=sys.stderr)
      continue
    for m in lr:
      w = m.which()
      if w == 'carParams':
        if wheelbase is None:
          wheelbase = m.carParams.wheelbase
      elif w == 'carState':
        v = m.carState.vEgo
        a = m.carState.steeringAngleDeg
        rate = m.carState.steeringRateDeg
        pressed = m.carState.steeringPressed
      elif w == 'carControl':
        lat = m.carControl.latActive
      elif w == 'livePose':
        yaw = m.livePose.angularVelocityDevice.z
        if (wheelbase and lat and not pressed and v > MIN_V and abs(rate) <= RATE_GATE
            and abs(yaw) > MIN_YAW and abs(a) > MIN_ANGLE):
          curv = yaw / v
          rw = math.atan(wheelbase * curv)
          if abs(rw) > 1e-4:
            sr = abs(math.radians(a) / rw)
            if 5.0 < sr < 40.0:  # sanity clamp, drops garbage frames
              b = int(abs(a) // ANGLE_BIN) * int(ANGLE_BIN)
              bins[b].append(sr)

  if not bins:
    print("no usable turning frames - point it at a route with real cornering (your switchback)")
    return

  print(f"wheelbase = {wheelbase:.3f} m\n")
  print(f"{'|angle| bin':>13} {'n':>7} {'steerRatio':>11} {'std':>6}")
  for b in sorted(bins):
    xs = bins[b]
    if len(xs) < MIN_N:
      continue
    mean = sum(xs) / len(xs)
    std = (sum((x - mean) ** 2 for x in xs) / len(xs)) ** 0.5
    print(f"{b:>3}-{b + int(ANGLE_BIN):<3} deg {len(xs):>7} {mean:>11.2f} {std:>6.2f}")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: python3 steerratio_by_angle.py <rlog> [<rlog> ...]")
    sys.exit(1)
  main(sys.argv[1:])
