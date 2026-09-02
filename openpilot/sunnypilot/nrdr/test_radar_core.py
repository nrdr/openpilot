import math
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.honda.values import CAR as HONDA_CAR, HONDA_BOSCH_A
from openpilot.cereal import log
from openpilot.sunnypilot.nrdr.radar import (
  HONDA_BOSCH_A_LOW_SPEED_MIN_SWEEPS,
  NrdrRadar,
  is_honda_bosch_a_radar,
)
from openpilot.sunnypilot.nrdr.radar_core import COAST_CYCLES, CivicBoschKalmanParams, CivicBoschTrack


DT = 0.06
V_EGO = 25.0


def make_track(v_lead: float = 20.0, identifier: int = 7) -> CivicBoschTrack:
  return CivicBoschTrack(identifier, v_lead, CivicBoschKalmanParams())


def update_measured(track: CivicBoschTrack, v_lead: float, count: int = 50) -> None:
  for _ in range(count):
    track.update(40.0, 0.0, v_lead - V_EGO, v_lead, True, V_EGO)


def make_positioned_track(identifier: int, distance: float, measured_sweeps: int, *,
                          y_rel: float = 0.0, v_ego: float = 1.0, v_rel: float = 0.0) -> CivicBoschTrack:
  track = make_track(v_ego + v_rel, identifier)
  for _ in range(measured_sweeps):
    track.update(distance, y_rel, v_rel, v_ego + v_rel, True, v_ego)
  return track


def make_model_lead(distance: float, *, probability: float = 0.99, v_ego: float = 1.0):
  return SimpleNamespace(
    prob=probability,
    x=[distance + 1.52],
    y=[0.0],
    v=[v_ego],
    xStd=[1.0],
    yStd=[1.0],
    vStd=[1.0],
  )


def make_radar(*, fingerprint=None, unavailable: bool = False, brand: str = "honda") -> NrdrRadar:
  fingerprint = fingerprint if fingerprint is not None else next(iter(HONDA_BOSCH_A))
  return NrdrRadar(SimpleNamespace(brand=brand, radarUnavailable=unavailable, carFingerprint=fingerprint))


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


@pytest.mark.parametrize("fingerprint", sorted(HONDA_BOSCH_A, key=str))
def test_all_plain_honda_bosch_a_platforms_use_nrdr_radar_semantics(fingerprint):
  cp = SimpleNamespace(brand="honda", radarUnavailable=False, carFingerprint=fingerprint)
  assert is_honda_bosch_a_radar(cp)
  assert NrdrRadar(cp).active


def test_unavailable_or_non_bosch_a_radar_does_not_use_nrdr_semantics():
  assert not make_radar(unavailable=True).active
  assert not make_radar(fingerprint=HONDA_CAR.HONDA_CIVIC).active
  assert not make_radar(fingerprint=HONDA_CAR.HONDA_CLARITY).active
  assert not make_radar(brand="toyota").active


def test_non_bosch_adapter_leaves_generic_points_and_lead_selection_untouched():
  radar = make_radar(fingerprint=HONDA_CAR.HONDA_CIVIC)
  point = SimpleNamespace(trackId=7, dRel=40.0, yRel=0.5, vRel=-2.0)
  sm = SimpleNamespace(recv_frame={"radarTracks": 10})
  assert radar.points(sm, SimpleNamespace(points=[point])) == {7: [40.0, 0.5, -2.0]}

  lead_dict = {"present": False}
  assert radar.select_lead(0, {}, make_model_lead(40.0), 20.0, True, 0.99, lead_dict, True) is lead_dict
  radar.update_preferred_staleness(0, {}, make_model_lead(40.0), 20.0, True, 0.99)
  assert radar.prev_lead_track_ids == [-1, -1]


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
  previous_sweeps = track.measured_sweep_count

  track.update(40.0, 0.0, math.nan, math.nan, False, V_EGO)

  assert track.vLeadK == pytest.approx(previous_velocity + previous_accel * DT, abs=1e-9)
  assert track.get_RadarState()["vRel"] == pytest.approx(track.vLeadK - V_EGO, abs=1e-9)
  assert track.measured_sweep_count == previous_sweeps


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


def test_low_speed_takeover_requires_three_real_sweeps_not_model_cycles():
  radar = make_radar()
  track = make_positioned_track(4, 5.0, HONDA_BOSCH_A_LOW_SPEED_MIN_SWEEPS - 1)
  for _ in range(20):
    track.update(5.0, 0.0, 0.0, 1.0, False, 1.0)

  lead = radar.select_lead(
    0, {4: track}, make_model_lead(5.0, probability=0.0), 1.0, False, 0.0,
    {"present": False}, True,
  )
  assert not lead["present"]

  track.update(5.0, 0.0, 0.0, 1.0, True, 1.0)
  lead = radar.select_lead(
    0, {4: track}, make_model_lead(5.0, probability=0.0), 1.0, False, 0.0,
    {"present": False}, True,
  )
  assert lead["present"]
  assert lead["radarTrackId"] == 4


def test_immature_closer_track_does_not_replace_established_lead():
  radar = make_radar()
  closer = make_positioned_track(2, 2.0, 1)
  established = make_positioned_track(7, 7.0, 5)
  lead = radar.select_lead(
    0, {2: closer, 7: established}, make_model_lead(7.0), 1.0, True, 0.99,
    established.get_RadarState(0.99), True,
  )
  assert lead["radarTrackId"] == 7


def test_mature_strict_candidate_can_replace_established_lead():
  radar = make_radar()
  candidate = make_positioned_track(2, 2.0, 3)
  established = make_positioned_track(7, 7.0, 5)
  lead = radar.select_lead(
    0, {2: candidate, 7: established}, make_model_lead(2.0), 1.0, True, 0.99,
    established.get_RadarState(0.99), True,
  )
  assert lead["radarTrackId"] == 2


def test_preferred_low_speed_lead_blocks_unrelated_closer_track_without_model():
  radar = make_radar()
  closer = make_positioned_track(2, 2.0, 3)
  preferred = make_positioned_track(7, 7.0, 5)
  radar.prev_lead_track_ids[0] = 7
  lead = radar.select_lead(
    0, {2: closer, 7: preferred}, make_model_lead(7.0, probability=0.0), 1.0, False, 0.0,
    {"present": False}, True,
  )
  assert lead["radarTrackId"] == 7


@pytest.mark.parametrize("lead_index", [0, 1])
def test_mature_relaxed_preferred_association_works_at_highway_speed_for_both_leads(lead_index):
  radar = make_radar()
  preferred = make_positioned_track(7, 40.0, 3, y_rel=1.4, v_ego=20.0)
  other = make_positioned_track(8, 40.0, 3, y_rel=3.0, v_ego=20.0)
  radar.prev_lead_track_ids[lead_index] = 7

  selected = radar.associate_model_lead(
    lead_index, {7: preferred, 8: other}, make_model_lead(40.0, v_ego=20.0), 20.0,
  )
  assert selected is preferred


def test_immature_preferred_track_cannot_use_relaxed_continuity():
  radar = make_radar()
  preferred = make_positioned_track(7, 40.0, 1, y_rel=1.4, v_ego=20.0)
  radar.prev_lead_track_ids[0] = 7
  assert radar.associate_model_lead(0, {7: preferred}, make_model_lead(40.0, v_ego=20.0), 20.0) is None


def test_recorded_strict_match_identity_distinguishes_relaxed_continuity():
  radar = make_radar()
  track = make_positioned_track(7, 40.0, 3, y_rel=0.2, v_ego=20.0)
  lead = make_model_lead(40.0, v_ego=20.0)
  radar.record_lead(0, {7: track}, lead, 20.0, True, 0.99, track.get_RadarState(0.99))
  assert radar.strict_match_track_ids[0] == 7
  assert radar.strict_fcw_authority(0, track.get_RadarState(0.99), 0.99)

  track.yRel = 1.4
  radar.record_lead(0, {7: track}, lead, 20.0, True, 0.99, track.get_RadarState(0.99))
  assert radar.prev_lead_track_ids[0] == 7
  assert radar.strict_match_track_ids[0] == -1
  assert not radar.strict_fcw_authority(0, track.get_RadarState(0.99), 0.99)


def test_fcw_authority_requires_strict_radar_lead_and_high_model_probability():
  radar = make_radar()
  track = make_positioned_track(7, 20.0, 3)
  state = track.get_RadarState(0.99)
  radar.strict_match_track_ids[0] = 7
  assert radar.strict_fcw_authority(0, state, 0.99)
  assert not radar.strict_fcw_authority(0, state, 0.9)
  assert not radar.strict_fcw_authority(1, state, 0.99)
  assert not radar.strict_fcw_authority(0, {**state, "radar": False}, 0.99)
  assert not radar.strict_fcw_authority(0, state, math.nan)
  assert not radar.strict_fcw_authority(0, state, "invalid")
  assert not radar.strict_fcw_authority(0, {**state, "radarTrackId": object()}, 0.99)
  assert not make_radar(fingerprint=HONDA_CAR.HONDA_CIVIC).strict_fcw_authority(0, state, 0.99)


def test_deprecated_fcw_authority_round_trips_and_false_preserves_generic_encoding():
  strict = log.RadarState.new_message()
  strict.leadOne.present = True
  strict.leadOne.deprecated.fcw = True
  with log.RadarState.from_bytes(strict.to_bytes()) as restored:
    assert restored.leadOne.present
    assert restored.leadOne.deprecated.fcw

  implicit_false = log.RadarState.new_message()
  implicit_false.leadOne.present = True
  explicit_false = log.RadarState.new_message()
  explicit_false.leadOne.present = True
  explicit_false.leadOne.deprecated.fcw = False
  assert explicit_false.to_bytes() == implicit_false.to_bytes()


def test_radar_state_producer_sets_deprecated_fcw_only_for_current_strict_match():
  radar = make_radar()
  strict_track = make_positioned_track(7, 20.0, 3, y_rel=0.2, v_ego=8.0, v_rel=-6.0)
  relaxed_track = make_positioned_track(8, 20.0, 3, y_rel=1.4, v_ego=8.0, v_rel=-6.0)
  model = make_model_lead(20.0, v_ego=2.0)
  strict_state = strict_track.get_RadarState(0.99)
  relaxed_state = relaxed_track.get_RadarState(0.99)
  radar.record_lead(0, {7: strict_track}, model, 8.0, True, 0.99, strict_state)
  radar.record_lead(1, {8: relaxed_track}, model, 8.0, True, 0.99, relaxed_state)

  radar_state = log.RadarState.new_message()
  radar_state.leadOne = strict_state
  radar_state.leadTwo = relaxed_state
  radar.set_fcw_authority(radar_state, (strict_state, relaxed_state), (0.99, 0.99))
  assert radar_state.leadOne.deprecated.fcw
  assert not radar_state.leadTwo.deprecated.fcw

  radar.record_lead(0, {}, model, 8.0, True, 0.99, {"present": False})
  radar_state.leadOne.deprecated.fcw = True
  radar.set_fcw_authority(radar_state, ({"present": False}, relaxed_state), (0.99, 0.99))
  assert not radar_state.leadOne.deprecated.fcw


def test_challenger_staleness_clears_after_two_cycles():
  radar = make_radar()
  radar.prev_lead_track_ids[0] = 27
  tracks = {
    27: make_positioned_track(27, 10.0, 5, y_rel=3.0),
    38: make_positioned_track(38, 10.0, 5, y_rel=2.0),
  }
  lead = make_model_lead(10.0)

  radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
  assert radar.prev_lead_track_ids[0] == 27
  assert radar.preferred_challenger_stale_counts[0] == 1
  radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
  assert radar.prev_lead_track_ids[0] == -1
  assert radar.preferred_challenger_stale_counts[0] == 0


def test_gross_distance_staleness_clears_after_three_cycles():
  radar = make_radar()
  radar.prev_lead_track_ids[0] = 53
  tracks = {53: make_positioned_track(53, 79.0, 5)}
  lead = make_model_lead(110.0)

  for expected in (1, 2):
    radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
    assert radar.prev_lead_track_ids[0] == 53
    assert radar.preferred_gross_distance_stale_counts[0] == expected
  radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
  assert radar.prev_lead_track_ids[0] == -1


def test_strict_match_resets_gross_distance_streak():
  radar = make_radar()
  radar.prev_lead_track_ids[0] = 46
  tracks = {46: make_positioned_track(46, 78.5, 5)}
  lead = make_model_lead(104.0)

  for _ in range(4):
    radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
    assert radar.prev_lead_track_ids[0] == 46
    assert radar.preferred_gross_distance_stale_counts[0] == 0


def test_stale_evidence_is_independent_per_lead_and_resets_on_id_change():
  radar = make_radar()
  tracks = {
    24: make_positioned_track(24, 10.0, 5, y_rel=3.0),
    44: make_positioned_track(44, 10.0, 5, y_rel=2.0),
    54: make_positioned_track(54, 10.0, 5, y_rel=3.0),
  }
  radar.prev_lead_track_ids = [24, 24]
  lead = make_model_lead(10.0)

  radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
  radar.update_preferred_staleness(1, tracks, lead, 1.0, True, 0.99)
  assert radar.preferred_challenger_stale_counts == [1, 1]
  radar.update_preferred_staleness(0, tracks, lead, 1.0, True, 0.99)
  assert radar.prev_lead_track_ids == [-1, 24]

  radar.prev_lead_track_ids[1] = 54
  radar.update_preferred_staleness(1, tracks, lead, 1.0, True, 0.99)
  assert radar.preferred_stale_track_ids[1] == 54
  assert radar.preferred_challenger_stale_counts[1] == 1


def test_preference_resets_when_selected_track_disappears():
  radar = make_radar()
  radar.prev_lead_track_ids[0] = 7
  radar.preferred_stale_track_ids[0] = 7
  radar.preferred_challenger_stale_counts[0] = 1
  radar.record_lead(
    0, {}, make_model_lead(7.0), 1.0, True, 0.99,
    {"present": True, "radar": False, "radarTrackId": -1},
  )
  assert radar.prev_lead_track_ids[0] == -1
  assert radar.preferred_stale_track_ids[0] == -1
  assert radar.preferred_challenger_stale_counts[0] == 0
