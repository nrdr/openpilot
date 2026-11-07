"""ROOT startup/UI contract for the opt-in Civic PCM acceleration-error deadzone."""
import ast
from dataclasses import replace
import json

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.honda.mvl_longitudinal import pcm_deadzone_config
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.params import mvl_pcm_deadzone as choices
from openpilot.nrdr.params.tuning_policy import MVL_LOCK_KEYS, tuning_write_allowed
from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT, Params, Widget, _font_advance_upper_bound, native_layout, state
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as rpc_fixture
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.nrdr.ui.honda_pcm import mvl_pcm_deadzone_available, saved_mvl_pcm_deadzone, save_mvl_pcm_deadzone
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC


KEY = "NrdrMvlPcmDeadzone"
CAP = "nrdr_mvl_pcm_deadzone_available"
VALUES = choices.MVL_PCM_DEADZONE_VALUES
INVALID = (None, True, False, -1, 1, 3, 100, 2.0, .02, "", "02", "2.0", " 2", "2\n", "+2", "0.02", "nan", b"\xff", {}, [])


@pytest.fixture
def rpc():
  return rpc_fixture.__wrapped__()


def mici_control(ui):
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MvlPcmDeadzoneControl"]
  env = {"BigMultiToggle": Widget, "ui_state": ui, "tr": lambda s: s,
         "mvl_pcm_deadzone_available": mvl_pcm_deadzone_available, "saved_mvl_pcm_deadzone": saved_mvl_pcm_deadzone,
         "save_mvl_pcm_deadzone": save_mvl_pcm_deadzone}
  env.update({key: value for key, value in vars(choices).items() if key.startswith("MVL_PCM_DEADZONE_")})
  exec(compile(tree, str(path), "exec"), env)
  return env["MvlPcmDeadzoneControl"]()


def emitted_capability(ui):
  """Execute the production capability assignment with current vehicle objects."""
  path = ROOT / "openpilot/sunnypilot/sunnylink/capabilities.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  method = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "generate_capabilities")
  assignment = next(node for node in method.body if isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Subscript) and isinstance(node.targets[0].slice, ast.Constant)
                    and node.targets[0].slice.value == CAP)
  env = {"caps": {}, "CP": ui.CP, "CP_SP": ui.CP_SP, "params": ui.params,
         "mvl_pcm_deadzone_available": mvl_pcm_deadzone_available}
  exec(compile(ast.Module([assignment], []), str(path), "exec"), env)
  return env["caps"][CAP]


@pytest.mark.parametrize("value", VALUES)
def test_strict_host_and_wire_enum(value):
  for raw in (value, str(value), str(value).encode()):
    assert choices.decode_mvl_pcm_deadzone(raw) == value
  assert saved_mvl_pcm_deadzone(Params(**{KEY: value})) == value


@pytest.mark.parametrize("value", INVALID)
def test_invalid_values_fall_back_without_repair_or_native_write(value):
  assert choices.decode_mvl_pcm_deadzone(value) is None
  ui = state()
  ui.params.values.update(HondaLiveLearningGas=True, **{KEY: value})
  assert saved_mvl_pcm_deadzone(ui.params) == 0
  assert not save_mvl_pcm_deadzone(ui, value)
  assert not ui.params.writes


@pytest.mark.parametrize("value", ["0", "2", "5", "10", b"2", b"10"])
def test_native_values_are_typed_not_storage_encodings(value):
  ui = state()
  ui.params.values.update(HondaLiveLearningGas=True, **{KEY: value})
  assert saved_mvl_pcm_deadzone(ui.params) == 0
  assert not save_mvl_pcm_deadzone(ui, value)
  assert not ui.params.writes


@pytest.mark.parametrize("car", list(CAR))
@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
def test_exact_car_and_selected_or_active_gate_native_and_capability(car, saved, active):
  ui = state(carFingerprint=str(car), flags=int(HondaFlags.MVL_LONGITUDINAL) if active else 0)
  ui.params.values["HondaLiveLearningGas"] = saved
  expected = car == CAR.HONDA_CIVIC and (saved or active)
  assert mvl_pcm_deadzone_available(ui.CP, ui.CP_SP, ui.params) is expected
  assert emitted_capability(ui) is expected
  assert save_mvl_pcm_deadzone(ui, 5) is expected
  assert ui.params.writes == ([(KEY, 5), ("OnroadCycleRequested", True)] if expected else [])


@pytest.mark.parametrize("case", ["onroad", "stock", "interceptor", "stock_flag", "missing_cp", "missing_sp",
                                 "unknown", "other_brand", "stale_bundle", "bad_bundle", "mvl_off"])
@pytest.mark.parametrize("native", ["large", "mici"])
def test_both_native_callbacks_recheck_stale_vehicle_and_road_state(case, native):
  ui = state()
  ui.params.values.update(HondaLiveLearningGas=True, ExperimentalMode=True, **{KEY: 2})
  layout = native_layout(ui) if native == "large" else mici_control(ui)
  if native == "large":
    layout._update_state()
    assert layout._mvl_pcm_deadzone.enabled
    def select():
      layout._mvl_pcm_deadzone.kwargs["callback"](2)
  else:
    assert layout.enabled()
    def select():
      layout._select("0.05")
  if case == "onroad":
    ui.is_offroad = lambda: False
  elif case == "stock":
    ui.CP.openpilotLongitudinalControl = False
  elif case == "interceptor":
    ui.CP_SP.enableGasInterceptor = True
  elif case == "stock_flag":
    ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  elif case == "missing_cp":
    ui.CP = None
  elif case == "missing_sp":
    ui.CP_SP = None
  elif case == "unknown":
    ui.CP.carFingerprint = "UNKNOWN_HONDA"
  elif case == "other_brand":
    ui.CP.brand = "toyota"
  elif case == "stale_bundle":
    ui.params.values["CarPlatformBundle"] = {"brand": "honda", "platform": "HONDA_CLARITY"}
  elif case == "bad_bundle":
    ui.params.values["CarPlatformBundle"] = True
  elif case == "mvl_off":
    ui.params.values["HondaLiveLearningGas"] = False
  select()
  layout._update_state()
  assert not ui.params.writes
  assert ui.params.get_bool("ExperimentalMode")
  if native == "large":
    assert not layout._mvl_pcm_deadzone.enabled and layout._mvl_pcm_deadzone.value == 1
  else:
    assert not layout.enabled() and layout.value == "0.02"


@pytest.mark.parametrize("saved,active", [(True, False), (False, True), (True, True)])
@pytest.mark.parametrize("value", VALUES)
def test_native_controls_save_enum_not_button_index_and_leave_other_locks(saved, active, value):
  ui = state(flags=int(HondaFlags.MVL_LONGITUDINAL) if active else 0)
  ui.params.values.update(HondaLiveLearningGas=saved, ExperimentalMode=False)
  large, mici = native_layout(ui), mici_control(ui)
  assert KEY not in MVL_LOCK_KEYS
  assert tuning_write_allowed(ui.params, KEY, CP=ui.CP)
  assert all(not tuning_write_allowed(ui.params, key, CP=ui.CP) for key in MVL_LOCK_KEYS)
  assert large._mvl_pcm_deadzone.param_key is None  # no automatic post-callback write
  large._mvl_pcm_deadzone.kwargs["callback"](VALUES.index(value))
  large._update_state()
  assert large._mvl_pcm_deadzone.value == VALUES.index(value)
  assert large._mvl_pcm_deadzone.enabled
  assert not large._pcm_mode.enabled and not large._wind_brake.enabled and not large._static_feedforward_long.enabled
  assert ui.params.writes == [(KEY, value), ("OnroadCycleRequested", True)]
  ui.params.writes.clear()
  mici._update_state()
  assert mici.value == choices.MVL_PCM_DEADZONE_LABELS[VALUES.index(value)]
  mici._select(mici.value)
  assert ui.params.writes == [(KEY, value), ("OnroadCycleRequested", True)]
  assert not ui.params.get_bool("ExperimentalMode")


@pytest.mark.parametrize("index", [-1, 4, True, None, "2", 2.0])
def test_native_invalid_button_indices_do_not_write(index):
  ui = state()
  ui.params.values["HondaLiveLearningGas"] = True
  layout = native_layout(ui)
  layout._mvl_pcm_deadzone.kwargs["callback"](index)
  assert not ui.params.writes


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("compressed", [False, True])
def test_remote_valid_enum_parked_restart_and_no_experimental_write(rpc, value, compressed):
  save, params, caps = rpc
  params.values.update(HondaLiveLearningGas=True, ExperimentalMode=True)
  caps[CAP] = True
  save({KEY: encoded(value, compressed)}, compressed)
  assert params.get(KEY) == value and type(params.get(KEY)) is int
  assert params.get_bool("OnroadCycleRequested")
  assert params.get_bool("ExperimentalMode")
  assert {key for key, _ in params.writes} == {KEY, "OnroadCycleRequested", "ParamsVersion"}


@pytest.mark.parametrize("value", INVALID)
@pytest.mark.parametrize("compressed", [False, True])
def test_remote_malformed_values_rejected_before_any_write(rpc, value, compressed):
  save, params, caps = rpc
  caps[CAP] = True
  with pytest.raises(ValueError):
    save({"ExperimentalMode": encoded(1, compressed), KEY: encoded(value, compressed)}, compressed)
  assert not params.writes


@pytest.mark.parametrize("payload,compressed", [("!bad-base64", False), ("!bad-base64", True), (encoded(5), True)])
def test_remote_bad_transport_rejected(rpc, payload, compressed):
  save, params, caps = rpc
  caps[CAP] = True
  with pytest.raises(ValueError):
    save({KEY: payload}, compressed)
  assert not params.writes


@pytest.mark.parametrize("offroad,capability", [(False, True), (True, False), (True, None)])
def test_remote_road_and_capability_fail_closed(rpc, offroad, capability):
  save, params, caps = rpc
  params.values["IsOffroad"] = offroad
  caps[CAP] = capability
  with pytest.raises(ValueError):
    save({KEY: encoded(5)})
  assert not params.writes


@pytest.mark.parametrize("change", ["road", "vehicle"])
def test_remote_rechecks_just_before_write(rpc, change):
  save, params, caps = rpc
  caps[CAP] = True
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
    save({KEY: encoded(10)})
  assert not params.writes


@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
def test_remote_deadzone_does_not_unlock_custom_tuning_in_same_batch(rpc, key):
  save, params, caps = rpc
  params.values["HondaLiveLearningGas"] = True
  caps[CAP] = True
  with pytest.raises(ValueError):
    save({KEY: encoded(5), key: encoded(1)})
  assert not params.writes


@pytest.mark.parametrize("reverse", [False, True])
def test_remote_batch_cannot_disable_its_own_mvl_eligibility(rpc, reverse):
  save, params, caps = rpc
  params.values["HondaLiveLearningGas"] = True
  caps[CAP] = True
  entries = [(KEY, encoded(5)), ("HondaLiveLearningGas", encoded(0))]
  with pytest.raises(ValueError):
    save(dict(reversed(entries) if reverse else entries))
  assert not params.writes


@pytest.mark.parametrize("car,interceptor,openlong,mvl,stock", [
  (CAR.HONDA_CIVIC, False, True, True, False), (CAR.HONDA_CIVIC, False, True, False, False),
  (CAR.HONDA_CLARITY, False, True, True, False), (CAR.HONDA_CIVIC_BOSCH, False, True, True, False),
  (CAR.HONDA_CIVIC, True, True, True, False), (CAR.HONDA_CIVIC, False, False, True, False),
  (CAR.HONDA_CIVIC, False, True, True, True),
])
def test_host_value_passes_scaled_to_core_but_cannot_apply_to_unsupported_path(tmp_path, car, interceptor, openlong, mvl, stock):
  params = FakeParams({KEY: 5, "HondaLiveLearningGas": mvl})
  config = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  ui = state(carFingerprint=str(car), enableGasInterceptor=interceptor, openpilotLongitudinalControl=openlong,
             flags=int(HondaFlags.BOSCH if car == CAR.HONDA_CIVIC_BOSCH else HondaFlags.NIDEC))
  if stock:
    ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  expected = .05 if car == CAR.HONDA_CIVIC and not interceptor and openlong and mvl and not stock else 0.0
  assert config.honda.mvl_pcm_deadzone == .05
  assert pcm_deadzone_config(ui.CP, ui.CP_SP, config.honda.mvl_longitudinal, config.honda.mvl_pcm_deadzone) == expected
  # Aside from this explicit startup option, every other host setting stays identical.
  baseline = build_sunnypilot_car_config(FakeParams({"HondaLiveLearningGas": mvl}), start_worker=False, metadata_path=tmp_path / "off.json")
  assert config == replace(baseline, honda=replace(baseline.honda, provider=config.honda.provider, mvl_pcm_deadzone=.05))
  assert not params.writes


def test_copy_schema_native_options_and_compact_geometry_match():
  ui = state()
  large, mici = native_layout(ui), mici_control(ui)
  schema = compile_schema(DEFAULT_SRC)
  section = next(page for page in schema["panels"] if page["id"] == "steering")["sections"]
  panel = next(panel for group in section for panel in group.get("sub_panels", []) if panel["id"] == "nrdr_longitudinal")
  web = next(item for item in panel["items"] if item.get("key") == KEY)
  local = large._mvl_pcm_deadzone.kwargs
  assert web["title"] == local["title"]() == mici.text == choices.MVL_PCM_DEADZONE_TITLE
  assert web["description"] == choices.MVL_PCM_DEADZONE_DESCRIPTION
  assert web["details"] == choices.MVL_PCM_DEADZONE_DETAILS
  assert "m/s²" in web["details"]
  assert local["description"]() == mici.kwargs["description"] == web["description"] + " " + web["details"]
  assert web["options"] == [{"label": label, "value": value} for label, value in zip(choices.MVL_PCM_DEADZONE_LABELS, VALUES, strict=True)]
  assert [label() for label in local["buttons"]] == mici.options == list(choices.MVL_PCM_DEADZONE_LABELS)
  assert web["needs_onroad_cycle"]
  gate = {"type": "capability", "field": CAP, "equals": True}
  assert web["visibility"] == [gate]
  assert web["enablement"] == [{"type": "offroad_only"}, gate]  # no blanket MVL lock
  assert json.loads((ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8")) == schema
  fields = ast.parse((ROOT / "openpilot/sunnypilot/sunnylink/capabilities.py").read_text(encoding="utf-8"))
  field_list = next(node.value for node in fields.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "CAPABILITY_FIELDS" for target in node.targets))
  assert CAP in ast.literal_eval(field_list)
  # MICI's 536px screen uses a 402px settings card; reserve the right pill column.
  assert mici._rect.width == 402
  size, width = mici.kwargs["font_size"], mici._title_width_hint()
  lines = []
  for word in mici.text.split():
    joined = f"{lines[-1]} {word}" if lines else word
    if lines and _font_advance_upper_bound("Inter-Bold.ttf", joined, size) <= width:
      lines[-1] = joined
    else:
      lines.append(word)
  assert all(_font_advance_upper_bound("Inter-Bold.ttf", line, size) <= width for line in lines)
  title_height = size * 1.16 * (1 + .9 * (len(lines) - 1))
  assert mici._rect.height - 2 * mici.LABEL_VERTICAL_PADDING - title_height - 36 * 1.16 > 10
  assert all(_font_advance_upper_bound("Inter-Regular.ttf", label, 36) < mici._subtitle_width_hint() for label in mici.options)
  assert mici._txt_enabled_toggle.height + 3 * 35 <= mici._rect.height
