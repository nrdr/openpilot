"""Pinned MVL host parity; runs without native capnp/acados (including Windows).

Real source definitions execute against recording solver/message boundaries.
This proves host math, state, solver inputs and isolation, NOT native optimizer
or vehicle behavior. See longitudinal_mpc_lib/mvl_manifest.json for exceptions.
"""
import ast
import copy
import hashlib
import json
import math
import os
import subprocess
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.modeld.constants import ModelConstants, index_function

ROOT = Path(__file__).resolve().parents[3]
CORE = "openpilot/selfdrive/controls/lib/"
MPC = CORE + "longitudinal_mpc_lib/"
SP = "openpilot/sunnypilot/selfdrive/controls/lib/"
MANIFEST = json.loads((ROOT / MPC / "mvl_manifest.json").read_text())
DONOR = MANIFEST["donor_commit"]
LEGACY = MANIFEST["legacy_commit"]
PERSONALITY = NS(aggressive=0, standard=1, relaxed=2, econ=3)
STATE = NS(off=0, pid=1, stopping=2, starting=3)
SOURCE = NS(cruise=0, lead0=1, lead1=2, e2e=3, sccVision=4, sccMap=5, speedLimitAssist=6)
MVL_FLAG = 131072
POLLUTED = {
  "HondaLiveLearningGas": False, "HondaStopAccel": -9., "HondaStoppingDecelRateLong": 5.,
  "HondaVEgoStarting": 5., "HondaVEgoStopping": 5., "NrdrRoenAccelerationLimits": True,
  "NrdrCruiseMismatchCorrection": 105., "NrdrStandstillGapExtra": 5.,
  "NrdrCruiseOverspeedAllowance": 10., "NrdrExperimentalEngineBraking": True, "AccelBoostSP": True,
  "LongPidTuneScaleAggressive": 500, "LongPidTuneScaleStandard": 0,
  "LongPidTuneScaleRelaxed": 500, "StaticFeedforwardLong": False,
}
POLLUTED_TUNE = {
  "comfort_brake": 3., "stop_distance": 7.5, "low_speed_jerk_scale": 2.,
  "a_cruise_max_scale": [1.5] * 4,
  "t_follow_offsets": dict.fromkeys(("aggressive", "standard", "relaxed", "econ"), .5),
  "jerk_factors": {name: {"a_change": 3., "j_ego": .2} for name in ("aggressive", "standard", "relaxed", "econ")},
  "lead_consumption": {"m1_anchor": 0., "m2_w_max": 1., "m3_b_eff_max": 4.5},
  "stopping": {"l2_enable": 1., "hold_accel": -1., "pitch_margin": 2.},
}


@lru_cache
def git_source(path, revision=DONOR):
  # Offline C4 staging need not contain .git. Mirror these relative paths under
  # <MVL_PARITY_REFERENCE_ROOT>/<full commit>/ and blob checks still apply.
  if reference_root := os.environ.get("MVL_PARITY_REFERENCE_ROOT"):
    data = (Path(reference_root) / revision / path).read_bytes()
  else:
    fixture = ROOT / "openpilot/nrdr/tests/fixtures/mvl_baseline" / revision / (path + ".txt")
    data = fixture.read_bytes() if fixture.exists() else subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)
  data = data.replace(b"\r\n", b"\n")
  expected = MANIFEST["reference_blobs"][revision][path]
  actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
  if actual != expected:
    raise ValueError(f"Pinned reference blob mismatch: {revision}:{path}: {actual} != {expected}")
  return data.decode()


def source(path):
  return (ROOT / path).read_text(encoding="utf-8")


def forbidden(*_args, **_kwargs):
  raise AssertionError("MVL accessed a custom NRDR setting, tune, or controller")


def definitions(text, env):
  tree = ast.parse(text)
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
  namespace = dict(env, __file__=str(ROOT / MPC / "long_mpc.py"))
  exec(compile(tree, "<actual source definitions>", "exec"), namespace)
  return namespace


def mvl_enabled(cp):
  return cp.brand == "honda" and cp.openpilotLongitudinalControl and bool(cp.flags & MVL_FLAG)


def personality(value, four):
  value = getattr(value, "raw", value)
  if isinstance(value, bool) or not isinstance(value, int) or value not in range(4):
    return 1
  return value if four else min(value, 2)


def environment(**extra):
  env = {
    "np": np, "math": math, "os": os, "CV": CV, "DT_CTRL": .01, "DT_MDL": .05, "CONTROL_N": 17,
    "ACCEL_MIN": -3.5, "ACCEL_MAX": 2., "ModelConstants": ModelConstants, "index_function": index_function,
    "PIDController": PIDController, "FirstOrderFilter": FirstOrderFilter, "LongCtrlState": STATE,
    "car": NS(CarControl=NS(Actuators=NS(LongControlState=STATE))),
    "log": NS(LongitudinalPersonality=PERSONALITY, LongitudinalPlan=NS(LongitudinalPlanSource=SOURCE)),
    "custom": NS(LongitudinalPlanSP=NS(LongitudinalPlanSource=SOURCE)),
    "LongitudinalPlanSource": SOURCE, "_LEAD_ACCEL_TAU": 1.5,
    "time": NS(monotonic=lambda: 100.), "cloudlog": NS(info=lambda *_: None, warning=lambda *_: None),
    "messaging": NS(SubMaster=object, PubMaster=object), "structs": NS(CarParams=object, CarParamsSP=object),
    "mvl_longitudinal_enabled": mvl_enabled, "nrdr_longitudinal_enabled": lambda cp: cp.brand == "honda",
    "legacy_pcm_enabled": lambda *_: False,
    "fixed_pcm_cruise_enabled": lambda *_: False,
    "nrdr_custom_longitudinal_enabled": lambda cp: cp.brand == "honda" and not mvl_enabled(cp),
    "longitudinal_personality": personality, "is_honda_bosch_a_radar": lambda _: True,
    "NrdrLongControl": forbidden, "NrdrLongitudinalPlanner": forbidden, "NrdrLongitudinalMpc": forbidden,
    "Params": forbidden, "get_live_params": forbidden, "LongTune": forbidden, "apply_standstill_gap": forbidden,
    "V_CRUISE_MAX": 145, "V_CRUISE_UNSET": 255, "ACCELERATION_DUE_TO_GRAVITY": 9.81,
  }
  econ = definitions(source(MPC + "mvl_econ.py"), {"np": np})
  env.update({k: v for k, v in econ.items() if not k.startswith("__")})
  env.update(extra)
  return env


def car_params(brand="honda", flagged=True, openlong=True):
  return NS(brand=brand, flags=MVL_FLAG if flagged else 0, openpilotLongitudinalControl=openlong,
            carFingerprint="HONDA_TEST", stopAccel=-.5, longitudinalActuatorDelay=.3,
            steerRatio=15., wheelbase=2.87,
            longitudinalTuning=NS(kiBP=[0., 10., 30.], kiV=[1.2, .8, .5],
                                  deprecated=NS(kpBP=[0.], kpV=[99.])),
            deprecated=NS(startingState=True, stoppingDecelRate=5., vEgoStarting=5., vEgoStopping=5.))


def parsed(text):
  return ast.dump(ast.parse(text), include_attributes=False)


@pytest.mark.parametrize("path,blob", MANIFEST["donor_blobs"].items())
def test_pinned_donor_blobs(path, blob):
  data = git_source(path).encode()
  assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob


def test_bundled_references_work_without_any_git_or_external_reference_folder(monkeypatch):
  monkeypatch.delenv("MVL_PARITY_REFERENCE_ROOT", raising=False)
  monkeypatch.setattr(subprocess, "check_output", forbidden)
  git_source.cache_clear()
  try:
    for revision, paths in MANIFEST["reference_blobs"].items():
      for path in paths:
        assert git_source(path, revision)
  finally:
    git_source.cache_clear()


def test_explicit_reference_folder_normalizes_crlf_and_rejects_modified_source(monkeypatch, tmp_path):
  path = CORE + "longcontrol.py"
  original = git_source(path)
  target = tmp_path / DONOR / path
  target.parent.mkdir(parents=True)
  target.write_bytes(original.replace("\n", "\r\n").encode())
  monkeypatch.setenv("MVL_PARITY_REFERENCE_ROOT", str(tmp_path))
  git_source.cache_clear()
  try:
    assert git_source(path) == original
    target.write_bytes((original + "# modified\n").encode())
    git_source.cache_clear()
    with pytest.raises(ValueError, match="Pinned reference blob mismatch"):
      git_source(path)
  finally:
    git_source.cache_clear()


@pytest.mark.parametrize("current,donor", [
  (MPC + "mvl_accel_boost.py", CORE + "accel_boost.py"),
])
def test_copied_helpers_exact_ast(current, donor):
  expected = git_source(donor)
  assert parsed(source(current)) == parsed(expected)


def test_planner_only_documented_donor_edits():
  expected = git_source(CORE + "longitudinal_planner.py")
  expected = expected.replace("from openpilot.selfdrive.controls.lib.accel_boost import AccelBoost",
                              "from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.mvl_accel_boost import AccelBoost\n" +
                              "from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.mvl_econ import econ_cruise_accel")
  expected = expected.replace("class LongitudinalPlanner(", "class MvlLongitudinalPlanner(")
  expected = expected.replace("from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET",
                              "from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET")
  expected = expected.replace("A_CRUISE_MIN = -0.5", "A_CRUISE_MIN = -0.5\nV_CRUISE_MAX = 145")
  expected = expected.replace("LongitudinalMpc(dt=dt)", "LongitudinalMpc(dt=dt, mvl_enabled=True)")
  expected = expected.replace("self.accel_boost = AccelBoost()", "self.accel_boost = AccelBoost()\n    self.experimental_mode = False")
  expected = expected.replace("self.a_cruise = get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.dt)",
                              "self.a_cruise = (econ_cruise_accel(v_cruise, v_ego, self.a_cruise, self.dt)\n" +
                              "                     if sm['selfdriveState'].personality == 3 else\n" +
                              "                     get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.dt))")
  expected = expected.replace("    longitudinalPlan.accelBoost = float(self.accel_boost.total_boost)\n", "")
  expected = expected.replace(
    "    output_a_target_e2e = self.accel_boost.update(sm, output_a_target_e2e, output_a_target_mpc, self.a_cruise)\n\n" +
    "    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),\n" +
    "                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop),\n" +
    "                  (output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e)]",
    "    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),\n" +
    "                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop)]\n" +
    "    experimental_mode = sm['selfdriveState'].experimentalMode\n" +
    "    if experimental_mode:\n" +
    "      output_a_target_e2e = self.accel_boost.update(sm, output_a_target_e2e, output_a_target_mpc, self.a_cruise)\n" +
    "      candidates.append((output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e))\n" +
    "    elif self.experimental_mode:\n" +
    "      self.accel_boost = AccelBoost()\n" +
    "    self.experimental_mode = experimental_mode",
  )
  expected = expected.replace("longitudinalPlan.allowBrake = True",
                              "longitudinalPlan.allowBrake = True\n    longitudinalPlan.allowThrottle = True")
  assert parsed(source(MPC + "mvl_planner.py")) == parsed(expected)


def node(text, *names):
  result = ast.parse(text)
  for name in names:
    result = next(n for n in result.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
  return result


@pytest.mark.parametrize("names", [
  ("gen_long_model",), ("gen_long_ocp",), ("get_stopped_equivalence_factor",),
  ("get_safe_obstacle_distance",), ("LongitudinalMpc", "set_cost_weights"),
  ("LongitudinalMpc", "set_cur_state"), ("LongitudinalMpc", "extrapolate_lead"),
  ("LongitudinalMpc", "process_lead"), ("LongitudinalMpc", "run"),
])
def test_optimizer_and_lead_methods_exact(names):
  assert ast.dump(node(source(MPC + "long_mpc.py"), *names)) == ast.dump(node(git_source(MPC + "long_mpc.py"), *names))


def test_donor_longcontrol_state_machine_exact():
  assert ast.dump(node(source(CORE + "longcontrol.py"), "long_control_state_trans")) == ast.dump(
    node(git_source(CORE + "longcontrol.py"), "long_control_state_trans"))
  assert parsed(source("openpilot/common/pid.py")) == parsed(git_source("openpilot/common/pid.py"))


def test_pinned_optional_feature_defaults():
  keys = git_source("openpilot/common/params_keys.h")
  assert '{"SmartCruiseControlMap", {PERSISTENT | BACKUP, BOOL, "0"}}' in keys
  assert '{"SmartCruiseControlVision", {PERSISTENT | BACKUP, BOOL, "0"}}' in keys
  assert '{"SpeedLimitMode", {PERSISTENT | BACKUP, INT, "1"}}' in keys
  mode = node(git_source(SP + "speed_limit/common.py"), "Mode")
  values = {n.targets[0].id: ast.literal_eval(n.value) for n in mode.body if isinstance(n, ast.Assign)}
  assert values["information"] == 1 and values["assist"] == 3
  # Sunny's optional boost remains excluded. Unlike the always-E2E donor,
  # manual ExperimentalMode now owns whether the model participates at all.
  names = {n.id for n in ast.walk(ast.parse(source(MPC + "mvl_planner.py"))) if isinstance(n, ast.Name)}
  assert "AccelBoostSP" not in names
  assert "sm['selfdriveState'].experimentalMode" in source(MPC + "mvl_planner.py")


def test_generated_solver_contract_and_constants_are_unchanged():
  current, donor = mpc_pair()
  for name in ("MODEL_NAME", "X_DIM", "U_DIM", "PARAM_DIM", "COST_E_DIM", "COST_DIM", "CONSTR_DIM",
               "X_EGO_OBSTACLE_COST", "X_EGO_COST", "V_EGO_COST", "A_EGO_COST", "J_EGO_COST", "A_CHANGE_COST",
               "DANGER_ZONE_COST", "CRASH_DISTANCE", "LEAD_DANGER_FACTOR", "LIMIT_COST", "ACADOS_SOLVER_TYPE",
               "N", "MAX_T", "COMFORT_BRAKE", "STOP_DISTANCE", "MIN_X_LEAD_FACTOR",
               "T_IDXS_LST", "T_IDXS", "T_DIFFS", "FCW_IDXS"):
    np.testing.assert_array_equal(current[name], donor[name])


@pytest.mark.parametrize("interceptor", [False, True])
@pytest.mark.parametrize("profile", [0, 1, 2, 3])
def test_controller_matches_donor_ignoring_custom_settings_and_hill(interceptor, profile):
  env = environment()
  env["saved_settings"], env["tune_file"] = POLLUTED, POLLUTED_TUNE
  current = definitions(source(CORE + "longcontrol.py"), env)
  donor = definitions(git_source(CORE + "longcontrol.py"), env)
  cp, cp_sp = car_params(), NS(enableGasInterceptor=interceptor)
  actual, expected = (m["LongControl"](cp, cp_sp) for m in (current, donor))
  assert actual.nrdr_controller is None
  rng = np.random.default_rng(8192)
  for frame in range(800):
    stopping = 100 <= frame % 400 < 270
    cs = NS(vEgo=.1 if stopping else float(rng.uniform(0, 40)), aEgo=float(rng.uniform(-4, 2)),
            brakePressed=frame % 73 == 0, cruiseState=NS(standstill=240 < frame % 400 < 300))
    args = (frame % 400 > 8, cs, float(rng.uniform(-5, 4)), stopping, (-3.5, 2.))
    assert actual.update(*args, pitch=(-1.) ** frame, drel=.01, personality=profile) == expected.update(*args)
    assert actual.long_control_state == expected.long_control_state
    for field in ("p", "i", "f", "control", "k_p", "k_i"):
      assert getattr(actual.pid, field) == getattr(expected.pid, field)


class RecordingSolver:
  def __init__(self, *_):
    self.reset()

  def reset(self):
    self.calls = []
    self.values = {}
    self.x0 = np.zeros(3)
    self.status = 0

  def set(self, i, key, value):
    self.calls.append((i, key, np.copy(value)))
    self.values[i, key] = np.copy(value)

  def cost_set(self, i, key, value):
    self.set(i, key, value)

  def constraints_set(self, i, key, value):
    self.set(i, key, value)
    self.x0 = np.copy(value)

  def solve(self):
    # Deterministic boundary double, deliberately NOT an optimizer.
    return self.status

  def get(self, i, key):
    if key == "x":
      t = index_function(i, max_val=10., max_idx=12)
      return np.array([self.x0[1] * t, self.x0[1], self.x0[2]])
    return np.zeros(1)

  def get_stats(self, _):
    return [.001]


def mpc_pair():
  env = environment(AcadosOcpSolverCython=RecordingSolver)
  return definitions(source(MPC + "long_mpc.py"), env), definitions(git_source(MPC + "long_mpc.py"), env)


def assert_solver_equal(actual, expected):
  assert len(actual.solver.calls) == len(expected.solver.calls)
  for a, b in zip(actual.solver.calls, expected.solver.calls, strict=True):
    assert a[:2] == b[:2]
    np.testing.assert_array_equal(a[2], b[2])


@pytest.mark.parametrize("profile", [0, 1, 2])
@pytest.mark.parametrize("bosch", [False, True])
def test_mpc_exact_costs_trajectories_obstacles_fcw_and_reset(profile, bosch):
  current, donor = mpc_pair()
  actual = current["LongitudinalMpc"](mvl_enabled=True, nrdr_enabled=True, honda_bosch_a_radar=bosch)
  expected = donor["LongitudinalMpc"]()
  assert actual.nrdr is actual.tune is None  # mode wins even if caller mistakenly enables NRDR too
  rng = np.random.default_rng(181)
  for frame in range(70):
    speed, accel = float(rng.uniform(0, 40)), float(rng.uniform(-3.5, 2))
    for mpc in (actual, expected):
      mpc.set_cur_state(speed, accel)
      mpc.set_weights(frame % 3 != 0, profile)
      mpc.solver.status = 1 if frame == 33 else 0
    lead = NS(present=frame % 9 != 0, dRel=float(rng.uniform(.5, 60)), vLead=float(rng.uniform(-1, 40)),
              aLeadK=float(rng.uniform(-15, 8)), aLeadTau=1.5, modelProb=.95 if frame % 4 else .5,
              radar=bosch, deprecated=NS(fcw=False), vLeadK=99, radarTrackId=frame)
    radar = NS(leadOne=lead, leadTwo=NS(**(vars(lead) | {"dRel": 40., "vLead": 20.})))
    actual.update(radar, profile, model=NS(leadsV3=POLLUTED_TUNE), v_cruise=100., extra_stop_distance=5.)
    expected.update(radar, profile)
    np.testing.assert_array_equal(actual.params, expected.params)
    for field in ("v_solution", "a_solution", "j_solution", "a_prev"):
      np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    assert actual.source == expected.source
    assert actual.crash_cnt == expected.crash_cnt
    assert actual.solution_status == expected.solution_status
    assert_solver_equal(actual, expected)


def test_econ_changes_only_follow_and_jerk_not_obstacles_or_fcw():
  current, donor = mpc_pair()
  econ = current["LongitudinalMpc"](mvl_enabled=True)
  relaxed = donor["LongitudinalMpc"]()
  lead = NS(present=True, dRel=10., vLead=0., aLeadK=-2., aLeadTau=1.5, modelProb=.99)
  radar = NS(leadOne=lead, leadTwo=lead)
  for mpc, profile in ((econ, 3), (relaxed, 2)):
    mpc.set_cur_state(25., -1.)
    mpc.set_weights(True, profile)
    mpc.update(radar, profile)
  np.testing.assert_array_equal(econ.params[:, :4], relaxed.params[:, :4])
  np.testing.assert_array_equal(econ.params[:, 5], relaxed.params[:, 5])
  np.testing.assert_array_equal(econ.params[:, 4], 2.25)
  assert econ.crash_cnt == relaxed.crash_cnt > 0
  assert econ.solver.values[0, "W"][4, 4] == 300.
  assert econ.solver.values[0, "W"][5, 5] == 7.5


class PlannerSPDouble:
  def __init__(self, *_):
    pass

  def update(self, _):
    pass

  def update_targets(self, sm, _v, a, cruise):
    self.seen_cruise_target = cruise
    return min(cruise, sm.target_limit), a

  def apply_accel_boost(self, _sm, e2e, _mpc, _cruise):
    return e2e

  def publish_longitudinal_plan_sp(self, *_):
    pass


class PlannerMpcDouble:
  def __init__(self, **kwargs):
    self.kwargs = kwargs
    self.tune = self.nrdr = None
    self.source = SOURCE.lead0
    self.crash_cnt = 0
    self.solve_time = .001

  def set_weights(self, prev, personality):
    self.weights = (prev, personality)

  def set_cur_state(self, v, a):
    self.v, self.a = v, a

  def update(self, radar, personality, **_):
    self.v_solution = np.maximum(0., self.v + np.linspace(0., 10., 13) * radar.accel)
    self.a_solution = np.full(13, radar.accel)
    self.j_solution = np.zeros(12)
    self.crash_cnt = radar.crash_cnt
    self.source = SOURCE.lead0
    self.lead_xv_0 = self.lead_xv_1 = np.zeros((13, 2))


class Messages(dict):
  target_limit = 100.
  logMonoTime = {"modelV2": 100}

  def all_checks(self, **_):
    return True


def constant(text, name):
  return next(ast.literal_eval(n.value) for n in ast.parse(text).body
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


def planner_modules(legacy=False):
  host_cruise_max = constant(source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")
  donor_cruise_max = constant(git_source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")
  env = environment(LongitudinalMpc=PlannerMpcDouble, LongitudinalPlannerSP=PlannerSPDouble,
                    T_IDXS_MPC=np.linspace(0., 10., 13), V_CRUISE_MAX=host_cruise_max)
  helpers = definitions(source(CORE + "drive_helpers.py"), env)
  env.update({key: helpers[key] for key in ("get_accel_from_plan", "should_stop")})
  env["AccelBoost"] = definitions(source(MPC + "mvl_accel_boost.py"), env)["AccelBoost"]
  env["MvlLongitudinalPlanner"] = definitions(source(MPC + "mvl_planner.py"), env)["MvlLongitudinalPlanner"]
  return (definitions(source(CORE + "longitudinal_planner.py"), env),
          definitions(git_source(CORE + "longitudinal_planner.py", LEGACY if legacy else DONOR),
                      env | {"V_CRUISE_MAX": host_cruise_max if legacy else donor_cruise_max}))


@pytest.mark.parametrize("profile", [0, 1, 2])
def test_pinned_high_speed_cruise_cap_does_not_import_legacy_maximum(profile):
  current, donor = planner_modules()
  cp = car_params()
  actual, expected = (m["LongitudinalPlanner"](cp, NS(), init_v=44.) for m in (current, donor))
  sm = planner_messages(1, np.random.default_rng(9), profile)
  sm["carState"].vEgo, sm["carState"].vCruise = 44., 160.
  sm["carState"].standstill = False
  sm["controlsState"].longControlState = STATE.pid
  sm["modelV2"].action.desiredAcceleration = 2.
  sm["modelV2"].action.shouldStop = False
  sm["radarState"].accel = 1.
  for planner in (actual, expected):
    planner.update(sm)
    assert planner.seen_cruise_target == 145. * CV.KPH_TO_MS
    assert planner.a_cruise == pytest.approx(-.03)
  assert actual.output_a_target == expected.output_a_target
  assert current["V_CRUISE_MAX"] == 169  # unchanged non-MVL import


def planner_messages(frame, rng, profile):
  speed = float(rng.choice([0., .2, .29, .3, 2., 5., 15., 30., 40.]))
  sm = Messages(carState=NS(vEgo=speed, aEgo=float(rng.uniform(-4, 3)), standstill=speed == 0,
                           gasPressed=frame % 31 > 7, steeringAngleDeg=999., vCruise=255 if frame % 21 == 0 else 110),
                carControl=NS(orientationNED=[0., 1.5, 0.], actuators=NS(accel=-.7)),
                controlsState=NS(forceDecel=frame % 7 == 0, longControlState=STATE.off if frame % 5 == 0 else STATE.pid),
                selfdriveState=NS(enabled=frame % 5 != 0, personality=profile, experimentalMode=frame % 3 == 0),
                vehicleParameters=NS(angleOffsetDeg=900.),
                modelV2=NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 0.])),
                           leadsV3=POLLUTED_TUNE,
                           action=NS(desiredAcceleration=float(rng.uniform(-3., 2.)), shouldStop=frame % 4 == 0)),
                radarState=NS(accel=float(rng.uniform(-3., 2.)), crash_cnt=3 if frame % 9 == 0 else 0))
  sm.target_limit = 18. if frame % 4 == 0 else 100.
  return sm


@pytest.mark.parametrize("profile", [0, 1, 2])
@pytest.mark.parametrize("interceptor", [False, True])
def test_planner_exact_donor_first_three_with_polluted_custom_inputs(profile, interceptor):
  current, donor = planner_modules()
  cp, cp_sp = car_params(), NS(enableGasInterceptor=interceptor)
  actual, expected = (m["LongitudinalPlanner"](cp, cp_sp) for m in (current, donor))
  assert actual.mpc.kwargs["mvl_enabled"]
  assert not hasattr(actual, "nrdr")
  # A persisted setting change cannot turn off the CP-latched path.
  actual.saved_settings, actual.tune_file = POLLUTED.copy(), POLLUTED_TUNE.copy()
  rng = np.random.default_rng(376)
  for frame in range(250):
    sm = planner_messages(frame, rng, profile)
    sm['selfdriveState'].experimentalMode = True  # Exact donor parity when explicitly selected.
    actual.update(sm)
    expected.update(copy.deepcopy(sm))
    for attr in ("output_a_target", "output_should_stop", "a_cruise", "fcw", "seen_cruise_target"):
      assert getattr(actual, attr) == getattr(expected, attr), (frame, attr)
    assert actual.v_desired_filter.x == expected.v_desired_filter.x
    assert vars(actual.accel_boost) == vars(expected.accel_boost)
    assert actual.mpc.weights == expected.mpc.weights
    assert actual.mpc.source == expected.mpc.source
    for attr in ("v_desired_trajectory", "a_desired_trajectory", "j_desired_trajectory"):
      np.testing.assert_array_equal(getattr(actual, attr), getattr(expected, attr))


@pytest.mark.parametrize("brand,flagged", [("toyota", True), ("hyundai", False), ("unknown", True)])
@pytest.mark.parametrize("openlong", [False, True])
@pytest.mark.parametrize("profile", [0, 1, 2, 3])
def test_non_honda_planner_unchanged_from_pre_mode(brand, flagged, openlong, profile):
  current, legacy = planner_modules(legacy=True)
  cp = car_params(brand, flagged, openlong)
  actual, expected = (m["LongitudinalPlanner"](cp, NS()) for m in (current, legacy))
  rng = np.random.default_rng(810)
  for frame in range(40):
    sm = planner_messages(frame, rng, profile)
    actual.update(sm)
    expected.update(copy.deepcopy(sm))
    for attr in ("output_a_target", "output_should_stop", "a_cruise", "fcw", "allow_throttle"):
      assert getattr(actual, attr) == getattr(expected, attr)
    assert actual.mpc.weights == expected.mpc.weights
    assert actual.v_desired_filter.x == expected.v_desired_filter.x


@pytest.mark.parametrize("flagged,openlong", [(False, True), (True, False)])
def test_unflagged_or_stock_honda_keeps_legacy_controller(flagged, openlong):
  sentinel = NS(pid=object())
  module = definitions(source(CORE + "longcontrol.py"), environment(NrdrLongControl=lambda *_: sentinel))
  actual = module["LongControl"](car_params(flagged=flagged, openlong=openlong), NS())
  assert actual.nrdr_controller is sentinel


def test_econ_acceleration_is_fixed_and_braking_stays_donor():
  env = environment()
  legacy = definitions(git_source("openpilot/nrdr/features/longitudinal/longitudinal_planner.py", LEGACY), env)
  donor = definitions(git_source(CORE + "longitudinal_planner.py"), env | {"LongitudinalPlannerSP": PlannerSPDouble})
  for speed in np.linspace(0, 60, 121):
    ceiling = min(legacy["c3_personality_accel_max"](speed, 3),
                  np.interp(speed, [0., 10., 25., 40.], legacy["CRUISE_ACCEL_VALUES"]))
    # Long dt removes the jerk transient, exposing exactly the frozen ceiling.
    assert env["econ_cruise_accel"](100., speed, 0., 100.) == ceiling
    assert env["econ_cruise_accel"](0., speed, 0., .05) == donor["get_cruise_accel"](0., speed, 0., .05)
  econ_source = source(MPC + "mvl_econ.py")
  assert "import Params" not in econ_source and "import LongTune" not in econ_source


class TargetFeatureBoundary:
  """Controlled leaf output; planner routing/arbitration/publication stay real."""
  def __init__(self, *_):
    self.enabled = self.is_enabled = self.is_active = False
    self.state = 0
    self.output_v_target, self.output_a_target = 255., 0.
    self.requested_v_target, self.requested_a_target = 15., -.8
    self.current_lat_acc, self.max_pred_lat_acc = 1.7, 2.1
    self.calls = []

  def update(self, *args):
    self.calls.append(args)
    self.is_enabled = self.is_active = self.enabled
    self.state = int(self.enabled)
    self.output_v_target = self.requested_v_target if self.enabled else 255.
    self.output_a_target = self.requested_a_target if self.enabled else 0.


class SmartCruiseBoundary:
  def __init__(self):
    self.vision, self.map = TargetFeatureBoundary(), TargetFeatureBoundary()

  def update(self, *args):
    self.vision.update(*args)
    self.map.update(*args)


class ResolverBoundary:
  def __init__(self, **kwargs):
    self.kwargs, self.calls = kwargs, []
    self.speed_limit = self.speed_limit_last = self.speed_limit_final = self.speed_limit_final_last = 15.
    self.speed_limit_valid = self.speed_limit_last_valid = True
    self.speed_limit_offset, self.distance, self.source = 0., 100., 1

  def update(self, *args):
    self.calls.append(args)


def integrated_planner_classes():
  """Actual routed MVL -> current SP versus pinned donor -> pinned donor SP.

  Only the solver/feature/message boundaries are doubles. In particular, do
  not substitute PlannerSPDouble: that would miss the MVL-wide target bypass.
  Feature algorithms and cruise-button preferences have separate regressions.
  """
  def message(service):
    payload = (NS(e2eAlerts=NS(), smartCruiseControl=NS(vision=NS(), map=NS()),
                  speedLimit=NS(resolver=NS(), assist=NS())) if service == "longitudinalPlanSP" else NS())
    return NS(logMonoTime=200, **{service: payload})

  env = environment(
    EventsSP=lambda: NS(clear=lambda: None, to_msg=list),
    E2EAlertsHelper=lambda: NS(update=lambda *_: None, green_light_alert=False, lead_depart_alert=False),
    SmartCruiseControl=SmartCruiseBoundary, SpeedLimitResolver=ResolverBoundary,
    SpeedLimitAssist=TargetFeatureBoundary, NrdrSpeedLimitAssist=TargetFeatureBoundary,
    AccelBoostSP=forbidden, get_active_bundle=lambda: None,
    messaging=NS(SubMaster=object, PubMaster=object, new_message=message),
    LongitudinalMpc=PlannerMpcDouble, T_IDXS_MPC=np.linspace(0., 10., 13),
  )
  helpers = definitions(source(CORE + "drive_helpers.py"), env)
  env.update({key: helpers[key] for key in ("get_accel_from_plan", "should_stop")})
  env["AccelBoost"] = definitions(source(MPC + "mvl_accel_boost.py"), env)["AccelBoost"]
  current_env = env | {"V_CRUISE_MAX": constant(source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")}
  current_env["LongitudinalPlannerSP"] = definitions(source(SP + "longitudinal_planner.py"), current_env)["LongitudinalPlannerSP"]
  current_env["MvlLongitudinalPlanner"] = definitions(source(MPC + "mvl_planner.py"), current_env)["MvlLongitudinalPlanner"]
  env["LongitudinalPlannerSP"] = definitions(git_source(SP + "longitudinal_planner.py"), env)["LongitudinalPlannerSP"]
  return (definitions(source(CORE + "longitudinal_planner.py"), current_env)["LongitudinalPlanner"],
          definitions(git_source(CORE + "longitudinal_planner.py"), env)["LongitudinalPlanner"])


def integrated_planner_messages(frame, rng, profile):
  sm = planner_messages(frame, rng, profile)
  sm["carState"].vCruiseCluster = sm["carState"].vCruise
  sm["carControl"].enabled = sm["selfdriveState"].enabled
  sm["carControl"].cruiseControl = NS(override=False)
  sm["radarState"].leadOne = NS(present=True)
  return sm


def test_mvl_constructs_sp_target_features_but_not_custom_accel_or_tune():
  current, _ = integrated_planner_classes()
  planner = current(car_params(), NS(enableGasInterceptor=False))
  assert planner.mvl_enabled and planner.mpc.kwargs["mvl_enabled"]
  assert isinstance(planner.scc, SmartCruiseBoundary)
  assert isinstance(planner.resolver, ResolverBoundary)
  assert isinstance(planner.sla, TargetFeatureBoundary)
  assert planner.accel_boost_sp is planner.mpc.nrdr is planner.mpc.tune is None
  assert not hasattr(planner, "nrdr")


@pytest.mark.parametrize("profile", [0, 1, 2])
@pytest.mark.parametrize("interceptor", [False, True])
def test_integrated_sp_disabled_features_preserve_numerical_donor_parity(profile, interceptor):
  actual, expected = (cls(car_params(), NS(enableGasInterceptor=interceptor)) for cls in integrated_planner_classes())
  actual.saved_settings, actual.tune_file = POLLUTED.copy(), POLLUTED_TUNE.copy()
  rng = np.random.default_rng(376)
  for frame in range(80):
    sm = integrated_planner_messages(frame, rng, profile)
    sm["selfdriveState"].experimentalMode = True  # Donor always includes its model candidate.
    actual.update(sm)
    expected.update(copy.deepcopy(sm))
    for attr in ("output_v_target", "output_a_target", "output_should_stop", "a_cruise", "fcw", "source"):
      assert getattr(actual, attr) == getattr(expected, attr), (frame, attr)
    assert actual.source == SOURCE.cruise
    assert actual.v_desired_filter.x == expected.v_desired_filter.x
    assert vars(actual.accel_boost) == vars(expected.accel_boost)
    assert actual.mpc.weights == expected.mpc.weights
    assert (actual.mpc.v, actual.mpc.a, actual.mpc.source) == (expected.mpc.v, expected.mpc.a, expected.mpc.source)
    for attr in ("v_desired_trajectory", "a_desired_trajectory", "j_desired_trajectory"):
      np.testing.assert_array_equal(getattr(actual, attr), getattr(expected, attr))
    # Disabled feature outputs are neutral, not a skipped SP lifecycle.
    for feature in (actual.scc.vision, actual.scc.map, actual.sla, actual.resolver):
      assert len(feature.calls) == frame + 1

  sent_actual, sent_expected = {}, {}
  actual.publish(sm, NS(send=lambda key, value: sent_actual.update({key: value})))
  expected.publish(sm, NS(send=lambda key, value: sent_expected.update({key: value})))
  assert vars(sent_actual["longitudinalPlanSP"]) == vars(sent_expected["longitudinalPlanSP"])


def test_retired_host_runtime_is_absent():
  assert not (ROOT / "openpilot/nrdr/features/longitudinal/engine_braking.py").exists()
  controls = source("openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py")
  for text in ("engine_brake_context", "pcmEngineBrake", "NrdrCruiseOverspeedAllowance", "NrdrExperimentalEngineBraking"):
    assert text not in controls
  for path in ("openpilot/nrdr/features/longitudinal/longitudinal_planner.py",
               "openpilot/nrdr/features/longitudinal/__init__.py", "openpilot/sunnypilot/nrdr/longitudinal_planner.py"):
    assert "apply_cruise_overspeed_allowance" not in source(path)


def test_mvl_mode_never_reads_tune_file_or_live_custom_params():
  for path in ("mvl_planner.py", "mvl_econ.py", "mvl_accel_boost.py"):
    tree = ast.parse(source(MPC + path))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names.intersection({"LongTune", "Params", "get_live_params", "NrdrLongitudinalPlanner", "NrdrLongitudinalMpc"})


@pytest.mark.parametrize("feature_name,expected_source", [
  ("vision", SOURCE.sccVision), ("map", SOURCE.sccMap), ("sla", SOURCE.speedLimitAssist),
])
@pytest.mark.parametrize("experimental", [False, True])
def test_routed_mvl_sp_target_features_reach_planner_and_publication(feature_name, expected_source, experimental):
  sent = {}
  current, _ = integrated_planner_classes()
  planner, neutral = (current(car_params(), NS(enableGasInterceptor=True), init_v=25.) for _ in range(2))
  feature = planner.sla if feature_name == "sla" else getattr(planner.scc, feature_name)
  feature.enabled = True
  sm = integrated_planner_messages(1, np.random.default_rng(123), 1)
  sm["carState"].vEgo, sm["carState"].vCruise, sm["carState"].vCruiseCluster = 25., 110., 110.
  sm["carState"].standstill = sm["carState"].gasPressed = False
  sm["selfdriveState"].experimentalMode = experimental
  sm["modelV2"].action.desiredAcceleration, sm["modelV2"].action.shouldStop = 2., False
  sm["radarState"].accel = 1.
  planner.saved_settings, planner.tune_file = POLLUTED.copy(), POLLUTED_TUNE.copy()
  planner.update(sm)
  neutral.update(copy.deepcopy(sm))
  assert planner.source == expected_source
  assert feature.is_active and len(feature.calls) == 1
  assert planner.output_v_target == feature.requested_v_target < neutral.output_v_target
  assert planner.mpc.a == feature.requested_a_target
  assert planner.a_cruise < neutral.a_cruise
  assert planner.output_a_target < neutral.output_a_target
  assert planner.accel_boost_sp is planner.mpc.tune is planner.mpc.nrdr is None
  planner.publish(sm, NS(send=lambda key, value: sent.update({key: value})))
  assert set(sent) == {"longitudinalPlan", "longitudinalPlanSP"}
  main = sent["longitudinalPlan"].longitudinalPlan
  assert main.allowBrake and main.allowThrottle
  assert main.aTarget == planner.output_a_target and main.shouldStop == planner.output_should_stop
  assert main.hasLead is True
  sp = sent["longitudinalPlanSP"].longitudinalPlanSP
  assert sp.longitudinalPlanSource == expected_source
  assert sp.vTarget == feature.requested_v_target and sp.aTarget == planner.output_a_target
  published_feature = sp.speedLimit.assist if feature_name == "sla" else getattr(sp.smartCruiseControl, feature_name)
  assert published_feature.enabled and published_feature.active
  assert published_feature.vTarget == feature.requested_v_target
  assert published_feature.aTarget == feature.requested_a_target
  assert sp.speedLimit.resolver.speedLimitValid and sp.speedLimit.resolver.speedLimit == 15.
  assert sp.e2eAlerts.greenLightAlert is False and sp.e2eAlerts.leadDepartAlert is False

  # Disabling the target source returns ownership to cruise on the next tick;
  # it must not require re-instantiating or changing the MVL controller/tune.
  feature.enabled = False
  planner.update(sm)
  assert not feature.is_active and len(feature.calls) == 2
  assert planner.source == SOURCE.cruise
  assert planner.output_v_target == sm["carState"].vCruise * CV.KPH_TO_MS


@pytest.mark.parametrize("brand", ["toyota", "hyundai", "unknown"])
@pytest.mark.parametrize("interceptor", [False, True])
def test_non_honda_controller_unchanged(brand, interceptor):
  env = environment()
  modules = [definitions(text, env) for text in (source(CORE + "longcontrol.py"), git_source(CORE + "longcontrol.py"))]
  actual, expected = (module["LongControl"](car_params(brand), NS(enableGasInterceptor=interceptor)) for module in modules)
  for frame in range(80):
    cs = NS(vEgo=0. if frame > 20 else 20., aEgo=-.5, brakePressed=frame == 40,
            cruiseState=NS(standstill=30 < frame < 50))
    args = (frame > 5, cs, -1. if frame > 20 else 1., 20 < frame < 60, (-3.5, 2.))
    assert actual.update(*args) == expected.update(*args)
    assert actual.long_control_state == expected.long_control_state
