import math
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.nrdr.features.lateral.honda_rack_map import (
  CIVIC_TEG_A010_RACK, RACK_MAP_TABLES, RackMapGeometry, RackMapTable, get_rack_map_table,
)
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode, resolve_steer_ratio_selection

STEER_RATIO = {"HONDA_CLARITY": 16.5, "HONDA_CIVIC_BOSCH": 15.38, "HONDA_CIVIC": 15.38, "HONDA_INSIGHT": 15.0}
MEASURED = {
  "clarity": ("HONDA_CLARITY", b"39990-TRW-A020"),
  "c020": ("HONDA_CIVIC_BOSCH", b"39990-TBA-C020"),
  "teg": ("HONDA_CIVIC", b"39990-TEG-A010\x00"),
  "insight": ("HONDA_INSIGHT", b"39990-TXM-A040"),
}
# JamesL787 ns-bosch-radar-testing honda_eps_rack_map.HondaEpsRackMap.angle_from_curvature on opendbc's Table A
# inverses: (desired curvature, vEgo, roll) -> physical wheel angle, deg.
CASES = ((0.002, 25.0, 0.0), (-0.01, 12.0, 0.03), (0.05, 6.0, -0.02), (0.12, 3.0, 0.0))
SOURCE_ANGLES = {
  "clarity": (-7.2556, 29.3431, -124.6848, -273.6899),
  "c020": (-6.4948, 25.2898, -108.9301, -235.3979),
  "teg": (-6.3637, 24.8706, -105.5852, -229.3676),
  "insight": (-7.6419, 30.1357, -124.0563, -274.0711),
}


def cp(fingerprint, firmware, brand="honda"):
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, steerRatio=STEER_RATIO.get(fingerprint, 15.38),
                         carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)])


def firmware_selection(CP):
  return resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": SteerRatioMode.FIRMWARE})


@pytest.mark.parametrize("car", MEASURED)
def test_firmware_mode_reproduces_the_source_rack_map(car):
  selection = firmware_selection(cp(*MEASURED[car]))
  assert selection.rack_map is not None
  vm = SimpleNamespace(sR=0.0)
  for (curvature, speed, roll), expected in zip(CASES, SOURCE_ANGLES[car], strict=True):
    angle = selection.desired_angle_no_offset(vm, 0.0, speed, roll, curvature)
    assert angle == pytest.approx(expected, abs=0.02)
    assert selection.measured_curvature(vm, angle, speed, roll) == pytest.approx(curvature, rel=1e-6)
  assert vm.sR == pytest.approx(selection.cp_ratio)  # VehicleModel keeps CP's ratio for everything else


@pytest.mark.parametrize("car", MEASURED)
def test_map_inverts_at_every_angle_and_is_symmetric(car):
  geometry = firmware_selection(cp(*MEASURED[car])).rack_map
  for angle in np.linspace(-1000.0, 1000.0, 201):
    assert geometry.linear_to_physical(geometry.physical_to_linear(angle)) == pytest.approx(angle, abs=1e-6)
    assert geometry.physical_to_linear(-angle) == pytest.approx(-geometry.physical_to_linear(angle))
    for speed, roll in ((5.0, 0.0), (30.0, 0.04)):
      curvature = geometry.curvature_from_angle(angle, speed, roll)
      assert geometry.angle_from_curvature(curvature, speed, roll) == pytest.approx(angle, abs=1e-6)


@pytest.mark.parametrize("car", MEASURED)
def test_speed_free_paths_agree_with_the_full_map_without_slip(car):
  # At zero speed and roll the slip factor drops out, so the linearized path VehicleModel sees (CP ratio) and the
  # full map must give the same wheel angle.
  selection = firmware_selection(cp(*MEASURED[car]))
  geometry = selection.rack_map
  for curvature in (0.001, 0.01, 0.05, 0.15):
    linear = math.degrees(curvature * selection.cp_ratio * geometry.table.wheelbase)
    assert selection.physicalize_desired_angle(linear) == pytest.approx(geometry.angle_from_curvature(curvature, 0.0, 0.0))


def test_teg_centre_is_measured_not_cp():
  selection = firmware_selection(cp(*MEASURED["teg"]))
  table = selection.rack_map.table
  assert table is CIVIC_TEG_A010_RACK and selection.rack_map.center_ratio == pytest.approx(14.16)
  # Near centre Table A is ~linear, so the measured map asks for 14.16 / 15.38 of the angle the CP anchor did.
  cp_anchor = get_honda_vgr_profile(cp(*MEASURED["teg"]))
  linear = 1.0
  assert (selection.physicalize_desired_angle(linear) / cp_anchor.linear_to_physical(linear) ==
          pytest.approx(14.16 / 15.38, rel=2e-3))


@pytest.mark.parametrize("fingerprint,firmware", (
  ("HONDA_CIVIC_BOSCH", b"39990-TBA-C120"),
  ("HONDA_CIVIC_BOSCH", b"39990-TGG-A120"),
  ("HONDA_CRV_5G", b"39990-TLA-A040"),
))
def test_unmeasured_images_steer_on_their_spec_map(fingerprint, firmware):
  # predicted from the car's own published specs (test_honda_spec_plant.py), not taken from a different measured car
  CP = cp(fingerprint, firmware)
  selection = firmware_selection(CP)
  assert selection.firmware_vgr_selected and selection.rack_map is not None
  assert not selection.rack_map.table.measured and selection.rack_map.profile is get_honda_vgr_profile(CP)


@pytest.mark.parametrize("fingerprint,firmware", (
  ("HONDA_CIVIC_BOSCH", b"39990-TEG-A010"),   # right EPS, wrong car
  ("HONDA_CIVIC", b"39990-TBA-C020"),         # right car family, other EPS
  ("HONDA_ACCORD", b"39990-TRW-A020"),
  ("HONDA_CLARITY", b"39990-TRW-A030"),
))
def test_maps_are_never_borrowed(fingerprint, firmware):
  assert get_rack_map_table(cp(fingerprint, firmware)) is None
  assert get_rack_map_table(cp("HONDA_CLARITY", b"39990-TRW-A020", brand="toyota")) is None


def test_other_modes_and_hybrid_firmware_source():
  CP = cp(*MEASURED["clarity"])
  manual = resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": SteerRatioMode.MANUAL})
  assert manual.rack_map is None and not manual.firmware_vgr_selected
  hybrid = resolve_steer_ratio_selection(CP, {"NrdrSteerRatioMode": 2, "NrdrSteerRatioSourceB": 3,
                                             "NrdrSteerRatioBlendStart": 10.0, "NrdrSteerRatioHybrid": True})
  # A hybrid's Firmware side is the measured map too, through the speed-free path.
  assert hybrid.hybrid is not None and hybrid.rack_map is None
  assert hybrid.hybrid.forward(120.0) == pytest.approx(hybrid.firmware_profile.physical_to_linear(120.0))
  assert isinstance(hybrid.firmware_profile, RackMapGeometry)


def test_tables_are_valid_and_inside_their_table_a():
  for table in RACK_MAP_TABLES:
    profile = get_honda_vgr_profile(cp(table.fingerprint, table.firmware[0].encode()))
    assert profile is not None and table.ratio_bp[-1] < profile.physical_knots[-1]
  with pytest.raises(ValueError):
    RackMapTable("bad", "HONDA_CLARITY", ("39990-TRW-A020",), 2.75, (10.0, 5.0), (17.0, 16.0), -0.0005, "")
  with pytest.raises(ValueError):
    RackMapTable("bad", "HONDA_CLARITY", ("39990-TRW-A020",), 0.0, (5.0, 10.0), (17.0, 16.0), -0.0005, "")


def test_the_a030_takes_the_tegs_measured_map_as_the_same_car():
  # same 2016-18 Civic sedan (US vs Japanese part number), same published specs, byte-identical Table A
  a030 = firmware_selection(cp("HONDA_CIVIC", b"39990-TBA,A030\x00\x00"))
  teg = firmware_selection(cp(*MEASURED["teg"]))
  assert a030.rack_map.table is teg.rack_map.table is CIVIC_TEG_A010_RACK and CIVIC_TEG_A010_RACK.measured
  assert a030.rack_map.profile is teg.rack_map.profile


def test_the_map_is_built_once_not_every_frame():
  # controlsd resolves the steer-ratio selection every frame, in every mode; the map's grid is built once per car
  CP = cp(*MEASURED["teg"])
  first, second = firmware_selection(CP), firmware_selection(CP)
  assert first.rack_map is second.rack_map is not None
  assert first.rack_map.name == "Civic TEG-A010 measured rack map"
