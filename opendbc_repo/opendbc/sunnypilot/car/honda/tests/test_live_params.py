from threading import Event, get_ident

from opendbc.sunnypilot.car.honda.live_params import FAST_PARAM_GROUP, HondaLiveParams, PARAM_GROUPS, REFRESH_PERIOD


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


def test_groups_cover_each_key_once():
  keys = [key for group in (*PARAM_GROUPS, FAST_PARAM_GROUP) for key in group]
  assert len(keys) == len(set(keys))
  assert set(keys) == {
    "HondaOverrideFadeDownSecs", "HondaOverrideFadeUpSecs", "HondaOverrideTorqueScale", "HondaDriverAssistDuringOverride",
    "HondaTorqueLowPassFilter", "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
    "HondaSteerDeltaLimiter", "HondaSteerDeltaUp", "HondaSteerDeltaDown", "HondaLiveLearningGas",
    "HondaStoppingDecelRate", "NrdrHondaEcuMatchedLong", "NrdrHondaFullBrakeAuthority", "NrdrRoenAccelerationLimits",
    "HondaAltDashboardSpeed", "HondaAltDashboardDistance",
    "NrdrClearDashFaults", "HondaSpoofCameraMessages", "NrdrCruiseButtonSubMode", "NrdrHudSubModeUntil",
    "NrdrDriverOverrideThreshold", "HondaCenterBoostThreshold", "NrdrOverrideThresholdCenterBoost",
    "NrdrIncreaseOverrideTolerance",
  }


def test_group_refresh_is_atomic_and_staggered():
  values = {key: 1 for group in PARAM_GROUPS for key in group}
  params = RecordingParams(values)
  reader = HondaLiveParams(params=params, start_worker=False)
  first_group = PARAM_GROUPS[0]
  initial = reader.snapshot
  params.values.update({key: 2 for key in first_group})

  assert reader.poll_once()
  assert reader.snapshot is not initial
  assert all(reader.snapshot.get(key) == 2 for key in first_group)
  assert reader._slot_period * len(PARAM_GROUPS) == REFRESH_PERIOD


def test_failed_group_retains_last_good_values():
  values = {key: 1 for group in PARAM_GROUPS for key in group}
  params = RecordingParams(values)
  reader = HondaLiveParams(params=params, start_worker=False)
  initial = reader.snapshot
  failed_key = PARAM_GROUPS[0][-1]
  params.values.update({key: 2 for key in PARAM_GROUPS[0]})
  params.fail_keys.add(failed_key)

  assert not reader.poll_once()
  assert reader.snapshot is initial
  assert all(reader.snapshot.get(key) == 1 for key in PARAM_GROUPS[0])

  params.fail_keys.clear()
  params.values[failed_key] = None
  reader._slot = 0
  assert not reader.poll_once()
  assert reader.snapshot is initial


def test_hud_deadline_uses_fast_lane():
  values = {key: 1 for group in PARAM_GROUPS for key in group}
  values[FAST_PARAM_GROUP[0]] = 10.0
  params = RecordingParams(values)
  reader = HondaLiveParams(params=params, start_worker=False)
  params.values[FAST_PARAM_GROUP[0]] = 20.0

  assert reader.poll_fast()
  assert reader.snapshot.get(FAST_PARAM_GROUP[0]) == 20.0


def test_worker_owns_periodic_io():
  values = {key: 1 for group in PARAM_GROUPS for key in group}
  params = RecordingParams(values)
  reader = HondaLiveParams(params=params, refresh_period=0.02, start_worker=True)
  main_thread = get_ident()
  params.reads.clear()
  params.read_event.clear()
  try:
    assert params.read_event.wait(1.0)
    reader.close()
    assert all(thread_id != main_thread for _, thread_id in params.reads)
  finally:
    reader.close()
