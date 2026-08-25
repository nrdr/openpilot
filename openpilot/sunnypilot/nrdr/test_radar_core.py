import math
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.honda.values import CAR as HONDA_CAR
from openpilot.sunnypilot.nrdr.radar import NrdrRadar
from openpilot.sunnypilot.nrdr.radar_core import COAST_CYCLES, CivicBoschKalmanParams, CivicBoschTrack


DT = 0.06
V_EGO = 25.0


def make_track(v_lead: float = 20.0) -> CivicBoschTrack:
  return CivicBoschTrack(7, v_lead, CivicBoschKalmanParams())


def update_measured(track: CivicBoschTrack, v_lead: float, count: int = 50) -> None:
  for _ in range(count):
    track.update(40.0, 0.0, v_lead - V_EGO, v_lead, True, V_EGO)


def test_kalman_gain():
  params = CivicBoschKalmanParams()
  assert params.K[0][0] == pytest.approx(0.3513, abs=0.01)
  assert params.K[1][0] == pytest.approx(1.2477, abs=0.01)


def test_nrdr_radar_uses_current_radar_tracks_service_for_freshness():
  radar = NrdrRadar(SimpleNamespace(
    brand="honda",
    radarUnavailable=False,
    carFingerprint=HONDA_CAR.HONDA_CIVIC_BOSCH,
  ))
  point = SimpleNamespace(
    trackId=7,
    dRel=40.0,
    yRel=0.5,
    vRel=-2.0,
    deprecated=SimpleNamespace(measured=True),
  )
  radar_data = SimpleNamespace(points=[point])
  sm = SimpleNamespace(recv_frame={"radarTracks": 10})

  assert radar.points(sm, radar_data)[7][3] is True
  assert radar.points(sm, radar_data)[7][3] is False
  sm.recv_frame["radarTracks"] = 11
  assert radar.points(sm, radar_data)[7][3] is True


def test_measured_track_converges():
  track = make_track()
  update_measured(track, 20.0)
  assert track.vLeadK == pytest.approx(20.0, abs=0.05)
  assert track.aLeadK == pytest.approx(0.0, abs=0.05)


def test_unmeasured_track_coasts():
  track = make_track()
  velocity = 20.0
  for _ in range(60):
    velocity -= 2.0 * DT
    track.update(40.0, 0.0, velocity - V_EGO, velocity, True, V_EGO)
  previous_velocity = track.vLeadK
  previous_accel = track.aLeadK

  track.update(40.0, 0.0, math.nan, math.nan, False, V_EGO)

  assert track.vLeadK == pytest.approx(previous_velocity + previous_accel * DT, abs=1e-9)
  assert track.get_RadarState()["vRel"] == pytest.approx(track.vLeadK - V_EGO, abs=1e-9)


def test_unmeasured_track_falls_back_after_budget():
  track = make_track()
  update_measured(track, 20.0)
  for _ in range(COAST_CYCLES + 1):
    track.update(40.0, 0.0, 0.0, V_EGO, False, V_EGO)
  state = track.get_RadarState()
  assert state["vRel"] == 0.0
  assert state["vLead"] == V_EGO


def test_nan_cannot_poison_track():
  track = make_track(math.nan)
  for _ in range(10):
    track.update(40.0, 0.0, math.nan, math.nan, True, V_EGO)
  state = track.get_RadarState()
  assert all(math.isfinite(value) for value in state.values() if isinstance(value, float))
  assert not track.measured


def test_braking_convergence():
  rng = np.random.default_rng(42)
  track = make_track()
  velocity = 20.0
  for _ in range(60):
    measurement = velocity + rng.normal(0.0, 0.3)
    track.update(40.0, 0.0, measurement - V_EGO, measurement, True, V_EGO)

  history = []
  for _ in range(25):
    velocity -= 3.0 * DT
    measurement = velocity + rng.normal(0.0, 0.3)
    track.update(40.0, 0.0, measurement - V_EGO, measurement, True, V_EGO)
    history.append(track.aLeadK)

  cycles = next(index for index, accel in enumerate(history, start=1) if accel <= -1.5)
  assert cycles <= 7
