"""RDX Route-A source parity and fail-closed selection; no real VIN, receipt or flash image."""
import hashlib
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral import rdx_identity as identity, vfn_eps_core as core
from openpilot.nrdr.features.lateral.controller_selection import RDX_PROFILE, firmware_controller_profile, firmware_controller_selected
from openpilot.nrdr.features.lateral.honda_rack_map import get_rack_map_table
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
from openpilot.nrdr.features.lateral.rdx_rack import RDX_POSITION
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode, resolve_steer_ratio_selection


def rdx(fingerprint="ACURA_RDX_3G"):
  return NS(brand="honda", carFingerprint=fingerprint, carVin="TEST1234567890123",
            fuzzyFingerprint=False, dashcamOnly=False, notCar=False, passive=False, fingerprintSource="fw",
            lateralParams=NS(torqueBP=[0, 4096], torqueV=[0, 4096]), lateralTuning=NS(which=lambda: "pid"),
            steerRatio=11.95, wheelbase=2.75, steerLimitTimer=.8,
            carFw=[NS(ecu="eps", address=0x18DA30F1, subAddress=0, fwVersion=b"39990-TJB,A220\0\0", logging=False)])


MODIFIED = NS(flags=HondaFlagsSP.EPS_MODIFIED.value)


def simulate_receipt(monkeypatch, cp):
  # This synthetic pin exists ONLY in this test process. It is not an image identity.
  pin = "3dd8b91b" + "f" * 56
  record = f"route-a-v1:{cp.carFingerprint}:{hashlib.sha256(cp.carVin.encode()).hexdigest()}:{pin}".encode()
  monkeypatch.setattr(identity, "RDX_ROUTE_A_SHA256", pin)
  monkeypatch.setattr(identity, "_owner_receipt", lambda: record)
  return record


def test_prefix_only_never_checks_or_admits_a_receipt(monkeypatch):
  cp = rdx()
  for pin in (None, "3dd8b91b"):
    monkeypatch.setattr(identity, "RDX_ROUTE_A_SHA256", pin)
    monkeypatch.setattr(identity, "_owner_receipt", lambda: pytest.fail("no full pin; must not poll settings"))
    assert firmware_controller_profile(cp, MODIFIED) is get_honda_vgr_profile(cp) is get_rack_map_table(cp) is None


@pytest.mark.parametrize("fingerprint", identity.RDX_CARS)
def test_confirmed_exact_rdx_does_not_select_controller_or_geometry(monkeypatch, fingerprint):
  cp = rdx(fingerprint)
  simulate_receipt(monkeypatch, cp)
  assert firmware_controller_profile(cp, MODIFIED) is RDX_PROFILE
  assert not firmware_controller_selected({}, cp, MODIFIED)
  assert not firmware_controller_selected({"NrdrLateralController": 0}, cp, MODIFIED)
  assert firmware_controller_selected({"NrdrLateralController": 1}, cp, MODIFIED)
  assert firmware_controller_profile(cp, NS(flags=0)) is None
  assert resolve_steer_ratio_selection(cp, {"NrdrSteerRatioMode": SteerRatioMode.COMMA}).rack_map is None
  rack = resolve_steer_ratio_selection(cp, {"NrdrSteerRatioMode": SteerRatioMode.FIRMWARE}).rack_map
  assert rack.profile is RDX_POSITION and rack.table.measured == (fingerprint == "ACURA_RDX_3G")
  for speed in (3., 15., 30.):
    for angle in (-480., -200., -10., 4., 90., 400., 480.):
      assert rack.angle_from_curvature(rack.curvature_from_angle(angle, speed, .01), speed, .01) == pytest.approx(angle, abs=.001)


@pytest.mark.parametrize("change", [
  {"carFingerprint": "ACURA_RDX_3G_MMR"}, {"carFingerprint": "ACURA_RDX"}, {"carVin": "TEST1234567890124"},
  {"carVin": "0" * 17}, {"carVin": ""}, {"brand": "toyota"}, {"passive": True}, {"dashcamOnly": True},
  {"fuzzyFingerprint": True}, {"notCar": True}, {"fingerprintSource": "fixed"},
  {"lateralTuning": NS(which=lambda: "torque")}, {"lateralParams": NS(torqueBP=[0, 4096], torqueV=[0, 4076])},
  {"lateralParams": NS(torqueBP=[0, 128, 4096], torqueV=[0, 128, 4096])}, {"carFw": []},
])
def test_wrong_identity_or_transport_cannot_use_a_valid_receipt(monkeypatch, change):
  cp = rdx()
  simulate_receipt(monkeypatch, cp)
  vars(cp).update(change)
  assert firmware_controller_profile(cp, MODIFIED) is get_honda_vgr_profile(cp) is get_rack_map_table(cp) is None


@pytest.mark.parametrize("change", [
  {"fwVersion": b"39990-TJB-A220\0\0"}, {"fwVersion": b"39990-TJB,A220"}, {"fwVersion": b"39990-TJB,A220\0\0X"},
  {"fwVersion": b"39990-TJB,A210\0\0"}, {"address": 0x18DA31F1}, {"subAddress": 1}, {"logging": True}, {"ecu": "engine"},
])
def test_stale_modified_flag_cannot_rescue_nonexact_rack(monkeypatch, change):
  cp = rdx()
  simulate_receipt(monkeypatch, cp)
  vars(cp.carFw[0]).update(change)
  assert firmware_controller_profile(cp, MODIFIED) is get_honda_vgr_profile(cp) is None


def test_conflicting_eps_reply_and_malformed_receipts(monkeypatch):
  cp = rdx()
  receipt = simulate_receipt(monkeypatch, cp)
  cp.carFw.append(NS(**(vars(cp.carFw[0]) | {"fwVersion": b"stock"})))
  assert not identity.confirmed_rdx(cp)
  cp.carFw[-1].logging = True
  assert identity.confirmed_rdx(cp)
  for wrong in (None, b"", b"1", b"3dd8b91b", receipt[:-1], receipt + b"\n", receipt.decode()):
    monkeypatch.setattr(identity, "_owner_receipt", lambda wrong=wrong: wrong)
    assert not identity.confirmed_rdx(cp)


def test_rdx_inversion_in_native_tjb_units_across_entire_command_range():
  cal = core.RDX_TJB_A220
  assert cal.output_ceiling() == 1. and cal.e4_per_output == 4096 and cal.key_clamp == 1774
  for a in range(-1024, 1025):
    r5 = np.sign(a) * np.interp(abs(a), range(0, 1025, 128), (0, 3968, 7936, 11904, 15872, 19840, 23808, 27776, 30000))
    assert core.r5_from_output(-a / 1024, 20., cal) == pytest.approx(r5, abs=40)
    assert core.output_from_r5(r5, cal) == pytest.approx(-a / 1024, abs=.001)
    kp = np.interp(abs(a), (0, 58, 109, 243, 320, 448, 640, 896, 1024), (7, 8, 9, 11, 13, 15, 16, 17, 17))
    assert core.firmware_kp(r5, cal) / 1024 == pytest.approx(kp / 64, rel=.02)
  assert core.firmware_r6(1., 0., cal) == pytest.approx(-7.8 * 32 * 15768 / 32768, abs=.1)
  assert core.firmware_r6(1., 200., cal) / cal.r6_per_deg_s == pytest.approx(9.58 / 7.8, rel=.01)
  assert (core.friction_width(25., cal.friction_width_v), core.friction_width(25.)) == (15., 5.)
  for angle in (0., 30., 140., 400.):
    for rate in (-80., -4., 0., 30.):
      for load in (-1200., 0., 1300.):
        r5 = core.r5_for_motion(load, rate, angle_deg=angle, cal=cal)
        assert core.firmware_output(r5, rate, angle, cal) == pytest.approx(load, abs=1e-6)
