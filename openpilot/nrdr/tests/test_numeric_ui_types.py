"""Real native option write path against the strict registered parameter types."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamType

ROOT = Path(__file__).resolve().parents[3]


def option(key, filename):
  path = ROOT / "openpilot/nrdr/ui/settings" / filename
  tree = ast.parse(path.read_text(encoding="utf-8"))
  call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and
              isinstance(n.func, ast.Name) and n.func.id == "option_item_sp" and
              any(k.arg == "param" and isinstance(k.value, ast.Constant) and k.value.value == key for k in n.keywords))
  values = {k.arg: ast.literal_eval(k.value) for k in call.keywords if k.arg in
            ("min_value", "max_value", "value_change_step", "use_float_scaling")}
  label = next(k.value for k in call.keywords if k.arg == "label_callback")
  values["label_callback"] = eval(compile(ast.Expression(label), str(path), "eval"))
  return values


def production_set_value(control, value):
  path = ROOT / "openpilot/system/ui/sunnypilot/widgets/option_control.py"
  cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "OptionControlSP")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "set_value")
  namespace = {}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), namespace)
  namespace["set_value"](control, value)


@pytest.mark.parametrize("key,filename", [
  ("NrdrSteerRatioBlendStart", "steer_ratio_tuning.py"),
  ("NrdrStandstillGapExtra", "longitudinal_tuning.py"),
])
def test_float_settings_write_decimals_without_crashing(key, filename):
  spec = option(key, filename)
  writes = []
  def put(name, value):
    expected = {ParamType.FLOAT: float, ParamType.INT: int}[PARAM_SPECS_BY_KEY[name].param_type]
    assert type(value) is expected, f"UI would raise a Params TypeError: {name} {value!r}"
    writes.append(value)
  control = NS(**spec, current_value=spec["min_value"], value_map=None, param_key=key,
               params=NS(put=put), on_value_changed=None)
  for value in range(spec["min_value"] + spec["value_change_step"], spec["max_value"] + 1, spec["value_change_step"]):
    production_set_value(control, value)
    assert writes[-1] == pytest.approx(value / 100)
  production_set_value(control, spec["min_value"])
  assert writes[-1] == 0.0


def test_blend_display_and_one_degree_step_are_preserved():
  settings = option("NrdrSteerRatioBlendStart", "steer_ratio_tuning.py")
  assert settings["label_callback"](2500) == "25–30°"
  assert settings["label_callback"](18000) == "180–185°"
  assert settings["value_change_step"] / 100 == 1
