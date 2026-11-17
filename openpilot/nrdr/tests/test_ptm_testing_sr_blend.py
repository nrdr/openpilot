"""Temporary Clarity 250-degree model blend; production geometry stays unchanged."""
from types import SimpleNamespace as NS
import sys

import numpy as np
import pytest

from openpilot.nrdr.features.lateral import lane_change_tuning
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioModeLatch, resolve_steer_ratio_selection


def car(fingerprint="HONDA_CLARITY", firmware=b"39990-TRW-A020"):
  return NS(brand="honda", carFingerprint=fingerprint, steerRatio=16.5,
            carFw=[NS(ecu="eps", fwVersion=firmware)])


@pytest.fixture
def eligible(monkeypatch):
  monkeypatch.setattr(lane_change_tuning, "active_model_supports_optimized_lane_changes", lambda: True)


def selection(cp=None, testing=False, **settings):
  return resolve_steer_ratio_selection(cp or car(),
    {"NrdrSteerRatioMode": 3, "NrdrSteerRatioModelBlend": True, **settings},
    ptm_baseline=True, ptm_testing=testing)


def test_testing_preserves_center_and_reaches_endpoint_at_250(eligible):
  normal, candidate = selection(), selection(testing=True)
  assert normal.model_blend.outer == pytest.approx(433.8)
  assert candidate.model_blend.outer == 250.
  assert candidate.model_blend.center == normal.model_blend.center
  assert candidate.model_blend.final == normal.model_blend.final == 12.72
  assert candidate.rack_map is normal.rack_map
  for a, weight in ((.001, .001 / 250), (125., .5), (250., 1.), (400., 1.)):
    expected = candidate.model_blend.center * (1 - weight) + 12.72 * weight
    assert candidate.cp_ratio * a / candidate.linearize_measured_angle(a) == pytest.approx(expected)
  # This is the analytic inverse, not a ratio lookup at the measured wheel angle.
  for measured in (-300., 0., 300.):
    for curvature in (-.025, -.003, .003, .025):
      assert candidate.desired_angle_no_offset(NS(sR=16.5), measured, 10., .02, curvature) == (
        candidate.desired_angle_no_offset(NS(sR=16.5), 0., 10., .02, curvature))


def test_round_trip_symmetry_and_monotonicity(eligible):
  candidate = selection(testing=True)
  angles = np.unique(np.r_[np.linspace(-500., 500., 1001), -250.0001, -249.9999, 249.9999, 250.0001])
  mapped = [candidate.linearize_measured_angle(a) for a in angles]
  assert np.all(np.diff(mapped) > 0)
  for a, linear in zip(angles, mapped, strict=True):
    assert candidate.linearize_measured_angle(-a) == pytest.approx(-linear)
    assert candidate.physicalize_desired_angle(linear) == pytest.approx(a, abs=1e-8)
    for speed, roll in ((0., 0.), (10., .03), (30., -.02)):
      vm = NS(sR=16.5)
      curvature = candidate.measured_curvature(vm, a, speed, roll)
      assert candidate.desired_angle_no_offset(vm, 0., speed, roll, curvature) == pytest.approx(a, abs=1e-6)


@pytest.mark.parametrize("fingerprint,firmware", [
  ("HONDA_CIVIC", b"39990-TEG-A010"), ("HONDA_ODYSSEY", b"39990-THR-A020"),
  ("HONDA_CLARITY", b"unknown"),
])
def test_other_cars_and_unknown_eps_unchanged(eligible, fingerprint, firmware):
  cp = car(fingerprint, firmware)
  assert selection(cp, testing=True) == selection(cp)


@pytest.mark.parametrize("mode,toggle,model_eligible", [(1, True, True), (3, False, True), (3, True, False)])
def test_existing_admission_gates_remain(monkeypatch, mode, toggle, model_eligible):
  monkeypatch.setattr(lane_change_tuning, "active_model_supports_optimized_lane_changes", lambda: model_eligible)
  options = {"NrdrSteerRatioMode": mode, "NrdrSteerRatioModelBlend": toggle}
  assert selection(testing=True, **options) == selection(**options)
  assert selection(testing=True, **options).model_blend is None


@pytest.mark.parametrize("testing", [False, True])
@pytest.mark.skipif(sys.platform == "win32", reason="native control-hook dependencies")
def test_control_hook_shares_testing_geometry_with_measured_and_desired_paths(eligible, testing):
  from openpilot.nrdr.hooks.controlsd import vehicle_model_state
  cp = car()
  snapshot = {"NrdrSteerRatioMode": 3, "NrdrSteerRatioModelBlend": True}
  accepted = []
  lac = NS(firmware_profile=object(), set_steer_ratio_selection=accepted.append)
  if testing:
    lac.ptm_testing = True
  controls = NS(CP=cp, LaC=lac, nrdr_live_params=NS(snapshot=snapshot),
                sm=NS(valid={"vehicleParameters": True}), steer_ratio_latch=SteerRatioModeLatch(selection(cp)))
  live = NS(steerRatio=16.5, steerRatioValid=True, stiffnessFactor=1., angleOffsetDeg=0.)
  result = vehicle_model_state(controls, live, NS(steeringAngleDeg=125.), False)
  expected = selection(cp, testing=testing)
  assert accepted[-1] == expected == controls.steer_ratio_latch.selection
  assert result[3] == expected.linearize_measured_angle(125.)
  assert expected.model_blend.outer == pytest.approx(250. if testing else 433.8)
