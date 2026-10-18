"""Rack maps predicted from published specs: checked held out against the yaw-measured maps, and pinned to the source tree."""
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.nrdr.features.lateral import honda_spec_plant as spec
from openpilot.nrdr.features.lateral.honda_rack_map import (
  CIVIC_TBA_C020_RACK, CIVIC_TBA_C120_SPEC_RACK, CIVIC_TEG_A010_RACK, CIVIC_TGG_A120_SPEC_RACK,
  CLARITY_TRW_A020_RACK, CRV_TLA_A040_SPEC_RACK, INSIGHT_TXM_A040_RACK, MEASURED_RACK_MAP_TABLES, SPEC_RACK_MAP_TABLES,
  RackMapGeometry, get_rack_map_table,
)
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES

PROFILE = {p.name: p for p in HONDA_VGR_PROFILES}
# Each yaw-measured car: its specs, its Table A and its measured map
MEASURED = {
  "clarity": (spec.CLARITY_SPEC, PROFILE["Clarity TRW-A020"], CLARITY_TRW_A020_RACK),
  "c020": (spec.CIVIC_SPORT_SEDAN_SPEC, PROFILE["Civic C020/TGG-A120"], CIVIC_TBA_C020_RACK),
  "insight": (spec.INSIGHT_SPEC, PROFILE["Insight TXM-A040"], INSIGHT_TXM_A040_RACK),
  "teg": (spec.CIVIC_2016_SEDAN_SPEC, PROFILE["Civic C120/A030/TEG"], CIVIC_TEG_A010_RACK),
}
# Geometry from JamesL787 ns-bosch-radar-testing honda_eps_calibrations;
# slip factors refitted after the single-driver axle-allocation correction.
# (last angle, ratio at centre, 6th point, last, slip factor)
SOURCE = {
  "Civic Bosch TBA-C120": (399.6, 14.472, 14.175, 12.956, -0.000675),
  "Civic hatch TGG-A120": (379.8, 14.878, 14.615, 13.518, -0.000624),
  "CR-V TLA-A040": (414.0, 16.822, 16.533, 15.33, -0.000589),
}


def _r0_gain(name):
  s, profile, table = MEASURED[name]
  measured = spec.r0_of_table(table.ratio_bp, table.ratio_v, profile)
  return measured / (profile.physical_to_linear(s.lock_deg) / (s.lock_deg / s.lock_ratio))


def _slip_gain(name):
  s, _, table = MEASURED[name]
  return table.slip_factor / spec.spec_slip_factor(s) * spec.SPEC_SLIP_GAIN


@pytest.mark.parametrize("car", (spec.CLARITY_SPEC, spec.CIVIC_SPORT_SEDAN_SPEC, spec.INSIGHT_SPEC,
                                spec.CIVIC_2016_SEDAN_SPEC, spec.CIVIC_2019_SEDAN_SPEC,
                                spec.CIVIC_HATCH_SPORT_SPEC, spec.CRV_2017_SPEC))
def test_driver_mass_is_added_to_each_axle_once(car):
  front, rear = spec.spec_axle_masses(car)
  curb = car.curb_mass_lb * spec.LB
  assert front + rear == pytest.approx(curb + spec.DRIVER_KG)
  assert front - curb * car.front_weight_fraction == pytest.approx(50.0)
  assert rear - curb * (1.0 - car.front_weight_fraction) == pytest.approx(30.0)


def test_the_constants_are_the_mean_over_the_measured_cars():
  assert spec.SPEC_R0_GAIN == pytest.approx(np.mean([_r0_gain(n) for n in MEASURED]), abs=0.002)
  assert spec.SPEC_SLIP_GAIN == pytest.approx(np.mean([_slip_gain(n) for n in MEASURED]), rel=0.01)
  assert {t.name for t in MEASURED_RACK_MAP_TABLES} == {m[2].name for m in MEASURED.values()}


@pytest.mark.parametrize("name", MEASURED)
def test_each_measured_map_is_predicted_held_out(name):
  # the constants from the other three cars only: R0 within 2.6%, the map within 4.5% from 15 to 230 deg
  s, profile, table = MEASURED[name]
  gain = np.mean([_r0_gain(n) for n in MEASURED if n != name])
  r0 = gain * profile.physical_to_linear(s.lock_deg) / (s.lock_deg / s.lock_ratio)
  assert r0 == pytest.approx(spec.r0_of_table(table.ratio_bp, table.ratio_v, profile), rel=0.026)
  for angle, ratio in zip(table.ratio_bp, table.ratio_v, strict=True):
    if 15.0 <= angle <= 230.0:
      assert spec.tan_ratio(profile.physical_to_linear(angle), r0) == pytest.approx(ratio, rel=0.045), angle
  slip = np.mean([_slip_gain(n) for n in MEASURED if n != name])
  assert spec.spec_slip_factor(s) / spec.SPEC_SLIP_GAIN * slip == pytest.approx(table.slip_factor, rel=0.10)


@pytest.mark.parametrize("table", SPEC_RACK_MAP_TABLES, ids=lambda t: t.name)
def test_spec_maps_attach_to_their_exact_car_and_invert(table):
  assert not table.measured and table.provenance.startswith("spec")
  CP = SimpleNamespace(brand="honda", carFingerprint=table.fingerprint, carFw=[SimpleNamespace(ecu="eps", fwVersion=table.firmware[0].encode())])
  assert get_rack_map_table(CP) is table
  assert all(b <= a for a, b in zip(table.ratio_v, table.ratio_v[1:], strict=False))  # quickens off centre only
  profile = next(p for p in HONDA_VGR_PROFILES if table.firmware[0] in p.firmware)
  geometry = RackMapGeometry(profile, table, 15.38)
  assert geometry.name.endswith("spec rack map")
  for v in (3.0, 15.0, 30.0):
    for angle in (-300.0, -40.0, 3.0, 90.0, 380.0):
      assert geometry.angle_from_curvature(geometry.curvature_from_angle(angle, v, 0.01), v, 0.01) == pytest.approx(angle, abs=1e-3)


@pytest.mark.parametrize("table", (CIVIC_TBA_C120_SPEC_RACK, CIVIC_TGG_A120_SPEC_RACK, CRV_TLA_A040_SPEC_RACK), ids=lambda t: t.name)
def test_spec_maps_match_the_source_tree(table):
  last, centre, sixth, end, slip = SOURCE[table.name]
  assert (table.ratio_bp[-1], table.ratio_v[0], table.ratio_v[5], table.ratio_v[-1]) == \
    pytest.approx((last, centre, sixth, end), abs=1e-3)
  assert table.slip_factor == pytest.approx(slip, abs=1e-9)



def test_the_a030s_spec_prediction_would_be_2_percent_off_the_tegs_measured_map():
  # why the A030 takes the TEG's measured map (honda_rack_map): its specs and Table A are the TEG's
  s, profile, table = MEASURED["teg"]
  assert spec.spec_r0(s, profile) / spec.r0_of_table(table.ratio_bp, table.ratio_v, profile) == pytest.approx(1.016, abs=0.003)

