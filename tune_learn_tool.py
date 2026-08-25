#!/usr/bin/env python3
"""
tune_learn_tool.py - offline companion to the 2D online tune learner (tune_learner.py).

  view                       show the learned trim map (NrdrTuneLearnerMap) as L/R grids + heatmap.
  view <rlog> [<rlog> ...]   same, plus the residual error grid from those logs, so you can see how
                             much systematic bias the learner has NOT yet cancelled.
  seed <rlog> [<rlog> ...]   compute a conservative warm-start trim map from drive logs (the
                             tune_grid error surface scaled to a small trim) and write it to the map.

Reads/writes the NrdrTuneLearnerMap param directly when run on the device. On a PC, pass
--file <path> to read/write a raw blob instead. Override the warm-start aggressiveness with
--gain <torque-per-deg>. Seeding is a head start only -- the online learner refines from there
using a cleaner (rate-gated) error signal.

  'view' is read-only. 'seed' overwrites the map, so run it OFFROAD (a running, enabled learner
  saves over it) and reset on-device to undo. The learner loads the map at the start of the next
  drive.

Usage:
  python3 tune_learn_tool.py view
  python3 tune_learn_tool.py view /data/media/0/realdata/*/rlog.zst
  python3 tune_learn_tool.py seed /data/media/0/realdata/*/rlog.zst
"""
import sys
import numpy as np

from openpilot.common.params import Params
from openpilot.sunnypilot.nrdr.tune_learner import (
  N_SPEED, N_ANGLE, SPEED_BIN_MPH, ANGLE_BIN_DEG, TRIM_HARD_FRAC,
)

PARAM_KEY = "NrdrTuneLearnerMap"
SEED_GAIN = 0.002       # torque per deg of residual error (gentle warm-start; the learner refines)
SEED_CAP = 0.10         # torque: warm-start cap, well under the learner's TRIM_HARD_FRAC runtime cap
SEED_MIN_SPEED_BIN = 1  # skip the 0-5 mph row -- transient junk the learner won't touch either
STEER_MAX = 1.0         # Honda Nidec normalized torque (the learner scales its real cap by steer_max)
HEATMAP_PNG = "/tmp/tune_learn_map.png"


def _blob(map_l, map_r):
  return np.concatenate([map_l.ravel(), map_r.ravel()]).astype(np.float32).tobytes()


def _unblob(raw):
  n = N_SPEED * N_ANGLE
  if not raw or len(raw) != 2 * n * 4:
    return None, None
  arr = np.frombuffer(raw, dtype=np.float32)
  return arr[:n].reshape(N_SPEED, N_ANGLE).copy(), arr[n:].reshape(N_SPEED, N_ANGLE).copy()


def load_map(file=None):
  if file:
    try:
      with open(file, "rb") as f:
        raw = f.read()
    except FileNotFoundError:
      return None, None
  else:
    raw = Params().get(PARAM_KEY)
  return _unblob(raw)


def save_map(map_l, map_r, file=None):
  blob = _blob(map_l, map_r)
  if file:
    with open(file, "wb") as f:
      f.write(blob)
  else:
    Params().put(PARAM_KEY, blob)


def _max_used_col(map_l, map_r):
  hi = 0
  for m in (map_l, map_r):
    nz = np.nonzero(np.any(m != 0.0, axis=0))[0]
    if len(nz):
      hi = max(hi, int(nz[-1]))
  return hi


def _hdr(hi_a):
  s = f"{'mph | deg':>10} |"
  for a in range(hi_a + 1):
    s += f"{f'{int(a * ANGLE_BIN_DEG)}-{int((a + 1) * ANGLE_BIN_DEG)}':>9}"
  return s


def print_map(m, name, hi_a):
  bar = "=" * (12 + (hi_a + 1) * 9)
  print(bar)
  print(f"{name} learned trim (torque; + = more turn in the commanded direction; '.' = 0)")
  print(bar)
  print(_hdr(hi_a))
  for s in range(N_SPEED):
    row = f"{f'{int(s * SPEED_BIN_MPH)}-{int((s + 1) * SPEED_BIN_MPH)}':>10} |"
    for a in range(hi_a + 1):
      v = float(m[s, a])
      row += f"{'.':>9}" if abs(v) < 1e-6 else f"{v:>+9.3f}"
    print(row)
  print()


def make_heatmap(map_l, map_r, hi_a):
  try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
  except Exception:
    print("(heatmap skipped - matplotlib not available. `pip install matplotlib`, or run on your PC.)")
    return
  vmax = max(float(np.abs(map_l).max()), float(np.abs(map_r).max()), 1e-6)
  fig, axes = plt.subplots(1, 2, figsize=(max(9.0, (hi_a + 1) * 0.7), 7), constrained_layout=True)
  for ax, (m, nm) in zip(axes, ((map_l, "LEFT"), (map_r, "RIGHT"))):
    g = np.where(m[:, :hi_a + 1] != 0.0, m[:, :hi_a + 1], np.nan)
    im = ax.imshow(g, origin="lower", aspect="auto", cmap="RdBu", vmin=-vmax, vmax=vmax)
    ax.set_title(f"{nm} learned trim (torque)")
    ax.set_xlabel("|steering angle| (deg)")
    ax.set_ylabel("speed (mph)")
    ax.set_xticks(range(hi_a + 1))
    ax.set_xticklabels([int(a * ANGLE_BIN_DEG) for a in range(hi_a + 1)], rotation=90, fontsize=7)
    ax.set_yticks(range(N_SPEED))
    ax.set_yticklabels([int(s * SPEED_BIN_MPH) for s in range(N_SPEED)], fontsize=7)
    fig.colorbar(im, ax=ax, shrink=0.85, label="less turn (-)      more turn (+)")
  fig.savefig(HEATMAP_PNG, dpi=130)
  print(f"heatmap saved -> {HEATMAP_PNG}")


def _print_residual(paths):
  from tune_grid import collect, build_grid, max_used_angle_bin, print_grid
  errs = build_grid(collect(paths))
  hi_a = max_used_angle_bin(errs)
  for d in ("L", "R"):
    print_grid(errs, d, hi_a)


def cmd_view(paths, file=None):
  map_l, map_r = load_map(file)
  if map_l is None:
    src = f"file {file}" if file else f"{PARAM_KEY} param"
    print(f"No learned map found ({src} empty or wrong size).")
    print("The learner writes one once it has driven with NrdrTuneLearner on, or seed one first.")
    return
  hi_a = max(_max_used_col(map_l, map_r), 4)
  for m, nm in ((map_l, "LEFT"), (map_r, "RIGHT")):
    print_map(m, nm, hi_a)
  nz = int(np.count_nonzero(map_l) + np.count_nonzero(map_r))
  peak = max(float(np.abs(map_l).max()), float(np.abs(map_r).max()))
  print(f"{nz} learned cells; peak |trim| = {peak:.3f} torque.\n")
  make_heatmap(map_l, map_r, hi_a)
  if paths:
    print("\n--- residual error in these logs (what the learner has NOT yet cancelled) ---")
    _print_residual(paths)


def cmd_seed(paths, file=None, gain=SEED_GAIN, steer_max=STEER_MAX):
  if not paths:
    print("seed needs at least one rlog. e.g. tune_learn_tool.py seed /data/media/0/realdata/*/rlog.zst")
    return
  from tune_grid import collect, build_grid, cell_stats, MIN_CELL
  errs = build_grid(collect(paths))
  cap = min(SEED_CAP, TRIM_HARD_FRAC * steer_max)
  map_l = np.zeros((N_SPEED, N_ANGLE), np.float32)
  map_r = np.zeros((N_SPEED, N_ANGLE), np.float32)
  for d, m in (("L", map_l), ("R", map_r)):
    for s in range(SEED_MIN_SPEED_BIN, N_SPEED):
      for a in range(N_ANGLE):
        st = cell_stats(errs[d][s][a])
        if st and st[0] >= MIN_CELL:
          # grid mean is direction-normalized: + = under-turn = needs more turn = + trim.
          m[s, a] = float(np.clip(gain * st[1], -cap, cap))
  save_map(map_l, map_r, file)
  nz = int(np.count_nonzero(map_l) + np.count_nonzero(map_r))
  where = f"file {file}" if file else f"{PARAM_KEY} param"
  print(f"seeded {nz} cells (gain {gain} torque/deg, cap +-{cap:.3f}) -> {where}.")
  print("warm start only -- turn NrdrTuneLearner on and the online learner refines from here.")
  print("run `tune_learn_tool.py view` to see what was seeded; reset on-device to undo.")


def main(argv):
  file = None
  gain = SEED_GAIN
  args = []
  i = 0
  while i < len(argv):
    if argv[i] == "--file" and i + 1 < len(argv):
      file = argv[i + 1]
      i += 2
    elif argv[i] == "--gain" and i + 1 < len(argv):
      try:
        gain = float(argv[i + 1])
      except ValueError:
        pass
      i += 2
    else:
      args.append(argv[i])
      i += 1
  if not args:
    print(__doc__)
    return
  cmd, paths = args[0], args[1:]
  if cmd == "view":
    cmd_view(paths, file)
  elif cmd == "seed":
    cmd_seed(paths, file, gain)
  else:
    print(f"unknown command '{cmd}'.\n")
    print(__doc__)


if __name__ == "__main__":
  main(sys.argv[1:])
