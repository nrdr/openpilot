from types import SimpleNamespace

import pytest

from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD


class RecordingParams:
  def __init__(self):
    self.puts = []

  def put(self, key, value):
    self.puts.append((key, value))


@pytest.mark.parametrize(("initial", "expected"), ((0, 3), (1, 0), (2, 1), (3, 2)))
def test_button_personality_change_is_live_and_persisted(initial, expected):
  selfdrived = object.__new__(SelfdriveD)
  selfdrived.params = RecordingParams()
  selfdrived.personality = initial

  selfdrived._cycle_personality_from_button()

  assert selfdrived.personality == expected
  assert selfdrived.params.puts == [("LongitudinalPersonality", expected)]


def test_onroad_params_thread_does_not_read_personality(monkeypatch):
  class OneIterationEvent:
    def __init__(self):
      self.calls = 0

    def is_set(self):
      self.calls += 1
      return self.calls > 1

  class ParamsWithoutPersonalityReads:
    def get_bool(self, _key):
      return False

    def get(self, key, **_kwargs):
      raise AssertionError(f"onroad params thread read {key}")

  selfdrived = object.__new__(SelfdriveD)
  selfdrived.params = ParamsWithoutPersonalityReads()
  selfdrived.CP = SimpleNamespace(openpilotLongitudinalControl=True)
  selfdrived.mads = SimpleNamespace(read_params=lambda: None)
  monkeypatch.setattr("openpilot.selfdrive.selfdrived.selfdrived.time.sleep", lambda _: None)

  selfdrived.params_thread(OneIterationEvent())
