"""Exercise generic compiler build wiring without SCons, native modules or a GPU."""
import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import shlex
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCONSCRIPT = ROOT / 'openpilot/selfdrive/modeld/SConscript'
MODEL_DIR = '/repo/openpilot/selfdrive/modeld'


class WithoutImports(ast.NodeTransformer):
  def visit_Import(self, node):
    return None

  def visit_ImportFrom(self, node):
    return None


class BuildFile:
  def __init__(self, path):
    path = str(path)
    self.abspath = str(PurePosixPath('/repo', path[1:]) if path.startswith('#') else PurePosixPath(MODEL_DIR, path))
    self.relpath = self.abspath.removeprefix('/repo/')

  def __str__(self):
    return self.abspath


@dataclass
class BuildAction:
  function: object
  display: str


class BuildEnvironment:
  def __init__(self):
    self.commands, self.side_effects, self.executed = [], [], []

  def Clone(self):
    return self

  def Dir(self, path):
    return BuildFile(path)

  def PrependENVPath(self, *_args):
    pass

  def Command(self, targets, sources, actions):
    node = SimpleNamespace(targets=targets, sources=sources, actions=actions)
    self.commands.append(node)
    return node

  def SideEffect(self, lock, node):
    self.side_effects.append((str(lock), node))

  def Execute(self, command):
    self.executed.append(command)
    return 0


def assemble_build(arch, chestnut=False, link=True, skip=False):
  tree = WithoutImports().visit(ast.parse(SCONSCRIPT.read_text(encoding='utf-8')))
  env = BuildEnvironment()
  namespace = {'arch': arch, 'env': env, 'Import': lambda *_: None, 'File': BuildFile, 'Dir': BuildFile,
                   'Action': BuildAction, 'Value': lambda v: v, 'chestnut_present': lambda: chestnut, 'link_up': lambda: link,
                   'time': SimpleNamespace(sleep=lambda *_: None),
                   'glob': SimpleNamespace(glob=lambda *a, **k: ['tinygrad_repo/tinygrad/engine/jit.py']),
                   'os': SimpleNamespace(getenv=lambda key: '1' if key == 'SKIP_TINYGRAD_COMPILE' and skip else None,
                                      path=SimpleNamespace(isfile=lambda _: True, join=lambda *p: str(PurePosixPath(*p)),
                                                          expanduser=lambda _: '/home/test')),
                   '_ar_ox_fisheye': SimpleNamespace(width=1928, height=1208), '_os_fisheye': SimpleNamespace(width=1344, height=760),
                   'MEDMODEL_INPUT_SIZE': (512, 256), 'DM_INPUT_SIZE': (1440, 960),
                   'get_nv12_info': lambda w, h: (w, h, h // 2, w * (h + h // 2))}
  exec(compile(tree, str(SCONSCRIPT), 'exec'), namespace)
  return env


@pytest.mark.parametrize('arch', ['comma_arm64', 'Darwin', 'x86_64'])
@pytest.mark.parametrize('chestnut', [False, True])
def test_generic_build_inherits_affinity_and_declares_provenance(arch, chestnut):
  env = assemble_build(arch, chestnut)
  assert len(env.commands) == (8 if chestnut else 6)
  for node in env.commands:
    assert len(node.targets) == 2
    pkl, stamp = node.targets
    assert stamp == pkl + '.nrdr-abi.json'
    if isinstance(node.actions, BuildAction) and callable(node.actions.function):
      assert node.actions.function([], [], env) == 0
      command = env.executed[-1]
      assert (f'{MODEL_DIR}/models/.chestnut.lock', node) in env.side_effects
    else:
      command = node.actions.function if isinstance(node.actions, BuildAction) else node.actions
    words = shlex.split(command)
    executable = next(i for i, word in enumerate(words) if '=' not in word)
    assert words[executable:executable + 2] == ['python3', '/repo/openpilot/nrdr/tools/model_compile.py']
    assert 'taskset' not in command
    assert words[words.index('--output') + 1] == pkl
    assert any(str(source).endswith('model_artifacts.json') for source in node.sources)
    assert any(str(source).endswith('model_artifacts.py') for source in node.sources)
    assert '#tinygrad_repo/tinygrad/engine/jit.py' in node.sources
    if words[executable + 2] == 'onnx':
      assert '--out-of-band' in words and '--device-input' in words
    elif 'dm_warp' in pkl:
      assert words[words.index('--layout') + 1] == 'luma'
    else:
      assert words[words.index('--frames') + 1] == '2'
  targets = [node.targets[0] for node in env.commands]
  for stem in ('driving_warp', 'dm_warp'):
    for resolution in ('1928x1208', '1344x760'):
      assert f'{MODEL_DIR}/models/{stem}_{resolution}_tinygrad.pkl' in targets
  assert not any('big_driving_tinygrad.pkl' in path for path in targets)


def test_missing_chestnut_link_is_a_failed_build_not_a_fake_success():
  env = assemble_build('comma_arm64', chestnut=True, link=False)
  actions = [node.actions for node in env.commands if isinstance(node.actions, BuildAction) and callable(node.actions.function)]
  assert len(actions) == 2
  assert all(action.function([], [], env) == 1 for action in actions)
  assert env.executed == []


def test_explicit_ci_skip_still_builds_all_camera_warps():
  env = assemble_build('comma_arm64', chestnut=False, skip=True)
  assert len(env.commands) == 4
  assert all('_warp_' in node.targets[0] for node in env.commands)
