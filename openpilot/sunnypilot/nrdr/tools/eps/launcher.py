"""Stable launch boundary for canonical and compatibility EPS commands."""

import glob
import os
from pathlib import Path
import subprocess
import sys


EPS_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = EPS_DIR.parents[4]
TOOLS = frozenset(("flash.py", "eps-update.py", "eps-diag.py", "check_rwd.py"))
_RWD_ALIASES = ("rwd/", "eps_tools/rwd/")


def _expand_rwd_alias(argument: str) -> list[str]:
  normalized = argument.replace("\\", "/")
  for prefix in _RWD_ALIASES:
    if not normalized.startswith(prefix):
      continue
    canonical = EPS_DIR / "rwd" / normalized.removeprefix(prefix)
    matches = sorted(glob.glob(str(canonical), recursive=True))
    return matches or [str(canonical)]
  return [argument]


def normalized_arguments(tool: str, arguments: list[str]) -> list[str]:
  if tool not in TOOLS:
    raise ValueError(f"Unknown EPS tool: {tool}")
  if tool not in ("check_rwd.py", "eps-update.py"):
    return list(arguments)

  normalized: list[str] = []
  for argument in arguments:
    expanded = _expand_rwd_alias(argument)
    if tool == "eps-update.py" and len(expanded) > 1:
      raise SystemExit(f"Firmware path matched more than one image: {argument}")
    normalized.extend(expanded)
  return normalized


def exec_tool(tool: str) -> None:
  """Replace the launcher process with the canonical tool.

  Using exec rather than importing the command preserves its arguments, exit
  status, signals, prompts, and __file__-relative firmware/parser lookup.
  """
  if tool not in TOOLS:
    raise ValueError(f"Unknown EPS tool: {tool}")

  environment = os.environ.copy()
  python_path = [str(EPS_DIR), str(REPOSITORY_ROOT)]
  if environment.get("PYTHONPATH"):
    python_path.append(environment["PYTHONPATH"])
  environment["PYTHONPATH"] = os.pathsep.join(python_path)

  target = EPS_DIR / tool
  arguments = normalized_arguments(tool, sys.argv[1:])
  command = [sys.executable, str(target), *arguments]
  if os.name == "nt":
    # Windows Store Python cannot reliably replace itself with os.execve.
    # Keep Linux/device launchers as true exec boundaries while preserving
    # the same arguments and exit status for off-device Windows validation.
    raise SystemExit(subprocess.call(command, env=environment))
  os.execve(sys.executable, command, environment)


__all__ = ("EPS_DIR", "REPOSITORY_ROOT", "TOOLS", "exec_tool", "normalized_arguments")
