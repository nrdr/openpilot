import threading

from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD


class DelayedParams:
  def __init__(self, value):
    self.value = value
    self.puts = []
    self.read_started = threading.Event()
    self.release_read = threading.Event()

  def get(self, _key, return_default=False):
    assert return_default
    stale_value = self.value
    self.read_started.set()
    assert self.release_read.wait(1.0)
    return stale_value

  def put(self, key, value):
    self.puts.append((key, value))


def test_stale_param_read_cannot_undo_button_personality_change():
  selfdrived = object.__new__(SelfdriveD)
  selfdrived.params = DelayedParams(value=1)
  selfdrived._personality_lock = threading.Lock()
  selfdrived._personality_pending = None
  selfdrived.personality = 1

  stale_reader = threading.Thread(target=selfdrived._refresh_personality_from_params)
  stale_reader.start()
  assert selfdrived.params.read_started.wait(1.0)

  selfdrived._cycle_personality_from_button()
  selfdrived.params.release_read.set()
  stale_reader.join(1.0)

  assert not stale_reader.is_alive()
  assert selfdrived.personality == 0
  assert selfdrived.params.puts == [("LongitudinalPersonality", 0)]

  # Once params exposes the requested value, the guard acknowledges and clears it.
  selfdrived.params.value = 0
  selfdrived._refresh_personality_from_params()
  assert selfdrived._personality_pending is None


def test_expired_guard_does_not_mask_external_personality_change():
  selfdrived = object.__new__(SelfdriveD)
  selfdrived.params = DelayedParams(value=2)
  selfdrived.params.release_read.set()
  selfdrived._personality_lock = threading.Lock()
  selfdrived._personality_pending = (0, 0.0)
  selfdrived.personality = 0

  selfdrived._refresh_personality_from_params()

  assert selfdrived.personality == 2
  assert selfdrived._personality_pending is None
