import math

from opendbc.car.honda.values import CAR as HONDA_CAR
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_core import CivicBoschKalmanParams, CivicBoschTrack


_RADAR_TO_CAMERA = 1.52


class NrdrRadar:
  def __init__(self, CP):
    self.active = CP.brand == "honda" and not CP.radarUnavailable and CP.carFingerprint == HONDA_CAR.HONDA_CIVIC_BOSCH
    self.last_tracks_frame = -1

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
