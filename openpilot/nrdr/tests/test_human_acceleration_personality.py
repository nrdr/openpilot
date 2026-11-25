import ast
from pathlib import Path

import pytest

from openpilot.cereal import log
from openpilot.nrdr.features.longitudinal.bosch_a import human_acceleration

P = log.LongitudinalPersonality


def test_applies_relaxed_standard_and_econ_only():
  assert human_acceleration.applies(P.relaxed)
  assert human_acceleration.applies(P.standard)
  assert human_acceleration.applies(P.econ)
  assert not human_acceleration.applies(P.aggressive)


def test_applies_takes_raw_ints_and_rejects_junk():
  assert human_acceleration.applies(1) and human_acceleration.applies(2)
  assert not human_acceleration.applies(0)
  assert human_acceleration.applies(3)  # Econ
  for junk in (None, True, 7, -1, "standard"):
    assert not human_acceleration.applies(junk), junk


def test_cap_unchanged():
  # 30 mph set speed, 15 mph ego: between half and full max accel, ramp-off not reached.
  assert abs(human_acceleration.cap(2.0, 13.4, 6.7) - (1.0 + 1.0 * (13.4 - 12.5) / 12.5)) < 1e-6


@pytest.mark.parametrize('personality', [P.aggressive, P.standard, P.relaxed, P.econ])
@pytest.mark.parametrize('target', [-2.0, 0.0, 1.5])
def test_post_planner_cap_preserves_uncapped_personality_and_braking(personality, target):
  # Exercise the production cap block without importing the native MPC solver.
  path = Path(__file__).parents[2] / 'selfdrive/controls/lib/longitudinal_planner.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  cap_block = next(node for node in ast.walk(tree) if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "'acceleration_max' in bosch_a_mpc")
  capped = human_acceleration.applies(personality)
  scope = {'output_a_target': target, 'bosch_a_mpc': {'acceleration_max': 0.5} if capped else {}}
  exec(compile(ast.Module(body=[cap_block], type_ignores=[]), str(path), 'exec'), scope)
  assert scope['output_a_target'] == (min(target, 0.5) if capped else target)
