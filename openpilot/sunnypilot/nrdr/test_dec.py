from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.nrdr.dec import enforce_mode_dwell, slow_down_threshold


@pytest.mark.parametrize(
  "duration, emergency, current, requested, blocked",
  [
    (0, False, "acc", "blended", True),
    (0, True, "blended", "blended", False),
    (0, True, "blended", "acc", True),
    (10, False, "acc", "blended", False),
  ],
)
def test_enforce_mode_dwell(duration, emergency, current, requested, blocked):
  manager = SimpleNamespace(
    emergency_override=emergency,
    current_mode=current,
    mode_duration=duration,
    min_mode_duration=10,
  )
  assert enforce_mode_dwell(manager, requested) is blocked


@pytest.mark.parametrize(
  "active, enter_scale, exit_scale, expected",
  [
    (False, 1.0, 0.625, 0.6),
    (True, 1.0, 0.625, 0.375),
    (False, 0.8, 0.5, 0.48),
    (True, 0.8, 0.5, 0.3),
  ],
)
def test_slow_down_threshold(active, enter_scale, exit_scale, expected):
  assert slow_down_threshold(0.6, active, enter_scale, exit_scale) == pytest.approx(expected)
