"""Persistence regressions only: execute production writers without device I/O."""

import ast
import base64
from enum import IntEnum
import gzip
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import pytest

from openpilot.nrdr.tests.test_experimental_button_regressions import RecordingParams, load_definitions
from openpilot.nrdr.tests import test_handcrafted_request_routing as routing_tests
from openpilot.nrdr.tests.test_param_defaults import _apply, _load_defaults


ROOT = Path(__file__).resolve().parents[3]
VISION = "SmartCruiseControlVision"
EXPERIMENTAL = "ExperimentalMode"


def boot(params):
  defaults, _ = _load_defaults()
  _apply(defaults, params)
  params.flush()


def method(relative, class_name, method_name):
  tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
  return next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)


def execute(nodes, namespace):
  exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), "production_preference_writer", "exec"), namespace)


@pytest.mark.parametrize("key", (VISION, EXPERIMENTAL))
def test_existing_off_survives_repeated_boot_but_fresh_default_is_unchanged(key):
  params = RecordingParams({key: False})
  for _ in range(3):
    boot(params)
    assert params.get(key) is False
  assert not any(action[1] == key for action in params.actions)
  fresh = RecordingParams()
  boot(fresh)
  assert fresh.get(key) is True


def cleanup_vision(params, has_long):
  namespace = {"Params": RecordingParams, "structs": NS(CarParams=NS(SteerControlType=NS(angle=2)), CarParamsSP=object),
               "cloudlog": Mock(), "set_speed_limit_assist_availability": Mock()}
  load_definitions("openpilot/sunnypilot/selfdrive/car/interfaces.py", {"_cleanup_unsupported_params"}, namespace)
  namespace["_cleanup_unsupported_params"](NS(steerControlType=1, openpilotLongitudinalControl=has_long),
                                            NS(intelligentCruiseButtonManagementAvailable=False, pcmCruiseSpeed=True), params)


def cleanup_experimental(params, has_long):
  init = method("openpilot/selfdrive/selfdrived/selfdrived.py", "SelfdriveD", "__init__")
  branch = next(node for node in init.body if isinstance(node, ast.If)
                and ast.unparse(node.test) == "not self.CP.openpilotLongitudinalControl")
  execute([branch], {"self": NS(params=params, CP=NS(openpilotLongitudinalControl=has_long))})


@pytest.mark.parametrize("key,cleanup", ((VISION, cleanup_vision), (EXPERIMENTAL, cleanup_experimental)))
@pytest.mark.parametrize("initial", (False, True, None))
def test_unsupported_cleanup_leaves_durable_off_not_missing_default(key, cleanup, initial):
  params = RecordingParams({} if initial is None else {key: initial})
  cleanup(params, False)
  # Cleanup remains disabling, but no longer erases an explicit Off.
  assert params.get(key) is False
  assert ("remove", key) not in params.actions
  if initial is False:
    assert not any(action[1] == key for action in params.actions)
  boot(params)
  assert params.get(key) is False


@pytest.mark.parametrize("key,cleanup", ((VISION, cleanup_vision), (EXPERIMENTAL, cleanup_experimental)))
@pytest.mark.parametrize("initial", (False, True))
def test_supported_cleanup_leaves_explicit_choice_alone(key, cleanup, initial):
  params = RecordingParams({key: initial})
  cleanup(params, True)
  assert params.get(key) is initial
  assert not any(action[1] == key for action in params.actions)


@pytest.mark.parametrize("has_cp,has_long,has_icbm,offroad", (
  (True, True, False, False), (True, False, True, False), (True, False, False, False),
  (True, False, False, True), (False, False, False, True),
))
@pytest.mark.parametrize("when", ("committed_during", "committed_after", "queued_before"))
@pytest.mark.parametrize("initial", (False, True))
def test_cruise_refresh_cannot_replay_stale_vision_choice(has_cp, has_long, has_icbm, offroad, when, initial):
  params = RecordingParams({VISION: initial, "SmartCruiseControlMap": False, "CustomAccIncrementsEnabled": False})
  namespace = {"tr": lambda text: text, "CRUISE_PARAMS": ("CustomAccIncrementsEnabled", VISION, "SmartCruiseControlMap")}
  load_definitions("openpilot/nrdr/ui/settings_policy.py", {"snapshot_params", "_restore_params", "apply_cruise_preferences"}, namespace)
  original = namespace["apply_cruise_preferences"]

  def apply(*args):
    if when == "committed_during":
      params.put_bool(VISION, not initial, block=True)
    original(*args)

  namespace["apply_cruise_preferences"] = apply
  namespace["Widget"] = type("Widget", (), {"_update_state": lambda self: None})
  namespace["ui_state"] = NS(params=params, has_longitudinal_control=has_long, has_icbm=has_icbm, is_offroad=lambda: offroad,
                             CP=NS(alphaLongitudinalAvailable=True, pcmCruise=False) if has_cp else None,
                             CP_SP=NS(intelligentCruiseButtonManagementAvailable=has_icbm) if has_cp else None)
  for name in ("ICBM_DESC", "ICMB_UNAVAILABLE", "ICMB_UNAVAILABLE_LONG_AVAILABLE", "ICMB_UNAVAILABLE_LONG_UNAVAILABLE",
               "ONROAD_ONLY_DESCRIPTION", "ACC_PCMCRUISE_DISABLED_DESCRIPTION", "ACC_ENABLED_DESCRIPTION", "ACC_NOLONG_DESCRIPTION"):
    namespace[name] = name
  update = method("openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise.py", "CruiseLayout", "_update_state")
  execute([ast.ClassDef(name="CruiseLayout", bases=[ast.Name(id="Widget", ctx=ast.Load())], keywords=[], body=[update], decorator_list=[])], namespace)
  layout = namespace["CruiseLayout"]()
  for attr in ("icbm_toggle", "custom_acc_toggle", "scc_v_toggle", "scc_m_toggle", "accel_boost_toggle"):
    setattr(layout, attr, Mock(description="", action_item=Mock(get_state=lambda: False)))
  layout._on_custom_acc_toggle = Mock()
  if when == "queued_before":
    params.put_bool(VISION, not initial)
  layout._update_state()
  if when == "committed_after":
    params.put_bool(VISION, not initial, block=True)
  params.flush()
  assert params.get(VISION) is not initial
  assert [action for action in params.actions if action[1] == VISION] == [("put", VISION, not initial)]


@pytest.mark.parametrize("relative", ("openpilot/selfdrive/ui/layouts/settings/toggles.py", "openpilot/selfdrive/ui/mici/layouts/settings/toggles.py"))
@pytest.mark.parametrize("initial", (False, True, None))
def test_native_experimental_cleanup_preserves_off_through_next_boot(relative, initial):
  params = RecordingParams({} if initial is None else {EXPERIMENTAL: initial})
  tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
  update = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "_update_toggles")
  branch = next(node for node in ast.walk(update) if isinstance(node, ast.If) and ast.unparse(node.test) == "ui_state.has_longitudinal_control")
  layout = NS(_params=params, _toggles={EXPERIMENTAL: Mock()}, _long_personality_setting=Mock(), _is_release=False,
              _experimental_btn=Mock(), _personality_toggle=Mock())
  execute([branch], {"self": layout, "ui_state": NS(params=params, has_longitudinal_control=False, CP=NS(alphaLongitudinalAvailable=True)),
                     "tr": lambda text: text, "e2e_description": ""})
  assert params.get(EXPERIMENTAL) is False
  assert ("remove", EXPERIMENTAL) not in params.actions
  boot(params)
  assert params.get(EXPERIMENTAL) is False


@pytest.mark.parametrize("key", (VISION, EXPERIMENTAL))
@pytest.mark.parametrize("compressed", (False, True))
def test_sunnylink_explicit_off_routes_and_survives_boot(key, compressed):
  routing = routing_tests.TestHandcraftedRequestRouting()
  routing.setUp()
  params = RecordingParams({key: True, "IsOffroad": True})
  params.get_type = lambda _: 1  # Native BOOL type.
  namespace = {"Params": lambda: params, "IntEnum": IntEnum, "base64": base64, "gzip": gzip, "json": json}
  load_definitions("openpilot/common/params.py", {"ParamKeyType"}, namespace)
  load_definitions("openpilot/sunnypilot/sunnylink/utils.py", {"_convert_param_to_type", "save_param_from_base64_encoded_string"}, namespace)
  routing.namespace["params"] = params
  routing.namespace["save_param_from_base64_encoded_string"] = namespace["save_param_from_base64_encoded_string"]
  raw = b"False"
  routing.save_params({key: base64.b64encode(gzip.compress(raw) if compressed else raw).decode()}, compressed)
  assert params.get(key) is False
  boot(params)
  assert params.get(key) is False


@pytest.mark.parametrize("key", (VISION, EXPERIMENTAL))
def test_explicit_backup_restore_is_still_allowed_not_an_automatic_writer(key):
  params = RecordingParams({key: True})
  params.get_type = lambda _: 1
  params.all_keys = lambda _: [key.encode()]
  name = "openpilot.nrdr.features.lateral.lane_guidance"
  spec = importlib.util.spec_from_file_location(name, ROOT / "openpilot/nrdr/features/lateral/lane_guidance.py")
  lane = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(lane)
  namespace = {"Params": lambda: params, "IntEnum": IntEnum, "base64": base64, "gzip": gzip, "json": json,
               "cloudlog": Mock(), "ParamKeyFlag": NS(BACKUP=0x100)}
  load_definitions("openpilot/common/params.py", {"ParamKeyType"}, namespace)
  load_definitions("openpilot/sunnypilot/sunnylink/utils.py", {"_convert_param_to_type", "save_param_from_base64_encoded_string"}, namespace)
  apply = method("openpilot/sunnypilot/sunnylink/backups/manager.py", "BackupManagerSP", "_apply_config")
  execute([apply], namespace)
  with patch.dict(sys.modules, {name: lane}):
    namespace["_apply_config"](NS(params=params), {key: base64.b64encode(b"False").decode()})
  assert params.get(key) is False
  boot(params)
  assert params.get(key) is False


def test_handcrafted_profiles_do_not_own_these_user_preferences():
  from openpilot.nrdr.params.profiles import HANDCRAFTED_LATERAL_PROFILES
  for profile in HANDCRAFTED_LATERAL_PROFILES.values():
    assert not {VISION, EXPERIMENTAL}.intersection(dict(profile.values))
