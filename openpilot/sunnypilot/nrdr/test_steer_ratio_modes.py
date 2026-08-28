from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  CLARITY_RAW_ANGLE_BP,
  CLARITY_RAW_SOURCE_BLOB,
  CLARITY_RAW_SOURCE_COMMIT,
  CLARITY_RAW_STEER_RATIO,
  GENERIC_OUTER_ANGLE_DEG,
  MANUAL_CENTER_DEFAULT,
  MANUAL_FINAL_DEFAULT,
  SteerRatioMode,
  SteerRatioResolver,
)


RAW_ANGLES = (
  0.0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5,
  57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5,
)
RAW_RATIOS = (
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


def test_raw_profile_is_the_literal_audited_csv_data():
  assert CLARITY_RAW_SOURCE_COMMIT == "54f74ae3e5973aa681904780f8cac140870a2b5f"
  assert CLARITY_RAW_SOURCE_BLOB == "8a96cab2b8d5fcfa055709e997bea38e3f5724b0"
  assert CLARITY_RAW_ANGLE_BP == RAW_ANGLES
  assert CLARITY_RAW_STEER_RATIO == RAW_RATIOS
  assert CLARITY_RAW_STEER_RATIO[2] > CLARITY_RAW_STEER_RATIO[1]
  assert CLARITY_RAW_STEER_RATIO[10] > CLARITY_RAW_STEER_RATIO[9]


@pytest.mark.parametrize("angle, expected", [
  (-500.0, RAW_RATIOS[-1]),
  (0.0, RAW_RATIOS[0]),
  (1.0, RAW_RATIOS[0]),
  (7.5, RAW_RATIOS[2]),
  (250.0, RAW_RATIOS[-1]),
])
def test_raw_uses_absolute_measured_angle_and_endpoint_clamps(angle, expected):
  selection = resolver(SteerRatioMode.NRDR_RAW)
  assert selection.effective_ratio(angle) == pytest.approx(expected)


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
