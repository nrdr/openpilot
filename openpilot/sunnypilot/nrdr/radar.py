import math
from typing import Any

from opendbc.car.honda.values import HONDA_BOSCH_A
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.nrdr.radar_core import CivicBoschKalmanParams, CivicBoschTrack


_RADAR_TO_CAMERA = 1.52
HONDA_BOSCH_A_LOW_SPEED_MIN_SWEEPS = 3
HONDA_BOSCH_A_CHALLENGER_STALE_CYCLES = 2
HONDA_BOSCH_A_GROSS_DISTANCE_STALE_CYCLES = 3
HONDA_BOSCH_A_GROSS_DISTANCE_M = 25.0


def is_honda_bosch_a_radar(CP) -> bool:
  return CP.brand == "honda" and not CP.radarUnavailable and CP.carFingerprint in HONDA_BOSCH_A


def _laplacian_pdf(value: float, mean: float, scale: float) -> float:
  return math.exp(-abs(value - mean) / max(scale, 1e-4))


def vision_track_probability(track, lead, v_ego: float) -> float:
  vision_distance = lead.x[0] - _RADAR_TO_CAMERA
  return (
    _laplacian_pdf(track.dRel, vision_distance, lead.xStd[0]) *
    _laplacian_pdf(track.yRel, -lead.y[0], lead.yStd[0]) *
    _laplacian_pdf(track.vRel + v_ego, lead.v[0], lead.vStd[0])
  )


def track_matches_vision(track, lead, v_ego: float, *, dist_scale: float, dist_floor: float,
                         vel_limit: float, y_std_scale: float, y_floor: float) -> bool:
  vision_distance = lead.x[0] - _RADAR_TO_CAMERA
  distance_sane = abs(track.dRel - vision_distance) < max(abs(vision_distance) * dist_scale, dist_floor)
  velocity_sane = abs(track.vRel + v_ego - lead.v[0]) < vel_limit or v_ego + track.vRel > 3.0
  lateral_sane = abs(track.yRel + lead.y[0]) < max(y_floor, y_std_scale * max(float(lead.yStd[0]), 0.2))
  return distance_sane and velocity_sane and lateral_sane


def _mature_track(track) -> bool:
  return getattr(track, "measured_sweep_count", 0) >= HONDA_BOSCH_A_LOW_SPEED_MIN_SWEEPS


def _mature_low_speed_track(track, v_ego: float) -> bool:
  return _mature_track(track) and track.potential_low_speed_lead(v_ego)


class NrdrRadar:
  def __init__(self, CP):
    self.active = is_honda_bosch_a_radar(CP)
    self.last_tracks_frame = -1
    self.prev_lead_track_ids = [-1, -1]
    self.preferred_stale_track_ids = [-1, -1]
    self.preferred_challenger_stale_counts = [0, 0]
    self.preferred_gross_distance_stale_counts = [0, 0]
    self.strict_match_track_ids = [-1, -1]

  def kalman_params(self, default_class):
    return CivicBoschKalmanParams() if self.active else default_class(DT_MDL)

  def points(self, sm, radar_data):
    if not self.active:
      return {point.trackId: [point.dRel, point.yRel, point.vRel] for point in radar_data.points}

    fresh = sm.recv_frame["radarTracks"] != self.last_tracks_frame
    self.last_tracks_frame = sm.recv_frame["radarTracks"]
    return {
      point.trackId: [point.dRel, point.yRel, point.vRel, point.deprecated.measured and fresh]
      for point in radar_data.points
    }

  def create_track(self, default_class, radar, sm, identifier: int, point, v_lead: float):
    if not self.active:
      return default_class(identifier, v_lead, radar.kalman_params)

    measured = bool(point[3]) and not math.isnan(point[2])
    seed = v_lead
    model = sm["modelV2"]
    model_v_ego = model.velocity.x[0] if len(model.velocity.x) else radar.v_ego
    leads = model.leadsV3
    if not measured and radar.ready and len(leads) and leads[0].prob > 0.5 and len(leads[0].v):
      vision_distance = leads[0].x[0] - _RADAR_TO_CAMERA
      if abs(point[0] - vision_distance) < max(0.25 * vision_distance, 5.0):
        seed = radar.v_ego + leads[0].v[0] - model_v_ego
      else:
        seed = radar.v_ego_hist[0]
    elif not measured:
      seed = radar.v_ego_hist[0]
    return CivicBoschTrack(identifier, seed, radar.kalman_params)

  def update_track(self, track, point, v_lead: float, delayed_v_ego: float) -> None:
    if self.active:
      track.update(point[0], point[1], point[2], v_lead, point[3], delayed_v_ego)
    else:
      track.update(point[0], point[1], point[2], v_lead)

  def _reset_preferred_stale_evidence(self, lead_index: int, track_id: int = -1) -> None:
    self.preferred_stale_track_ids[lead_index] = track_id
    self.preferred_challenger_stale_counts[lead_index] = 0
    self.preferred_gross_distance_stale_counts[lead_index] = 0

  def update_preferred_staleness(self, lead_index: int, tracks: dict[int, Any], lead,
                                 v_ego: float, ready: bool, lead_prob: float) -> None:
    if not self.active:
      return

    preferred_id = self.prev_lead_track_ids[lead_index]
    if self.preferred_stale_track_ids[lead_index] != preferred_id:
      self._reset_preferred_stale_evidence(lead_index, preferred_id)

    preferred_track = tracks.get(preferred_id)
    if preferred_id < 0 or preferred_track is None or not ready or lead_prob <= 0.5:
      self._reset_preferred_stale_evidence(lead_index, preferred_id)
      return

    strict_match = track_matches_vision(
      preferred_track, lead, v_ego,
      dist_scale=0.25, dist_floor=5.0, vel_limit=10.0, y_std_scale=1.0, y_floor=1.0,
    )
    relaxed_match = track_matches_vision(
      preferred_track, lead, v_ego,
      dist_scale=0.40, dist_floor=8.0, vel_limit=13.0, y_std_scale=2.0, y_floor=1.5,
    )

    if relaxed_match:
      self.preferred_challenger_stale_counts[lead_index] = 0
    else:
      best_track = max(tracks.values(), key=lambda candidate: vision_track_probability(candidate, lead, v_ego))
      preferred_score = vision_track_probability(preferred_track, lead, v_ego)
      best_score = vision_track_probability(best_track, lead, v_ego)
      if best_track.identifier != preferred_id and best_score > preferred_score:
        self.preferred_challenger_stale_counts[lead_index] += 1
      else:
        self.preferred_challenger_stale_counts[lead_index] = 0

    distance_mismatch = abs(preferred_track.dRel - (lead.x[0] - _RADAR_TO_CAMERA))
    if strict_match:
      self.preferred_gross_distance_stale_counts[lead_index] = 0
    elif distance_mismatch > HONDA_BOSCH_A_GROSS_DISTANCE_M:
      self.preferred_gross_distance_stale_counts[lead_index] += 1
    else:
      self.preferred_gross_distance_stale_counts[lead_index] = 0

    challenger_stale = (
      self.preferred_challenger_stale_counts[lead_index] >= HONDA_BOSCH_A_CHALLENGER_STALE_CYCLES
    )
    distance_stale = (
      self.preferred_gross_distance_stale_counts[lead_index] >= HONDA_BOSCH_A_GROSS_DISTANCE_STALE_CYCLES
    )
    if challenger_stale or distance_stale:
      self.prev_lead_track_ids[lead_index] = -1
      self._reset_preferred_stale_evidence(lead_index)

  def associate_model_lead(self, lead_index: int, tracks: dict[int, Any], lead, v_ego: float):
    if not self.active or not tracks:
      return None

    strict_candidate = max(tracks.values(), key=lambda candidate: vision_track_probability(candidate, lead, v_ego))
    if track_matches_vision(
      strict_candidate, lead, v_ego,
      dist_scale=0.25, dist_floor=5.0, vel_limit=10.0, y_std_scale=1.0, y_floor=1.0,
    ):
      return strict_candidate

    preferred_track = tracks.get(self.prev_lead_track_ids[lead_index])
    if preferred_track is not None and _mature_track(preferred_track) and track_matches_vision(
      preferred_track, lead, v_ego,
      dist_scale=0.40, dist_floor=8.0, vel_limit=13.0, y_std_scale=2.0, y_floor=1.5,
    ):
      return preferred_track
    return None

  def select_lead(self, lead_index: int, tracks: dict[int, Any], lead, v_ego: float,
                  ready: bool, lead_prob: float, lead_dict: dict[str, Any],
                  low_speed_override: bool) -> dict[str, Any]:
    if not self.active or not low_speed_override:
      return lead_dict

    low_speed_tracks = [track for track in tracks.values() if _mature_low_speed_track(track, v_ego)]
    model_lead_available = ready and lead_prob > 0.5
    preferred_id = self.prev_lead_track_ids[lead_index]
    preferred_track = tracks.get(preferred_id)

    if preferred_track is not None and _mature_low_speed_track(preferred_track, v_ego):
      preferred_matches_model = (
        not model_lead_available or
        track_matches_vision(
          preferred_track, lead, v_ego,
          dist_scale=0.25, dist_floor=5.0, vel_limit=10.0, y_std_scale=1.0, y_floor=1.0,
        )
      )
      preferred_is_current = (
        not lead_dict.get("present", False) or
        lead_dict.get("radarTrackId", -1) == preferred_id or
        not lead_dict.get("radar", False)
      )
      if preferred_is_current and preferred_matches_model:
        lead_dict = preferred_track.get_RadarState(lead_prob)

    def candidate_is_established(candidate) -> bool:
      if not lead_dict.get("present", False):
        return True
      if lead_dict.get("radarTrackId", -1) == candidate.identifier:
        return True
      return (
        model_lead_available and
        track_matches_vision(
          candidate, lead, v_ego,
          dist_scale=0.25, dist_floor=5.0, vel_limit=10.0, y_std_scale=1.0, y_floor=1.0,
        )
      )

    established_tracks = [track for track in low_speed_tracks if candidate_is_established(track)]
    if established_tracks:
      closest_track = min(established_tracks, key=lambda track: track.dRel)
      if not lead_dict.get("present", False) or closest_track.dRel < lead_dict["dRel"]:
        lead_dict = closest_track.get_RadarState()

    return lead_dict

  def record_lead(self, lead_index: int, tracks: dict[int, Any], lead, v_ego: float,
                  ready: bool, lead_prob: float, lead_dict: dict[str, Any]) -> None:
    if not self.active:
      return

    self.strict_match_track_ids[lead_index] = -1
    if lead_dict.get("present", False) and lead_dict.get("radar", False):
      track_id = int(lead_dict.get("radarTrackId", -1))
      selected_track = tracks.get(track_id)
      if (selected_track is not None and ready and lead_prob > 0.5 and
          track_matches_vision(
            selected_track, lead, v_ego,
            dist_scale=0.25, dist_floor=5.0, vel_limit=10.0, y_std_scale=1.0, y_floor=1.0,
          )):
        self.strict_match_track_ids[lead_index] = track_id
      if track_id != self.prev_lead_track_ids[lead_index]:
        self._reset_preferred_stale_evidence(lead_index, track_id)
      self.prev_lead_track_ids[lead_index] = track_id
    elif not lead_dict.get("present", False) or self.prev_lead_track_ids[lead_index] not in tracks:
      self.prev_lead_track_ids[lead_index] = -1
      self._reset_preferred_stale_evidence(lead_index)
