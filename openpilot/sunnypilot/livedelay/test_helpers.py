import ast
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

previous_params_module = sys.modules.get("openpilot.common.params")
injected_params_module = sys.platform == "win32" and previous_params_module is None
if injected_params_module:
  params_module = ModuleType("openpilot.common.params")
  params_module.Params = object
  sys.modules["openpilot.common.params"] = params_module

from openpilot.sunnypilot.livedelay.helpers import LAT_DELAY_BUFFER_SECONDS, MAX_SOFTWARE_DELAY, MIN_SOFTWARE_DELAY, get_lat_delay

lagd_toggle = importlib.import_module("openpilot.sunnypilot.livedelay.lagd_toggle")
if injected_params_module:
  del sys.modules["openpilot.common.params"]
  del sys.modules["openpilot.sunnypilot.livedelay.lagd_toggle"]
  delattr(sys.modules["openpilot.sunnypilot.livedelay"], "lagd_toggle")


class FakeParams:
  def __init__(self, live_learning: bool, software_delay: float):
    self.values = {
      "LagdToggle": live_learning,
      "LagdToggleDelay": software_delay,
      "LagdValueCache": 0.31,
    }
    self.writes = {}

  def get_bool(self, key: str) -> bool:
    return bool(self.values[key])

  def get(self, key: str, *, return_default: bool = False):
    return self.values[key]

  def put(self, key: str, value: float) -> None:
    self.values[key] = value
    self.writes[key] = value


def test_live_learning_uses_published_delay():
  params = FakeParams(True, MAX_SOFTWARE_DELAY)
  assert get_lat_delay(params, 0.37, 0.10) == 0.37


@pytest.mark.parametrize("live_delay", [0.0, float("nan"), None])
def test_live_learning_ignores_stale_cache_until_published_delay_is_valid(live_delay):
  params = FakeParams(True, MAX_SOFTWARE_DELAY)
  params.values["LagdValueCache"] = 1.70
  assert get_lat_delay(params, live_delay, 0.10) == pytest.approx(0.30)


@pytest.mark.parametrize("live_delay", [float("inf"), -1.0])
def test_live_learning_falls_back_to_actuator_plus_default(live_delay):
  params = FakeParams(True, MAX_SOFTWARE_DELAY)
  assert get_lat_delay(params, live_delay, 0.10) == pytest.approx(0.30)


def test_live_learning_delay_is_bounded_by_history():
  params = FakeParams(True, MAX_SOFTWARE_DELAY)
  assert get_lat_delay(params, 9.0, 0.10) == LAT_DELAY_BUFFER_SECONDS


@pytest.mark.parametrize("software_delay", [MIN_SOFTWARE_DELAY, 0.2, 0.5, MAX_SOFTWARE_DELAY])
def test_fixed_delay_adds_actuator_and_software_delay(software_delay):
  params = FakeParams(False, software_delay)
  assert get_lat_delay(params, 0.37, 0.10) == pytest.approx(0.10 + software_delay)


@pytest.mark.parametrize(
  ("software_delay", "expected"),
  [(-1.0, 0.10 + MIN_SOFTWARE_DELAY), (2.0, 0.10 + MAX_SOFTWARE_DELAY)],
)
def test_fixed_delay_is_clamped_to_supported_range(software_delay, expected):
  params = FakeParams(False, software_delay)
  assert get_lat_delay(params, 0.37, 0.10) == pytest.approx(expected)


@pytest.mark.parametrize("software_delay", [float("nan"), float("inf"), None])
def test_invalid_fixed_delay_uses_default(software_delay):
  params = FakeParams(False, software_delay)
  assert get_lat_delay(params, 0.37, 0.10) == pytest.approx(0.30)


def test_lagd_toggle_caches_the_effective_delay(monkeypatch):
  params = FakeParams(False, MAX_SOFTWARE_DELAY)
  monkeypatch.setattr(lagd_toggle, "Params", lambda: params)
  toggle = lagd_toggle.LagdToggle(SimpleNamespace(steerActuatorDelay=0.10))
  msg = SimpleNamespace(lateralDelay=SimpleNamespace(lateralDelay=0.37))

  toggle.update(msg)
  assert toggle.lag == pytest.approx(1.10)
  assert msg.lateralDelay.lateralDelay == pytest.approx(1.10)
  assert params.writes["LagdValueCache"] == pytest.approx(1.10)

  params.values["LagdToggle"] = True
  msg.lateralDelay.lateralDelay = 0.37
  toggle.update(msg)
  assert toggle.lag == 0.37
  assert msg.lateralDelay.lateralDelay == 0.37
  assert params.writes["LagdValueCache"] == 0.37


def test_lagd_toggle_publishes_effective_delay_without_excess_cache_writes(monkeypatch):
  params = FakeParams(False, 0.5)
  monkeypatch.setattr(lagd_toggle, "Params", lambda: params)
  toggle = lagd_toggle.LagdToggle(SimpleNamespace(steerActuatorDelay=0.10))
  msg = SimpleNamespace(lateralDelay=SimpleNamespace(lateralDelay=0.37, lateralDelayEstimate=0.41))

  toggle.update(msg, cache=False)
  assert msg.lateralDelay.lateralDelay == pytest.approx(0.60)
  assert msg.lateralDelay.lateralDelayEstimate == pytest.approx(0.41)
  assert params.writes == {}


def test_lagd_selects_effective_delay_before_serializing_and_publishing():
  openpilot_root = Path(__file__).resolve().parents[2]
  source = (openpilot_root / "selfdrive/locationd/lagd.py").read_text(encoding="utf-8")
  selection = source.index("lagd_toggle.update(lag_msg, cache=sm.frame % 60 == 0)")
  serialization = source.index("lag_msg_dat = lag_msg.to_bytes()", selection)
  publication = source.index("pm.send('lateralDelay', lag_msg_dat)", serialization)
  assert selection < serialization < publication


def test_torque_history_covers_fixed_delay_range():
  assert LAT_DELAY_BUFFER_SECONDS >= MAX_SOFTWARE_DELAY + 0.5

  openpilot_root = Path(__file__).resolve().parents[2]
  for relative_path in (
    "selfdrive/controls/lib/latcontrol_torque.py",
    "sunnypilot/selfdrive/controls/lib/latcontrol_torque_v0.py",
  ):
    tree = ast.parse((openpilot_root / relative_path).read_text(encoding="utf-8"))
    assignments = [
      node for node in ast.walk(tree)
      if isinstance(node, ast.Assign)
      and any(isinstance(target, ast.Name) and target.id == "LAT_ACCEL_REQUEST_BUFFER_SECONDS" for target in node.targets)
    ]
    assert len(assignments) == 1
    assert isinstance(assignments[0].value, ast.Name)
    assert assignments[0].value.id == "LAT_DELAY_BUFFER_SECONDS"


def _calls_in_function(source_path: Path, function_name: str, call_name: str):
  tree = ast.parse(source_path.read_text(encoding="utf-8"))
  function = next(node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name)
  return [
    node for node in ast.walk(function)
    if isinstance(node, ast.Call)
    and ((isinstance(node.func, ast.Name) and node.func.id == call_name)
         or (isinstance(node.func, ast.Attribute) and node.func.attr == call_name))
  ]


def test_delay_consumers_resolve_startup_and_refresh_paths():
  openpilot_root = Path(__file__).resolve().parents[2]
  expected_calls = (
    ("selfdrive/modeld/modeld.py", "main", 2),
    ("sunnypilot/modeld_v2/modeld.py", "main", 2),
    ("selfdrive/locationd/torqued.py", "__init__", 1),
    ("selfdrive/locationd/torqued.py", "handle_log", 1),
    ("sunnypilot/selfdrive/controls/controlsd_ext.py", "__init__", 1),
    ("sunnypilot/selfdrive/controls/controlsd_ext.py", "get_params_sp", 1),
    ("sunnypilot/livedelay/lagd_toggle.py", "update", 1),
  )
  for relative_path, function_name, count in expected_calls:
    calls = _calls_in_function(openpilot_root / relative_path, function_name, "get_lat_delay")
    assert len(calls) == count, f"{relative_path}:{function_name} must resolve every expected delay path"
    assert all(len(call.args) == 3 for call in calls)


def test_fixed_and_learned_modes_switch_without_reusing_the_other_source():
  params = FakeParams(True, 0.8)
  assert get_lat_delay(params, 0.37, 0.10) == pytest.approx(0.37)

  params.values["LagdToggle"] = False
  assert get_lat_delay(params, 0.41, 0.10) == pytest.approx(0.90)

  params.values["LagdToggle"] = True
  assert get_lat_delay(params, 0.41, 0.10) == pytest.approx(0.41)


def test_controlsd_refreshes_each_published_lateral_delay():
  openpilot_root = Path(__file__).resolve().parents[2]
  controlsd_source = (openpilot_root / "selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
  assert 'if self.sm.updated["lateralDelay"]:' in controlsd_source
  assert 'get_lat_delay(self.params, self.sm["lateralDelay"].lateralDelay, self.CP.steerActuatorDelay)' in controlsd_source


def test_modeld_refreshes_each_published_lateral_delay():
  openpilot_root = Path(__file__).resolve().parents[2]
  for relative_path in ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"):
    source = (openpilot_root / relative_path).read_text(encoding="utf-8")
    assert 'if sm.updated["lateralDelay"]:' in source


def test_delay_setting_ranges_match_runtime():
  openpilot_root = Path(__file__).resolve().parents[2]
  native_source = (openpilot_root / "selfdrive/ui/sunnypilot/layouts/settings/models.py").read_text(encoding="utf-8")
  assert '"LagdToggleDelay", 5, 100,' in native_source

  schema = json.loads((openpilot_root / "sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))
  items = [item for panel in schema["panels"] for section in panel["sections"] for item in section.get("items", [])]
  delay = next(item for item in items if item.get("key") == "LagdToggleDelay")
  assert (delay["min"], delay["max"], delay["step"]) == (MIN_SOFTWARE_DELAY, MAX_SOFTWARE_DELAY, 0.01)
