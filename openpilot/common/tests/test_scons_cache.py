"""Run the real SCons scheduler/cache against small generated targets."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


@pytest.fixture
def build(tmp_path):
  root = Path(__file__).resolve().parents[3]
  # Use the project's actual default-target graph walk and recovery registration.
  graph = (root / 'SConstruct').read_text(encoding='utf-8').split('# progress output\n')[1].split('def progress_function(')[0]
  (tmp_path / 'seed').write_text('first')
  (tmp_path / 'SConstruct').write_text(textwrap.dedent("""
    from pathlib import Path
    CacheDir('cache')
    def produce(target, source, env):
      name = target[0].name
      with open('calls', 'a') as f:
        print(name, file=f)
      Path(target[0].abspath).write_bytes(b'' if name == 'marker' or Path('interrupt').exists() else name.encode())
    env = Environment(tools=[])
    targets = [e.Command(name, 'seed', produce)[0] for e, name in
               [(env, 'one.o'), (Environment(tools=[]), 'two.os'), (env, 'marker')]]
    Default(targets)
  """) + graph, encoding='utf-8')

  def run(*args, expect_error=None):
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join((str(root), os.environ.get('PYTHONPATH', '')))}
    result = subprocess.run([sys.executable, '-m', 'SCons', '-Q', *args], cwd=tmp_path, env=env,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if expect_error is None:
      assert result.returncode == 0, result.stdout
    else:
      assert result.returncode == 2 and expect_error in result.stdout and 'Traceback' not in result.stdout, result.stdout

  run()
  return run


def test_rebuilds_only_corrupt_generated_objects(tmp_path, build):
  local, other, calls = (tmp_path / n for n in ('one.o', 'two.os', 'calls'))
  cached, = [p for p in (tmp_path / 'cache').glob('*/*') if p.read_bytes() == other.read_bytes()]
  local.write_bytes(b'')  # Correct build signature but truncated local object.
  cached.write_bytes(b'')  # Missing local object with a poisoned cache entry.
  other.unlink()
  (tmp_path / 'marker').unlink()  # A legitimately empty cached non-object is still a hit.
  stray = tmp_path / 'unmanaged.o'
  stray.touch()
  before = calls.read_text().splitlines()
  build('-n')
  assert local.read_bytes() == cached.read_bytes() == b'' and not other.exists()

  build('--cache-readonly')
  assert local.read_bytes() == b'one.o' and other.read_bytes() == b'two.os'
  assert calls.read_text().splitlines() == [*before, 'two.os']  # one.o was restored from good cache.
  assert cached.read_bytes() == stray.read_bytes() == (tmp_path / 'marker').read_bytes() == b''
  build()
  assert calls.read_text().splitlines() == [*before, 'two.os']


@pytest.mark.parametrize('flags', [(), ('--cache-disable',)])
def test_rebuilds_when_both_copies_are_empty(tmp_path, build, flags):
  local = tmp_path / 'one.o'
  cached, = [p for p in (tmp_path / 'cache').glob('*/*') if p.read_bytes() == local.read_bytes()]
  local.write_bytes(b'')
  cached.write_bytes(b'')
  build(*flags, 'one.o')
  assert local.read_bytes() == b'one.o'
  assert cached.read_bytes() == b''  # Rebuild does not modify even this shared entry.


def test_does_not_publish_an_empty_object(tmp_path, build):
  cache = tmp_path / 'cache'
  before = set(cache.glob('*/*'))
  (tmp_path / 'seed').write_text('new signature')
  interrupted = tmp_path / 'interrupt'
  interrupted.touch()
  build('one.o', expect_error='compiler produced an empty object: one.o')
  assert (tmp_path / 'one.o').read_bytes() == b''
  assert set(cache.glob('*/*')) == before
  interrupted.unlink()
  build('one.o')
  assert (tmp_path / 'one.o').read_bytes() == b'one.o'
