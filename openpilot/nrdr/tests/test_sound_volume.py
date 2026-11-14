"""Exercise production volume logic without native messaging or audio hardware."""

import ast
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.common.filter_simple import FirstOrderFilter


SOURCE = Path(__file__).resolve().parents[3] / "openpilot/selfdrive/ui/soundd.py"


def volume_logic(device_type="tici"):
  tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
  constants = {"MIN_VOLUME", "MAX_VOLUME", "AMBIENT_DB", "DB_SCALE", "VOLUME_BASE", "ALERT_RAMP_TIME"}
  nodes = [node for node in tree.body if isinstance(node, ast.Assign) and
           any(isinstance(target, ast.Name) and target.id in constants for target in node.targets)]
  nodes += [node for node in tree.body if isinstance(node, ast.If) and "HARDWARE.get_device_type" in ast.unparse(node.test)]
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Soundd")
  nodes += [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "calculate_volume"]
  loop = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "soundd_thread")
  namespace = {"np": np, "math": math, "HARDWARE": SimpleNamespace(get_device_type=lambda: device_type),
               "AudibleAlert": SimpleNamespace(none=0, warningImmediate=6)}
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)
  sound = SimpleNamespace(current_alert=0, current_volume=0.1,
                          spl_filter_weighted=FirstOrderFilter(0, 2.5, 0.1, initialized=False))
  sound.calculate_volume = lambda db: namespace["calculate_volume"](sound, db)
  namespace["self"] = sound
  return namespace, loop


def run_loop_block(namespace, loop, selector):
  nodes = [node for node in ast.walk(loop) if isinstance(node, ast.If) and selector in ast.unparse(node.test)]
  assert len(nodes) == 1
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)


def update_microphone(namespace, loop, db, updated=True):
  class Messages(dict):
    pass

  messages = Messages(soundPressure=SimpleNamespace(soundPressureWeightedDb=db))
  messages.updated = {"soundPressure": updated}
  namespace["sm"] = messages
  run_loop_block(namespace, loop, "sm.updated['soundPressure']")


@pytest.mark.parametrize(("device_type", "ambient_db", "volume_base"), (("tici", 24, 20), ("tizi", 30, 10), ("mici", 26, 20)))
@pytest.mark.parametrize("db", (-20, 0, 24, 26, 30, 39, 45, 54, 56, 60, 100))
def test_volume_matches_ford_curve_and_preserves_c4(device_type, ambient_db, volume_base, db):
  namespace, _ = volume_logic(device_type)
  # tici=C3 and tizi=C3X match Ford's 01747aa; mici=C4 keeps its pre-change calibration.
  scaled = min(1.0, max(0.1, (db - ambient_db) / 30 * 0.9 + 0.1))
  assert namespace["self"].calculate_volume(db) == pytest.approx(volume_base ** (scaled - 1))


def test_no_microphone_update_keeps_initial_gain():
  namespace, loop = volume_logic()
  sound = namespace["self"]
  update_microphone(namespace, loop, 60, updated=False)
  assert sound.current_volume == 0.1
  assert not sound.spl_filter_weighted.initialized


@pytest.mark.parametrize("alert", (1, 2, 3, 4, 5, 6))
def test_alert_freezes_filter_and_gain_then_resumes(alert):
  namespace, loop = volume_logic()
  sound = namespace["self"]
  update_microphone(namespace, loop, 39)
  initial_gain = sound.current_volume
  assert initial_gain == pytest.approx(sound.calculate_volume(39))
  sound.current_alert = alert
  for _ in range(100):
    update_microphone(namespace, loop, 100)
  assert sound.spl_filter_weighted.x == 39
  assert sound.current_volume == initial_gain
  sound.current_alert = 0
  update_microphone(namespace, loop, 39)
  assert sound.current_volume == initial_gain
  update_microphone(namespace, loop, 50)
  assert 39 < sound.spl_filter_weighted.x < 50
  assert sound.current_volume > initial_gain


def test_immediate_warning_still_ramps_to_full_volume():
  namespace, loop = volume_logic()
  sound = namespace["self"]
  sound.current_alert = 6
  sound.ramp_start_time = 0.0
  sound.ramp_start_volume = sound.current_volume
  volumes = []
  for elapsed in (0, 1, 2, 3, 4, 5):
    namespace["time"] = SimpleNamespace(monotonic=lambda now=elapsed: now)
    run_loop_block(namespace, loop, "self.current_alert == AudibleAlert.warningImmediate")
    volumes.append(sound.current_volume)
  assert volumes == sorted(volumes)
  assert volumes[0] == sound.ramp_start_volume
  assert volumes[4:] == [1.0, 1.0]
