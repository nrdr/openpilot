import pytest

from openpilot.sunnypilot.nrdr.phase_detector import PHASE_SWITCH_MIN_SPEED, phase_with_latch


def test_phase_can_initialize_but_not_switch_at_or_below_half_mph():
  phase, direction = phase_with_latch(10.0, 0.2, 0.0, 0.0)
  assert phase == pytest.approx(2.0)
  assert direction == 1.0

  phase, direction = phase_with_latch(10.0, -0.2, PHASE_SWITCH_MIN_SPEED, direction)
  assert phase == pytest.approx(2.0)
  assert direction == 1.0


def test_phase_switches_above_half_mph():
  phase, direction = phase_with_latch(10.0, -0.2, PHASE_SWITCH_MIN_SPEED + 1e-6, 1.0)
  assert phase == pytest.approx(-2.0)
  assert direction == -1.0


def test_zero_phase_preserves_direction_without_applying_phase_gain():
  phase, direction = phase_with_latch(10.0, 0.0, 0.0, -1.0)
  assert phase == 0.0
  assert direction == -1.0
