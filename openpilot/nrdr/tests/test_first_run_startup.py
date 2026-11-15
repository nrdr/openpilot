"""Exercise real startup/UI call sites with local test settings, without CAN or a GUI."""
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.services.model_manager import select_default_model
from openpilot.nrdr.params.profiles import (
  FIRMWARE_DEFAULTS_KEY, HandcraftedLateralUnsafeStateError,
  consume_handcrafted_lateral_request, request_handcrafted_lateral_profile,
)
from openpilot.nrdr.tests.test_handcrafted_preset_v18 import FakeParams, cp_sp, vehicle_cp
from openpilot.nrdr.tests.test_model_manager import bundle
from openpilot.nrdr.tests.test_param_defaults import _apply, _load_defaults
from openpilot.nrdr.tests.test_suggested_defaults import FileParams

ROOT = Path(__file__).resolve().parents[3]
MODEL_KEYS = ("NrdrAutoSelectModel", "ModelManager_ActiveBundle", "ModelManager_ActiveBundleChestnut", "ModelManager_DownloadRef")


def _call_name(node):
  return ast.unparse(node.func) if isinstance(node, ast.Call) else ""


def _card_startup(params, cp=None, sp=None, consumer=consume_handcrafted_lateral_request):
  """Keep every statement/guard after identification, not just the inner consumer call."""
  source = ROOT / "openpilot/selfdrive/car/card.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  car = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Car")
  init = next(node for node in car.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
  identify = next(node for node in init.body if isinstance(node, ast.If) and ast.unparse(node.test) == "CI is None")
  identified = next(i for i, node in enumerate(identify.body) if isinstance(node, ast.Assign) and
                    any(ast.unparse(target) == "self.CP_SP" for target in node.targets))
  startup = identify.body[identified + 1:]
  publications = [node for node in init.body if isinstance(node, ast.Expr) and
                  _call_name(node.value) == "self.params.put" and
                  isinstance(node.value.args[0], ast.Constant) and node.value.args[0].value in ("CarParams", "CarParamsSP")]
  assert len(publications) == 2 and max(node.end_lineno for node in startup) < min(node.lineno for node in publications)
  errors = []
  namespace = {
    "self": SimpleNamespace(params=params, CP=cp if cp is not None else vehicle_cp(), CP_SP=sp if sp is not None else cp_sp()),
    "consume_handcrafted_lateral_request": consumer, "HandcraftedLateralUnsafeStateError": HandcraftedLateralUnsafeStateError,
    "cloudlog": SimpleNamespace(exception=errors.append), "cp_bytes": "test-cp", "cp_sp_bytes": "test-cp-sp",
  }
  # Serialize nothing and contact no vehicle; execute the real publication calls with sentinel payloads.
  exec(compile(ast.Module(body=startup + publications, type_ignores=[]), str(source), "exec"), namespace)
  return errors


def _fresh_params(tmp_path):
  params = FileParams(tmp_path)
  defaults, _ = _load_defaults()
  _apply(defaults, params)
  params.put_bool("NrdrHandcraftedLateralTune", False, block=True)
  return params


def test_card_consumes_fresh_defaults_before_publishing_params(tmp_path):
  params = _fresh_params(tmp_path)
  assert params.get(FIRMWARE_DEFAULTS_KEY) and params.get("NrdrLateralController") == 0
  assert _card_startup(params) == []
  assert params.get("NrdrLateralController") == 1 and params.get("NrdrSteerRatioMode") == 3
  assert params.get("NrdrSteerRatioHybrid") is False and params.get(FIRMWARE_DEFAULTS_KEY) == {}
  assert not params.get_bool("NrdrSuggestedSettings")
  enabled = next(i for i, call in enumerate(params.calls) if call[1:3] == ("NrdrLateralController", 1))
  query_done = next(i for i, call in enumerate(params.calls) if call[1] == "FirmwareQueryDone")
  published = [i for i, call in enumerate(params.calls) if call[1] in ("CarParams", "CarParamsSP")]
  assert enabled < query_done < min(published)


@pytest.mark.parametrize("change", ["stock", "unknown-rack", "wrong-car", "wrong-controller", "owner-rewrite"])
def test_card_leaves_unadmitted_or_owner_edited_defaults_off(tmp_path, change):
  params = _fresh_params(tmp_path)
  cp = vehicle_cp()
  if change == "unknown-rack":
    cp = vehicle_cp(firmware=b"39990-TEG-A999")
  elif change == "wrong-car":
    cp = vehicle_cp("HONDA_ACCORD")
  elif change == "wrong-controller":
    cp = vehicle_cp(controller="torque")
  elif change == "owner-rewrite":
    params.put("NrdrLateralController", 0, block=True)
  assert _card_startup(params, cp, cp_sp(modified=change != "stock")) == []
  assert params.get("NrdrLateralController") == 0 and params.get("NrdrSteerRatioMode") == 0
  assert params.get(FIRMWARE_DEFAULTS_KEY) == {}


def test_card_without_pending_defaults_preserves_saved_choices(tmp_path):
  saved = {"NrdrLateralController": 0, "NrdrSteerRatioMode": 2, "NrdrSteerRatioHybrid": True,
           "HondaOverrideFadeUpSecs": .01, "NrdrHandcraftedLateralTune": False}
  params = FileParams(tmp_path, saved)
  assert _card_startup(params) == []
  assert all(params.get(key) == value for key, value in saved.items())
  assert [call[1] for call in params.calls] == ["FirmwareQueryDone", "CarParams", "CarParamsSP"]


def test_card_still_consumes_an_explicit_preset_request(tmp_path):
  params = FileParams(tmp_path, {"IsOffroad": True})
  cp, sp = vehicle_cp(), cp_sp()
  assert request_handcrafted_lateral_profile(cp, sp, params)
  assert _card_startup(params, cp, sp) == []
  assert params.get("NrdrLateralController") == 1 and params.get_bool("NrdrSuggestedSettings")
  assert not params.get_bool("NrdrHandcraftedLateralTune")


def test_card_recoverable_default_failure_keeps_controller_off(tmp_path):
  params = _fresh_params(tmp_path)
  params.fail_once_keys.add("NrdrSteerRatioMode")
  assert _card_startup(params) == ["car: lateral startup settings apply failed"]
  assert params.get("NrdrLateralController") == 0 and params.get(FIRMWARE_DEFAULTS_KEY) == {}
  assert params.get("CarParamsSP") == "test-cp-sp"


def test_card_unsafe_failure_stops_before_firmware_ready_or_publication():
  def unsafe(*args, **kwargs):
    raise HandcraftedLateralUnsafeStateError("unsafe state")

  params = FakeParams()
  with pytest.raises(HandcraftedLateralUnsafeStateError, match="unsafe state"):
    _card_startup(params, consumer=unsafe)
  assert not params.calls


def _first_run(params):
  source = ROOT / "openpilot/nrdr/ui/home/layout.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "FirstRunSetup")
  dialogs = []
  namespace = {
    "Params": object, "DialogResult": SimpleNamespace(CONFIRM=1, CANCEL=0), "tr": lambda text: text,
    "ConfirmDialog": lambda text, button, callback: SimpleNamespace(text=text, button=button, callback=callback),
    "gui_app": SimpleNamespace(push_widget=dialogs.append),
  }
  exec(compile(ast.Module(body=[cls], type_ignores=[]), str(source), "exec"), namespace)
  return namespace["FirstRunSetup"](params), dialogs


@pytest.mark.parametrize("result", [0, 1])
@pytest.mark.parametrize("manager_first", [False, True])
@pytest.mark.parametrize("saved", [{}, {"NrdrAutoSelectModel": False}, {"ModelManager_ActiveBundle": {"ref": "saved-model"}},
                                  {"ModelManager_DownloadRef": "owner-request"}])
def test_maps_decision_is_independent_of_model_manager_order(result, manager_first, saved):
  params = FakeParams(saved)
  defaults, _ = _load_defaults()
  _apply(defaults, params)
  setup, dialogs = _first_run(params)
  available = [bundle(59, "Pop Model v2", "compatible-pop")]
  if manager_first:
    select_default_model(params, available)
  before = {key: params.get(key) for key in MODEL_KEYS}
  setup.update()
  assert len(dialogs) == 1 and dialogs[0].button == "Download maps"
  assert dialogs[0].text.startswith("Download offline maps")
  assert "optional" in dialogs[0].text and "does not change your model selection" in dialogs[0].text
  dialogs[0].callback(result)
  assert {key: params.get(key) for key in MODEL_KEYS} == before
  if not manager_first:
    select_default_model(params, available)
  expected_ref = "compatible-pop" if not saved else saved.get("ModelManager_DownloadRef")
  assert params.get("ModelManager_DownloadRef") == expected_ref
  assert params.get_bool("NrdrFirstRunSetupDone")
  assert params.get_bool("OsmLocal") == bool(result)
  assert params.get_bool("OsmDbUpdatesCheck") == bool(result)
  setup.update()
  assert len(dialogs) == 1
  restarted, new_dialogs = _first_run(params)
  restarted.update()
  assert not new_dialogs


def test_maps_decline_preserves_pending_compatible_model_request():
  params = FakeParams()
  defaults, _ = _load_defaults()
  _apply(defaults, params)
  setup, dialogs = _first_run(params)
  setup.update()
  dialogs[0].callback(0)
  select_default_model(params, [bundle(59, "Pop Model v2", "legacy-pop", compiler="")])
  assert params.get_bool("NrdrAutoSelectModel") and params.get("ModelManager_DownloadRef") is None
  select_default_model(params, [bundle(60, "Pop Model v2", "compatible-pop")])
  assert params.get("ModelManager_DownloadRef") == "compatible-pop" and not params.get_bool("NrdrAutoSelectModel")
