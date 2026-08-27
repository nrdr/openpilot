import math

from openpilot.nrdr.tools.steer_ratio.by_angle import CarStateSample, angle_bin_start, effective_ratio, nearest_state_sample


def state(timestamp: float, angle: float = 10.0, offset: float = 0.0) -> CarStateSample:
  return CarStateSample(timestamp, 15.0, angle, 0.0, False, offset, True)


def test_effective_ratio_removes_angle_offset():
  wheelbase = 2.75
  expected_ratio = 18.0
  corrected_angle_deg = 20.0
  road_angle = math.radians(corrected_angle_deg) / expected_ratio
  yaw_rate = 15.0 * math.tan(road_angle) / wheelbase

  assert math.isclose(effective_ratio(22.0, 2.0, yaw_rate, 15.0, wheelbase), expected_ratio, rel_tol=1e-9)


def test_effective_ratio_rejects_invalid_geometry():
  assert effective_ratio(20.0, 0.0, 0.1, 0.0, 2.75) is None
  assert effective_ratio(20.0, 0.0, 0.1, 15.0, 0.0) is None
  assert effective_ratio(20.0, 0.0, 0.0, 15.0, 2.75) is None


def test_nearest_state_sample_supports_delay_alignment():
  samples = [state(10.00), state(10.05), state(10.10)]
  assert nearest_state_sample(samples, 10.06, 0.02) == samples[1]
  assert nearest_state_sample(samples, 9.90, 0.05) is None


def test_fractional_angle_bins_do_not_collapse():
  assert angle_bin_start(7.49, 2.5) == 5.0
  assert angle_bin_start(-7.50, 2.5) == 7.5
