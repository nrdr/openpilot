#!/usr/bin/env python3
"""Run the guided NRDR EPS flasher from the repository root."""

from openpilot.sunnypilot.nrdr.tools.eps.launcher import exec_tool


if __name__ == "__main__":
  exec_tool("flash.py")
