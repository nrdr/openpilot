"""Compatibility bootstrap for the former eps_tools command paths."""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
  sys.path.insert(0, str(REPOSITORY_ROOT))

from openpilot.sunnypilot.nrdr.tools.eps.launcher import exec_tool


__all__ = ("exec_tool",)
