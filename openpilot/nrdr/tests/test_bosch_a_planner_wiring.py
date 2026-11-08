"""Bosch-A longitudinal tuning wired into the nrdr planner and MPC (workers b+c of the Biscuit-Labs port).

Ported from the SOURCE test_bosch_a_toggles.py (planner classes) and test_bosch_a_engage_init.py with the owner toggles
removed (always on). Static tests with a recording stand-in for the native acados solver: no replay and no road evidence.
"""
import sys
from types import SimpleNamespace as NS
from unittest.mock import patch

import numpy as np
import pytest

if sys.platform == "win32":
  pytest.skip("Planner harness runs on Linux", allow_module_level=True)

from openpilot.cereal import custom, log, messaging
from opendbc.car.honda.values import HondaFlags
from opendbc.car.interfaces import ACCEL_MAX
from opendbc.car.structs import car
from openpilot.nrdr.features.longitudinal.bosch_a import gate, human_acceleration, human_following, model_lead_qualification
from openpilot.selfdrive.controls.lib import longitudinal_planner
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib import long_mpc
from openpilot.selfdrive.controls.radard import RADAR_TO_CAMERA
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP

LEAD_T = human_following.LEAD_T_IDXS_MODEL


def cp(fingerprint="HONDA_CIVIC_BOSCH", *, long=True, radar_unavailable=False, mvl=False):
  out = car.CarParams.new_message()
  out.brand = "honda"
  out.carFingerprint = fingerprint
  out.openpilotLongitudinalControl = long
  out.radarUnavailable = radar_unavailable
  out.steerRatio, out.wheelbase = 15.38, 2.7
  out.longitudinalActuatorDelay = 0.15
  out.deprecated.vEgoStopping = 0.5
  if mvl:
    out.flags = int(HondaFlags.MVL_LONGITUDINAL)
  return out


BOSCH_A = cp()
CLARITY = cp("HONDA_CLARITY")
CIVIC_NIDEC = cp("HONDA_CIVIC")
NOT_BOSCH_A = (CLARITY, CIVIC_NIDEC, cp("HONDA_ACCORD_11G"), cp(long=False))


class RecordingSolver:
  """Deterministic stand-in for AcadosOcpSolverCython: logs every call and derives x from the stage parameters, so any
  change in what the planner hands the MPC changes both the log and the planner output."""
  def __init__(self, *_):
    self.calls, self.p, self.x0 = [], {}, np.zeros(3)

  def _log(self, *args):
    self.calls.append(tuple(np.copy(a).tolist() if isinstance(a, np.ndarray) else a for a in args))

  def reset(self):
    self._log("reset")

  def cost_set(self, stage, key, value):
    self._log("cost_set", stage, key, value)

  def set(self, stage, key, value):
    self._log("set", stage, key, value)
    if key == "p":
      self.p[stage] = np.copy(value)

  def constraints_set(self, stage, key, value):
    self._log("constraints_set", stage, key, value)
    self.x0 = np.copy(value)

  def solve(self):
    return 0

  def get_stats(self, _):
    return [0.001]

  def get(self, stage, key):
    if key == "u":
      return np.array([0.0])
    p = self.p.get(stage, np.zeros(8))
    a = 0.5 * float(p[1]) - 0.02 * max(0.0, 60.0 - float(p[2]))
    return np.array([self.x0[0] + stage, self.x0[1] + 0.1 * stage * a, a])


# SOURCE qualified_model_leads reads freshness from a real SubMaster (valid/alive/freq_ok/logMonoTime/recv_time) and a
# (monotonic, boottime) clock pair. The harness fixes both so a frame is fresh unless a test ages it.
NOW_NS = 10_000_000_000
BOOT_OFFSET_NS = 1_000_000_000


class FakeSubMaster(dict):
  def __init__(self, messages, frame):
    super().__init__(messages)
    names = ("modelV2", "radarState", "carState")
    self.valid = dict.fromkeys(names, True)
    self.alive = dict.fromkeys(names, True)
    self.freq_ok = dict.fromkeys(names, True)
    stamp = NOW_NS - 30_000_000 + frame * 1_000_000
    self.logMonoTime = {"modelV2": stamp, "radarState": stamp + 2_000_000, "carState": stamp + 2_000_000}
    self.recv_time = {name: (NOW_NS - 5_000_000) / 1e9 for name in names}
    self["radarState"].mdMonoTime = stamp
    self["modelV2"].timestampEof = NOW_NS + BOOT_OFFSET_NS - 40_000_000


@pytest.fixture(autouse=True)
def fixed_clock_pair(monkeypatch):
  monkeypatch.setattr(model_lead_qualification, "_model_lead_clock_pair_ns", lambda: (NOW_NS, NOW_NS + BOOT_OFFSET_NS))


def submaster(frame, *, v_ego=22.0, a_ego=-0.2, v_cruise_kph=100.0, personality=log.LongitudinalPersonality.standard):
  services = ("carControl", "carState", "controlsState", "vehicleParameters", "radarState", "modelV2", "selfdriveState")
  msgs = {name: messaging.new_message(name) for name in services}
  cs = msgs["carState"].carState
  cs.vEgo, cs.aEgo, cs.vCruise, cs.canValid = v_ego - 0.05 * frame, a_ego, v_cruise_kph, True
  # Frame 0 is the engage frame: "off" resets the planner state to vEgo, as on the car.
  msgs["controlsState"].controlsState.longControlState = "off" if frame == 0 else "pid"
  ss = msgs["selfdriveState"].selfdriveState
  ss.enabled, ss.personality = True, personality
  rs = msgs["radarState"].radarState
  d_rels = (32.0 - 0.3 * frame, 60.0)
  for track, (lead, d_rel) in enumerate(zip((rs.leadOne, rs.leadTwo), d_rels, strict=True)):
    lead.present, lead.dRel, lead.vLead, lead.vLeadK, lead.aLeadK, lead.aLeadTau, lead.modelProb, lead.radar = \
      True, d_rel, 18.0, 18.0, -0.8, 1.5, 0.9, True
    lead.radarTrackId = track + 1
  model = msgs["modelV2"].modelV2
  model.meta.disengagePredictions.gasPressProbs = [0.5, 0.5]
  model.velocity.x = [v_ego] * 33
  model.init("leadsV3", 3)
  for i, model_lead in enumerate(model.leadsV3):
    # Matches leadOne/leadTwo (the horizon check) but brakes harder than the radar aLeadK extrapolation.
    d_rel = d_rels[min(i, 1)]
    model_lead.prob = 0.9
    model_lead.t = LEAD_T.tolist()
    model_lead.x = [d_rel + RADAR_TO_CAMERA + 18.0 * t - 0.75 * t * t for t in model_lead.t]
    model_lead.y = [0.0] * len(model_lead.t)
    model_lead.v = [max(0.0, 18.0 - 1.5 * t) for t in model_lead.t]
    model_lead.a = [-1.5] * len(model_lead.t)
  return FakeSubMaster({name: getattr(msg, name) for name, msg in msgs.items()}, frame)


def build(CP):
  """The real nrdr LongitudinalPlanner with the recording solver; only the optional map/remote base class is isolated."""
  with patch.object(long_mpc, "AcadosOcpSolverCython", RecordingSolver), \
       patch.object(LongitudinalPlannerSP, "__init__", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a)):
    planner = longitudinal_planner.LongitudinalPlanner(CP, custom.CarParamsSP.new_message(), init_v=22.0)
  planner.accel_boost_sp = None  # attribute the isolated SP base __init__ would have set
  if hasattr(planner, "bosch_a_clock_ns"):
    planner.bosch_a_clock_ns = lambda: NOW_NS
  return planner


def run(planner, frames=6, **kwargs):
  out = []
  with patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a)):
    for frame in range(frames):
      planner.update(submaster(frame, **kwargs))
      out.append((float(planner.output_a_target), bool(planner.output_should_stop), bool(planner.fcw),
                  planner.v_desired_trajectory.tolist(), planner.a_desired_trajectory.tolist(),
                  planner.j_desired_trajectory.tolist()))
  return out, planner.mpc.solver.calls


def spy_mpc_update(planner):
  seen = []
  original = planner.mpc.update

  def spy(radarstate, *args, **kwargs):
    seen.append(kwargs)
    return original(radarstate, *args, **kwargs)
  planner.mpc.update = spy
  return seen


def test_wired_only_for_bosch_a_with_op_long_and_mvl_off():
  planner = build(BOSCH_A)
  assert planner.bosch_a_wired and planner.mpc.nrdr.human_following
  for name in ("bosch_a_long", "bosch_a_smooth", "bosch_a_coast_first", "bosch_a_release_coast", "bosch_a_onset_ramp",
               "bosch_a_stop_gap"):
    assert hasattr(planner, name), name
  assert planner.bosch_a_long.stock_feel
  vision_only = build(cp(radar_unavailable=True))
  assert vision_only.bosch_a_wired  # HumanFollowing / HumanAcceleration run vision-only (SOURCE semantics)
  assert not vision_only.bosch_a_long.enabled
  for CP in NOT_BOSCH_A:
    other = build(CP)
    assert not other.bosch_a_wired, CP.carFingerprint
    assert not other.mpc.nrdr.human_following
    assert not hasattr(other, "bosch_a_long")


def test_mvl_on_bosch_a_is_not_wired():
  planner = build(cp(mvl=True))
  assert planner.mvl_enabled
  assert not getattr(planner, "bosch_a_wired", False)
  assert not hasattr(planner, "bosch_a_long")


@pytest.mark.parametrize("CP", [CLARITY, CIVIC_NIDEC, cp(mvl=True), cp(long=False)], ids=lambda c: f"{c.carFingerprint}-mvl{bool(c.flags)}")
def test_unwired_configurations_match_the_wiring_forced_off(CP):
  """MVL on or a non-Bosch-A car: the planner output and the exact solver call log do not depend on the Bosch-A wiring.
  (The byte-for-byte comparison against the pre-port planner source was done separately; see the worker report.)"""
  reference_planner = build(CP)
  seen = spy_mpc_update(reference_planner)
  reference = run(reference_planner)
  with patch.object(gate, "human_following_enabled", lambda _cp: False):
    forced_off = build(CP)
  assert not getattr(forced_off, "bosch_a_wired", False)
  assert run(forced_off) == reference
  for kwargs in seen:
    assert "acceleration_max" not in kwargs and "lead_paths" not in kwargs
  np.testing.assert_array_equal(reference_planner.mpc.params[:, 1], ACCEL_MAX)


def test_wired_planner_passes_cap_and_lead_paths_and_changes_the_output():
  planner = build(BOSCH_A)
  seen = spy_mpc_update(planner)
  outputs, _ = run(planner)
  with patch.object(gate, "human_following_enabled", lambda _cp: False):
    reference, _ = run(build(BOSCH_A))
  assert len(seen) == len(outputs)
  for kwargs in seen:
    assert set(kwargs) >= {"acceleration_max", "lead_paths"}
    assert 0.0 <= kwargs["acceleration_max"] <= ACCEL_MAX
    assert len(kwargs["lead_paths"]) == 2
    assert any(path is not None for path in kwargs["lead_paths"])
  np.testing.assert_array_equal(planner.mpc.params[:, 1], seen[-1]["acceleration_max"])
  assert outputs != reference


def test_human_path_replaces_the_bosch_a_model_horizon_fallback():
  """The path HumanFollowing builds is the one the MPC lead trajectory carries (not the raw aLeadK extrapolation)."""
  planner = build(BOSCH_A)
  seen = spy_mpc_update(planner)
  run(planner, frames=2)
  expected = seen[-1]["lead_paths"][0]
  assert expected is not None
  raw = np.zeros((len(long_mpc.T_IDXS), 2))
  got = planner.mpc.nrdr._lead_trajectory(NS(), submaster(1)["radarState"].leadOne, 0, 21.9, raw, expected)
  np.testing.assert_array_equal(got, expected)


def test_no_fresh_human_path_falls_back_to_raw_extrapolation_not_the_bosch_model_horizon():
  planner = build(BOSCH_A)
  raw = np.full((len(long_mpc.T_IDXS), 2), 3.0)
  lead = submaster(1)["radarState"].leadOne
  assert planner.mpc.nrdr._lead_trajectory(NS(), lead, 0, 21.9, raw, None).tolist() == raw.tolist()
  # A malformed path is rejected too.
  bad = np.full((len(long_mpc.T_IDXS), 2), np.nan)
  assert planner.mpc.nrdr._lead_trajectory(NS(), lead, 0, 21.9, raw, bad).tolist() == raw.tolist()


def test_post_mpc_chain_runs_in_source_order_on_bosch_a():
  planner = build(BOSCH_A)
  order = []
  for name, method in (("bosch_a_long", "step"), ("bosch_a_coast_first", "step"), ("bosch_a_release_coast", "update"),
                       ("bosch_a_smooth", "step"), ("bosch_a_onset_ramp", "step"), ("bosch_a_stop_gap", "step")):
    obj = getattr(planner, name)
    original = getattr(obj, method)

    def spy(*args, _name=name, _original=original, **kwargs):
      order.append(_name)
      return _original(*args, **kwargs)
    setattr(obj, method, spy)
  outputs, _ = run(planner, frames=2)
  assert order == ["bosch_a_long", "bosch_a_coast_first", "bosch_a_release_coast", "bosch_a_smooth", "bosch_a_onset_ramp",
                   "bosch_a_stop_gap"] * 2
  assert all(np.isfinite(o[0]) for o in outputs)


def test_human_acceleration_cap_is_throttle_side_only():
  base = 2.0
  assert human_acceleration.cap(base, 30.0, 10.0) == pytest.approx(base)  # far below the set speed, full speed range
  assert human_acceleration.cap(base, 30.0, 30.0) == 0.0  # at the set speed: no throttle, never negative
  assert human_acceleration.cap(base, 30.0, 35.0) == 0.0
  assert human_acceleration.cap(base, 0.0, 0.0) == 0.0
  assert human_acceleration.cap(-1.0, 30.0, 10.0) == 0.0
  assert 0.0 < human_acceleration.cap(base, 12.5, 11.5) < base


def test_upstream_lead_paths_follow_the_model_deltas_from_the_radar_anchor():
  sm = submaster(0)
  paths = human_following.upstream_lead_paths(sm["modelV2"], sm["radarState"], 22.0)
  assert paths[0] is not None and paths[0].shape == (len(long_mpc.T_IDXS), 2)
  assert paths[0][0, 0] >= sm["radarState"].leadOne.dRel - 1e-9
  assert np.all(np.diff(paths[0][:, 0]) >= -1e-9)  # monotone distance
  assert human_following.upstream_lead_paths(None, sm["radarState"], 22.0) == (None, None)


def test_urgent_closing_hands_the_lead_back_to_the_raw_extrapolation():
  sm = submaster(0)
  lead = sm["radarState"].leadOne
  # closing 22 - 18 = 4 m/s at 32 m: TTC 8 s, builds a path; at 6 m the TTC is < 2 s, so no human path.
  assert human_following.build_trajectory(sm["modelV2"].leadsV3[0], lead, 22.0, 22.0) is not None
  lead.dRel = 6.0
  sm["modelV2"].leadsV3[0].x = [float(6.0 + RADAR_TO_CAMERA + 18.0 * t - 0.75 * t * t) for t in LEAD_T]
  assert human_following.build_trajectory(sm["modelV2"].leadsV3[0], lead, 22.0, 22.0) is None


def test_mpc_rejects_out_of_range_cap():
  with patch.object(long_mpc, "AcadosOcpSolverCython", RecordingSolver):
    mpc = long_mpc.LongitudinalMpc()
  radar = submaster(0)["radarState"]
  for bad in (float("nan"), float("inf"), -0.1, ACCEL_MAX + 0.1):
    mpc.update(radar, acceleration_max=bad)
    np.testing.assert_array_equal(mpc.params[:, 1], ACCEL_MAX)
  mpc.update(radar, acceleration_max=0.5)
  np.testing.assert_array_equal(mpc.params[:, 1], 0.5)


def test_gate_matches_the_wiring():
  for CP in (BOSCH_A, cp(radar_unavailable=True), *NOT_BOSCH_A):
    assert build(CP).bosch_a_wired == gate.human_following_enabled(CP), CP.carFingerprint


# ---- Engage init (SOURCE test_bosch_a_engage_init.py) ---------------------------------------------------------------
V_EGO = 22.0


def engage_sm(a_ego, v_cruise_kph, frame=0):
  sm = submaster(frame)
  sm["carState"].vEgo, sm["carState"].aEgo, sm["carState"].vCruise = V_EGO, a_ego, v_cruise_kph
  return sm


def reset_a_cruise(CP, a_ego, v_cruise_kph, wired=True):
  if wired:
    planner = build(CP)
  else:
    with patch.object(gate, "human_following_enabled", lambda _cp: False):
      planner = build(CP)
  with patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a)):
    planner.update(engage_sm(a_ego, v_cruise_kph))
  return planner.a_cruise


def test_engage_init_above_set_speed_seeds_the_cruise_target():
  # 22 m/s against a 72 km/h (20 m/s) set speed: the cruise target is the floor, aEgo is +1.5.
  on = reset_a_cruise(BOSCH_A, 1.5, 72.0)
  off = reset_a_cruise(BOSCH_A, 1.5, 72.0, wired=False)
  print("engage init above set speed: on", on, "off", off)
  assert np.isfinite(on)
  assert on == pytest.approx(-1.2)  # the cruise floor, replacing the stock jerk-limited seed
  assert on < off  # the unlimited cruise target replaces the stock jerk-limited seed


def test_engage_init_never_below_the_cruise_floor():
  for a_ego in (1.5, 0.0):
    assert reset_a_cruise(BOSCH_A, a_ego, 30.0) >= -1.2 - 1e-9


def test_engage_init_target_above_aego_is_stock():
  # Set speed well above vEgo: min() keeps the stock value bit-for-bit.
  assert reset_a_cruise(BOSCH_A, -0.5, 120.0) == reset_a_cruise(BOSCH_A, -0.5, 120.0, wired=False)


def test_engage_init_other_cars_untouched():
  for CP in NOT_BOSCH_A:
    assert reset_a_cruise(CP, 1.5, 72.0) == reset_a_cruise(CP, 1.5, 72.0, wired=False), CP.carFingerprint


def test_engaged_frames_do_not_reseed():
  on, off = build(BOSCH_A), None
  with patch.object(gate, "human_following_enabled", lambda _cp: False):
    off = build(BOSCH_A)
  with patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a)):
    for planner in (on, off):
      planner.update(engage_sm(-0.3, 120.0, frame=0))
      planner.update(engage_sm(1.5, 72.0, frame=1))  # engaged (pid): only the normal jerk-limited path runs
  assert on.a_cruise == off.a_cruise


def test_engage_seed_is_the_unlimited_cruise_target():
  args = (False, 20.0, 22.0, 0.5, 0.0, BOSCH_A)
  limited = longitudinal_planner.get_cruise_accel(*args, 0.05, -0.3, True)
  free = longitudinal_planner._cruise_accel_without_jerk_limit(*args, longitudinal_planner._NO_JERK_LIMIT_DT, -0.3, True)
  assert limited == pytest.approx(0.5 - 0.88 * 0.05)  # J_CRUISE interpolated at 22 m/s  # one jerk step toward the target
  assert free == pytest.approx(-1.2)  # clip(v_cruise - v_ego, A_CRUISE_MIN, ...)


# ---- Review fixes: follow time, acceleration base, model-lead freshness ------------------------------------------------
def test_coast_first_gets_the_follow_time_the_mpc_used_this_frame():
  planner = build(BOSCH_A)
  planner.mpc.nrdr.tune.t_follow_offset = lambda _name: 0.3  # a tune offset the raw personality lookup cannot know
  follows = []
  original = planner.bosch_a_coast_first.step

  def spy(*args, **kwargs):
    follows.append(kwargs["follow_s"])
    return original(*args, **kwargs)
  planner.bosch_a_coast_first.step = spy
  with patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, sm, v, a, cruise: (cruise, a)):
    planner.update(submaster(1, personality=log.LongitudinalPersonality.aggressive))
  used = float(planner.mpc.params[0, 4])
  assert follows == [used]
  assert used == pytest.approx(0.75 + 0.3)  # nrdr aggressive 0.75 s plus the tune offset
  assert used != pytest.approx(long_mpc.get_T_FOLLOW(log.LongitudinalPersonality.aggressive))  # the raw lookup SOURCE does not use


def nrdr_stub(max_accel, ceiling):
  return NS(accel_envelope=lambda v_ego, personality: (max_accel, 0.0, ceiling))


def test_human_accel_base_applies_the_personality_ceiling_like_the_cruise_path():
  base = longitudinal_planner.bosch_a_human_accel_base
  assert base(nrdr_stub(1.2, 0.4), False, 20.0, 1) == pytest.approx(0.4)  # ceiling below max accel lowers the base
  assert base(nrdr_stub(1.2, 2.0), False, 20.0, 1) == pytest.approx(1.2)  # a higher ceiling never raises it
  assert base(nrdr_stub(1.2, -1.0), False, 20.0, 1) == 0.0  # same max(0, ceiling) as get_cruise_accel
  assert base(nrdr_stub(1.2, None), False, 20.0, 1) == pytest.approx(1.2)
  assert base(nrdr_stub(1.2, float("nan")), False, 20.0, 1) == pytest.approx(1.2)
  assert base(nrdr_stub(1.2, 0.4), True, 20.0, 1) == ACCEL_MAX  # experimental mode: ACCEL_MAX, as SOURCE


def test_planner_caps_the_mpc_with_the_personality_ceiling():
  planner = build(BOSCH_A)
  planner.nrdr.personality_accel_ceiling = lambda v_ego, personality: 0.3
  seen = spy_mpc_update(planner)
  run(planner, frames=2)
  assert all(kwargs["acceleration_max"] <= 0.3 + 1e-9 for kwargs in seen)
  uncapped = build(BOSCH_A)
  uncapped.nrdr.personality_accel_ceiling = lambda v_ego, personality: None
  seen_uncapped = spy_mpc_update(uncapped)
  run(uncapped, frames=2)
  assert seen_uncapped[-1]["acceleration_max"] > 0.3


def lead_paths_for(sm, planner=None):
  planner = planner or build(BOSCH_A)
  seen = spy_mpc_update(planner)
  with patch.object(LongitudinalPlannerSP, "update", lambda *_: None), \
       patch.object(LongitudinalPlannerSP, "update_targets", lambda self, s, v, a, cruise: (cruise, a)):
    planner.update(sm)
  return seen[-1]["lead_paths"]


def test_fresh_model_frame_is_qualified():
  assert any(path is not None for path in lead_paths_for(submaster(1)))


def test_stale_model_frame_gives_the_raw_extrapolation():
  sm = submaster(1)
  sm.logMonoTime["modelV2"] = NOW_NS - 400_000_000  # older than the 150 ms frame-age limit
  sm["radarState"].mdMonoTime = sm.logMonoTime["modelV2"]
  sm.logMonoTime["radarState"] = NOW_NS - 20_000_000
  assert lead_paths_for(sm) == (None, None)


def test_model_frame_not_matching_the_radar_frame_gives_the_raw_extrapolation():
  sm = submaster(1)
  sm["radarState"].mdMonoTime = sm.logMonoTime["modelV2"] - 50_000_000  # radar built from another model frame
  assert lead_paths_for(sm) == (None, None)


def test_dead_or_invalid_inputs_give_the_raw_extrapolation():
  for name, field in (("modelV2", "valid"), ("radarState", "alive"), ("carState", "freq_ok")):
    sm = submaster(1)
    getattr(sm, field)[name] = False
    assert lead_paths_for(sm) == (None, None), (name, field)
  sm = submaster(1)
  sm["carState"].canValid = False
  assert lead_paths_for(sm) == (None, None)


def test_old_model_timestamp_eof_gives_the_raw_extrapolation():
  sm = submaster(1)
  sm["modelV2"].timestampEof = NOW_NS + BOOT_OFFSET_NS - 400_000_000
  assert model_lead_qualification.qualified_model_leads(sm, NOW_NS, model_lead_qualification.ModelLeadHistory()) is None


def test_qualified_model_leads_rejects_a_clock_that_is_ahead_of_the_pair():
  sm = submaster(1)
  assert model_lead_qualification.qualified_model_leads(sm, NOW_NS, model_lead_qualification.ModelLeadHistory()) is not None
  assert model_lead_qualification.qualified_model_leads(sm, NOW_NS + 1, model_lead_qualification.ModelLeadHistory()) is None
  assert model_lead_qualification.qualified_model_leads(sm, NOW_NS - 200_000_000, model_lead_qualification.ModelLeadHistory()) is None
  assert model_lead_qualification.qualified_model_leads(sm, float(NOW_NS), model_lead_qualification.ModelLeadHistory()) is None
