import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.features.longitudinal.longitudinal_mpc import apply_standstill_gap
from openpilot.nrdr.params.snapshots import PLANNER_GROUPS
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY


@pytest.mark.parametrize("present", [(True, False), (False, True), (True, True), (False, False)])
@pytest.mark.parametrize("extra", [0.0, 0.25, 2.0, 5.0, 50.0])
def test_distance_floor_survives_entire_horizon_and_leaves_originals_intact(present, extra):
  # Includes a stopped lead: a constant distance does not erode while creeping.
  raw = np.column_stack([np.full(13, 8.0), np.linspace(12.0, 30.0, 13)])
  before = raw.copy()
  radar = NS(leadOne=NS(present=present[0]), leadTwo=NS(present=present[1]))
  actual = apply_standstill_gap(raw, radar, extra)
  expected = before - np.array(present) * min(extra, 5.0)
  np.testing.assert_array_equal(actual, expected)
  np.testing.assert_array_equal(raw, before)
  assert np.all(actual <= before)  # Never reduces clearance or weakens a constraint.


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), "bad", None, True])
def test_invalid_gap_is_exact_baseline(bad):
  raw = np.ones((13, 2))
  assert apply_standstill_gap(raw, NS(), bad) is raw


def test_zero_default_and_live_snapshot_membership():
  assert float(PARAM_SPECS_BY_KEY["NrdrStandstillGapExtra"].default) == 0.0
  assert "NrdrStandstillGapExtra" in {key for group in PLANNER_GROUPS for key in group.keys}


def test_adjustments_wait_for_disengagement():
  path = Path(__file__).resolve().parents[3] / "openpilot/nrdr/features/longitudinal/longitudinal_planner.py"
  cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "NrdrLongitudinalPlanner")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "stopped_gap")
  env = {}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), env)
  planner = NS(standstill_gap_requested=2.0, standstill_gap_extra=0.0)
  assert env["stopped_gap"](planner, True) == 2.0
  planner.standstill_gap_requested = 0.0
  for _ in range(100):
    assert env["stopped_gap"](planner, False) == 2.0
  assert env["stopped_gap"](planner, True) == 0.0
