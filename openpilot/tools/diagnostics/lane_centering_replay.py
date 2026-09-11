#!/usr/bin/env python3
"""Compare a lane-centering candidate with the installed controller on local logs.

This does not publish messages, write parameters, or command actuators. On a
comma device it requires fresh off-road/no-output state throughout processing.
Forced lateral availability is only an offline sensitivity check, not a driving
simulation or evidence that a candidate is safe to deploy.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import time

import numpy as np

from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.lane_centering import LaneCenteringController
from openpilot.tools.lib.logreader import LogReader


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


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('candidate', type=Path)
  parser.add_argument('logs', nargs='+', type=Path)
  parser.add_argument('--force-lateral', action='store_true', help='Offline sensitivity only; ignores recorded engagement')
  parser.add_argument('--min-speed-mph', type=int, default=50)
  parser.add_argument('--max-models', type=int, default=4000)
  parser.add_argument('--assumed-action-time', type=float, default=None,
                      help='Offline sensitivity only: explicit action time for legacy logs without matching timing metadata')
  args = parser.parse_args()
  guard = offroad_guard()
  candidate_class = load_candidate(args.candidate.resolve(strict=True))
  total = []
  last_guard = time.monotonic()

  for path in args.logs:
    path = path.resolve(strict=True)
    assert path.is_file(), path
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
              **({'model_frame': event.logMonoTime, 'action_time': args.assumed_action_time} if candidate else {}),
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
        'p95_fresh_us': float(np.percentile(item['fresh_us'], 95)) if item['fresh_us'] else None,
        'p95_cached_us': float(np.percentile(item['cached_us'], 95)) if item['cached_us'] else None,
      }
    total.append({'log': str(path), 'model_frames': model_count, 'max_speed_mps': max_speed, 'results': results})
    print(json.dumps(total[-1]), flush=True)
  guard()
  print(json.dumps({'status': 'completed', 'offline_only': True, 'forced_lateral': args.force_lateral,
                    'assumed_action_time': args.assumed_action_time,
                    'min_speed_mph': args.min_speed_mph, 'logs': len(total)}))


if __name__ == '__main__':
  main()
