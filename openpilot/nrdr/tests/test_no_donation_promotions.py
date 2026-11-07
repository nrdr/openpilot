"""Keep inherited fundraising text out of NRDR's C3/C4 UI and startup alerts.

Execute the production text-producing functions without loading the native UI,
creating Params, or opening IPC sockets. This also runs on Windows before a build.
"""
import ast
import datetime
from pathlib import Path
import re
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
EVENTS = ROOT / "openpilot/selfdrive/selfdrived/events.py"
MICI_HOME = ROOT / "openpilot/selfdrive/ui/mici/layouts/home.py"


def source_function(path, name, namespace, class_name=None):
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  container = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name) if class_name else tree
  function = next(node for node in container.body if isinstance(node, ast.FunctionDef) and node.name == name)
  future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
  module = ast.fix_missing_locations(ast.Module(body=[future, function], type_ignores=[]))
  exec(compile(module, str(path), "exec"), namespace)
  return namespace[name]


@pytest.mark.parametrize("replay", (False, True))
@pytest.mark.parametrize("branch", ("nrdr-architecture-development", "nrdr-nightly", "350", "nrdr-staging-09.26.2026"))
def test_nrdr_startup_restores_custom_message_and_branch(replay, branch):
  def startup_alert(text, branch, **kwargs):
    return SimpleNamespace(text=text, branch=branch, **kwargs)

  startup = source_function(EVENTS, "startup_master_alert", {
    "StartupAlert": startup_alert,
    "AlertStatus": SimpleNamespace(normal="normal"),
    "get_short_branch": lambda: branch,
    "os": SimpleNamespace(environ={"REPLAY": "1"} if replay else {}),
  })
  alert = startup(None, None, None, False, 0, None)
  assert alert.text == "Openpilot is now in on-road mode."
  assert alert.branch == ("replay" if replay else branch)
  assert alert.alert_status == "normal"


def test_startup_message_and_takeover_reminder_remain_registered():
  tree = ast.parse(EVENTS.read_text(encoding="utf-8"))
  startup_events = {}
  for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
      for key, value in zip(node.keys, node.values, strict=True):
        if isinstance(key, ast.Attribute) and isinstance(key.value, ast.Name) and key.value.id == "EventName":
          startup_events[key.attr] = value
  registration = startup_events["startupMaster"]
  assert isinstance(registration, ast.Dict)
  assert any(isinstance(value, ast.Name) and value.id == "startup_master_alert" for value in registration.values)
  assert "Be ready to take over at any time" in ast.unparse(startup_events["startup"])
  assert all(key in startup_events for key in ("startupNoCar", "startupNoControl", "startupNoSecOcKey"))


def version_text(values):
  function = source_function(MICI_HOME, "_get_version_text", {
    "ui_state": SimpleNamespace(params=values), "datetime": datetime,
  }, "MiciHomeLayout")
  return function(None)


@pytest.mark.parametrize("branch", ("release", "nrdr-nightly", "nrdr-architecture-development"))
def test_mici_home_shows_actual_branch_and_short_commit(branch):
  stamp = 1708012345
  text = version_text({
    "Version": "2026.003.000", "GitBranch": branch, "GitCommit": "94bdcd4bc4f66d5493daa7c0bddf71ca1bdb6bdd",
    "GitCommitDate": f"'{stamp} 2024-02-15 12:00:00 +0000'",
  })
  assert text == ("2026.003.000", branch, "94bdcd4", datetime.datetime.fromtimestamp(stamp).strftime("%b %d"))


@pytest.mark.parametrize("missing", ("Version", "GitBranch", "GitCommit"))
def test_incomplete_mici_version_metadata_does_not_show_placeholder(missing):
  values = {"Version": "1.0", "GitBranch": "release", "GitCommit": "abcdef0123"}
  values.pop(missing)
  assert version_text(values) is None


@pytest.mark.parametrize("date", (None, "", "not a date"))
def test_invalid_commit_date_still_shows_real_commit(date):
  assert version_text({"Version": "1.0", "GitBranch": "dev", "GitCommit": "abcdef0123", "GitCommitDate": date}) == (
    "1.0", "dev", "abcdef0", "",
  )


def test_mici_commit_font_is_restored():
  tree = ast.parse(MICI_HOME.read_text(encoding="utf-8"))
  assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Attribute) and target.attr == "_version_commit_label" for target in node.targets))
  assert next(ast.literal_eval(keyword.value) for keyword in assignment.value.keywords if keyword.arg == "font_size") == 36


def test_no_donation_advertising_in_production_ui_sources():
  pattern = re.compile(r"buy[\s_-]*me[\s_-]*a[\s_-]*coffee|bmc\.link", re.IGNORECASE)
  paths = [EVENTS]
  for folder in ("openpilot/selfdrive/ui", "openpilot/system/ui", "openpilot/nrdr/ui",
                 "openpilot/sunnypilot/sunnylink", "openpilot/sunnypilot/selfdrive/selfdrived"):
    paths.extend(path for path in (ROOT / folder).rglob("*")
                 if path.is_file() and path.suffix in (".py", ".json", ".yaml", ".yml", ".ts", ".po", ".pot", ".html")
                 and not {"test", "tests", "docs"}.intersection(path.parts))
  offenders = [str(path.relative_to(ROOT)) for path in paths if pattern.search(path.read_text(encoding="utf-8"))]
  assert not offenders, f"Donation promotion reintroduced in production UI: {offenders}"
