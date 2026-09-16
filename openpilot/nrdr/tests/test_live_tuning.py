from types import MappingProxyType

import pytest

from openpilot.nrdr.features.lateral.live_tuning import LiveTorqueTransition
from openpilot.nrdr.params.snapshots import ParamSnapshot


def snapshot(generation=1, **changes):
  return ParamSnapshot(generation, MappingProxyType({"NrdrInterpolatedTorqueShare": 10, **changes}))


def test_unchanged_settings_pass_normal_steering_through_exactly():
  transition = LiveTorqueTransition()
  for value in (0.0, 0.8, -0.7, 0.3, -1.0, 1.0):
    assert transition.update(value, snapshot(), True, False, 0.01) == value
  assert transition.update(0.65, snapshot(2), True, False, 0.01) == 0.65


@pytest.mark.parametrize("changed", (
  {"NrdrInterpolatedTorqueShare": 5}, {"NrdrSteerRatioMode": 3},
  {"NrdrSteerRatioManualCenter": 17.0}, {"LatPScaleHighway": 110},
  {"LaneCenteringStrength": 0.3}, {"NrdrLearnAngleOffset": False},
  {"NrdrSteerRatioHybrid": True}, {"NrdrSteerRatioSourceB": 3}, {"NrdrSteerRatioBlendStart": 25.0},
  {"NrdrInterpolatedTorqueFrictionHighway": 0.3},
))
def test_active_edit_is_bumpless_then_converges_without_disengagement(changed):
  transition = LiveTorqueTransition()
  transition.update(0.3, snapshot(), True, False, 0.01)
  updated = snapshot(2, **changed)
  assert transition.update(0.7, updated, True, False, 0.01) == pytest.approx(0.3)
  values = [transition.update(0.7, updated, True, False, 0.01) for _ in range(100)]
  assert values[-1] == pytest.approx(0.7)
  assert all(0.3 <= value <= 0.7 for value in values)
  assert max(b - a for a, b in zip([0.3, *values[:-1]], values, strict=True)) <= 0.004001


@pytest.mark.parametrize("active,pressed", ((False, False), (True, True)))
def test_disengagement_and_driver_override_clear_transition_immediately(active, pressed):
  transition = LiveTorqueTransition()
  transition.update(0.3, snapshot(), True, False, 0.01)
  updated = snapshot(2, NrdrInterpolatedTorqueShare=5)
  transition.update(0.7, updated, True, False, 0.01)
  assert transition.update(0.0, updated, active, pressed, 0.01) == 0.0
  assert transition.remaining == 0.0
  assert transition.update(0.1, updated, True, False, 0.01) == 0.1


def test_repeated_edits_and_nonfinite_outputs_do_not_leave_stale_bias():
  transition = LiveTorqueTransition()
  transition.update(0.3, snapshot(), True, False, 0.01)
  first = snapshot(2, NrdrInterpolatedTorqueShare=5)
  transition.update(0.7, first, True, False, 0.01)
  second = snapshot(3, NrdrInterpolatedTorqueShare=15)
  assert transition.update(-0.5, second, True, False, 0.01) == pytest.approx(0.3)
  transition.update(float("nan"), second, True, False, 0.01)
  assert transition.remaining == 0.0
  assert transition.update(-0.2, second, True, False, 0.01) == -0.2


def test_longitudinal_and_maintenance_changes_do_not_trigger_steering_transition():
  transition = LiveTorqueTransition()
  transition.update(0.3, snapshot(), True, False, 0.01)
  updated = snapshot(2, LongPidTuneScaleStandard=120, NrdrTuneLearnerReset=True)
  assert transition.update(-0.4, updated, True, False, 0.01) == -0.4
