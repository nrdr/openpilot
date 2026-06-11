#!/usr/bin/env python3
"""
tune_report.py - log-based lateral PID tuning report.

Reads one or more openpilot rlogs and reports, per 1 mph speed bin, how well the
lateral PID controller is tracking the desired steering angle. Splits by turn
direction (left/right) and phase (turn-in / unwind) so you can see exactly which
part of the tune (and which _pid_output_scale quadrant) is off.

ONLY analyzes frames where the controller was genuinely in control:
  - lateral control active
  - hands off the wheel (not steeringPressed)
  - not saturated (output not pinned to the limit)
These are excluded because their "error" reflects you/the limits, not the tune.

Usage:
  python3 tune_report.py <rlog> [<rlog> ...]
  python3 tune_report.py /data/media/0/realdata/<route>--0/rlog.zst
  python3 tune_report.py /data/media/0/realdata/*/rlog.zst     # whole day

Read-only. Touches nothing on the device, changes no params.
"""
import sys
import math
from collections import defaultdict

from openpilot.tools.lib.logreader import LogReader

MS_TO_MPH = 2.23694
ANGLE_STRAIGHT_DEG = 2.0      # |desired angle| below this = treated as "straight"
MIN_SAMPLES = 50              # don't report a bin with fewer frames than this


class Bin:
  __slots__ = ("n", "sum_e", "sum_e2", "sign_flips", "prev_e_sign",
               "sum_abs_out", "n_sat_seen", "n_total_seen")

  def __init__(self):
    self.n = 0
    self.sum_e = 0.0
    self.sum_e2 = 0.0
    self.sign_flips = 0
    self.prev_e_sign = 0
    self.sum_abs_out = 0.0
    self.n_sat_seen = 0       # saturated frames seen (counted before filtering them out of error stats)
    self.n_total_seen = 0     # all active+handsoff frames (for saturation %)

  def add(self, err, out):
    self.n += 1
    self.sum_e += err
    self.sum_e2 += err * err
    self.sum_abs_out += abs(out)
    s = 1 if err > 0 else (-1 if err < 0 else 0)
    if s != 0 and self.prev_e_sign != 0 and s != self.prev_e_sign:
      self.sign_flips += 1
    if s != 0:
      self.prev_e_sign = s

  def mean(self):
    return self.sum_e / self.n if self.n else 0.0

  def rms(self):
    if not self.n:
      return 0.0
    m = self.mean()
    var = max(self.sum_e2 / self.n - m * m, 0.0)
    return math.sqrt(var)

  def flip_rate(self):
    # sign flips per 100 samples (proxy for oscillation)
    return 100.0 * self.sign_flips / self.n if self.n else 0.0

  def mean_abs_out(self):
    return self.sum_abs_out / self.n if self.n else 0.0


def diagnose(b):
  mean = b.mean()
  rms = b.rms()
  flip = b.flip_rate()
  sat_pct = 100.0 * b.n_sat_seen / b.n_total_seen if b.n_total_seen else 0.0
  tags = []
  if sat_pct > 15:
    tags.append("SATURATING (out of authority)")
  if flip > 12 and rms > 0.5:
    tags.append("OSCILLATING (kp too high?)")
  if abs(mean) > 0.6 and abs(mean) > rms:
    tags.append("BIASED/SLUGGISH (kp/kf too low?)" if mean > 0 else "BIASED/SLUGGISH other dir")
  if not tags:
    tags.append("ok")
  return ", ".join(tags)


def main(paths):
  # bins keyed by (mph_int, side, phase) where side in L/R, phase in IN/OUT/STR
  bins = defaultdict(Bin)
  speed_only = defaultdict(Bin)

  v_ego = 0.0
  steering_pressed = False
  lat_active = False
  prev_desired = 0.0

  total = 0
  used = 0

  for path in paths:
    try:
      lr = LogReader(path)
    except Exception as e:
      print(f"!! could not open {path}: {e}", file=sys.stderr)
      continue

    for msg in lr:
      w = msg.which()
      if w == "carState":
        cs = msg.carState
        v_ego = cs.vEgo
        steering_pressed = cs.steeringPressed
      elif w == "carControl":
        lat_active = msg.carControl.latActive
      elif w == "controlsState":
        lcs = msg.controlsState.lateralControlState
        if lcs.which() != "pidState":
          continue
        pid = lcs.pidState
        total += 1
        if not pid.active:
          continue

        desired = pid.steeringAngleDesiredDeg
        actual = pid.steeringAngleDeg
        err = desired - actual
        out = pid.output
        sat = pid.saturated

        # gate: in control, hands off
        if not lat_active or steering_pressed or not pid.active:
          prev_desired = desired
          continue

        mph = int(round(v_ego * MS_TO_MPH))
        if mph < 1:
          prev_desired = desired
          continue

        # phase via desired-angle rate (matches _pid_output_scale's intent)
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

        # saturation accounting (on all in-control frames), then exclude sat from error stats
        for key in ((mph, side, ph), (mph,)):
          target = bins[key] if len(key) == 3 else speed_only[key[0]]
          target.n_total_seen += 1
          if sat:
            target.n_sat_seen += 1

        if sat:
          continue

        bins[(mph, side, ph)].add(err, out)
        speed_only[mph].add(err, out)
        used += 1

  print(f"\nParsed {total} pid frames, used {used} in-control hands-off non-saturated frames.\n")

  print("=" * 92)
  print("PER-SPEED SUMMARY (all directions/phases combined)")
  print("=" * 92)
  print(f"{'mph':>4} {'n':>7} {'mean_err':>9} {'rms_err':>8} {'flip/100':>9} {'|out|':>7} {'sat%':>6}  diagnosis")
  for mph in sorted(speed_only):
    b = speed_only[mph]
    if b.n < MIN_SAMPLES:
      continue
    sat_pct = 100.0 * b.n_sat_seen / b.n_total_seen if b.n_total_seen else 0.0
    print(f"{mph:>4} {b.n:>7} {b.mean():>9.3f} {b.rms():>8.3f} {b.flip_rate():>9.1f} "
          f"{b.mean_abs_out():>7.3f} {sat_pct:>5.0f}%  {diagnose(b)}")

  print("\n" + "=" * 92)
  print("PER-SPEED x DIRECTION x PHASE  (STR=straight, IN=turn-in, OUT=unwind)")
  print("  -> use this to spot left/right asymmetry and which _pid_output_scale quadrant is off")
  print("=" * 92)
  print(f"{'mph':>4} {'side':>4} {'phase':>5} {'n':>6} {'mean_err':>9} {'rms_err':>8} {'flip/100':>9} {'sat%':>6}")
  for key in sorted(bins):
    mph, side, ph = key
    b = bins[key]
    if b.n < MIN_SAMPLES:
      continue
    sat_pct = 100.0 * b.n_sat_seen / b.n_total_seen if b.n_total_seen else 0.0
    print(f"{mph:>4} {side:>4} {ph:>5} {b.n:>6} {b.mean():>9.3f} {b.rms():>8.3f} {b.flip_rate():>9.1f} {sat_pct:>5.0f}%")

  print("\nReading guide:")
  print("  mean_err  >0 means the car is UNDER-steering vs desired (lagging into the turn).")
  print("            sign tells which way it's biased; large |mean| with small rms = steady offset.")
  print("  rms_err   how much it jitters around its mean. High rms + high flip = oscillation.")
  print("  flip/100  error sign-changes per 100 frames. High = controller hunting (lower kp).")
  print("  sat%      fraction of frames pinned at the torque limit. High = out of authority")
  print("            (raise steer authority / it's the steady-state-error-in-saturation case).")
  print("  Compare L vs R at the same mph/phase: a big gap = asymmetric EPS, the reason the")
  print("  _pid_output_scale table is split left/right. Bump the matching constant for the weak side.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
  main(sys.argv[1:])
