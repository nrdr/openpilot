#!/usr/bin/env python3
"""Compatibility launcher for the canonical NRDR EPS diagnostic tool."""

from _bootstrap import exec_tool


if __name__ == "__main__":
  exec_tool("eps-diag.py")
