from collections.abc import Callable
import importlib
import sys
from typing import Any
import unittest
from unittest.mock import Mock, call, patch

from openpilot.system import audio


class FakeClock:
  def __init__(self) -> None:
    self.now = 0.0

  def monotonic(self) -> float:
    return self.now

  def sleep(self, seconds: float) -> None:
    self.now += seconds


class FakeReadyEvent:
  def __init__(self, clock: FakeClock) -> None:
    self.clock = clock
    self.ready = False
    self.set_calls = 0

  def is_set(self) -> bool:
    return self.ready

  def set(self) -> None:
    self.set_calls += 1
    self.ready = True

  def wait(self, timeout: float) -> bool:
    self.clock.sleep(timeout)
    return self.ready


class FakeStream:
  def __init__(self, start_error: Exception | None = None, stop_error: Exception | None = None,
               active_after_start: bool = True, invoke_callback: bool = True) -> None:
    self.start_error = start_error
    self.stop_error = stop_error
    self.active_after_start = active_after_start
    self.invoke_callback = invoke_callback
    self.callback: Callable[..., Any] | None = None
    self.active = False
    self.operations: list[str] = []

  def start(self) -> None:
    self.operations.append("start")
    if self.start_error is not None:
      raise self.start_error
    self.active = self.active_after_start
    if self.invoke_callback and self.callback is not None:
      self.callback()

  def stop(self) -> None:
    self.operations.append("stop")
    if self.stop_error is not None:
      raise self.stop_error
    self.active = False

  def close(self) -> None:
    self.operations.append("close")
    self.active = False


class FakeSoundDevice:
  def __init__(self) -> None:
    self.terminate_calls = 0
    self.initialize_calls = 0

  def _terminate(self) -> None:
    self.terminate_calls += 1

  def _initialize(self) -> None:
    self.initialize_calls += 1


def stream_factory(results: list[FakeStream | Exception]) -> Callable[[Callable[..., Any]], FakeStream]:
  pending = iter(results)

  def create_stream(callback: Callable[..., Any]) -> FakeStream:
    result = next(pending)
    if isinstance(result, Exception):
      raise result
    result.callback = callback
    return result

  return create_stream


def event_factory(clock: FakeClock) -> Callable[[], FakeReadyEvent]:
  return lambda: FakeReadyEvent(clock)


class TestAudioStartup(unittest.TestCase):
  def test_retries_until_late_success_within_deadline(self) -> None:
    clock = FakeClock()
    errors = [RuntimeError(f"PortAudio unavailable {i}") for i in range(5)]
    failed_streams = [FakeStream(error) for error in errors]
    ready_stream = FakeStream()
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception") as log_exception, patch.object(audio.cloudlog, "warning") as log_warning:
      with audio.open_audio_stream(sd, stream_factory([*failed_streams, ready_stream]), lambda: None, "micd",
                                   startup_timeout=90.0, retry_interval=15.0,
                                   monotonic=clock.monotonic, sleep=clock.sleep,
                                   readiness_event_factory=event_factory(clock)) as stream:
        self.assertIs(stream, ready_stream)
        self.assertEqual(clock.now, 75.0)

    self.assertEqual(sd.terminate_calls, 6)
    self.assertTrue(all(stream.operations == ["start", "close"] for stream in failed_streams))
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])
    self.assertEqual(repr(errors[0]), log_exception.call_args.args[0].split(": ", 1)[1])
    self.assertEqual([repr(error) for error in errors[1:]], [call.args[0].split(": ", 1)[1] for call in log_warning.call_args_list])

  def test_retries_construction_and_cleans_partial_stream(self) -> None:
    clock = FakeClock()
    construction_error = RuntimeError("construction failed")
    partial_stream = FakeStream(RuntimeError("start failed"))
    ready_stream = FakeStream()
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception") as log_exception, patch.object(audio.cloudlog, "warning") as log_warning:
      with audio.open_audio_stream(sd, stream_factory([construction_error, partial_stream, ready_stream]), lambda: None, "soundd",
                                   startup_timeout=10.0, retry_interval=1.0,
                                   monotonic=clock.monotonic, sleep=clock.sleep,
                                   readiness_event_factory=event_factory(clock)):
        pass

    self.assertEqual(partial_stream.operations, ["start", "close"])
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])
    self.assertEqual(sd.terminate_calls, 3)
    self.assertEqual(sd.initialize_calls, 3)
    self.assertEqual(log_exception.call_count, 1)
    self.assertEqual(log_warning.call_count, 1)

  def test_active_stream_without_callback_is_closed_and_retried(self) -> None:
    clock = FakeClock()
    no_callback_stream = FakeStream(invoke_callback=False)
    ready_stream = FakeStream()
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception") as log_exception:
      with audio.open_audio_stream(sd, stream_factory([no_callback_stream, ready_stream]), lambda: None, "micd",
                                   startup_timeout=10.0, retry_interval=1.0, callback_timeout=1.0,
                                   readiness_poll_interval=0.25, monotonic=clock.monotonic, sleep=clock.sleep,
                                   readiness_event_factory=event_factory(clock)):
        pass

    self.assertEqual(no_callback_stream.operations, ["start", "close"])
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])
    self.assertEqual(clock.now, 2.0)
    self.assertIn("did not receive its first callback", log_exception.call_args.args[0])

  def test_callback_must_complete_before_stream_is_ready(self) -> None:
    clock = FakeClock()
    callback_error = RuntimeError("callback failed")
    failed_stream = FakeStream()
    ready_stream = FakeStream()
    callback = Mock(side_effect=[callback_error, None])
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception"):
      with audio.open_audio_stream(sd, stream_factory([failed_stream, ready_stream]), callback, "soundd",
                                   startup_timeout=10.0, retry_interval=1.0,
                                   monotonic=clock.monotonic, sleep=clock.sleep,
                                   readiness_event_factory=event_factory(clock)):
        pass

    self.assertEqual(callback.call_count, 2)
    self.assertEqual(failed_stream.operations, ["start", "close"])
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])

  def test_late_callback_from_failed_stream_cannot_mark_next_stream_ready(self) -> None:
    clock = FakeClock()
    first_stream = FakeStream(invoke_callback=False)
    second_stream = FakeStream(invoke_callback=False)
    ready_stream = FakeStream()
    sd = FakeSoundDevice()

    def sleep_with_stale_callback(seconds: float) -> None:
      clock.sleep(seconds)
      if first_stream.callback is not None:
        first_stream.callback()

    with patch.object(audio.cloudlog, "exception"), patch.object(audio.cloudlog, "warning"):
      with audio.open_audio_stream(sd, stream_factory([first_stream, second_stream, ready_stream]), lambda: None, "micd",
                                   startup_timeout=10.0, retry_interval=1.0, callback_timeout=1.0,
                                   readiness_poll_interval=0.25, monotonic=clock.monotonic, sleep=sleep_with_stale_callback,
                                   readiness_event_factory=event_factory(clock)):
        pass

    self.assertEqual(first_stream.operations, ["start", "close"])
    self.assertEqual(second_stream.operations, ["start", "close"])
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])

  def test_recurring_callbacks_only_signal_readiness_once(self) -> None:
    clock = FakeClock()
    ready_stream = FakeStream()
    callback = Mock()
    sd = FakeSoundDevice()
    readiness_events: list[FakeReadyEvent] = []

    def readiness_event_factory() -> FakeReadyEvent:
      event = FakeReadyEvent(clock)
      readiness_events.append(event)
      return event

    with audio.open_audio_stream(sd, stream_factory([ready_stream]), callback, "soundd",
                                 monotonic=clock.monotonic, sleep=clock.sleep,
                                 readiness_event_factory=readiness_event_factory):
      self.assertIsNotNone(ready_stream.callback)
      ready_stream.callback()

    self.assertEqual(callback.call_count, 2)
    self.assertEqual(readiness_events[0].set_calls, 1)

  def test_shared_process_readiness_is_not_set_before_callback_success(self) -> None:
    clock = FakeClock()
    callback = Mock()
    shared_ready = FakeReadyEvent(clock)
    ready_stream = FakeStream()
    sd = FakeSoundDevice()

    with audio.open_audio_stream(sd, stream_factory([ready_stream]), callback, "micd",
                                 monotonic=clock.monotonic, sleep=clock.sleep,
                                 readiness_event_factory=event_factory(clock)):
      callback.assert_called_once_with()
      self.assertFalse(shared_ready.is_set())
      shared_ready.set()  # Mirrors micd_thread/soundd_thread immediately after this yield.

    self.assertTrue(shared_ready.is_set())

  def test_exhaustion_raises_and_logs_original_portaudio_error(self) -> None:
    clock = FakeClock()
    errors = [RuntimeError(f"original PortAudio error {i}") for i in range(3)]
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "warning") as log_warning, patch.object(audio.cloudlog, "exception") as log_exception:
      with self.assertRaisesRegex(RuntimeError, "original PortAudio error 2") as raised:
        with audio.open_audio_stream(sd, stream_factory(errors), lambda: None, "micd",
                                     startup_timeout=6.0, retry_interval=2.0,
                                     monotonic=clock.monotonic, sleep=clock.sleep,
                                     readiness_event_factory=event_factory(clock)):
          pass

    self.assertIs(raised.exception, errors[-1])
    self.assertEqual(clock.now, 6.0)
    self.assertEqual(repr(errors[1]), log_warning.call_args.args[0].split(": ", 1)[1])
    self.assertEqual([repr(errors[0]), repr(errors[-1])],
                     [call.args[0].split(": ", 1)[1] for call in log_exception.call_args_list])

  def test_successful_shutdown_closes_after_stop_failure(self) -> None:
    clock = FakeClock()
    stop_error = RuntimeError("PortAudio stop failed")
    ready_stream = FakeStream(stop_error=stop_error)
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception") as log_exception:
      with self.assertRaisesRegex(RuntimeError, "PortAudio stop failed") as raised:
        with audio.open_audio_stream(sd, stream_factory([ready_stream]), lambda: None, "soundd",
                                     monotonic=clock.monotonic, sleep=clock.sleep,
                                     readiness_event_factory=event_factory(clock)):
          pass

    self.assertIs(raised.exception, stop_error)
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])
    self.assertIn("soundd audio stream stop failed", log_exception.call_args.args[0])

  def test_shutdown_failure_does_not_mask_body_failure(self) -> None:
    clock = FakeClock()
    body_error = RuntimeError("body failed")
    ready_stream = FakeStream(stop_error=RuntimeError("stop failed"))
    sd = FakeSoundDevice()

    with patch.object(audio.cloudlog, "exception"):
      with self.assertRaisesRegex(RuntimeError, "body failed") as raised:
        with audio.open_audio_stream(sd, stream_factory([ready_stream]), lambda: None, "micd",
                                     monotonic=clock.monotonic, sleep=clock.sleep,
                                     readiness_event_factory=event_factory(clock)):
          raise body_error

    self.assertIs(raised.exception, body_error)
    self.assertEqual(ready_stream.operations, ["start", "stop", "close"])


@unittest.skipIf(sys.platform == "win32", "openpilot native messaging modules are not built on Windows")
class TestAudioProcessIntegration(unittest.TestCase):
  def test_micd_and_soundd_use_wrapped_successful_callback(self) -> None:
    cases = (
      ("openpilot.system.micd", "Mic", "InputStream", 16000, 800),
      ("openpilot.selfdrive.ui.soundd", "Soundd", "OutputStream", 48000, 4096),
    )

    for module_name, class_name, constructor_name, sample_rate, blocksize in cases:
      with self.subTest(process=class_name):
        module = importlib.import_module(module_name)
        process_type = getattr(module, class_name)
        process = process_type.__new__(process_type)
        process.callback = Mock()
        ready_stream = FakeStream()
        sd = FakeSoundDevice()
        constructor_calls: list[dict[str, Any]] = []

        def constructor(*, _calls: list[dict[str, Any]] = constructor_calls,
                        _stream: FakeStream = ready_stream, **kwargs: Any) -> FakeStream:
          _calls.append(kwargs)
          _stream.callback = kwargs["callback"]
          return _stream

        setattr(sd, constructor_name, constructor)
        with process.get_stream(sd) as stream:
          self.assertIs(stream, ready_stream)

        process.callback.assert_called_once_with()
        self.assertIsNot(constructor_calls[0]["callback"], process.callback)
        self.assertEqual(constructor_calls[0]["samplerate"], sample_rate)
        self.assertEqual(constructor_calls[0]["blocksize"], blocksize)

  def test_child_main_clears_shared_readiness_on_exit(self) -> None:
    for module_name, class_name, thread_name in (
      ("openpilot.system.micd", "Mic", "micd_thread"),
      ("openpilot.selfdrive.ui.soundd", "Soundd", "soundd_thread"),
    ):
      with self.subTest(process=class_name):
        module = importlib.import_module(module_name)
        ready_event = Mock()
        daemon = Mock()
        getattr(daemon, thread_name).side_effect = RuntimeError("exit")

        with patch.object(module, class_name, return_value=daemon) as daemon_type:
          with self.assertRaisesRegex(RuntimeError, "exit"):
            module.main(ready_event)

        daemon_type.assert_called_once_with(ready_event)
        self.assertEqual(ready_event.method_calls, [call.clear(), call.clear()])


if __name__ == "__main__":
  unittest.main()
