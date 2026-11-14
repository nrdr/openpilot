"""In-path radar keep (route 11c8fa231c0499ed/0000009e--9704dd1da2 seg 24, replay evidence, 2026-11-06).

A real in-path radar lead (track 39: dRel 28.1, yRel -0.86, vRel -7.9, cnt 342) was dropped when the model
lead's x jumped 33 -> 50.6 m: the strict and relaxed vision matches in match_vision_to_track both failed on
the distance gap alone, so get_lead fell through to the vision-only lead and aLeadK flipped -3.0 -> +0.33.
These tests cover the keep rule added to match_vision_to_track (and the gross-distance staleness exemption
it needs in BoschALeadPolicy) so a track that is still in lane, still closer than the vision lead, and still
closing is kept instead of dropped.
"""
from types import SimpleNamespace

from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.radard import KalmanParams
from openpilot.nrdr.features.radar.bosch_a_lead_policy import (RADAR_TO_CAMERA, BoschALeadPolicy, Track, get_lead, in_path_radar_keep,
                                                match_vision_to_track)


def make_track(identifier: int, d_rel: float, y_rel: float, v_rel: float, cnt: int, v_ego: float = 25.0) -> Track:
  track = Track(identifier, v_rel + v_ego, KalmanParams(DT_MDL))
  for _ in range(cnt):
    track.update(d_rel, y_rel, v_rel, v_rel + v_ego, True)
  assert track.cnt == cnt
  return track


def make_lead(x: float, v: float, prob: float = 0.99, y: float = 0.0, a: float = 0.0):
  return SimpleNamespace(x=[x], y=[y], v=[v], a=[a], xStd=[1.0], yStd=[0.5], vStd=[1.0], prob=prob)


# The route-9e shape: track 39 was real and closing; the model lead's x jumped out to 50.6 m (prob 0.99).
TRACK_39_KWARGS: dict = {'d_rel': 28.1, 'y_rel': -0.86, 'v_rel': -7.9, 'cnt': 342}
V_EGO = 25.0
NINE_E_LEAD = make_lead(x=50.6, v=V_EGO - 7.9)  # v consistent with a farther car at roughly the same closing rate


def test_route_9e_shape_keeps_the_preferred_track():
  track = make_track(39, **TRACK_39_KWARGS, v_ego=V_EGO)
  tracks = {39: track}
  # Confirm the relaxed match really fails first, i.e. this is the case the keep exists for.
  from openpilot.nrdr.features.radar.bosch_a_lead_policy import track_matches_vision
  assert not track_matches_vision(track, NINE_E_LEAD, V_EGO, dist_scale=0.4, dist_floor=8.0, vel_limit=13.0, y_std_scale=2.0, y_floor=1.5)
  result = match_vision_to_track(V_EGO, NINE_E_LEAD, tracks, preferred_track_id=39)
  assert result is track


def test_left_lane_track_is_not_kept():
  track = make_track(39, d_rel=28.1, y_rel=-2.0, v_rel=-7.9, cnt=342, v_ego=V_EGO)
  tracks = {39: track}
  assert match_vision_to_track(V_EGO, NINE_E_LEAD, tracks, preferred_track_id=39) is None


def test_non_closing_track_is_not_kept():
  track = make_track(39, d_rel=28.1, y_rel=-0.86, v_rel=0.5, cnt=342, v_ego=V_EGO)
  tracks = {39: track}
  assert match_vision_to_track(V_EGO, NINE_E_LEAD, tracks, preferred_track_id=39) is None


def test_track_farther_than_vision_lead_is_not_kept():
  track = make_track(39, d_rel=90.0, y_rel=-0.86, v_rel=-7.9, cnt=342, v_ego=V_EGO)
  tracks = {39: track}
  assert match_vision_to_track(V_EGO, NINE_E_LEAD, tracks, preferred_track_id=39) is None


def test_no_preferred_id_is_not_kept():
  track = make_track(39, **TRACK_39_KWARGS, v_ego=V_EGO)
  tracks = {39: track}
  assert match_vision_to_track(V_EGO, NINE_E_LEAD, tracks, preferred_track_id=-1) is None
  assert in_path_radar_keep(None, NINE_E_LEAD) is False


def test_strict_match_still_wins_over_the_keep():
  offset = 30.0 - RADAR_TO_CAMERA
  lead = make_lead(x=30.0, v=V_EGO - 1.0)
  track = make_track(39, d_rel=offset, y_rel=0.0, v_rel=-1.0, cnt=342, v_ego=V_EGO)
  tracks = {39: track}
  result = match_vision_to_track(V_EGO, lead, tracks, preferred_track_id=39)
  assert result is track


def _drive_one_frame(policy: BoschALeadPolicy, lead, lead_prob: float, model_v_ego: float):
  # Lowest-level reproduction of the per-frame bookkeeping in BoschALeadPolicy.leads(): the staleness update,
  # then get_lead with low_speed_override disabled (that path is untouched by this change and tested elsewhere),
  # then the prev_lead_track_ids bookkeeping from the tail of leads(). Avoids building a full SubMaster/modelV2
  # harness just to drive the staleness path.
  policy._update_honda_bosch_a_preferred_staleness(0, lead, lead_prob)
  lead_dict = get_lead(
    policy.v_ego, policy.ready, policy.tracks, lead, model_v_ego, policy.starpilot_toggles,
    low_speed_override=False, lead_prob=lead_prob, preferred_track_id=policy.prev_lead_track_ids[0],
    vision_state=policy.vision_state,
  )
  if lead_dict.get('present', False) and lead_dict.get('radar', False):
    identifier = int(lead_dict.get('radarTrackId', -1))
    if identifier != policy.prev_lead_track_ids[0]:
      policy._reset_preferred_stale_evidence(0, identifier)
    policy.prev_lead_track_ids[0] = identifier
  elif not lead_dict.get('present', False) or policy.prev_lead_track_ids[0] not in policy.tracks:
    policy.prev_lead_track_ids[0] = -1
    policy._reset_preferred_stale_evidence(0)
  return lead_dict


def test_staleness_does_not_drop_the_kept_track_over_consecutive_frames():
  policy = BoschALeadPolicy()
  policy.ready = True
  policy.v_ego = V_EGO
  track = make_track(39, **TRACK_39_KWARGS, v_ego=V_EGO)
  policy.tracks = {39: track}
  policy.prev_lead_track_ids[0] = 39
  policy._reset_preferred_stale_evidence(0, 39)

  for _ in range(20):
    lead_dict = _drive_one_frame(policy, NINE_E_LEAD, NINE_E_LEAD.prob, V_EGO)
    assert lead_dict['present'] and lead_dict['radar']
    assert lead_dict['radarTrackId'] == 39
    assert policy.prev_lead_track_ids[0] == 39

  # Once the track leaves lane, the keep conditions go false and the old path (vision fallback) runs.
  track.yRel = -2.0
  lead_dict = _drive_one_frame(policy, NINE_E_LEAD, NINE_E_LEAD.prob, V_EGO)
  assert lead_dict['present'] and not lead_dict['radar']


def test_better_scoring_challenger_does_not_retire_the_kept_track():
  policy = BoschALeadPolicy()
  policy.ready = True
  policy.v_ego = V_EGO
  track = make_track(39, **TRACK_39_KWARGS, v_ego=V_EGO)
  # A second track nearer the vision lead than track 39, but not close enough to match it strictly.
  challenger = make_track(52, d_rel=36.0, y_rel=3.0, v_rel=-7.9, cnt=50, v_ego=V_EGO)
  policy.tracks = {39: track, 52: challenger}
  policy.prev_lead_track_ids[0] = 39
  policy._reset_preferred_stale_evidence(0, 39)
  assert match_vision_to_track(V_EGO, NINE_E_LEAD, policy.tracks, preferred_track_id=-1) is None

  for _ in range(20):
    lead_dict = _drive_one_frame(policy, NINE_E_LEAD, NINE_E_LEAD.prob, V_EGO)
    assert lead_dict['present'] and lead_dict['radar']
    assert lead_dict['radarTrackId'] == 39


def test_cross_traffic_while_stopped_is_not_kept():
  # Route 7e i5814 shape: ego stopped, kept track 62 at 14 m closing at 9 m/s was a car crossing the intersection.
  lead = make_lead(x=23.4 + RADAR_TO_CAMERA, v=0.0)
  track = make_track(62, d_rel=14.0, y_rel=0.49, v_rel=-9.0, cnt=50, v_ego=0.0)
  assert match_vision_to_track(0.0, lead, {62: track}, preferred_track_id=62) is None


def test_next_lane_edge_track_is_not_kept():
  # Route 7b i5143 shape: box truck in the next lane at yRel -1.48 was kept under the first 1.5 m bound.
  track = make_track(39, d_rel=36.0, y_rel=-1.48, v_rel=-7.1, cnt=342, v_ego=17.7)
  assert match_vision_to_track(17.7, make_lead(x=70.0, v=17.7 - 2.0), {39: track}, preferred_track_id=39) is None
