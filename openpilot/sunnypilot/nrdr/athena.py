import asyncio
import base64
import hashlib
import hmac
import json
import os
import queue
import threading
import time

from openpilot.cereal import car
from openpilot.common.hardware import HARDWARE
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


TOKEN_TTL = 5 * 60
LOCKOUT = 30
MAX_FAILURES = 5
DEFAULT_PIN = "1234"

sdp_receive: queue.Queue[dict] = queue.Queue()
sdp_send: queue.Queue[str] = queue.Queue()
ice_send: queue.Queue[str] = queue.Queue()


class RemotePin:
  def __init__(self):
    self.tokens: dict[str, float] = {}
    self.lock = threading.RLock()
    self.failures = 0
    self.locked_until = 0.0

  @staticmethod
  def _is_set() -> bool:
    params = Params()
    iterations = params.get("RemoteAccessPinIterations")
    return (params.get_bool("RemoteAccessPinEnabled") and bool(params.get("RemoteAccessPinSalt")) and
            bool(params.get("RemoteAccessPinHash")) and isinstance(iterations, int) and iterations > 0)

  @staticmethod
  def _hash(pin: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, iterations, dklen=32)

  @staticmethod
  def _validate_format(pin: str) -> None:
    if not isinstance(pin, str) or not pin.isdigit() or not 4 <= len(pin) <= 12:
      raise ValueError("PIN must be 4-12 digits")

  def _set(self, params: Params, pin: str) -> None:
    self._validate_format(pin)
    iterations = 150000
    salt = os.urandom(16)
    params.put("RemoteAccessPinSalt", salt)
    params.put("RemoteAccessPinHash", self._hash(pin, salt, iterations))
    params.put("RemoteAccessPinIterations", iterations)
    params.put_bool("RemoteAccessPinEnabled", True)

  def _verify(self, params: Params, pin: str) -> bool:
    salt = params.get("RemoteAccessPinSalt") or b""
    expected = params.get("RemoteAccessPinHash") or b""
    iterations = params.get("RemoteAccessPinIterations") or 0
    if not salt or not expected or not isinstance(iterations, int) or iterations <= 0:
      return False
    return hmac.compare_digest(expected, self._hash(pin, salt, iterations))

  def _issue_token(self, now: float) -> tuple[str, int]:
    self.tokens = {token: expiry for token, expiry in self.tokens.items() if expiry > now}
    token = base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip("=")
    self.tokens[token] = now + TOKEN_TTL
    return token, TOKEN_TTL

  def require_auth(self, token: str | None) -> None:
    if not self._is_set():
      return
    now = time.monotonic()
    with self.lock:
      self.tokens = {key: expiry for key, expiry in self.tokens.items() if expiry > now}
      if not token or self.tokens.get(token, 0) <= now:
        raise Exception("PIN required")

  def ensure_default(self) -> None:
    try:
      if not self._is_set():
        with self.lock:
          self._set(Params(), DEFAULT_PIN)
        cloudlog.event("athena.remote_pin.default_set")
    except Exception:
      cloudlog.exception("failed to initialize remote access PIN")

  def status(self) -> dict[str, bool | int]:
    with self.lock:
      remaining = max(0, int(self.locked_until - time.monotonic()))
    return {"set": self._is_set(), "locked": remaining > 0, "lockRemainingS": remaining}

  def verify(self, pin: str) -> dict[str, bool | str | int]:
    if not self._is_set():
      with self.lock:
        token, ttl = self._issue_token(time.monotonic())
      return {"success": True, "token": token, "expiresInS": ttl}
    try:
      self._validate_format(pin)
    except ValueError as error:
      return {"success": False, "error": str(error)}

    with self.lock:
      now = time.monotonic()
      if now < self.locked_until:
        return {"success": False, "error": "Locked", "lockRemainingS": int(self.locked_until - now)}
      if not self._verify(Params(), pin):
        self.failures += 1
        if self.failures % MAX_FAILURES == 0:
          self.locked_until = now + LOCKOUT
          return {"success": False, "error": "Locked", "lockRemainingS": LOCKOUT}
        return {"success": False, "error": "Incorrect PIN"}
      self.failures = 0
      self.locked_until = 0.0
      token, ttl = self._issue_token(now)
      return {"success": True, "token": token, "expiresInS": ttl}

  def set(self, pin: str) -> dict[str, bool]:
    if self._is_set():
      raise Exception("PIN already set")
    with self.lock:
      self._set(Params(), pin)
    return {"success": True}

  def change(self, old_pin: str, new_pin: str) -> dict[str, bool]:
    if not self._is_set():
      raise Exception("PIN not set")
    if not isinstance(old_pin, str) or not isinstance(new_pin, str):
      raise Exception("Invalid PIN")

    with self.lock:
      now = time.monotonic()
      if now < self.locked_until:
        raise Exception(f"Locked. Try again in {int(self.locked_until - now)}s.")
      if not self._verify(Params(), old_pin):
        self.failures += 1
        if self.failures % MAX_FAILURES == 0:
          self.locked_until = now + LOCKOUT
          raise Exception(f"Too many attempts. Try again in {LOCKOUT}s.")
        raise Exception("Incorrect PIN")
      self._set(Params(), new_pin)
      self.failures = 0
      self.locked_until = 0.0
    return {"success": True}

  def clear(self, force: bool = False, pin: str | None = None) -> dict[str, bool]:
    params = Params()
    with self.lock:
      now = time.monotonic()
      if not force and self._is_set():
        if now < self.locked_until:
          raise Exception(f"Locked. Try again in {int(self.locked_until - now)}s.")
        if pin is None or not self._verify(params, pin):
          self.failures += 1
          if self.failures % MAX_FAILURES == 0:
            self.locked_until = now + LOCKOUT
            raise Exception(f"Too many attempts. Try again in {LOCKOUT}s.")
          raise Exception("Incorrect PIN")
      params.put_bool("RemoteAccessPinEnabled", False)
      params.remove("RemoteAccessPinSalt")
      params.remove("RemoteAccessPinHash")
      params.put("RemoteAccessPinIterations", 150000)
      self.failures = 0
      self.locked_until = 0.0
      self.tokens.clear()
    return {"success": True}


remote_pin = RemotePin()


def _rtc_handler(exit_event: threading.Event | None) -> None:
  from openpilot.sunnypilot.nrdr.athena_streamer import Streamer
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  try:
    loop.run_until_complete(Streamer(sdp_send, sdp_receive, ice_send).event_loop(exit_event))
  finally:
    loop.close()


def _set_sdp_answer(answer, authToken: str | None = None) -> None:
  remote_pin.require_auth(authToken)
  sdp_receive.put_nowait(answer)


def _get_sdp(authToken: str | None = None):
  remote_pin.require_auth(authToken)
  deadline = time.monotonic() + 10
  while time.monotonic() < deadline:
    try:
      result = json.loads(sdp_send.get(timeout=0.1))
      if result:
        return result
    except queue.Empty:
      pass
  return {"error": "timeout"}


def _get_ice(authToken: str | None = None):
  remote_pin.require_auth(authToken)
  candidates = []
  while not ice_send.empty():
    try:
      candidates.append(json.loads(ice_send.get_nowait()))
    except queue.Empty:
      break
  return candidates or {"error": True}


def _start_stream(sdp: str | None = None, enabled: bool = True) -> dict:
  from openpilot.system.webrtc.helpers import StreamRequestBody, post_stream_request, wait_for_webrtcd
  params = Params()
  if not enabled:
    params.put_bool("IsLiveStreaming", False, block=True)
    params.put_bool("LiveView", False, block=True)
    return {"success": True}
  if params.get_bool("IsOnroad"):
    raise Exception("Live View unavailable while onroad")
  if not params.get_bool("LiveViewEnabled"):
    raise Exception("Live View disabled")
  if not isinstance(sdp, str) or not sdp:
    raise Exception("sdp is required")

  services = []
  cp_bytes = params.get("CarParamsPersistent")
  if cp_bytes is None:
    raise Exception("failed to get CarParamsPersistent")
  with car.CarParams.from_bytes(cp_bytes) as CP:
    if CP.notCar:
      services.append("testJoystick")
  if not params.get_bool("IsOffroad"):
    raise Exception("Live View unavailable unless offroad")

  body = StreamRequestBody(sdp, "wideRoad", True, services, ["carState", "deviceState"])
  started = False
  params.put_bool("IsLiveStreaming", True, block=True)
  try:
    wait_for_webrtcd()
    result = post_stream_request(body)
    started = True
    return result
  except TimeoutError as error:
    raise Exception("webrtc took too long to start") from error
  finally:
    if not started:
      params.put_bool("IsLiveStreaming", False, block=True)
      params.put_bool("LiveView", False, block=True)


def install(dispatcher) -> None:
  dispatcher["remotePinStatus"] = remote_pin.status
  dispatcher["remotePinVerify"] = remote_pin.verify
  dispatcher["remotePinSet"] = remote_pin.set
  dispatcher["remotePinChange"] = lambda oldPin, newPin: remote_pin.change(oldPin, newPin)
  dispatcher["remotePinClear"] = remote_pin.clear
  dispatcher["setSdpAnswer"] = _set_sdp_answer
  dispatcher["getSdp"] = _get_sdp
  dispatcher["getIce"] = _get_ice
  dispatcher["getNetworks"] = HARDWARE.get_networks
  dispatcher["startStream"] = _start_stream


def start(exit_event: threading.Event | None) -> None:
  remote_pin.ensure_default()
  threading.Thread(target=_rtc_handler, args=(exit_event,), name="nrdr_rtc", daemon=True).start()
