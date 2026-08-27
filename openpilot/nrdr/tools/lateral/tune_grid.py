#!/usr/bin/env python3
"""
tune_grid.py - 2D error map of the lateral tune across speed x steering angle.

Companion to tune_report.py / tune_trace.py. Where those surface the worst low-speed
turn events, this characterizes the WHOLE operating envelope: it bins every active,
hands-off PID frame by speed (0-85 mph) and |desired steering angle| (0-500 deg),
split by turn direction, and reports the steering tracking error per cell. The point
is to lay the non-linear response out flat - exactly where, and in which direction,
the car over- or under-turns.

The error is DIRECTION-NORMALIZED, so the sign means the same thing for left and right:
  negative cell  -> car OVER-turns there  (turned more than commanded)  <- the roundabout symptom
  positive cell  -> car UNDER-turns there (turned less than commanded)
That lets you read LEFT vs RIGHT at the same cell directly and see the asymmetry.

Best run with the StarPilot additions toggled OFF, so you're measuring the raw
banded PID/F + D base rather than the borrowed turn-in scaling on top.

Gate (same as tune_report): lateral active, hands off the wheel.

Usage:
  python3 -m openpilot.nrdr.tools.lateral.tune_grid <rlog> [<rlog> ...]
  python3 -m openpilot.nrdr.tools.lateral.tune_grid /data/media/0/realdata/*/rlog.zst

Prints a per-direction grid + sample counts, and (if matplotlib is installed) writes
a heatmap PNG. Read-only - touches nothing on the device, changes no params.
Tighten SPEED_BIN_MPH / ANGLE_BIN_DEG below for finer resolution.
"""
import sys
import math

from openpilot.tools.lib.logreader import LogReader

MS_TO_MPH = 2.23694

SPEED_MAX_MPH = 85.0
SPEED_BIN_MPH = 5.0          # -> 17 speed rows
ANGLE_MAX_DEG = 500.0
ANGLE_BIN_DEG = 20.0         # -> 25 angle columns
MIN_ABS_DES = 1.0           # deg: ignore dead-ahead micro-corrections
MIN_CELL = 8                 # frames a cell needs before it's trusted/printed
HEATMAP_PNG = "/tmp/tune_grid_heatmap.png"

N_SPEED = int(SPEED_MAX_MPH / SPEED_BIN_MPH)
N_ANGLE = int(ANGLE_MAX_DEG / ANGLE_BIN_DEG)


def collect(paths):
  # -> list of (mph, desired_deg, actual_deg, error_deg)  where error_deg = desired - actual
  samples = []
  v_ego = 0.0
  steering_pressed = False
  lat_active = False
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
      elif w == "controlsState":
        lcs = msg.controlsState.lateralControlState
        if lcs.which() != "pidState":
          continue
        pid = lcs.pidState
        if not pid.active or not lat_active or steering_pressed:
          continue
        des = float(pid.steeringAngleDesiredDeg)
        act = float(pid.steeringAngleDeg)
        samples.append((v_ego * MS_TO_MPH, des, act, des - act))
  return samples


def build_grid(samples):
  def empty():
    return [[[] for _ in range(N_ANGLE)] for _ in range(N_SPEED)]
  errs = {"L": empty(), "R": empty()}
  for mph, des, _act, err in samples:
    if abs(des) < MIN_ABS_DES:
      continue
    s = int(mph / SPEED_BIN_MPH)
    a = int(abs(des) / ANGLE_BIN_DEG)
    if not (0 <= s < N_SPEED and 0 <= a < N_ANGLE):
      continue
    # direction-normalize so the sign is consistent: negative = OVER-turn (|actual| > |desired|),
    # positive = under-turn, for both left and right.
    errs["L" if des > 0 else "R"][s][a].append(err if des > 0 else -err)
  return errs


def cell_stats(vals):
  n = len(vals)
  if n == 0:
    return None
  mean = sum(vals) / n
  rms = math.sqrt(sum(v * v for v in vals) / n)
  peak = max(vals, key=abs)
  return n, mean, rms, peak


def max_used_angle_bin(errs):
  hi = 0
  for d in errs:
    for s in range(N_SPEED):
      for a in range(N_ANGLE):
        if len(errs[d][s][a]) >= MIN_CELL:
          hi = max(hi, a)
  return hi


def _angle_hdr(hi_a):
  axis = "mph | deg"
  s = f"{axis:>10} |"
  for a in range(hi_a + 1):
    label = f"{int(a * ANGLE_BIN_DEG)}-{int((a + 1) * ANGLE_BIN_DEG)}"
    s += f"{label:>8}"
  return s


def _row_prefix(s):
  label = f"{int(s * SPEED_BIN_MPH)}-{int((s + 1) * SPEED_BIN_MPH)}"
  return f"{label:>10} |"


def print_grid(errs, direction, hi_a):
  name = "LEFT" if direction == "L" else "RIGHT"
  bar = "=" * (12 + (hi_a + 1) * 8)
  print(bar)
  print(f"{name} turns - mean error (deg): negative = OVER-turn, positive = under-turn  ('.' = <{MIN_CELL} frames)")
  print(bar)
  print(_angle_hdr(hi_a))
  for s in range(N_SPEED):
    row = _row_prefix(s)
    for a in range(hi_a + 1):
      st = cell_stats(errs[direction][s][a])
      row += f"{'.':>8}" if (st is None or st[0] < MIN_CELL) else f"{st[1]:>+8.1f}"
    print(row)
  print()


def print_counts(errs, direction, hi_a):
  name = "LEFT" if direction == "L" else "RIGHT"
  print(f"--- {name} sample counts per cell ---")
  print(_angle_hdr(hi_a))
  for s in range(N_SPEED):
    row = _row_prefix(s)
    for a in range(hi_a + 1):
      n = len(errs[direction][s][a])
      row += f"{n:>8}" if n else f"{'.':>8}"
    print(row)
  print()


def make_heatmap(errs, hi_a):
  try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
  except Exception:
    print("(heatmap skipped - matplotlib/numpy not available here. `pip install matplotlib`, or run on your PC.)")
    return

  grids = {}
  vmax = 0.0
  for d in ("L", "R"):
    g = np.full((N_SPEED, hi_a + 1), np.nan)
    for s in range(N_SPEED):
      for a in range(hi_a + 1):
        st = cell_stats(errs[d][s][a])
        if st is not None and st[0] >= MIN_CELL:
          g[s, a] = st[1]
    grids[d] = g
    if np.any(~np.isnan(g)):
      vmax = max(vmax, float(np.nanmax(np.abs(g))))
  vmax = vmax or 1.0

  fig, axes = plt.subplots(1, 2, figsize=(max(9.0, (hi_a + 1) * 0.7), 7), constrained_layout=True)
  for ax, d in zip(axes, ("L", "R")):
    im = ax.imshow(grids[d], origin="lower", aspect="auto", cmap="RdBu", vmin=-vmax, vmax=vmax)
    ax.set_title(("LEFT" if d == "L" else "RIGHT") + " turns - mean error (deg)")
    ax.set_xlabel("|steering angle| (deg)")
    ax.set_ylabel("speed (mph)")
    ax.set_xticks(range(hi_a + 1))
    ax.set_xticklabels([int(a * ANGLE_BIN_DEG) for a in range(hi_a + 1)], rotation=90, fontsize=7)
    ax.set_yticks(range(N_SPEED))
    ax.set_yticklabels([int(s * SPEED_BIN_MPH) for s in range(N_SPEED)], fontsize=7)
    fig.colorbar(im, ax=ax, shrink=0.85, label="over-turn (-)      under-turn (+)")
  fig.savefig(HEATMAP_PNG, dpi=130)
  print(f"heatmap saved -> {HEATMAP_PNG}")


def main(paths):
  samples = collect(paths)
  print(f"\nCollected {len(samples)} active hands-off pid frames.")
  errs = build_grid(samples)
  usable = sum(1 for d in errs for s in range(N_SPEED) for a in range(N_ANGLE) if len(errs[d][s][a]) >= MIN_CELL)
  if usable == 0:
    print("Not enough binned data. Need hands-off, lat-active driving across a range of speeds/angles.")
    return
  hi_a = max_used_angle_bin(errs)
  print(f"Bins: {int(SPEED_BIN_MPH)} mph x {int(ANGLE_BIN_DEG)} deg, out to {int((hi_a + 1) * ANGLE_BIN_DEG)} deg of wheel. "
        f"{usable} cells with >= {MIN_CELL} frames.\n")
  for d in ("L", "R"):
    print_grid(errs, d, hi_a)
  for d in ("L", "R"):
    print_counts(errs, d, hi_a)
  make_heatmap(errs, hi_a)

  print("\nReading guide:")
  print("  cell = mean direction-normalized error: negative = OVER-turn, positive = under-turn (same sign L and R).")
  print("  a strong NEGATIVE band = the car consistently OVER-turns there (the roundabout problem).")
  print("  read LEFT vs RIGHT at the same cell to see the asymmetry head-on.")
  print("  the counts grids tell you which cells you actually have the miles to trust.")
  print("  run it with StarPilot additions OFF to see the raw PID/F + D base you're tuning.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
  main(sys.argv[1:])


__all__ = (
  "ANGLE_BIN_DEG",
  "ANGLE_MAX_DEG",
  "HEATMAP_PNG",
  "MIN_ABS_DES",
  "MIN_CELL",
  "MS_TO_MPH",
  "N_ANGLE",
  "N_SPEED",
  "SPEED_BIN_MPH",
  "SPEED_MAX_MPH",
  "build_grid",
  "cell_stats",
  "collect",
  "main",
  "make_heatmap",
  "max_used_angle_bin",
  "print_counts",
  "print_grid",
)
