from types import SimpleNamespace

from opendbc.car.structs import car
from opendbc.car.honda.values import CAR as HONDA_CAR
from openpilot.selfdrive.controls.radard import RadarD


def model_lead(distance: float = 20.0, probability: float = 0.99):
  return SimpleNamespace(
    prob=probability,
    x=[distance + 1.52],
    y=[0.0],
    v=[2.0],
    a=[0.0],
    xStd=[1.0],
    yStd=[1.0],
    vStd=[1.0],
  )


class FakeSubMaster:
  def __init__(self):
    self.seen = {"modelV2": True}
    self.recv_frame = {"radarTracks": 0, "carState": 0}
    self.logMonoTime = {"modelV2": 0, "radarTracks": 0, "carState": 0}
    self.data = {
      "carState": SimpleNamespace(vEgo=8.0),
      "modelV2": SimpleNamespace(
        velocity=SimpleNamespace(x=[8.0]),
        leadsV3=[model_lead(), model_lead(probability=0.0)],
      ),
    }

  def __getitem__(self, key):
    return self.data[key]

  def all_checks(self):
    return True

  def advance(self):
    for key in self.recv_frame:
      self.recv_frame[key] += 1
      self.logMonoTime[key] += 50_000_000


def radar_data(*, y_rel: float = 0.0, points: bool = True):
  radar = car.RadarData.new_message()
  radar_points = radar.init("points", 1 if points else 0)
  if points:
    radar_points[0].trackId = 7
    radar_points[0].dRel = 20.0
    radar_points[0].yRel = y_rel
    radar_points[0].vRel = -6.0
    radar_points[0].deprecated.measured = True
  return radar


def car_params(fingerprint):
  return SimpleNamespace(
    brand="honda",
    radarUnavailable=False,
    carFingerprint=fingerprint,
    radarDelay=0.0,
  )


def test_radard_publishes_strict_only_deprecated_fcw_and_clears_it_on_track_loss():
  radar = RadarD(car_params(HONDA_CAR.HONDA_CIVIC_BOSCH), SimpleNamespace(flags=0))
  sm = FakeSubMaster()

  for _ in range(3):
    sm.advance()
    radar.update(sm, radar_data())
  assert radar.radar_state.leadOne.present
  assert radar.radar_state.leadOne.radar
  assert radar.radar_state.leadOne.deprecated.fcw

  sm.advance()
  radar.update(sm, radar_data(y_rel=1.4))
  assert radar.radar_state.leadOne.present
  assert radar.radar_state.leadOne.radarTrackId == 7
  assert not radar.radar_state.leadOne.deprecated.fcw

  sm.advance()
  radar.update(sm, radar_data(points=False))
  assert radar.radar_state.leadOne.present
  assert not radar.radar_state.leadOne.radar
  assert not radar.radar_state.leadOne.deprecated.fcw


def test_non_bosch_radard_keeps_deprecated_fcw_false():
  radar = RadarD(car_params(HONDA_CAR.HONDA_CIVIC), SimpleNamespace(flags=0))
  sm = FakeSubMaster()
  sm.advance()
  radar.update(sm, radar_data())
  assert radar.radar_state.leadOne.present
  assert radar.radar_state.leadOne.radar
  assert not radar.radar_state.leadOne.deprecated.fcw
