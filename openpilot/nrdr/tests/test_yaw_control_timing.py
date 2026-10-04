"""Yaw command timing stays separate from shared live/manual model delay."""
import ast
import math
from pathlib import Path

import pytest

from openpilot.nrdr.features.lateral import yaw_control_timing as timing
from openpilot.nrdr.params.snapshots import ParamSnapshot
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.sunnypilot.livedelay.helpers import get_lat_delay


def test_reference_schedule_is_the_refit_table():
  assert [timing.clarity_lateral_delay(v) for v in (0., 3.5, 7., 12., 20., 30., 40.)] == \
    pytest.approx([.15, .15, .08, .10, .20, .30, .30])


@pytest.mark.parametrize("settings, speed, expected", [
  (None, 0., .145), (None, 12.5, .085), (None, 30., .025),
  (ParamSnapshot(1, {}), 5., .145),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": .2, "NrdrYawCommandDelayHigh": .05}), 12.5, .125),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": 9., "NrdrYawCommandDelayHigh": -1.}), 5., timing.MAX_COMMAND_DELAY),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": 9., "NrdrYawCommandDelayHigh": -1.}), 20., 0.),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": math.nan, "NrdrYawCommandDelayHigh": b"x"}), 5., .145),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": math.nan, "NrdrYawCommandDelayHigh": b"x"}), 20., .025),
])
def test_command_delay_defaults_fade_and_bounds(settings, speed, expected):
  assert timing.command_delay(settings, speed) == pytest.approx(expected)


def test_delay_line_interpolates_between_samples_and_never_runs_out():
  line = timing.CommandDelay(.01)
  assert line.update(1., .025) == 1.
  for value in range(2, 40):
    out = line.update(float(value), .025)
  assert out == pytest.approx(39. - 2.5)
  assert line.update(40., 0.) == 40.
  assert len(line.buf) == line.buf.maxlen == 32


@pytest.mark.parametrize("controller", [0, 1])
@pytest.mark.parametrize("legacy_schedule", [False, True])
@pytest.mark.parametrize("live", [False, True])
def test_delay_selection_is_independent_of_controller_and_retired_override(controller, legacy_schedule, live):
  values = {"NrdrLateralController": controller, "NrdrYawDelaySchedule": legacy_schedule,
            "LagdToggle": live, "LagdToggleDelay": .3}
  settings = ParamSnapshot(1, values)
  assert get_lat_delay(settings, .8, .2) == pytest.approx(.8 if live else .5)
  assert settings.values == values


def test_manual_delay_edit_changes_total_delay_without_touching_command_delay():
  values = {"NrdrLateralController": 1, "NrdrYawDelaySchedule": True,
            "LagdToggle": False, "LagdToggleDelay": .4}
  before = ParamSnapshot(1, values)
  after = ParamSnapshot(2, {**values, "LagdToggleDelay": .3})
  assert get_lat_delay(before, .8, .2) - get_lat_delay(after, .8, .2) == pytest.approx(.1)
  for speed in (5., 12.5, 30.):
    assert timing.command_delay(before, speed) == timing.command_delay(after, speed)


def test_live_toggle_preserves_manual_value_for_return_to_manual():
  manual = ParamSnapshot(1, {"NrdrLateralController": 1, "LagdToggle": False, "LagdToggleDelay": .3})
  live = ParamSnapshot(2, {**manual.values, "LagdToggle": True})
  assert get_lat_delay(manual, .8, .2) == pytest.approx(.5)
  assert get_lat_delay(live, .8, .2) == pytest.approx(.8)
  assert live.get("LagdToggleDelay") == manual.get("LagdToggleDelay") == .3
  assert get_lat_delay(manual, .8, .2) == pytest.approx(.5)


def test_retired_override_cannot_be_written():
  assert not tuning_write_allowed(ParamSnapshot(1, {}), "NrdrYawDelaySchedule")


def test_model_and_controls_runtimes_keep_shared_delay_wiring():
  root = Path(__file__).resolve().parents[2]
  for relative in ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"):
    source = (root / relative).read_text()
    assert "model_lateral_delay_schedule" not in source
    assert 'if sm.updated["lateralDelay"]:\n      model.lat_delay = get_lat_delay(params,' in source
  source = (root / "selfdrive/controls/controlsd.py").read_text()
  assert "get_lat_delay(self.nrdr_lateral_snapshot," in source
  assert "LaC.lateral_delay" not in source
  assert "LaC.measured_curvature" not in source


@pytest.mark.parametrize("live", [False, True])
@pytest.mark.parametrize("saved", [None, .05, .31, .4, 1., math.nan])
@pytest.mark.parametrize("actuator", [0., .2, .5])
def test_firmware_delay_is_fixed_total_and_preserves_pif_settings(live, saved, actuator):
  values = {"LagdToggle": live, "LagdToggleDelay": saved}
  snapshot = ParamSnapshot(1, values)
  for learned in (0., .15, .8, math.nan):
    assert get_lat_delay(snapshot, learned, actuator, firmware_controller=True) == .30
  assert snapshot.values == values


def test_model_and_control_fixed_delay_gates_match():
  root = Path(__file__).resolve().parents[2]
  for relative in ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"):
    source = (root / relative).read_text()
    assert "firmware_controller = firmware_controller_for_model(params, CP)" in source
    assert source.count("firmware_controller=firmware_controller") == 2
  source = (root / "selfdrive/controls/controlsd.py").read_text()
  assert 'firmware_controller=getattr(self.LaC, "uses_firmware_delay", False)' in source


@pytest.mark.parametrize("relative", ["selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"])
@pytest.mark.parametrize("smooth", [0., .1, .3])
def test_firmware_total_is_not_extended_by_model_specific_smoothing(relative, smooth):
  from types import SimpleNamespace as NS
  root = Path(__file__).resolve().parents[2]
  tree = ast.parse((root / relative).read_text())
  assignment, = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "lat_delay" for target in node.targets)]
  expr = compile(ast.Expression(assignment.value), relative, "eval")
  context = {"model": NS(lat_delay=.30, LAT_SMOOTH_SECONDS=smooth), "LAT_SMOOTH_SECONDS": smooth}
  assert eval(expr, {**context, "firmware_controller": True}) == .30
  assert eval(expr, {**context, "firmware_controller": False}) == pytest.approx(.30 + smooth)


def test_model_firmware_selection_never_reads_honda_data_for_another_vehicle():
  from types import SimpleNamespace as NS
  from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_for_model
  class OtherCarParams:
    def get(self, *args, **kwargs):
      raise AssertionError("Other cars must not read Honda controller settings or CP_SP")
  for cp in (None, NS(brand="toyota", carFingerprint="LEXUS_ES_TSS2"), NS(brand="honda", carFingerprint="HONDA_CIVIC")):
    assert not firmware_controller_for_model(OtherCarParams(), cp)


def test_admitted_firmware_selection_matches_runtime_and_stale_selection_falls_back():
  from types import SimpleNamespace as NS
  from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
  from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_selected
  cp = NS(brand="honda", carFingerprint="HONDA_CLARITY", lateralTuning=NS(which=lambda: "pid"),
          carFw=[NS(ecu="eps", fwVersion=b"39990-TRW-A020\x00")])
  sp = NS(flags=HondaFlagsSP.EPS_MODIFIED.value)
  for selected in (1, "1", b"1"):
    assert firmware_controller_selected({"NrdrLateralController": selected}, cp, sp)
    assert not firmware_controller_selected({"NrdrLateralController": selected}, cp, NS(flags=0))
  assert not firmware_controller_selected({"NrdrLateralController": 0}, cp, sp)
