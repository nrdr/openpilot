#!/usr/bin/env python3
import time
import json
import jwt
import os
from typing import cast
from pathlib import Path
from urllib.parse import urlparse

from datetime import datetime, timedelta, UTC
from openpilot.common.api import Api, api_get, get_key_pair
from openpilot.common.api.comma_connect import API_HOST
from openpilot.common.params import Params
from openpilot.common.spinner import Spinner
from openpilot.selfdrive.selfdrived.alertmanager import set_offroad_alert
from openpilot.common.hardware import HARDWARE, PC
from openpilot.common.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog


UNREGISTERED_DONGLE_ID = "UnregisteredDevice"
KONIK_DONGLE_ID_PATH_ENV = "KONIK_DONGLE_ID_PATH"


def _is_valid_dongle_id(dongle_id: str | None) -> bool:
  return bool(dongle_id and dongle_id != UNREGISTERED_DONGLE_ID and not any(c.isspace() for c in dongle_id))


def _is_konik_backend() -> bool:
  hostname = (urlparse(API_HOST).hostname or "").lower()
  return hostname == "konik.ai" or hostname.endswith(".konik.ai")


def get_konik_dongle_id_path() -> Path:
  override = os.getenv(KONIK_DONGLE_ID_PATH_ENV)
  if override:
    return Path(override)
  if PC:
    return Path(Paths.comma_home()) / "community" / "identity" / "konik_dongle_id"
  return Path("/data/community/identity/konik_dongle_id")


def _read_dongle_id(path: Path) -> str | None:
  try:
    dongle_id = path.read_text().strip()
    return dongle_id if _is_valid_dongle_id(dongle_id) else None
  except FileNotFoundError:
    return None
  except OSError:
    cloudlog.exception(f"failed to read dongle id from {path}")
    return None


def persist_konik_dongle_id(dongle_id: str | None) -> None:
  """Atomically save a Konik-validated identity outside the params directory."""
  if not _is_valid_dongle_id(dongle_id):
    return

  path = get_konik_dongle_id_path()
  tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tmp_path.open("w", encoding="ascii") as f:
      f.write(cast(str, dongle_id))
      f.flush()
      os.fsync(f.fileno())
    tmp_path.chmod(0o600)
    os.replace(tmp_path, path)
  except OSError:
    cloudlog.exception(f"failed to persist Konik dongle id to {path}")
  finally:
    try:
      tmp_path.unlink(missing_ok=True)
    except OSError:
      pass


def _validate_konik_dongle_id(dongle_id: str) -> bool | None:
  """Return True/False for a definitive Konik answer, or None if Konik is unavailable."""
  try:
    api = Api(dongle_id)
    response = api.get(f"v1.1/devices/{dongle_id}", timeout=5, access_token=api.get_token())
    if response.status_code == 200:
      device = response.json()
      server_dongle_id = device.get("dongle_id")
      server_serial = device.get("serial")
      if server_dongle_id not in (None, dongle_id) or server_serial not in (None, HARDWARE.get_serial()):
        cloudlog.warning("Konik dongle validation returned a different device")
        return False
      return True
    if response.status_code in (401, 403, 404):
      return False
    cloudlog.warning(f"Konik dongle validation returned HTTP {response.status_code}")
  except Exception:
    cloudlog.exception("Konik dongle validation unavailable")
  return None


def _resolve_konik_dongle_id(params_dongle_id: str | None) -> str | None:
  # /persist/comma/dongle_id is the factory comma identity on newer hardware and
  # is a read-only squashfs file on tici. It must never be treated as Konik's
  # identity without asking Konik first.
  durable_dongle_id = _read_dongle_id(get_konik_dongle_id_path())
  if durable_dongle_id is not None:
    if params_dongle_id not in (None, UNREGISTERED_DONGLE_ID, durable_dongle_id):
      cloudlog.warning("restoring durable Konik dongle id over a different params value")
    return durable_dongle_id

  candidates: list[tuple[str, str]] = []
  if _is_valid_dongle_id(params_dongle_id):
    candidates.append(("params", cast(str, params_dongle_id)))

  factory_dongle_id = _read_dongle_id(Path(Paths.persist_root()) / "comma" / "dongle_id")
  if factory_dongle_id is not None and all(factory_dongle_id != candidate for _, candidate in candidates):
    candidates.append(("factory", factory_dongle_id))

  for source, candidate in candidates:
    validation = _validate_konik_dongle_id(candidate)
    if validation is True:
      persist_konik_dongle_id(candidate)
      return candidate
    if validation is None and source == "params":
      # Do not knock an otherwise-working device offline just because Konik was
      # temporarily unreachable during boot. Retry migration on the next boot.
      return candidate

  return None


def is_registered_device() -> bool:
  dongle = Params().get("DongleId")
  return dongle not in (None, UNREGISTERED_DONGLE_ID)


def register(show_spinner=False) -> str | None:
  """
  All devices built since March 2024 come with all
  info stored in /persist/. This is kept around
  only for devices built before then.

  With a backend update to take serial number instead
  of dongle ID to some endpoints, this can be removed
  entirely.
  """
  params = Params()

  konik_backend = _is_konik_backend()
  params_dongle_id: str | None = params.get("DongleId")
  dongle_id = _resolve_konik_dongle_id(params_dongle_id) if konik_backend else params_dongle_id
  if not konik_backend and dongle_id is None and Path(Paths.persist_root()+"/comma/dongle_id").is_file():
    # not all devices will have this; added early in comma 3X production (2/28/24)
    with open(Paths.persist_root()+"/comma/dongle_id") as f:
      dongle_id = f.read().strip()

  # Create registration token, in the future, this key will make JWTs directly
  jwt_algo, private_key, public_key = get_key_pair()

  if not public_key:
    dongle_id = UNREGISTERED_DONGLE_ID
    cloudlog.warning("missing public key")
  elif dongle_id is None:
    if show_spinner:
      spinner = Spinner()
      spinner.update("registering device")

    # Block until we get the imei
    serial = HARDWARE.get_serial()
    start_time = time.monotonic()
    imei: str | None = None
    while imei is None:
      try:
        imei = HARDWARE.get_imei()
      except Exception:
        cloudlog.exception("Error getting imei, trying again...")
        time.sleep(1)

      if time.monotonic() - start_time > 60 and show_spinner:
        spinner.update(f"registering device - serial: {serial}, IMEI: {imei}")

    backoff = 0
    start_time = time.monotonic()
    while True:
      try:
        register_token = jwt.encode({'register': True, 'exp': datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)},
                                    cast(str, private_key), algorithm=jwt_algo)
        cloudlog.info("getting pilotauth")
        cloudlog.info("getting pilotauth")
        resp = api_get("v2/pilotauth/", method='POST', timeout=15,
                       imei=imei, imei2="", serial=serial, public_key=public_key, register_token=register_token)

        if resp.status_code in (402, 403):
          cloudlog.info(f"Unable to register device, got {resp.status_code}")
          dongle_id = UNREGISTERED_DONGLE_ID
        else:
          dongleauth = json.loads(resp.text)
          dongle_id = dongleauth["dongle_id"]
          if konik_backend:
            persist_konik_dongle_id(dongle_id)
        break
      except NotImplementedError:
        # dependency issues with PyJWT will hang the registration test in backoff loop otherwise
        raise
      except Exception:
        cloudlog.exception("failed to authenticate")
        backoff = min(backoff + 1, 15)
        time.sleep(backoff)

      if time.monotonic() - start_time > 60 and show_spinner:
        spinner.update(f"registering device - serial: {serial}, IMEI: {imei}")
        return UNREGISTERED_DONGLE_ID  # hotfix to prevent an infinite wait for registration

    if show_spinner:
      spinner.close()

  if dongle_id:
    params.put("DongleId", dongle_id, block=True)
    set_offroad_alert("Offroad_UnregisteredHardware", (dongle_id == UNREGISTERED_DONGLE_ID) and not PC)

    # Konik identities must not share the factory comma identity file. On tici,
    # /persist is read-only and already contains comma's dongle id, so the old
    # write-once mirror silently preserved the wrong backend's identity.
    if dongle_id != UNREGISTERED_DONGLE_ID and not konik_backend:
      try:
        dongle_path = Path(Paths.persist_root() + "/comma/dongle_id")
        if not dongle_path.is_file():
          dongle_path.parent.mkdir(parents=True, exist_ok=True)
          dongle_path.write_text(dongle_id)
      except Exception:
        cloudlog.exception("failed to mirror dongle_id to persist")

  return dongle_id


if __name__ == "__main__":
  print(register())
