"""Exercise the real C4 overrides without loading a graphics context."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import pytest


SOURCE = Path(__file__).parents[1] / "ui/onroad/mici_onroad.py"


def ball(show, sidebar):
  calls = []

  class Base:
    def __init__(self):
      self._rect = NS(x=0, y=0, width=536, height=240)
      self._demo = False
      self._confidence_filter = NS(x=0.5)

    def _update_state(self):
      calls.append("animate")

    def _render(self, rect):
      calls.append(("original", rect))

  tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "NrdrConfidenceBall")
  state = NS(nrdr_confidence_ball=show, nrdr_developer_sidebar=sidebar, status=0)
  env = {"ConfidenceBall": Base, "ui_state": state, "SIDE_PANEL_WIDTH": 60,
         "UIStatus": NS(ENGAGED=1, LAT_ONLY=2, LONG_ONLY=3, OVERRIDE=4),
         "rl": NS(Color=lambda *v: v), "draw_circle_gradient": lambda *v: calls.append(("fixed", *v))}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), str(SOURCE), "exec"), env)
  return env["NrdrConfidenceBall"](), calls


@pytest.mark.parametrize("show", [False, True])
@pytest.mark.parametrize("sidebar", [False, True])
def test_ball_animation_and_position(show, sidebar):
  instance, calls = ball(show, sidebar)
  instance._update_state()
  assert ("animate" in calls) is show
  if show:  # Widget's visibility gate skips rendering otherwise.
    instance._render(instance._rect)
    assert calls[-1][0] == ("fixed" if sidebar else "original")
    if sidebar:
      assert calls[-1][1:4] == (436, 60, 24)
  else:
    assert not calls


def test_sidebar_off_skips_all_metric_reads_and_draws():
  tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "StripDevUiRenderer")
  render = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_render")
  env = {"ui_state": NS(nrdr_developer_sidebar=False)}
  exec(compile(ast.Module(body=[render], type_ignores=[]), str(SOURCE), "exec"), env)
  env["_render"](None, None)  # No other state is available: disabled means no reads/draws.


def test_master_visibility_keeps_alert_suppression():
  text = SOURCE.read_text(encoding="utf-8")
  assert "set_visible(ui_state.nrdr_confidence_ball and _confidence_ball_visible(alert_type))" in text
