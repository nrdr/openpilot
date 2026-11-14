"""Radar-interface tests ported from Honda-PTM-Testing (tests/test_bosch_a_radar.py).

Left out: the card-startup/HondaBoschARadar param test and the ALT_RADAR_STOCK (stock_aol) set checks, which depend on
StarPilot-only modules this repo does not have. The nrdr RadarInterface is still selected by DBC name + CP.radarUnavailable.
"""
import pytest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.can_definitions import CanData
from opendbc.car.honda.bosch_a_radar import VERIFIED_BOSCH_A_CARS, bosch_a_range_offset_m, bosch_a_radar_platform
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.radar_interface import RadarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

BOSCH_A_DIRECT_VREL_INVALID = 0x7FE
RADAR_CONFIG = make_test_car_config(bosch_a_radar=True)
CP_SP = structs.CarParamsSP()


def make_f0(frame_idx=0, status=7, range_raw=0, angle_raw=0, range_sigma_raw=1):
  B0 = (range_sigma_raw & 127) << 1
  B3 = frame_idx & 15 | (range_raw & 15) << 4
  B2 = range_raw >> 4 & 255
  B1 = (status & 15) << 4
  B5 = (angle_raw & 7) << 5
  B4 = angle_raw >> 3 & 255
  return bytes([B0, B1, B2, B3, B4, B5, 0, 0])

def make_f1(frame_idx=0, existence_raw=126):
  return bytes([0, 0, 0, (frame_idx & 15) << 1, 0, existence_raw & 127, 0, 0])

def make_f2(frame_idx=0, life=0):
  B1 = frame_idx & 15 | (life & 15) << 4
  B0 = life >> 4 & 255
  return bytes([B0, B1, 0, 0, 0, 0, 0, 0])

def make_f3(frame_idx=0, edge_a_raw=0, edge_b_raw=0, sigma_a_raw=0, track_id=255):
  B0 = edge_a_raw >> 3 & 255
  B1 = (edge_a_raw & 7) << 5 | (frame_idx & 15) << 1
  B2 = edge_b_raw >> 3 & 255
  B3 = (edge_b_raw & 7) << 5
  B4 = sigma_a_raw >> 2 & 255
  B5 = (sigma_a_raw & 3) << 6
  return bytes([B0, B1, B2, B3, B4, B5, track_id & 255, 0])

def make_aux(frame_idx=0, rawc9=0, rawca=0, direct_vrel_raw=BOSCH_A_DIRECT_VREL_INVALID, direct_vrel_uncertainty_raw=1023):
  B0 = direct_vrel_raw >> 3 & 255
  B1 = (direct_vrel_raw & 7) << 5 | (frame_idx & 15) << 1
  B2 = direct_vrel_uncertainty_raw >> 2 & 255
  B3 = (direct_vrel_uncertainty_raw & 3) << 6
  B5 = (rawc9 & 3) << 6
  B4 = rawc9 >> 2 & 255
  B7 = (rawca & 3) << 6
  B6 = rawca >> 2 & 255
  return bytes([B0, B1, B2, B3, B4, B5, B6, B7])


def sweep(bus, index, timestamp, with_aux=True, status=7):
  frames = []
  for slot in range(16):
    base = 0x280 + 4 * slot if slot < 4 else 0x2D0 + 4 * (slot - 4)
    valid = slot == 0
    frames.extend((CanData(base, make_f0(index, status if valid else 15, 1000, 1024), bus),
                   CanData(base + 1, make_f1(index), bus),
                   CanData(base + 2, make_f2(index, 1 + index * 2), bus),
                   CanData(base + 3, make_f3(index, track_id=1 if valid else 255), bus)))
    if with_aux:
      address = 0x2C8 + slot if slot < 8 else 0x290 + slot - 8
      frames.append(CanData(address, make_aux(index, direct_vrel_raw=864, direct_vrel_uncertainty_raw=0), bus))
  return [(timestamp, frames)]


@pytest.mark.parametrize("identity", (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G))
def test_actual_parser_points_silence_retires_and_new_track_recovers(identity):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  assert not cp.radarUnavailable
  ri = RadarInterface(cp, CP_SP)
  bus = CanBus(cp).camera
  first = ri.update(sweep(bus, 0, 1_000_000_000))
  assert first is not None and not first.points
  second = ri.update(sweep(bus, 1, 1_066_666_667))
  assert not second.errors.canError
  assert len(second.points) == 1
  # firmware range: raw/16 minus the car's ROM offset n0/128 (Civic 346, CR-V 341)
  assert second.points[0].dRel == pytest.approx(1000 / 16 + bosch_a_range_offset_m(identity))
  assert second.points[0].yRel == pytest.approx(0.0)
  stale = ri.update([(1_400_000_000, [])])
  assert stale is not None and not stale.points and stale.errors.radarUnavailableTemporary
  assert not ri.update(sweep(bus, 2, 1_466_666_667)).points
  assert len(ri.update(sweep(bus, 3, 1_533_333_334)).points) == 1


@pytest.mark.parametrize("identity", (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G))
def test_point_status_is_the_status_nibble_of_its_latest_observation(identity):
  # route 34 T479: the phantom lead's track was STATUS 9 for its first ~4 s, then 7
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  ri = RadarInterface(cp, CP_SP)
  bus = CanBus(cp).camera
  assert ri.point_statuses == {}
  ri.update(sweep(bus, 0, 1_000_000_000, status=9))
  unconfirmed = ri.update(sweep(bus, 1, 1_066_666_667, status=9))
  assert ri.point_statuses == {p.trackId: 9 for p in unconfirmed.points} and len(unconfirmed.points) == 1
  confirmed = ri.update(sweep(bus, 2, 1_133_333_334))
  assert ri.point_statuses == {p.trackId: 7 for p in confirmed.points} and len(confirmed.points) == 1


def test_point_status_is_none_without_a_bosch_a_radar():
  cp = CarInterface.get_params(CAR.HONDA_CIVIC, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  assert RadarInterface(cp, CP_SP).point_statuses is None


@pytest.mark.parametrize("identity", (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G))
def test_wrong_bus_cannot_create_radar_points(identity):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  ri = RadarInterface(cp, CP_SP)
  for index in range(3):
    assert ri.update(sweep(CanBus(cp).camera + 1, index, 1_000_000_000 + index * 66_666_667)) is None
  assert not ri.bosch_a.pts


def test_verified_bosch_a_cars_are_all_platform_cars():
  expected = frozenset(c for c in CAR if bosch_a_radar_platform(c))
  assert VERIFIED_BOSCH_A_CARS == expected
  assert CAR.ACURA_RDX_3G in VERIFIED_BOSCH_A_CARS
  assert CAR.HONDA_ACCORD in VERIFIED_BOSCH_A_CARS
  assert CAR.HONDA_CIVIC_2022 not in VERIFIED_BOSCH_A_CARS


@pytest.mark.parametrize("identity", (CAR.HONDA_CIVIC_2022, CAR.HONDA_ACCORD_11G, CAR.HONDA_HRV_3G, CAR.ACURA_MDX_4G_MMR))
def test_non_bosch_a_platform_factory_has_no_radar_decoder(identity):
  cp = CarInterface.get_params(identity, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  assert cp.radarUnavailable
  assert RadarInterface(cp, CP_SP).rcp is None


@pytest.mark.parametrize("candidate", (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CRV_5G))
def test_selected_bosch_a_direct_update_uses_its_actual_protocol(candidate):
  cp = CarInterface.get_params(candidate, gen_empty_fingerprint(), [], False, False, False, RADAR_CONFIG)
  cp.radarUnavailable = False
  radar = RadarInterface(cp, CP_SP)
  assert radar.bosch_a is not None
  assert radar.update([]) is None
  result = radar._update([radar.trigger_msg])
  assert result.errors.canError
  assert not result.points
