#!/usr/bin/env python3
"""tune_attribute.py - offline culprit attribution for the lateral tune (stage-1 param advisor).

tune_grid.py shows WHERE the car over/under-turns; this asks WHY, per (speed, angle) cell:
does the residual track steering RATE (-> damping / actuator lag), decay with TIME-in-turn
(-> integrator windup/freeze), or sit as a steady bias the FEEDFORWARD owns (-> kf)? It uses
the per-term contributions openpilot already logs in pidState (p, i, f, output), reports the
dominant signature with how strongly the data backs it, and is honest when the signal is mush.

It reasons only about OUR layer -- FF, P, I, D, lag. The kinematic params (steer ratio, offset,
stiffness) are paramsd's; this tool only READS them as context and FLAGS a residual that smells
kinematic as "paramsd's domain -- check it converged," it never prescribes a change there.

Gate: lat active, hands off, pid active, paramsd valid (so the residual is ours, not the
estimator mid-adaptation). Direction-normalized: + = under-turn, - = OVER-turn (L and R alike).

Usage:
  python3 tune_attribute.py <rlog> [<rlog> ...]
  python3 tune_attribute.py /data/media/0/realdata/*/rlog.zst
"""
import sys
import numpy as np

from openpilot.tools.lib.logreader import LogReader

MS_TO_MPH = 2.23694
DT = 0.01                    # controlsState ~100 Hz

SPEED_BIN_MPH = 5.0
ANGLE_BIN_DEG = 20.0
MIN_ABS_DES = 1.0

MIN_SAMPLES = 40            # frames a cell needs before we'll attribute it
RESID_REPORT = 3.0         # deg: only report cells whose mean residual exceeds this
RATE_SIG = 0.40            # |corr(resid, rate)| above this = rate-linked (dynamic)
RATE_PRESENT = 5.0         # deg/s: mean |rate| must exceed this for the rate signature to mean anything
FF_DOMINATED = 0.50        # |f|/|out| above this = feedforward is carrying the turn
I_HEAVY = 0.40             # |i|/|out| above this = the integrator is doing a lot of the work
TOP_N = 40


def collect(paths):
  rows = []
  lp = {"n": 0, "valid": 0, "sr": [], "ao": [], "srstd": [], "aostd": []}
  v_ego = 0.0
  pressed = False
  lat = False
  lp_ok = False
  t_turn = 0.0
  prev_sign = 0
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
        pressed = msg.carState.steeringPressed
      elif w == "carControl":
        lat = msg.carControl.latActive
      elif w == "liveParameters":
        p = msg.liveParameters
        lp_ok = bool(p.valid and p.steerRatioValid and p.angleOffsetValid and p.stiffnessFactorValid)
        lp["n"] += 1
        lp["valid"] += int(bool(p.valid))
        lp["sr"].append(float(p.steerRatio))
        lp["ao"].append(float(p.angleOffsetDeg))
        lp["srstd"].append(float(p.steerRatioStd))
        lp["aostd"].append(float(p.angleOffsetFastStd))
      elif w == "controlsState":
        lcs = msg.controlsState.lateralControlState
        if lcs.which() != "pidState":
          continue
        pid = lcs.pidState
        if not pid.active or not lat or pressed:
          t_turn = 0.0
          prev_sign = 0
          continue
        des = float(pid.steeringAngleDesiredDeg)
        act = float(pid.steeringAngleDeg)
        sgn = 1 if des > MIN_ABS_DES else (-1 if des < -MIN_ABS_DES else 0)
        if sgn == 0:
          t_turn = 0.0
          prev_sign = 0
          continue
        t_turn = 0.0 if sgn != prev_sign else t_turn + DT
        prev_sign = sgn
        resid = (des - act) if des > 0 else (act - des)              # + = under-turn
        rate = float(pid.steeringRateDeg) * (1.0 if des > 0 else -1.0)  # + = toward more turn
        rows.append((v_ego * MS_TO_MPH, abs(des), 1 if des > 0 else 0, resid,
                     float(pid.f), float(pid.i), float(pid.p), float(pid.output), rate, t_turn, lp_ok))
  return rows, lp


def _pearson(x, y):
  if len(x) < 3 or x.std() < 1e-9 or y.std() < 1e-9:
    return 0.0
  return float(np.corrcoef(x, y)[0, 1])


def _intercept(x, y):
  # residual extrapolated to rate=0 -> the steady (non-rate-linked) part of the bias
  if x.std() < 1e-9:
    return float(y.mean())
  slope, intercept = np.polyfit(x, y, 1)
  return float(intercept)


def _verdict(mean_resid, steady, r_rate, rate, r_time, ff_share, i_share):
  mean_rate = float(np.abs(rate).mean())
  # 1) rate-linked -> dynamic (damping / actuator lag): the steady-state learner can't fix this
  if abs(r_rate) >= RATE_SIG and mean_rate >= RATE_PRESENT:
    return ("rate-linked -> damping / actuator lag (DYNAMIC)", abs(r_rate),
            "tune D / SteerActuatorDelay; the auto-tuner won't touch this (not a steady bias)")
  # 2) integrator-limited: residual fades through the turn and I is carrying a lot of the load
  if r_time <= -0.30 and i_share >= I_HEAVY:
    return ("integrator-limited -> windup / freeze (I can't hold it)", abs(r_time),
            "check I gain / the unwind freeze; the bias fades as I slowly catches up")
  # 3) steady bias the feedforward owns
  if abs(steady) >= RESID_REPORT and ff_share >= FF_DOMINATED:
    knob = "lower kf" if steady < 0 else "raise kf"
    return ("steady FF bias -> kf", min(1.0, abs(steady) / 10.0),
            f"{knob} here -- or just let the auto-tuner cancel it; this is exactly its job")
  # 4) steady but not clearly FF-dominated -> ambiguous root cause, but the learner still cancels it
  if abs(steady) >= RESID_REPORT:
    return ("steady bias (mixed P/I/F)", min(1.0, abs(steady) / 10.0),
            "steady -> the auto-tuner cancels it; P/I/F split is confounded here, don't force a knob")
  return ("low / mixed signal", 0.0, "not enough separable signal -- tune by feel")


def analyze(rows):
  cells = {}
  for (mph, ades, isL, resid, f, i, p, out, rate, t, lp_ok) in rows:
    if not lp_ok:                       # attribute only frames paramsd vouched for -> the residual is ours
      continue
    key = (isL, int(mph / SPEED_BIN_MPH), int(ades / ANGLE_BIN_DEG))
    cells.setdefault(key, []).append((resid, f, i, p, out, rate, t))
  result = []
  for key, vals in cells.items():
    if len(vals) < MIN_SAMPLES:
      continue
    arr = np.array(vals, dtype=np.float64)   # cols: resid, f, i, p, out, rate, t
    resid, f, out, rate, t = arr[:, 0], arr[:, 1], arr[:, 4], arr[:, 5], arr[:, 6]
    i = arr[:, 2]
    mean_resid = float(resid.mean())
    if abs(mean_resid) < RESID_REPORT:
      continue
    steady = _intercept(rate, resid)
    ff_share = float(np.abs(f).mean() / (np.abs(out).mean() + 1e-6))
    i_share = float(np.abs(i).mean() / (np.abs(out).mean() + 1e-6))
    verdict, conf, fix = _verdict(mean_resid, steady, _pearson(resid, rate), rate, _pearson(resid, t), ff_share, i_share)
    result.append({"isL": key[0], "s": key[1], "a": key[2], "n": len(vals), "resid": mean_resid,
                   "steady": steady, "r_rate": _pearson(resid, rate), "ff": ff_share, "i": i_share,
                   "verdict": verdict, "conf": conf, "fix": fix})
  result.sort(key=lambda c: abs(c["resid"]), reverse=True)
  return result


def paramsd_context(lp):
  if lp["n"] == 0:
    print("paramsd context: no liveParameters in these logs.\n")
    return
  vf = 100.0 * lp["valid"] / lp["n"]
  sr = np.array(lp["sr"]); ao = np.array(lp["ao"])
  srstd = np.array(lp["srstd"]); aostd = np.array(lp["aostd"])
  print("paramsd context (read-only -- its domain, not ours):")
  print(f"  valid {vf:.0f}% of frames | steerRatio {sr.mean():.2f} (drift {sr.ptp():.2f}, std~{srstd.mean():.2f})"
        f" | angleOffset {ao.mean():+.2f} deg (drift {ao.ptp():.2f}, std~{aostd.mean():.2f})")
  if vf > 90 and sr.ptp() < 1.0 and srstd.mean() < 1.0:
    print("  -> looks settled; the residuals below are ours to attribute.\n")
  else:
    print("  -> paramsd was still moving / low-valid here; any near-center asymmetry is SUSPECT,")
    print("     re-run once it has converged before trusting the kinematic flag.\n")


def offset_flag(cells):
  loL = [c["steady"] for c in cells if c["isL"] and c["a"] == 0]
  loR = [c["steady"] for c in cells if not c["isL"] and c["a"] == 0]
  if loL and loR:
    asym = float(np.mean(loL) - np.mean(loR))
    if abs(asym) > 3.0:
      print(f"FLAG: near-center L/R steady bias differs by {asym:+.1f} deg -- that smells like steering")
      print("      offset, which is paramsd's angleOffset, NOT ours. Confirm paramsd converged first.\n")


def print_cells(cells):
  print(f"Top {min(TOP_N, len(cells))} offending cells (|resid| > {RESID_REPORT} deg, >= {MIN_SAMPLES} frames, paramsd-valid):\n")
  hdr = f"{'speed':>7} {'angle':>9} {'dir':>4} {'n':>5} {'resid':>7} {'steady':>7} {'r_rate':>7} {'FFsh':>5} {'Ish':>5}  verdict"
  print(hdr)
  print("-" * len(hdr))
  for c in cells[:TOP_N]:
    sp = f"{int(c['s'] * SPEED_BIN_MPH)}-{int((c['s'] + 1) * SPEED_BIN_MPH)}"
    an = f"{int(c['a'] * ANGLE_BIN_DEG)}-{int((c['a'] + 1) * ANGLE_BIN_DEG)}"
    d = "L" if c["isL"] else "R"
    print(f"{sp:>7} {an:>9} {d:>4} {c['n']:>5} {c['resid']:>+7.1f} {c['steady']:>+7.1f} {c['r_rate']:>+7.2f} {c['ff']:>5.2f} {c['i']:>5.2f}  {c['verdict']}")
    print(f"{'':>44}-> {c['fix']}  [confidence {c['conf']:.2f}]")
  print()


GUIDE = """Reading guide:
  resid   = mean tracking miss (deg): negative = OVER-turn, positive = under-turn.
  steady  = the part of resid left when steering rate -> 0; this is the bias FF/the learner own.
  r_rate  = correlation of resid with steering rate. High -> the miss is DYNAMIC (damping/lag),
            not a steady tune error -- the auto-tuner deliberately won't touch it.
  FFsh    = fraction of output the feedforward is carrying; high + steady resid -> it's a kf issue.
  Ish     = fraction the integrator is carrying; high + a residual that fades through the turn ->
            the integrator is the limiter (windup/freeze).
  The split it CAN'T make cleanly (P vs I, stiffness vs steer ratio) it says so instead of guessing.
  Where it says 'steady', that cell is exactly what the online auto-tuner cancels on its own."""


def main(paths):
  rows, lp = collect(paths)
  valid = sum(1 for r in rows if r[10])
  print(f"\nCollected {len(rows)} gated pid frames ({valid} with paramsd valid).\n")
  paramsd_context(lp)
  cells = analyze(rows)
  if not cells:
    print("No cells cleared the residual + sample bar. Either it's clean where you have data, or you need more miles.")
    return
  offset_flag(cells)
  print_cells(cells)
  print(GUIDE)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
  main(sys.argv[1:])
