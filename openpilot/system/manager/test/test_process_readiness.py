#!/usr/bin/env python3

import unittest
from unittest import mock

import openpilot.system.manager.process as process_module
from openpilot.system.manager.process import PythonProcess, launcher


def always_run(*_args) -> bool:
  return True


class FakeProcess:
  def __init__(self, alive: bool, exitcode: int | None = None):
    self.alive = alive
    self.exitcode = exitcode
    self.pid = 123

  def is_alive(self) -> bool:
    return self.alive


class TestProcessReadiness(unittest.TestCase):
  def make_process(self, *, wait_for_ready: bool = True) -> PythonProcess:
    process = PythonProcess("testd", "openpilot.system.testd", always_run, wait_for_ready=wait_for_ready)
    process.shutting_down = False
    return process

  def test_alive_process_is_unhealthy_until_ready(self) -> None:
    process = self.make_process()
    process.proc = FakeProcess(alive=True)

    self.assertFalse(process.is_healthy())
    state = process.get_process_state_msg()
    self.assertFalse(state.running)
    self.assertTrue(state.shouldBeRunning)

  def test_alive_process_is_healthy_when_ready(self) -> None:
    process = self.make_process()
    process.proc = FakeProcess(alive=True)
    self.assertIsNotNone(process.ready_event)
    process.ready_event.set()

    self.assertTrue(process.is_healthy())
    state = process.get_process_state_msg()
    self.assertTrue(state.running)
    self.assertTrue(state.shouldBeRunning)

  def test_dead_process_is_unhealthy_with_stale_readiness(self) -> None:
    process = self.make_process()
    dead_process = FakeProcess(alive=False, exitcode=17)
    process.proc = dead_process
    self.assertIsNotNone(process.ready_event)
    process.ready_event.set()

    self.assertFalse(process.is_healthy())
    state = process.get_process_state_msg()
    self.assertFalse(state.running)
    self.assertTrue(state.shouldBeRunning)
    self.assertEqual(state.exitCode, 17)

    with mock.patch.object(process_module, "Process") as process_factory:
      process.start()
    process_factory.assert_not_called()
    self.assertIs(process.proc, dead_process)

  def test_start_clears_readiness_and_passes_event_to_launcher(self) -> None:
    process = self.make_process()
    self.assertIsNotNone(process.ready_event)
    process.ready_event.set()

    child = mock.Mock()
    with mock.patch.object(process_module, "Process", return_value=child) as process_factory:
      process.start()

    self.assertFalse(process.ready_event.is_set())
    process_factory.assert_called_once_with(
      name=process.name,
      target=process.launcher,
      args=(process.module, process.name, process.ready_event),
    )
    child.start.assert_called_once_with()

  def test_non_gated_process_preserves_liveness_behavior(self) -> None:
    process = self.make_process(wait_for_ready=False)
    process.proc = FakeProcess(alive=True)

    self.assertIsNone(process.ready_event)
    self.assertTrue(process.is_healthy())
    self.assertTrue(process.get_process_state_msg().running)

  def test_non_gated_start_preserves_launcher_arguments(self) -> None:
    process = self.make_process(wait_for_ready=False)
    child = mock.Mock()
    with mock.patch.object(process_module, "Process", return_value=child) as process_factory:
      process.start()

    process_factory.assert_called_once_with(
      name=process.name,
      target=process.launcher,
      args=(process.module, process.name),
    )
    child.start.assert_called_once_with()

  def test_launcher_passes_readiness_event_only_when_present(self) -> None:
    module = mock.Mock()
    ready_event = mock.Mock()
    with (
      mock.patch.object(process_module.importlib, "import_module", return_value=module),
      mock.patch.object(process_module, "setproctitle"),
      mock.patch.object(process_module.messaging, "reset_context"),
      mock.patch.object(process_module.cloudlog, "bind"),
      mock.patch.object(process_module.sentry, "set_tag"),
    ):
      launcher("openpilot.system.testd", "testd", ready_event)
      module.main.assert_called_once_with(ready_event)
      ready_event.clear.assert_called_once_with()

      module.main.reset_mock()
      launcher("openpilot.system.testd", "testd")
      module.main.assert_called_once_with()

  def test_launcher_clears_readiness_after_exception_and_reraises(self) -> None:
    error = RuntimeError("process failed")
    module = mock.Mock()
    module.main.side_effect = error
    ready_event = mock.Mock()
    with (
      mock.patch.object(process_module.importlib, "import_module", return_value=module),
      mock.patch.object(process_module, "setproctitle"),
      mock.patch.object(process_module.messaging, "reset_context"),
      mock.patch.object(process_module.cloudlog, "bind"),
      mock.patch.object(process_module.sentry, "set_tag"),
      mock.patch.object(process_module.sentry, "capture_exception") as capture_exception,
      self.assertRaises(RuntimeError) as raised,
    ):
      launcher("openpilot.system.testd", "testd", ready_event)

    self.assertIs(raised.exception, error)
    capture_exception.assert_called_once_with()
    ready_event.clear.assert_called_once_with()

  def test_launcher_clears_readiness_after_keyboard_interrupt(self) -> None:
    module = mock.Mock()
    module.main.side_effect = KeyboardInterrupt
    ready_event = mock.Mock()
    with (
      mock.patch.object(process_module.importlib, "import_module", return_value=module),
      mock.patch.object(process_module, "setproctitle"),
      mock.patch.object(process_module.messaging, "reset_context"),
      mock.patch.object(process_module.cloudlog, "bind"),
      mock.patch.object(process_module.cloudlog, "warning") as warning,
      mock.patch.object(process_module.sentry, "set_tag"),
      mock.patch.object(process_module.sentry, "capture_exception") as capture_exception,
    ):
      launcher("openpilot.system.testd", "testd", ready_event)

    warning.assert_called_once_with("child openpilot.system.testd got SIGINT")
    capture_exception.assert_not_called()
    ready_event.clear.assert_called_once_with()


if __name__ == "__main__":
  unittest.main()
