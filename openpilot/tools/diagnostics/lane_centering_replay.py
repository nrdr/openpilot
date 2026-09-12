#!/usr/bin/env python3
"""Compare a lane-centering candidate with the installed controller on local logs.

This does not publish messages, write parameters, or command actuators. On a
comma device it requires fresh off-road/no-output state throughout processing.
Forced lateral availability is only an offline sensitivity check, not a driving
simulation or evidence that a candidate is safe to deploy.

Legacy sidecar timing is joined by exact modelMonoTime, never arrival order.
Using an invalid sidecar Event requires --repair-timing-transport: this is an
explicit offline repair of the broken transport, not recorded live behavior.
"""
import argparse
from collections import Counter
import importlib.util
import inspect
import json
from pathlib import Path
import time
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.lane_centering import LaneCenteringController, lane_centering_action_time as installed_action_time
from openpilot.tools.lib.logreader import LogReader


INSTALLED_TIMING_CONTRACT = len(inspect.signature(installed_action_time).parameters)
if INSTALLED_TIMING_CONTRACT not in (1, 3):
  raise RuntimeError('Unknown installed lane-centering timing helper contract')


def offroad_guard():
  params = Params()
  sm = messaging.SubMaster(['deviceState', 'pandaStates'])
  for _ in range(30):
    sm.update(100)
    if sm.all_alive() and sm.all_valid():
      break

  def check():
    sm.update(0)
    # This diagnostic polls slowly, so subscriber frequency is not a producer
    # health measurement. Still require both fresh messages and valid contents.
    assert sm.all_alive() and sm.all_valid(), 'Fresh device and Panda state required'
    assert params.get_bool('IsOffroad') and not sm['deviceState'].started, 'Device is not off-road'
    assert len(sm['pandaStates']) > 0, 'Panda state is missing'
    assert all(not p.ignitionLine and not p.ignitionCan and str(p.safetyModel) == 'noOutput'
               for p in sm['pandaStates']), 'Ignition or output-capable safety mode detected'
  check()
  return check


def load_candidate(path):
  spec = importlib.util.spec_from_file_location('lane_centering_candidate', path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module.LaneCenteringController


def index_recorded_timing(events, guard):
  """Index even invalid producer Events; validity is enforced during selection."""
  timing_by_model = {}
  stats = Counter()
  last_guard = time.monotonic()
  for event in events:
    if time.monotonic() - last_guard >= 0.5:
      guard()
      last_guard = time.monotonic()
    if event.which() != 'modelDataV2SP':
      continue
    stats['records'] += 1
    stats['valid_events' if event.valid else 'invalid_events'] += 1
    timing = event.modelDataV2SP
    frame = int(timing.modelMonoTime)
    if frame <= 0:
      stats['missing_identity'] += 1
      continue
    value = float(timing.lateralActionTime)
    previous = timing_by_model.get(frame)
    record = (value, bool(event.valid))
    if frame in timing_by_model and previous != record:
      # Conflicting metadata cannot be resolved by choosing the last arrival.
      timing_by_model[frame] = None
      stats['conflicting_records'] += 1
    elif frame not in timing_by_model:
      timing_by_model[frame] = record
  guard()
  return timing_by_model, stats


def select_action_time(model, frame, timing_by_model, timing_record_count, *, repair_transport=False, assumed=None):
  """Return raw timing and its provenance; the candidate enforces its envelope."""
  try:
    atomic_time = float(getattr(model.action, 'lateralActionTime', 0.0))
  except (AttributeError, OverflowError, TypeError, ValueError):
    return None, 'malformed_atomic_timing'
  if atomic_time != 0.0:
    # Invalid or unsupported atomic values must fail closed, not use a fallback.
    return atomic_time, 'modelV2.action'
  if frame in timing_by_model:
    record = timing_by_model[frame]
    if record is None:
      return None, 'conflicting_recorded_timing'
    action_time, valid = record
    if valid:
      return action_time, 'recorded_exact_sidecar'
    if repair_transport:
      return action_time, 'offline_transport_repair_invalid_sidecar'
    return None, 'invalid_sidecar_event'
  if timing_record_count:
    return None, 'no_exact_recorded_timing'
  if assumed is not None:
    return assumed, 'assumed_legacy_sensitivity'
  return None, 'timing_unavailable'


def select_installed_action_time(frame, timing_by_model, model=None):
  """Exercise the installed timing contract without repair or assumed timing."""
  if INSTALLED_TIMING_CONTRACT == 1:
    return installed_action_time(model)
  record = timing_by_model.get(frame)
  if record is None:
    return None
  value, valid = record
  timing = SimpleNamespace(modelMonoTime=frame, lateralActionTime=value)
  return installed_action_time(frame, timing, valid)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('candidate', type=Path)
  parser.add_argument('logs', nargs='+', type=Path)
  parser.add_argument('--force-lateral', action='store_true', help='Offline sensitivity only; ignores recorded engagement')
  parser.add_argument('--min-speed-mph', type=int, default=50)
  parser.add_argument('--max-models', type=int, default=4000)
  parser.add_argument('--assumed-action-time', type=float, default=None,
                      help='Offline sensitivity only: explicit action time for legacy logs with no timing records at all')
  parser.add_argument('--repair-timing-transport', action='store_true',
                      help='Offline repair only: use exact recorded sidecar timing even when its producer Event.valid is false')
  args = parser.parse_args()
  if args.max_models <= 0:
    parser.error('--max-models must be positive')
  if args.assumed_action_time is not None and (not np.isfinite(args.assumed_action_time) or args.assumed_action_time <= 0.0):
    parser.error('--assumed-action-time must be finite and positive')
  guard = offroad_guard()
  candidate_class = load_candidate(args.candidate.resolve(strict=True))
  total = []
  last_guard = time.monotonic()

  for path in args.logs:
    path = path.resolve(strict=True)
    assert path.is_file(), path
    # Producers write the sidecar after modelV2. A complete first pass avoids
    # substituting stale or guessed timing merely because it arrives later.
    timing_by_model, timing_stats = index_recorded_timing(LogReader(str(path)), guard)
    timing_sources = Counter()
    selected_times = Counter()
    state = None
    state_time = 0
    lateral_active = False
    lateral_time = 0
    configs = {}
    for name, cls in [('installed', LaneCenteringController), ('candidate', candidate_class)]:
      for strength in [0.3, 1.0]:
        for authority in [0.0, 1.0]:
          configs[f'{name}/strength={strength}/break_in={authority}'] = {
            'controller': cls(), 'reasons': Counter(), 'deltas': [], 'targets': [],
            'fresh_us': [], 'cached_us': [],
          }
    model_count = 0
    max_speed = 0.0
    for event in LogReader(str(path)):
      if time.monotonic() - last_guard >= 0.5:
        guard()
        last_guard = time.monotonic()
      kind = event.which()
      if kind == 'carState':
        state = event.carState
        state_time = event.logMonoTime if event.valid else 0
      elif kind == 'carControl':
        lateral_active = bool(event.valid and event.carControl.latActive)
        lateral_time = event.logMonoTime
      elif kind == 'modelV2' and state is not None:
        model_count += 1
        model = event.modelV2
        speed = float(state.vEgo)
        max_speed = max(max_speed, speed)
        fresh_state = 0 <= (event.logMonoTime - state_time) * 1e-9 <= 0.2
        fresh_lateral = 0 <= (event.logMonoTime - lateral_time) * 1e-9 <= 0.2
        action_time, timing_source = select_action_time(
          model, event.logMonoTime, timing_by_model, timing_stats['records'],
          repair_transport=args.repair_timing_transport, assumed=args.assumed_action_time,
        )
        timing_sources[timing_source] += 1
        if action_time is not None:
          selected_times[str(action_time)] += 1
        baseline_action_time = select_installed_action_time(event.logMonoTime, timing_by_model, model)
        for key, item in configs.items():
          candidate = key.startswith('candidate/')
          strength = 1.0 if 'strength=1.0' in key else 0.3
          authority = 1.0 if 'break_in=1.0' in key else 0.0
          ctrl = item['controller']
          model_action = float(model.action.desiredCurvature)
          # Five controller ticks per model frame reproduce cache/filter rates.
          for tick in range(5):
            start = time.perf_counter_ns()
            output = ctrl.update(
              model_action, model, speed, args.min_speed_mph, True, 0.0, authority, strength,
              args.force_lateral or (lateral_active and fresh_lateral), bool(event.valid and fresh_state),
              pause_on_signal=True, turn_signal_active=bool(state.leftBlinker or state.rightBlinker),
              driver_override=bool(state.steeringPressed),
              model_frame=event.logMonoTime, action_time=action_time if candidate else baseline_action_time,
            )
            elapsed_us = (time.perf_counter_ns() - start) / 1000.0
            assert np.isfinite(output), f'Non-finite output in {key}'
            assert abs(output - model_action) <= 0.0012 + 1e-12, f'Correction cap exceeded in {key}'
            item['fresh_us' if tick == 0 else 'cached_us'].append(elapsed_us)
          item['deltas'].append(output - model_action)
          item['targets'].append(ctrl.diagnostics.target_correction_curvature)
          item['reasons'][str(ctrl.diagnostics.reason)] += 1
        if model_count >= args.max_models:
          break

    results = {}
    for key, item in configs.items():
      results[key] = {
        'reasons': item['reasons'],
        'max_correction': float(np.max(np.abs(item['deltas']))) if item['deltas'] else None,
        'nonzero_correction_frames': int(np.count_nonzero(np.abs(item['deltas']) > 1e-12)),
        'p95_fresh_us': float(np.percentile(item['fresh_us'], 95)) if item['fresh_us'] else None,
        'p95_cached_us': float(np.percentile(item['cached_us'], 95)) if item['cached_us'] else None,
      }
    total.append({'log': str(path), 'model_frames': model_count, 'max_speed_mps': max_speed,
                  'timing_records': timing_stats, 'timing_sources': timing_sources,
                  'selected_action_times': selected_times, 'results': results})
    print(json.dumps(total[-1]), flush=True)
  guard()
  print(json.dumps({'status': 'completed', 'offline_only': True, 'forced_lateral': args.force_lateral,
                    'timing_transport_repair_enabled': args.repair_timing_transport,
                    'model_event_validity_preserved': True,
                    'installed_baseline': ('Recorded atomic modelV2 action' if INSTALLED_TIMING_CONTRACT == 1 else
                                           'Exact recorded sidecar identity and Event.valid'),
                    'installed_baseline_timing_repaired': False,
                    'limitations': 'Offline controller sensitivity only; not live behavior, SubMaster health, or publication timing',
                    'assumed_action_time': args.assumed_action_time,
                    'min_speed_mph': args.min_speed_mph, 'logs': len(total)}))


if __name__ == '__main__':
  main()
