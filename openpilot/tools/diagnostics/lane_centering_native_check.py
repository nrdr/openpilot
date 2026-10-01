#!/usr/bin/env python3
"""Run isolated candidate schema/controller tests against a comma's native runtime.

Run with -B and PYTHONPATH pointing to the installed checkout. The candidate
directory must contain log.capnp, custom.capnp, deprecated.capnp, lane_centering.py,
lane_centering_status.py, test_lane_centering.py, lane_centering_replay.py, and
modeld.py (only its timing helper body is executed, never the model daemon).
Nothing is installed or published. Fresh off-road/no-output state is required.
"""
import argparse
import ast
import base64
import importlib.machinery
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading
import types
import unittest


def load_module(name, path):
  spec = importlib.util.spec_from_file_location(name, path)
  module = importlib.util.module_from_spec(spec)
  sys.modules[name] = module
  spec.loader.exec_module(module)
  return module


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('candidate_dir', type=Path)
  args = parser.parse_args()
  candidate = args.candidate_dir.resolve(strict=True)

  # Select candidate schemas before importing any installed cereal consumers.
  # Native messaging/extensions continue to load from the installed package.
  import capnp
  import opendbc
  import openpilot
  capnp.remove_import_hook()
  installed = Path(openpilot.__file__).resolve().parent / 'cereal'
  imports = [str(candidate), str(installed), str(Path(opendbc.__file__).resolve().parent / 'car')]
  cereal = types.ModuleType('openpilot.cereal')
  cereal.__path__ = [str(installed)]
  cereal.__spec__ = importlib.machinery.ModuleSpec('openpilot.cereal', loader=None, is_package=True)
  cereal.CEREAL_PATH = str(candidate)
  cereal.log = capnp.load(str(candidate / 'log.capnp'), imports=imports)
  cereal.custom = capnp.load(str(candidate / 'custom.capnp'), imports=imports)
  sys.modules['openpilot.cereal'] = cereal
  openpilot.cereal = cereal

  sys.path.insert(0, str(candidate))
  from lane_centering_replay import (
    INSTALLED_TIMING_CONTRACT, index_recorded_timing, offroad_guard, select_action_time, select_installed_action_time,
  )
  read_guard = offroad_guard()
  guard_lock = threading.Lock()

  def guard():
    with guard_lock:
      read_guard()

  controller_module = load_module('openpilot.selfdrive.controls.lib.lane_centering', candidate / 'lane_centering.py')
  load_module('openpilot.selfdrive.ui.sunnypilot.onroad.lane_centering_status', candidate / 'lane_centering_status.py')
  tests = load_module('lane_centering_native_tests', candidate / 'test_lane_centering.py')
  publisher_source = candidate / 'modeld.py'
  publisher_tree = ast.parse(publisher_source.read_text())
  publisher_helpers = [node for node in publisher_tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == 'set_lateral_action_timing']
  assert len(publisher_helpers) == 1, 'Expected one actual modeld timing publisher helper'
  publisher_namespace = {}
  exec(compile(ast.Module(body=publisher_helpers, type_ignores=[]), str(publisher_source), 'exec'), publisher_namespace)
  publish_timing = publisher_namespace['set_lateral_action_timing']

  class TimingSchemaTests(unittest.TestCase):
    @staticmethod
    def model_event(action_time=None, valid=True):
      event = cereal.log.Event.new_message(logMonoTime=987654321012345, valid=valid)
      model = event.init('modelV2')
      model.action.desiredCurvature = 0.0007
      if action_time is not None:
        model.action.lateralActionTime = action_time
      speed = 55.0 * 0.44704
      xs = [float(x) for x in range(101)]
      model.position.x = xs
      model.position.y = [0.0] * len(xs)
      model.position.yStd = [0.1] * len(xs)
      model.position.t = [x / speed for x in xs]
      lines = model.init('laneLines', 4)
      for line, y in zip(lines, [0.0, -1.45, 2.15, 0.0], strict=True):
        line.x = xs
        line.y = [y] * len(xs)
      model.laneLineProbs = [0.0, 0.9, 0.9, 0.0]
      model.laneLineStds = [0.0, 0.1, 0.1, 0.0]
      model.meta.laneChangeState = 'off'
      return event

    @staticmethod
    def update(controller, event):
      model = event.modelV2
      return controller.update(
        model.action.desiredCurvature, model, 55.0 * 0.44704, 50, True, 0.0, 0.0, 1.0, True, bool(event.valid),
        model_frame=event.logMonoTime, action_time=controller_module.lane_centering_action_time(model),
      )

    def test_default_action_time_is_unavailable_in_full_event(self):
      event = self.model_event()
      with cereal.log.Event.from_bytes(event.to_bytes()) as decoded:
        self.assertTrue(decoded.valid)
        self.assertEqual(decoded.modelV2.action.lateralActionTime, 0.0)
        self.assertIsNone(controller_module.lane_centering_action_time(decoded.modelV2))
        controller = controller_module.LaneCenteringController()
        self.assertEqual(self.update(controller, decoded), decoded.modelV2.action.desiredCurvature)
        self.assertEqual(str(controller.diagnostics.reason), 'timingUnavailable')

    def test_installed_schema_event_without_timing_defaults_to_zero(self):
      # A separate process avoids registering old and new schemas with the same
      # Cap'n Proto IDs in one native runtime. It only serializes an Event.
      source = '''import base64, json
from openpilot.cereal import log
event = log.Event.new_message(logMonoTime=123456789012345, valid=True)
model = event.init('modelV2')
model.action.desiredCurvature = 0.0007
print(json.dumps({'encoded': base64.b64encode(event.to_bytes()).decode(),
                  'installed_has_atomic_timing': 'lateralActionTime' in log.ModelDataV2.Action.schema.fields}))
'''
      guard()
      record = json.loads(subprocess.check_output([sys.executable, '-B', '-c', source], text=True, timeout=15))
      guard()
      with cereal.log.Event.from_bytes(base64.b64decode(record['encoded'])) as decoded:
        self.assertEqual(decoded.logMonoTime, 123456789012345)
        self.assertTrue(decoded.valid)
        self.assertEqual(decoded.modelV2.action.lateralActionTime, 0.0)
        self.assertIsNone(controller_module.lane_centering_action_time(decoded.modelV2))
      print(json.dumps({'legacy_schema_roundtrip': 'passed',
                        'installed_has_atomic_timing': record['installed_has_atomic_timing']}), flush=True)

    def test_float32_action_timing_and_nonzero_output_survive_event_roundtrip(self):
      for action_time in (0.325, 0.545):
        with self.subTest(action_time=action_time):
          event = self.model_event(action_time)
          with cereal.log.Event.from_bytes(event.to_bytes()) as decoded:
            self.assertEqual(decoded.which(), 'modelV2')
            self.assertEqual(decoded.logMonoTime, 987654321012345)
            self.assertTrue(decoded.valid)
            self.assertAlmostEqual(decoded.modelV2.action.lateralActionTime, action_time, places=6)
            self.assertAlmostEqual(controller_module.lane_centering_action_time(decoded.modelV2), action_time, places=6)
            controller = controller_module.LaneCenteringController()
            output = self.update(controller, decoded)
            delta = output - decoded.modelV2.action.desiredCurvature
            self.assertTrue(math.isfinite(output))
            self.assertGreater(delta, 1e-8)
            self.assertLessEqual(delta, 0.0012 + 1e-12)
            self.assertEqual(str(controller.diagnostics.reason), 'correcting')

    def test_invalid_model_event_keeps_model_gate_closed(self):
      controller = controller_module.LaneCenteringController()
      for valid in (True, False):
        event = self.model_event(0.545, valid=valid)
        with cereal.log.Event.from_bytes(event.to_bytes()) as decoded:
          self.assertEqual(decoded.valid, valid)
          self.assertIsNotNone(controller_module.lane_centering_action_time(decoded.modelV2))
          output = self.update(controller, decoded)
          if valid:
            self.assertNotEqual(output, decoded.modelV2.action.desiredCurvature)
          else:
            self.assertEqual(output, decoded.modelV2.action.desiredCurvature)
            self.assertEqual(str(controller.diagnostics.reason), 'modelInvalid')

    def test_malformed_or_unsupported_serialized_action_time_fails_closed(self):
      for value in (0.0, -0.1, float('nan'), float('inf'), -float('inf'), controller_module._MAX_ACTION_TIME + 0.1):
        with self.subTest(action_time=value):
          event = self.model_event(value)
          with cereal.log.Event.from_bytes(event.to_bytes()) as decoded:
            self.assertIsNone(controller_module.lane_centering_action_time(decoded.modelV2))
            controller = controller_module.LaneCenteringController()
            self.assertEqual(self.update(controller, decoded), decoded.modelV2.action.desiredCurvature)
            self.assertEqual(str(controller.diagnostics.reason), 'timingUnavailable')

    def test_missing_or_malformed_python_action_objects_fail_closed(self):
      for model in (None, types.SimpleNamespace(), types.SimpleNamespace(action=None),
                    types.SimpleNamespace(action=types.SimpleNamespace(lateralActionTime='broken'))):
        self.assertIsNone(controller_module.lane_centering_action_time(model))

    def test_actual_publisher_helper_preserves_action_and_copies_event_validity(self):
      for valid in (True, False):
        with self.subTest(valid=valid):
          model_event = self.model_event(valid=valid)
          model_event.modelV2.action.desiredAcceleration = -0.75
          model_event.modelV2.action.shouldStop = True
          before = model_event.modelV2.action.to_dict()
          timing_event = cereal.log.Event.new_message(logMonoTime=model_event.logMonoTime + 1, valid=not valid)
          timing_event.init('modelDataV2SP')
          publish_timing(model_event, timing_event, 0.545)
          with cereal.log.Event.from_bytes(model_event.to_bytes()) as model_decoded:
            with cereal.log.Event.from_bytes(timing_event.to_bytes()) as timing_decoded:
              self.assertEqual(model_decoded.valid, valid)
              self.assertEqual(timing_decoded.valid, valid)
              self.assertEqual(timing_decoded.modelDataV2SP.modelMonoTime, model_decoded.logMonoTime)
              self.assertAlmostEqual(model_decoded.modelV2.action.lateralActionTime, 0.545, places=6)
              self.assertEqual(timing_decoded.modelDataV2SP.lateralActionTime, model_decoded.modelV2.action.lateralActionTime)
              for name in ('desiredCurvature', 'desiredAcceleration', 'shouldStop'):
                self.assertEqual(getattr(model_decoded.modelV2.action, name), before[name])

  class ReplayTimingTests(unittest.TestCase):
    @staticmethod
    def sidecar(frame, value, valid):
      event = cereal.log.Event.new_message(logMonoTime=frame + 1, valid=valid)
      timing = event.init('modelDataV2SP')
      timing.modelMonoTime = frame
      timing.lateralActionTime = value
      return event

    def test_invalid_sidecar_roundtrip_requires_explicit_offline_repair(self):
      event = self.sidecar(987654321012345, 0.545, False)
      with cereal.log.Event.from_bytes(event.to_bytes()) as decoded:
        self.assertFalse(decoded.valid)
        self.assertEqual(decoded.modelDataV2SP.modelMonoTime, 987654321012345)
        self.assertAlmostEqual(decoded.modelDataV2SP.lateralActionTime, 0.545, places=6)
        model = TimingSchemaTests.model_event()
        index, stats = index_recorded_timing([model, decoded], guard)
        value, source = select_action_time(model.modelV2, model.logMonoTime, index, stats['records'], assumed=0.325)
        self.assertIsNone(value)
        self.assertEqual(source, 'invalid_sidecar_event')
        value, source = select_action_time(model.modelV2, model.logMonoTime, index, stats['records'], repair_transport=True)
        self.assertAlmostEqual(value, 0.545, places=6)
        self.assertEqual(source, 'offline_transport_repair_invalid_sidecar')
        self.assertIsNone(select_installed_action_time(model.logMonoTime, index, model.modelV2))

    def test_exact_join_never_uses_other_frame_or_assumption(self):
      model = TimingSchemaTests.model_event()
      index, stats = index_recorded_timing([self.sidecar(model.logMonoTime - 1, 0.325, True)], guard)
      value, source = select_action_time(model.modelV2, model.logMonoTime, index, stats['records'],
                                         repair_transport=True, assumed=0.325)
      self.assertIsNone(value)
      self.assertEqual(source, 'no_exact_recorded_timing')

    def test_atomic_timing_has_priority_and_bad_atomic_does_not_fallback(self):
      for atomic in (0.325, float('nan'), -0.1):
        model = TimingSchemaTests.model_event(atomic)
        index, stats = index_recorded_timing([self.sidecar(model.logMonoTime, 0.545, True)], guard)
        value, source = select_action_time(model.modelV2, model.logMonoTime, index, stats['records'], assumed=0.275)
        self.assertEqual(source, 'modelV2.action')
        if math.isnan(atomic):
          self.assertTrue(math.isnan(value))
        else:
          self.assertAlmostEqual(value, atomic, places=6)

    def test_conflicting_records_fail_closed(self):
      model = TimingSchemaTests.model_event()
      events = [self.sidecar(model.logMonoTime, value, True) for value in (0.325, 0.545, 0.325)]
      index, stats = index_recorded_timing(events, guard)
      value, source = select_action_time(model.modelV2, model.logMonoTime, index, stats['records'],
                                         repair_transport=True, assumed=0.325)
      self.assertIsNone(value)
      self.assertEqual(source, 'conflicting_recorded_timing')

    def test_assumption_only_for_logs_without_recorded_timing(self):
      model = TimingSchemaTests.model_event()
      self.assertEqual(select_action_time(model.modelV2, model.logMonoTime, {}, 0, assumed=0.325),
                       (0.325, 'assumed_legacy_sensitivity'))
      self.assertEqual(select_action_time(model.modelV2, model.logMonoTime, {}, 1, assumed=0.325),
                       (None, 'no_exact_recorded_timing'))

    def test_installed_baseline_keeps_original_validity_and_delay_envelope(self):
      frame = 987654321012345
      if INSTALLED_TIMING_CONTRACT == 3:
        self.assertAlmostEqual(select_installed_action_time(frame, {frame: (0.325, True)}), 0.325)
        self.assertIsNone(select_installed_action_time(frame, {frame: (0.325, False)}))
        self.assertIsNone(select_installed_action_time(frame, {frame: (0.545, True)}))
        self.assertIsNone(select_installed_action_time(frame, {frame: (0.545, False)}))
      else:
        model = TimingSchemaTests.model_event(0.325)
        self.assertAlmostEqual(select_installed_action_time(frame, {frame: (0.545, False)}, model.modelV2), 0.325, places=6)
        legacy = TimingSchemaTests.model_event()
        self.assertIsNone(select_installed_action_time(frame, {frame: (0.325, True)}, legacy.modelV2))

  class GuardedResult(unittest.TextTestResult):
    def startTest(self, test):
      guard()
      super().startTest(test)

  suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
  suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TimingSchemaTests))
  suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ReplayTimingTests))
  stop_guard = threading.Event()

  def guard_watchdog():
    # Long single-test simulations must not defer the off-road check until the
    # next test. Failure terminates this isolated, read-only diagnostic process.
    while not stop_guard.wait(0.5):
      try:
        guard()
      except Exception as exc:
        print(f'Native diagnostic safety guard failed: {exc}', file=sys.stderr, flush=True)
        os._exit(2)

  watchdog = threading.Thread(target=guard_watchdog, name='native-check-offroad-guard', daemon=True)
  watchdog.start()
  try:
    result = unittest.TextTestRunner(resultclass=GuardedResult, verbosity=1).run(suite)
  finally:
    stop_guard.set()
    watchdog.join(timeout=1.0)
  guard()
  return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
  raise SystemExit(main())
