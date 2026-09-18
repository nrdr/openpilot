#!/usr/bin/env python3
"""Restore stock communication alerts in a generated clean release tree only."""

import argparse
import ast
from pathlib import Path


EVENTS_PATH = Path("openpilot/selfdrive/selfdrived/events.py")
COMM_EVENT_HANDLERS = {
  "commIssue": (
    'ET.SOFT_DISABLE: soft_disable_alert("Communication Issue Between Processes"),',
    'ET.NO_ENTRY: comm_issue_alert,',
  ),
  "commIssueAvgFreq": (
    'ET.SOFT_DISABLE: soft_disable_alert("Low Communication Rate Between Processes"),',
    'ET.NO_ENTRY: NoEntryAlert("Low Communication Rate Between Processes"),',
  ),
}


def _event_name(node: ast.AST | None) -> str | None:
  if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "EventName":
    return node.attr
  return None


def _events_mapping(tree: ast.Module) -> ast.Dict:
  assignments = []
  for statement in tree.body:
    if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
      targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
      if any(isinstance(node, ast.Name) and node.id == "EVENTS" for target in targets for node in ast.walk(target)):
        assignments.append(statement)
  if len(assignments) != 1:
    raise ValueError(f"expected exactly one EVENTS assignment, found {len(assignments)}")
  assignment = assignments[0]
  targets = assignment.targets if isinstance(assignment, ast.Assign) else [assignment.target]
  if len(targets) != 1 or not isinstance(targets[0], ast.Name) or targets[0].id != "EVENTS":
    raise ValueError("expected a direct assignment to EVENTS")
  if isinstance(assignment, ast.AugAssign) or not isinstance(assignment.value, ast.Dict):
    raise ValueError("expected EVENTS to be a dictionary literal")
  if any(key is None for key in assignment.value.keys):
    raise ValueError("unexpected dictionary unpacking in EVENTS")
  return assignment.value


def _canonical_handlers(value: ast.Dict, handlers: tuple[str, ...]) -> bool:
  expected = ast.parse("{" + " ".join(handlers) + "}", mode="eval").body
  assert isinstance(expected, ast.Dict)
  actual_items = [(ast.dump(key), ast.dump(item)) for key, item in zip(value.keys, value.values, strict=True) if key is not None]
  expected_items = [(ast.dump(key), ast.dump(item)) for key, item in zip(expected.keys, expected.values, strict=True) if key is not None]
  return len(actual_items) == len(value.keys) and sorted(actual_items) == sorted(expected_items)


def restore_comm_event_source(source: str) -> str:
  """Replace only empty communication event values; reject unexpected source drift.

  AST parsing does not import or execute the events module. Byte-based AST spans
  preserve every unrelated character, including Unicode and original newlines.
  Already-restored handler dictionaries are accepted without rewriting them.
  """
  try:
    mapping = _events_mapping(ast.parse(source))
  except SyntaxError as error:
    raise ValueError(f"cannot parse base events source: {error.msg}") from error

  encoded = source.encode("utf-8")
  lines = encoded.splitlines(keepends=True)
  line_offsets = [0]
  for line in lines:
    line_offsets.append(line_offsets[-1] + len(line))

  replacements = []
  for name, handlers in COMM_EVENT_HANDLERS.items():
    matches = [(key, value) for key, value in zip(mapping.keys, mapping.values, strict=True) if _event_name(key) == name]
    if len(matches) != 1:
      raise ValueError(f"expected exactly one EventName.{name} entry, found {len(matches)}")
    key, value = matches[0]
    if not isinstance(value, ast.Dict):
      raise ValueError(f"expected EventName.{name} to be a dictionary literal")
    if value.keys:
      if not _canonical_handlers(value, handlers):
        raise ValueError(f"unexpected handlers for EventName.{name}; refusing to overwrite them")
      continue

    assert key is not None and value.end_lineno is not None and value.end_col_offset is not None
    key_line = lines[key.lineno - 1]
    indent = key_line[:len(key_line) - len(key_line.lstrip(b" \t"))]
    value_line = lines[value.lineno - 1]
    newline = b"\r\n" if value_line.endswith(b"\r\n") else b"\r" if value_line.endswith(b"\r") else b"\n"
    replacement = b"{" + newline + b"".join(indent + b"  " + handler.encode("utf-8") + newline for handler in handlers) + indent + b"}"
    start = line_offsets[value.lineno - 1] + value.col_offset
    end = line_offsets[value.end_lineno - 1] + value.end_col_offset
    replacements.append((start, end, replacement))

  for start, end, replacement in sorted(replacements, reverse=True):
    encoded = encoded[:start] + replacement + encoded[end:]
  restored = encoded.decode("utf-8")
  # Do not write an output that fails Python's syntax validation.
  ast.parse(restored)
  return restored


def restore_comm_events(build_root: Path) -> bool:
  """Restore the clean tree's base events file, returning whether it changed."""
  root = build_root.resolve(strict=True)
  if not root.is_dir():
    raise ValueError(f"build root is not a directory: {root}")
  target = (root / EVENTS_PATH).resolve(strict=True)
  if not target.is_relative_to(root) or not target.is_file():
    raise ValueError(f"base events target must be a file inside the build root: {target}")
  original = target.read_bytes()
  restored = restore_comm_event_source(original.decode("utf-8")).encode("utf-8")
  if restored == original:
    return False
  target.write_bytes(restored)
  return True


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("build_root", type=Path, help="generated clean build root (never the development checkout)")
  arguments = parser.parse_args()
  try:
    restore_comm_events(arguments.build_root)
  except (OSError, ValueError) as error:
    parser.exit(1, f"clean communication event restoration failed: {error}\n")


if __name__ == "__main__":
  main()
