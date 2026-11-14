import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from openpilot.nrdr.tools.civic_pcm_brake_shadow import analyze, brake_shadow, civic_pcm, past, replay, stable_tx


CONFIG = {"carParams": {"carFingerprint": "HONDA_CIVIC", "flags": 272, "openpilotLongitudinalControl": True,
                        "pcmCruise": True, "safetyConfigs": [{"safetyModel": "hondaNidec", "safetyParam": 0}]},
          "carParamsSP": {"flags": 10, "enableGasInterceptor": False, "safetyParam": 0}}


def run(a, *, scope=None, demand=None, hud=None, t=None):
  a = np.array(a)
  yes = np.ones(len(a), dtype=bool)
  return brake_shadow(np.arange(len(a)) * .02 if t is None else np.array(t), a,
                      yes if scope is None else np.array(scope, bool), yes if demand is None else demand, yes if hud is None else hud)


class TestCivicBrakeShadow(unittest.TestCase):
  def test_scope_fails_closed(self):
    self.assertTrue(civic_pcm(CONFIG))
    for field, value in (("carFingerprint", "HONDA_CIVIC_BOSCH"), ("carFingerprint", "HONDA_CLARITY"), ("openpilotLongitudinalControl", False),
                         ("safetyConfigs", []), ("flags", 272 | 4), ("flags", 272 | 2048), ("pcmCruise", False),
                         ("flags", 256), ("enableGasInterceptor", True), ("safetyParam", 2), ("flagsSP", 26)):
      c = copy.deepcopy(CONFIG)
      target = "carParamsSP" if field in ("enableGasInterceptor", "safetyParam", "flagsSP") else "carParams"
      c[target]["flags" if field == "flagsSP" else field] = value
      with self.subTest(field=field, value=value):
        self.assertFalse(civic_pcm(c))
    for group in CONFIG:
      for field in CONFIG[group]:
        c = copy.deepcopy(CONFIG)
        del c[group][field]
        self.assertFalse(civic_pcm(c))

  def test_short_pulse_not_late_onset_and_deadline_from_real_onset(self):
    a = [0, 1, 7] + [0] * 100
    b, stat = run(a)
    np.testing.assert_array_equal(b[:3], a[:3])
    self.assertEqual(list(np.flatnonzero(b == 3)), list(range(3, 76)))
    self.assertEqual(stat["changed_releases"], 1)
    self.assertEqual(stat["observed_onsets_A"], stat["observed_onsets_B"])
    b, stat = run([0, 2, 0, 1, 0])
    self.assertEqual(list(b), [0, 2, 2, 1, 1])
    self.assertEqual((stat["observed_onsets_A"], stat["observed_onsets_B"]), (2, 1))

  def test_censored_edges_and_long_pulse_unchanged(self):
    for a in ([8, 7, 0, 0], [0] * 100, [0] + [10] * 80 + [0], [0, 1, 40, 160, 255]):
      np.testing.assert_array_equal(run(a)[0], a)
    self.assertEqual(list(run([0, 4, 0, 0], t=[1., 1.02, 1.08, 1.1])[0]), [0, 4, 0, 0])

  def test_veto_and_scope_loss_do_not_rearm_in_zero_run(self):
    for key in ("demand", "hud", "scope"):
      for mask, expected in (([1, 1, 0, 1, 1], [0, 8, 0, 0, 0]), ([1, 1, 1, 0, 1], [0, 8, 3, 0, 0])):
        np.testing.assert_array_equal(run([0, 8, 0, 0, 0], **{key: mask})[0], expected)

  def test_no_lookahead_invalid_or_stale_join(self):
    z = {"wire": np.array([[2., 1, 10], [2.03, 0, 22], [2.07, 1, 30]])}
    result, = past(z, {"wire": ["mono", "valid", "x"]}, "wire", ["x"], np.array([1.99, 2., 2.04, 2.08, 2.15]), .05)
    np.testing.assert_equal(result, [np.nan, 10, np.nan, 30, np.nan])

  def test_native_packet_replay(self):
    t = 40. + np.arange(12) * .02
    fields, streams = {}, {}

    def add(stream, **cols):
      fields[stream] = ["mono", "valid", *cols]
      streams[stream] = np.column_stack([t, np.ones(len(t)), *[np.broadcast_to(v, t.shape) for v in cols.values()]])

    add("sendcan_0_506", brake=[0, 7] + [0] * 10, cancel=0, override=1, brake_request=[0, 1] + [0] * 10)
    add("carState", v=3, a=-.1, pedal_gas=0, pedal_brake=0, stock_aeb=0, can_valid=1, acc_fault=0, standstill=0)
    add("carControl", active=1, enabled=1, request=-.2, long_state=1)
    add("carControlSP", pcm_enabled=1, ref_mono=t)
    add("pandaStates", controls_allowed=1, controls_long=1, tx_blocked=85, rx_checks_invalid=0)
    prior = streams["pandaStates"][0].copy()
    prior[0] -= .1
    streams["pandaStates"] = np.vstack([prior, streams["pandaStates"]])
    add("can_128_780", pcm_gas=[0]*5 + [1]*7, pcm_speed=0)
    meta = {"fields": fields, "init": {"mono": 40}, "segment": 1}
    with tempfile.TemporaryDirectory() as tmp:
      raw = Path(tmp) / "001.raw.npz"
      np.savez(raw, **streams)
      stats, changes, releases, windows = analyze(raw, meta, [("test", 0., 1.)])
      self.assertEqual((stats["rolling_scope_frames"], stats["changed_frames"]), (12, 3))
      self.assertEqual(changes[0]["first_s"], .04)
      self.assertIsNone(changes[0]["logged_pressure_raw"])
      self.assertEqual(releases[0]["on_duration_s"], .02)
      self.assertEqual((windows["test"]["positive_A"], windows["test"]["positive_B"]), (1, 4))
      for stream, col, value in (("carControl", "active", 0), ("pandaStates", "controls_long", 0),
                                 ("carState", "pedal_brake", 1), ("carState", "stock_aeb", 1), ("carState", "v", 20),
                                 ("carState", "standstill", 1), ("carControlSP", "ref_mono", 38), ("can_128_780", "pcm_speed", 2)):
        with self.subTest(stream=stream, col=col):
          changed = streams[stream].copy()
          changed[:, fields[stream].index(col)] = value
          np.savez(raw, **(streams | {stream: changed}))
          self.assertEqual(analyze(raw, meta, [])[0]["changed_frames"], 0)
          if col == "v":
            self.assertEqual(analyze(raw, meta, [], all_rolling_speeds=True)[0]["changed_frames"], 3)
          else:
            self.assertEqual(analyze(raw, meta, [], all_rolling_speeds=True)[0]["changed_frames"], 0)

  def test_tx_counter_change_reset_staleness_and_unknown_history(self):
    z = {"pandaStates": np.array([[1., 1, 85], [1.1, 1, 85], [1.2, 1, 86], [1.3, 1, 86], [1.4, 1, 0]])}
    names = {"pandaStates": ["mono", "valid", "tx_blocked"]}
    np.testing.assert_equal(stable_tx(z, names, np.array([1., 1.11, 1.19, 1.22, 1.31, 1.41, 1.76])),
                            [False, True, True, False, True, False, False])

  def test_stock_config_skipped_before_opening_data_and_duplicate_hash_checked(self):
    with tempfile.TemporaryDirectory() as tmp:
      roots = [Path(tmp) / name for name in ("one", "two")]
      meta = {"route": "r", "segment": 1, "source_sha256": "a"*64, "config": {}}
      for root in roots:
        (root / "r").mkdir(parents=True)
        (root / "r/001.metadata.json").write_text(json.dumps(meta))
      result = replay(roots)
      self.assertEqual(result["duplicate_segments_skipped"], 1)
      self.assertEqual(result["totals"]["configuration_excluded_segments"], 1)
      (roots[1] / "r/001.metadata.json").write_text(json.dumps(meta | {"source_sha256": "b"*64}))
      with self.assertRaisesRegex(ValueError, "conflicting"):
        replay(roots)


if __name__ == "__main__":
  unittest.main()
