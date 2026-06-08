#!/usr/bin/env python3
"""
tune_report.py - log-based lateral PID tuning report.

Reads one or more openpilot rlogs and reports how well the lateral PID controller
tracks the desired steering angle, per 1 mph speed bin, split by turn direction
(left/right) and phase (turn-in / unwind / straight).

Key metrics:
  mean_err / rms_err : absolute tracking error in DEGREES of steering wheel.
  rel_err%           : |error| as a PERCENT of the desired angle magnitude. This is
                       speed-fair: a 2 deg miss on a 100 deg low-speed turn (2%) is a
                       good track, while a 2 deg miss on a 4 deg highway nudge (50%) is
                       terrible. Use rel_err% to compare tune quality ACROSS speeds.
  mean_des           : mean |desired angle| in the bin (context: how big the turns are).
  flip/100           : error sign-changes per 100 frames (oscillation proxy).
  sat%               : fraction of frames pinned at the torque limit.

ONLY analyzes frames where the controller was genuinely in control:
  lateral active, hands off (not steeringPressed), not saturated.

Also reports the learned angle offset (from liveParameters) so you can tell whether a
left/right bias is the tune or a drifted learned offset.

Usage:
  python3 tune_report.py <rlog> [<rlog> ...]
  python3 tune_report.py /data/media/0/realdata/*/rlog.zst

Read-only.
"""
import sys
import math
from collections import defaultdict

from openpilot.tools.lib.logreader import LogReader

MS_TO_MPH = 2.23694
ANGLE_STRAIGHT_DEG = 2.0
REL_ERR_MIN_DES = 3.0   # only compute rel_err% when |desired| > this (avoid div blowup near center)
MIN_SAMPLES = 50


class Bin:
  __slots__ = ("n", "sum_e", "sum_e2", "sign_flips", "prev_e_sign",
               "sum_abs_out", "sum_abs_des", "n_sat_seen", "n_total_seen",
               "rel_n", "rel_sum")

  def __init__(self):
    self.n = 0
    self.sum_e = 0.0
    self.sum_e2 = 0.0
    self.sign_flips = 0
    self.prev_e_sign = 0
    self.sum_abs_out = 0.0
    self.sum_abs_des = 0.0
    self.n_sat_seen = 0
    self.n_total_seen = 0
    self.rel_n = 0
    self.rel_sum = 0.0

  def add(self, err, out, des):
    self.n += 1
    self.sum_e += err
    self.sum_e2 += err * err
    self.sum_abs_out += abs(out)
    self.sum_abs_des += abs(des)
    s = 1 if err > 0 else (-1 if err < 0 else 0)
    if s != 0 and self.prev_e_sign != 0 and s != self.prev_e_sign:
      self.sign_flips += 1
    if s != 0:
      self.prev_e_sign = s
    if abs(des) > REL_ERR_MIN_DES:
      self.rel_n += 1
      self.rel_sum += abs(err) / abs(des)

  def mean(self):
    return self.sum_e / self.n if self.n else 0.0

  def rms(self):
    if not self.n:
      return 0.0
    m = self.mean()
    return math.sqrt(max(self.sum_e2 / self.n - m * m, 0.0))

  def flip_rate(self):
    return 100.0 * self.sign_flips / self.n if self.n else 0.0

  def mean_abs_out(self):
    return self.sum_abs_out / self.n if self.n else 0.0

  def mean_abs_des(self):
    return self.sum_abs_des / self.n if self.n else 0.0

  def rel_pct(self):
    return 100.0 * self.rel_sum / self.rel_n if self.rel_n else float('nan')

  def sat_pct(self):
    return 100.0 * self.n_sat_seen / self.n_total_seen if self.n_total_seen else 0.0


def diagnose(b):
  rel = b.rel_pct()
  flip = b.flip_rate()
  rms = b.rms()
  tags = []
  if b.sat_pct() > 15:
    tags.append("SATURATING")
  if flip > 12 and rms > 0.5:
    tags.append("OSCILLATING (kp high?)")
  # rel_err% is the speed-fair tune-quality signal:
  if not math.isnan(rel):
    if rel > 25:
      tags.append("WEAK/LAGGING (raise kp/kf)")
    elif rel > 12:
      tags.append("soft")
  if not tags:
    tags.append("ok")
  return ", ".join(tags)


def main(paths):
  bins = defaultdict(Bin)
  speed_only = defaultdict(Bin)

  v_ego = 0.0
  steering_pressed = False
  lat_active = False
  prev_desired = 0.0

  offset_sum = 0.0
  offset_n = 0
  offset_avg_last = None

  total = used = 0

  for path in paths:
    try:
      lr = LogReader(path)
    except Exception as e:
      print(f"!! could not open {path}: {e}", file=sys.stderr)
      continue

    for msg in lr:
      w = msg.which()
      if w == "carState":
        v_ego = msg.carState.vEgo
        steering_pressed = msg.carState.steeringPressed
      elif w == "carControl":
        lat_active = msg.carControl.latActive
      elif w == "liveParameters":
        lp = msg.liveParameters
        offset_sum += lp.angleOffsetDeg
        offset_n += 1
        offset_avg_last = lp.angleOffsetAverageDeg
      elif w == "controlsState":
        lcs = msg.controlsState.lateralControlState
        if lcs.which() != "pidState":
          continue
        pid = lcs.pidState
        total += 1
        if not pid.active:
          prev_desired = pid.steeringAngleDesiredDeg
          continue

        desired = pid.steeringAngleDesiredDeg
        actual = pid.steeringAngleDeg
        err = desired - actual
        out = pid.output
        sat = pid.saturated

        if not lat_active or steering_pressed:
          prev_desired = desired
          continue

        mph = int(round(v_ego * MS_TO_MPH))
        if mph < 1:
          prev_desired = desired
          continue

        d_delta = desired - prev_desired
        phase = desired * d_delta
        prev_desired = desired

        abs_des = abs(desired)
        if abs_des < ANGLE_STRAIGHT_DEG:
          ph = "STR"
        elif phase > 0:
          ph = "IN"
        elif phase < 0:
          ph = "OUT"
        else:
          ph = "STR"
        side = "L" if desired > 0 else ("R" if desired < 0 else "STR")

        for tgt in (bins[(mph, side, ph)], speed_only[mph]):
          tgt.n_total_seen += 1
          if sat:
            tgt.n_sat_seen += 1
        if sat:
          continue

        bins[(mph, side, ph)].add(err, out, desired)
        speed_only[mph].add(err, out, desired)
        used += 1

  print(f"\nParsed {total} pid frames, used {used} in-control hands-off non-saturated frames.")
  if offset_n:
    print(f"Learned angle offset: instant avg {offset_sum/offset_n:+.3f} deg, "
          f"long-term avg {offset_avg_last:+.3f} deg  "
          f"(if non-trivial, a left/right bias below may be this, not the tune)")

  print("\n" + "=" * 100)
  print("PER-SPEED SUMMARY (all directions/phases). Use rel_err% to compare tune quality across speeds.")
  print("=" * 100)
  print(f"{'mph':>4} {'n':>7} {'mean_des':>8} {'mean_err':>9} {'rms_err':>8} {'rel_err%':>9} {'flip/100':>9} {'sat%':>5}  diagnosis")
  for mph in sorted(speed_only):
    b = speed_only[mph]
    if b.n < MIN_SAMPLES:
      continue
    rel = b.rel_pct()
    rel_s = f"{rel:8.1f}" if not math.isnan(rel) else "     n/a"
    print(f"{mph:>4} {b.n:>7} {b.mean_abs_des():>8.1f} {b.mean():>9.3f} {b.rms():>8.3f} {rel_s:>9} "
          f"{b.flip_rate():>9.1f} {b.sat_pct():>4.0f}%  {diagnose(b)}")

  print("\n" + "=" * 100)
  print("LEFT vs RIGHT TURN-IN ASYMMETRY (rel_err%, turn-in only). Big L/R gap = asymmetric EPS.")
  print("=" * 100)
  print(f"{'mph':>4} {'L_in rel%':>10} {'R_in rel%':>10} {'gap':>8}   weaker side")
  for mph in sorted(speed_only):
    L = bins.get((mph, "L", "IN"))
    R = bins.get((mph, "R", "IN"))
    if not L or not R or L.rel_n < MIN_SAMPLES or R.rel_n < MIN_SAMPLES:
      continue
    lr_, rr_ = L.rel_pct(), R.rel_pct()
    gap = lr_ - rr_
    weak = "LEFT turn-in" if gap > 3 else ("RIGHT turn-in" if gap < -3 else "balanced")
    print(f"{mph:>4} {lr_:>10.1f} {rr_:>10.1f} {gap:>+8.1f}   {weak}")

  print("\n" + "=" * 100)
  print("FULL PER-SPEED x DIRECTION x PHASE")
  print("=" * 100)
  print(f"{'mph':>4} {'side':>4} {'phase':>5} {'n':>6} {'mean_des':>8} {'mean_err':>9} {'rms_err':>8} {'rel_err%':>9} {'flip/100':>9}")
  for key in sorted(bins):
    mph, side, ph = key
    b = bins[key]
    if b.n < MIN_SAMPLES:
      continue
    rel = b.rel_pct()
    rel_s = f"{rel:8.1f}" if not math.isnan(rel) else "     n/a"
    print(f"{mph:>4} {side:>4} {ph:>5} {b.n:>6} {b.mean_abs_des():>8.1f} {b.mean():>9.3f} "
          f"{b.rms():>8.3f} {rel_s:>9} {b.flip_rate():>9.1f}")

  print("\nReading guide:")
  print("  rel_err%  KEY METRIC. |error| as % of the requested angle. <12% good, 12-25% soft,")
  print("            >25% the controller is failing to deliver the requested motion (raise kp/kf).")
  print("            This is speed-fair, so low-speed bins are finally trustworthy here.")
  print("  mean_des  how big the turns were in that bin (low speed = big angles = needs more gain).")
  print("  L/R gap   positive = left turn-in is weaker than right (raise left turn_in_scale etc.).")
  print("  Check the learned-offset line up top before blaming the tune for a one-sided bias.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
  main(sys.argv[1:])
