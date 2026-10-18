#!/usr/bin/env python3
"""Fit a car's column load model (vfn_eps_core load tuples: k0, k1, c, friction, bias, kroll), the Clarity recipe.

Target: the firmware's own output, in the counts the feedforward works in, taken from the EPS telemetry where the car
has a telemetry build, or rebuilt from the sent 0xE4 through the calibration's firmware law where it has none.
Frames: engaged, not pressed, moving (v > 1 m/s), and inside the driver-torque range where the firmware does not
yield (the scale word >= 240 on the Clarity; a |steeringTorque| cap elsewhere), so resting-hand turns are kept.
Regressors: k0*th + k1*th*v^2 + c*thd + fr*tanh(thd/2) + j*thdd + bias + kroll*roll*v^2, with th the offset-corrected
wheel angle, thd its 5-frame smoothed steeringRateDeg; the inertia term j is fitted but not deployed. The motion is
shifted by the lag (0-40 ms) that fits best. Scored held out by route.

Telemetry layouts (--source):
  clarity  bus 0: 0x6A2 = A, B, scale word, A030 (the output); 0x6A3 = m801, A348, R5, R6
  c020     bus 1: 0x6A0 w1 = P+D; R5 = s32(0x6A1 w0:w1) + 0x6A2 w0 (R5 - R6 plus R6); target P+D + KFF*R5/1024
  teg      bus 0: 0x6A3 w0 = P + D + KFF*R5/1024 exactly
  e4       no telemetry: target = the calibration's firmware law at the sent 0xE4 and the measured rate and angle

  python -m openpilot.nrdr.tools.lateral.eps_fit_column_load --source teg --calibration civic_teg_a010 '<route>/rlog*' ...
"""
import argparse
import bz2
import glob
import re
import struct

import numpy as np
import zstandard as zstd

from openpilot.cereal import log
from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.tools.lateral.eps_common import VEHICLE_PARAMETERS, calibration

NAMES = ('k0', 'k1', 'c', 'friction', 'j', 'bias', 'kroll')
s16 = lambda b, i: struct.unpack('>h', b[i:i + 2])[0]  # noqa: E731
u16 = lambda b, i: struct.unpack('>H', b[i:i + 2])[0]  # noqa: E731
BUS = {'clarity': 0, 'c020': 1, 'teg': 0, 'e4': None}


def seg(p):
  m = re.search(r'(?:rlog_|--)(\d+)(?:\.zst|\.bz2|/rlog)', p)
  return int(m.group(1)) if m else 0


def read_route(pattern, source, cal):
  st = {'lat': 0.0, 'e4': 0.0, 'off': 0.0, 'roll': 0.0, 'y': np.nan, 'sc': 256.0, 'fresh': 0.0}
  tel = {}
  rows = []
  bus = BUS[source]
  for p in sorted({f for g in pattern.split(',') for f in glob.glob(g)}, key=seg):
    raw = bz2.decompress(open(p, 'rb').read()) if p.endswith('.bz2') else zstd.ZstdDecompressor().stream_reader(open(p, 'rb').read()).read()
    try:
      for e in log.Event.read_multiple_bytes(raw):
        w = e.which()
        if w == 'sendcan':
          for m in e.sendcan:
            if m.address == 0xE4:
              st['e4'] = s16(m.dat, 0)
        elif w == 'can' and bus is not None:
          for m in e.can:
            if m.src == bus and 0x6A0 <= m.address <= 0x6A3 and len(m.dat) == 8:
              tel[m.address] = m.dat
              if source == 'clarity' and m.address == 0x6A2:
                st['sc'], st['y'], st['fresh'] = s16(m.dat, 4), s16(m.dat, 6), 1.0
              elif source == 'teg' and m.address == 0x6A3:
                st['y'], st['fresh'] = s16(m.dat, 0), 1.0
              elif source == 'c020' and m.address == 0x6A2 and 0x6A0 in tel and 0x6A1 in tel:
                r5 = s16(tel[0x6A1], 0) * 65536 + u16(tel[0x6A1], 2) + s16(m.dat, 0)
                st['y'], st['fresh'] = s16(tel[0x6A0], 2) + core.KFF * r5 / 1024.0, 1.0
        elif w in VEHICLE_PARAMETERS:
          st['off'], st['roll'] = getattr(e, w).angleOffsetDeg, getattr(e, w).roll
        elif w == 'carControl':
          st['lat'] = float(e.carControl.latActive)
        elif w == 'carState':
          c = e.carState
          rows.append((e.logMonoTime * 1e-9, c.vEgo, c.steeringAngleDeg - st['off'], c.steeringRateDeg, float(c.steeringPressed),
                       c.steeringTorque, st['roll'], st['lat'], st['e4'], st['y'], st['sc'], st['fresh']))
          st['fresh'] = 0.0
    except Exception:
      pass
  return dict(zip(('t', 'v', 'ang', 'rate', 'pr', 'tq', 'roll', 'lat', 'e4', 'y', 'sc', 'fresh'), np.array(rows, float).T, strict=True))


def target(d, source, cal):
  if source != 'e4':
    return d['y'], d['fresh'] > 0.5
  # rebuild: what the firmware law gives for the command it was sent, at the rate and angle the wheel had
  y = np.array([core.firmware_output(core.r5_from_output(-e4 / cal.e4_per_output, v, cal), r, a, cal=cal)
                for e4, v, r, a in zip(d['e4'], d['v'], d['rate'], d['ang'], strict=True)])
  return y, np.ones(len(y), bool)


def rows(d, y, ok, source, max_torque, shift):
  smooth = lambda x: np.convolve(x, np.ones(5) / 5, 'same')  # noqa: E731
  rate = smooth(d['rate'])
  acc = smooth(np.gradient(rate, d['t']))
  gate = d['sc'] >= 240 if source == 'clarity' else np.abs(d['tq']) < max_torque
  m = ok & (d['lat'] > 0.5) & (d['pr'] < 0.5) & (d['v'] > 1.0) & gate & np.isfinite(y)
  idx = np.flatnonzero(m)
  idx = idx[(idx + shift < len(m)) & (idx > 5)]
  th, thd, thdd = d['ang'][idx + shift], rate[idx + shift], acc[idx + shift]
  v, ro = d['v'][idx + shift], d['roll'][idx + shift]
  X = np.column_stack([th, th * v ** 2, thd, np.tanh(thd / 2.0), thdd, np.ones_like(th), ro * v ** 2])
  good = np.all(np.isfinite(X), 1)
  return X[good], y[idx][good]


def r2(X, y, coef):
  return 1 - np.sum((y - X @ coef) ** 2) / np.sum((y - y.mean()) ** 2)


def main():
  ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
  ap.add_argument('--source', required=True, choices=tuple(BUS))
  ap.add_argument('--calibration', required=True, help='calibration name, e.g. civic_teg_a010 (latcontrol_fw._OWN_CALIBRATIONS)')
  ap.add_argument('--max-torque', type=float, default=300.0, help='|steeringTorque| cap where there is no scale word')
  ap.add_argument('routes', nargs='+', help='rlog glob per route, comma-separated globs allowed (quote it)')
  a = ap.parse_args()
  cal, shipped_load = calibration(a.calibration)
  data = []
  for r in a.routes:
    d = read_route(r, a.source, cal)
    data.append((d, *target(d, a.source, cal)))
  best = None
  for shift in range(5):
    X, y = map(np.concatenate, zip(*[rows(d, y, ok, a.source, a.max_torque, shift) for d, y, ok in data], strict=True))
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    if best is None or r2(X, y, coef) > best[1]:
      best = (shift, r2(X, y, coef), coef, len(y))
  shift, fit_r2, coef, n = best
  print(f'{a.calibration} ({a.source}): {n / 100 / 60:.1f} min of frames, best motion lag {shift * 10} ms, R^2 {fit_r2:.3f}')
  print('  ' + '  '.join(f'{k} {c:+.5g}' for k, c in zip(NAMES, coef, strict=True)))
  k0, k1, c, fr, _, bias, kroll = coef
  print(f'load = ({k0:.4g}, {k1:.4g}, {c:.4g}, {fr:.4g}, {bias:.4g}, {kroll:.4g})  # (k0, k1, c, friction, bias, kroll); j not deployed')
  shipped = np.array([*shipped_load[:4], 0.0, *shipped_load[4:]])  # the j column is not deployed
  if len(data) > 1:
    print('held out by route: R^2 of this recipe / of the shipped load (in-sample if it was fitted on these routes)')
    for i in range(len(data)):
      tr = [rows(d, y, ok, a.source, a.max_torque, shift) for j, (d, y, ok) in enumerate(data) if j != i]
      Xtr, ytr = map(np.concatenate, zip(*tr, strict=True))
      ci = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
      Xte, yte = rows(*data[i], a.source, a.max_torque, shift)
      print(f'  route {i}: {r2(Xte, yte, ci):.3f} / {r2(Xte, yte, shipped):.3f}')


if __name__ == '__main__':
  main()
