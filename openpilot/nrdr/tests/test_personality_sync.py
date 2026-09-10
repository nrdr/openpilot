from types import SimpleNamespace

import pytest

from openpilot.cereal import custom
from opendbc.car.structs import car
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.nrdr.hooks.selfdrived import NrdrSelfdrive


class RecordingParams:
  def __init__(self):
    self.puts = []

  def put(self, key, value):
    self.puts.append((key, value))


@pytest.mark.parametrize(("initial", "expected"), ((0, 3), (1, 0), (2, 1), (3, 2)))
def test_button_personality_change_is_live_and_persisted(monkeypatch, initial, expected):
  monkeypatch.setattr("openpilot.nrdr.hooks.selfdrived.consume_button_press", lambda _: True)
  selfdrived = SimpleNamespace(
    CP=SimpleNamespace(openpilotLongitudinalControl=True),
    params=RecordingParams(),
    personality=initial,
    experimental_mode_switched=False,
  )
  CS = SimpleNamespace(buttonEvents=[SimpleNamespace(pressed=False, type=car.CarState.ButtonEvent.Type.gapAdjustCruise)])

  assert NrdrSelfdrive.update_personality(selfdrived, CS, False)

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


def test_sla_confirmation_release_stays_reserved_across_planner_race(monkeypatch):
  times = iter((10.0, 10.1, 10.8))
  monkeypatch.setattr("openpilot.nrdr.hooks.selfdrived.time.monotonic", lambda: next(times))

  nrdr = NrdrSelfdrive()
  pre_active = custom.LongitudinalPlanSP.SpeedLimit.AssistState.preActive
  active = custom.LongitudinalPlanSP.SpeedLimit.AssistState.active

  assert nrdr.reserve_distance_button(pre_active)
  assert nrdr.reserve_distance_button(active)
  assert not nrdr.reserve_distance_button(active)
