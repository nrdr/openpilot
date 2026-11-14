"""Build a provisional, offline SR curve from exported correction samples.

This is a versioned hypothesis builder, not a learner or automatic deployment.
It never reads/writes device Params and never installs its output.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
from statistics import median


ANGLE_EDGES = (0.0, 5.0, 15.0, 30.0, 50.0, 75.0, 100.0, 150.0, 250.0, 450.0)


def build_draft(rows, fingerprint, eps_firmware, min_seconds=5, min_routes=2):
  """Balance seconds, configuration, then route/direction; keep support per anchor."""
  if not fingerprint or not eps_firmware or 'unknown' in (fingerprint, eps_firmware):
    raise ValueError('an explicit known fingerprint and EPS identifier are required')
  if min_seconds < 1 or min_routes < 2:
    raise ValueError('draft requires positive occupied seconds and at least two routes')
  cells = defaultdict(list)
  rejected = Counter()
  models = set()
  for row in rows:
    if row['fingerprint'] != fingerprint or row.get('eps_firmware') != eps_firmware:
      rejected['other vehicle/EPS'] += 1
      continue
    if (row['phase'] != 'steady' or row['quality'] not in ('strict', 'relaxed')
        or str(row.get('command_output_available')).lower() != 'true'
        or str(row.get('safety_limited')).lower() != 'false'):
      rejected['not steady/unlimited command cohort'] += 1
      continue
    try:
      angle, ratio, timestamp, speed = (float(row[key]) for key in ('angle_deg', 'effective_ratio', 'timestamp', 'speed_mps'))
    except (KeyError, TypeError, ValueError):
      rejected['invalid values'] += 1
      continue
    if (not all(math.isfinite(v) for v in (angle, ratio, timestamp, speed)) or not 8 <= ratio <= 25
        or not 0 < angle < ANGLE_EDGES[-1] or speed <= 0):
      rejected['invalid values'] += 1
      continue
    if (row.get('direction') not in ('left', 'right') or not row.get('route_id')
        or not row.get('software_id') or row['software_id'] == 'unknown'):
      rejected['unknown route/direction/configuration'] += 1
      continue
    model = row.get('vehicle_model_id', 'unknown')
    if not model or model == 'unknown':
      rejected['unknown vehicle model'] += 1
      continue
    models.add(model)
    for lower, upper in zip(ANGLE_EDGES, ANGLE_EDGES[1:], strict=False):
      if lower <= angle < upper:
        key = (lower, upper, row['route_id'], row['direction'], row['software_id'], math.floor(timestamp))
        cells[key].append((angle, ratio, speed, row['quality']))
        break
  if len(models) != 1:
    raise ValueError('draft requires one known vehicle-model geometry; split inputs before fitting')
  by_config = defaultdict(list)
  for (lower, upper, route, direction, software, second), samples in cells.items():
    by_config[(lower, upper, route, direction, software)].append({
      'second': second, 'angle': median(s[0] for s in samples), 'ratio': median(s[1] for s in samples),
      'speed': median(s[2] for s in samples), 'strict_frames': sum(s[3] == 'strict' for s in samples),
    })
  by_route = defaultdict(list)
  for (lower, upper, route, direction, software), seconds in by_config.items():
    by_route[(lower, upper, route, direction)].append({
      'software': software, 'angle': median(s['angle'] for s in seconds),
      'ratio': median(s['ratio'] for s in seconds), 'speed': median(s['speed'] for s in seconds),
      'seconds': [s['second'] for s in seconds], 'strict_frames': sum(s['strict_frames'] for s in seconds),
    })
  bins = defaultdict(list)
  for (lower, upper, route, direction), configs in by_route.items():
    bins[(lower, upper)].append({
      'route': route, 'direction': direction, 'angle': median(s['angle'] for s in configs),
      'ratio': median(s['ratio'] for s in configs), 'speed_mps': median(s['speed'] for s in configs),
      'occupied_seconds': len({second for s in configs for second in s['seconds']}),
      'strict_frames': sum(s['strict_frames'] for s in configs),
      'configurations': [{key: value for key, value in config.items() if key != 'seconds'} |
                         {'occupied_seconds': len(config['seconds'])} for config in configs],
    })
  anchors, coverage = [], []
  for (lower, upper), observations in sorted(bins.items()):
    routes = {o['route'] for o in observations}
    paired = {o['route'] for o in observations if o['direction'] == 'left'} & {
      o['route'] for o in observations if o['direction'] == 'right'}
    seconds = sum(o['occupied_seconds'] for o in observations)
    ratios = [o['ratio'] for o in observations]
    ratio = median(ratios)
    spread = (max(ratios) / min(ratios) - 1) * 100
    # These modest thresholds admit an explicitly provisional hypothesis, not
    # calibrated anchors. Retain rejected bins in the audit rather than filling them.
    eligible = seconds >= min_seconds and len(routes) >= min_routes and len(paired) >= 1 and spread <= 15
    evidence = {'angle_bin': [lower, upper], 'occupied_seconds': seconds,
                'routes': len(routes), 'paired_routes': len(paired), 'route_direction_spread_percent': spread,
                'observations': observations, 'used': eligible}
    coverage.append(evidence)
    if eligible:
      anchors.append({'angle_deg': round(median(o['angle'] for o in observations), 3),
                      'ratio': round(ratio, 4), 'evidence': 'provisional-command-conditioned', **evidence})
  if len(anchors) < 2:
    raise ValueError('fewer than two provisional anchors; do not manufacture a curve')
  if anchors[0]['angle_deg'] <= 0 or any(a['angle_deg'] >= b['angle_deg'] for a, b in zip(anchors, anchors[1:], strict=False)):
    raise ValueError('rounded draft angles must be positive and strictly increasing')
  if any(a['angle_deg'] / a['ratio'] >= b['angle_deg'] / b['ratio'] for a, b in zip(anchors, anchors[1:], strict=False)):
    raise ValueError('draft would reverse the angle-to-curvature mapping; review the anchors')
  center = {'angle_deg': 0.0, 'ratio': anchors[0]['ratio'], 'evidence': 'held-nearest-anchor-not-measured-at-zero'}
  return {'schema_version': 1, 'status': 'provisional-offline-draft-not-road-validated',
          'fingerprint': fingerprint, 'eps_firmware': eps_firmware, 'vehicle_model_id': next(iter(models)),
          'ratio_domain': 'vehicle-model', 'interpolation': 'piecewise-linear',
          'outside_range': 'hold-nearest-anchor; unmeasured extrapolation, not firmware-derived',
          'minimum_seconds': min_seconds, 'minimum_routes': min_routes,
          'angles_deg': [center['angle_deg'], *(a['angle_deg'] for a in anchors)],
          'ratios': [center['ratio'], *(a['ratio'] for a in anchors)],
          'anchors': [center, *anchors], 'coverage': coverage, 'rejected_samples': dict(rejected),
          'limitations': ['Controller-conditioned observations are not independent rack measurements.',
                          'Model-normalized ratio depends on learned roll, stiffness and offsets.',
                          'No speed correction or new actuator-delay estimate is fitted.',
                          'No calibration guarantee at unmeasured angles; no automatic deployment.']}


def main(argv=None):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('samples', type=Path, help='sr_samples.csv.gz from the correction analyzer')
  parser.add_argument('--fingerprint', required=True)
  parser.add_argument('--eps-firmware', required=True)
  parser.add_argument('--output', type=Path, required=True, help='new draft JSON; existing files are never overwritten')
  args = parser.parse_args(argv)
  with gzip.open(args.samples, 'rt', newline='', encoding='utf-8') as stream:
    draft = build_draft(csv.DictReader(stream), args.fingerprint, args.eps_firmware)
  draft['source_sha256'] = hashlib.sha256(args.samples.read_bytes()).hexdigest()
  with args.output.open('x', encoding='utf-8') as stream:
    json.dump(draft, stream, indent=2, allow_nan=False)
    stream.write('\n')
  print(json.dumps({key: draft[key] for key in ('angles_deg', 'ratios', 'source_sha256')}, indent=2))
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
