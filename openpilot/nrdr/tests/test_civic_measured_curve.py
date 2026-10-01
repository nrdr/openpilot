from dataclasses import replace
import math
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  CIVIC_TEG_PROVISIONAL_STEER_RATIO as PROFILE,
  CLARITY_RAW_STEER_RATIO,
  SteerRatioMode,
  SteerRatioModeLatch,
  get_raw_steer_ratio_profile,
  resolve_steer_ratio_selection,
  stock_steer_ratio_selection,
)


def cp(fingerprint='HONDA_CIVIC', firmware=b'39990-TEG-A010', brand='honda'):
  return SimpleNamespace(carFingerprint=fingerprint, brand=brand, steerRatio=15.38,
                         carFw=[] if firmware is None else [SimpleNamespace(ecu='eps', fwVersion=firmware)])


def test_draft_literals_are_explicitly_model_normalized_and_not_double_converted():
  assert PROFILE.ratio_domain == 'vehicle-model'
  assert PROFILE.provisional
  assert PROFILE.observed_angle_range == (3.292, 58.671)
  assert PROFILE.angles_deg == (0.0, 3.292, 8.783, 19.289, 35.669, 58.671)
  assert PROFILE.ratios == (15.8207, 15.8207, 15.6557, 15.5427, 15.1964, 14.7617)
  for angle, ratio in zip(PROFILE.angles_deg, PROFILE.ratios, strict=True):
    assert PROFILE.ratio_at(angle) == ratio
  assert CLARITY_RAW_STEER_RATIO.ratio_domain == 'raw-angle'
  assert CLARITY_RAW_STEER_RATIO.ratio_at(435.7) == pytest.approx(14.1656734608)


def test_curve_is_symmetric_continuous_positive_and_monotonic_in_angle_to_curvature():
  previous_curvature = -1
  for i in range(10001):
    angle = i / 10
    ratio = PROFILE.ratio_at(angle)
    assert 8 <= ratio <= 25
    assert ratio == PROFILE.ratio_at(-angle)
    curvature_proxy = angle / ratio
    assert curvature_proxy > previous_curvature
    previous_curvature = curvature_proxy
  for angle in PROFILE.angles_deg:
    assert abs(PROFILE.ratio_at(angle - 1e-6) - PROFILE.ratio_at(angle + 1e-6)) < 1e-6
  assert PROFILE.ratio_at(500) == PROFILE.ratio_at(58.671)
  assert PROFILE.ratio_at(math.inf) == PROFILE.ratios[-1]
  assert PROFILE.ratio_at(math.nan) == PROFILE.ratios[0]
  for lower, upper, r_lower, r_upper in zip(PROFILE.angles_deg, PROFILE.angles_deg[1:], PROFILE.ratios, PROFILE.ratios[1:], strict=False):
    assert PROFILE.ratio_at((lower + upper) / 2) == pytest.approx((r_lower + r_upper) / 2)


@pytest.mark.parametrize('fingerprint,firmware,brand', [
  ('HONDA_CIVIC', None, 'honda'), ('HONDA_CIVIC', b'39990-TBA-A030', 'honda'),
  ('HONDA_CIVIC', b'39990-TGG-A120', 'honda'), ('HONDA_CIVIC_BOSCH', b'39990-TEG-A010', 'honda'),
  ('HONDA_CIVIC', b'39990-TEG-A010', 'toyota'), ('LEXUS_ES_TSS2', b'39990-TEG-A010', 'toyota'),
])
def test_profile_does_not_leak_to_other_cars_or_eps(fingerprint, firmware, brand):
  CP = cp(fingerprint, firmware, brand)
  assert get_raw_steer_ratio_profile(CP) is None
  selection = resolve_steer_ratio_selection(CP, {'NrdrSteerRatioMode': 2})
  assert selection.effective_mode is None
  assert selection.ratio_at(80) == 15.38
  assert 'reported EPS' in selection.unavailable_reason


def test_profile_requires_unambiguous_reported_eps_and_accepts_normalized_format():
  assert get_raw_steer_ratio_profile(cp(firmware=b'39990,TEG,A010\0')) is PROFILE
  CP = cp()
  CP.carFw.append(SimpleNamespace(ecu='eps', fwVersion=b'unknown'))
  assert get_raw_steer_ratio_profile(CP) is None
  CP.carFw = [SimpleNamespace(ecu='engine', fwVersion=b'39990-TEG-A010')]
  assert get_raw_steer_ratio_profile(CP) is None


def test_availability_does_not_activate_curve_or_replace_saved_manual_values():
  values = {'NrdrSteerRatioMode': 0, 'NrdrSteerRatioManualCenter': 20.0, 'NrdrSteerRatioManualFinal': 13.75}
  before = values.copy()
  manual = resolve_steer_ratio_selection(cp(), values)
  assert values == before
  assert manual.effective_mode is SteerRatioMode.MANUAL
  assert manual.ratio_at(0) == 20
  assert manual.ratio_at(450) == 13.75
  assert stock_steer_ratio_selection(cp()).effective_mode is None
  selected = resolve_steer_ratio_selection(cp(), values | {'NrdrSteerRatioMode': 2})
  assert selected.effective_mode is SteerRatioMode.NRDR_RAW
  assert 'provisional' in selected.effective_label
  assert selected.firmware_vgr_selected is False
  assert selected.linearize_measured_angle(60) == 60
  assert selected.physicalize_desired_angle(60) == 60
  latch = SteerRatioModeLatch(manual)
  assert latch.update(selected, active=True) is selected
  assert latch.update(manual, active=True) is manual
  assert values == before


@pytest.mark.parametrize('changes', [
  {'angles_deg': (0, 1, 2, 3, 4, math.nan)}, {'ratio_domain': 'unknown'},
  {'observed_angle_range': None}, {'observed_angle_range': (0, 100)},
  {'ratios': (0, 1, 2, 3, 4, 5)},
  {'angles_deg': (0, 3, 8), 'ratios': (8, 8, 25), 'observed_angle_range': (3, 8)},
])
def test_profile_rejects_invalid_geometry_and_missing_uncertainty_metadata(changes):
  with pytest.raises(ValueError):
    replace(PROFILE, **changes)


def test_provisional_evidence_ships_with_profile():
  path = Path(__file__).resolve().parents[1] / 'features/lateral/CIVIC_TEG_PROVISIONAL_STEER_RATIO_EVIDENCE.md'
  evidence = ' '.join(path.read_text(encoding='utf-8').split())
  for text in ('15c8c34551eb6dd9d31e09a9959225dbe1c0e2dbdff5522e62dc1ac9daedec5a',
               '00000059--23041ba9e2', '0000005a--8cecadb216', '0000005b--b351e105bb',
               'not road-validated', '58.671', 'unmeasured', 'vehicle-model'):
    assert text in evidence


@pytest.mark.skipif(sys.platform == 'win32', reason='VehicleModel imports native CarParams bindings')
def test_real_vehicle_model_round_trips_draft_at_angles_speeds_and_stiffnesses():
  from opendbc.car.vehicle_model import VehicleModel

  CP = cp()
  CP.mass, CP.rotationalInertia = 1500, 2500
  CP.wheelbase, CP.centerToFront, CP.steerRatioRear = 2.7, 1.08, 0
  CP.tireStiffnessFront, CP.tireStiffnessRear = 180000, 200000
  selection = resolve_steer_ratio_selection(CP, {'NrdrSteerRatioMode': 2})
  vm = VehicleModel(CP)
  for stiffness in (0.7, 1.0, 1.3):
    vm.update_params(stiffness, CP.steerRatio)
    for speed in (0.0, 5.0, 15.0, 25.0, 33.0):
      for roll in (-0.04, 0, 0.04):
        for angle in (-450, -58.671, -8, 0, 8, 58.671, 450):
          curvature = selection.measured_curvature(vm, angle, speed, roll, angle_offset_deg=0.7)
          desired = selection.desired_angle_no_offset(vm, angle, speed, roll, curvature)
          assert math.isfinite(curvature)
          assert desired + 0.7 == pytest.approx(angle, abs=1e-8)
          assert vm.sR == PROFILE.ratio_at(angle)
          assert selection.curvature_deadzone(vm, angle, 0.1, speed) > 0
          assert selection.measured_curvature_rate(vm, angle, 2.0, speed, 0.01) < 0
