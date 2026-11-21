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
  python3 -m openpilot.nrdr.tools.lateral.tune_report <rlog> [<rlog> ...]
  python3 -m openpilot.nrdr.tools.lateral.tune_report /data/media/0/realdata/<route>--0/rlog.zst
  python3 -m openpilot.nrdr.tools.lateral.tune_report /data/media/0/realdata/*/rlog.zst  # whole day

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


# --- friendly scoring & advice ------------------------------------------------
# Speed bands match the UI knobs (Lateral Tuning), so every suggestion points at a
# slider the user can actually move.

BAND_DEFS = (
  ("below 25 mph", 0, 25, "Low Speed PID Scale (Below 25mph)", "Low Pass Filter Tau (Below 25mph)"),
  ("25-50 mph", 25, 50, "Standard Speed PID Scale (25-50mph)", "Standard Tau (25-50mph)"),
  ("above 50 mph", 50, 10**9, "Highway PID Scale (50mph+)", "Highway Tau (50mph+)"),
)

SIDE_WORD = {"L": "left", "R": "right"}
PHASE_WORD = {"IN": "turn-in", "OUT": "unwind", "STR": "driving straight"}

# Score penalty weights / full-penalty thresholds. Hand-tunable.
SCORE_BIAS_FULL_DEG = 2.5    # weighted avg |bias| that costs the full 4 points
SCORE_RMS_FULL_DEG = 8.0     # weighted avg rms that costs the full 3 points
SCORE_FLIP_FLOOR = 8.0       # flips/100 below this are considered normal
SCORE_FLIP_FULL = 20.0       # flips/100 above floor that cost the full 2 points
SCORE_SAT_FULL_PCT = 25.0    # saturation % that costs the full 1 point


class _Agg:
  """Mergeable aggregate over Bin objects (flip merge is approximate)."""

  def __init__(self):
    self.n = 0
    self.sum_e = 0.0
    self.sum_e2 = 0.0
    self.flips = 0
    self.sat = 0
    self.total = 0

  def add_bin(self, b):
    self.n += b.n
    self.sum_e += b.sum_e
    self.sum_e2 += b.sum_e2
    self.flips += b.sign_flips
    self.sat += b.n_sat_seen
    self.total += b.n_total_seen

  def mean(self):
    return self.sum_e / self.n if self.n else 0.0

  def rms(self):
    if not self.n:
      return 0.0
    m = self.mean()
    return math.sqrt(max(self.sum_e2 / self.n - m * m, 0.0))

  def flip_rate(self):
    return 100.0 * self.flips / self.n if self.n else 0.0

  def sat_pct(self):
    return 100.0 * self.sat / self.total if self.total else 0.0


def _classify(agg):
  """Return 'saturated' / 'undertuned' / 'overtuned' / None for an aggregate.

  Order matters: a steady bias (undertuned) wins over a high flip count, because a
  strongly biased error rarely crosses zero anyway - if both look true, bias is the
  more trustworthy signal."""
  if agg.sat_pct() > 15.0:
    return "saturated"
  if abs(agg.mean()) > 1.5 and abs(agg.mean()) > 0.8 * agg.rms():
    return "undertuned"
  if agg.flip_rate() > 12.0 and agg.rms() > 1.0:
    return "overtuned"
  return None


def _severity(o, kind=None):
  # Magnitude of badness for ranking: bias + noise, with oscillation (flip rate)
  # weighted in so a pure hunting spot doesn't get out-ranked by mild bias spots.
  return abs(o.mean()) + 0.5 * o.rms() + 0.01 * o.flip_rate() + (2.0 if kind == "saturated" else 0.0)


def compute_score(speed_only):
  """0-10 score from sample-weighted bias / noise / oscillation / saturation."""
  tot = 0
  abs_bias_w = 0.0
  rms_w = 0.0
  flips = 0
  sat = 0
  seen = 0
  for b in speed_only.values():
    if b.n < MIN_SAMPLES:
      continue
    tot += b.n
    abs_bias_w += abs(b.mean()) * b.n
    rms_w += b.rms() * b.n
    flips += b.sign_flips
    sat += b.n_sat_seen
    seen += b.n_total_seen
  if tot == 0:
    return None, {}

  wb = abs_bias_w / tot
  wr = rms_w / tot
  fr = 100.0 * flips / tot
  sp = 100.0 * sat / seen if seen else 0.0
  pens = {
    "bias": 4.0 * min(wb / SCORE_BIAS_FULL_DEG, 1.0),
    "noise": 3.0 * min(wr / SCORE_RMS_FULL_DEG, 1.0),
    "oscillation": 2.0 * min(max(fr - SCORE_FLIP_FLOOR, 0.0) / SCORE_FLIP_FULL, 1.0),
    "saturation": 1.0 * min(sp / SCORE_SAT_FULL_PCT, 1.0),
  }
  score = max(0.0, 10.0 - sum(pens.values()))
  return round(score, 1), {"bias": wb, "rms": wr, "flip": fr, "sat": sp, "pens": pens}


def _suggest(kind, band_name, scale_knob, tau_knob, phase):
  if kind == "saturated":
    return ("The controller is pinned at its torque limit here, so PID scales won't help - "
            "this is a steering-authority limit, not a tuning problem.")
  if kind == "overtuned":
    s = (f"Logs show PID values might be overtuned at this speed (the controller is hunting). "
         f"Suggestion: lower {scale_knob} by about 10%, or add a touch more filtering "
         f"({tau_knob} +0.01-0.02).")
    return s + " If it feels like a narrow buzz rather than a sway, check the Notch Filter frequency instead."
  if kind == "undertuned":
    if phase == "STR":
      return ("Logs show the tune is too soft for straight-line driving at this speed. "
              "Suggestion: raise Center Boost a step or two, and make sure Center Boost Threshold "
              "covers the wheel angles you cruise at.")
    return (f"Logs show PID values might be undertuned at this speed (steady tracking lag). "
            f"Suggestion: raise {scale_knob} by 10-15% and re-scan. With Keep Feedforward Static ON, "
            f"that boost goes to error correction only, not the feedforward.")
  return ""


def friendly_report(bins, speed_only):
  """Returns printable lines: score headline, worst-spot callout, ranked findings."""
  lines = []
  score, stats = compute_score(speed_only)
  if score is None:
    return ["Not enough in-control, hands-off driving captured to score this tune yet. Drive more and re-scan."]

  # Worst single (mph, side, phase) bin for the headline callout.
  worst_key, worst_sev = None, 0.0
  for key, b in bins.items():
    if b.n < MIN_SAMPLES:
      continue
    sev = _severity(b, _classify_bin(b))
    if sev > worst_sev:
      worst_key, worst_sev = key, sev

  headline = f"Your tuning scored {score:g} out of 10"
  if worst_key is not None:
    mph, side, ph = worst_key
    b = bins[worst_key]
    where = f"{SIDE_WORD.get(side, side)} turns" if side in SIDE_WORD else "near center"
    if ph == "STR":
      where = "driving straight"
    headline += f", with the most error on {where} at {mph} mph"
    kind = _classify_bin(b)
    if kind == "undertuned":
      headline += ". Logs show PID values might be undertuned at this speed."
    elif kind == "overtuned":
      headline += ". Logs show PID values might be overtuned at this speed."
    elif kind == "saturated":
      headline += ". The controller runs out of steering authority there."
    else:
      headline += "."
  else:
    headline += "."
  lines.append(headline)
  lines.append(f"(weighted avg bias {stats['bias']:.2f} deg, rms {stats['rms']:.2f} deg, "
               f"flips {stats['flip']:.1f}/100, saturation {stats['sat']:.0f}%)")
  lines.append("")

  # Findings: classify each (mph, side, phase) bin individually, then group the
  # problem bins by (band, side, phase, kind). Aggregating healthy bins in would
  # dilute a hot spot and could even flip its diagnosis, so only problem bins count.
  problems = {}
  band_aggs = {}  # full per-band aggregates (all bins) for the asymmetry check
  for (mph, side, ph), b in bins.items():
    if b.n < MIN_SAMPLES:
      continue
    band = next(bd for bd in BAND_DEFS if bd[1] <= mph < bd[2])
    band_name, _lo, _hi, scale_knob, tau_knob = band
    band_aggs.setdefault((band_name, side, ph), _Agg()).add_bin(b)
    kind = _classify_bin(b)
    if kind is None:
      continue
    rec = problems.setdefault((band_name, side, ph, kind, scale_knob, tau_knob),
                              {"agg": _Agg(), "mphs": [], "sev": 0.0})
    rec["agg"].add_bin(b)
    rec["mphs"].append(mph)
    rec["sev"] = max(rec["sev"], _severity(b, kind))

  findings = sorted(problems.items(), reverse=True, key=lambda kv: kv[1]["sev"])

  if not findings:
    lines.append("No specific problem areas stood out. Nice tune.")
  else:
    lines.append("FINDINGS & SUGGESTIONS (worst first)")
    for i, ((band_name, side, ph, kind, scale_knob, tau_knob), rec) in enumerate(findings[:6], 1):
      agg = rec["agg"]
      side_w = SIDE_WORD.get(side, side)
      ph_w = PHASE_WORD.get(ph, ph)
      lo_m, hi_m = min(rec["mphs"]), max(rec["mphs"])
      mph_txt = f"{lo_m} mph" if lo_m == hi_m else f"{lo_m}-{hi_m} mph"
      lines.append(f"{i}. {side_w.capitalize()} {ph_w} at {mph_txt} ({band_name} band): "
                   f"avg err {agg.mean():+.2f} deg, rms {agg.rms():.2f}, flips {agg.flip_rate():.1f}/100, sat {agg.sat_pct():.0f}%.")
      lines.append(f"   {_suggest(kind, band_name, scale_knob, tau_knob, ph)}")
    lines.append("")

  # Left/right asymmetry per band+phase (the reason _pid_output_scale is split L/R).
  asym = []
  for (band_name, side, ph), agg in band_aggs.items():
    if side != "L" or agg.n < MIN_SAMPLES:
      continue
    right = band_aggs.get((band_name, "R", ph))
    if right is None or right.n < MIN_SAMPLES:
      continue
    l_rms, r_rms = agg.rms(), right.rms()
    hi, lo_v = max(l_rms, r_rms), min(l_rms, r_rms)
    if lo_v > 0.0 and hi / lo_v > 1.6 and hi > 1.5:
      weak = "left" if l_rms > r_rms else "right"
      asym.append(f"- {band_name} ({PHASE_WORD.get(ph, ph)}): the {weak} side tracks noticeably worse "
                  f"(rms {hi:.1f} vs {lo_v:.1f} deg). PID scales are symmetric, so this points at the "
                  f"per-direction constants in _pid_output_scale (advanced; see the L/R table below).")
  if asym:
    lines.append("LEFT/RIGHT ASYMMETRY")
    lines.extend(asym)
    lines.append("")

  return lines


def _classify_bin(b):
  agg = _Agg()
  agg.add_bin(b)
  return _classify(agg)


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
  print("TUNE SCORE")
  print("=" * 92)
  for line in friendly_report(bins, speed_only):
    print(line)

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


__all__ = (
  "ANGLE_STRAIGHT_DEG",
  "BAND_DEFS",
  "MIN_SAMPLES",
  "MS_TO_MPH",
  "PHASE_WORD",
  "SCORE_BIAS_FULL_DEG",
  "SCORE_FLIP_FLOOR",
  "SCORE_FLIP_FULL",
  "SCORE_RMS_FULL_DEG",
  "SCORE_SAT_FULL_PCT",
  "SIDE_WORD",
  "Bin",
  "compute_score",
  "diagnose",
  "friendly_report",
  "main",
)
