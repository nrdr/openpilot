import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


HARDWARED_PATH = Path(__file__).parents[1] / "hardwared.py"
TIMING_CONSTANTS = {"SLOW_HARDWARE_STAGE_SECONDS", "SLOW_HARDWARE_STAGE_LOG_INTERVAL"}


def load_timing_helper():
  """Load only the timing helper so this test remains runnable on non-Linux hosts."""
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  selected_nodes = [
    node for node in tree.body
    if (
      isinstance(node, ast.Assign)
      and any(isinstance(target, ast.Name) and target.id in TIMING_CONSTANTS for target in node.targets)
    ) or (
      isinstance(node, ast.FunctionDef) and node.name == "log_slow_hardware_stage"
    )
  ]
  assert len(selected_nodes) == len(TIMING_CONSTANTS) + 1

  monotonic = Mock()
  event = Mock()
  namespace = {
    "time": SimpleNamespace(monotonic=monotonic),
    "cloudlog": SimpleNamespace(event=event),
  }
  helper_module = ast.fix_missing_locations(ast.Module(body=selected_nodes, type_ignores=[]))
  exec(compile(helper_module, str(HARDWARED_PATH), "exec"), namespace)
  return namespace["log_slow_hardware_stage"], monotonic, event


def test_slow_stage_threshold():
  log_slow_hardware_stage, monotonic, event = load_timing_helper()
  last_logged: dict[str, float] = {}
  monotonic.side_effect = [0.199, 0.20, 0.20, 0.21]
  next_stage = log_slow_hardware_stage(
    "main", "device_telemetry", 0.0, last_logged, True, 123,
  )

  assert next_stage == 0.20
  assert last_logged == {}
  event.assert_not_called()

  next_stage = log_slow_hardware_stage(
    "main", "device_telemetry", 0.0, last_logged, True, 124,
  )
  assert next_stage == 0.21
  assert last_logged == {"device_telemetry": 0.20}
  event.assert_called_once()


def test_slow_stage_event():
  log_slow_hardware_stage, monotonic, event = load_timing_helper()
  last_logged: dict[str, float] = {}
  monotonic.side_effect = [10.21, 10.22]
  next_stage = log_slow_hardware_stage(
    "main", "device_telemetry", 10.0, last_logged, True, 123,
  )

  assert next_stage == 10.22
  assert last_logged == {"device_telemetry": 10.21}
  event.assert_called_once()
  args, kwargs = event.call_args
  assert args == ("hardwared slow stage",)
  assert kwargs == {
    "thread": "main",
    "stage": "device_telemetry",
    "duration": pytest.approx(0.21),
    "onroad": True,
    "frame": 123,
    "error": True,
  }


def test_slow_stage_rate_limit_is_per_stage():
  log_slow_hardware_stage, monotonic, event = load_timing_helper()
  last_logged: dict[str, float] = {}
  monotonic.side_effect = [
    20.25, 20.26,
    25.50, 25.51,
    25.75, 25.76,
    31.00, 31.01,
  ]
  log_slow_hardware_stage("main", "device_telemetry", 20.0, last_logged, True, 200)
  log_slow_hardware_stage("main", "device_telemetry", 25.25, last_logged, True, 250)
  log_slow_hardware_stage("main", "startup_policy", 25.5, last_logged, True, 251)
  log_slow_hardware_stage("main", "device_telemetry", 30.75, last_logged, True, 310)

  assert event.call_count == 3
  assert [call.kwargs["stage"] for call in event.call_args_list] == [
    "device_telemetry", "startup_policy", "device_telemetry",
  ]


def test_slow_stage_call_sites_cover_each_synchronous_group():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  stages: dict[str, set[str]] = {}
  for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "log_slow_hardware_stage":
      continue
    thread, stage = (ast.literal_eval(node.args[index]) for index in (0, 1))
    stages.setdefault(thread, set()).add(stage)

  assert stages == {
    "main": {
      "panda_poll", "panda_state", "device_telemetry", "display_usb_chestnut", "thermal",
      "startup_policy", "engagement", "power", "publish", "post_publish",
    },
    "hw_state": {
      "usb_topology", "network_type", "modem_temperatures", "modem_data_usage", "network_info",
      "network_strength", "network_metered", "usb_state", "queue",
    },
  }
