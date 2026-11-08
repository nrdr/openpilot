"""Parked saved-tuning RPC admission, real parameter types and fresh road gates."""
import ast
import itertools
import re

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.nrdr.params.tuning_policy import MVL_LOCK_KEYS
from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as base_rpc
from openpilot.nrdr.tests.test_nidec_pcm_experiments import cp_bytes

LOCK_KEYS = MVL_LOCK_KEYS
MODE_KEYS = {"HondaLiveLearningGas",
             "NrdrHondaPcmMode", "NrdrHondaWindBrake", "NrdrMvlPcmDeadzone"}
REGISTRY = {}
for relative in ("openpilot/common/params_keys.h", "openpilot/nrdr/params/generated/params_keys.inc"):
  REGISTRY.update(re.findall(r'\{"([^"]+)", \{[^{}\n]*,\s*(BOOL|INT|FLOAT)\s*[,}]',
                            (ROOT / relative).read_text(encoding="utf-8")))
CONTEXTS = ("mvl_saved", "mvl_active", "legacy_saved", "legacy_active", "both_saved", "both_active")


@pytest.fixture
def rpc():
  # Execute the real RPC and admission helpers, excluding only daemon/hardware imports.
  save, params, caps = base_rpc.__wrapped__()
  types = save.__globals__["ParamKeyType"]
  params.get_type = lambda key: getattr(types, REGISTRY[key])
  caps.update(nrdr_honda_pcm_experiments_available=True, nrdr_mvl_pcm_deadzone_available=True,
              nrdr_honda_tuning_available=True)
  path = ROOT / "openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  save.__globals__["BLOCKED_PARAMS"] = next(ast.literal_eval(node.value) for node in tree.body
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "BLOCKED_PARAMS" for target in node.targets))
  params.values.update(CarParamsPersistent=cp_bytes(), SavedLearning=b"keep learning", ModelSelection="keep model")
  return save, params, caps


def choice(key):
  if key == "NrdrHondaPcmMode":
    return 2
  if key == "NrdrMvlPcmDeadzone":
    return 5
  return {"BOOL": True, "INT": 37, "FLOAT": 1.25}[REGISTRY[key]]


def wire(value, compressed=False):
  return encoded(int(value) if type(value) is bool else value, compressed)


def context(params, mode):
  saved = mode.endswith("saved")
  mvl, legacy = mode.startswith(("mvl", "both")), mode.startswith(("legacy", "both"))
  flags = (HondaFlags.MVL_LONGITUDINAL if mvl and not saved else 0) | (524288 if legacy and not saved else 0)
  params.values.update(HondaLiveLearningGas=mvl and saved, NrdrHondaLegacyPcm=legacy and saved, CarParamsPersistent=cp_bytes(flags))


def assert_only_requested_values_changed(params, before, requested):
  assert all(params.get(key) == value and type(params.get(key)) is type(value) for key, value in requested.items())
  assert {key for key, _ in params.writes} == set(requested) | {"ParamsVersion"} | (
    {"OnroadCycleRequested"} if MODE_KEYS.intersection(requested) else set())
  assert all(params.get(key) == value for key, value in before.items() if key not in requested)


def test_every_mode_lock_key_has_a_supported_real_registered_type():
  assert LOCK_KEYS <= REGISTRY.keys()
  assert {REGISTRY[key] for key in LOCK_KEYS} == {"BOOL", "INT", "FLOAT"}
  assert all(REGISTRY[key] == "INT" for key in ("SpeedLimitMode", "SpeedLimitPolicy", "SpeedLimitOffsetType", "SpeedLimitValueOffset"))


@pytest.mark.parametrize("key", sorted(LOCK_KEYS))
@pytest.mark.parametrize("mode", CONTEXTS)
@pytest.mark.parametrize("compressed", [False, True])
def test_every_conflicting_saved_tune_is_parked_configurable_without_resets(rpc, key, mode, compressed):
  save, params, _ = rpc
  context(params, mode)
  before = dict(params.values)
  selected = choice(key)
  save({key: wire(selected, compressed)}, compressed)
  assert_only_requested_values_changed(params, before, {key: selected})


@pytest.mark.parametrize("mvl,legacy", list(itertools.product((False, True), repeat=2)))
@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("reverse,compressed", list(itertools.product((False, True), repeat=2)))
def test_modes_and_all_saved_tunes_can_share_either_batch_order(rpc, mvl, legacy, active, reverse, compressed):
  save, params, _ = rpc
  context(params, "both_active" if active else "both_saved")
  before = dict(params.values)
  requested = {"HondaLiveLearningGas": mvl, "NrdrHondaPcmMode": 2 if legacy else 0}
  requested.update({key: choice(key) for key in sorted(LOCK_KEYS) if key != "HondaLiveLearningGas"})
  entries = [(key, wire(value, compressed)) for key, value in requested.items()]
  save(dict(reversed(entries) if reverse else entries), compressed)
  assert_only_requested_values_changed(params, before, requested)
  assert params.get_bool("OnroadCycleRequested")


@pytest.mark.parametrize("key", sorted(LOCK_KEYS))
@pytest.mark.parametrize("mode", CONTEXTS)
def test_saved_and_active_modes_do_not_lock_ordinary_tuning(rpc, key, mode):
  save, params, _ = rpc
  context(params, mode)
  params.values["IsOffroad"] = False
  before = dict(params.values)
  requested = {"ExperimentalMode": True, key: choice(key)}
  save({name: wire(value) for name, value in requested.items()})
  if key == "NrdrStandstillGapExtra":
    assert params.get(key) is None
    requested.pop(key)  # Existing explicit offroad-only gap setting, not an MVL lock.
  assert_only_requested_values_changed(params, before, requested)


@pytest.mark.parametrize("key", sorted(MODE_KEYS))
@pytest.mark.parametrize("offroad", [False, None])
def test_drive_mode_choices_never_save_onroad_or_with_unknown_road_state(rpc, key, offroad):
  save, params, _ = rpc
  params.values["IsOffroad"] = offroad
  with pytest.raises(ValueError):
    save({"StaticFeedforwardLong": wire(True), key: wire(choice(key))})
  assert not params.writes


@pytest.mark.parametrize("key", ["StaticFeedforwardLong", "LongPidTuneScaleStandard", "SpeedLimitValueOffset"])
def test_existing_unlocked_onroad_tuning_behavior_is_preserved(rpc, key):
  save, params, _ = rpc
  params.values["IsOffroad"] = False
  before = dict(params.values)
  save({key: wire(choice(key))})
  assert_only_requested_values_changed(params, before, {key: choice(key)})


@pytest.mark.parametrize("key,bad", [
  ("NrdrHondaPcmFixedCruise", "invalid"), ("NrdrHondaLegacyPcm", "invalid"), ("HondaLiveLearningGas", "invalid"),
  ("NrdrHondaPcmMode", 3), ("NrdrHondaWindBrake", "invalid"), ("NrdrMvlPcmDeadzone", 3),
  ("StaticFeedforwardLong", "invalid"), ("SpeedLimitPolicy", "1.5"), ("LongPidTuneScaleStandard", "invalid"),
  ("HondaStopAccel", "invalid"), ("NrdrStandstillGapExtra", "nan"), ("NrdrCruiseMismatchCorrection", "inf"),
])
@pytest.mark.parametrize("reverse,compressed", list(itertools.product((False, True), repeat=2)))
def test_invalid_tuning_or_mode_rejects_entire_batch_before_writes(rpc, key, bad, reverse, compressed):
  save, params, _ = rpc
  context(params, "both_active")
  entries = [("ExperimentalMode", wire(True, compressed)),
             (key, encoded(bad, compressed))]
  with pytest.raises(ValueError):
    save(dict(reversed(entries) if reverse else entries), compressed)
  assert not params.writes


@pytest.mark.parametrize("key", ["StaticFeedforwardLong", "LongPidTuneScaleStandard", "HondaStopAccel"])
@pytest.mark.parametrize("payload,compressed", [("!bad-base64", False), ("!bad-base64", True), (encoded(1), True)])
def test_bad_tuning_transport_rejects_batch_before_writes(rpc, key, payload, compressed):
  save, params, _ = rpc
  with pytest.raises(ValueError):
    save({"ExperimentalMode": wire(True, compressed), key: payload}, compressed)
  assert not params.writes


@pytest.mark.parametrize("key,cap", [
  ("HondaLiveLearningGas", "nrdr_honda_mvl_selection_available"),
  ("NrdrHondaPcmMode", "nrdr_honda_pcm_tuning_available"), ("NrdrHondaWindBrake", "nrdr_honda_pcm_tuning_available"),
  ("NrdrMvlPcmDeadzone", "nrdr_mvl_pcm_deadzone_available"),
])
@pytest.mark.parametrize("change", ["unavailable", "missing", "lost_before_write", "started_during_capability_check", "started_before_loop"])
def test_mode_hardware_and_fresh_road_checks_remain_fail_closed(rpc, key, cap, change):
  save, params, caps = rpc
  if change in ("unavailable", "missing"):
    caps[cap] = False if change == "unavailable" else None
  calls = 0

  def capabilities():
    nonlocal calls
    calls += 1
    if calls == 1 and change == "started_before_loop":
      params.values["IsOffroad"] = False
    if calls > 1:
      if change == "lost_before_write":
        return {**caps, cap: False}
      if change == "started_during_capability_check":
        params.values["IsOffroad"] = False
    return dict(caps)

  save.__globals__["_vehicle_tuning_capabilities"] = capabilities
  with pytest.raises(ValueError):
    save({key: wire(choice(key))})
  assert not params.writes


@pytest.mark.parametrize("key", sorted(LOCK_KEYS - MODE_KEYS))
def test_parked_generic_tuning_rechecks_road_after_validation(rpc, key):
  save, params, _ = rpc
  context(params, "both_active")
  get_type = params.get_type

  def starts_during_validation(name):
    params.values["IsOffroad"] = False
    return get_type(name)

  params.get_type = starts_during_validation
  before = dict(params.values)
  save({key: wire(choice(key))})
  before["IsOffroad"] = False
  requested = {} if key == "NrdrStandstillGapExtra" else {key: choice(key)}
  assert_only_requested_values_changed(params, before, requested)


def test_each_generic_write_rechecks_road_after_preceding_saved_value(rpc):
  save, params, _ = rpc
  context(params, "both_active")
  put = params.put

  def starts_after_first(name, value, **kwargs):
    put(name, value, **kwargs)
    if name == "StaticFeedforwardLong":
      params.values["IsOffroad"] = False

  params.put = starts_after_first
  save({"StaticFeedforwardLong": wire(True), "LongPidTuneScaleStandard": wire(125)})
  assert params.writes == [("StaticFeedforwardLong", True), ("LongPidTuneScaleStandard", 125), ("ParamsVersion", "1")]
  assert params.get("LongPidTuneScaleStandard") == 125


def test_client_cannot_forge_offroad_to_bypass_mode_conflicts(rpc):
  save, params, _ = rpc
  context(params, "both_active")
  params.values["IsOffroad"] = False
  save({"IsOffroad": wire(True), "StaticFeedforwardLong": wire(True)})
  assert params.get("IsOffroad") is False
  assert params.writes == [("StaticFeedforwardLong", True), ("ParamsVersion", "1")]


@pytest.mark.parametrize("offroad", [True, False, None])
@pytest.mark.parametrize("pending", [False, True])
def test_completed_suggested_marker_allows_parked_real_typed_edits_but_pending_request_blocks(rpc, offroad, pending):
  save, params, _ = rpc
  params.values.update(IsOffroad=offroad, NrdrSuggestedSettings=True, NrdrHandcraftedLateralTune=pending, LatPScaleStandard=100)
  before = dict(params.values)
  save({"LatPScaleStandard": wire(120)})
  allowed = offroad is True and not pending
  assert params.get("LatPScaleStandard") == (120 if allowed else 100)
  assert type(params.get("LatPScaleStandard")) is int
  assert params.writes == ([("LatPScaleStandard", 120)] if allowed else []) + [("ParamsVersion", "1")]
  assert all(params.get(key) == value for key, value in before.items() if key != "LatPScaleStandard")


@pytest.mark.parametrize("offroad", [True, False, None])
@pytest.mark.parametrize("pending", [False, True])
@pytest.mark.parametrize("mode", [0, 1, 2])
def test_lane_guidance_under_suggested_preserves_marker_and_pending_guard(rpc, offroad, pending, mode):
  save, params, caps = rpc
  params.values.update(IsOffroad=offroad, NrdrSuggestedSettings=True, NrdrHandcraftedLateralTune=pending,
                       LaneGuidanceMode=0, LaneCentering=False)
  caps["custom_model_active"] = True
  save({"LaneGuidanceMode": wire(mode)})
  allowed = offroad is True and not pending
  assert params.get("LaneGuidanceMode") == (mode if allowed else 0)
  assert params.get("LaneCentering") is (allowed and mode == 1)
  assert params.get("NrdrSuggestedSettings") is True
  assert params.get("NrdrHandcraftedLateralTune") is pending
  assert {name for name, _ in params.writes} == ({"LaneGuidanceMode", "LaneCentering"} if allowed else set()) | {"ParamsVersion"}


@pytest.mark.parametrize("custom_model", [False, None])
def test_parked_suggested_marker_does_not_bypass_sunny_model_requirement(rpc, custom_model):
  save, params, caps = rpc
  params.values.update(NrdrSuggestedSettings=True, LaneGuidanceMode=0)
  caps["custom_model_active"] = custom_model
  with pytest.raises(ValueError, match="non-Default custom model"):
    save({"LatPScaleStandard": wire(120), "LaneGuidanceMode": wire(2)})
  assert not params.writes
  assert params.get("NrdrSuggestedSettings") is True


def test_parked_suggested_marker_does_not_bypass_firmware_controller_lock(rpc):
  save, params, _ = rpc
  params.values.update(NrdrSuggestedSettings=True, NrdrLateralController=1, LatPScaleStandard=100)
  save({"LatPScaleStandard": wire(120)})
  assert params.get("LatPScaleStandard") == 100
  assert params.get("NrdrSuggestedSettings") is True
  assert params.writes == [("ParamsVersion", "1")]
