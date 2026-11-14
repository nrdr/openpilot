"""Profile-only writer serialization. Never call from a control-loop tick."""
import hashlib
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


PERSONALITY_KEY = "LongitudinalPersonality"


def personality_lock_path(params) -> Path:
  # get_param_path includes the Params root AND OPENPILOT_PREFIX. Do not resolve
  # its namespace symlink: the lock must survive replacement/clearing of keys.
  namespace = os.path.normcase(os.path.abspath(params.get_param_path(PERSONALITY_KEY)))
  digest = hashlib.sha256(os.fsencode(namespace)).hexdigest()
  directory = Path("/dev/shm") if sys.platform.startswith("linux") else Path(tempfile.gettempdir())
  return directory / f"nrdr_personality_{digest}.lock"


@contextmanager
def personality_write_lock(params):
  """Shared by UI/RPC/startup and the background wheel writer, never unlinked.

  This is NOT Params' internal .lock. Always acquire this lock first, then use
  blocking Params.put; queuing an async write would escape the critical section.
  The file lives outside Params so clear_all cannot split the lock's inode.
  """
  fd = os.open(personality_lock_path(params), os.O_CREAT | os.O_RDWR, 0o600)
  try:
    if os.name == "nt":
      import msvcrt
      msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
    else:
      import fcntl
      fcntl.flock(fd, fcntl.LOCK_EX)
    try:
      yield
    finally:
      if os.name == "nt":
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
      else:
        fcntl.flock(fd, fcntl.LOCK_UN)
  finally:
    os.close(fd)


def write_personality(params, value: int) -> None:
  if type(value) is not int or value not in range(4):
    raise ValueError("Personality must be an integer from 0 to 3")
  with personality_write_lock(params):
    params.put(PERSONALITY_KEY, value, block=True)
