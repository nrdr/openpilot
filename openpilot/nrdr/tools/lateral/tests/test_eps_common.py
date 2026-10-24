import numpy as np
import pytest

from openpilot.nrdr.tools.lateral import eps_common


def test_yaw_decode_ramps_the_clockwise_correction_in():
  scale, _, right = eps_common.YAW_RATE_CALIBRATION["HONDA_CIVIC"]
  assert eps_common.yaw_rate_deg_s(0.0, scale, right) == 0.0
  assert eps_common.yaw_rate_deg_s(-10.0, scale, right) == pytest.approx(-10.0 * scale)  # left: no correction
  assert eps_common.yaw_rate_deg_s(4.0, scale, right) == pytest.approx(4.0 * scale + right / 2)
  assert eps_common.yaw_rate_deg_s(10.0, scale, right) == pytest.approx(10.0 * scale + right)
  assert eps_common.vsa_counts(bytes([0x80, 0x00])) == 512


@pytest.mark.parametrize("fingerprint,eps_fw", [
  ("HONDA_CLARITY", "39990-TRW-A020"), ("HONDA_CIVIC", "39990-TEG-A010"), ("HONDA_INSIGHT", "39990-TXM-A040"),
  ("HONDA_CIVIC_BOSCH", "39990-TBA-C020"),
])
def test_vgr_inverse_samples_the_exact_table(fingerprint, eps_fw):
  profile = eps_common.vgr_profile(fingerprint, eps_fw)
  linear, angle = eps_common.vgr_inverse(profile)
  assert np.all(np.diff(angle) > 0) and np.all(np.diff(linear) > 0)
  for a in (3.0, 47.0, 133.0, 301.0):
    assert np.interp(a, angle, linear) == pytest.approx(profile.physical_to_linear(a), abs=0.01)


def test_unknown_eps_has_no_profile_or_calibration():
  assert eps_common.vgr_profile("HONDA_CIVIC", "39990-XXX-A000") is None
  assert eps_common.vgr_profile("HONDA_CIVIC", None) is None
  assert eps_common.firmware_profile("HONDA_CIVIC", None) is None
  assert eps_common.prediction_schedule(None) is None


def test_event_names_cover_old_and_new_logs():
  assert eps_common.VEHICLE_PARAMETERS == ("vehicleParameters", "liveParameters")
  assert eps_common.DEVICE_POSE == ("deviceMotion", "livePose")


def test_rack_map_finds_the_cars_map_when_the_tree_has_rack_maps():
  # guards the lookup against renames in honda_rack_map: with the module present, a mapped car must get its map
  pytest.importorskip("openpilot.nrdr.features.lateral.honda_rack_map")
  rack = eps_common.rack_map("HONDA_CIVIC", b"39990-TEG,A010\x00\x00", 15.38)
  assert rack is not None and rack.table.ratio_v[0] == pytest.approx(14.16)
  assert eps_common.rack_map("HONDA_CIVIC", b"39990-TBA,C020\x00\x00", 15.38) is None  # never borrowed


@pytest.mark.parametrize("path,expected", (
  (r"C:\drive\0000013d--8de8634497--43\rlog.zst", 43),
  ("/drive/0000013d--8de8634497--43/rlog.zst", 43),
  (r"C:\drive\rlog_10.zst", 10),
  ("/drive/rlog_2.bz2", 2),
  (r"C:\drive\device_route--10--rlog.zst", 10),
  ("/drive/device_route--2--rlog.zst", 2),
))
def test_plan_timing_orders_segment_numbers_on_both_platforms(path, expected):
  from openpilot.nrdr.tools.lateral.eps_plan_timing import seg_number
  assert seg_number(path) == expected
  assert eps_common.log_segment_number(path) == expected


def test_flat_downloads_sort_numerically_not_lexically():
  files = [f"/drive/route--{segment}--rlog.zst" for segment in (0, 1, 10, 11, 2)]
  assert [eps_common.log_segment_number(p) for p in sorted(files, key=eps_common.log_segment_number)] == [0, 1, 2, 10, 11]
