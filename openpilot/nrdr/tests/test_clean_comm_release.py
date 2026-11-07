import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / "openpilot/nrdr/tools/release/clean_overlay/restore_comm_events.py"
BASE_EVENTS_PATH = Path("openpilot/selfdrive/selfdrived/events.py")
EXPECTED_HANDLERS = {
  "commIssue": {
    "SOFT_DISABLE": 'soft_disable_alert("Communication Issue Between Processes")',
    "NO_ENTRY": "comm_issue_alert",
  },
  "commIssueAvgFreq": {
    "SOFT_DISABLE": 'soft_disable_alert("Low Communication Rate Between Processes")',
    "NO_ENTRY": 'NoEntryAlert("Low Communication Rate Between Processes")',
  },
}

spec = importlib.util.spec_from_file_location("restore_comm_events", HELPER_PATH)
assert spec is not None and spec.loader is not None
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def source_fixture(first: str = "{}", second: str = "{}") -> str:
  return (
    '# Preserve this header and all unrelated definitions.\n'
    'raise RuntimeError("The release helper must never execute this module")\n'
    'EVENTS: dict[int, dict] = {\n'
    '  EventName.canError: {ET.NO_ENTRY: NoEntryAlert("CAN Error")},\n'
    f'  EventName.commIssue: {first},\n'
    '  # Keep this separator.\n'
    f'  EventName.commIssueAvgFreq: {second},\n'
    '  EventName.processNotRunning: {ET.SOFT_DISABLE: soft_disable_alert("Process Not Running")},\n'
    '}\n'
    'OTHER = {EventName.commIssue: "unrelated dictionary stays unchanged"}\n'
  )


def canonical_value(name: str, indent: str = "  ", newline: str = "\n") -> str:
  handlers = EXPECTED_HANDLERS[name]
  return "{" + newline + "".join(f"{indent}  ET.{event_type}: {expression},{newline}" for event_type, expression in handlers.items()) + indent + "}"


def event_mapping(source: str) -> ast.Dict:
  for node in ast.parse(source).body:
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "EVENTS":
      assert isinstance(node.value, ast.Dict)
      return node.value
  raise AssertionError("EVENTS mapping missing")


def assert_canonical_handlers(source: str) -> None:
  mapping = event_mapping(source)
  values = {key.attr: value for key, value in zip(mapping.keys, mapping.values, strict=True) if isinstance(key, ast.Attribute)}
  for name, expected in EXPECTED_HANDLERS.items():
    value = values[name]
    assert isinstance(value, ast.Dict)
    assert len(value.keys) == 2
    actual = {}
    for key, handler in zip(value.keys, value.values, strict=True):
      assert isinstance(key, ast.Attribute) and isinstance(key.value, ast.Name) and key.value.id == "ET"
      actual[key.attr] = ast.dump(handler)
    assert actual == {event_type: ast.dump(ast.parse(expression, mode="eval").body) for event_type, expression in expected.items()}


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_restores_only_exact_canonical_handlers_and_preserves_unrelated_bytes(newline: str) -> None:
  source = source_fixture().replace("\n", newline)
  expected = source
  for name in EXPECTED_HANDLERS:
    expected = expected.replace(f"EventName.{name}: {{}}", f"EventName.{name}: {canonical_value(name, newline=newline)}", 1)

  restored = helper.restore_comm_event_source(source)

  assert restored == expected
  assert_canonical_handlers(restored)
  assert helper.restore_comm_event_source(restored) == restored


def test_restores_real_source_without_changing_any_unrelated_event() -> None:
  original = (REPO_ROOT / BASE_EVENTS_PATH).read_bytes()
  source = original.decode("utf-8")
  newline = "\r\n" if "\r\n" in source else "\n"
  expected = source
  for name in EXPECTED_HANDLERS:
    empty_entry = f"EventName.{name}: {{{newline}  }}"
    assert expected.count(empty_entry) == 1
    expected = expected.replace(empty_entry, f"EventName.{name}: {canonical_value(name, newline=newline)}", 1)

  restored = helper.restore_comm_event_source(source)

  assert restored == expected
  assert_canonical_handlers(restored)
  assert (REPO_ROOT / BASE_EVENTS_PATH).read_bytes() == original


def test_utf8_byte_offsets_preserve_non_ascii_before_inline_values() -> None:
  source = 'EVENTS = {EventName.other: "café 🚗", EventName.commIssue: {}, EventName.commIssueAvgFreq: {}}\n'
  expected = source
  for name in EXPECTED_HANDLERS:
    expected = expected.replace(f"EventName.{name}: {{}}", f"EventName.{name}: {canonical_value(name, indent='')}", 1)
  assert helper.restore_comm_event_source(source) == expected


def test_already_correct_dictionaries_preserve_original_formatting_and_order() -> None:
  first = "{" + ", ".join(f"ET.{event_type}: {expression}" for event_type, expression in reversed(EXPECTED_HANDLERS["commIssue"].items())) + "}"
  source = source_fixture(first=first, second=canonical_value("commIssueAvgFreq"))
  assert helper.restore_comm_event_source(source) == source


def test_mixed_empty_and_restored_entries_are_supported() -> None:
  source = source_fixture(first=canonical_value("commIssue"))
  assert helper.restore_comm_event_source(source) == source_fixture(first=canonical_value("commIssue"), second=canonical_value("commIssueAvgFreq"))


@pytest.mark.parametrize("source, message", [
  ("EVENTS = {", "cannot parse"),
  ("OTHER = {}", "exactly one EVENTS assignment"),
  (source_fixture() + "EVENTS = {}\n", "exactly one EVENTS assignment"),
  ("EVENTS = []", "dictionary literal"),
  ("EVENTS: dict", "dictionary literal"),
  ("EVENTS += {}", "dictionary literal"),
  ("EVENTS, OTHER = {}", "direct assignment"),
  ("EVENTS = OTHER = {}", "direct assignment"),
  ("EVENTS = {}", "exactly one EventName.commIssue entry"),
  (source_fixture().replace("EventName.commIssueAvgFreq:", "EventName.other:"), "exactly one EventName.commIssueAvgFreq entry"),
  (source_fixture().replace("  # Keep this separator.", "  EventName.commIssue: {},"), "exactly one EventName.commIssue entry"),
  (source_fixture().replace("  # Keep this separator.", "  EventName.commIssueAvgFreq: {},"), "exactly one EventName.commIssueAvgFreq entry"),
  (source_fixture().replace("  # Keep this separator.", "  **OTHER,"), "dictionary unpacking"),
  (source_fixture(first="None"), "dictionary literal"),
  (source_fixture(second="make_events()"), "dictionary literal"),
  (source_fixture(first='{ET.NO_ENTRY: comm_issue_alert}'), "unexpected handlers"),
  (source_fixture(first='{ET.NO_ENTRY: other_alert, ET.SOFT_DISABLE: soft_disable_alert("Communication Issue Between Processes")}'), "unexpected handlers"),
  (source_fixture(second='{ET.NO_ENTRY: NoEntryAlert("Wrong text"), ET.SOFT_DISABLE: soft_disable_alert("Low Communication Rate Between Processes")}'),
   "unexpected handlers"),
  (source_fixture(first='{**OTHER}'), "unexpected handlers"),
  (source_fixture(first='{ET.NO_ENTRY: comm_issue_alert, ET.NO_ENTRY: comm_issue_alert}'), "unexpected handlers"),
])
def test_unexpected_or_ambiguous_source_fails_closed(source: str, message: str) -> None:
  with pytest.raises(ValueError, match=message):
    helper.restore_comm_event_source(source)


def write_build_source(root: Path, source: str) -> Path:
  target = root / BASE_EVENTS_PATH
  target.parent.mkdir(parents=True)
  target.write_bytes(source.encode("utf-8"))
  return target


def test_cli_changes_only_target_in_generated_tree_and_is_idempotent(tmp_path: Path) -> None:
  source = source_fixture().replace("\n", "\r\n")
  target = write_build_source(tmp_path / "clean build", source)
  sentinel = target.parent / "other.py"
  sentinel.write_bytes(b"untouched\r\n")
  command = [sys.executable, str(HELPER_PATH), str(tmp_path / "clean build")]

  result = subprocess.run(command, capture_output=True, text=True, check=False)
  assert result.returncode == 0, result.stderr
  assert target.read_bytes() == helper.restore_comm_event_source(source).encode("utf-8")
  assert sentinel.read_bytes() == b"untouched\r\n"
  modified = target.stat().st_mtime_ns
  result = subprocess.run(command, capture_output=True, text=True, check=False)
  assert result.returncode == 0, result.stderr
  assert target.stat().st_mtime_ns == modified


def test_cli_failure_does_not_partially_rewrite_first_entry(tmp_path: Path) -> None:
  source = source_fixture(second="None")
  target = write_build_source(tmp_path, source)

  result = subprocess.run([sys.executable, str(HELPER_PATH), str(tmp_path)], capture_output=True, text=True, check=False)

  assert result.returncode != 0
  assert "clean communication event restoration failed" in result.stderr
  assert target.read_bytes() == source.encode("utf-8")


def test_target_symlink_outside_build_root_is_rejected(tmp_path: Path) -> None:
  outside = tmp_path / "outside.py"
  original = source_fixture().encode("utf-8")
  outside.write_bytes(original)
  root = tmp_path / "clean"
  target = root / BASE_EVENTS_PATH
  target.parent.mkdir(parents=True)
  try:
    target.symlink_to(outside)
  except OSError as error:
    pytest.skip(f"symlinks unavailable: {error}")

  with pytest.raises(ValueError, match="inside the build root"):
    helper.restore_comm_events(root)
  assert outside.read_bytes() == original


def test_missing_base_events_target_fails_without_creating_files(tmp_path: Path) -> None:
  with pytest.raises(FileNotFoundError):
    helper.restore_comm_events(tmp_path)
  assert list(tmp_path.iterdir()) == []
