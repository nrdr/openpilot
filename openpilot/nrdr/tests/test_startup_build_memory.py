"""Run startup build control flow without hardware, native Params, or a compiler."""
import ast
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


SOURCE = Path(__file__).resolve().parents[2] / "system/manager/build.py"


def run_build(agnos, results, *, ci=False):
  tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
  tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build"]
  attempts = []
  spinner = Mock()
  window = Mock()
  window.__enter__ = Mock(return_value=window)
  window.__exit__ = Mock(return_value=False)
  codes = iter(results)

  class Process:
    def __init__(self, command, **kwargs):
      attempts.append((command, kwargs))
      self.returncode = next(codes)
      self.stderr = io.BytesIO(b"progress: 100\n" if self.returncode == 0 else b"compiler failed\n")

    def __enter__(self):
      return self

    def __exit__(self, *args):
      return False

    def poll(self):
      return self.returncode

  def exit_build(code):
    raise SystemExit(code)

  env = {
    "os": SimpleNamespace(environ={"PWD": "/wrong"}, sched_setaffinity=Mock(), sync=Mock(),
                          getenv=lambda key: "1" if ci and key == "CI" else None),
    "subprocess": SimpleNamespace(Popen=Process, PIPE=object()),
    "BASEDIR": "/checkout", "AGNOS": agnos, "HARDWARE": Mock(),
    "Spinner": Mock(return_value=spinner), "TextWindow": Mock(return_value=window), "exit": exit_build,
  }
  exec(compile(tree, str(SOURCE), "exec"), env)
  try:
    env["build"]()
    exit_code = 0
  except SystemExit as error:
    exit_code = error.code
  return attempts, env, exit_code


def test_device_first_attempt_is_serial_without_debug_symbols():
  attempts, env, exit_code = run_build(True, [0])
  assert exit_code == 0
  assert [command for command, _ in attempts] == [["scons", "-j1", "--ccflags=-g0"]]
  assert attempts[0][1]["cwd"] == attempts[0][1]["env"]["PWD"] == "/checkout"
  env["os"].sched_setaffinity.assert_called_once_with(0, range(8))
  env["TextWindow"].assert_not_called()
  env["os"].sync.assert_called_once()


@pytest.mark.parametrize("ci", [False, True])
def test_device_failure_is_not_hidden_or_retried_with_unsafe_flags(ci):
  attempts, env, exit_code = run_build(True, [-9], ci=ci)
  assert exit_code == 1
  assert len(attempts) == 1
  env["Spinner"].return_value.close.assert_called_once()
  if ci:
    env["TextWindow"].assert_not_called()
  else:
    assert "compiler failed" in env["TextWindow"].call_args.args[0]
    env["TextWindow"].return_value.wait_for_exit.assert_called_once()


@pytest.mark.parametrize("results", [[0], [1, 0], [1, 1, 0], [1, 1, 1]])
def test_desktop_retry_behavior_is_preserved(results):
  attempts, env, exit_code = run_build(False, results)
  assert [command for command, _ in attempts] == [["scons"], ["scons", "-j4"], ["scons", "-j1"]][:len(results)]
  assert exit_code == (0 if results[-1] == 0 else 1)
  env["os"].sched_setaffinity.assert_not_called()
