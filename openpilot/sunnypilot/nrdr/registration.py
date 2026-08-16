import os
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from openpilot.common.api import Api
from openpilot.common.api.comma_connect import API_HOST
from openpilot.common.hardware import HARDWARE, PC
from openpilot.common.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog


UNREGISTERED_DONGLE_ID = "UnregisteredDevice"
PATH_ENV = "KONIK_DONGLE_ID_PATH"


def is_enabled() -> bool:
  hostname = (urlparse(API_HOST).hostname or "").lower()
  return hostname == "konik.ai" or hostname.endswith(".konik.ai")


def identity_path() -> Path:
  override = os.getenv(PATH_ENV)
  if override:
    return Path(override)
  if PC:
    return Path(Paths.comma_home()) / "community" / "identity" / "konik_dongle_id"
  return Path("/data/community/identity/konik_dongle_id")


def _valid(dongle_id: str | None) -> bool:
  return bool(dongle_id and dongle_id != UNREGISTERED_DONGLE_ID and not any(c.isspace() for c in dongle_id))


def _read(path: Path) -> str | None:
  try:
    dongle_id = path.read_text().strip()
    return dongle_id if _valid(dongle_id) else None
  except FileNotFoundError:
    return None
  except OSError:
    cloudlog.exception("failed to read dongle id from %s", path)
    return None


def persist(dongle_id: str | None) -> None:
  if not _valid(dongle_id):
    return

  path = identity_path()
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
    cloudlog.exception("failed to persist Konik dongle id to %s", path)
  finally:
    try:
      tmp_path.unlink(missing_ok=True)
    except OSError:
      pass


def commit(dongle_id: str | None, konik_backend: bool) -> None:
  if not _valid(dongle_id):
    return
  if konik_backend:
    persist(dongle_id)
    return

  try:
    path = Path(Paths.persist_root()) / "comma" / "dongle_id"
    if not path.is_file():
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(cast(str, dongle_id))
  except Exception:
    cloudlog.exception("failed to mirror dongle id to persist")


def _validate(dongle_id: str) -> bool | None:
  try:
    api = Api(dongle_id)
    response = api.get(f"v1.1/devices/{dongle_id}", timeout=5, access_token=api.get_token())
    if response.status_code == 200:
      device = response.json()
      if device.get("dongle_id") not in (None, dongle_id) or device.get("serial") not in (None, HARDWARE.get_serial()):
        cloudlog.warning("Konik dongle validation returned a different device")
        return False
      return True
    if response.status_code in (401, 403, 404):
      return False
    cloudlog.warning("Konik dongle validation returned HTTP %s", response.status_code)
  except Exception:
    cloudlog.exception("Konik dongle validation unavailable")
  return None


def resolve(params_dongle_id: str | None) -> str | None:
  durable_dongle_id = _read(identity_path())
  if durable_dongle_id is not None:
    if params_dongle_id not in (None, UNREGISTERED_DONGLE_ID, durable_dongle_id):
      cloudlog.warning("restoring durable Konik dongle id over a different params value")
    return durable_dongle_id

  candidates: list[tuple[str, str]] = []
  if _valid(params_dongle_id):
    candidates.append(("params", cast(str, params_dongle_id)))

  factory_dongle_id = _read(Path(Paths.persist_root()) / "comma" / "dongle_id")
  if factory_dongle_id is not None and all(factory_dongle_id != candidate for _, candidate in candidates):
    candidates.append(("factory", factory_dongle_id))

  for source, candidate in candidates:
    validation = _validate(candidate)
    if validation is True:
      persist(candidate)
      return candidate
    if validation is None and source == "params":
      return candidate
  return None
