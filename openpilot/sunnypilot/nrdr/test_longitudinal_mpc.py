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


def make_policy():
  return NrdrLongitudinalMpc(
    DT,
    MPC_TIMES,
    np.diff(MPC_TIMES, prepend=[0.0]),
    -1.2,
    2.0,
    0.5,
    -3.5,
  )


def model_lead(prob=0.9, speed=20.0, accel=0.0):
  times = np.arange(0.0, 12.0, 2.0)
  return SimpleNamespace(
    prob=prob,
    x=40.0 + speed * times + 0.5 * accel * times ** 2,
    v=speed + accel * times,
  )


def radar_lead(present=True, speed=20.0, filtered_speed=None, accel=0.0,
               accel_tau=1.0, distance=40.0, track_id=7):
  return SimpleNamespace(
    present=present,
    dRel=distance,
    vLead=speed,
    vLeadK=speed if filtered_speed is None else filtered_speed,
    aLeadK=accel,
    aLeadTau=accel_tau,
    radarTrackId=track_id,
    modelProb=0.9,
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
