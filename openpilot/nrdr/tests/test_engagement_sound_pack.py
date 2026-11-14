"""Exercise the real audio state machine without messaging, Params or a speaker."""

import ast
import hashlib
import math
import time
import wave
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamType
from openpilot.nrdr.ui.engagement_sounds import june_engagement_files, june_engagement_volume


ROOT = Path(__file__).resolve().parents[3]
SOUNDD = ROOT / "openpilot/selfdrive/ui/soundd.py"
JUNE_SOUNDS = ROOT / "openpilot/selfdrive/assets/sounds/nrdr_june_2026"
JUNE_HASHES = {
  "engage.wav": "b1e177499d9439367179cc57a6301b6162393972e3a136cc35c5fdac026bf10a",
  "disengage.wav": "42bd04a57b527c787a0555503e02a203f7d672c12d448769a3f41f17befbf013",
  "refuse.wav": "4af81cbf1d96a42cc351878b015298aee82874b46baaf1a615ca91ec36c0ced6",
  "engage_tizi.wav": "6b54a85cc09b8ee79fce23d48209205d2e70510eed4c5a86fa400fe3f7caebfd",
  "disengage_tizi.wav": "1f061777d66d8d856a5fcb17378416f959088885ed770181355195ad15de881b",
}


def soundd(device="mici", pack=1, quiet=False):
  names = ("none", "engage", "disengage", "refuse", "prompt", "promptRepeat", "promptDistracted", "preAlert",
           "warningSoft", "warningImmediate")
  alerts = SimpleNamespace(**{name: index for index, name in enumerate(names)})
  params = SimpleNamespace(value=pack, get=lambda key: params.value, get_bool=lambda key: quiet)
  errors = []
  namespace = {
    "np": np, "math": math, "time": time, "wave": wave, "Lock": Lock, "BASEDIR": str(ROOT),
    "Params": lambda: params, "FirstOrderFilter": FirstOrderFilter, "FILTER_DT": 0.1,
    "SAMPLE_RATE": 48000, "MIN_VOLUME": 0.1, "MAX_VOLUME": 1.0,
    "AMBIENT_DB": {"mici": 26, "tici": 24, "tizi": 30}[device], "DB_SCALE": 30,
    "VOLUME_BASE": 10 if device == "tizi" else 20,
    "AudibleAlert": alerts, "AudibleAlertSP": SimpleNamespace(promptSingleLow=20, promptSingleHigh=21),
    "HARDWARE": SimpleNamespace(get_device_type=lambda: device),
    "cloudlog": SimpleNamespace(exception=errors.append),
    "june_engagement_files": june_engagement_files, "june_engagement_volume": june_engagement_volume,
  }
  quiet_tree = ast.parse((ROOT / "openpilot/sunnypilot/selfdrive/ui/quiet_mode.py").read_text())
  quiet_nodes = [node for node in quiet_tree.body if isinstance(node, ast.ClassDef) or
                 isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ALERTS_ALWAYS_PLAY" for t in node.targets)]
  tree = ast.parse(SOUNDD.read_text())
  nodes = [node for node in tree.body if isinstance(node, ast.ClassDef) or
           isinstance(node, ast.AnnAssign) and node.target.id in ("sound_list", "sound_list_sp")]
  exec(compile(ast.Module(body=quiet_nodes + nodes, type_ignores=[]), str(SOUNDD), "exec"), namespace)
  sound = namespace["Soundd"]()
  return sound, alerts, errors


@pytest.mark.parametrize("filename", JUNE_HASHES)
def test_exact_june_assets(filename):
  # d6798c75a5, June 29 2026 nrdr first-parent snapshot. Never re-encoded.
  assert hashlib.sha256((JUNE_SOUNDS / filename).read_bytes()).hexdigest() == JUNE_HASHES[filename]
  with wave.open(str(JUNE_SOUNDS / filename), "rb") as audio:
    assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) == (1, 2, 48000)
    assert len(audio.readframes(audio.getnframes())) == audio.getnframes() * 2 > 0


@pytest.mark.parametrize("device", ("mici", "tici", "tizi"))
@pytest.mark.parametrize("db", (0, 24, 30, 39, 54, 60, 100))
def test_exact_june_volume(device, db):
  ambient, base = (30, 10) if device == "tizi" else (24, 20)
  expected = base ** (np.clip((db - ambient) / 30 * 0.9 + 0.1, 0.1, 1.0) - 1)
  assert june_engagement_volume(db, device) == pytest.approx(expected)


@pytest.mark.parametrize("device", ("mici", "tici", "tizi"))
@pytest.mark.parametrize("name", ("engage", "disengage", "refuse"))
def test_legacy_sound_and_gain_are_latched_until_chime_finishes(device, name):
  sound, alerts, errors = soundd(device)
  sound.spl_filter_weighted.update(39)
  sound.current_volume = sound.calculate_volume(39)
  normal_gain = sound.current_volume
  alert = getattr(alerts, name)
  sound.update_alert(alert)
  assert sound.active_sound is sound.june_engagement_sounds[alert]
  with wave.open(str(JUNE_SOUNDS / june_engagement_files(device)[name]), "rb") as audio:
    expected = np.frombuffer(audio.readframes(audio.getnframes()), dtype=np.int16).astype(np.float32) / 32768
  expected *= june_engagement_volume(39, device)
  parts = [sound.get_sound_data(4096)]
  sound.params.value = 0  # Applies next chime, not in the middle of this recording.
  sound.update_alert(alert)
  sound.update_alert(alerts.none)
  while sound.current_sound_frame < len(expected):
    parts.append(sound.get_sound_data(4096))
  actual = np.concatenate(parts)
  np.testing.assert_array_equal(actual[:len(expected)], expected)
  assert not np.any(actual[len(expected):])
  assert sound.current_volume == normal_gain
  sound.update_alert(alerts.none)
  sound.update_alert(alert)
  assert sound.active_sound is sound.loaded_sounds[alert]
  assert sound.chime_volume is None
  assert not errors


@pytest.mark.parametrize("value", (None, 0, 2, -1, "invalid"))
def test_unset_current_or_invalid_setting_uses_current_sound(value):
  sound, alerts, _ = soundd(pack=value)
  sound.update_alert(alerts.engage)
  assert sound.active_sound is sound.loaded_sounds[alerts.engage]
  assert sound.chime_volume is None


def test_missing_ambient_reading_keeps_initial_volume():
  sound, alerts, _ = soundd()
  sound.update_alert(alerts.engage)
  assert sound.chime_volume == sound.current_volume == 0.1


@pytest.mark.parametrize("name", ("prompt", "promptRepeat", "promptDistracted", "preAlert", "warningSoft", "warningImmediate"))
def test_other_alerts_keep_current_sound_and_volume_even_when_preempting_old_chime(name):
  sound, alerts, _ = soundd()
  sound.spl_filter_weighted.update(39)
  sound.current_volume = sound.calculate_volume(39)
  sound.update_alert(alerts.engage)
  sound.get_sound_data(4096)
  sound.update_alert(getattr(alerts, name))
  expected = sound.loaded_sounds[getattr(alerts, name)][:4096] * sound.current_volume
  np.testing.assert_array_equal(sound.get_sound_data(4096), expected)
  assert sound.chime_volume is None
  if name == "warningImmediate":
    assert sound.ramp_start_volume == sound.calculate_volume(39)


def test_quiet_mode_still_mutes_old_engagement_but_not_urgent_warning():
  sound, alerts, _ = soundd(quiet=True)
  sound.update_alert(alerts.engage)
  assert not np.any(sound.get_sound_data(4096))
  sound.update_alert(alerts.warningImmediate)
  assert np.any(sound.get_sound_data(4096))


def test_missing_optional_assets_fall_back_without_breaking_alerts(monkeypatch):
  original_open = wave.open

  def open_audio(path, mode):
    if "nrdr_june_2026" in str(path):
      raise FileNotFoundError(path)
    return original_open(path, mode)

  monkeypatch.setattr(wave, "open", open_audio)
  sound, alerts, errors = soundd()
  assert len(errors) == 3
  assert not sound.june_engagement_sounds
  sound.update_alert(alerts.engage)
  assert sound.active_sound is sound.loaded_sounds[alerts.engage]
  assert sound.chime_volume is None
  sound.update_alert(alerts.warningImmediate)
  assert np.any(sound.get_sound_data(4096))


def test_setting_is_persistent_current_by_default():
  spec = PARAM_SPECS_BY_KEY["NrdrEngagementSoundPack"]
  assert spec.param_type == ParamType.INT
  assert spec.default == "0"
  assert {flag.value for flag in spec.flags} == {"PERSISTENT", "BACKUP"}
