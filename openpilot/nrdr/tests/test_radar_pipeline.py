import copy
from types import SimpleNamespace

import pytest

from opendbc.car import structs
from opendbc.car.honda.bosch_a_radar import BOSCH_A_FREQ_HZ
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.radar_interface import RadarInterface
from opendbc.car.honda.tests.test_bosch_a_radar import sweep as decoder_sweep
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
from openpilot.cereal import messaging
from openpilot.nrdr.tests.test_radar_lead_bound import ReplaySubMaster, bosch_a_radard
from openpilot.selfdrive.controls.radard import RadarD


def sweep(cp, index, t_nanos):
  """One valid Bosch-A track (id 1, range_raw 227, angle 1024) in slot 0, on cp's camera bus.

  nrdr's opendbc test helper builds a sweep per slot (not the whole bank the Biscuit-Labs helper did), with
  the trigger frame added; the bus is rebound to the platform under test.
  """
  (stamp, frames), = decoder_sweep(0, index, 7, 227, 1024, 1 + index * 2, t_nanos, with_aux=True,
                                   direct_vrel_raw=864, direct_vrel_uncertainty_raw=0)
  return [(stamp, [frame._replace(src=CanBus(cp).camera) for frame in frames])]


def source_tick(sm, tick, rr=None, speed=0.0, probability=0.0, distance=10.0, standstill=False):
  stamp = 1_000_000_000 + tick * 50_000_000
  model_event = messaging.new_message('modelV2', valid=True)
  model_event.logMonoTime = stamp
  model = model_event.modelV2
  model.velocity.x = [speed]
  leads = model.init('leadsV3', 2)
  for lead in leads:
    lead.x = [distance + 1.52]
    lead.y = [0.0]
    lead.v = [speed]
    lead.a = [0.0]
    lead.xStd = lead.yStd = lead.vStd = [1.0]
    lead.prob = probability
  car_event = messaging.new_message('carState', valid=True)
  car_event.logMonoTime = stamp
  car_event.carState.vEgo = speed
  car_event.carState.standstill = standstill
  events = [model_event.as_reader(), car_event.as_reader()]
  if rr is not None:
    radar_event = messaging.new_message('radarTracks', valid=True)
    radar_event.logMonoTime = stamp
    radar_event.radarTracks = rr
    events.append(radar_event.as_reader())
  sm.update_msgs(stamp / 1e9, events)


def radar_data(measured=True, relative_speed=0.0, distance=10.0):
  rr = structs.RadarData()
  point = rr.init('points', 1)[0]
  point.trackId = 1
  point.dRel = distance
  point.yRel = 0.0
  point.vRel = relative_speed
  point.deprecated.measured = measured
  return rr


def test_actual_radard_duplicate_and_predicted_point_hold_kalman_measurement():
  sm = ReplaySubMaster(['modelV2', 'carState', 'radarTracks'])
  radar = bosch_a_radard()
  source_tick(sm, 0, radar_data(), speed=10.0)
  radar.update(sm, sm['radarTracks'])
  track = radar.tracks[1]
  assert track.cnt == 1
  original = copy.deepcopy(track.kf.x)
  source_tick(sm, 1, speed=20.0)
  radar.update(sm, sm['radarTracks'])
  assert track.cnt == 1 and track.kf.x == original and not track.measured
  source_tick(sm, 2, radar_data(False, 30.0), speed=20.0)
  radar.update(sm, sm['radarTracks'])
  assert track.cnt == 1 and track.kf.x == original and not track.measured
  source_tick(sm, 3, radar_data(True, 2.0), speed=20.0)
  radar.update(sm, sm['radarTracks'])
  assert track.cnt == 2 and track.kf.x != original and track.measured
  assert radar.kalman_params.A[0][1] == pytest.approx(1.0 / BOSCH_A_FREQ_HZ)


def test_non_honda_radard_keeps_ordinary_duplicate_measurement_behavior():
  sm = ReplaySubMaster(['modelV2', 'carState', 'radarTracks'])
  radar = RadarD(SimpleNamespace(brand='toyota', radarUnavailable=False, carFingerprint='TOYOTA', radarDelay=0.0), SimpleNamespace(flags=0))
  source_tick(sm, 0, radar_data(), speed=10.0)
  radar.update(sm, sm['radarTracks'])
  source_tick(sm, 1, speed=20.0)
  radar.update(sm, sm['radarTracks'])
  assert radar.tracks[1].cnt == 2
  assert radar.kalman_params.A[0][1] == 0.05


@pytest.mark.parametrize('identity', (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G))
def test_actual_decoder_radard_maturity_stale_retirement_and_recovery(identity):
  # nrdr gates the Bosch-A radar on a runtime config (HondaBoschARadar), not on the fingerprint alone
  cp = CarInterface.get_non_essential_params(identity, make_test_car_config(bosch_a_radar=True))
  cp_sp = structs.CarParamsSP()
  decoder = RadarInterface(cp, cp_sp)
  radar = RadarD(cp, SimpleNamespace(flags=0), cp.radarDelay)
  sm = ReplaySubMaster(['modelV2', 'carState', 'radarTracks'])
  for index in range(4):
    rr = decoder.update(sweep(cp, index, 1_000_000_000 + index * 66_666_667))
    source_tick(sm, index, rr)
    radar.update(sm, sm['radarTracks'])
    if index < 3:
      assert not radar.radar_state.leadOne.present
  assert radar.radar_state.leadOne.present and radar.radar_state.leadOne.radar
  assert radar.radar_state.leadOne.radarTrackId == 1
  stale = decoder.update([(1_500_000_000, [])])
  assert stale.errors.radarUnavailableTemporary and not stale.points
  source_tick(sm, 4, stale)
  radar.update(sm, sm['radarTracks'])
  assert not radar.tracks and not radar.radar_state.leadOne.present
  rr = decoder.update(sweep(cp, 5, 1_566_666_667))
  source_tick(sm, 5, rr)
  radar.update(sm, sm['radarTracks'])
  assert not radar.tracks
