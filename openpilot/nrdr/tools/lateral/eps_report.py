#!/usr/bin/env python3
"""Per-drive lateral report for a Honda on the Firmware Controller, measured against the car's own yaw sensor (0x94).

  python -m openpilot.nrdr.tools.lateral.eps_report <rlog.zst | route dir> ...

Everything is judged in true units: car curvature = VSA yaw / vEgo (eps_common.YAW_RATE_CALIBRATION, zero learned at
standstill, clockwise under-read corrected, 0x94 on whichever bus carries it), 17 ms latency, decoded straight from CAN.
Several routes in one folder are read route by route, each in segment order. Sections:
  yaw sources   VSA zero on straights; deviceMotion / livePose yaw (the comma's estimate) scale and lag against the VSA
  map           car curvature vs what the car's rack map (honda_rack_map, yaw-measured or spec-predicted) says
                the ACTUAL wheel angle gives (1.000 = exact); skipped otherwise
  tracking      actual wheel angle vs the controller's target
  delivery      car curvature vs controlsd's output curvature (lag-aligned); = map x tracking
  timing        car curvature lag behind the model action -> the delay the model should be told, vs its profile's schedule
  left/right    map and tracking by turn direction
  turns         engaged turns past 60 deg, ranked by how far the car overshot the requested curvature
Slopes are robust regressions WITH an intercept, so an angle offset or road crown does not bias them.
Only engaged, hands-off, |aEgo| < 2 frames count, except in the yaw-source section.
"""
import argparse
import glob
import math
import os
import re
import sys

import numpy as np
import zstandard as zstd

from openpilot.cereal import log
from openpilot.nrdr.features.lateral.honda_vgr import normalize_honda_eps_firmware
from openpilot.nrdr.tools.lateral.eps_common import (DEFAULT_YAW_RATE_CALIBRATION, DEVICE_POSE, RIGHT_LOSS_BP, VEHICLE_PARAMETERS,
                                                     YAW_RATE_CALIBRATION, firmware_profile, prediction_schedule, rack_map)

VSA_ADDR, VSA_LATENCY = 0x94, 0.017
PIPELINE_OFFSET = 0.038  # logged action -> on-time execution (publish + smoothing), see the delay schedule
WHEEL_TO_YAW_LAG = ([3.75, 7.0, 12.0, 20.0, 30.0], [0.08, 0.06, 0.06, 0.08, 0.10])  # s, measured
SPEED_BANDS = ((2.5, 5), (5, 9), (9, 15), (15, 25), (25, 40))
ANGLE_BANDS = ((0, 20), (20, 90), (90, 500))
ROUTE_GAP_S = 100.0
LAGS = np.arange(0.0, 0.8, 0.01)
FRAMES_PER_MIN = 6000
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def profile_for(info):
  return firmware_profile(str(info.get('fingerprint')), info.get('eps_fw'))


def shipped_delay_schedule(info):
  """The schedule told to the model, or None where the model is told the live (lagd) or manual delay."""
  schedule = prediction_schedule(profile_for(info))
  return [list(x) for x in schedule] if schedule is not None else None


def segment_number(path):
  m = re.search(r'rlog_(\d+)\.(?:zst|bz2)$', path)    # flat downloads: rlog_<segment>.zst
  if m:
    return int(m.group(1))
  nums = re.findall(r'--(\d+)(?=/|$)', os.path.dirname(path) + '/')
  return int(nums[-1]) if nums else 0


def rlog_files(paths):
  files = []
  for p in paths:
    files += sorted(glob.glob(os.path.join(p, '**', 'rlog*'), recursive=True)) if os.path.isdir(p) else [p]
  # route by route, each in segment order: '<route>--<n>/rlog*' folders of several routes must not interleave
  route = lambda f: re.sub(r'--\d+$', '', os.path.basename(os.path.dirname(f)))  # noqa: E731
  return sorted(set(files), key=lambda f: (os.path.dirname(os.path.dirname(f)), route(f), segment_number(f), f))


def read(files):
  R = {k: [] for k in ('vsa', 'cs', 'cc', 'ctl', 'lp', 'pose', 'model')}
  vsa = {}
  info = {}
  # Each route's logMonoTime restarts at its device boot, so a later route can run backwards from an earlier one.
  # Shift each route to start ROUTE_GAP_S after the previous one ended, so time stays increasing across routes.
  route_of = lambda f: re.sub(r'--\d+$', '', os.path.basename(os.path.dirname(f)))  # noqa: E731
  prev_route, offset, last_t, pending = None, 0.0, None, False
  for f in files:
    if route_of(f) != prev_route:
      prev_route, pending = route_of(f), last_t is not None
    raw = open(f, 'rb').read()
    if f.endswith('.zst'):
      raw = zstd.ZstdDecompressor().stream_reader(raw).read()
    try:
      for e in log.Event.read_multiple_bytes(raw):
        w = e.which()
        t = e.logMonoTime * 1e-9
        if pending:
          offset, pending = last_t + ROUTE_GAP_S - t, False
        t += offset
        last_t = t if last_t is None else max(last_t, t)
        if w == 'can':
          for m in e.can:
            if m.address == VSA_ADDR:
              vsa.setdefault(m.src, []).append((t, (m.dat[0] << 2) | (m.dat[1] >> 6)))
        elif w == 'carState':
          c = e.carState
          R['cs'].append((t, c.vEgo, c.aEgo, c.steeringAngleDeg, c.steeringRateDeg, c.steeringTorque, c.steeringPressed,
                          c.leftBlinker or c.rightBlinker))
        elif w == 'carControl':
          R['cc'].append((t, e.carControl.latActive))
        elif w == 'controlsState':
          lcs = e.controlsState.lateralControlState
          des = lcs.pidState.steeringAngleDesiredDeg if lcs.which() == 'pidState' else math.nan
          R['ctl'].append((t, e.controlsState.desiredCurvature, des))
        elif w in VEHICLE_PARAMETERS:
          R['lp'].append((t, getattr(e, w).angleOffsetDeg, getattr(e, w).roll))
        elif w in DEVICE_POSE:
          R['pose'].append((t, getattr(e, w).angularVelocityDevice.z))
        elif w == 'modelV2':
          R['model'].append((t, e.modelV2.action.desiredCurvature))
        elif w == 'initData':
          info.setdefault('branch', e.initData.gitBranch)
          info.setdefault('commit', e.initData.gitCommit[:10])
        elif w == 'carParams':
          info.update(fingerprint=e.carParams.carFingerprint, wheelbase=e.carParams.wheelbase, steer_ratio=e.carParams.steerRatio)
          eps = [normalize_honda_eps_firmware(f.fwVersion) for f in e.carParams.carFw if str(f.ecu) == 'eps']
          if eps:
            info['eps_fw'] = eps[0]
    except Exception as ex:  # a truncated last segment
      print(f'  (partial read {f}: {ex})', file=sys.stderr)
  if vsa:
    info['vsa_bus'] = max(vsa, key=lambda b: len(vsa[b]))
    R['vsa'] = vsa[info['vsa_bus']]
  return {k: np.array(v, dtype=float) for k, v in R.items()}, info


def build(R, info):
  cs = R['cs']
  t = cs[:, 0]

  def at(arr, col, dt=0.0):
    return np.interp(t + dt, arr[:, 0], arr[:, col]) if len(arr) else np.full(len(t), np.nan)

  s = {'t': t, 'v': cs[:, 1], 'a': cs[:, 2], 'ang': cs[:, 3], 'rate': cs[:, 4], 'tq': cs[:, 5], 'pr': cs[:, 6], 'bl': cs[:, 7]}
  s['lat'] = at(R['cc'], 1) if len(R['cc']) else np.zeros(len(t))
  s['dc'], s['des'] = at(R['ctl'], 1), at(R['ctl'], 2)
  s['off'], s['roll'] = at(R['lp'], 1), at(R['lp'], 2)
  s['vsa_raw'] = at(R['vsa'], 1, VSA_LATENCY)
  stopped = s['v'] < 0.01
  vsa_deg_s, vsa_zero, vsa_right_loss = YAW_RATE_CALIBRATION.get(str(info.get('fingerprint')), DEFAULT_YAW_RATE_CALIBRATION)
  s['vsa_zero'] = float(np.mean(s['vsa_raw'][stopped])) if stopped.sum() > 200 else vsa_zero  # true yaw is 0 when stopped
  counts = s['vsa_raw'] - s['vsa_zero']
  right_loss = vsa_right_loss * np.clip((counts - RIGHT_LOSS_BP[0]) / (RIGHT_LOSS_BP[1] - RIGHT_LOSS_BP[0]), 0.0, 1.0)
  s['yaw'] = np.radians(counts * vsa_deg_s + right_loss)  # rad/s, RIGHT-positive like openpilot curvature (yaw_rate.yaw_rate_deg_s)
  s['k'] = np.convolve(s['yaw'], np.ones(10) / 10, 'same') / np.maximum(s['v'], 0.1)
  s['gyro'] = at(R['pose'], 1)

  rack = rack_map(str(info.get('fingerprint')), info.get('eps_fw'), info.get('steer_ratio') or 15.0)
  lag_frames = np.round(np.interp(s['v'], *WHEEL_TO_YAW_LAG) / 0.01).astype(int)
  s['a_true'] = s['ang'] - s['off']
  a_lagged = s['a_true'][np.clip(np.arange(len(t)) - lag_frames, 0, len(t) - 1)]
  # the map gives VehicleModel's sign (left-positive); the report works right-positive, as openpilot curvature
  s['k_map'] = (np.array([-rack.curvature_from_angle(a, v, r) for a, v, r in zip(a_lagged, s['v'], s['roll'], strict=True)])
                if rack is not None else None)
  s['map_name'] = rack.name if rack is not None else None

  ok = (s['lat'] > 0.5) & (s['pr'] < 0.5) & (np.abs(s['tq']) < 400) & (np.abs(s['a']) < 2) & np.isfinite(s['k'] + s['dc'])
  s['ok'] = ok & (np.convolve(~ok, np.ones(100), 'same') == 0)  # 1 s clear of any disengagement or press
  return s


def rob(x, y):
  if len(x) < 50 or np.ptp(x) == 0:
    return math.nan
  a, b = np.polyfit(x, y, 1)
  for _ in range(6):
    r = y - (a * x + b)
    w = 1 / np.maximum(np.abs(r) / (2 * np.median(np.abs(r)) + 1e-12), 1)
    a, b = np.polyfit(x, y, 1, w=np.sqrt(w))
  return a


def best_lag(t, y, ts, src, idx, lags=LAGS):
  errs = []
  for lag in lags:
    p = np.interp(t[idx] - lag, ts, src)
    gain = np.sum(p * y[idx]) / max(np.sum(p * p), 1e-12)
    errs.append(np.sqrt(np.mean((y[idx] - gain * p) ** 2)))
  return float(lags[int(np.argmin(errs))])


def smooth(x, n=50):
  return np.convolve(x, np.ones(n) / n, 'same')


def cell(value, frames):
  return f'{value:8.3f} ({frames / FRAMES_PER_MIN:3.1f}m)'


def cell_table(title, s, fn, min_frames=300):
  print(f'\n{title}')
  print('  m/s      ' + ''.join(f'{f"{lo}-{hi} deg":>14s}' for lo, hi in ANGLE_BANDS))
  A = np.abs(s['a_true'])
  for vlo, vhi in SPEED_BANDS:
    row = []
    for alo, ahi in ANGLE_BANDS:
      m = s['ok'] & (s['v'] >= vlo) & (s['v'] < vhi) & (A >= alo) & (A < ahi)
      row.append(cell(fn(m), m.sum()) if m.sum() >= min_frames else '-')
    print(f'  {vlo:4.1f}-{vhi:<4.0f}' + ''.join(f'{c:>14s}' for c in row))


def yaw_sources(s):
  t = s['t']
  print('\nyaw sources')
  straight = (np.abs(s['a_true']) < 1.0) & (np.abs(s['rate']) < 2) & (s['v'] > 8)
  if straight.sum() > 500:
    print(f"  VSA zero: {s['vsa_zero']:.2f} counts at standstill (used), {np.median(s['vsa_raw'][straight]):.2f} on straights")
  turning = np.abs(np.degrees(s['yaw'])) > 3
  if not (np.isfinite(s['gyro']).all() and turning.sum() > 500):
    return
  lag = best_lag(t, s['gyro'], t, s['yaw'], np.flatnonzero(turning)[::3], np.arange(-0.1, 0.2, 0.005))
  ref = np.interp(t - lag, t, s['yaw'])
  turning &= np.abs(np.degrees(ref)) > 3
  with np.errstate(divide='ignore', invalid='ignore'):
    ratio = s['gyro'] / ref
  for name, m in (('below 8 m/s', turning & (s['v'] < 8)), ('8 m/s and up', turning & (s['v'] >= 8))):
    if m.sum() > 300:
      med, p10, mins = np.median(ratio[m]), np.percentile(ratio[m], 10), m.sum() / FRAMES_PER_MIN
      print(f'  device yaw / VSA, {name}: median {med:.3f}, p10 {p10:.3f}  ({mins:.1f} min)')
  print(f'  device yaw runs {1000 * lag:+.0f} ms behind the VSA')


def delivery(s):
  t = s['t']
  A = np.abs(s['a_true'])
  print('\ndelivery: car curvature / controlsd output, lag-aligned per band   (= map x tracking)')
  for vlo, vhi in SPEED_BANDS:
    m = s['ok'] & (s['v'] >= vlo) & (s['v'] < vhi) & (np.abs(s['dc']) > (0.001 if vlo >= 15 else 0.003))
    if m.sum() < 300:
      continue
    lag = best_lag(t, s['k'], t, s['dc'], np.flatnonzero(m)[::3])
    dc_lagged = np.interp(t - lag, t, s['dc'])
    row = []
    for alo, ahi in ANGLE_BANDS:
      mm = m & (A >= alo) & (A < ahi)
      row.append(cell(rob(dc_lagged[mm], s['k'][mm]), mm.sum()) if mm.sum() >= 300 else '-')
    print(f'  {vlo:4.1f}-{vhi:<4.0f}' + ''.join(f'{c:>14s}' for c in row) + f'   lag {lag:.2f} s')


def timing(s, model, info):
  schedule = shipped_delay_schedule(info)
  bp, vals = schedule if schedule is not None else (None, None)
  told = 'its profile\'s schedule' if schedule is not None else 'the live (lagd) or manual delay: no schedule to compare'
  print(f'\ntiming: car curvature behind the model action   (on-time delay = lag - {PIPELINE_OFFSET:.3f}; told {told})')
  if len(model) < 100:
    return
  for vlo, vhi in SPEED_BANDS:
    m = s['ok'] & (s['bl'] < .5) & (s['v'] >= vlo) & (s['v'] < vhi) & (np.abs(s['k']) > (0.001 if vlo >= 15 else 0.004))
    if m.sum() < 600:
      continue
    on_time = best_lag(s['t'], s['k'], model[:, 0], model[:, 1], np.flatnonzero(m)[::5]) - PIPELINE_OFFSET
    note = '   (includes lane centering)' if vlo >= 15 else ''
    if bp is None:
      print(f'  {vlo:4.1f}-{vhi:<4.0f} on-time {on_time:.2f} s ({m.sum() / FRAMES_PER_MIN:.1f} min){note}')
      continue
    sched = float(np.interp((vlo + vhi) / 2, bp, vals))
    verdict = f"car {'late' if on_time > sched else 'early'} {abs(on_time - sched) * 1000:.0f} ms"
    print(f'  {vlo:4.1f}-{vhi:<4.0f} on-time {on_time:.2f} s, schedule {sched:.2f} s: {verdict} ({m.sum() / FRAMES_PER_MIN:.1f} min){note}')


def left_right(s, des_s, ang_s):
  print('\nleft/right, 45+ deg, 3-15 m/s   (the map uses their mean)')
  for name, sign in (('left ', 1), ('right', -1)):
    m = s['ok'] & (s['v'] >= 3) & (s['v'] < 15) & (s['a_true'] * sign > 45)
    if m.sum() > 300:
      tr = rob(des_s[m] - s['off'][m], ang_s[m] - s['off'][m])
      mp = f"map {rob(s['k_map'][m], s['k'][m]):.3f}   " if s['k_map'] is not None else ''
      print(f'  {name}: {mp}tracking {tr:.3f}  ({m.sum() / FRAMES_PER_MIN:.1f} min)')


def turns(s):
  t, A = s['t'], s['a_true']
  print('\nturns past 60 deg, engaged: car curvature peak vs requested peak')
  big = (s['lat'] > .5) & (np.abs(A) > 60) & (s['v'] > 2.5)
  edges = np.flatnonzero(np.diff(np.r_[0, big.astype(int), 0]))
  found = []
  for i0, i1 in zip(edges[::2], edges[1::2], strict=True):
    if i1 - i0 < 50:
      continue
    w = slice(max(i0 - 100, 0), min(i1 + 100, len(t)))
    j = i0 + int(np.argmax(np.abs(A[i0:i1])))
    asked, got = np.max(np.abs(s['dc'][w])), np.max(np.abs(s['k'][w]))
    found.append((got / max(asked, 1e-6) - 1, t[j] - t[0], s['v'][j], 'L' if A[j] > 0 else 'R', asked, got,
                  np.max(np.abs(s['des'][w] - s['off'][w])), np.max(np.abs(A[w])), np.mean(s['pr'][w] > .5)))
  if not found:
    return
  print(f'  {len(found)} turns, median overshoot {np.median([x[0] for x in found]) * 100:+.1f}%')
  print('    t (s)   v   dir  asked k   car k   over   target deg  actual deg  pressed')
  for over, tj, v, side, asked, got, tgt, act, pressed in sorted(found, reverse=True)[:12]:
    print(f'  {tj:7.1f} {v:4.1f}  {side}   {asked:.4f}   {got:.4f}  {over * 100:+5.1f}%   {tgt:7.1f}     {act:7.1f}    {pressed * 100:3.0f}%')


def report(s, R, info):
  mins, engaged, usable = (s['t'][-1] - s['t'][0]) / 60, np.mean(s['lat'] > .5) * 100, np.mean(s['ok']) * 100
  profile = profile_for(info)
  calibration = profile.calibration if profile else 'no Firmware Controller calibration'
  route = f"{info.get('branch', '?')} @ {info.get('commit', '?')}  {info.get('fingerprint', '?')}  {info.get('eps_fw', '?')}  {calibration}"
  print(f'route: {route}   {mins:.1f} min, engaged {engaged:.0f}%, usable {usable:.0f}%')
  if len(R['vsa']) < 1000:
    print('no 0x94 frames: CAN not logged')
    return
  yaw_sources(s)
  if s['k_map'] is not None:
    cell_table(f"map: car curvature / its {s['map_name']}(actual wheel angle)   (1.000 = the shipped map is exact)", s,
               lambda m: rob(s['k_map'][m], s['k'][m]))
  else:
    print('\nmap: no rack map for this car in this tree (fit one with eps_fit_rack_map)')
  # smoothed first: the target's frame-to-frame jitter would otherwise attenuate the slope at small angles
  des_s, ang_s = smooth(s['des']), smooth(s['ang'])
  cell_table('tracking: actual wheel angle / controller target (0.5 s smoothed)', s,
             lambda m: rob(des_s[m] - s['off'][m], ang_s[m] - s['off'][m]))
  cell_table('tracking: RMS angle error, deg', s, lambda m: float(np.sqrt(np.mean((s['ang'][m] - s['des'][m]) ** 2))))
  delivery(s)
  timing(s, R['model'], info)
  left_right(s, des_s, ang_s)
  turns(s)


def main():
  ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
  ap.add_argument('paths', nargs='+', help='rlog files or route/segment directories')
  files = rlog_files(ap.parse_args().paths)
  if not files:
    sys.exit('no rlogs found')
  R, info = read(files)
  if len(R['cs']) < 1000:
    sys.exit('too little carState to report on')
  report(build(R, info), R, info)


if __name__ == '__main__':
  main()
