#!/usr/bin/env python3
"""Does the car run the model's plan on time? Per drive, by turn phase.

The model publishes a plan for each camera frame: the car's yaw rate and speed at 33 future times. Their ratio is the
curvature the model expects the car to have at frame + T. The car's real curvature comes from its own yaw sensor
(VSA 0x94; carState.yawRate is not populated on these builds). For each turning frame the plan curve (T = 0.1-1.5 s)
is matched against the car's curvature shifted by s; s* is the shift with the least error:
  s* < 0  the car gets there EARLY (turns in before the model meant to: hugs the inside, unwinds early)
  s* > 0  the car gets there LATE
Phases: entry = planned curvature growing over the next 0.5 s, exit = shrinking, all = every turning frame at 5-12 m/s.
Frames within ~1 s of a takeover (steeringPressed) are left out. A steady curve has a flat plan, so time is barely
observable there: trust entry / exit / all, not the steady phase.

  python -m openpilot.nrdr.tools.lateral.eps_plan_timing <route dir or rlog glob> [...]

Konik/comma "files" lists are sorted as text (0, 1, 10, 11, 2, ...): name downloaded rlogs by the segment number in
their URL, not by list position, or the timeline is scrambled.
"""
import argparse
import glob
import os
import sys

import numpy as np
import zstandard as zstd

from openpilot.cereal import log
from openpilot.nrdr.tools.lateral.eps_common import DEFAULT_YAW_RATE_CALIBRATION, YAW_RATE_CALIBRATION, log_segment_number, yaw_rate_deg_s

T_IDX = 10.0 * (np.arange(33) / 32) ** 2
T_FIT = (T_IDX >= 0.1) & (T_IDX <= 1.5)
SHIFTS = np.arange(-0.4, 0.41, 0.01)
VSA_LATENCY = 0.017  # s, measured on the Clarity against rear-wheel-speed yaw; assumed for the others


def seg_number(path):
  return log_segment_number(path)


def rlog_paths(args):
  out = []
  for a in args:
    if os.path.isdir(a):
      out += glob.glob(os.path.join(a, '*rlog*')) + glob.glob(os.path.join(a, '*', 'rlog*'))
    else:
      out += glob.glob(a)
  return sorted({p for p in out if not p.endswith('.lock')}, key=seg_number)


def read(paths):
  M, CS, LAT, Y = [], [], [], {}
  fingerprint = None
  for p in paths:
    raw = open(p, 'rb').read()
    if p.endswith('.zst'):
      raw = zstd.ZstdDecompressor().stream_reader(raw).read()
    try:
      for e in log.Event.read_multiple_bytes(raw):
        w = e.which()
        t = e.logMonoTime * 1e-9
        if w == 'modelV2':
          m = e.modelV2
          vx = np.maximum(np.array(m.velocity.x), 1.0)
          M.append(np.r_[t, m.timestampEof * 1e-9, np.array(m.orientationRate.z) / vx])
        elif w == 'carState':
          CS.append((t, e.carState.vEgo, e.carState.steeringPressed))
        elif w == 'carControl':
          LAT.append((t, e.carControl.latActive))
        elif w == 'carParams' and fingerprint is None:
          fingerprint = str(e.carParams.carFingerprint)
        elif w == 'can':
          for c in e.can:
            if c.address == 0x94:
              Y.setdefault(c.src, []).append((t, (c.dat[0] << 2) | (c.dat[1] >> 6)))
    except Exception as ex:  # a truncated last segment
      print(f'  (partial read {p}: {ex})', file=sys.stderr)
  return [np.array(x, float) for x in (M, CS, LAT)], {k: np.array(v, float) for k, v in Y.items()}, fingerprint


def car_curvature(Y, CS, fingerprint):
  # scale and clockwise correction from opendbc's per-car calibration (GPS-checked); 0x94 is read on whichever bus
  # carries it (Clarity 0, Bosch 1). An uncalibrated car falls back to the nominal 0.25 deg/s per count.
  scale, _, right = YAW_RATE_CALIBRATION.get(str(fingerprint), DEFAULT_YAW_RATE_CALIBRATION)
  bus = max(Y, key=lambda b: len(Y[b]))
  y = Y[bus]
  v = np.interp(y[:, 0], CS[:, 0], CS[:, 1])
  stopped = v < 0.01
  zero = y[stopped, 1].mean() if stopped.sum() > 100 else 512.0  # the zero drifts by unit and temperature
  yaw = np.radians([yaw_rate_deg_s(c, scale, right) for c in y[:, 1] - zero])
  k = np.convolve(yaw / np.maximum(v, 0.5), np.ones(5) / 5, 'same')
  return y[:, 0] - VSA_LATENCY, k, bus, zero


def best_shift(tf, plan, yt, k):
  errs = [np.sum((np.interp(tf[:, None] + T_IDX[T_FIT][None, :] + s, yt, k) - plan[:, T_FIT]) ** 2) for s in SHIFTS]
  return float(SHIFTS[int(np.argmin(errs))])


def main():
  ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
  ap.add_argument('paths', nargs='+', help='route directory or rlog glob (quote globs)')
  paths = rlog_paths(ap.parse_args().paths)
  if not paths:
    sys.exit('no rlogs found')
  (M, CS, LAT), Y, fingerprint = read(paths)
  if len(M) < 100 or not Y:
    sys.exit('need modelV2 and the 0x94 yaw sensor in the logs')
  yt, k, bus, zero = car_curvature(Y, CS, fingerprint)
  tm, tf, plan = M[:, 0], M[:, 1], M[:, 2:]
  plan = plan * np.sign(np.corrcoef(np.interp(tf + 0.5, yt, k), plan[:, 10])[0, 1])
  v = np.interp(tm, CS[:, 0], CS[:, 1])
  engaged = np.interp(tm, LAT[:, 0], LAT[:, 1]) > 0.5
  near_takeover = np.interp(tm, CS[:, 0], (np.convolve(CS[:, 2], np.ones(200), 'same') > 0).astype(float)) > 0.5
  k_now = np.abs(plan[:, 0])
  k_ahead = np.abs(np.array([np.interp(0.5, T_IDX, row) for row in plan]))
  turning = engaged & ~near_takeover & (np.maximum(k_now, k_ahead) > 0.006)
  town = (v > 3) & (v < 12)
  phases = {
    'entry': turning & town & (k_ahead > 1.25 * k_now),
    'exit': turning & town & (k_ahead < 0.8 * k_now),
    'all turns 5-12 m/s': turning & (v > 5) & (v < 12),
  }
  minutes = (CS[-1, 0] - CS[0, 0]) / 60
  eng_min = np.mean(np.interp(CS[:, 0], LAT[:, 0], LAT[:, 1]) > 0.5) * minutes
  takeovers = int(np.sum(np.diff((CS[:, 2] > 0.5).astype(int)) == 1))
  where = os.path.dirname(paths[0]) or '.'
  print(f'{where}: {fingerprint}, {len(paths)} segments, {eng_min:.0f} engaged min, yaw bus {bus} (zero {zero:.1f}), '
        + f'model frame -> publish {np.median(tm - tf) * 1000:.0f} ms')
  print('car vs the model\'s plan, s (negative = early):')
  for name, m in phases.items():
    if m.sum() < 150:
      print(f'  {name:20s}       -   (only {m.sum()} frames)')
      continue
    print(f'  {name:20s} {best_shift(tf[m], plan[m], yt, k):+.2f}   ({m.sum()} frames)')
  print(f'reported steeringPressed rising edges: {takeovers} ({takeovers / max(eng_min, 0.1):.2f} per engaged minute; '
        + 'not verified driver interventions)')


if __name__ == '__main__':
  main()
