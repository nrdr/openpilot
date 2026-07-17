#!/usr/bin/env python3
"""
sr_curve_fit.py — offline companion to nrdr_steer_ratio_curve.py (Phase C).

Fit an angle-dependent steer-ratio curve from drive logs (same physics + gates as the
live gap-filler), write it into NrdrSteerRatioCurveData, and/or export a paste-ready
fingerprint seed for NRDR_STEER_RATIO_CURVES in latcontrol_pid.py.

  view                         show device CurveData (promoted bins + coverage)
  fit <rlog> [<rlog> ...]      measure from logs; print table (add --apply to write Params)
  export                       print Python seed snippet from device CurveData
  export <rlog> [...]          fit then print seed snippet (no write unless --apply)

Gates (match live learner / author protocol):
  lat active, !steeringPressed (unless --calibrate), v ≥ ~7 mph, |steeringRate| ≤ 20°/s,
  |yaw| / |SWA| floors, SR in (5, 40).

Examples:
  python3 sr_curve_fit.py view
  python3 sr_curve_fit.py fit /data/media/0/realdata/*/rlog.zst
  python3 sr_curve_fit.py fit /data/media/0/realdata/*/rlog.zst --apply
  python3 sr_curve_fit.py fit route--*/rlog.zst --apply --replace   # destructive wipe
  python3 sr_curve_fit.py export --fingerprint HONDA_CRV_5G
  python3 sr_curve_fit.py fit route--*/rlog.zst --export --fingerprint HONDA_CRV_5G

On a PC without Params, use --file curve.json for read/write.
Run --apply OFFROAD (a live learner may overwrite CurveData while driving).
--apply merges into the existing sample pool by default so a thin fit cannot wipe history.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict

from openpilot.selfdrive.controls.lib.nrdr_steer_ratio_curve import (
  ANGLE_BP,
  BIN_HALF,
  DATA_VERSION,
  MIN_ABS_SWA_DEG,
  MIN_V_MS,
  MIN_YAW_RAD_S,
  RATE_GATE_DEG_S,
  SR_MAX,
  SR_MIN,
  STD_MAX,
  _bin_index,
  _n_min,
)

PARAM_KEY = "NrdrSteerRatioCurveData"


def _load_json(path_or_none):
  if path_or_none:
    with open(path_or_none, "r", encoding="utf-8") as f:
      return json.load(f)
  from openpilot.common.params import Params
  raw = Params().get(PARAM_KEY)
  if raw is None:
    return {"version": DATA_VERSION, "promoted": {}, "bins": {}}
  if isinstance(raw, bytes):
    raw = json.loads(raw.decode("utf-8"))
  elif isinstance(raw, str):
    raw = json.loads(raw)
  if not isinstance(raw, dict):
    return {"version": DATA_VERSION, "promoted": {}, "bins": {}}
  return raw


def _save_json(data: dict, path_or_none):
  data = dict(data)
  data["version"] = DATA_VERSION
  if path_or_none:
    with open(path_or_none, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, sort_keys=True)
      f.write("\n")
  else:
    from openpilot.common.params import Params
    Params().put(PARAM_KEY, data)


def _empty_bin():
  return {"n": 0, "sum": 0.0, "sumsq": 0.0, "nPos": 0, "nNeg": 0}


def _bin_stats(b):
  n = int(b.get("n", 0))
  if n <= 0:
    return 0.0, 0.0, 0
  mean = float(b["sum"]) / n
  var = max(float(b["sumsq"]) / n - mean * mean, 0.0)
  return mean, math.sqrt(var), n


def fit_logs(paths, calibrate: bool = False):
  """Return (wheelbase, fingerprint, bins dict keyed by angle str, sample_count)."""
  from openpilot.tools.lib.logreader import LogReader
  from openpilot.selfdrive.locationd.helpers import Pose, PoseCalibrator

  wheelbase = None
  fingerprint = None
  v = a = yaw = rate = 0.0
  pressed = True
  lat = False
  samples = defaultdict(list)  # angle_key -> list of (sr, sign)
  calibrator = PoseCalibrator()
  skipped_uncal = 0

  for p in paths:
    try:
      lr = LogReader(p)
    except Exception as e:
      print(f"!! could not open {p}: {e}", file=sys.stderr)
      continue
    for m in lr:
      w = m.which()
      if w == "carParams":
        if wheelbase is None:
          wheelbase = float(m.carParams.wheelbase)
        if fingerprint is None:
          fingerprint = str(m.carParams.carFingerprint)
      elif w == "carState":
        v = float(m.carState.vEgo)
        a = float(m.carState.steeringAngleDeg)
        rate = float(m.carState.steeringRateDeg)
        pressed = bool(m.carState.steeringPressed)
      elif w == "carControl":
        lat = bool(m.carControl.latActive)
      elif w == "liveCalibration":
        calibrator.feed_live_calib(m.liveCalibration)
      elif w == "livePose":
        if wheelbase is None:
          continue
        if not calibrator.calib_valid:
          skipped_uncal += 1
          continue
        # Match live LatControlPID: calibrated yaw, not raw device-frame z.
        device_pose = Pose.from_live_pose(m.livePose)
        yaw = float(calibrator.build_calibrated_pose(device_pose).angular_velocity.yaw)
        if not calibrate:
          if not lat or pressed:
            continue
        if v < MIN_V_MS or abs(rate) > RATE_GATE_DEG_S:
          continue
        if abs(a) < MIN_ABS_SWA_DEG or abs(yaw) < MIN_YAW_RAD_S:
          continue
        curv = yaw / v
        rw = math.atan(wheelbase * curv)
        if abs(rw) < 1e-4:
          continue
        sr = abs(math.radians(a) / rw)
        if not (SR_MIN < sr < SR_MAX):
          continue
        key = str(ANGLE_BP[_bin_index(abs(a))])
        samples[key].append((sr, 1 if a >= 0.0 else -1))

  if skipped_uncal and not samples:
    print(f"!! skipped {skipped_uncal} livePose frames before calibration was valid", file=sys.stderr)

  bins = {}
  for key, xs in samples.items():
    b = _empty_bin()
    for sr, sign in xs:
      b["n"] += 1
      b["sum"] += sr
      b["sumsq"] += sr * sr
      if sign >= 0:
        b["nPos"] += 1
      else:
        b["nNeg"] += 1
    bins[key] = b
  return wheelbase, fingerprint, bins, sum(len(v) for v in samples.values())


def promote_from_bins(bins: dict) -> tuple[dict, dict]:
  promoted = {}
  promoted_n = {}
  for key, b in bins.items():
    angle = float(key)
    mean, std, n = _bin_stats(b)
    if n < _n_min(angle) or std > STD_MAX:
      continue
    promoted[key] = round(mean, 3)
    promoted_n[key] = int(n)
  return promoted, promoted_n


def merge_curve_data(existing: dict, bins: dict, promoted: dict, promoted_n: dict, merge: bool) -> dict:
  out_bins = {}
  if merge:
    for k, b in (existing.get("bins") or {}).items():
      out_bins[str(k)] = dict(b)
  for k, b in bins.items():
    if k not in out_bins:
      out_bins[k] = dict(b)
    else:
      o = out_bins[k]
      out_bins[k] = {
        "n": int(o.get("n", 0)) + int(b.get("n", 0)),
        "sum": float(o.get("sum", 0.0)) + float(b.get("sum", 0.0)),
        "sumsq": float(o.get("sumsq", 0.0)) + float(b.get("sumsq", 0.0)),
        "nPos": int(o.get("nPos", 0)) + int(b.get("nPos", 0)),
        "nNeg": int(o.get("nNeg", 0)) + int(b.get("nNeg", 0)),
      }
  if merge:
    # Re-promote from merged cumulative bins (evidence-weighted by construction).
    out_promoted, out_n = promote_from_bins(out_bins)
  else:
    out_promoted = dict(promoted)
    out_n = dict(promoted_n)
  return {
    "version": DATA_VERSION,
    "promoted": out_promoted,
    "promotedN": out_n,
    "bins": out_bins,
  }


def print_table(bins: dict, promoted: dict, wheelbase, fingerprint, n_samples):
  print(f"fingerprint = {fingerprint or '?'}")
  print(f"wheelbase   = {wheelbase:.3f} m" if wheelbase else "wheelbase   = ?")
  print(f"samples     = {n_samples}")
  print(f"gates       = v≥{MIN_V_MS/0.44704:.0f}mph  |rate|≤{RATE_GATE_DEG_S:.0f}°/s  "
        f"|yaw|≥{MIN_YAW_RAD_S}  |SWA|≥{MIN_ABS_SWA_DEG}°  band±{BIN_HALF}°")
  print()
  print(f"{'|angle|':>8} {'n':>7} {'n+/n-':>9} {'mean SR':>9} {'std':>6} {'Nmin':>5} {'promoted':>9}")
  for a in ANGLE_BP:
    key = str(a)
    b = bins.get(key)
    if not b:
      continue
    mean, std, n = _bin_stats(b)
    promo = promoted.get(key)
    promo_s = f"{promo:.2f}" if promo is not None else "-"
    print(f"{a:>6.0f}° {n:>7} {int(b.get('nPos',0)):>4}/{int(b.get('nNeg',0)):<4} "
          f"{mean:>9.2f} {std:>6.2f} {_n_min(a):>5} {promo_s:>9}")
  print(f"\npromoted bins: {len(promoted)}")


def export_snippet(promoted: dict, fingerprint: str) -> str:
  if not promoted:
    return "# no promoted bins to export"
  pts = sorted((float(k), float(v)) for k, v in promoted.items())
  # Always include a 0° anchor (hold first measured) so seed interp is well-defined on-center
  if pts[0][0] > 0.0:
    pts = [(0.0, pts[0][1])] + pts
  bps = [p[0] for p in pts]
  vals = [p[1] for p in pts]
  bp_s = ", ".join(f"{x:g}" for x in bps)
  v_s = ", ".join(f"{float(x):.2f}" for x in vals)
  return (
    f'# Paste into NRDR_STEER_RATIO_CURVES in latcontrol_pid.py (human-reviewed graduation)\n'
    f'"{fingerprint}": ([{bp_s}], [{v_s}]),\n'
  )


def cmd_view(args):
  data = _load_json(args.file)
  bins = data.get("bins") or {}
  promoted = {str(k): float(v) for k, v in (data.get("promoted") or {}).items()}
  print_table(bins, promoted, None, None, sum(int(b.get("n", 0)) for b in bins.values()))
  if args.export:
    fp = args.fingerprint or "YOUR_FINGERPRINT"
    print("\n" + export_snippet(promoted, fp))


def cmd_fit(args):
  if not args.paths:
    print("fit requires one or more rlog paths", file=sys.stderr)
    sys.exit(2)
  wheelbase, fingerprint, bins, n = fit_logs(args.paths, calibrate=args.calibrate)
  promoted, promoted_n = promote_from_bins(bins)
  print_table(bins, promoted, wheelbase, fingerprint, n)
  if not promoted:
    print("\n!! no bins met Nmin/std — need more cornering / try --calibrate for manual fills",
          file=sys.stderr)
    if args.apply and not args.force:
      print("refusing --apply with zero promoted bins (pass --force to overwrite anyway)",
            file=sys.stderr)
      sys.exit(1)

  data = {"version": DATA_VERSION, "promoted": promoted, "promotedN": promoted_n, "bins": bins}
  if args.apply:
    # Default merge: accumulate into existing pool so a thin fit cannot wipe history.
    do_merge = not args.replace
    existing = _load_json(args.file)
    data = merge_curve_data(existing, bins, promoted, promoted_n, merge=do_merge)
    _save_json(data, args.file)
    where = args.file or f"Params:{PARAM_KEY}"
    how = "merged" if do_merge else "replaced"
    print(f"\nwrote {len(data['promoted'])} promoted bins → {where} ({how})")

  if args.export:
    fp = args.fingerprint or fingerprint or "YOUR_FINGERPRINT"
    print("\n" + export_snippet(data["promoted"], fp))


def cmd_export(args):
  if args.paths:
    args.apply = False
    args.export = True
    cmd_fit(args)
    return
  data = _load_json(args.file)
  promoted = {str(k): float(v) for k, v in (data.get("promoted") or {}).items()}
  fp = args.fingerprint or "YOUR_FINGERPRINT"
  print(export_snippet(promoted, fp))


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("cmd", choices=["view", "fit", "export"], help="subcommand")
  ap.add_argument("paths", nargs="*", help="rlog path(s) for fit/export")
  ap.add_argument("--apply", action="store_true",
                  help="write CurveData to Params/file (merges into existing pool by default)")
  ap.add_argument("--replace", action="store_true",
                  help="with --apply: replace CurveData instead of evidence-merge (destructive)")
  ap.add_argument("--file", default=None, help="JSON file instead of Params (PC use)")
  ap.add_argument("--export", action="store_true", help="also print NRDR_STEER_RATIO_CURVES snippet")
  ap.add_argument("--fingerprint", default=None, help="fingerprint string for export snippet")
  ap.add_argument("--calibrate", action="store_true",
                  help="relax latActive/steeringPressed (manual/lot fills in logs)")
  ap.add_argument("--force", action="store_true",
                  help="allow --apply even when no bins promoted (can wipe CurveData)")
  args = ap.parse_args()

  if args.cmd == "view":
    cmd_view(args)
  elif args.cmd == "fit":
    cmd_fit(args)
  else:
    cmd_export(args)


if __name__ == "__main__":
  main()
