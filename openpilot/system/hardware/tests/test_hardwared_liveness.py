import ast
from collections import namedtuple
import queue
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest


HARDWARED_PATH = Path(__file__).parents[1] / "hardwared.py"
POWER_MONITORING_PATH = Path(__file__).parents[1] / "power_monitoring.py"


def load_hardwared_subset(*names: str, namespace: dict | None = None):
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  selected = []
  found_names: set[str] = set()
  for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in names:
      selected.append(node)
      found_names.add(node.name)
    elif isinstance(node, ast.Assign):
      assignment_names = {target.id for target in node.targets if isinstance(target, ast.Name)}
      if assignment_names & set(names):
        selected.append(node)
        found_names.update(assignment_names & set(names))

  assert found_names == set(names)
  module_namespace = {"Params": object, "queue": queue, "namedtuple": namedtuple}
  if namespace is not None:
    module_namespace.update(namespace)
  module = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
  exec(compile(module, str(HARDWARED_PATH), "exec"), module_namespace)
  return tuple(module_namespace[name] for name in names)


def enclosing_calls(tree: ast.AST, call_names: set[str]):
  found: list[tuple[str, str, ast.Call]] = []

  class Visitor(ast.NodeVisitor):
    def __init__(self):
      self.function = "<module>"

    def visit_FunctionDef(self, node: ast.FunctionDef):
      previous = self.function
      self.function = node.name
      self.generic_visit(node)
      self.function = previous

    def visit_Call(self, node: ast.Call):
      if isinstance(node.func, ast.Attribute) and node.func.attr in call_names:
        found.append((self.function, node.func.attr, node))
      self.generic_visit(node)

  Visitor().visit(tree)
  return found


def telemetry_worker_namespace(hardware, params, cloudlog=None):
  if not hasattr(hardware, "get_gpu_usage_percent"):
    hardware.get_gpu_usage_percent = Mock(return_value=7.)
  system_stats = SimpleNamespace(
    memory_usage_percent=Mock(return_value=12.),
    cpu_usage_percent=Mock(return_value=[11., 22.]),
  )
  return {
    "HARDWARE": hardware,
    "Params": lambda: params,
    "LinuxSystemStats": lambda: system_stats,
    "get_available_percent": Mock(return_value=90.),
    "cloudlog": cloudlog or Mock(),
    "DT_HW": 0.01,
    "NONCRITICAL_TELEMETRY_ERROR_LOG_INTERVAL": 10.0,
    "time": time,
    "log_slow_hardware_stage": lambda _thread, _stage, stage_started, *_args: stage_started,
  }


def make_telemetry_state(state_type, current_power=0., som_power=0., last_ping=None):
  return state_type(90., 12, 7, [11, 22], current_power, som_power, last_ping)


def test_blocked_production_worker_cannot_block_main_cache_read():
  entered = threading.Event()
  release = threading.Event()

  def blocked_power_read():
    entered.set()
    assert release.wait(timeout=2.)
    return 4.2

  hardware = SimpleNamespace(
    get_current_power_draw=Mock(side_effect=blocked_power_read),
    get_som_power_draw=Mock(return_value=2.1),
  )
  params = SimpleNamespace(get=Mock(return_value=b"123"))
  namespace = telemetry_worker_namespace(hardware, params)
  NoncriticalTelemetryState, get_cached_hardware_state, _put_latest, worker_fn = load_hardwared_subset(
    "NoncriticalTelemetryState", "get_cached_hardware_state", "put_latest_cached_state",
    "noncritical_telemetry_thread",
    namespace=namespace,
  )

  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  cold_cache = make_telemetry_state(NoncriticalTelemetryState)
  end_event = threading.Event()
  worker = threading.Thread(target=worker_fn, args=(end_event, telemetry_queue), daemon=True)
  worker.start()
  assert entered.wait(timeout=1.)

  network_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  network_cache = object()
  network_queue.put_nowait(network_cache)
  started = time.monotonic()
  assert get_cached_hardware_state(network_queue, object()) is network_cache
  assert get_cached_hardware_state(telemetry_queue, cold_cache) is cold_cache
  assert time.monotonic() - started < 0.1
  assert worker.is_alive()

  end_event.set()
  join_started = time.monotonic()
  worker.join(timeout=0.02)
  assert time.monotonic() - join_started < 0.1
  assert worker.is_alive()
  release.set()
  worker.join(timeout=1.)
  assert not worker.is_alive()
  assert telemetry_queue.get_nowait() == make_telemetry_state(NoncriticalTelemetryState, 4.2, 2.1, b"123")


def test_telemetry_cache_default_and_stale_fallback():
  NoncriticalTelemetryState, get_cached_hardware_state = load_hardwared_subset(
    "NoncriticalTelemetryState", "get_cached_hardware_state",
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  cold_cache = make_telemetry_state(NoncriticalTelemetryState)

  assert get_cached_hardware_state(telemetry_queue, cold_cache) is cold_cache
  fresh = make_telemetry_state(NoncriticalTelemetryState, 5.1, 2.4, b"456")
  telemetry_queue.put_nowait(fresh)
  assert get_cached_hardware_state(telemetry_queue, cold_cache) is fresh
  assert get_cached_hardware_state(telemetry_queue, fresh) is fresh


def test_latest_cache_replaces_oldest_unconsumed_snapshot():
  NoncriticalTelemetryState, get_cached_hardware_state, put_latest_cached_state = load_hardwared_subset(
    "NoncriticalTelemetryState", "get_cached_hardware_state", "put_latest_cached_state",
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  oldest = make_telemetry_state(NoncriticalTelemetryState, 1., 1., b"old")
  latest = make_telemetry_state(NoncriticalTelemetryState, 2., 2., b"new")
  telemetry_queue.put_nowait(oldest)

  put_latest_cached_state(telemetry_queue, latest)

  assert get_cached_hardware_state(telemetry_queue, oldest) is latest
  assert telemetry_queue.empty()


def test_telemetry_worker_publishes_only_atomic_snapshots():
  entered = threading.Event()
  release = threading.Event()

  def blocked_som_read():
    entered.set()
    assert release.wait(timeout=2.)
    return 2.2

  hardware = SimpleNamespace(
    get_current_power_draw=Mock(return_value=4.4),
    get_som_power_draw=Mock(side_effect=blocked_som_read),
  )
  params = SimpleNamespace(get=Mock(return_value=b"789"))
  namespace = telemetry_worker_namespace(hardware, params)
  NoncriticalTelemetryState, _put_latest, worker_fn = load_hardwared_subset(
    "NoncriticalTelemetryState", "put_latest_cached_state", "noncritical_telemetry_thread", namespace=namespace,
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  end_event = threading.Event()
  worker = threading.Thread(target=worker_fn, args=(end_event, telemetry_queue), daemon=True)
  worker.start()
  assert entered.wait(timeout=1.)

  assert telemetry_queue.empty()
  end_event.set()
  release.set()
  worker.join(timeout=1.)
  assert not worker.is_alive()
  assert telemetry_queue.get_nowait() == make_telemetry_state(NoncriticalTelemetryState, 4.4, 2.2, b"789")


def test_telemetry_worker_read_error_preserves_stale_cache():
  attempted = threading.Event()

  def failed_read():
    attempted.set()
    raise OSError("power sysfs unavailable")

  hardware = SimpleNamespace(
    get_current_power_draw=Mock(side_effect=failed_read),
    get_som_power_draw=Mock(),
  )
  params = SimpleNamespace(get=Mock())
  cloudlog = Mock()
  namespace = telemetry_worker_namespace(hardware, params, cloudlog)
  NoncriticalTelemetryState, get_cached_hardware_state, _put_latest, worker_fn = load_hardwared_subset(
    "NoncriticalTelemetryState", "get_cached_hardware_state", "put_latest_cached_state",
    "noncritical_telemetry_thread",
    namespace=namespace,
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  stale_cache = make_telemetry_state(NoncriticalTelemetryState, 3.3, 1.8, b"old")
  end_event = threading.Event()

  worker = threading.Thread(target=worker_fn, args=(end_event, telemetry_queue), daemon=True)
  worker.start()
  assert attempted.wait(timeout=1.)
  time.sleep(0.03)

  assert worker.is_alive()
  assert not end_event.is_set()
  assert get_cached_hardware_state(telemetry_queue, stale_cache) is stale_cache
  end_event.set()
  worker.join(timeout=1.)

  assert not worker.is_alive()
  hardware.get_som_power_draw.assert_not_called()
  params.get.assert_not_called()
  cloudlog.exception.assert_called_once_with("Error getting noncritical telemetry")


def test_telemetry_worker_survives_diagnostic_logger_error():
  attempted = threading.Event()

  def failed_read():
    attempted.set()
    raise OSError("power sysfs unavailable")

  hardware = SimpleNamespace(
    get_current_power_draw=Mock(side_effect=failed_read),
    get_som_power_draw=Mock(),
  )
  params = SimpleNamespace(get=Mock())
  cloudlog = Mock()
  cloudlog.exception.side_effect = RuntimeError("logger unavailable")
  namespace = telemetry_worker_namespace(hardware, params, cloudlog)
  _put_latest, worker_fn = load_hardwared_subset(
    "put_latest_cached_state", "noncritical_telemetry_thread", namespace=namespace,
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  end_event = threading.Event()

  worker = threading.Thread(target=worker_fn, args=(end_event, telemetry_queue), daemon=True)
  worker.start()
  assert attempted.wait(timeout=1.)
  time.sleep(0.03)

  assert worker.is_alive()
  assert not end_event.is_set()
  end_event.set()
  worker.join(timeout=1.)

  assert not worker.is_alive()
  assert telemetry_queue.empty()
  cloudlog.exception.assert_called_once()


def test_telemetry_worker_retries_params_constructor_without_stopping_critical_loop():
  attempted = threading.Event()
  constructor = Mock()

  def failed_params_constructor():
    attempted.set()
    raise OSError("params unavailable")

  constructor.side_effect = failed_params_constructor
  hardware = SimpleNamespace(
    get_current_power_draw=Mock(),
    get_som_power_draw=Mock(),
  )
  cloudlog = Mock()
  namespace = telemetry_worker_namespace(hardware, SimpleNamespace(), cloudlog)
  namespace["Params"] = constructor
  _put_latest, worker_fn = load_hardwared_subset(
    "put_latest_cached_state", "noncritical_telemetry_thread", namespace=namespace,
  )
  telemetry_queue: queue.Queue[object] = queue.Queue(maxsize=1)
  end_event = threading.Event()

  worker = threading.Thread(target=worker_fn, args=(end_event, telemetry_queue), daemon=True)
  worker.start()
  assert attempted.wait(timeout=1.)
  time.sleep(0.03)

  assert worker.is_alive()
  assert not end_event.is_set()
  assert constructor.call_count >= 2
  assert telemetry_queue.empty()
  hardware.get_current_power_draw.assert_not_called()
  cloudlog.exception.assert_called_once_with("Error getting noncritical telemetry")

  end_event.set()
  worker.join(timeout=1.)
  assert not worker.is_alive()


def test_github_runner_voltage_param_is_written_on_edges_only():
  (put_bool_on_edge,) = load_hardwared_subset("put_bool_on_edge")
  params = Mock()
  previous = None

  for value in (False, False, True, True, False):
    previous = put_bool_on_edge(params, "GithubRunnerSufficientVoltage", value, previous)

  assert previous is False
  assert params.put_bool.call_args_list == [
    call("GithubRunnerSufficientVoltage", False),
    call("GithubRunnerSufficientVoltage", True),
    call("GithubRunnerSufficientVoltage", False),
  ]


def test_hidden_offroad_alert_ignores_changing_extra_text():
  setter = Mock()
  previous_states: dict[str, tuple[bool, str | None]] = {}
  namespace = {"prev_offroad_states": previous_states, "set_offroad_alert": setter}
  (set_offroad_alert_if_changed,) = load_hardwared_subset("set_offroad_alert_if_changed", namespace=namespace)

  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", False, "40.0C")
  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", False, "40.1C")
  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", True, "85.0C")
  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", True, "85.1C")
  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", False, "40.2C")
  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", False, "40.3C")

  assert setter.call_args_list == [
    call("Offroad_TemperatureTooHigh", False, None),
    call("Offroad_TemperatureTooHigh", True, "85.0C"),
    call("Offroad_TemperatureTooHigh", True, "85.1C"),
    call("Offroad_TemperatureTooHigh", False, None),
  ]
  assert previous_states == {"Offroad_TemperatureTooHigh": (False, None)}


def test_offroad_alert_write_failure_is_retried():
  setter = Mock(side_effect=[OSError("params write failed"), None])
  previous_states: dict[str, tuple[bool, str | None]] = {}
  namespace = {"prev_offroad_states": previous_states, "set_offroad_alert": setter}
  (set_offroad_alert_if_changed,) = load_hardwared_subset("set_offroad_alert_if_changed", namespace=namespace)

  with pytest.raises(OSError, match="params write failed"):
    set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", True, "90.0C")
  assert previous_states == {}

  set_offroad_alert_if_changed("Offroad_TemperatureTooHigh", True, "90.0C")
  assert setter.call_count == 2
  assert previous_states == {"Offroad_TemperatureTooHigh": (True, "90.0C")}


def test_noncritical_reads_are_owned_only_by_dedicated_worker():
  hardwared_tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  hardware_calls = enclosing_calls(
    hardwared_tree,
    {"memory_usage_percent", "get_gpu_usage_percent", "cpu_usage_percent", "get_current_power_draw", "get_som_power_draw"},
  )
  assert [(owner, name) for owner, name, _ in hardware_calls] == [
    ("noncritical_telemetry_thread", "memory_usage_percent"),
    ("noncritical_telemetry_thread", "get_gpu_usage_percent"),
    ("noncritical_telemetry_thread", "cpu_usage_percent"),
    ("noncritical_telemetry_thread", "get_current_power_draw"),
    ("noncritical_telemetry_thread", "get_som_power_draw"),
  ]

  last_ping_reads = []
  for owner, name, node in enclosing_calls(hardwared_tree, {"get"}):
    if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "LastAthenaPingTime":
      last_ping_reads.append((owner, name))
  assert last_ping_reads == [("noncritical_telemetry_thread", "get")]

  power_tree = ast.parse(POWER_MONITORING_PATH.read_text(encoding="utf-8"), filename=str(POWER_MONITORING_PATH))
  power_calls = enclosing_calls(power_tree, {"get_current_power_draw", "get_som_power_draw"})
  assert [(owner, name) for owner, name, _ in power_calls] == [("calculate", "get_current_power_draw")]


def test_main_consumes_noncritical_values_only_from_cache():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  hardware_thread = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hardware_thread")

  cached_attributes = {
    node.attr for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "last_telemetry_state"
  }
  assert cached_attributes == {
    "free_space_percent", "memory_usage_percent", "gpu_usage_percent", "cpu_usage_percent",
    "current_power_draw", "som_power_draw", "last_athena_ping_time",
  }

  cache_reads = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "get_cached_hardware_state"
  ]
  assert len(cache_reads) == 2

  calculate_calls = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "calculate"
  ]
  assert len(calculate_calls) == 1
  assert len(calculate_calls[0].args) == 2

  forbidden_onroad_reads = enclosing_calls(
    hardware_thread,
    {"memory_usage_percent", "get_gpu_usage_percent", "cpu_usage_percent", "get_current_power_draw", "get_som_power_draw"},
  )
  assert forbidden_onroad_reads == []

  free_space_calls = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "get_available_percent"
  ]
  assert len(free_space_calls) == 1
  free_space_if = next(
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.If) and free_space_calls[0] in list(ast.walk(node))
  )
  assert isinstance(free_space_if.test, ast.Compare)
  assert isinstance(free_space_if.test.left, ast.Name) and free_space_if.test.left.id == "started_ts"
  assert len(free_space_if.test.ops) == 1 and isinstance(free_space_if.test.ops[0], ast.Is)
  assert isinstance(free_space_if.test.comparators[0], ast.Constant)
  assert free_space_if.test.comparators[0].value is None


def test_noncritical_cache_has_safe_cold_defaults():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  assignment = next(
    node for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "NoncriticalTelemetryState" for target in node.targets)
  )
  assert isinstance(assignment.value, ast.Call)
  assert ast.literal_eval(assignment.value.args[1]) == [
    "free_space_percent", "memory_usage_percent", "gpu_usage_percent", "cpu_usage_percent",
    "current_power_draw", "som_power_draw", "last_athena_ping_time",
  ]

  hardware_thread = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hardware_thread")
  state_calls = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NoncriticalTelemetryState"
  ]
  assert len(state_calls) == 1
  defaults = {keyword.arg: ast.literal_eval(keyword.value) for keyword in state_calls[0].keywords}
  assert defaults == {
    "free_space_percent": 100.,
    "memory_usage_percent": 0,
    "gpu_usage_percent": 0,
    "cpu_usage_percent": [],
    "current_power_draw": 0.,
    "som_power_draw": 0.,
    "last_athena_ping_time": None,
  }


def test_worker_call_order_builds_snapshot_after_every_read():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  worker = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "noncritical_telemetry_thread"
  )

  call_lines = {}
  for node in ast.walk(worker):
    if not isinstance(node, ast.Call):
      continue
    if isinstance(node.func, ast.Name) and node.func.id == "get_available_percent":
      call_lines["get_available_percent"] = [node.lineno]
    if isinstance(node.func, ast.Attribute) and node.func.attr in {
      "memory_usage_percent", "get_gpu_usage_percent", "cpu_usage_percent",
      "get_current_power_draw", "get_som_power_draw", "get",
    }:
      if node.func.attr != "get" or (
        node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "LastAthenaPingTime"
      ):
        call_lines.setdefault(node.func.attr, []).append(node.lineno)

  snapshot_line = next(
    node.lineno for node in ast.walk(worker)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NoncriticalTelemetryState"
  )
  ordered_reads = [
    "get_available_percent", "memory_usage_percent", "get_gpu_usage_percent", "cpu_usage_percent",
    "get_current_power_draw", "get_som_power_draw", "get",
  ]
  assert [call_lines[name][0] for name in ordered_reads] == sorted(call_lines[name][0] for name in ordered_reads)
  assert call_lines["get_som_power_draw"][0] < call_lines["get"][0]
  publish_line = next(
    node.lineno for node in ast.walk(worker)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "put_latest_cached_state"
  )
  assert call_lines["get"][0] < snapshot_line < publish_line


def test_startup_reads_pause_onroad_and_refresh_mutable_conditions_after_stop():
  values = {
    "Offroad_ConnectivityNeeded": b"needed",
    "DisableUpdates": False,
    "SnoozeUpdate": True,
    "Offroad_ExcessiveActuation": None,
    "DoUninstall": False,
    "HasAcceptedTerms": b"terms",
    "HasAcceptedTermsSP": b"terms-sp",
    "CompletedTrainingVersion": b"training",
    "IsDriverViewEnabled": False,
  }

  class RecordingParams:
    def __init__(self):
      self.calls: list[tuple[str, str]] = []

    def get(self, key):
      self.calls.append(("get", key))
      return values[key]

    def get_bool(self, key):
      self.calls.append(("get_bool", key))
      return values[key]

  params = RecordingParams()
  hardware = SimpleNamespace(booted=Mock(return_value=True))
  startup_policy = Mock()
  timing = Mock(side_effect=lambda _thread, _stage, stage_started, *_args: stage_started + 1.)
  namespace = {
    "HARDWARE": hardware,
    "apply_startup_policy": startup_policy,
    "log_slow_hardware_stage": timing,
    "terms_version": b"terms",
    "terms_version_sp": b"terms-sp",
    "training_version": b"training",
  }
  (refresh_startup_conditions,) = load_hardwared_subset("refresh_startup_conditions", namespace=namespace)
  startup_conditions: dict[str, bool] = {}

  stage_started = refresh_startup_conditions(None, params, startup_conditions, 10., {}, 1)
  expected_first_calls = [
    ("get", "Offroad_ConnectivityNeeded"),
    ("get_bool", "DisableUpdates"),
    ("get_bool", "SnoozeUpdate"),
    ("get", "Offroad_ExcessiveActuation"),
    ("get_bool", "DoUninstall"),
    ("get", "HasAcceptedTerms"),
    ("get", "HasAcceptedTermsSP"),
    ("get", "CompletedTrainingVersion"),
    ("get_bool", "IsDriverViewEnabled"),
  ]
  assert params.calls == expected_first_calls
  assert startup_conditions == {
    "up_to_date": True,
    "no_excessive_actuation": True,
    "not_uninstalling": True,
    "accepted_terms": True,
    "accepted_terms_sp": True,
    "completed_training": True,
    "not_driver_view": True,
    "device_booted": True,
  }
  assert stage_started == 21.
  startup_policy.assert_called_once_with(startup_conditions)
  hardware.booted.assert_called_once()

  values.update({
    "SnoozeUpdate": False,
    "Offroad_ExcessiveActuation": b"fault",
    "DoUninstall": True,
    "HasAcceptedTerms": b"old",
    "HasAcceptedTermsSP": b"old",
    "CompletedTrainingVersion": b"old",
    "IsDriverViewEnabled": True,
  })
  assert refresh_startup_conditions(100., params, startup_conditions, stage_started, {}, 2) == stage_started
  assert params.calls == expected_first_calls
  startup_policy.assert_called_once()
  hardware.booted.assert_called_once()

  stage_started = refresh_startup_conditions(None, params, startup_conditions, stage_started, {}, 3)
  assert params.calls == expected_first_calls * 2
  assert startup_conditions == {
    "up_to_date": False,
    "no_excessive_actuation": False,
    "not_uninstalling": False,
    "accepted_terms": False,
    "accepted_terms_sp": False,
    "completed_training": False,
    "not_driver_view": False,
    "device_booted": True,
  }
  assert stage_started == 32.
  assert startup_policy.call_count == 2
  # Device boot completion is monotonic for a hardwared process. Once latched,
  # avoid repeating its subprocess-backed probe while still refreshing every
  # mutable startup condition after returning offroad.
  hardware.booted.assert_called_once()


def test_startup_read_ownership_and_refresh_precedes_restart_decision():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  startup_keys = {
    "Offroad_ConnectivityNeeded", "DisableUpdates", "SnoozeUpdate", "Offroad_ExcessiveActuation",
    "DoUninstall", "HasAcceptedTerms", "HasAcceptedTermsSP", "CompletedTrainingVersion",
    "IsDriverViewEnabled",
  }
  found = []
  for owner, name, node in enclosing_calls(tree, {"get", "get_bool"}):
    if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in startup_keys:
      found.append((owner, name, node.args[0].value))
  assert {owner for owner, _name, _key in found} == {"refresh_startup_conditions"}
  assert {key for _owner, _name, key in found} == startup_keys

  hardware_thread = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hardware_thread")
  loop = next(node for node in hardware_thread.body if isinstance(node, ast.While))
  refresh_call = next(
    node for node in ast.walk(loop)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "refresh_startup_conditions"
  )
  should_start_assignment = next(
    node for node in ast.walk(loop)
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "should_start" for target in node.targets)
  )
  assert refresh_call.lineno < should_start_assignment.lineno
  assert isinstance(should_start_assignment.value, ast.Call)
  assert isinstance(should_start_assignment.value.func, ast.Name)
  assert should_start_assignment.value.func.id == "all"

  state_transition = next(
    node for node in ast.walk(loop)
    if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "should_start"
  )
  assert any(
    isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "started_ts" for target in node.targets)
    and isinstance(node.value, ast.Constant) and node.value.value is None
    for statement in state_transition.orelse for node in ast.walk(statement)
  )

  every_loop_param_reads = {
    node.args[0].value for node in ast.walk(loop)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    and node.func.attr in {"get", "get_bool"} and node.args
    and isinstance(node.args[0], ast.Constant) and node.args[0].value in {"OffroadMode", "OnroadCycleRequested"}
  }
  assert every_loop_param_reads == {"OffroadMode", "OnroadCycleRequested"}

  condition_keys = {
    node.slice.value for node in ast.walk(loop)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
    and node.value.id == "startup_conditions" and isinstance(node.slice, ast.Constant)
  }
  assert {"free_space", "device_temp_engageable", "not_always_offroad", "not_tici"} <= condition_keys

  onroad_condition_keys = {
    node.slice.value for node in ast.walk(loop)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
    and node.value.id == "onroad_conditions" and isinstance(node.slice, ast.Constant)
  }
  assert {"ignition", "not_onroad_cycle", "device_temp_good"} <= onroad_condition_keys


def test_build_metadata_is_cached_once_before_main_loop():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  hardware_thread = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hardware_thread")
  calls = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "get_build_metadata"
  ]
  loop = next(node for node in hardware_thread.body if isinstance(node, ast.While))
  assert len(calls) == 1
  assert calls[0].lineno < loop.lineno


def test_tici_offroad_alert_is_edge_gated():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  hardware_thread = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hardware_thread")
  calls = [
    node for node in ast.walk(hardware_thread)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.args
    and isinstance(node.args[0], ast.Constant) and node.args[0].value == "Offroad_TiciSupport"
  ]
  assert len(calls) == 1
  assert calls[0].func.id == "set_offroad_alert_if_changed"


def test_main_wires_independent_hardware_and_telemetry_workers():
  tree = ast.parse(HARDWARED_PATH.read_text(encoding="utf-8"), filename=str(HARDWARED_PATH))
  main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
  thread_targets = []
  for node in ast.walk(main):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "Thread":
      continue
    target = next((kw.value for kw in node.keywords if kw.arg == "target"), None)
    args = next((kw.value for kw in node.keywords if kw.arg == "args"), None)
    if isinstance(target, ast.Name) and isinstance(args, ast.Tuple):
      thread_targets.append((target.id, [elt.id for elt in args.elts if isinstance(elt, ast.Name)]))

  assert ("hw_state_thread", ["end_event", "hw_queue"]) in thread_targets
  assert ("noncritical_telemetry_thread", ["end_event", "telemetry_queue"]) in thread_targets
  assert ("hardware_thread", ["end_event", "hw_queue", "telemetry_queue"]) in thread_targets

  telemetry_assignment = next(
    node for node in main.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "telemetry_thread" for target in node.targets)
  )
  assert isinstance(telemetry_assignment.value, ast.Call)
  daemon = next(keyword.value for keyword in telemetry_assignment.value.keywords if keyword.arg == "daemon")
  assert isinstance(daemon, ast.Constant) and daemon.value is True

  critical_assignment = next(
    node for node in main.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "threads" for target in node.targets)
  )
  assert isinstance(critical_assignment.value, ast.List)
  assert not any(
    isinstance(node, ast.Name) and node.id == "noncritical_telemetry_thread"
    for node in ast.walk(critical_assignment.value)
  )

  liveness_all = next(
    node for node in ast.walk(main)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "all"
  )
  assert isinstance(liveness_all.args[0], ast.GeneratorExp)
  assert isinstance(liveness_all.args[0].generators[0].iter, ast.Name)
  assert liveness_all.args[0].generators[0].iter.id == "threads"

  telemetry_joins = [
    node for node in ast.walk(main)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join"
    and isinstance(node.func.value, ast.Name) and node.func.value.id == "telemetry_thread"
  ]
  assert len(telemetry_joins) == 1
  timeout = next(keyword.value for keyword in telemetry_joins[0].keywords if keyword.arg == "timeout")
  assert isinstance(timeout, ast.Name) and timeout.id == "DT_HW"
