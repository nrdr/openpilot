#!/usr/bin/env python3
"""Honda VSA yaw (0x94 KINEMATICS) scale against GPS heading, from straight-to-straight pairs.

Pairs of GPS fixes 10-40 s apart, both on a straight (|yaw| <= ~0.25 deg/s over 2 s), so GPS bearing lag and
sideslip cancel at the ends; the heading change between them is fitted against the integral of the raw counts.
The zero is the mean count at standstill on each drive. Fits one scale plus a clockwise (right-turn) correction
ramped in over RIGHT_LOSS_BP counts, the form eps_common.YAW_RATE_CALIBRATION decodes with.

  python -m openpilot.nrdr.tools.lateral.eps_fit_yaw_scale --bus 1 '<route dir>/rlog*' ['<another route>' ...]
"""
import argparse
import bz2
import glob
import re

import numpy as np
import zstandard as zstd

from openpilot.cereal import log
from openpilot.nrdr.tools.lateral.eps_common import RIGHT_LOSS_BP

GPS_LAG = 0.4  # s, GPS bearing behind the car


def seg(p):
  m = re.search(r'(?:rlog_|--)(\d+)(?:\.zst|\.bz2|/rlog)', p)
  return int(m.group(1)) if m else 0


def read_route(pattern, bus):
  Y, G, V = [], [], []
  for p in sorted(glob.glob(pattern), key=seg):
    raw = bz2.decompress(open(p, 'rb').read()) if p.endswith('.bz2') else zstd.ZstdDecompressor().stream_reader(open(p, 'rb').read()).read()
    try:
      for e in log.Event.read_multiple_bytes(raw):
        w, t = e.which(), e.logMonoTime * 1e-9
        if w == 'can':
          for m in e.can:
            if m.src == bus and m.address == 0x94:
              Y.append((t, (m.dat[0] << 2) | (m.dat[1] >> 6)))
        elif w in ('gpsLocation', 'gpsLocationExternal'):
          g = getattr(e, w)
          if g.hasFix or (g.flags & 1):  # logs before hasFix mark a fix in flags
            G.append((t, g.bearingDeg, g.speed, g.bearingAccuracyDeg))
        elif w == 'carState':
          V.append((t, e.carState.vEgo))
    except Exception:
      pass
  return [np.array(x, float).reshape(-1, n) for x, n in ((Y, 2), (G, 4), (V, 2))]


def pairs(Y, G, V):
  Y, G, V = Y[np.argsort(Y[:, 0])], G[np.argsort(G[:, 0])], V[np.argsort(V[:, 0])]
  t = Y[:, 0]
  v = np.interp(t, V[:, 0], V[:, 1])
  stopped = v < 0.01
  zero = float(np.mean(Y[stopped, 1])) if stopped.sum() > 300 else 512.0
  k = Y[:, 1] - zero
  dt = np.r_[0.0, np.diff(t)]
  ramp = np.clip((k - RIGHT_LOSS_BP[0]) / (RIGHT_LOSS_BP[1] - RIGHT_LOSS_BP[0]), 0.0, 1.0)
  ck, cr = np.cumsum(k * dt), np.cumsum(ramp * dt)
  smooth = np.convolve(k, np.ones(200) / 200, 'same')
  gs = G[(G[:, 2] > 5) & (G[:, 3] < 3)]
  gs = gs[np.abs(np.interp(gs[:, 0] - GPS_LAG, t, smooth)) <= 1.0]
  rows = []
  for i in range(len(gs)):
    for j in range(i + 1, len(gs)):
      T = gs[j, 0] - gs[i, 0]
      if T < 10:
        continue
      if T > 40:
        break
      ends = [gs[i, 0] - GPS_LAG, gs[j, 0] - GPS_LAG]
      dk, dr = np.diff(np.interp(ends, t, ck))[0], np.diff(np.interp(ends, t, cr))[0]
      dh = gs[j, 1] - gs[i, 1]
      dh += 360 * np.round((0.245 * dk - dh) / 360)
      if abs(dh) >= 30:
        rows.append((dh, dk, dr))
  return zero, np.array(rows)


def main():
  ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
  ap.add_argument('--bus', type=int, required=True, help='bus 0x94 is read on (Clarity 0, Bosch 1)')
  ap.add_argument('routes', nargs='+', help='rlog glob per route (quote it)')
  a = ap.parse_args()
  per, allr = [], []
  for r in a.routes:
    zero, R = pairs(*read_route(r, a.bus))
    if len(R) < 10:
      print(f'{r}: {len(R)} pairs, skipped')
      continue
    sc = np.linalg.lstsq(R[:, 1:2], R[:, 0], rcond=None)[0][0]
    print(f'{r}: zero {zero:.2f}, {len(R)} pairs, scale {sc:.4f} deg/s per count')
    per.append(sc)
    allr.append(R)
  R = np.vstack(allr)
  one = np.linalg.lstsq(R[:, 1:2], R[:, 0], rcond=None)[0]
  two = np.linalg.lstsq(R[:, 1:3], R[:, 0], rcond=None)[0]
  def rms(c, A):
    return np.sqrt(np.mean((R[:, 0] - A @ c) ** 2))
  right, left = R[:, 0] > 0, R[:, 0] < 0
  print(f'\n{len(R)} pairs: one scale {one[0]:.4f} (rms {rms(one, R[:, 1:2]):.2f} deg); ' +
        f'scale {two[0]:.4f} + clockwise {two[1]:.3f} deg/s (rms {rms(two, R[:, 1:3]):.2f} deg)')
  for name, m in (('right-dominant', right), ('left-dominant', left)):
    if m.sum() >= 10:
      print(f'  {name}: scale {np.linalg.lstsq(R[m, 1:2], R[m, 0], rcond=None)[0][0]:.4f} ({m.sum()} pairs)')
  if len(per) > 1:
    print(f'  per-route scales {np.round(per, 4)}')


if __name__ == '__main__':
  main()
