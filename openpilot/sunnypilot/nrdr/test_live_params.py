from threading import Event, get_ident
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.nrdr.controlsd import refresh_engagement_latches, refresh_live_parameter_settings
from openpilot.sunnypilot.nrdr.live_params import (
  CONTROL_GROUPS,
  ENGAGEMENT_LATCHED_LATERAL_GROUPS,
  ENGAGEMENT_LATCHED_LATERAL_KEYS,
  PLANNER_GROUPS,
  LiveParams,
  ParamGroup,
  REFRESH_PERIOD,
)


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


def test_steer_ratio_mode_and_manual_pair_publish_as_one_snapshot():
  control_keys = {key for group in CONTROL_GROUPS for key in group.keys}
  sr_groups = [group for group in CONTROL_GROUPS if "NrdrSteerRatioMode" in group.keys]
  assert len(sr_groups) == 1
  assert sr_groups[0].keys == (
    "NrdrSteerRatioMode", "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal",
  )
  assert "NrdrLegacyDualBpSteerRatio" not in control_keys
  assert "NrdrLearnSteerRatio" not in control_keys
  assert "NrdrLaneChangeEndpointSteerRatio" not in control_keys
  assert not any(key.startswith(("NrdrSteerRatioCenter", "NrdrSteerRatioOuter")) for key in control_keys)


def test_interpolated_torque_controls_publish_as_one_snapshot():
  matching = [group for group in CONTROL_GROUPS if "NrdrInterpolatedTorquePifBlend" in group.keys]
  assert len(matching) == 1
  assert matching[0].keys == (
    "NrdrInterpolatedTorquePifBlend",
    "NrdrInterpolatedTorqueShare",
    "NrdrInterpolatedTorqueLatAccelFactor",
    "NrdrInterpolatedTorqueFriction",
    "NrdrInterpolatedTorqueFrictionStandard",
    "NrdrInterpolatedTorqueFrictionHighway",
  )


def test_engagement_latch_refresh_is_exactly_nine_keys_and_atomic_on_failure():
  keys = tuple(key for group in ENGAGEMENT_LATCHED_LATERAL_GROUPS for key in group.keys)
  assert len(keys) == len(set(keys)) == 9
  assert ENGAGEMENT_LATCHED_LATERAL_KEYS == frozenset(keys)
  params = RecordingParams(dict.fromkeys(keys, b"1"))
  reader = LiveParams(ENGAGEMENT_LATCHED_LATERAL_GROUPS, params=params, start_worker=False)
  initial = reader.snapshot
  initial_generation = reader.generation

  params.values = dict.fromkeys(keys, b"2")
  params.fail_keys.add("NrdrSteerRatioManualCenter")
  params.reads.clear()
  assert not reader.refresh_groups_atomic(ENGAGEMENT_LATCHED_LATERAL_GROUPS)
  assert reader.snapshot is initial
  assert reader.generation == initial_generation
  assert all(value == b"1" for value in reader.snapshot.values.values())

  params.fail_keys.clear()
  params.reads.clear()
  assert reader.refresh_groups_atomic(ENGAGEMENT_LATCHED_LATERAL_GROUPS)
  assert [key for key, _ in params.reads] == list(keys)
  assert reader.generation == initial_generation + 1
  assert all(value == b"2" for value in reader.snapshot.values.values())

  unchanged = reader.snapshot
  assert reader.refresh_groups_atomic(ENGAGEMENT_LATCHED_LATERAL_GROUPS)
  assert reader.snapshot is unchanged

  with pytest.raises(ValueError, match="must belong"):
    reader.refresh_groups_atomic((ParamGroup(("not-owned",)),))


def test_engagement_latch_refresh_reads_only_once_on_falling_edge():
  keys = tuple(key for group in ENGAGEMENT_LATCHED_LATERAL_GROUPS for key in group.keys)
  params = RecordingParams(dict.fromkeys(keys, b"1"))
  reader = LiveParams(ENGAGEMENT_LATCHED_LATERAL_GROUPS, params=params, start_worker=False)
  controls = SimpleNamespace(nrdr_live_params=reader, nrdr_lateral_active=False)
  params.reads.clear()

  assert not refresh_engagement_latches(controls, False)
  assert not refresh_engagement_latches(controls, True)
  assert not refresh_engagement_latches(controls, True)
  assert params.reads == []

  params.values = dict.fromkeys(keys, b"2")
  assert refresh_engagement_latches(controls, False)
  assert [key for key, _ in params.reads] == list(keys)
  read_count = len(params.reads)
  assert not refresh_engagement_latches(controls, False)
  assert len(params.reads) == read_count


def test_engaged_edit_activates_on_immediate_disengage_reengage():
  values = {
    "NrdrInterpolatedTorquePifBlend": True,
    "NrdrInterpolatedTorqueShare": 25,
    "NrdrInterpolatedTorqueLatAccelFactor": 6.0,
    "NrdrInterpolatedTorqueFriction": 0.4,
    "NrdrInterpolatedTorqueFrictionStandard": 0.5,
    "NrdrInterpolatedTorqueFrictionHighway": 0.6,
    "NrdrSteerRatioMode": 0,
    "NrdrSteerRatioManualCenter": 15.38,
    "NrdrSteerRatioManualFinal": 10.93,
  }
  params = RecordingParams(values.copy())
  reader = LiveParams(ENGAGEMENT_LATCHED_LATERAL_GROUPS, params=params, start_worker=False)
  controls = SimpleNamespace(nrdr_live_params=reader, nrdr_lateral_active=False)
  keys = tuple(key for group in ENGAGEMENT_LATCHED_LATERAL_GROUPS for key in group.keys)

  class EngagementLatch:
    def __init__(self):
      self.was_active = False
      self.values = None

    def update(self, active):
      if active and not self.was_active:
        self.values = tuple(reader.snapshot.get(key) for key in keys)
      self.was_active = active

  latch = EngagementLatch()

  assert not refresh_engagement_latches(controls, True)
  latch.update(True)
  assert latch.values[keys.index("NrdrInterpolatedTorqueShare")] == 25

  params.values.update({
    "NrdrInterpolatedTorqueShare": 75,
    "NrdrInterpolatedTorqueFrictionStandard": 0.10,
    "NrdrInterpolatedTorqueFrictionHighway": 0.06,
    "NrdrSteerRatioMode": 3,
  })
  assert not refresh_engagement_latches(controls, True)
  latch.update(True)
  assert latch.values[keys.index("NrdrInterpolatedTorqueShare")] == 25

  assert refresh_engagement_latches(controls, False)
  latch.update(False)
  assert not refresh_engagement_latches(controls, True)
  latch.update(True)
  assert latch.values[keys.index("NrdrInterpolatedTorqueShare")] == 75
  assert latch.values[keys.index("NrdrInterpolatedTorqueFrictionStandard")] == 0.10
  assert latch.values[keys.index("NrdrInterpolatedTorqueFrictionHighway")] == 0.06
  assert latch.values[keys.index("NrdrSteerRatioMode")] == 3


def test_learning_toggles_preserve_typed_boolean_values():
  values = {
    "NrdrLearnStiffness": True,
    "NrdrLearnAngleOffset": False,
  }
  reader = LiveParams((ParamGroup(tuple(values)),), params=RecordingParams(values), start_worker=False)
  controls = SimpleNamespace(nrdr_live_params=reader)

  refresh_live_parameter_settings(controls, None)

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
