"""Exercise the custom model's output decoder without starting the model daemon."""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan


@pytest.fixture
def decoder():
  path = Path(__file__).resolve().parents[2] / 'sunnypilot/modeld_v2/modeld.py'
  cls = next(n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n, ast.ClassDef) and n.name == 'ModelState')
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'get_action_from_model')
  plan_curvature = Mock(return_value=-0.03125)
  namespace = {'Plan': Plan, 'log': NS(ModelDataV2=NS(Action=NS)), 'smooth_value': lambda val, prev, tau: val,
               'get_accel_from_plan': Mock(return_value=0.25), 'get_curvature_from_output': plan_curvature}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), namespace)
  state = NS(generation=None, LONG_SMOOTH_SECONDS=0, constants=ModelConstants, mlsim=False)

  def decode(output, speed):
    return namespace['get_action_from_model'](state, output, NS(desiredAcceleration=0), 0.3, 0.4, speed)

  return decode, plan_curvature


@pytest.mark.parametrize('speed,lateral,expected', [
  (0.0, 0.5, 0.08), (1.0, -0.5, -0.08), (2.49, 0.5, 0.08), (2.5, 0.5, 0.08), (5.0, 0.5, 0.02),
])
def test_action_curvature(decoder, speed, lateral, expected):
  decode, plan_curvature = decoder
  action = decode({'action': np.array([[lateral, -0.25]])}, speed)
  assert action.desiredCurvature == pytest.approx(expected)
  assert action.desiredAcceleration == -0.25
  plan_curvature.assert_not_called()


def test_plan_decoder_still_uses_actual_speed(decoder):
  decode, plan_curvature = decoder
  plan = np.zeros((ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH))
  output = {'plan': [plan]}
  action = decode(output, 1.0)
  plan_curvature.assert_called_once_with(output, plan, 1.0, 0.3, False)
  assert action.desiredCurvature == -0.03125
  assert action.desiredAcceleration == 0.25
