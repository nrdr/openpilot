import importlib
import sys
from types import ModuleType, SimpleNamespace


# updated is Linux-only, but this regression is pure Python. Stub its platform
# dependencies so the same focused test can run in the Windows development tree.
if sys.platform == "win32":
  sys.modules.setdefault("fcntl", ModuleType("fcntl"))

  params_module = ModuleType("openpilot.common.params")
  params_module.Params = object
  sys.modules.setdefault("openpilot.common.params", params_module)

  swaglog_module = ModuleType("openpilot.common.swaglog")
  swaglog_module.cloudlog = SimpleNamespace()
  sys.modules.setdefault("openpilot.common.swaglog", swaglog_module)

  alertmanager_module = ModuleType("openpilot.selfdrive.selfdrived.alertmanager")
  alertmanager_module.set_offroad_alert = lambda *_args, **_kwargs: None
  sys.modules.setdefault("openpilot.selfdrive.selfdrived.alertmanager", alertmanager_module)

  hardware_module = ModuleType("openpilot.common.hardware")
  hardware_module.AGNOS = False
  hardware_module.HARDWARE = SimpleNamespace(get_device_type=lambda: "pc")
  sys.modules.setdefault("openpilot.common.hardware", hardware_module)

  version_module = ModuleType("openpilot.common.version")
  version_module.get_build_metadata = lambda: None
  version_module.SP_BRANCH_MIGRATIONS = {}
  version_module.sunnylink_consent_version = ""
  version_module.terms_version = ""
  version_module.terms_version_sp = ""
  version_module.training_version = ""
  sys.modules.setdefault("openpilot.common.version", version_module)


updated = importlib.import_module("openpilot.system.updated.updated")
nrdr_hardware = importlib.import_module("openpilot.sunnypilot.nrdr.hardware")


class FakeParams:
  def __init__(self, values):
    self.values = dict(values)

  def get(self, key, *, return_default=False):
    return self.values.get(key)

  def put(self, key, value, *, block=False):
    self.values[key] = value

  def put_bool(self, key, value, *, block=False):
    self.values[key] = bool(value)

  def remove(self, key):
    self.values.pop(key, None)


def test_stale_connectivity_alerts_stay_retired_but_online_failure_remains(monkeypatch, tmp_path):
  params = FakeParams({
    "UpdaterTargetBranch": "test-branch",
    "UptimeOnroad": 10_000 * 60 * 60,
    "RouteCount": 1_000_000,
    "LastUpdateUptimeOnroad": 0.0,
    "LastUpdateRouteCount": 0,
  })
  updater = updated.Updater.__new__(updated.Updater)
  updater.params = params
  updater.branches = {}
  updater._has_internet = False

  monkeypatch.setattr(updated, "BASEDIR", str(tmp_path / "missing-base"))
  monkeypatch.setattr(updated, "FINALIZED", str(tmp_path / "missing-finalized"))
  monkeypatch.setattr(updated, "OVERLAY_MERGED", str(tmp_path / "missing-overlay"))
  monkeypatch.setattr(updated, "parse_release_notes", lambda _path: b"")
  monkeypatch.setattr(updated, "get_build_metadata", lambda: SimpleNamespace(tested_channel=False))

  active_alerts = {
    "Offroad_ConnectivityNeeded": "legacy hard alert",
    "Offroad_ConnectivityNeededPrompt": "legacy prompt",
  }
  alert_calls = []

  def set_alert(name, show, extra_text=None):
    alert_calls.append((name, show, extra_text))
    if show:
      active_alerts[name] = extra_text
    else:
      active_alerts.pop(name, None)

  monkeypatch.setattr(updated, "set_offroad_alert", set_alert)

  updater.set_params(update_success=False, failed_count=1_000_000, exception="network unreachable")

  assert "Offroad_ConnectivityNeeded" not in active_alerts
  assert "Offroad_ConnectivityNeededPrompt" not in active_alerts
  assert "Offroad_UpdateFailed" not in active_alerts
  assert not any(show and name.startswith("Offroad_ConnectivityNeeded") for name, show, _ in alert_calls)

  updater._has_internet = True
  updater.set_params(update_success=False, failed_count=16, exception="git fetch failed")

  assert active_alerts == {"Offroad_UpdateFailed": "git fetch failed"}
  assert not any(show and name.startswith("Offroad_ConnectivityNeeded") for name, show, _ in alert_calls)


def test_nrdr_startup_policy_explicitly_ignores_expired_update_block():
  startup_conditions = {
    "up_to_date": False,
    "accepted_terms": False,
    "accepted_terms_sp": False,
    "completed_training": False,
    "unrelated_safety_gate": False,
  }

  nrdr_hardware.apply_startup_policy(startup_conditions)

  assert startup_conditions["up_to_date"] is True
  assert startup_conditions["accepted_terms"] is True
  assert startup_conditions["accepted_terms_sp"] is True
  assert startup_conditions["completed_training"] is True
  assert startup_conditions["unrelated_safety_gate"] is False
