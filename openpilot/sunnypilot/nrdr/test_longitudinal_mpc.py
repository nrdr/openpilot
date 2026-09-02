from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.sunnypilot.nrdr.long_tune import LEAD_FIELDS
from openpilot.sunnypilot.nrdr.longitudinal_mpc import (
  BRAKE_ENGAGE_DELAY,
  BRAKE_PERSISTENCE,
  CROSSFADE_FRAMES,
  MIN_TRACK_AGE,
  NrdrLongitudinalMpc,
)


DT = 0.05
MPC_TIMES = np.linspace(0.0, 10.0, 13)
OPENPILOT_ROOT = Path(__file__).parents[2]


def make_policy(*, honda_bosch_a_radar: bool = False):
  return NrdrLongitudinalMpc(
    DT,
    MPC_TIMES,
    np.diff(MPC_TIMES, prepend=[0.0]),
    -1.2,
    2.0,
    0.5,
    -3.5,
    honda_bosch_a_radar=honda_bosch_a_radar,
  )


def model_lead(prob=0.9, speed=20.0, accel=0.0):
  times = np.arange(0.0, 12.0, 2.0)
  return SimpleNamespace(
    prob=prob,
    x=40.0 + speed * times + 0.5 * accel * times ** 2,
    v=speed + accel * times,
  )


def radar_lead(present=True, speed=20.0, filtered_speed=None, accel=0.0,
               accel_tau=1.0, distance=40.0, track_id=7, radar=True,
               model_prob=0.9, fcw=False):
  return SimpleNamespace(
    present=present,
    dRel=distance,
    vLead=speed,
    vLeadK=speed if filtered_speed is None else filtered_speed,
    aLeadK=accel,
    aLeadTau=accel_tau,
    radarTrackId=track_id,
    modelProb=model_prob,
    radar=radar,
    deprecated=SimpleNamespace(fcw=fcw),
  )


def test_filtered_velocity_crossfades_after_track_birth():
  policy = make_policy()
  model = model_lead()
  radar = radar_lead(filtered_speed=18.5)
  assert policy._lead_trajectory(model, radar, 0, 25.0)[0, 1] == pytest.approx(20.0)
  for _ in range(CROSSFADE_FRAMES):
    trajectory = policy._lead_trajectory(model, radar, 0, 25.0)
  assert trajectory[0, 1] == pytest.approx(18.5)


def test_anchor_escape_uses_raw_velocity_during_hard_accel():
  policy = make_policy()
  radar = radar_lead(filtered_speed=18.5, accel=3.0)
  for _ in range(CROSSFADE_FRAMES + 1):
    trajectory = policy._lead_trajectory(model_lead(), radar, 0, 25.0)
  assert trajectory[0, 1] == pytest.approx(20.0)


def test_missing_lead_produces_monotonic_clear_path():
  policy = make_policy()
  trajectory = policy._lead_trajectory(model_lead(), radar_lead(present=False), 0, 25.0)
  assert np.all(np.diff(trajectory[:, 0]) >= 0.0)
  assert np.all(trajectory[:, 1] == 35.0)


def test_effective_brake_requires_track_age_and_persistence():
  policy = make_policy()
  policy.tune.lead_consumption["m3_b_eff_max"] = 4.0
  lead = radar_lead(accel=-3.0, accel_tau=0.0)
  frames = int((MIN_TRACK_AGE + BRAKE_PERSISTENCE + BRAKE_ENGAGE_DELAY) / DT) + 3
  outputs = [policy._effective_brake(lead, 2.5, 0) for _ in range(frames)]
  assert outputs[0] == 2.5
  assert outputs[-1] == pytest.approx(3.0)


def test_default_tune_keeps_accel_projection_disabled():
  policy = make_policy()
  assert policy.tune.lead_consumption == {name: values[0] for name, values in LEAD_FIELDS.items()}
  assert policy.tune.lead_consumption["m2_w_max"] == 0.0
  assert policy.tune.lead_consumption["m3_b_eff_max"] == 2.5


def test_prepare_returns_solver_sized_trajectories():
  policy = make_policy()
  model = SimpleNamespace(leadsV3=[model_lead(0.9), model_lead(0.2)])
  radar = SimpleNamespace(leadOne=radar_lead(), leadTwo=radar_lead(present=False))
  result = policy.prepare(30.0, model, radar, 1, 25.0, 1.45)
  assert result.lead_0.shape == (13, 2)
  assert result.obstacles.shape == (13, 3)
  assert result.status
  assert result.lead_probability == pytest.approx(0.9)


@pytest.mark.parametrize(
  ("v_ego", "distance", "lead_speed"),
  [
    (27.0, 12.0, 27.0),
    (27.0, 35.0, 20.0),
  ],
)
def test_bosch_raw_geometry_boundaries_use_raw_fallback(v_ego, distance, lead_speed):
  policy = make_policy(honda_bosch_a_radar=True)
  raw = np.column_stack((np.linspace(distance, distance + 10.0, len(MPC_TIMES)),
                         np.full(len(MPC_TIMES), lead_speed)))
  result = policy._lead_trajectory(
    model_lead(), radar_lead(distance=distance, speed=lead_speed), 0, v_ego, raw,
  )
  assert result is raw


@pytest.mark.parametrize(
  ("v_ego", "distance", "lead_speed"),
  [
    (27.0, 12.001, 27.0),
    (27.0, 35.01, 20.0),
  ],
)
def test_bosch_just_above_raw_geometry_boundaries_keeps_model_horizon(v_ego, distance, lead_speed):
  policy = make_policy(honda_bosch_a_radar=True)
  raw = np.column_stack((np.linspace(distance, distance + 10.0, len(MPC_TIMES)),
                         np.full(len(MPC_TIMES), lead_speed)))
  result = policy._lead_trajectory(
    model_lead(), radar_lead(distance=distance, speed=lead_speed), 0, v_ego, raw,
  )
  assert result is not raw


def test_bosch_nonurgent_pessimistic_acceleration_keeps_model_horizon():
  policy = make_policy(honda_bosch_a_radar=True)
  raw = np.zeros((len(MPC_TIMES), 2))
  result = policy._lead_trajectory(
    model_lead(),
    radar_lead(distance=36.832, speed=3.497, accel=-5.466),
    0,
    9.606,
    raw,
  )
  assert result is not raw


@pytest.mark.parametrize("slot", [0, 1])
@pytest.mark.parametrize("invalid", ["probability", "length", "nan_model", "nan_anchor", "nan_ego"])
def test_invalid_bosch_model_horizon_falls_back_to_finite_raw_trajectory(slot, invalid):
  policy = make_policy(honda_bosch_a_radar=True)
  model = model_lead()
  radar = radar_lead(distance=40.0, speed=20.0)
  v_ego = 25.0
  raw = np.column_stack((np.linspace(40.0, 80.0, len(MPC_TIMES)), np.full(len(MPC_TIMES), 20.0)))

  if invalid == "probability":
    model.prob = 0.5
  elif invalid == "length":
    model.x = model.x[:-1]
  elif invalid == "nan_model":
    model.v[1] = np.nan
  elif invalid == "nan_anchor":
    radar.dRel = np.nan
    raw[0, 0] = np.nan
  elif invalid == "nan_ego":
    v_ego = np.nan
    raw[:] = np.nan

  result = policy._lead_trajectory(model, radar, slot, v_ego, raw)
  assert result.shape == (len(MPC_TIMES), 2)
  assert np.all(np.isfinite(result))


def test_raw_geometry_guard_is_bosch_radar_only():
  raw = np.zeros((len(MPC_TIMES), 2))
  close_lead = radar_lead(distance=10.0, speed=20.0)
  assert make_policy()._lead_trajectory(model_lead(), close_lead, 0, 25.0, raw) is not raw
  assert make_policy(honda_bosch_a_radar=True)._lead_trajectory(
    model_lead(), radar_lead(distance=10.0, speed=20.0, radar=False), 0, 25.0, raw,
  ) is not raw


def test_bosch_fcw_authority_requires_strict_bit_probability_closing_speed_and_ttc():
  policy = make_policy(honda_bosch_a_radar=True)
  lead = radar_lead(distance=8.0, speed=2.0, model_prob=0.99, fcw=True)
  assert policy.fcw_authorized(lead, 8.0)

  assert not policy.fcw_authorized(radar_lead(distance=8.0, speed=2.0, model_prob=0.99, fcw=False), 8.0)
  assert not policy.fcw_authorized(radar_lead(distance=8.0, speed=2.0, model_prob=0.9, fcw=True), 8.0)
  assert not policy.fcw_authorized(radar_lead(distance=8.0, speed=7.6, model_prob=0.99, fcw=True), 8.0)
  assert not policy.fcw_authorized(radar_lead(distance=25.0, speed=2.0, model_prob=0.99, fcw=True), 8.0)
  assert not policy.fcw_authorized(radar_lead(distance=8.0, speed=2.0, radar=False, model_prob=0.99, fcw=True), 8.0)

  assert not policy.fcw_authorized(radar_lead(distance=24.0, speed=2.0, model_prob=0.99, fcw=True), 8.0)
  assert policy.fcw_authorized(radar_lead(distance=23.999, speed=2.0, model_prob=0.99, fcw=True), 8.0)


@pytest.mark.parametrize("field", ["dRel", "vLead", "modelProb"])
def test_bosch_fcw_authority_rejects_nonfinite_inputs(field):
  policy = make_policy(honda_bosch_a_radar=True)
  lead = radar_lead(distance=8.0, speed=2.0, model_prob=0.99, fcw=True)
  setattr(lead, field, np.nan)
  assert not policy.fcw_authorized(lead, 8.0)
  assert not policy.fcw_authorized(radar_lead(distance=8.0, speed=2.0, model_prob=0.99, fcw=True), np.nan)


def test_non_bosch_fcw_path_preserves_generic_authority():
  policy = make_policy()
  assert policy.fcw_authorized(radar_lead(present=False, radar=False, model_prob=0.0, fcw=False), np.nan)


def test_mpc_and_planner_both_consume_bosch_fcw_authority():
  mpc_source = (OPENPILOT_ROOT / "selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py").read_text()
  planner_source = (OPENPILOT_ROOT / "selfdrive/controls/lib/longitudinal_planner.py").read_text()

  assert "lead_probability > 0.9 and self.nrdr.fcw_authorized(radarstate.leadOne, v_ego)" in mpc_source
  assert "self.mpc.nrdr.fcw_authorized(sm['radarState'].leadOne, v_ego)" in planner_source
  assert "honda_bosch_a_radar=self.honda_bosch_a_radar" in planner_source
