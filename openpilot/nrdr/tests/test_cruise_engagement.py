"""Exercise the real initial-speed method without native services."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.common.constants import CV

ROOT = Path(__file__).resolve().parents[3]
BUTTONS = NS(accelCruise=1, resumeCruise=2, decelCruise=3, setCruise=4)


def initialize(helper, cs, experimental):
  source = ROOT / "openpilot/selfdrive/car/cruise.py"
  tree = ast.parse(source.read_text())
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "VCruiseHelper")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "initialize_v_cruise")
  constants = [n for n in tree.body if isinstance(n, ast.Assign) and
               any(isinstance(t, ast.Name) and t.id.startswith("V_CRUISE_") for t in n.targets)]
  env = {"np": np, "CV": CV, "ButtonType": BUTTONS}
  exec(compile(ast.Module(body=[*constants, method], type_ignores=[]), str(source), "exec"), env)
  env["initialize_v_cruise"](helper, cs, experimental)


@pytest.mark.parametrize("experimental", [False, True])
@pytest.mark.parametrize("speed", [0.0, 5.0, 15.0, 25.0, 30.0, 65.0, 100.0])
@pytest.mark.parametrize("button", [BUTTONS.setCruise, BUTTONS.decelCruise])
def test_set_uses_current_speed_in_every_mode(experimental, speed, button):
  helper = NS(CP=NS(pcmCruise=False), v_cruise_initialized=True, v_cruise_kph_last=105.0,
              nrdr=NS(initial_speed=lambda kph: round(kph, 1)))
  initialize(helper, NS(vEgo=speed * CV.MPH_TO_MS, buttonEvents=[NS(type=button)]), experimental)
  assert helper.v_cruise_kph == round(min(speed * CV.MPH_TO_KPH, 169), 1)
  assert helper.v_cruise_cluster_kph == helper.v_cruise_kph


@pytest.mark.parametrize("button", [BUTTONS.accelCruise, BUTTONS.resumeCruise])
@pytest.mark.parametrize("initialized", [True, False])
def test_resume_only_restores_an_initialized_speed(button, initialized):
  helper = NS(CP=NS(pcmCruise=False), v_cruise_initialized=initialized, v_cruise_kph_last=80.0,
              nrdr=NS(initial_speed=lambda kph: round(kph, 1)))
  initialize(helper, NS(vEgo=10.0, buttonEvents=[NS(type=button)]), True)
  assert helper.v_cruise_kph == (80.0 if initialized else 36.0)


def test_pcm_owns_its_set_speed():
  helper = NS(CP=NS(pcmCruise=True), v_cruise_kph=47.0, v_cruise_cluster_kph=47.0)
  initialize(helper, NS(vEgo=10.0, buttonEvents=[]), True)
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == 47.0


def test_retired_dec_has_no_cruise_initialization_authority():
  tree = ast.parse((ROOT / "openpilot/selfdrive/car/cruise.py").read_text())
  method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "initialize_v_cruise")
  assert [arg.arg for arg in method.args.args] == ["self", "CS", "experimental_mode"]
  assert "dynamic_experimental_control" not in ast.unparse(method)
