#!/usr/bin/env python3
"""Run the NRDR EPS firmware updater from the repository root."""

from openpilot.nrdr.tools.eps.launcher import exec_tool


if __name__ == "__main__":
  exec_tool("eps-update.py")
