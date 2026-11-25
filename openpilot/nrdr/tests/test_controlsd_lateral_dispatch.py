"""Exercise the constructor and frame dispatch used by controlsd without starting device services."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
from opendbc.car.structs import car


@pytest.fixture(scope="module")
def dispatch():
  source = Path(__file__).resolve().parents[2] / "selfdrive/controls/controlsd.py"
  cls = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "Controls")
  init, frame = (next(f for f in cls.body if isinstance(f, ast.FunctionDef) and f.name == name).body
                 for name in ("__init__", "state_control"))
  start = next(i for i, n in enumerate(init) if isinstance(n, ast.AnnAssign) and ast.unparse(n.target) == "self.LaC")
  end = next(i for i, n in enumerate(init) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "ptm_controller")
  curv, plan = (next(i for i, n in enumerate(frame) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == name)
                for name in ("self.curvature", "long_plan"))
  return [compile(ast.Module(part, []), str(source), "exec") for part in (init[start:end], frame[curv + 1:plan])]


@pytest.mark.parametrize("actuation,tune", [(a, t) for a in ("angle", "curvature", "torque") for t in ("pid", "torque")])
def test_controller_selection_and_first_frame(dispatch, actuation, tune):
  # Angle/curvature have neither the PID hook nor the torque extension.
  geometric = object()
  selected = Mock()
  override = Mock(return_value=selected)
  model, learned = object(), NS(useParams=True, latAccelFactorFiltered=1, latAccelOffsetFiltered=2, frictionCoefficientFiltered=3)

  class Inputs(dict):
    def all_checks(self, _):
      return True

  cp = NS(steerControlType=getattr(car.CarParams.SteerControlType, actuation), lateralTuning=NS(which=lambda: tune))
  owner = NS(CP=cp, CP_SP=None, CI=None, sm=Inputs(modelV2=model, lateralTorqueParameters=learned), lat_delay=0.2)
  scope = {"self": owner, "car": car, "DT_CTRL": .01, "LatControl": object,
           "ControlsExt": NS(initialize_lateral_control=override),
           "LatControlAngle": Mock(return_value=geometric), "LatControlCurvature": Mock(return_value=geometric),
           "LatControlPID": Mock(), "LatControlTorque": Mock()}
  for block in dispatch:
    exec(block, scope)
  if actuation != "torque":
    scope["LatControlAngle" if actuation == "angle" else "LatControlCurvature"].assert_called_once()
    override.assert_not_called()
    assert owner.LaC is geometric
  elif tune == "pid":
    override.assert_called_once_with(owner, scope["LatControlPID"].return_value, None, .01)
    selected.update_model_v2.assert_called_once_with(model)
    selected.extension.update_model_v2.assert_not_called()
  else:
    override.assert_called_once_with(owner, scope["LatControlTorque"].return_value, None, .01)
    selected.update_torque_parameters.assert_called_once_with(1, 2, 3)
    selected.extension.update_limits.assert_called_once_with()
    selected.extension.update_model_v2.assert_called_once_with(model)
    selected.extension.update_lateral_lag.assert_called_once_with(.2)
