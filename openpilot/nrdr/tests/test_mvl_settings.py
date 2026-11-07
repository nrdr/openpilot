"""Settings admission parity: saved mode, boot latch, native callbacks and RPC."""
import ast
import base64
import gzip
import json
import re
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import HondaFlags
from opendbc.car.structs import car
from openpilot.nrdr.params.generated import ALL_KEYS
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, PLANNER_GROUPS
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY
from openpilot.nrdr.params.tuning_policy import LONG_SCALE_KEYS, MVL_DESCRIPTION, MVL_LOCK_KEYS, mvl_tuning_locked, tuning_write_allowed
from openpilot.nrdr.tests.test_honda_pcm_ui import Params, Widget, native_layout, native_layout_with_real_toggle_handlers, state
from openpilot.nrdr.ui.honda_pcm import live_gas_available, save_live_gas_choice
from openpilot.nrdr.params import mvl_pcm_deadzone
from openpilot.nrdr.ui.honda_pcm import mvl_pcm_deadzone_available, saved_mvl_pcm_deadzone, save_mvl_pcm_deadzone
from openpilot.nrdr.ui import honda_pcm
from openpilot.nrdr.params.nidec_pcm import PCM_EXPERIMENT_DETAILS
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC

ROOT = Path(__file__).resolve().parents[3]
RETIRED = {"NrdrExperimentalEngineBraking", "NrdrCruiseOverspeedAllowance"}
PARAM_TYPES = dict(re.findall(r'\{"([^"]+)",\s*\{[^,\n]+,\s*(BYTES|STRING|BOOL|INT|FLOAT|TIME|JSON)\b',
                             (ROOT / "openpilot/common/params_keys.h").read_text(encoding="utf-8")))
PARAM_TYPES.update({key: spec.param_type.value for key, spec in PARAM_SPECS_BY_KEY.items()})


def cp_bytes(active, **kwargs):
  return car.CarParams.new_message(brand="honda", carFingerprint="HONDA_CIVIC", openpilotLongitudinalControl=True,
                                   flags=int(HondaFlags.MVL_LONGITUDINAL) if active else 0, **kwargs).to_bytes()


@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
@pytest.mark.parametrize("offroad", [None, False, True])
def test_conflicting_writes_bypass_mode_only_while_parked(saved, active, key, offroad):
  params = Params(IsOffroad=offroad, HondaLiveLearningGas=saved, CarParamsPersistent=cp_bytes(active), **{key: 123})
  assert mvl_tuning_locked(params) is (saved or active)
  assert tuning_write_allowed(params, key) is (offroad is True or not (saved or active))
  assert params.get(key) == 123 and not params.writes


@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
def test_manual_experimental_is_not_an_mvl_conflict_but_dec_is(saved, active):
  params = Params(HondaLiveLearningGas=saved, CarParamsPersistent=cp_bytes(active))
  assert "ExperimentalMode" not in MVL_LOCK_KEYS
  assert "DynamicExperimentalControl" in MVL_LOCK_KEYS
  assert tuning_write_allowed(params, "ExperimentalMode")
  assert tuning_write_allowed(params, "DynamicExperimentalControl") is not (saved or active)
  assert not params.writes


@pytest.mark.parametrize("key", ["LongitudinalPersonality", "HondaLiveLearningGas", "HondaBoschARadar",
  "AlphaLongitudinalEnabled", "HondaNidecStockLongitudinal", "EnableGasInterceptor", "DisengageOnAccelerator",
  "NrdrResetLiveGas", "NrdrLiveGasResetStatus", "NrdrCarTuneInfo", "NrdrLateralController", "LatPScaleStandard",
  "LaneGuidanceMode", "HondaSteerDeltaUp", "IntelligentCruiseButtonManagement"])
def test_mvl_does_not_lock_personality_selection_lateral_hardware_safety_or_diagnostics(key):
  assert tuning_write_allowed(Params(HondaLiveLearningGas=True, CarParamsPersistent=cp_bytes(True)), key)


def test_current_cp_supersedes_old_persistent_latch_but_corruption_fails_closed():
  params = Params(HondaLiveLearningGas=False, CarParams=cp_bytes(False), CarParamsPersistent=cp_bytes(True))
  assert not mvl_tuning_locked(params)
  params.values["CarParams"] = b"invalid"
  assert mvl_tuning_locked(params)
  assert not mvl_tuning_locked(Params())


@pytest.mark.parametrize("brand,openlong", [("toyota", True), ("toyota", False), ("honda", False)])
@pytest.mark.parametrize("key", ["AccelBoostSP", "ExperimentalMode", "DynamicExperimentalControl",
                                "SmartCruiseControlVision", "SmartCruiseControlMap", "SpeedLimitMode"])
def test_saved_honda_mode_does_not_lock_current_non_honda_or_stock_acc(brand, openlong, key):
  cp = car.CarParams.new_message(brand=brand, openpilotLongitudinalControl=openlong, flags=131072)
  params = Params(HondaLiveLearningGas=True, CarParamsPersistent=cp_bytes(True))
  # Explicit live CP wins over the previous car's persistent snapshot.
  assert tuning_write_allowed(params, key, CP=cp)
  params.values["CarParams"] = cp.to_bytes()
  assert tuning_write_allowed(params, key)


def test_saved_on_without_known_cp_stays_fail_closed():
  assert mvl_tuning_locked(Params(HondaLiveLearningGas=True))
  assert mvl_tuning_locked(Params(HondaLiveLearningGas=True), car.CarParams.new_message())


@pytest.mark.parametrize("car,interceptor", [("HONDA_CIVIC", False), ("HONDA_CIVIC", True), ("HONDA_CIVIC_BOSCH", False)])
@pytest.mark.parametrize("selected", [True, False])
def test_live_gas_selects_all_honda_openlong_paths_parked_and_requests_restart(car, interceptor, selected):
  ui = state(carFingerprint=car, enableGasInterceptor=interceptor)
  ui.params.values.update(HondaLiveLearningGas=not selected, **dict.fromkeys(LONG_SCALE_KEYS, 150))
  assert live_gas_available(ui.CP, ui.CP_SP, ui.params)
  assert save_live_gas_choice(ui, selected)
  assert ui.params.writes[0] == ("HondaLiveLearningGas", selected)
  assert ui.params.writes[-1] == ("OnroadCycleRequested", True)
  assert not (ui.CP.flags & HondaFlags.MVL_LONGITUDINAL)  # Saving is not activation.
  assert all(ui.params.get(key) == 150 for key in LONG_SCALE_KEYS)
  ui.params.writes.clear()
  ui.is_offroad = lambda: False
  assert not save_live_gas_choice(ui, not selected)
  assert not ui.params.writes


@pytest.mark.parametrize("change", ["missing", "stock", "non_honda", "mismatch", "invalid"])
def test_live_gas_stale_callback_rechecks_identity_and_value(change):
  ui = state()
  selected = True
  if change == "missing":
    ui.CP = None
  elif change == "stock":
    ui.CP.openpilotLongitudinalControl = False
  elif change == "non_honda":
    ui.CP.brand = "toyota"
  elif change == "mismatch":
    ui.params.values["CarPlatformBundle"] = {"brand": "honda", "platform": "HONDA_CLARITY"}
  else:
    selected = 1
  assert not save_live_gas_choice(ui, selected)
  assert not ui.params.writes


def test_tici_live_toggle_never_writes_after_a_rejected_callback():
  ui = state()
  layout = native_layout_with_real_toggle_handlers(ui)
  toggle = layout._live_learning_gas
  assert toggle.kwargs.get("param") is None
  toggle.set_enabled(True)
  ui.is_offroad = lambda: False  # Still visually enabled until next refresh.
  toggle.toggle._handle_mouse_release(None)
  assert not ui.params.writes and toggle.toggle.get_state() is False
  ui.is_offroad = lambda: True
  toggle.toggle._handle_mouse_release(None)
  assert ui.params.get_bool("HondaLiveLearningGas")
  assert ui.params.get_bool("OnroadCycleRequested")


def test_tici_parked_saved_off_unlocks_tuning_without_changing_boot_latch():
  ui = state(flags=int(HondaFlags.MVL_LONGITUDINAL))
  ui.params.values["HondaLiveLearningGas"] = True
  layout = native_layout(ui)
  layout._set_live_gas(False)
  layout._update_state()
  controls = ("_pcm_mode", "_wind_brake", "_static_feedforward_long", "_full_brake_authority",
              "_roen_acceleration_limits", "_standstill_gap", "_cruise_mismatch_correction", "_stop_accel")
  assert all(getattr(layout, name).enabled for name in controls)
  assert layout._radar_tryout.enabled and layout._dashboard_variant.enabled
  assert layout._long_pid_tune_scale_standard.visible
  assert layout._live_learning_gas.value is False
  assert mvl_tuning_locked(ui.params, ui.CP)
  ui.params.values["IsOffroad"] = False
  layout._update_state()
  assert all(not getattr(layout, name).enabled for name in controls)
  assert not layout._long_pid_tune_scale_standard.visible
  ui.params.values["IsOffroad"] = True
  layout._update_state()
  assert layout._pcm_mode.enabled and layout._standstill_gap.enabled


def test_mici_order_and_write_guards_survive_stale_display():
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))]
  from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled, nrdr_longitudinal_enabled
  from openpilot.nrdr.ui.honda_pcm import pcm_tuning_available, save_pcm_choice, saved_pcm_mode, saved_wind_brake
  ui = state()
  env = {"BigToggle": Widget, "BigMultiToggle": Widget, "ui_state": ui, "tr": lambda s: s, "MVL_DESCRIPTION": MVL_DESCRIPTION,
         "mvl_longitudinal_enabled": mvl_longitudinal_enabled,
         "nrdr_longitudinal_enabled": nrdr_longitudinal_enabled, "live_gas_available": live_gas_available,
         "save_live_gas_choice": save_live_gas_choice, "mvl_tuning_locked": mvl_tuning_locked, "tuning_write_allowed": tuning_write_allowed,
         "pcm_tuning_available": pcm_tuning_available, "save_pcm_choice": save_pcm_choice, "saved_pcm_mode": saved_pcm_mode,
         "saved_wind_brake": saved_wind_brake, "mici_reset_button": lambda: "reset"}
  env.update({key: value for key, value in vars(mvl_pcm_deadzone).items() if key.startswith("MVL_PCM_DEADZONE_")})
  env.update(mvl_pcm_deadzone_available=mvl_pcm_deadzone_available, saved_mvl_pcm_deadzone=saved_mvl_pcm_deadzone,
             save_mvl_pcm_deadzone=save_mvl_pcm_deadzone)
  env.update(vars(honda_pcm))
  env["PCM_EXPERIMENT_DETAILS"] = PCM_EXPERIMENT_DETAILS
  exec(compile(tree, str(path), "exec"), env)
  live, reset, mode, wind, static, deadzone, *experiments = env["longitudinal_controls"]()
  assert len(experiments) == 2
  assert reset == "reset" and static.text == "Keep Feedforward Static"
  live._select(True)
  assert ui.params.get_bool("OnroadCycleRequested")
  ui.CP.flags |= int(HondaFlags.MVL_LONGITUDINAL)
  live._select(False)
  ui.params.writes.clear()
  mode._select("Experimental")
  wind._select(False)
  static._select(True)
  assert ui.params.writes == [("NrdrHondaPcmMode", 2), ("OnroadCycleRequested", True),
                              ("NrdrHondaWindBrake", False), ("OnroadCycleRequested", True), ("StaticFeedforwardLong", True)]
  assert mode.enabled() and wind.enabled() and static.enabled()
  assert deadzone.enabled()
  ui.params.values["IsOffroad"] = False
  ui.params.writes.clear()
  mode._select("Off")
  wind._select(True)
  static._select(False)
  live._select(True)
  deadzone._select("0.05")
  assert not ui.params.writes
  assert not mode.enabled() and not wind.enabled() and not static.enabled() and not deadzone.enabled()


@pytest.fixture
def rpc():
  path = ROOT / "openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("saveParams", "_remote_bool_value", "_remote_int_value")]
  for node in nodes:
    node.decorator_list = []
  params = Params(IsOffroad=True, HondaLiveLearningGas=False)
  caps = {"nrdr_honda_mvl_selection_available": True, "nrdr_honda_pcm_tuning_available": True}
  env = {"params": params, "base64": base64, "gzip": gzip, "BLOCKED_PARAMS": set(),
         "_vehicle_tuning_capabilities": lambda: caps,
         "cloudlog": NS(warning=lambda *a: None, error=lambda *a: None)}
  exec(compile(ast.Module(nodes, []), str(path), "exec"), env)
  # Exercise the actual remote road-state policy and boolean decoder without
  # importing Linux hardware or native Params on the portable test host.
  policy = ast.parse((ROOT / "openpilot/nrdr/features/services/sunnylink.py").read_text(encoding="utf-8"))
  policy.body = [n for n in policy.body if isinstance(n, ast.FunctionDef) and n.name == "allow_param_write"
                 or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in
                    ("ONROAD_WRITE_BLOCKLIST", "HONDA_TUNING_WRITE_KEYS") for t in n.targets)]
  exec(compile(policy, "sunnylink.py", "exec"), env)
  param_types = NS(BYTES=0, STRING=1, BOOL=2, INT=3, FLOAT=4, TIME=5, JSON=6)
  params.get_type = lambda key: getattr(param_types, PARAM_TYPES[key])
  env.update(Params=lambda: params, ParamKeyType=param_types, json=json)
  helpers = ast.parse((ROOT / "openpilot/sunnypilot/sunnylink/utils.py").read_text(encoding="utf-8"))
  helpers.body = [n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in
                  ("save_param_from_base64_encoded_string", "_convert_param_to_type")]
  exec(compile(helpers, "utils.py", "exec"), env)
  return env["saveParams"], params, caps


def encoded(value, compressed=False):
  raw = str(value).encode()
  return base64.b64encode(gzip.compress(raw) if compressed else raw).decode()


@pytest.mark.parametrize("compressed", [False, True])
@pytest.mark.parametrize("selected", ["1", "0"])
def test_remote_live_gas_is_typed_offroad_and_requests_restart(rpc, selected, compressed):
  save, params, _ = rpc
  save({"HondaLiveLearningGas": encoded(selected, compressed)}, compressed)
  assert params.get_bool("HondaLiveLearningGas") is (selected == "1")
  assert params.get_bool("OnroadCycleRequested")
  params.values["IsOffroad"] = False
  params.writes.clear()
  with pytest.raises(ValueError):
    save({"HondaLiveLearningGas": encoded(selected, compressed)}, compressed)
  assert not params.writes


@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("offroad", [False, True])
@pytest.mark.parametrize("compressed", [False, True])
def test_remote_manual_experimental_on_off_during_mvl_restart_states(rpc, saved, active, selected, offroad, compressed):
  save, params, _ = rpc
  params.values.update(HondaLiveLearningGas=saved, CarParamsPersistent=cp_bytes(active), IsOffroad=offroad,
                       ExperimentalMode=not selected, ExperimentalModeConfirmed=True)
  save({"ExperimentalMode": encoded(int(selected), compressed)}, compressed)
  assert params.get_bool("ExperimentalMode") is selected
  assert params.writes == [("ExperimentalMode", selected), ("ParamsVersion", "1")]
  assert params.get("HondaLiveLearningGas") is saved


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("mvl_selected", [False, True])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
def test_remote_manual_experimental_can_share_mvl_restart_batch(rpc, active, mvl_selected, selected, reverse):
  save, params, _ = rpc
  params.values.update(HondaLiveLearningGas=not mvl_selected, CarParamsPersistent=cp_bytes(active), ExperimentalMode=not selected)
  entries = [("HondaLiveLearningGas", encoded(int(mvl_selected))), ("ExperimentalMode", encoded(int(selected)))]
  save(dict(reversed(entries) if reverse else entries))
  assert params.get_bool("ExperimentalMode") is selected
  assert params.get_bool("HondaLiveLearningGas") is mvl_selected
  assert params.get_bool("OnroadCycleRequested")
  assert len(params.writes) == 4


@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("offroad", [None, False, True])
def test_remote_manual_experimental_and_dec_batch_respects_road_state(rpc, selected, offroad):
  save, params, _ = rpc
  params.values.update(IsOffroad=offroad, HondaLiveLearningGas=True, CarParamsPersistent=cp_bytes(True), ExperimentalMode=not selected)
  batch = {"ExperimentalMode": encoded(int(selected)), "DynamicExperimentalControl": encoded(1)}
  if offroad is True:
    save(batch)
    assert params.writes == [("ExperimentalMode", selected), ("DynamicExperimentalControl", True), ("ParamsVersion", "1")]
  else:
    with pytest.raises(ValueError):
      save(batch)
    assert not params.writes


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
@pytest.mark.parametrize("offroad", [None, False, True])
def test_remote_saved_or_active_conflicts_are_editable_only_while_parked(rpc, active, key, offroad):
  save, params, _ = rpc
  params.values.update(IsOffroad=offroad, HondaLiveLearningGas=not active, CarParamsPersistent=cp_bytes(active))
  if offroad is True:
    save({key: encoded(0)})
    assert params.get(key) == 0
    assert {name for name, _ in params.writes} == ({key, "OnroadCycleRequested", "ParamsVersion"}
                                                 if key in ("NrdrHondaPcmMode", "NrdrHondaWindBrake") else {key, "ParamsVersion"})
  else:
    with pytest.raises(ValueError):
      save({key: encoded(0)})
    assert not params.writes


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("offroad", [None, False, True])
def test_remote_mixed_enable_batch_is_parked_only_and_order_independent(rpc, reverse, offroad):
  save, params, _ = rpc
  params.values["IsOffroad"] = offroad
  entries = [("HondaLiveLearningGas", encoded(1)), ("StaticFeedforwardLong", encoded(1))]
  if offroad is True:
    save(dict(reversed(entries) if reverse else entries))
    assert params.get("HondaLiveLearningGas") is True and params.get("StaticFeedforwardLong") is True
    assert {key for key, _ in params.writes} == {"HondaLiveLearningGas", "StaticFeedforwardLong", "OnroadCycleRequested", "ParamsVersion"}
  else:
    with pytest.raises(ValueError):
      save(dict(reversed(entries) if reverse else entries))
    assert not params.writes


def test_remote_parked_saved_off_can_prepare_tuning_in_same_or_later_batch(rpc):
  save, params, _ = rpc
  params.values.update(HondaLiveLearningGas=True, CarParamsPersistent=cp_bytes(True))
  save({"HondaLiveLearningGas": encoded(0), "NrdrHondaPcmMode": encoded(2)})
  assert params.get("HondaLiveLearningGas") is False and params.get("NrdrHondaPcmMode") == 2
  assert mvl_tuning_locked(params)  # Preparing the next tune does not alter the running latch.
  params.writes.clear()
  save({"NrdrHondaPcmMode": encoded(1)})
  assert params.writes == [("NrdrHondaPcmMode", 1), ("OnroadCycleRequested", True), ("ParamsVersion", "2")]


@pytest.mark.parametrize("value", ["2", "", "not a bool"])
def test_remote_rejects_invalid_live_gas_without_writes(rpc, value):
  save, params, _ = rpc
  with pytest.raises(ValueError):
    save({"HondaLiveLearningGas": encoded(value)})
  assert not params.writes


def test_remote_rechecks_park_and_vehicle_at_write_time(rpc):
  save, params, caps = rpc
  caps["nrdr_honda_mvl_selection_available"] = False
  with pytest.raises(ValueError):
    save({"HondaLiveLearningGas": encoded(1)})
  assert not params.writes
  caps["nrdr_honda_mvl_selection_available"] = True
  calls = []
  def offroad(key):
    if key == "IsOffroad":
      calls.append(key)
      return len(calls) == 1
    return bool(params.get(key))
  params.get_bool = offroad
  with pytest.raises(ValueError):
    save({"HondaLiveLearningGas": encoded(1)})
  assert not params.writes


@pytest.mark.parametrize("key", ["AccelBoostSP", "ExperimentalMode", "SmartCruiseControlVision", "SmartCruiseControlMap",
                                "CustomAccIncrementsEnabled", "CustomAccShortPressIncrement", "CustomAccLongPressIncrement"])
def test_remote_non_honda_ignores_saved_honda_mode_for_global_sunny_controls(rpc, key):
  save, params, caps = rpc
  params.values.update(HondaLiveLearningGas=True,
                       CarParams=car.CarParams.new_message(brand="toyota", openpilotLongitudinalControl=True).to_bytes())
  caps.update(nrdr_honda_mvl_selection_available=False, nrdr_honda_pcm_tuning_available=False)
  save({key: encoded(1)})
  assert params.get(key) == 1
  params.writes.clear()
  with pytest.raises(ValueError):
    save({"HondaLiveLearningGas": encoded(0)})
  assert not params.writes


def test_retired_keys_are_absent_and_remote_writes_rejected(rpc):
  save, params, _ = rpc
  keys = set(ALL_KEYS) | {k for group in CONTROL_GROUPS + PLANNER_GROUPS for k in group.keys}
  assert not keys & RETIRED
  schema = compile_schema(DEFAULT_SRC)
  assert not any(key in json.dumps(schema) for key in RETIRED)
  for key in RETIRED:
    assert not tuning_write_allowed(params, key)
    with pytest.raises(ValueError):
      save({key: encoded(1)})
  assert not params.writes


def test_compiled_schema_keeps_onroad_mode_guards_and_preserves_econ_selection():
  schema = compile_schema(DEFAULT_SRC)
  def walk(node):
    if isinstance(node, dict):
      if "widget" in node and "key" in node:
        yield node
      for value in node.values():
        yield from walk(value)
    elif isinstance(node, list):
      for value in node:
        yield from walk(value)
  items = {item["key"]: item for item in walk(schema)}
  for key in MVL_LOCK_KEYS - {"LongPidTuneScale", "DynamicExperimentalControl"}:
    rules = json.dumps(items[key]["enablement"])
    assert "HondaLiveLearningGas" in rules and "nrdr_mvl_longitudinal_active" in rules
    assert "nrdr_mvl_tuning_exempt" in rules
    assert "offroad_only" in rules
  personality = items["LongitudinalPersonality"]
  assert [option["label"] for option in personality["options"]] == ["Aggressive", "Standard", "Relaxed", "Econ"]
  assert "HondaLiveLearningGas" not in json.dumps(personality.get("enablement"))
  assert "Only Econ" in items["HondaLiveLearningGas"]["description"]
  assert "including following distances" in items["HondaLiveLearningGas"]["description"]
  assert "Experimental Mode remains manually selectable" in items["HondaLiveLearningGas"]["description"]
  assert "needs_onroad_cycle" not in items["HondaLiveLearningGas"]
  assert items["ExperimentalMode"]["enablement"] == [
    {"type": "capability", "field": "has_longitudinal_control", "equals": True},
  ]
  assert schema == json.loads((ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("saved,active,exempt,allowed", [(True, False, True, True), (True, False, False, False),
                                                       (False, True, False, False), (False, False, False, True)])
@pytest.mark.parametrize("offroad", [None, False, True])
def test_sunnylink_visual_lock_matches_road_state_vehicle_scope_and_latch(saved, active, exempt, allowed, offroad):
  from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
  values = {"HondaLiveLearningGas": saved, "nrdr_mvl_longitudinal_active": active, "nrdr_mvl_tuning_exempt": exempt,
            "nrdr_honda_legacy_pcm_locked": False}
  def evaluate(rule):
    kind = rule["type"]
    if kind == "offroad_only":
      return offroad is True
    if kind in ("param", "capability"):
      return values[rule.get("key", rule.get("field"))] == rule["equals"]
    if kind == "not":
      return not evaluate(rule["condition"])
    return (any if kind == "any" else all)(evaluate(c) for c in rule["conditions"])
  item = apply_sunnylink_metadata({"key": "AccelBoostSP"})
  assert all(evaluate(rule) for rule in item["enablement"]) is (offroad is True or allowed)


@pytest.mark.parametrize("key", ["CustomAccIncrementsEnabled", "CustomAccShortPressIncrement", "CustomAccLongPressIncrement"])
def test_increment_schema_lock_preserves_existing_availability_rules(key):
  from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
  original = {"key": key, "enablement": [{"type": "capability", "field": "has_longitudinal_control", "equals": True}],
              "visibility": [{"type": "param", "key": "CustomAccIncrementsEnabled", "equals": True}]}
  result = apply_sunnylink_metadata(original)
  assert result["enablement"][:-2] == original["enablement"]
  assert result["visibility"] == original["visibility"]
  assert "nrdr_mvl_longitudinal_active" in json.dumps(result["enablement"][-2])
  assert "nrdr_honda_legacy_pcm_locked" in json.dumps(result["enablement"][-1])


def test_saved_learner_diagnostics_do_not_replace_next_drive_help():
  path = ROOT / "openpilot/sunnypilot/sunnylink/tools/generate_settings_schema.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("_inject_live_gas_help", "_walk_all_items")]
  def inject(schema, walk):
    walk(schema, lambda item: item.update(details="Saved snapshot only"))
  env = {"Callable": object, "inject_live_gas_details": inject}
  # These helpers use Callable only for annotations.
  from collections.abc import Callable
  env["Callable"] = Callable
  exec(compile(tree, str(path), "exec"), env)
  item = {"key": "HondaLiveLearningGas", "details": "Saved ON is not active. Applies next drive; no device reboot."}
  schema = {"panels": [{"items": [item]}]}
  env["_inject_live_gas_help"](schema)
  assert item["details"] == "Saved ON is not active. Applies next drive; no device reboot.<br><br>Saved snapshot only"


def test_full_compiled_schema_integrity_without_hardware_imports():
  # Execute the real validator with only its literal capability declarations;
  # no Linux hardware, UI renderer, native Params or network daemon needed.
  caps_path = ROOT / "openpilot/sunnypilot/sunnylink/capabilities.py"
  caps_tree = ast.parse(caps_path.read_text(encoding="utf-8"))
  fields = next(ast.literal_eval(n.value) for n in caps_tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "CAPABILITY_FIELDS" for t in n.targets))
  path = ROOT / "openpilot/sunnypilot/sunnylink/tools/validate_settings_ui.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
  env = {"json": json, "CAPABILITY_FIELDS": fields, "VALID_WIDGETS": {"toggle", "option", "multiple_button", "button", "info"},
         "VALID_COMPARE_OPS": {">", "<", ">=", "<="}}
  exec(compile(tree, str(path), "exec"), env)
  assert env["validate"](str(ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json"))
