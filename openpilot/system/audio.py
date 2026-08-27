from collections.abc import Callable, Generator
from contextlib import contextmanager
import threading
import time
from typing import Any

from openpilot.common.swaglog import cloudlog


# Keep cold-boot recovery bounded while allowing substantially more time than
# the previous ten-attempt retry loop.
AUDIO_STARTUP_TIMEOUT = 90.0
AUDIO_STARTUP_RETRY_INTERVAL = 3.0
AUDIO_CALLBACK_TIMEOUT = 1.0
AUDIO_READINESS_POLL_INTERVAL = 0.05


def _close_failed_stream(stream: Any, process_name: str) -> None:
  if stream is None:
    return

  try:
    stream.close()
  except Exception:
    # Cleanup must not replace the PortAudio error which caused this attempt to
    # fail, but it is still useful evidence when diagnosing a partial startup.
    cloudlog.exception(f"{process_name} audio stream cleanup failed")


def _stop_and_close_stream(stream: Any, process_name: str, suppress_errors: bool) -> None:
  first_error: Exception | None = None
  first_traceback = None

  try:
    stream.stop()
  except Exception as error:
    first_error = error
    first_traceback = error.__traceback__
    cloudlog.exception(f"{process_name} audio stream stop failed")

  try:
    stream.close()
  except Exception as error:
    if first_error is None:
      first_error = error
      first_traceback = error.__traceback__
    cloudlog.exception(f"{process_name} audio stream close failed")

  if first_error is not None and not suppress_errors:
    raise first_error.with_traceback(first_traceback)


def _callback_with_readiness(callback: Callable[..., Any], callback_ready: Any) -> Callable[..., None]:
  def ready_callback(*args: Any, **kwargs: Any) -> None:
    callback(*args, **kwargs)
    if not callback_ready.is_set():
      callback_ready.set()

  return ready_callback


@contextmanager
def open_audio_stream(sd: Any, stream_factory: Callable[[Callable[..., Any]], Any], callback: Callable[..., Any], process_name: str, *,
                      startup_timeout: float = AUDIO_STARTUP_TIMEOUT,
                      retry_interval: float = AUDIO_STARTUP_RETRY_INTERVAL,
                      callback_timeout: float = AUDIO_CALLBACK_TIMEOUT,
                      readiness_poll_interval: float = AUDIO_READINESS_POLL_INTERVAL,
                      monotonic: Callable[[], float] = time.monotonic,
                      sleep: Callable[[float], None] = time.sleep,
                      readiness_event_factory: Callable[[], Any] = threading.Event) -> Generator[Any, None, None]:
  """Open and start a PortAudio stream, retrying the complete startup lifecycle.

  Stream construction, ``start()``, and the first callback can fail
  independently while the audio device is appearing during a cold boot. Every
  retry therefore reloads PortAudio and uses a fresh stream. The final startup
  exception is re-raised unchanged when the overall deadline expires.
  """
  if startup_timeout < 0:
    raise ValueError("startup_timeout must be non-negative")
  if retry_interval <= 0:
    raise ValueError("retry_interval must be positive")
  if callback_timeout <= 0:
    raise ValueError("callback_timeout must be positive")
  if readiness_poll_interval <= 0:
    raise ValueError("readiness_poll_interval must be positive")

  deadline = monotonic() + startup_timeout
  attempt = 0
  stream = None

  while attempt == 0 or monotonic() < deadline:
    attempt += 1
    try:
      # Every stream generation gets a distinct process-local event. A late
      # callback from a failed stream therefore cannot certify its replacement.
      callback_ready = readiness_event_factory()
      ready_callback = _callback_with_readiness(callback, callback_ready)

      # sounddevice is imported after process forking. Reinitializing here also
      # discards any stale PortAudio device state left by the previous attempt.
      sd._terminate()
      sd._initialize()
      stream = stream_factory(ready_callback)
      stream.start()
      if not stream.active:
        raise RuntimeError(f"{process_name} audio stream did not become active")

      callback_deadline = min(deadline, monotonic() + callback_timeout)
      while not callback_ready.is_set():
        if not stream.active:
          raise RuntimeError(f"{process_name} audio stream became inactive before its first callback")

        callback_remaining = callback_deadline - monotonic()
        if callback_remaining <= 0:
          raise RuntimeError(f"{process_name} audio stream did not receive its first callback")
        callback_ready.wait(min(readiness_poll_interval, callback_remaining))

      if not stream.active:
        raise RuntimeError(f"{process_name} audio stream became inactive during its first callback")
      break
    except Exception as error:
      _close_failed_stream(stream, process_name)
      stream = None

      remaining = deadline - monotonic()
      final_attempt = remaining <= retry_interval
      log_message = f"{process_name} audio startup attempt {attempt} failed: {error!r}"
      if attempt == 1 or final_attempt:
        cloudlog.exception(log_message)
      else:
        cloudlog.warning(log_message)

      if remaining <= 0:
        raise
      sleep(min(retry_interval, remaining))
      if final_attempt or monotonic() >= deadline:
        raise

  body_failed = False
  try:
    yield stream
  except BaseException:
    body_failed = True
    raise
  finally:
    _stop_and_close_stream(stream, process_name, suppress_errors=body_failed)
