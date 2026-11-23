import ast
from pathlib import Path
from types import SimpleNamespace

from openpilot.sunnypilot.jetlink_adapter import with_blendful

MODELD_V2 = Path(__file__).resolve().parents[2] / 'modeld_v2' / 'modeld.py'


def _recorder():
  calls = []

  def get_action_from_model(*args, **kwargs):
    calls.append(kwargs)
    return SimpleNamespace(desiredCurvature=0.0)
  return get_action_from_model, calls


def test_lateral_speed_reaches_the_action_function():
  # modeld_v2 passes lateral_speed (d344192); without it the fallback to the small
  # model raised a TypeError and modeld died (route 00000006--17e8a390dd, t=703 s)
  stock, calls = _recorder()
  with_blendful(stock, 9.0)({}, None, 0.0, 0.0, 20.0, None, ptm_controller=True, lateral_speed=12.5)
  assert calls == [{'ptm_controller': True, 'lateral_speed': 12.5}]


def test_lateral_speed_defaults_to_none():
  stock, calls = _recorder()
  with_blendful(stock, 9.0)({}, None, 0.0, 0.0, 20.0)
  assert calls == [{'ptm_controller': False, 'lateral_speed': None}]


def test_it_accepts_every_keyword_modeld_v2_passes():
  # catches the next keyword added to modeld_v2's call without the wrapper
  tree = ast.parse(MODELD_V2.read_text())
  passed = {kw.arg for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'get_action_from_model'
            for kw in node.keywords}
  assert passed, 'no get_action_from_model call found in modeld_v2/modeld.py'
  accepted = set(with_blendful(lambda *a, **k: None, 0.0).__code__.co_varnames)
  assert passed <= accepted, passed - accepted
