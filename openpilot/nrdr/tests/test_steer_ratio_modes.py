from types import SimpleNamespace
import math
from pathlib import Path

import pytest

from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  CLARITY_RAW_STEER_RATIO,
  SteerRatioMode,
  SteerRatioModeLatch,
  resolve_steer_ratio_selection,
)
from openpilot.nrdr.hooks.controlsd import vehicle_model_state


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
NEAR_LOCK_ANGLE_DEG = 435.7
NEAR_LOCK_RAW_DOMAIN_RATIO = 15.435171905851


def cp(fingerprint="HONDA_CLARITY", steer_ratio=16.5, firmware=None):
  car_fw = [] if firmware is None else [SimpleNamespace(ecu="eps", fwVersion=firmware)]
  return SimpleNamespace(brand="honda", carFingerprint=fingerprint, steerRatio=steer_ratio, carFw=car_fw)


def settings(mode=0, center=15.38, final=10.93):
  return {
    "NrdrSteerRatioMode": mode,
    "NrdrSteerRatioManualCenter": center,
    "NrdrSteerRatioManualFinal": final,
  }


def test_clarity_raw_curve_preserves_54f_literals_and_appends_audited_near_lock_anchor():
  assert CLARITY_RAW_STEER_RATIO.angles_deg[:-1] == ORIGINAL_54F_RAW_ANGLES
  assert CLARITY_RAW_STEER_RATIO.ratios[:-1] == ORIGINAL_54F_RAW_DOMAIN_RATIOS
  assert CLARITY_RAW_STEER_RATIO.angles_deg[-1] == NEAR_LOCK_ANGLE_DEG
  assert CLARITY_RAW_STEER_RATIO.ratios[-1] == NEAR_LOCK_RAW_DOMAIN_RATIO
  assert "54f74ae3e5973aa681904780f8cac140870a2b5f" in CLARITY_RAW_STEER_RATIO.provenance
  assert "8a96cab2b8d5fcfa055709e997bea38e3f5724b0" in CLARITY_RAW_STEER_RATIO.provenance


def test_clarity_raw_curve_ships_complete_provenance_evidence():
  evidence_path = Path(__file__).resolve().parents[1] / "features/lateral/CLARITY_RAW_STEER_RATIO_EVIDENCE.md"
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


def test_clarity_raw_domain_interpolation_precedes_vehicle_model_conversion():
  profile = CLARITY_RAW_STEER_RATIO
  assert profile.raw_domain_ratio_at(-7.5) == pytest.approx(20.665984)
  assert profile.raw_domain_ratio_at(5.0) == pytest.approx((19.679678 + 20.665984) / 2.0)
  assert profile.raw_domain_ratio_at(1000.0) == pytest.approx(NEAR_LOCK_RAW_DOMAIN_RATIO)
  assert profile.raw_domain_ratio_at(47.5) > profile.raw_domain_ratio_at(42.5)

  assert profile.ratio_at(0.0) == pytest.approx(ORIGINAL_54F_RAW_DOMAIN_RATIOS[0])
  assert profile.ratio_at(247.5) == pytest.approx(14.8701034355)
  assert profile.ratio_at(435.7) == pytest.approx(14.1656734608)
  assert profile.ratio_at(433.8) == pytest.approx(14.1751986062)


@pytest.mark.parametrize("angle", (0.0, 7.5, 247.5, 433.8, 435.7, 1000.0, math.inf, math.nan))
def test_clarity_raw_curve_is_symmetric_finite_and_clamps_at_near_lock(angle):
  profile = CLARITY_RAW_STEER_RATIO
  positive = profile.ratio_at(angle)
  negative = profile.ratio_at(-angle)
  assert positive == pytest.approx(negative)
  assert math.isfinite(positive)
  if angle >= NEAR_LOCK_ANGLE_DEG:
    assert positive == pytest.approx(profile.ratio_at(NEAR_LOCK_ANGLE_DEG))


def test_manual_mode_uses_global_values_and_hidden_outer_angle():
  clarity = resolve_steer_ratio_selection(cp(), settings(center=15.38, final=10.93))
  assert clarity.effective_mode is SteerRatioMode.MANUAL
  assert clarity.manual_outer_angle_deg == 250.0
  assert clarity.ratio_at(0.0) == pytest.approx(15.38)
  assert clarity.ratio_at(125.0) == pytest.approx((15.38 + 10.93) / 2.0)
  assert clarity.ratio_at(500.0) == pytest.approx(10.93)

  unknown = resolve_steer_ratio_selection(cp("HONDA_ODYSSEY"), settings())
  assert unknown.effective_mode is None
  assert unknown.ratio_at(125.0) == pytest.approx(16.5)
  assert "not supported" in unknown.unavailable_reason

  spoofed_non_honda = resolve_steer_ratio_selection(
    SimpleNamespace(brand="toyota", carFingerprint="HONDA_CLARITY", steerRatio=14.2, carFw=[]),
    settings(),
  )
  assert spoofed_non_honda.effective_mode is None
  assert spoofed_non_honda.ratio_at(125.0) == pytest.approx(14.2)


def test_invalid_mode_is_manual_and_unsupported_explicit_modes_fall_back_for_whole_controller():
  invalid = resolve_steer_ratio_selection(cp(), settings(mode=99))
  assert invalid.requested_mode is SteerRatioMode.MANUAL
  assert invalid.effective_mode is SteerRatioMode.MANUAL

  civic_raw = resolve_steer_ratio_selection(cp("HONDA_CIVIC_BOSCH", 15.4), settings(mode=2))
  assert civic_raw.requested_mode is SteerRatioMode.NRDR_RAW
  assert civic_raw.effective_mode is None
  assert civic_raw.ratio_at(0.0) == pytest.approx(15.4)
  assert civic_raw.ratio_at(400.0) == pytest.approx(15.4)
  assert "No exact audited" in civic_raw.unavailable_reason

  no_firmware = resolve_steer_ratio_selection(cp("HONDA_CLARITY", 16.5), settings(mode=3))
  assert no_firmware.requested_mode is SteerRatioMode.FIRMWARE
  assert no_firmware.effective_mode is None
  assert no_firmware.ratio_at(200.0) == pytest.approx(16.5)


def test_firmware_mode_uses_exact_profile_and_immutable_cp_anchor():
  selection = resolve_steer_ratio_selection(cp(firmware=b"39990-TRW-A020"), settings(mode=3, center=25.0, final=8.0))
  assert selection.firmware_vgr_selected
  assert selection.ratio_at(200.0) == pytest.approx(16.5)
  physical = selection.physicalize_desired_angle(180.0)
  assert physical != pytest.approx(180.0)
  assert selection.linearize_measured_angle(physical) == pytest.approx(180.0)


def test_mode_latch_defers_complete_snapshot_while_active():
  manual = resolve_steer_ratio_selection(cp(), settings(mode=0, center=15.38, final=10.93))
  raw = resolve_steer_ratio_selection(cp(), settings(mode=2))
  latch = SteerRatioModeLatch(manual)
  assert latch.update(raw, active=True) is manual
  assert latch.pending is raw
  assert latch.update(raw, active=False) is raw
  assert latch.pending is None


class CaptureController:
  def set_steer_ratio_selection(self, selection):
    self.selection = selection


def control_fixture(initial_settings, *, sm_valid=True):
  snapshot = initial_settings
  controls = SimpleNamespace(
    CP=cp(),
    nrdr_live_params=SimpleNamespace(snapshot=snapshot),
    learn_stiffness=False,
    learn_angle_offset=False,
    LaC=CaptureController(),
    sm=SimpleNamespace(valid={"vehicleParameters": sm_valid}),
  )
  controls.steer_ratio_latch = SteerRatioModeLatch(resolve_steer_ratio_selection(controls.CP, snapshot))
  return controls


def test_comma_requires_valid_learning_and_valid_submaster_message():
  live = SimpleNamespace(steerRatio=21.0, steerRatioValid=False, stiffnessFactor=1.0, angleOffsetDeg=0.0)
  CS = SimpleNamespace(steeringAngleDeg=30.0)
  controls = control_fixture(settings(mode=1))
  assert vehicle_model_state(controls, live, CS, False)[1] == pytest.approx(16.5)

  live.steerRatioValid = True
  controls.sm.valid["vehicleParameters"] = False
  assert vehicle_model_state(controls, live, CS, False)[1] == pytest.approx(16.5)

  controls.sm.valid["vehicleParameters"] = True
  assert vehicle_model_state(controls, live, CS, False)[1] == pytest.approx(21.0)

  live.steerRatio = math.nan
  live.steerRatioValid = False
  assert vehicle_model_state(controls, live, CS, True)[1] == pytest.approx(21.0)

  live.steerRatioValid = True
  for inconsistent_ratio in (8.24, 33.01):
    live.steerRatio = inconsistent_ratio
    assert vehicle_model_state(controls, live, CS, True)[1] == pytest.approx(21.0)


def test_current_and_desired_paths_share_one_latched_selection_frame():
  live = SimpleNamespace(steerRatio=17.0, steerRatioValid=True, stiffnessFactor=1.0, angleOffsetDeg=0.0, roll=0.0)
  CS = SimpleNamespace(steeringAngleDeg=47.5, vEgo=15.0)
  controls = control_fixture(settings(mode=2))
  _, current_ratio, _, _ = vehicle_model_state(controls, live, CS, True)
  selection = controls.LaC.selection
  assert current_ratio == pytest.approx(CLARITY_RAW_STEER_RATIO.ratio_at(47.5))

  class VM:
    def __init__(self):
      self.sR = current_ratio

    def get_steer_from_curvature(self, curvature, _speed, _roll):
      return curvature * self.sR

  vm = VM()
  desired_no_offset = selection.desired_angle_no_offset(vm, CS.steeringAngleDeg, CS.vEgo, live.roll, -0.01)
  assert vm.sR == pytest.approx(current_ratio)
  assert desired_no_offset == pytest.approx(math.degrees(0.01 * current_ratio))

  controls.nrdr_live_params.snapshot = settings(mode=0, center=8.0, final=8.0)
  _, still_latched, _, _ = vehicle_model_state(controls, live, CS, True)
  assert still_latched == pytest.approx(current_ratio)
  assert controls.LaC.selection is selection
  _, changed, _, _ = vehicle_model_state(controls, live, CS, False)
  assert changed == pytest.approx(8.0)
  assert controls.LaC.selection is not selection


class LinearVehicleModel:
  def __init__(self, steer_ratio=16.5):
    self.sR = steer_ratio

  def get_steer_from_curvature(self, curvature, _speed, _roll):
    return curvature * self.sR

  def calc_curvature(self, steer_angle, _speed, _roll):
    return steer_angle / self.sR


class RollAwareVehicleModel(LinearVehicleModel):
  def get_steer_from_curvature(self, curvature, _speed, roll):
    return (curvature - 0.002 * roll) * self.sR

  def calc_curvature(self, steer_angle, _speed, roll):
    return steer_angle / self.sR + 0.002 * roll


@pytest.mark.parametrize("mode", tuple(SteerRatioMode))
def test_all_four_modes_round_trip_current_and_desired_geometry_with_offset_and_roll(mode):
  CP = cp(firmware=b"39990-TRW-A020")
  selection = resolve_steer_ratio_selection(CP, settings(mode=mode))
  assert selection.effective_mode is mode
  vm = RollAwareVehicleModel(18.2 if mode is SteerRatioMode.COMMA else CP.steerRatio)
  measured_angle = 85.0
  angle_offset = 1.7
  roll = 0.035

  measured_curvature = selection.measured_curvature(
    vm, measured_angle, 22.0, roll, angle_offset,
  )
  desired_no_offset = selection.desired_angle_no_offset(
    vm, measured_angle, 22.0, roll, measured_curvature,
  )

  assert desired_no_offset + angle_offset == pytest.approx(measured_angle, abs=1e-8)


@pytest.mark.parametrize("measured_angle", (-500.0, -435.7, -433.8, 433.8, 435.7, 500.0))
def test_raw_near_lock_controller_geometry_round_trips_and_stays_finite(measured_angle):
  selection = resolve_steer_ratio_selection(cp(), settings(mode=SteerRatioMode.NRDR_RAW))
  vm = RollAwareVehicleModel(selection.cp_ratio)
  angle_offset = 1.7
  roll = 0.035

  measured_curvature = selection.measured_curvature(vm, measured_angle, 12.0, roll, angle_offset)
  desired_no_offset = selection.desired_angle_no_offset(
    vm, measured_angle, 12.0, roll, measured_curvature,
  )

  assert math.isfinite(measured_curvature)
  assert math.isfinite(desired_no_offset)
  assert desired_no_offset + angle_offset == pytest.approx(measured_angle, abs=1e-8)
  assert vm.sR == pytest.approx(CLARITY_RAW_STEER_RATIO.ratio_at(measured_angle))


@pytest.mark.parametrize("mode", (SteerRatioMode.MANUAL, SteerRatioMode.COMMA, SteerRatioMode.NRDR_RAW))
def test_shared_geometry_helpers_cover_desired_measured_deadzone_and_rate(mode):
  selection = resolve_steer_ratio_selection(cp(), settings(mode=mode))
  vm = LinearVehicleModel(17.0 if mode is SteerRatioMode.COMMA else 16.5)
  measured = selection.measured_curvature(vm, 47.5, 15.0, 0.0)
  desired = selection.desired_angle_no_offset(vm, 47.5, 15.0, 0.0, 0.01)
  deadzone = selection.curvature_deadzone(vm, 47.5, 1.0, 15.0)
  curvature_rate = selection.measured_curvature_rate(vm, 47.5, 2.0, 15.0, 0.01)

  assert all(math.isfinite(value) for value in (measured, desired, deadzone, curvature_rate))
  assert deadzone > 0.0
  assert curvature_rate < 0.0


@pytest.mark.parametrize(("mode", "angle"), (
  (SteerRatioMode.MANUAL, 0.0),
  (SteerRatioMode.MANUAL, 180.0),
  (SteerRatioMode.NRDR_RAW, 50.0),
  (SteerRatioMode.FIRMWARE, 0.0),
  (SteerRatioMode.FIRMWARE, 180.0),
))
def test_deadzone_and_rate_use_local_physical_geometry_for_nonlinear_modes(mode, angle):
  selection = resolve_steer_ratio_selection(cp(firmware=b"39990-TRW-A020"), settings(mode=mode))
  vm = LinearVehicleModel(selection.cp_ratio)
  angle_offset = 1.25
  center = selection.measured_curvature(vm, angle, 15.0, 0.0, angle_offset)
  plus = selection.measured_curvature(vm, angle + 1.0, 15.0, 0.0, angle_offset)
  minus = selection.measured_curvature(vm, angle - 1.0, 15.0, 0.0, angle_offset)
  assert selection.curvature_deadzone(vm, angle, 1.0, 15.0, angle_offset) == pytest.approx(
    max(abs(plus - center), abs(minus - center)),
  )

  rate = 20.0
  dt = 0.01
  half_step = rate * dt * 0.5
  before = selection.measured_curvature(vm, angle - half_step, 15.0, 0.0, angle_offset)
  after = selection.measured_curvature(vm, angle + half_step, 15.0, 0.0, angle_offset)
  assert selection.measured_curvature_rate(vm, angle, rate, 15.0, dt, angle_offset) == pytest.approx((after - before) / dt)


def test_every_lateral_controller_path_uses_the_shared_selection_api():
  repository_root = Path(__file__).resolve().parents[3]
  expected_helpers = {
    "openpilot/selfdrive/controls/lib/latcontrol_angle.py": ("desired_angle_no_offset",),
    "openpilot/selfdrive/controls/lib/latcontrol_pid.py": ("desired_angle_no_offset",),
    "openpilot/nrdr/features/lateral/latcontrol_pid.py": ("desired_angle_no_offset",),
    "openpilot/selfdrive/controls/lib/latcontrol_torque.py": ("measured_curvature", "curvature_deadzone"),
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_v0.py": ("measured_curvature", "curvature_deadzone"),
    "openpilot/selfdrive/controls/lib/latcontrol_curvature.py": ("measured_curvature",),
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_ext_base.py": ("measured_curvature_rate",),
  }
  for relative_path, helpers in expected_helpers.items():
    source = (repository_root / relative_path).read_text(encoding="utf-8")
    for helper in helpers:
      assert f"steer_ratio_selection.{helper}" in source, f"{relative_path} bypasses {helper}"

  hybrid = (repository_root / "openpilot/nrdr/features/lateral/latcontrol_clarity_hybrid.py").read_text(encoding="utf-8")
  assert "self.pid_controller.set_steer_ratio_selection(selection)" in hybrid
  assert "self.torque_controller.set_steer_ratio_selection(selection)" in hybrid
