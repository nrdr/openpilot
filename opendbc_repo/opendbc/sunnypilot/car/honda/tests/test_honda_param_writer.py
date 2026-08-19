import threading

from openpilot.common import realtime
from opendbc.sunnypilot.car.honda import longitudinal


class RecordingParams:
  instances = []
  events = []

  def __init__(self):
    self.values = {}
    self.instances.append(self)

  def put(self, key, value, block=False):
    self.values[key] = value
    self.events.append(("put", key, block))


def test_persistence_runs_off_thread(monkeypatch):
  started = threading.Event()
  release = threading.Event()
  calls = []
  RecordingParams.events.clear()

  monkeypatch.setattr(realtime, "drop_realtime", lambda: RecordingParams.events.append("drop_realtime"))
  monkeypatch.setattr(realtime, "set_core_affinity", lambda cores: RecordingParams.events.append("set_core_affinity"))

  def write_metadata(car_fingerprint):
    calls.append((threading.current_thread().name, car_fingerprint))
    started.set()
    assert release.wait(2.0)

  monkeypatch.setattr(longitudinal, "Params", RecordingParams)
  monkeypatch.setattr(longitudinal, "write_metadata", write_metadata)
  writer = longitudinal.HondaParamWriter()

  caller = threading.Thread(target=writer.put_many, args=(
    {"HondaGasFactorParams": 1.25},
    "HONDA_CLARITY",
  ))
  caller.start()
  caller.join(1.0)
  assert not caller.is_alive()
  assert started.wait(1.0)
  release.set()

  assert RecordingParams.instances[-1].values == {"HondaGasFactorParams": 1.25}
  assert calls == [("honda-param-writer", "HONDA_CLARITY")]
  assert RecordingParams.events[:2] == ["drop_realtime", "set_core_affinity"]
  assert RecordingParams.events[2] == ("put", "HondaGasFactorParams", True)
