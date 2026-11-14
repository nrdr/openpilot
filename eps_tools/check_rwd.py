#!/usr/bin/env python3
"""Compatibility launcher for the canonical NRDR RWD validator."""

from _bootstrap import exec_tool


if __name__ == "__main__":
  exec_tool("check_rwd.py")
