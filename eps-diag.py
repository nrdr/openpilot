#!/usr/bin/env python3
"""Run the NRDR EPS diagnostic tool from the repository root."""

from openpilot.sunnypilot.nrdr.tools.eps.launcher import exec_tool


if __name__ == "__main__":
  exec_tool("eps-diag.py")
