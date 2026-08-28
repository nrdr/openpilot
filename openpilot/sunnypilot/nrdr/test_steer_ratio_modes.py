import math
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  CLARITY_RAW_ANGLE_BP,
  CLARITY_RAW_EXTRACTOR_SHA256,
  CLARITY_RAW_NEAR_LOCK_ANGLE_DEG,
  CLARITY_RAW_NEAR_LOCK_LEFT_COUNT,
  CLARITY_RAW_NEAR_LOCK_RAW_DOMAIN_RATIO,
  CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT,
  CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT,
  CLARITY_RAW_SOURCE_BLOB,
  CLARITY_RAW_SOURCE_COMMIT,
  CLARITY_RAW_STEER_RATIO,
  CLARITY_RAW_SYNCED_CSV_SHA256,
  CLARITY_RAW_TAIL_CACHE_META_SHA256,
  CLARITY_RAW_TAIL_CACHE_SHA256,
  CLARITY_RAW_TAIL_SEGMENTS,
  GENERIC_OUTER_ANGLE_DEG,
  MANUAL_CENTER_DEFAULT,
  MANUAL_FINAL_DEFAULT,
  SteerRatioMode,
  SteerRatioResolver,
  clarity_raw_domain_ratio_at,
  clarity_raw_steer_ratio_at,
)


ORIGINAL_54F_RAW_ANGLES = (
  0.0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5,
  57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5,
)
ORIGINAL_54F_RAW_DOMAIN_RATIOS = (
  19.679678, 19.679678, 20.665984, 19.948804, 19.330348, 19.362985,
  19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309,
  17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118,
  17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368,
)


class FakeParams:
  def __init__(self, mode=0, center=MANUAL_CENTER_DEFAULT, final=MANUAL_FINAL_DEFAULT):
    self.values = {
      "NrdrSteerRatioMode": mode,
      "NrdrSteerRatioManualCenter": center,
      "NrdrSteerRatioManualFinal": final,
    }

  def get(self, key):
    return self.values.get(key)


class FakeVehicleModel:
  def __init__(self, ratio: float):
    self.sR = ratio
    self.sr_curve = "must be neutralized"

  def calc_curvature(self, angle_rad, _speed, _roll):
    assert self.sr_curve is None
    return angle_rad / self.sR + _roll * 0.001

  def get_steer_from_curvature(self, curvature, _speed, _roll):
    assert self.sr_curve is None
    return (curvature - _roll * 0.001) * self.sR


def car(fingerprint="HONDA_CLARITY", firmware="39990-TRW-A020", ratio=16.5, brand="honda"):
  car_fw = [] if firmware is None else [SimpleNamespace(ecu="eps", fwVersion=firmware)]
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, steerRatio=ratio, carFw=car_fw)


def resolver(mode, *, fingerprint="HONDA_CLARITY", firmware="39990-TRW-A020", ratio=16.5,
             center=MANUAL_CENTER_DEFAULT, final=MANUAL_FINAL_DEFAULT):
  return SteerRatioResolver(car(fingerprint, firmware, ratio), FakeParams(mode, center, final))


def test_raw_profile_preserves_every_legacy_literal_and_appends_only_the_audited_tail_anchor():
  assert CLARITY_RAW_SOURCE_COMMIT == "54f74ae3e5973aa681904780f8cac140870a2b5f"
  assert CLARITY_RAW_SOURCE_BLOB == "8a96cab2b8d5fcfa055709e997bea38e3f5724b0"
  assert CLARITY_RAW_ANGLE_BP[:-1] == ORIGINAL_54F_RAW_ANGLES
  assert CLARITY_RAW_STEER_RATIO[:-1] == ORIGINAL_54F_RAW_DOMAIN_RATIOS
  assert CLARITY_RAW_ANGLE_BP[-1] == CLARITY_RAW_NEAR_LOCK_ANGLE_DEG
  assert CLARITY_RAW_STEER_RATIO[-1] == CLARITY_RAW_NEAR_LOCK_RAW_DOMAIN_RATIO
  assert CLARITY_RAW_STEER_RATIO[2] > CLARITY_RAW_STEER_RATIO[1]
  assert CLARITY_RAW_STEER_RATIO[10] > CLARITY_RAW_STEER_RATIO[9]
  assert CLARITY_RAW_NEAR_LOCK_ANGLE_DEG == 435.7
  assert CLARITY_RAW_NEAR_LOCK_RAW_DOMAIN_RATIO == 15.435171905851


def test_raw_tail_provenance_and_bilateral_counts_are_pinned():
  assert CLARITY_RAW_SYNCED_CSV_SHA256 == "861D8E00B286D5412C6C6D3908564789270A2026EC824EB6F49BD11793D96672"
  assert CLARITY_RAW_EXTRACTOR_SHA256 == "5CE250872F7607409E3562FECC323CC1FF69F3F20351F46BA72FA5887A7185C6"
  assert CLARITY_RAW_TAIL_CACHE_SHA256 == "1A633B31B91EDFFF9CE9D4F83B240566F21476B028D02960E7B14E44839E725B"
  assert CLARITY_RAW_TAIL_CACHE_META_SHA256 == "FAC9AB6F9C4E4DDACDBFC43911F7694DD8E7B07759C8C150F6F4DA12DBAF1CAE"
  assert CLARITY_RAW_TAIL_SEGMENTS == (
    "0000007e--d4a413c4c4--296",
    "00000080--ddc219bb73--4",
    "00000081--49da42be4e--18",
    "0000008a--91b97700bb--5",
    "0000008a--91b97700bb--6",
  )
  assert CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT == 825
  assert CLARITY_RAW_NEAR_LOCK_LEFT_COUNT == 598
  assert CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT == 227
  assert CLARITY_RAW_NEAR_LOCK_LEFT_COUNT + CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT == CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT


def test_raw_curve_ships_complete_provenance_evidence():
  evidence_path = Path(__file__).with_name("CLARITY_RAW_STEER_RATIO_EVIDENCE.md")
  evidence = evidence_path.read_text(encoding="utf-8")
  expected_evidence = (
    "861D8E00B286D5412C6C6D3908564789270A2026EC824EB6F49BD11793D96672",
    "5CE250872F7607409E3562FECC323CC1FF69F3F20351F46BA72FA5887A7185C6",
    "1A633B31B91EDFFF9CE9D4F83B240566F21476B028D02960E7B14E44839E725B",
    "FAC9AB6F9C4E4DDACDBFC43911F7694DD8E7B07759C8C150F6F4DA12DBAF1CAE",
    "0000007e--d4a413c4c4--296",
    "00000080--ddc219bb73--4",
    "00000081--49da42be4e--18",
    "0000008a--91b97700bb--5",
    "0000008a--91b97700bb--6",
    "pose_ok",
    "calibrationValid",
    "posenetOK",
    "7a9ad65863b713a525bebd932ee87e41448ccf57",
  )
  assert all(item in evidence for item in expected_evidence)


def _vehicle_model_ratio(angle_deg, raw_domain_ratio):
  if angle_deg == 0.0:
    return raw_domain_ratio
  theta_rad = math.radians(angle_deg)
  return theta_rad / math.tan(theta_rad / raw_domain_ratio)


@pytest.mark.parametrize("angle, expected", [
  (-500.0, 14.165673460789899),
  (0.0, ORIGINAL_54F_RAW_DOMAIN_RATIOS[0]),
  (247.5, 14.870103435525325),
  (433.8, 14.17519860618587),
  (435.7, 14.165673460789899),
  (500.0, 14.165673460789899),
])
def test_raw_interpolates_atan_domain_first_converts_for_vehicle_model_and_clamps_angle(angle, expected):
  selection = resolver(SteerRatioMode.NRDR_RAW)
  assert selection.effective_ratio(angle) == pytest.approx(expected)


def test_raw_midpoint_conversion_uses_interpolated_raw_value_not_interpolated_effective_ratio():
  angle = 433.8
  raw_domain_ratio = 15.279368 + (15.435171905851 - 15.279368) * (angle - 247.5) / (435.7 - 247.5)
  expected = _vehicle_model_ratio(angle, raw_domain_ratio)
  assert raw_domain_ratio == pytest.approx(15.433598965249955)
  assert clarity_raw_steer_ratio_at(angle) == pytest.approx(expected)
  assert clarity_raw_steer_ratio_at(-angle) == pytest.approx(expected)


@pytest.mark.parametrize("angle", (0.0, 7.5, 247.5, 433.8, 435.7, 1000.0, math.inf))
def test_raw_curve_is_symmetric_finite_and_clamps_at_near_lock(angle):
  assert clarity_raw_domain_ratio_at(angle) == pytest.approx(clarity_raw_domain_ratio_at(-angle))
  positive = clarity_raw_steer_ratio_at(angle)
  assert positive == pytest.approx(clarity_raw_steer_ratio_at(-angle))
  assert math.isfinite(positive)
  if angle >= CLARITY_RAW_NEAR_LOCK_ANGLE_DEG:
    assert positive == pytest.approx(clarity_raw_steer_ratio_at(CLARITY_RAW_NEAR_LOCK_ANGLE_DEG))


def test_raw_nan_falls_back_to_zero_angle_limit():
  assert clarity_raw_domain_ratio_at(math.nan) == pytest.approx(ORIGINAL_54F_RAW_DOMAIN_RATIOS[0])
  assert clarity_raw_steer_ratio_at(math.nan) == pytest.approx(ORIGINAL_54F_RAW_DOMAIN_RATIOS[0])


def test_raw_near_lock_is_not_the_old_247_point_hold_or_direct_fit_value():
  assert clarity_raw_steer_ratio_at(435.7) == pytest.approx(14.165673460789899)
  assert clarity_raw_steer_ratio_at(435.7) != pytest.approx(14.870103435525325)
  assert clarity_raw_steer_ratio_at(435.7) != pytest.approx(14.074514584823627)


def test_raw_is_clarity_only_and_never_borrows_family_data():
  for fingerprint in ("HONDA_CIVIC", "HONDA_ACCORD", "HONDA_CRV_5G", "UNKNOWN"):
    selection = resolver(SteerRatioMode.NRDR_RAW, fingerprint=fingerprint, firmware=None, ratio=17.25)
    assert not selection.available
    assert selection.effective_ratio(80.0) == pytest.approx(17.25)

  malformed_brand = SteerRatioResolver(
    car("HONDA_CLARITY", "39990-TRW-A020", 17.25, brand="toyota"), FakeParams(SteerRatioMode.NRDR_RAW),
  )
  assert not malformed_brand.available
  assert malformed_brand.effective_ratio(80.0) == pytest.approx(17.25)


def test_manual_defaults_use_exact_supported_honda_metadata():
  clarity = resolver(SteerRatioMode.MANUAL)
  assert clarity.outer_angle == 250.0
  assert clarity.effective_ratio(0.0) == pytest.approx(15.38)
  assert clarity.effective_ratio(125.0) == pytest.approx((15.38 + 10.93) / 2.0)
  assert clarity.effective_ratio(400.0) == pytest.approx(10.93)

  unknown = resolver(SteerRatioMode.MANUAL, fingerprint="UNKNOWN", firmware=None, ratio=17.1)
  assert unknown.outer_angle == GENERIC_OUTER_ANGLE_DEG
  assert not unknown.available
  assert unknown.effective_ratio(-125.0) == pytest.approx(17.1)

  non_honda = SteerRatioResolver(
    car("HONDA_CLARITY", "39990-TRW-A020", 14.9, brand="toyota"), FakeParams(SteerRatioMode.MANUAL),
  )
  assert not non_honda.available
  assert non_honda.effective_ratio(125.0) == pytest.approx(14.9)


def test_invalid_mode_and_manual_values_are_safe_and_bounded():
  selection = SteerRatioResolver(car(), FakeParams(b"99", float("nan"), 100.0))
  assert selection.mode is SteerRatioMode.MANUAL
  assert selection.settings.manual_center == MANUAL_CENTER_DEFAULT
  assert selection.settings.manual_final == 25.0


def test_comma_uses_only_a_valid_live_scalar():
  selection = resolver(SteerRatioMode.COMMA, ratio=16.5)
  selection.update_comma_ratio(SimpleNamespace(steerRatio=99.0, steerRatioValid=False))
  assert selection.effective_ratio(0.0) == pytest.approx(16.5)

  live = SimpleNamespace(steerRatio=18.75, steerRatioValid=True)
  selection.update_comma_ratio(live, service_valid=True)
  assert selection.effective_ratio(200.0) == pytest.approx(18.75)

  selection.update_comma_ratio(live, service_valid=False)
  assert selection.effective_ratio(200.0) == pytest.approx(18.75)
  selection.update_comma_ratio(SimpleNamespace(steerRatio=float("nan"), steerRatioValid=True))
  assert selection.effective_ratio(0.0) == pytest.approx(18.75)

  # Match paramsd's validity envelope as defense in depth, and hold the last
  # good value instead of stepping geometry on corrupted valid-looking input.
  selection.update_comma_ratio(SimpleNamespace(steerRatio=8.24, steerRatioValid=True))
  assert selection.effective_ratio(0.0) == pytest.approx(18.75)
  selection.update_comma_ratio(SimpleNamespace(steerRatio=33.01, steerRatioValid=True))
  assert selection.effective_ratio(0.0) == pytest.approx(18.75)


@pytest.mark.parametrize("mode, angle", [
  (SteerRatioMode.MANUAL, 125.0),
  (SteerRatioMode.NRDR_RAW, 5.0),
  (SteerRatioMode.NRDR_RAW, 50.0),
  (SteerRatioMode.FIRMWARE, 180.0),
])
def test_curvature_rate_is_a_local_finite_difference_of_full_geometry(mode, angle):
  selection = resolver(mode)
  VM = FakeVehicleModel(selection.cp_steer_ratio)
  speed = 15.0
  rate = 20.0
  dt = 0.01
  angle_offset = 1.25
  half_step = rate * dt * 0.5
  before = selection.calc_curvature(VM, angle - half_step, angle_offset, speed, 0.0)
  after = selection.calc_curvature(VM, angle + half_step, angle_offset, speed, 0.0)

  assert selection.measured_curvature_rate(VM, angle, rate, speed, dt, angle_offset) == pytest.approx((after - before) / dt)


@pytest.mark.parametrize("mode, angle", [
  (SteerRatioMode.MANUAL, 0.0),
  (SteerRatioMode.MANUAL, 180.0),
  (SteerRatioMode.NRDR_RAW, 50.0),
  (SteerRatioMode.FIRMWARE, 0.0),
  (SteerRatioMode.FIRMWARE, 180.0),
])
def test_deadzone_uses_local_physical_geometry(mode, angle):
  selection = resolver(mode)
  VM = FakeVehicleModel(selection.cp_steer_ratio)
  deadzone = 1.0
  speed = 15.0
  angle_offset = 1.25
  center = selection.calc_curvature(VM, angle, angle_offset, speed, 0.0)
  plus = selection.calc_curvature(VM, angle + deadzone, angle_offset, speed, 0.0)
  minus = selection.calc_curvature(VM, angle - deadzone, angle_offset, speed, 0.0)

  assert selection.curvature_deadzone(VM, angle, deadzone, speed, angle_offset) == pytest.approx(
    max(abs(plus - center), abs(minus - center)),
  )


def test_firmware_requires_exact_fingerprint_and_firmware_and_keeps_cp_anchor():
  exact = resolver(SteerRatioMode.FIRMWARE, ratio=17.2)
  assert exact.available
  assert exact.firmware_vgr_selected
  assert exact.effective_ratio(250.0) == pytest.approx(17.2)

  mismatch = resolver(SteerRatioMode.FIRMWARE, firmware="39990-TRW-A021", ratio=17.2)
  assert not mismatch.available
  assert not mismatch.firmware_vgr_selected
  assert mismatch.effective_ratio(250.0) == pytest.approx(17.2)

  normalized_brand = SteerRatioResolver(
    car("HONDA_CLARITY", "39990-TRW-A020", 17.2, brand="HONDA"), FakeParams(SteerRatioMode.FIRMWARE),
  )
  assert normalized_brand.available
  assert normalized_brand.firmware_vgr_selected


@pytest.mark.parametrize("mode", list(SteerRatioMode))
def test_current_and_pid_desired_paths_share_one_geometry(mode):
  selection = resolver(mode)
  selection.update_comma_ratio(SimpleNamespace(steerRatio=18.0, steerRatioValid=True))
  VM = FakeVehicleModel(selection.cp_steer_ratio)
  measured = 80.0
  current = selection.calc_curvature(VM, measured, 0.0, 15.0, 0.0)
  desired = selection.desired_angle_no_offset(VM, measured, 15.0, 0.0, current)
  assert desired == pytest.approx(measured)
  assert VM.sR == pytest.approx(selection.cp_steer_ratio)
  assert VM.sr_curve is None


@pytest.mark.parametrize("mode", list(SteerRatioMode))
def test_current_and_desired_geometry_round_trip_with_offset_and_roll(mode):
  selection = resolver(mode)
  selection.update_comma_ratio(SimpleNamespace(steerRatio=18.0, steerRatioValid=True))
  VM = FakeVehicleModel(selection.cp_steer_ratio)
  measured = 80.0
  angle_offset = 1.25
  roll = 0.04
  current = selection.calc_curvature(VM, measured, angle_offset, 15.0, roll)
  desired_no_offset = selection.desired_angle_no_offset(VM, measured, 15.0, roll, current)

  assert desired_no_offset + angle_offset == pytest.approx(measured)


@pytest.mark.parametrize("measured", (-500.0, -435.7, -433.8, 433.8, 435.7, 500.0))
def test_raw_near_lock_controller_geometry_round_trips_and_stays_finite(measured):
  selection = resolver(SteerRatioMode.NRDR_RAW)
  VM = FakeVehicleModel(selection.cp_steer_ratio)
  angle_offset = 1.7
  roll = 0.035

  current = selection.calc_curvature(VM, measured, angle_offset, 12.0, roll)
  desired_no_offset = selection.desired_angle_no_offset(VM, measured, 12.0, roll, current)

  assert math.isfinite(current)
  assert math.isfinite(desired_no_offset)
  assert desired_no_offset + angle_offset == pytest.approx(measured, abs=1e-8)
  assert selection.effective_ratio(measured) == pytest.approx(clarity_raw_steer_ratio_at(measured))
  assert VM.sR == pytest.approx(selection.cp_steer_ratio)


def test_active_changes_latch_mode_and_both_manual_values_until_disengagement():
  params = FakeParams(SteerRatioMode.MANUAL, 15.38, 10.93)
  selection = SteerRatioResolver(car(), params)
  params.values.update({
    "NrdrSteerRatioMode": SteerRatioMode.NRDR_RAW,
    "NrdrSteerRatioManualCenter": 20.0,
    "NrdrSteerRatioManualFinal": 12.0,
  })

  assert not selection.refresh(params, lateral_active=True)
  assert selection.mode is SteerRatioMode.MANUAL
  assert selection.settings.manual_center == 15.38
  assert selection.settings.manual_final == 10.93

  assert selection.refresh(params, lateral_active=False)
  assert selection.mode is SteerRatioMode.NRDR_RAW
  assert selection.settings.manual_center == 20.0
  assert selection.settings.manual_final == 12.0


def test_model_artifact_policy_is_not_an_input_to_mode_resolution():
  params = FakeParams(SteerRatioMode.MANUAL)
  params.values["ModelManager_ActiveBundle"] = '{"artifactSha256":"anything"}'
  selection = SteerRatioResolver(car(), params)
  assert selection.mode is SteerRatioMode.MANUAL
