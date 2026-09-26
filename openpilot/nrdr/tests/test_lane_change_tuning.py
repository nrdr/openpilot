"""Deterministic request-shaping checks; these are not road validation."""
import math
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.lateral.lane_change_tuning import LaneChangeEntry, bounded_setting, shape_lane_change_curvature
from openpilot.nrdr.features.lateral.steer_ratio_tuning import resolve_steer_ratio_selection
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, MODEL_GROUPS, LiveParams
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY
from openpilot.nrdr.params.ui_metadata import LANE_CHANGE_UI_METADATA, validate_ui_metadata
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
from openpilot.nrdr.ui.sunnylink_schema import sunnylink_fields_for_key


def settings(reduction=3.0, duration=1.0):
  return {"NrdrLaneChangeEntrySrReduction": reduction, "NrdrLaneChangeEntryReturnTime": duration}


def tick(entry, state=2, direction=1, **kwargs):
  args = {"active": True, "valid": True, "state": state, "direction": direction,
          "driver_override": False, "settings": settings(), "dt": 0.01}
  args.update(kwargs)
  return entry.update(**args)


@pytest.mark.parametrize("direction", (1, 2))
def test_envelope_has_smooth_entry_bounded_peak_return_and_no_retrigger(direction):
  entry = LaneChangeEntry()
  assert tick(entry, state=1, direction=direction) == 0
  values = [tick(entry, direction=direction) for _ in range(200)]
  assert values[0] < 0.05
  assert max(values) == pytest.approx(3.0)
  assert all(0 <= v <= 3 for v in values)
  assert values[115:] == [0.0] * len(values[115:])
  assert all(a <= b + 1e-10 for a, b in zip(values[:14], values[1:15], strict=True))
  assert all(a >= b - 1e-10 for a, b in zip(values[14:114], values[15:115], strict=True))
  assert tick(entry, state=1, direction=direction) == 0
  assert tick(entry, direction=direction) > 0


@pytest.mark.parametrize("state", (0, 1, 3))
def test_waiting_off_finishing_and_disabled_never_initiate(state):
  assert all(tick(LaneChangeEntry(), state=state) == 0 for _ in range(10))
  assert tick(LaneChangeEntry(), settings=settings(0)) == 0


@pytest.mark.parametrize("change", ({"state": 0}, {"state": 1}, {"state": 3}, {"direction": 2},
                                    {"driver_override": True}, {"settings": settings(0)}))
def test_cancel_returns_without_step_or_retrigger(change):
  entry = LaneChangeEntry()
  for _ in range(15):
    tick(entry)
  before = entry.applied
  values = [tick(entry, **change) for _ in range(25)]
  assert 0 < values[0] < before
  assert values[-1] == 0
  assert all(a >= b for a, b in zip(values, values[1:], strict=False))


@pytest.mark.parametrize("change", ({"active": False}, {"valid": False}))
def test_invalid_data_or_disengagement_clears_and_does_not_restart_mid_maneuver(change):
  entry = LaneChangeEntry()
  for _ in range(15):
    tick(entry)
  assert tick(entry, **change) == 0
  assert tick(entry) == 0


def test_driver_nudge_does_not_start_a_delayed_entry_after_release():
  entry = LaneChangeEntry()
  assert tick(entry, driver_override=True) == 0
  assert tick(entry, driver_override=False) == 0


def test_edits_are_captured_next_lane_change_except_zero_cancels():
  entry = LaneChangeEntry()
  tick(entry)
  for _ in range(14):
    tick(entry, settings=settings(5, 3))
  assert entry.applied == pytest.approx(3)
  assert entry.return_seconds == 1
  for _ in range(25):
    tick(entry, state=1, settings=settings(5, 3))
  tick(entry, settings=settings(5, 3))
  assert entry.reduction == 5 and entry.return_seconds == 3


@pytest.mark.parametrize("bad", (None, "bad", math.nan, math.inf, -math.inf))
def test_invalid_settings_fall_back(bad):
  assert bounded_setting({"x": bad}, "x", 1, 0, 5) == 1


class VehicleModel:
  """Invertible test double with additive roll compensation."""
  def __init__(self, ratio=16.5):
    self.sR = ratio

  def get_steer_from_curvature(self, curvature, speed, roll):
    return (curvature + roll * 0.01) * 2.75 * self.sR

  def calc_curvature(self, angle, speed, roll):
    return angle / (2.75 * self.sR) - roll * 0.01


def selection(mode, hybrid=False, b=3):
  cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CLARITY", steerRatio=16.5,
                       carFw=[SimpleNamespace(ecu="eps", fwVersion=b"39990-TRW-A020")])
  return resolve_steer_ratio_selection(cp, {
    "NrdrSteerRatioMode": mode, "NrdrSteerRatioManualCenter": 16.5, "NrdrSteerRatioManualFinal": 12.72,
    "NrdrSteerRatioHybrid": hybrid, "NrdrSteerRatioSourceB": b, "NrdrSteerRatioBlendStart": 25,
  }, 19.0)


@pytest.mark.parametrize("mode,hybrid,b", [(i, False, 3) for i in range(4)] + [(2, True, 3), (0, True, 0), (1, True, 3)])
@pytest.mark.parametrize("roll", (-0.08, 0.0, 0.08))
@pytest.mark.parametrize("angle", (-100, -30, -27.5, -20, 0, 20, 27.5, 30, 100))
def test_all_sources_and_hybrid_use_current_mapping_without_changing_feedback(mode, hybrid, b, roll, angle):
  selected = selection(mode, hybrid, b)
  assert selected.available
  vm = VehicleModel(19.0 if mode == 1 and not hybrid else 16.5)
  before = selected.measured_curvature(vm, angle, 25.0, roll)
  prior_ratio = vm.sR
  for curvature in (-0.005, -0.001, 0.0, 0.001, 0.005):
    assert shape_lane_change_curvature(selected, vm, angle, 25.0, roll, curvature, 0) == curvature
    shaped = shape_lane_change_curvature(selected, vm, angle, 25.0, roll, curvature, 3)
    assert math.isfinite(shaped)
    assert min(0, curvature) <= shaped <= max(0, curvature)
    if curvature:
      assert abs(shaped) < abs(curvature)
    assert vm.sR == prior_ratio
    assert selected.measured_curvature(vm, angle, 25.0, roll) == pytest.approx(before)


def test_comma_uses_actual_held_ratio_not_platform_default():
  selected = selection(1)
  vm = VehicleModel(21)
  assert shape_lane_change_curvature(selected, vm, 0, 25, 0, 0.01, 3) == pytest.approx(0.01 * 18 / 21)
  assert vm.sR == 21


def test_ratio_floor_and_disabled_path_preserve_request():
  selected = selection(0)
  selected = replace(selected, manual_center=8, manual_final=8)
  assert shape_lane_change_curvature(selected, VehicleModel(), 20, 25, 0, 0.01, 5) == 0.01


def test_zero_does_not_touch_geometry():
  assert shape_lane_change_curvature(None, None, 0, 25, 0, 0.01, 0) == 0.01


def test_ui_metadata_and_snapshots_are_complete():
  assert not validate_ui_metadata()
  controls = {key for group in CONTROL_GROUPS for key in group.keys}
  model = {key for group in MODEL_GROUPS for key in group.keys}
  assert len(LANE_CHANGE_UI_METADATA) == 5
  for metadata in LANE_CHANGE_UI_METADATA:
    key = metadata.key.value
    assert key in controls | model
    native = get_native_option_spec(key)
    remote = sunnylink_fields_for_key(key)
    assert native.description == remote["details"]
    assert remote["title"].startswith("NRDR ")
    assert "reboot" in native.description or "refresh" in native.description
  assert PARAM_SPECS_BY_KEY["NrdrLaneChangeEntrySrReduction"].default == "0.0"


def test_background_snapshot_propagates_entry_edits_without_engagement_or_reboot():
  class Params:
    def __init__(self):
      self.values = settings(0)

    def get(self, key, **kwargs):
      return self.values.get(key)

  params = Params()
  live = LiveParams(CONTROL_GROUPS, params=params, start_worker=False)
  params.values = settings(3)
  for _ in CONTROL_GROUPS:
    live.poll_once()
  entry = LaneChangeEntry()
  assert tick(entry, settings=live.snapshot) > 0
  assert entry.reduction == 3


def test_shaping_is_before_curvature_limit_and_has_vehicle_gate():
  root = Path(__file__).resolve().parents[3]
  controlsd = (root / "openpilot/selfdrive/controls/controlsd.py").read_text()
  assert controlsd.index("new_desired_curvature = lane_change_request(") < controlsd.index("self.desired_curvature, curvature_limited = clip_curvature(")
  hook = (root / "openpilot/nrdr/hooks/controlsd.py").read_text()
  assert 'controls.CP.brand == "honda"' in hook
  assert "controls.sm.all_checks(['modelV2'])" in hook
