"""Missing-only preferences requiring the current vehicle, not cached identity."""

import os
from pathlib import Path
import tempfile

from opendbc.car.honda.civic_pcm import uses_civic_pcm

from openpilot.nrdr.params.profiles import confirmed_vehicle_identity, get_selected_car_identity


def _publish_missing_on(params, key: str) -> bool:
  """Atomically install a complete value without replacing a concurrent choice.

  Params.put_bool replaces existing files, so a read-then-put can overwrite an
  owner saving Off during startup. A same-directory hard link is create-only:
  a concurrent Params rename wins either before or after this publication.
  Unsupported filesystems fail closed; there is deliberately no put fallback.
  """
  path = Path(params.get_param_path(key))
  fd, temporary = tempfile.mkstemp(prefix=".nrdr-engine-default-", dir=path.parent)
  try:
    with os.fdopen(fd, "wb") as stream:
      stream.write(b"1")
      stream.flush()
      os.fsync(stream.fileno())
    try:
      os.link(temporary, path)
    except FileExistsError:
      return False
    if os.name == "posix":
      directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
      try:
        os.fsync(directory)
      finally:
        os.close(directory)
    return True
  finally:
    Path(temporary).unlink(missing_ok=True)


def initialize_engine_braking_default(CP, CP_SP, params) -> bool:
  """Default an eligible Civic PCM to On without reinterpreting any saved value.

  Called once at car startup before CP publication, never from a control loop
  or migration. Keep the registry unset until live vehicle admission succeeds.
  Raw presence also preserves empty/malformed files and propagates storage
  errors: neither is evidence that the owner has never saved a preference.
  """
  if CP is None or CP_SP is None:
    return False
  present, fingerprint, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(CP, fingerprint, brand, selection_present=present)
  if identity is None or identity[1] != "honda" or not uses_civic_pcm(CP, CP_SP):
    return False
  key = "NrdrExperimentalEngineBraking"
  if params.get_raw(key) is not None:
    return False
  return _publish_missing_on(params, key)
