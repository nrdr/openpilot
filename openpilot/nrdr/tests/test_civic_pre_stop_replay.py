from collections import Counter
import os
from pathlib import Path
import unittest

import numpy as np

from openpilot.nrdr.tools.civic_pre_stop_replay import C, D, aged, candidate, consumed, historical_slice, hud_veto, main


def drive(n=160):
  one, zero = np.ones(n), np.zeros(n)
  d = {k: one.copy() for k in ("radarState_valid", "can_0_487_valid", "longitudinalPlanSP_valid", "radar_lead", "v")}
  d.update({k: zero.copy() for k in ("standstill", "wire_brake", "wire_pump", "wire_pcm_gas", "wire_pcm_speed", "a", "vision_active",
                                     "map_active", "radarState_age", "longitudinalPlanSP_age", "can_0_487_age")})
  d.update(t=np.arange(n)*.02, radar_lead_dist=5*one, hyd_pressure1_raw=103*one, hyd_pressure2_raw=104*one,
           long_state=2*one, request=-one)
  return d, one.astype(bool), one, zero, one, 20*one, one.astype(bool)


class TestPreStop(unittest.TestCase):
  def test_exact_consumed_plan_rejects_latest_future_stale_invalid(self):
    cols = ["mono", "valid", "plan_stop", "plan_source", "allow_brake"]
    z = {"longitudinalPlan": np.array([[1., 1, 1, 0, 1], [1.05, 1, 0, 1, 1], [1.10, 0, 0, 0, 0]])}
    stop, _, _ = consumed(z, {"longitudinalPlan": cols}, np.array([1.08, 1.09, 1.15, 1.4, 1.02]), np.array([1., 1.04, 1.1, 1., 1.05]))
    np.testing.assert_equal(stop, [1, np.nan, np.nan, np.nan, np.nan])

  def test_veto_native_packet_join_uses_state_not_should_stop_or_speed(self):
    t = np.arange(5)/10 + 5
    fields = {"carControl": ["mono", "valid", "active", "long_state"], "carControlSP": ["mono", "valid", "pcm_enabled"]}
    sent = np.column_stack((t, np.ones(5), [1, 0, 2, 1, 1], [10, 0, 30, 30, 5]))
    echo = sent.copy()
    echo[:, 0] += .008
    echo[-1, 3] += 1  # Unconfirmed echo must not be classed as either preserved or altered.
    fields["sendcan_0_780"] = fields["can_128_780"] = ["mono", "valid", "pcm_speed", "pcm_gas"]
    raw = {"sendcan_0_780": sent, "can_128_780": echo, "carControlSP": np.array([[4.99, 1, 1]]),
           "carControl": np.column_stack((t-.002, np.ones(5), np.ones(5), [0, 2, 1, 3, 2]))}
    out = {"coverage": Counter(), "windows": {}, "changed_packets": []}
    hud_veto(raw, {"fields": fields, "route": C, "segment": 0, "init": {"mono": 0}}, out)
    self.assertEqual(out["coverage"]["unpaired_echo"], 1)
    self.assertEqual(out["windows"]["all"]["veto"], 2)
    self.assertEqual(out["windows"]["all"]["changed"], 1)
    self.assertEqual(out["windows"]["all"]["positive_unchanged"], 2)
    self.assertEqual(out["changed_packets"], [[0, 5.008, 0, 1., 10]])

  def test_build_bound_not_applied_to_PID_hold_release_or_missing_authority(self):
    d, *args = drive()
    d["wire_brake"] = 4 + np.floor(5.376*d["t"])
    self.assertGreater(candidate(d, *args)[1].max(), 0)
    self.assertLessEqual(candidate(d, *args)[1].max(), 8)
    for key, value in (("standstill", 1), ("long_state", 1), ("request", .1), ("radar_lead_dist", 30), ("wire_pcm_gas", 1)):
      alt = d | {key: np.full(len(d["t"]), value)}
      self.assertFalse(candidate(alt, *args)[1].any())
    args[0][:] = False
    self.assertFalse(candidate(d, *args)[1].any())

  def test_deadzone_is_observation_only_and_stale_pressure_resets_dwell(self):
    d, *args = drive()
    d.update(v=d["v"]*20, long_state=np.ones(160), wire_pcm_speed=np.full(160, 17.))
    d["can_0_487_age"][40:50] = .2
    _, _, strict, behind, _ = candidate(d, *args)
    self.assertFalse(strict.any())
    self.assertTrue(behind[35] and behind[-1])
    self.assertFalse(behind[40:74].any())
    d["wire_pcm_gas"][:] = 1
    self.assertFalse(candidate(d, *args)[3].any())

  def test_approach_target_probe_preserves_away_from_set_and_lead_selected(self):
    d, ok, stop, source, allow, set_speed, steady = drive()
    d.update(v=set_speed-.3, request=np.ones(160)*.4, a=np.ones(160)*.7, wire_pcm_speed=set_speed+3, long_state=np.ones(160))
    def trim():
      return candidate(d, ok, stop, source, allow, set_speed, steady)[-1]
    self.assertTrue((trim() == 3).all())
    source[:] = 1
    self.assertFalse(trim().any())
    source[:] = 0
    d["v"] = set_speed-3
    self.assertFalse(trim().any())

  def test_historical_base_not_slew_limited_by_feedback_and_gap_resets(self):
    t = np.arange(201)*.02
    state = np.ones(201, bool)
    state[199] = False
    counts = historical_slice(t, state, np.full(201, -1.), np.zeros(201), np.zeros(201))
    self.assertGreater(counts[0], .5*.02*256)  # full base plus feedback rise; not a whole-effort slew limiter
    self.assertEqual(counts[198], 254)  # integration freezes before a proposed step would cross the upper bound
    self.assertTrue(np.isnan(counts[199]))
    self.assertEqual(counts[200], counts[0])
    np.testing.assert_allclose(aged(np.ones(4, bool), np.array([0., .02, .12, .14])), [0., .02, 0., .02])

  @unittest.skipUnless(os.getenv("CIVIC_REPLAY_ARCHIVES"), "set CIVIC_REPLAY_ARCHIVES to local parent of both extracted archives")
  def test_recorded_regressions(self):
    root = Path(os.environ["CIVIC_REPLAY_ARCHIVES"])
    r = main(root/"civic-evening-20261104", [root/"civic-brake-20261104"/v/"segments" for v in ("deep-scan-v3", "deep-scan-v2")])
    self.assertEqual(len(r["approaches"]), 9)
    self.assertEqual(r["hud"][C]["windows"]["P08 still stationary"]["changed"], 10)
    self.assertEqual(r["hud"][C]["windows"]["P08 first motion"]["changed"], 4)
    self.assertEqual(r["hud"][D]["windows"]["valid PID departure"]["positive_unchanged"], 28)
    self.assertEqual(r["hud"][D]["windows"]["all"]["changed"], 0)
    self.assertGreater(r["windows"]["successful rolling stop"]["build_upper_frames"], 0)
    self.assertEqual(r["windows"]["PID approach"]["build_upper_frames"], 0)
    self.assertEqual(r["windows"]["closing lead"]["no_positive_speed_lead_dead"], 271)
    self.assertEqual(r["stock"]["stock_frames_in_cells"], 0)
