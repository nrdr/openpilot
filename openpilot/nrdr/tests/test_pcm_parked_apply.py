"""Four longitudinal choices apply next drive without a device-reboot badge."""
import ast
from collections.abc import Callable
import datetime
import json

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.cereal import custom
from openpilot.nrdr.tests.test_honda_pcm_ui import Params, ROOT
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as rpc_fixture
from openpilot.nrdr.tests.test_nidec_pcm_experiments import cp_bytes, state
from openpilot.nrdr.ui import honda_pcm
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema

CHOICES = (
  ("HondaLiveLearningGas", True),
  ("NrdrHondaPcmMode", 2), ("NrdrHondaWindBrake", False), ("NrdrPcmSpeedDeadzone", 0.05),
)
COPY = "Change while parked. Applies next drive; no device reboot."


@pytest.fixture
def rpc():
  save, params, caps = rpc_fixture.__wrapped__()
  caps.update(nrdr_honda_pcm_experiments_available=True, nrdr_mvl_pcm_deadzone_available=True)
  return save, params, caps


def _functions(path, names=None):
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and (names is None or node.name in names)]
  return compile(tree, str(path), "exec")


@pytest.mark.parametrize("offroad", [None, True, False])
def test_compiled_and_runtime_overlays_keep_four_controls_parked_without_reboot_badges(offroad):
  params = Params(HondaLiveLearningGas=True, NrdrHondaLegacyPcm=False, NrdrHondaPcmFixedCruise=True,
                  CarParamsPersistent=cp_bytes(524288 | HondaFlags.MVL_LONGITUDINAL),
                  CarParamsSPPersistent=custom.CarParamsSP.new_message().to_bytes())
  if offroad is not None:
    params.values["IsOffroad"] = offroad
  # Run the real schema loader, dynamic options, help merge, status overlay and walker.
  # Only unrelated vehicle/learner diagnostics and capability declarations are inert.
  env = {"Params": lambda: params, "Callable": Callable, "json": json, "datetime": datetime,
         "CAPABILITY_FIELDS": [], "CAPABILITY_LABELS": {},
         "DEFINITION_PATH": str(ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json"),
         "TORQUE_VERSIONS_PATH": str(ROOT / "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_versions.json"),
         "inject_car_tune_details": lambda *_: None, "inject_live_gas_details": lambda *_: None}
  exec(_functions(ROOT / "openpilot/nrdr/features/services/sunnylink.py", {"inject_pcm_experiment_status"}), env)
  exec(_functions(ROOT / "openpilot/sunnypilot/sunnylink/tools/generate_settings_schema.py"), env)
  for schema in (compile_schema(DEFAULT_SRC), env["generate_schema"]()):
    items = {}
    env["_walk_all_items"](schema, lambda item, items=items: items.update({item["key"]: item}) if "key" in item else None)
    for key, _ in CHOICES:
      item = items[key]
      assert "needs_onroad_cycle" not in item
      assert "Applies next drive; no device reboot." in item["description"]
      assert "parked" in item["description"]
      assert "restart" not in (item["description"] + item.get("details", "")).lower()
      assert {"type": "offroad_only"} in item["enablement"]
  assert items["HondaLiveLearningGas"]["details"].startswith("MVL active<br>" if offroad is False else "MVL next drive<br>")
  assert "NrdrHondaPcmFixedCruise" not in items and "NrdrHondaLegacyPcm" not in items
  assert not params.writes


@pytest.mark.parametrize("key,value", CHOICES)
@pytest.mark.parametrize("offroad", [False, True])
def test_four_remote_choices_keep_server_parked_gate_and_explicit_cycle(rpc, key, value, offroad):
  save, params, _ = rpc
  params.values.update(IsOffroad=offroad, CarParamsPersistent=cp_bytes())
  if key == "NrdrPcmSpeedDeadzone":
    params.values["HondaLiveLearningGas"] = True
  if not offroad:
    with pytest.raises(ValueError):
      save({key: encoded(int(value) if type(value) is bool else value)})
    assert not params.writes
    return
  save({key: encoded(int(value) if type(value) is bool else value)})
  assert params.get(key) == value and type(params.get(key)) is type(value)
  assert params.get_bool("OnroadCycleRequested")
  assert {name for name, _ in params.writes} == {key, "OnroadCycleRequested", "ParamsVersion"}


@pytest.mark.parametrize("key,value", CHOICES)
@pytest.mark.parametrize("offroad", [False, True])
def test_four_native_choices_keep_parked_gate_and_explicit_cycle(key, value, offroad):
  ui = state()
  ui.is_offroad = lambda: offroad
  if key == "NrdrPcmSpeedDeadzone":
    ui.params.values["HondaLiveLearningGas"] = True
    saved = honda_pcm.save_pcm_speed_deadzone(ui, value)
  elif key == "HondaLiveLearningGas":
    saved = honda_pcm.save_live_gas_choice(ui, value)
  else:
    saved = honda_pcm.save_pcm_choice(ui, key, value)
  assert saved is offroad
  assert ui.params.writes == ([(key, value), ("OnroadCycleRequested", True)] if offroad else [])


@pytest.mark.parametrize("flag", [524288, HondaFlags.MVL_LONGITUDINAL])
def test_native_parked_banner_does_not_call_cached_mode_active(flag):
  ui = state(flags=int(HondaFlags.NIDEC | flag))
  path = ROOT / "openpilot/nrdr/ui/settings/longitudinal_tuning.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "LongitudinalTuningLayout")
  init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
  status = next(node for node in init.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "status" for target in node.targets))
  env = {**vars(honda_pcm), "ui_state": ui, "tr": lambda text: text, "ListItem": lambda **kwargs: kwargs}
  exec(compile(ast.Module([status], []), str(path), "exec"), env)
  assert env["status"]["title"]() == "Parked - saved settings apply next drive"
  assert env["status"]["description"]() == COPY + " MVL Off next drive"
  assert not ui.params.writes
