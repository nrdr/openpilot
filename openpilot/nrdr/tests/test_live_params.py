from threading import Event, get_ident
from types import SimpleNamespace

import pytest

from openpilot.nrdr.hooks.controlsd import refresh_live_parameter_settings
from openpilot.nrdr.params import CONTROL_GROUPS, PLANNER_GROUPS, LiveParams, ParamGroup, REFRESH_PERIOD


class RecordingParams:
  def __init__(self, values):
    self.values = values
    self.reads = []
    self.fail_keys = set()
    self.read_event = Event()

  def get(self, key):
    self.reads.append((key, get_ident()))
    self.read_event.set()
    if key in self.fail_keys:
      raise OSError(key)
    return self.values.get(key)

  def put(self, key, value):
    self.values[key] = value

  def put_bool(self, key, value):
    self.values[key] = b"1" if value else b"0"


def _poll_cycle(reader):
  for _ in reader.groups:
    reader.poll_once()


def test_staggered_groups_publish_atomically():
  groups = (ParamGroup(("a", "b")), ParamGroup(("c",)), ParamGroup(("d",)))
  params = RecordingParams({key: b"1" for group in groups for key in group.keys})
  reader = LiveParams(groups, params=params, start_worker=False)
  initial = reader.snapshot
  params.values.update({"a": b"2", "b": b"2"})

  assert reader.poll_once()
  assert reader.snapshot is not initial
  assert reader.snapshot.values["a"] == reader.snapshot.values["b"] == b"2"
  assert reader.snapshot.values["c"] == reader.snapshot.values["d"] == b"1"
  assert reader.generation == initial.generation + 1
  assert reader._slot_period * len(groups) == REFRESH_PERIOD
  with pytest.raises(TypeError):
    reader.snapshot.values["key0"] = b"3"


def test_failed_group_retains_last_good_values():
  groups = (ParamGroup(("a", "b")), ParamGroup(("c",)))
  params = RecordingParams({"a": b"1", "b": b"1", "c": b"1"})
  reader = LiveParams(groups, params=params, start_worker=False)
  initial = reader.snapshot
  params.values = {"a": b"2", "b": b"2", "c": b"2"}
  params.fail_keys.add("b")

  assert not reader.poll_once()
  assert reader.snapshot is initial
  assert reader.generation == initial.generation

  params.fail_keys.clear()
  reader.poll_once()
  assert reader.snapshot.values["c"] == b"2"
  reader.poll_once()
  assert reader.snapshot is not initial
  assert reader.snapshot.values["a"] == reader.snapshot.values["b"] == b"2"

  params.values["b"] = None
  reader._slot = 0
  assert not reader.poll_once()
  assert reader.snapshot.values["a"] == reader.snapshot.values["b"] == b"2"


def test_nnlc_enable_and_gains_publish_together():
  values = {key: b"1" for group in CONTROL_GROUPS for key in group.keys}
  values["NrdrNnlcEnabled"] = b"0"
  params = RecordingParams(values)
  reader = LiveParams(CONTROL_GROUPS, params=params, start_worker=False)
  initial = reader.snapshot

  params.values.update({
    "NrdrNnlcEnabled": b"1",
    "NrdrNnlcActivationSpeed": b"45",
    "NrdrNnlcKpGain": b"125",
    "NrdrNnlcKfGain": b"60",
    "NrdrNnlcKiGain": b"15",
  })
  _poll_cycle(reader)

  assert reader.snapshot is not initial
  assert reader.get_bool("NrdrNnlcEnabled")
  assert reader.get("NrdrNnlcActivationSpeed") == b"45"
  assert reader.get("NrdrNnlcKpGain") == b"125"
  assert reader.get("NrdrNnlcKfGain") == b"60"
  assert reader.get("NrdrNnlcKiGain") == b"15"


def test_roen_setting_reaches_control_and_planner_snapshots():
  control_keys = {key for group in CONTROL_GROUPS for key in group.keys}
  planner_keys = {key for group in PLANNER_GROUPS for key in group.keys}
  assert "NrdrRoenAccelerationLimits" in control_keys
  assert "NrdrRoenAccelerationLimits" in planner_keys


def test_personality_pid_scales_and_learning_gate_publish_atomically():
  scale_keys = {
    "LongPidTuneScaleAggressive",
    "LongPidTuneScaleStandard",
    "LongPidTuneScaleRelaxed",
    "LongPidTuneScaleEcon",
  }
  matching_groups = [group for group in CONTROL_GROUPS if scale_keys.intersection(group.keys)]

  assert len(matching_groups) == 1
  assert scale_keys.issubset(matching_groups[0].keys)
  assert "HondaLiveLearningGas" in matching_groups[0].keys


def test_deprecated_steer_ratio_mode_is_not_polled_by_controller():
  control_keys = {key for group in CONTROL_GROUPS for key in group.keys}
  assert "NrdrLegacyDualBpSteerRatio" not in control_keys


def test_learning_toggles_preserve_typed_boolean_values():
  values = {
    "NrdrLearnSteerRatio": False,
    "NrdrLearnStiffness": True,
    "NrdrLearnAngleOffset": False,
  }
  reader = LiveParams((ParamGroup(tuple(values)),), params=RecordingParams(values), start_worker=False)
  controls = SimpleNamespace(nrdr_live_params=reader)

  refresh_live_parameter_settings(controls, None)

  assert not controls.learn_steer_ratio
  assert controls.learn_stiffness
  assert not controls.learn_angle_offset


def test_worker_owns_periodic_params_io():
  params = RecordingParams({"a": b"1", "b": b"2"})
  reader = LiveParams((ParamGroup(("a",)), ParamGroup(("b",))), params=params,
                      refresh_period=0.02, start_worker=True)
  main_thread = get_ident()
  params.reads.clear()
  params.read_event.clear()
  try:
    assert params.read_event.wait(1.0)
    reader.close()
    assert all(thread_id != main_thread for _, thread_id in params.reads)
    read_count = len(params.reads)
    for _ in range(100):
      assert reader.snapshot.values
    assert len(params.reads) == read_count
  finally:
    reader.close()
