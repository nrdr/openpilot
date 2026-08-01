import threading

from opendbc.car.honda import carcontroller


class RecordingParams:
  instances = []

  def __init__(self):
    self.values = {}
    self.instances.append(self)

  def put(self, key, value):
    self.values[key] = value


def test_persistence_runs_on_worker_thread_with_immutable_snapshot(monkeypatch):
  meta_started = threading.Event()
  release_meta = threading.Event()
  brake_finished = threading.Event()
  calls = []

  def write_meta(car_fingerprint):
    calls.append(("meta", threading.current_thread().name, car_fingerprint))
    meta_started.set()
    assert release_meta.wait(2.0)

  def write_brakes(car_fingerprint, brake_bins):
    calls.append(("brakes", threading.current_thread().name, car_fingerprint, brake_bins))
    brake_finished.set()

  monkeypatch.setattr(carcontroller, "Params", RecordingParams)
  monkeypatch.setattr(carcontroller, "_write_learner_meta_atomic", write_meta)
  monkeypatch.setattr(carcontroller, "_write_brake_profiles_atomic", write_brakes)

  writer = carcontroller.HondaParamWriter()
  brake_bins = [0.1, 0.2, 0.3, 0.4]

  # Invoke from a separate thread so the test can prove that even deliberately
  # blocked disk persistence cannot block the controller-side caller.
  caller = threading.Thread(target=writer.put_many, kwargs={
    "values": {"HondaGasFactorParams": 1.25},
    "car_fingerprint": "HONDA_CLARITY",
    "brake_bins": brake_bins,
  })
  caller.start()
  caller.join(1.0)
  assert not caller.is_alive()
  assert meta_started.wait(1.0)

  # The queue owns a tuple snapshot, not the controller's mutable list.
  brake_bins[0] = 9.9
  release_meta.set()
  assert brake_finished.wait(1.0)

  assert RecordingParams.instances[-1].values == {"HondaGasFactorParams": 1.25}
  assert calls == [
    ("meta", "honda-param-writer", "HONDA_CLARITY"),
    ("brakes", "honda-param-writer", "HONDA_CLARITY", (0.1, 0.2, 0.3, 0.4)),
  ]
