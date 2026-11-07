"""Default-off startup contract, native/C4 presentation, and Sunnylink admission."""
import ast
from dataclasses import FrozenInstanceError
import itertools
import json

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.cereal import custom
from openpilot.nrdr.car.opendbc import FAST_PARAM_GROUP, SLOW_PARAM_GROUPS
from openpilot.nrdr.params.nidec_pcm import PCM_EXPERIMENTS, PCM_EXPERIMENT_DETAILS, decode_pcm_experiment
from openpilot.nrdr.params.tuning_policy import LEGACY_PCM_LOCK_KEYS, legacy_pcm_tuning_locked, tuning_write_allowed
from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT, Params, Widget, _font_advance_upper_bound, native_layout, state as base_state
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as rpc_fixture
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.nrdr.ui import honda_pcm
from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC

KEYS = tuple(PCM_EXPERIMENTS)
FIXED, LEGACY = KEYS
FLAGS = (HondaFlags.NIDEC_PCM_FIXED_CRUISE, HondaFlags.NIDEC_PCM_LEGACY)
CAP = "nrdr_honda_pcm_experiments_available"
INVALID = (None, 0, 1, 2, -1, .0, 1.0, "true", "false", "", "yes", "garbage", " 1", "1\n", b"true", {}, [])


def state(**kwargs):
  return base_state(**({"flags": int(HondaFlags.NIDEC)} | kwargs))


def cp_bytes(flags=0, **kwargs):
  return car.CarParams.new_message(**({"brand": "honda", "carFingerprint": "HONDA_CIVIC", "openpilotLongitudinalControl": True,
                                      "flags": int(HondaFlags.NIDEC | flags)} | kwargs)).to_bytes()


def mici_control(ui, key):
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PcmExperimentControl"]
  env = {**vars(honda_pcm), "BigToggle": Widget, "ui_state": ui, "tr": lambda s: s, "PCM_EXPERIMENT_DETAILS": PCM_EXPERIMENT_DETAILS}
  exec(compile(tree, str(path), "exec"), env)
  return env["PcmExperimentControl"](key)


@pytest.fixture
def rpc():
  save, params, caps = rpc_fixture.__wrapped__()
  caps[CAP] = True
  return save, params, caps


@pytest.mark.parametrize("raw,expected", [(False, False), (True, True), ("0", False), ("1", True), (b"0", False), (b"1", True)])
@pytest.mark.parametrize("key,field", [(FIXED, "nidec_fixed_cruise"), (LEGACY, "nidec_legacy_pcm")])
def test_host_latches_independent_booleans_without_live_polling_or_saved_value_rewrites(tmp_path, raw, expected, key, field):
  params = FakeParams({key: raw, "HondaLiveLearningGas": True, "NrdrHondaPcmMode": 2, "NrdrHondaWindBrake": True})
  config = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  assert getattr(config.honda, field) is expected
  assert config.honda.mvl_longitudinal and config.honda.nidec_pcm_mode == 2 and config.honda.nidec_wind_brake
  grouped = set(itertools.chain.from_iterable(SLOW_PARAM_GROUPS)) | set(FAST_PARAM_GROUP)
  assert not grouped.intersection(KEYS)
  params.values[key] = not expected
  config.honda.provider.refresh_all()
  assert getattr(config.honda, field) is expected
  with pytest.raises(FrozenInstanceError):
    setattr(config.honda, field, not expected)
  restarted = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "new.json")
  assert getattr(restarted.honda, field) is not expected
  assert not params.writes


@pytest.mark.parametrize("raw", INVALID)
@pytest.mark.parametrize("key,field", [(FIXED, "nidec_fixed_cruise"), (LEGACY, "nidec_legacy_pcm")])
def test_malformed_host_values_fail_off_without_repair(tmp_path, raw, key, field):
  assert decode_pcm_experiment(raw) is None
  params = FakeParams({key: raw})
  config = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  assert getattr(config.honda, field) is False
  assert not params.writes


@pytest.mark.parametrize("car_id", list(CAR))
@pytest.mark.parametrize("key", KEYS)
def test_only_exact_civic_is_offered_and_save_never_forces_other_values(car_id, key):
  ui = state(carFingerprint=str(car_id))
  ui.params.values.update(HondaLiveLearningGas=True, NrdrHondaPcmMode=2, NrdrHondaWindBrake=True)
  expected = car_id == CAR.HONDA_CIVIC
  assert honda_pcm.pcm_experiments_available(ui.CP, ui.CP_SP, ui.params) is expected
  assert honda_pcm.save_pcm_experiment(ui, key, True) is expected
  assert ui.params.writes == ([(key, True), ("OnroadCycleRequested", True)] if expected else [])


@pytest.mark.parametrize("saved_mvl,active_mvl,fixed,legacy", list(itertools.product((False, True), repeat=4)))
def test_both_controls_remain_independent_and_available_under_mvl_or_legacy(saved_mvl, active_mvl, fixed, legacy):
  flags = HondaFlags.NIDEC | (HondaFlags.MVL_LONGITUDINAL if active_mvl else 0) | HondaFlags.NIDEC_PCM_LEGACY
  ui = state(flags=int(flags))
  ui.params.values.update(HondaLiveLearningGas=saved_mvl)
  large = native_layout(ui)
  for key, choice in ((FIXED, fixed), (LEGACY, legacy)):
    assert tuning_write_allowed(ui.params, key, CP=ui.CP)
    large._pcm_experiments[key].kwargs["callback"](int(choice))
    large._update_state()
    assert large._pcm_experiments[key].enabled
    assert large._pcm_experiments[key].value == int(choice)
    compact = mici_control(ui, key)
    assert compact.enabled()
    compact._select(not choice)
    assert ui.params.get(key) is not choice
  assert ui.params.get("HondaLiveLearningGas") is saved_mvl
  assert {key for key, _ in ui.params.writes} <= {*KEYS, "OnroadCycleRequested"}


def make_ineligible(ui, case):
  if case == "onroad":
    ui.is_offroad = lambda: False
  elif case == "missing_cp":
    ui.CP = None
  elif case == "missing_sp":
    ui.CP_SP = None
  elif case == "interceptor":
    ui.CP_SP.enableGasInterceptor = True
  elif case == "stock_flag":
    ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  elif case == "stock":
    ui.CP.openpilotLongitudinalControl = False
  elif case == "other_brand":
    ui.CP.brand = "toyota"
  elif case == "other_civic":
    ui.CP.carFingerprint = CAR.HONDA_CIVIC_BOSCH
  elif case in ("dashcamOnly", "passive"):
    setattr(ui.CP, case, True)
  elif case == "no_nidec":
    ui.CP.flags = 0
  elif case == "bosch_flag":
    ui.CP.flags |= int(HondaFlags.BOSCH)
  else:
    ui.params.values["CarPlatformBundle"] = True if case == "bad_bundle" else {"brand": "honda", "platform": "HONDA_CLARITY"}


@pytest.mark.parametrize("case", ["onroad", "missing_cp", "missing_sp", "interceptor", "stock_flag", "stock", "other_brand", "other_civic",
                                  "dashcamOnly", "passive", "no_nidec", "bosch_flag", "bad_bundle", "stale_bundle"])
@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("native", ["large", "mici"])
def test_click_time_vehicle_and_parked_rechecks(case, key, native):
  ui = state()
  control = native_layout(ui) if native == "large" else mici_control(ui, key)
  make_ineligible(ui, case)
  if native == "large":
    control._pcm_experiments[key].kwargs["callback"](1)
  else:
    control._select(True)
  control._update_state()
  assert not ui.params.writes
  if native == "large":
    item = control._pcm_experiments[key]
    assert not item.enabled and item.value == 0 and item.param_key is None
  else:
    assert not control.enabled()


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("value", [None, -1, 2, True, False, "1", 1.0])
def test_native_segment_indices_are_strict(key, value):
  ui = state()
  native_layout(ui)._pcm_experiments[key].kwargs["callback"](value)
  assert not ui.params.writes


@pytest.mark.parametrize("key,flag", list(zip(KEYS, FLAGS, strict=True)))
@pytest.mark.parametrize("saved,active", list(itertools.product((False, True), repeat=2)))
@pytest.mark.parametrize("offroad", [False, True])
def test_saved_switch_never_claims_running_mode_and_pending_off_is_retained(key, flag, saved, active, offroad):
  ui = state(flags=int(HondaFlags.NIDEC | (flag if active else 0)))
  ui.is_offroad = lambda: offroad
  ui.params.values["IsOffroad"] = offroad
  ui.params.values[key] = saved
  status = honda_pcm.pcm_experiment_status(ui.CP, ui.CP_SP, ui.params, key)
  selected = "On" if saved else "Off"
  if offroad:
    assert status == f"Saved: {selected}. Applies next drive."
  else:
    assert status.startswith("Running: On." if active else "Running: Off.")
    assert ("applies next drive" in status) is (saved != active)
  # Native UI road state wins even while the stored road-state value is stale.
  ui.params.values["IsOffroad"] = not offroad
  compact = mici_control(ui, key)
  assert ("→" in compact.value) is (not offroad and saved != active)
  if offroad:
    assert compact.value == f"Next: {selected}"
  large = native_layout(ui)
  large._update_state()
  assert large._pcm_experiments[key].value == int(saved)
  assert status in large._pcm_experiments[key].kwargs["description"]()


@pytest.mark.parametrize("saved,active", list(itertools.product((False, True), repeat=2)))
@pytest.mark.parametrize("key", sorted(LEGACY_PCM_LOCK_KEYS))
def test_legacy_locks_conflicts_until_restart_without_erasing_saved_values(saved, active, key):
  params = Params(NrdrHondaLegacyPcm=saved, CarParamsPersistent=cp_bytes(HondaFlags.NIDEC_PCM_LEGACY if active else 0), **{key: 123})
  assert legacy_pcm_tuning_locked(params) is (saved or active)
  assert tuning_write_allowed(params, key) is not (saved or active)
  assert params.get(key) == 123 and not params.writes


@pytest.mark.parametrize("case", ["interceptor", "stock_flag", "stock", "other_brand", "other_civic", "dashcamOnly", "passive", "no_nidec", "bosch_flag"])
def test_saved_legacy_does_not_lock_other_vehicle_paths(case):
  ui = state()
  ui.params.values[LEGACY] = True
  make_ineligible(ui, case)
  assert not legacy_pcm_tuning_locked(ui.params, ui.CP, ui.CP_SP)
  ui.params.values["HondaLiveLearningGas"] = True
  assert "Legacy" not in honda_pcm.live_gas_status(ui.CP, ui.params, ui.CP_SP)


def test_current_latch_wins_over_persistent_and_bad_cp_fails_closed():
  params = Params(CarParams=cp_bytes(), CarParamsPersistent=cp_bytes(HondaFlags.NIDEC_PCM_LEGACY))
  assert not legacy_pcm_tuning_locked(params)
  params.values["CarParams"] = b"corrupt"
  assert legacy_pcm_tuning_locked(params)
  params.values["CarParams"] = cp_bytes(HondaFlags.NIDEC_PCM_LEGACY)
  params.values["CarParamsSPPersistent"] = custom.CarParamsSP.new_message(enableGasInterceptor=True).to_bytes()
  assert not legacy_pcm_tuning_locked(params)


def test_legacy_supersedes_saved_mvl_status_without_forcing_off():
  ui = state(flags=int(HondaFlags.NIDEC | HondaFlags.NIDEC_PCM_LEGACY | HondaFlags.MVL_LONGITUDINAL))
  ui.params.values.update(NrdrHondaLegacyPcm=True, HondaLiveLearningGas=True, NrdrHondaPcmMode=2, NrdrHondaWindBrake=True, NrdrMvlPcmDeadzone=5)
  assert honda_pcm.live_gas_status(ui.CP, ui.params, is_offroad=False) == "Legacy active\nMVL saved"
  assert honda_pcm.live_gas_status(ui.CP, ui.params, is_offroad=True) == "Legacy next drive\nMVL saved"
  large = native_layout(ui)
  large._update_state()
  for item in (large._live_learning_gas, large._mvl_pcm_deadzone, large._pcm_mode, large._wind_brake, large._static_feedforward_long):
    assert not item.enabled
  assert not honda_pcm.save_live_gas_choice(ui, False)
  assert not honda_pcm.save_pcm_choice(ui, "NrdrHondaPcmMode", 0)
  assert not honda_pcm.save_mvl_pcm_deadzone(ui, 0)
  assert not ui.params.writes
  ui.params.values[LEGACY] = False
  assert honda_pcm.live_gas_status(ui.CP, ui.params, is_offroad=False) == "Legacy active\nMVL next drive"
  assert honda_pcm.live_gas_status(ui.CP, ui.params, is_offroad=True) == "MVL next drive"


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("selected,compressed", list(itertools.product((False, True), repeat=2)))
def test_remote_saves_typed_choices_under_mvl_and_requests_restart(rpc, key, selected, compressed):
  save, params, _ = rpc
  params.values.update(HondaLiveLearningGas=True, CarParamsPersistent=cp_bytes(HondaFlags.MVL_LONGITUDINAL))
  save({key: encoded(int(selected), compressed)}, compressed)
  assert params.get(key) is selected
  assert params.get_bool("HondaLiveLearningGas") and params.get_bool("OnroadCycleRequested")
  assert {key for key, _ in params.writes} == {key, "OnroadCycleRequested", "ParamsVersion"}


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("value", [None, 2, -1, 1.0, "garbage", " 1", "1\n", {}, []])
@pytest.mark.parametrize("compressed", [False, True])
def test_remote_bad_values_reject_entire_batch_before_writes(rpc, key, value, compressed):
  save, params, _ = rpc
  with pytest.raises(ValueError):
    save({"ExperimentalMode": encoded(1, compressed), key: encoded(value, compressed)}, compressed)
  assert not params.writes


@pytest.mark.parametrize("offroad,cap", [(False, True), (True, False), (True, None)])
@pytest.mark.parametrize("key", KEYS)
def test_remote_vehicle_and_road_gate_fail_closed(rpc, key, offroad, cap):
  save, params, caps = rpc
  caps[CAP] = cap
  params.values["IsOffroad"] = offroad
  with pytest.raises(ValueError):
    save({key: encoded(1)})
  assert not params.writes


@pytest.mark.parametrize("change", ["vehicle", "road"])
@pytest.mark.parametrize("key", KEYS)
def test_remote_rechecks_at_write_time(rpc, key, change):
  save, params, caps = rpc
  calls = 0
  def capabilities():
    nonlocal calls
    calls += 1
    if calls == 1:
      if change == "road":
        params.values["IsOffroad"] = False
      return dict(caps)
    return {**caps, CAP: False}
  save.__globals__["_vehicle_tuning_capabilities"] = capabilities
  with pytest.raises(ValueError):
    save({key: encoded(1)})
  assert not params.writes


@pytest.mark.parametrize("key", sorted(LEGACY_PCM_LOCK_KEYS))
@pytest.mark.parametrize("reverse", [False, True])
def test_remote_cannot_enable_legacy_and_write_conflicts_in_either_order(rpc, key, reverse):
  save, params, _ = rpc
  entries = [(LEGACY, encoded(1)), (key, encoded(1))]
  with pytest.raises(ValueError):
    save(dict(reversed(entries) if reverse else entries))
  assert not params.writes


@pytest.mark.parametrize("saved,active", [(False, True), (True, False), (True, True)])
def test_remote_cannot_disable_legacy_and_unlock_conflict_in_same_batch(rpc, saved, active):
  save, params, _ = rpc
  params.values.update(NrdrHondaLegacyPcm=saved, CarParamsPersistent=cp_bytes(HondaFlags.NIDEC_PCM_LEGACY if active else 0))
  with pytest.raises(ValueError):
    save({LEGACY: encoded(0), "NrdrHondaWindBrake": encoded(1)})
  assert not params.writes
  save({LEGACY: encoded(0), FIXED: encoded(1)})
  assert params.get(LEGACY) is False and params.get(FIXED) is True


@pytest.mark.parametrize("key", KEYS)
def test_shared_copy_native_geometry_and_compiled_schema(key):
  ui = state()
  compact, large = mici_control(ui, key), native_layout(ui)
  local = large._pcm_experiments[key].kwargs
  schema = compile_schema(DEFAULT_SRC)
  page = next(p for p in schema["panels"] if p["id"] == "steering")
  panel = next(p for s in page["sections"] for p in s.get("sub_panels", []) if p["id"] == "nrdr_longitudinal")
  web = next(item for item in panel["items"] if item.get("key") == key)
  title, description = PCM_EXPERIMENTS[key]
  assert compact.text == local["title"]() == web["title"] == title
  assert description in compact.kwargs["description"] and description in local["description"]()
  assert web["description"] == description and "needs_onroad_cycle" not in web
  assert web["details"] == PCM_EXPERIMENT_DETAILS[key]
  assert len(description) < 170
  gate = {"type": "capability", "field": CAP, "equals": True}
  assert web["visibility"] == [gate] and web["enablement"] == [{"type": "offroad_only"}, gate]
  assert [label() for label in local["buttons"]] == ["Off", "On"]
  assert schema == json.loads((ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))
  size, width = compact.kwargs["font_size"], compact._title_width_hint()
  lines = []
  for word in title.split():
    joined = f"{lines[-1]} {word}" if lines else word
    if lines and _font_advance_upper_bound("Inter-Bold.ttf", joined, size) <= width:
      lines[-1] = joined
    else:
      lines.append(word)
  title_height = size * 1.16 * (1 + .9 * (len(lines) - 1))
  assert compact._rect.height - 2 * compact.LABEL_VERTICAL_PADDING - title_height - 36 * 1.16 > 10
  for label in ("Off", "On", "Off → On", "On → Off", "Next: On", "Next: Off", "Unavailable"):
    assert _font_advance_upper_bound("Inter-Regular.ttf", label, 36) < compact._subtitle_width_hint()


@pytest.mark.parametrize("key", sorted(LEGACY_PCM_LOCK_KEYS))
def test_remote_visual_lock_covers_every_legacy_conflict(key):
  item = apply_sunnylink_metadata({"key": key})
  assert {"type": "not", "condition": {"type": "capability", "field": "nrdr_honda_legacy_pcm_locked", "equals": True}} in item["enablement"]


@pytest.mark.parametrize("case", [None, "missing_cp", "missing_sp", "interceptor", "stock_flag", "stock", "other_brand", "other_civic",
                                  "dashcamOnly", "passive", "no_nidec", "bosch_flag", "bad_bundle", "stale_bundle"])
def test_actual_capability_assignment_matches_native_availability(case):
  path = ROOT / "openpilot/sunnypilot/sunnylink/capabilities.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  method = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate_capabilities")
  wanted = {CAP, "nrdr_honda_pcm_fixed_cruise_active", "nrdr_honda_legacy_pcm_active", "nrdr_honda_legacy_pcm_locked"}
  nodes = [n for n in method.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript)
           and isinstance(n.targets[0].slice, ast.Constant) and n.targets[0].slice.value in wanted]
  ui = state(flags=int(HondaFlags.NIDEC | HondaFlags.NIDEC_PCM_LEGACY | HondaFlags.NIDEC_PCM_FIXED_CRUISE))
  if case:
    make_ineligible(ui, case)
  env = {**vars(honda_pcm), "caps": {}, "CP": ui.CP, "CP_SP": ui.CP_SP, "params": ui.params}
  exec(compile(ast.Module(nodes, []), str(path), "exec"), env)
  assert env["caps"][CAP] is (case is None)
  assert set(env["caps"]) == wanted
  if case is None:
    assert all(env["caps"].values())


@pytest.mark.parametrize("offroad", [None, True, False])
def test_remote_status_injection_keeps_help_and_saved_choices(offroad):
  params = Params(NrdrHondaPcmFixedCruise=True, NrdrHondaLegacyPcm=False, HondaLiveLearningGas=True,
                  CarParamsPersistent=cp_bytes(HondaFlags.NIDEC_PCM_LEGACY), CarParamsSPPersistent=custom.CarParamsSP.new_message().to_bytes())
  if offroad is not None:
    params.values["IsOffroad"] = offroad
  path = ROOT / "openpilot/nrdr/features/services/sunnylink.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "inject_pcm_experiment_status"]
  env = {"Params": lambda: params}
  exec(compile(tree, str(path), "exec"), env)
  items = [{"key": key, "details": "Keep help"} for key in (*KEYS, "HondaLiveLearningGas", "Other")]
  env["inject_pcm_experiment_status"](items, lambda schema, visitor: [visitor(item) for item in schema])
  if offroad is False:
    assert items[0]["details"].startswith("Running: Off. Saved: On; applies next drive.")
    assert items[1]["details"].startswith("Running: On. Saved: Off; applies next drive.")
    assert items[2]["details"].startswith("Legacy active; MVL next drive")
  else:
    assert items[0]["details"].startswith("Saved: On. Applies next drive.")
    assert items[1]["details"].startswith("Saved: Off. Applies next drive.")
    assert items[2]["details"].startswith("MVL next drive")
    assert all("active" not in item["details"] and "Running:" not in item["details"] for item in items)
  assert all(item["details"].endswith("Keep help") for item in items)
  assert not params.writes
