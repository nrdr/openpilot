"""Portable checks for the legacy reminder chime, without native audio services."""

import ast
import hashlib
import wave
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[3]
SOUNDS = ROOT / "openpilot/selfdrive/assets/sounds"
SOUNDD = ROOT / "openpilot/selfdrive/ui/soundd.py"
# Exact prompt.wav from nrdr-bp-6.0 / 01747aa46b02ba90f25e04ce5ee805e84258b549.
LEGACY_SHA256 = "ad19268e4aaaeac8dd21f6b26c16a121e7b3f50bba867748e7226727643ae682"


def sound_mapping():
  tree = ast.parse(SOUNDD.read_text(encoding="utf-8"))
  mapping = next(node.value for node in tree.body if isinstance(node, ast.AnnAssign) and node.target.id == "sound_list")
  return {key.attr: (ast.literal_eval(value.elts[0]), ast.literal_eval(value.elts[1]))
          for key, value in zip(mapping.keys, mapping.values, strict=True) if key is not None}


def test_prompt_is_exact_ford_asset():
  filename, play_count = sound_mapping()["prompt"]
  assert (filename, play_count) == ("prompt.wav", 1)
  assert hashlib.sha256((SOUNDS / filename).read_bytes()).hexdigest() == LEGACY_SHA256
  with wave.open(str(SOUNDS / filename), "rb") as audio:
    assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) == (1, 2, 48000)
    assert audio.getnframes() == 72299
    assert len(audio.readframes(audio.getnframes())) == audio.getnframes() * 2


def test_green_light_reminder_uses_one_shot_prompt():
  source = ROOT / "openpilot/sunnypilot/selfdrive/selfdrived/events.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  reminders = [value for node in ast.walk(tree) if isinstance(node, ast.Dict)
               for key, value in zip(node.keys, node.values, strict=True)
               if isinstance(key, ast.Attribute) and key.attr == "e2eChime"]
  assert len(reminders) == 1
  sounds = [node.attr for node in ast.walk(reminders[0]) if isinstance(node, ast.Attribute) and
            isinstance(node.value, ast.Name) and node.value.id == "AudibleAlert"]
  assert sounds == ["prompt"]


def test_legacy_prompt_plays_once_without_truncating():
  # Exercise the actual loading/playback methods without Params, messaging or a speaker.
  tree = ast.parse(SOUNDD.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Soundd")
  methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in ("load_sounds", "get_sound_data")]
  namespace = {"np": np, "wave": wave, "BASEDIR": str(ROOT), "SAMPLE_RATE": 48000,
               "sound_list": {1: ("prompt.wav", 1, 1.0)}}
  exec(compile(ast.Module(body=methods, type_ignores=[]), str(SOUNDD), "exec"), namespace)
  sound = type("PlaybackUnderTest", (), {node.name: namespace[node.name] for node in methods})()
  sound.should_play_sound = lambda alert: alert == 1
  sound.current_alert = 1
  sound.current_sound_frame = 0
  sound.current_volume = 0.5
  sound.pending_stop = False
  sound.load_sounds()
  expected = sound.loaded_sounds[1] * sound.current_volume
  block_size = 4096
  blocks = len(expected) // block_size + 2
  actual = np.concatenate([sound.get_sound_data(block_size) for _ in range(blocks)])
  np.testing.assert_array_equal(actual[:len(expected)], expected)
  assert not np.any(actual[len(expected):])
  assert sound.current_sound_frame == len(expected)


@pytest.mark.parametrize(("alert", "filename", "play_count"), (
  ("promptRepeat", "warning.wav", None),
  ("promptDistracted", "dm_warning.wav", None),
  ("preAlert", "pre_alert.wav", 1),
  ("warningSoft", "critical.wav", None),
  ("warningImmediate", "dm_critical.wav", None),
))
def test_other_warning_sounds_are_unchanged(alert, filename, play_count):
  assert sound_mapping()[alert] == (filename, play_count)
  assert (SOUNDS / filename).is_file()
