#!/usr/bin/env python3
"""Run isolated candidate schema/controller tests against a comma's native runtime.

Run with -B and PYTHONPATH pointing to the installed checkout. The candidate
directory must contain log.capnp, custom.capnp, deprecated.capnp, lane_centering.py,
lane_centering_status.py, test_lane_centering.py, and lane_centering_replay.py.
Nothing is installed or published. Fresh off-road/no-output state is required.
"""
import argparse
import importlib.machinery
import importlib.util
from pathlib import Path
import sys
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
  from lane_centering_replay import offroad_guard
  guard = offroad_guard()
  load_module('openpilot.selfdrive.controls.lib.lane_centering', candidate / 'lane_centering.py')
  load_module('openpilot.selfdrive.ui.sunnypilot.onroad.lane_centering_status', candidate / 'lane_centering_status.py')
  tests = load_module('lane_centering_native_tests', candidate / 'test_lane_centering.py')

  class TimingSchemaTests(unittest.TestCase):
    def test_defaults_are_unavailable(self):
      timing = cereal.custom.ModelDataV2SP.new_message()
      self.assertEqual(timing.modelMonoTime, 0)
      self.assertEqual(timing.lateralActionTime, 0.0)

    def test_exact_model_identity_survives_roundtrip(self):
      timing = cereal.custom.ModelDataV2SP.new_message(modelMonoTime=987654321012345, lateralActionTime=0.375)
      with cereal.custom.ModelDataV2SP.from_bytes(timing.to_bytes()) as decoded:
        self.assertEqual(decoded.modelMonoTime, 987654321012345)
        self.assertAlmostEqual(decoded.lateralActionTime, 0.375)

  class GuardedResult(unittest.TextTestResult):
    def startTest(self, test):
      guard()
      super().startTest(test)

  suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
  suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TimingSchemaTests))
  result = unittest.TextTestRunner(resultclass=GuardedResult, verbosity=1).run(suite)
  guard()
  return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
  raise SystemExit(main())
