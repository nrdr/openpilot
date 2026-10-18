"""Pin the plan extractor's horizon contract without importing device services."""
import ast
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture(scope="module")
def plan_curvature():
  source = Path(__file__).resolve().parents[2] / "selfdrive/controls/lib/drive_helpers.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  constants = {"MIN_SPEED", "MIN_STABLE_DELAY"}
  functions = {"curv_from_psis", "get_curvature_from_plan"}
  body = [node for node in tree.body
          if (isinstance(node, ast.FunctionDef) and node.name in functions) or
          (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets))]
  assert len(body) == len(constants) + len(functions)
  namespace = {"np": np}
  exec(compile(ast.Module(body=body, type_ignores=[]), str(source), "exec"), namespace)
  assert namespace["MIN_STABLE_DELAY"] == 0.3
  return namespace["get_curvature_from_plan"]


def example_plan():
  t = 10.0 * (np.arange(33) / 32.0) ** 2
  return 0.12 * t + 0.04 * t**2 + 0.003 * t**3, 0.12 + 0.08 * t + 0.009 * t**2, t


@pytest.mark.parametrize("horizon", (0.025, 0.075, 0.10, 0.155, 0.22, 0.295, 0.3))
def test_subfloor_plan_extraction_is_the_same_as_point_three(plan_curvature, horizon):
  yaws, rates, times = example_plan()
  assert plan_curvature(yaws, rates, times, 12.0, horizon) == pytest.approx(
    plan_curvature(yaws, rates, times, 12.0, 0.3), abs=1e-14)


@pytest.mark.parametrize("horizon", (0.31, 0.375, 0.435, 0.6))
def test_larger_horizons_are_not_a_fixed_point_three_override(plan_curvature, horizon):
  yaws, rates, times = example_plan()
  result = plan_curvature(yaws, rates, times, 12.0, horizon)
  expected = 2.0 * np.interp(horizon, times, yaws) / (12.0 * horizon) - rates[0] / 12.0
  assert result == pytest.approx(expected, abs=1e-14)
  assert result > plan_curvature(yaws, rates, times, 12.0, 0.3)
