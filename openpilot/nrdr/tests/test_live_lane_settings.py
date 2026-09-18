"""Exercise live lane-setting decoding without starting controls or accessing Params."""
import math
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt


def decode(values, captured=None):
  controls = SimpleNamespace(nrdr_live_params=SimpleNamespace(snapshot=values))
  ControlsExt.update_lane_centering_params(controls, captured)
  return controls


@pytest.mark.parametrize("value", [None, "bad", "nan", "inf", "-inf", "0", "11", "101", "12.5"])
def test_invalid_live_minimum_speed_keeps_50_mph_fallback(value):
  assert decode({"LaneCenteringMinSpeed": value}).lane_centering_min_speed_mph == 50.0


@pytest.mark.parametrize("value", [12, 50, 100, b"65"])
def test_valid_live_minimum_speed_is_preserved(value):
  assert decode({"LaneCenteringMinSpeed": value}).lane_centering_min_speed_mph == float(value)


@pytest.mark.parametrize("key,attribute", [
  ("LaneCenterOffset", "lane_center_offset"),
  ("LaneCenteringE2EAuthority", "lane_centering_e2e_authority"),
])
@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_nonfinite_inputs_reach_existing_controller_rejection(key, attribute, value):
  assert not math.isfinite(getattr(decode({key: value}), attribute))


def test_defaults_and_captured_frame_override_background_publication():
  defaults = decode({})
  assert defaults.lane_center_offset == 0.0
  assert defaults.lane_centering_e2e_authority == 1.0
  assert defaults.lane_centering_strength == 0.3
  assert not defaults.lane_centering_enabled
  assert defaults.lane_centering_pause_on_signal
  controls = decode({"LaneCenteringStrength": "1.0"}, {"LaneCenteringStrength": "0.3"})
  assert controls.lane_centering_strength == 0.3
