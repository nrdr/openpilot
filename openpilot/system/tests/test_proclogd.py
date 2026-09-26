import ast
from io import BytesIO
import os
from pathlib import Path
from typing import TypedDict
from unittest.mock import patch

SOURCE_PATH = Path(__file__).resolve().parents[1] / "proclogd.py"


def _load_smaps_reader() -> dict:
  tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"), filename=str(SOURCE_PATH))
  wanted_assignments = {"_SMAPS_KEYS", "_EMPTY_SMAPS"}
  nodes = []
  for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "SmapsData":
      nodes.append(node)
    elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in wanted_assignments for target in node.targets):
      nodes.append(node)
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted_assignments:
      nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name == "_read_smaps":
      nodes.append(node)

  namespace = {"TypedDict": TypedDict, "os": os}
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE_PATH), "exec"), namespace)
  return namespace


def test_smaps_without_rollup_does_not_open_per_vma_file() -> None:
  module = _load_smaps_reader()
  with patch.object(module["os"].path, "exists", return_value=False), patch("builtins.open") as open_file:
    result = module["_read_smaps"](42)

  open_file.assert_not_called()
  assert result == module["_EMPTY_SMAPS"]


def test_smaps_parses_rollup_without_opening_smaps() -> None:
  module = _load_smaps_reader()
  data = b"Pss: 10 kB\nPss_Anon: 7 kB\nPss_Shmem: 2 kB\nRss: 20 kB\n"
  with patch.object(module["os"].path, "exists", return_value=True), \
       patch("builtins.open", return_value=BytesIO(data)) as open_file:
    result = module["_read_smaps"](42)

  open_file.assert_called_once_with("/proc/42/smaps_rollup", "rb")
  assert result == {"pss": 10 * 1024, "pss_anon": 7 * 1024, "pss_shmem": 2 * 1024}
