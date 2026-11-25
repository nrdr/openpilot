"""Cleanup contracts, independent of native Params, messaging and actuators."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.params.tuning_policy import LONG_SCALE_KEYS, reset_learning_scales, tuning_write_allowed
from openpilot.nrdr.params.profiles import disable_suggested_settings
from openpilot.nrdr.features.lateral.lane_change_tuning import bounded_setting, optimized_lane_change_active
from openpilot.nrdr.features.lateral.vfn_geometry import NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_VGR_ANGLE_BP
from openpilot.nrdr.features.lateral.vfn_rack_map import ClarityRackMap
from opendbc.car.honda.yaw_rate import get_yaw_rate_calibration

ROOT = Path(__file__).resolve().parents[3]


class MemoryParams(dict):
  def get(self, key, *args, **kwargs):
    return super().get(key)

  def get_bool(self, key):
    return bool(self.get(key))

  def put(self, key, value, block=False):
    assert block
    self[key] = value

  put_bool = put


@pytest.mark.parametrize("key", ["LatPScaleLowSpeed", "NrdrLatRateDampingHighway", "NrdrSteerRatioBlendStart",
  "LaneCentering", "LaneCenteringStrength", "HondaLpfTauLowSpeed", "HondaOverrideFadeDownSecs"])
def test_suggested_locks_touched_controls_and_off_preserves_values(key):
  params = MemoryParams(NrdrSuggestedSettings=True, NrdrHandcraftedLateralTune=False, **{key: 12})
  assert not tuning_write_allowed(params, key)
  disable_suggested_settings(params)
  assert params[key] == 12
  assert tuning_write_allowed(params, key)


@pytest.mark.parametrize("key", ["LatFScaleStandard", "NrdrLatRateDampingLowSpeed",
                                 "HondaTorqueLowPassFilter", "HondaLpfTauHighway"])
@pytest.mark.parametrize("controller", [1, "1", b"1", 2, "2", b"2"])
def test_yaw_locks_ignored_pif_controls_without_changing_the_saved_values(key, controller):
  params = MemoryParams(NrdrLateralController=controller, **{key: 7})
  assert not tuning_write_allowed(params, key)
  assert params[key] == 7
  params["NrdrLateralController"] = 0
  assert tuning_write_allowed(params, key)


@pytest.mark.parametrize("key", ["NrdrSteerRatioMode", "NrdrSteerRatioModelBlend"])
def test_shared_geometry_is_not_locked_by_controller_selection(key):
  from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
  params = MemoryParams(NrdrLateralController=1, NrdrSuggestedSettings=False)
  assert tuning_write_allowed(params, key)
  item = apply_sunnylink_metadata({"key": key})
  assert item["enablement"] == [
    {"type": "not", "condition": {"type": "param", "key": "NrdrLateralController", "equals": 3}},
    {"type": "any", "conditions": [
      {"type": "offroad_only"},
      {"type": "not", "condition": {"type": "param", "key": "NrdrSuggestedSettings", "equals": True}},
    ]},
    {"type": "not", "condition": {"type": "param", "key": "NrdrHandcraftedLateralTune", "equals": True}},
  ]
  params["NrdrSuggestedSettings"] = True
  assert not tuning_write_allowed(params, key)


@pytest.mark.parametrize("key", ["LagdToggle", "LagdToggleDelay"])
@pytest.mark.parametrize("controller", [1, "1", b"1", 2, "2", b"2"])
def test_only_measured_firmware_schedule_locks_live_manual_delay(key, controller):
  from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
  params = MemoryParams(NrdrLateralController=controller, **{key: .31})
  assert tuning_write_allowed(params, key)  # no prediction schedule: live/manual delay
  assert not tuning_write_allowed(params, key, firmware_prediction_schedule=True)
  item = apply_sunnylink_metadata({"key": key})
  assert item["enablement"][-1] == {"type": "not", "condition": {"type": "all", "conditions": [
    {"type": "any", "conditions": [
      {"type": "param", "key": "NrdrLateralController", "equals": selected} for selected in (1, 2)
    ]},
    {"type": "capability", "field": "nrdr_firmware_prediction_schedule", "equals": True},
  ]}}
  params["NrdrLateralController"] = 0
  assert tuning_write_allowed(params, key)
  assert tuning_write_allowed(params, key, firmware_prediction_schedule=True)
  assert params[key] == .31


def test_mvl_locks_scales_without_erasing_custom_saved_values():
  params = MemoryParams(HondaLiveLearningGas=True, **dict.fromkeys(LONG_SCALE_KEYS, 175))
  reset_learning_scales(params)
  assert all(params[k] == 175 and not tuning_write_allowed(params, k) for k in LONG_SCALE_KEYS)
  params["HondaLiveLearningGas"] = False
  assert all(params[k] == 175 and tuning_write_allowed(params, k) for k in LONG_SCALE_KEYS)


@pytest.mark.parametrize("state,active", [(0, False), (1, False), (2, True), (3, True)])
def test_optimized_lane_change_gate_supports_capnp_enum(monkeypatch, state, active):
  monkeypatch.setattr("openpilot.nrdr.features.lateral.lane_change_tuning.active_model_supports_optimized_lane_changes", lambda: True)
  assert optimized_lane_change_active({}, NS(raw=state)) == active
  assert not optimized_lane_change_active({"NrdrOptimizedLaneChanges": False}, NS(raw=state))


def test_lane_change_retired_sliders_cannot_change_fixed_settings(monkeypatch):
  monkeypatch.setattr("openpilot.nrdr.features.lateral.lane_change_tuning.active_model_supports_optimized_lane_changes", lambda: True)
  stale = {"NrdrLaneChangeMinTime": 9, "NrdrLaneChangeEntrySrReduction": 0,
           "NrdrLaneChangeEntryReturnTime": 2, "NrdrLaneChangeTorqueFactor": 9, "NrdrLaneChangeFrictionPercent": 100}
  for key, expected in (("NrdrLaneChangeMinTime", .5), ("NrdrLaneChangeEntrySrReduction", 5),
                        ("NrdrLaneChangeEntryReturnTime", 1), ("NrdrLaneChangeTorqueFactor", 2),
                        ("NrdrLaneChangeFrictionPercent", 0)):
    assert bounded_setting(stale, key, 0, 0, 10) == expected
    assert not tuning_write_allowed(MemoryParams(), key)


@pytest.mark.parametrize("speed", [0, 7, 15, 30])
@pytest.mark.parametrize("roll", [-.03, 0, .03])
def test_vfn_rack_round_trip(speed, roll):
  rack = ClarityRackMap(2.75, (NRDR_CLARITY_VGR_LINEAR_BP, NRDR_CLARITY_VGR_ANGLE_BP))
  for angle in [-430, -154, -40, -3, 0, 2, 25, 90, 300]:
    curvature = rack.curvature_from_angle(angle, speed, roll)
    assert rack.angle_from_curvature(curvature, speed, roll) == pytest.approx(angle, abs=.001)


def test_real_yaw_is_clarity_only_and_stationary_zero_is_bounded():
  assert get_yaw_rate_calibration("HONDA_CIVIC_BOSCH") is None
  yaw = get_yaw_rate_calibration("HONDA_CLARITY")
  assert yaw.update(-1., False) == 0
  assert yaw.update(0., False) == pytest.approx(4 * .246 + .12)
  for _ in range(250):
    yaw.update(-.75, True)
  assert yaw.zero == 509
  yaw.update(0, False)
  for _ in range(400):
    yaw.update(5, True)
  assert yaw.zero == 509  # a gross sensor offset is never learned as zero


def _definitions(relative, env):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
  exec(compile(tree, str(path), "exec"), env)
  return env


@pytest.mark.parametrize("offroad,available,value,allowed", [
  (True, True, 1, True), (True, False, 1, False), (False, True, 1, False),
  (True, False, 0, True), (False, True, 0, False), (True, True, 2, True),
  (True, False, 2, False), (False, True, 2, False), (True, True, 3, True), (True, False, 3, False), (False, True, 3, False),
  (True, True, None, False), (True, True, "2", False), (True, True, "garbage", False),
])
def test_native_controller_picker_rechecks_vehicle_and_offroad_on_confirmation(offroad, available, value, allowed):
  from collections.abc import Callable
  params = MemoryParams(NrdrLateralController=0)
  env = {"Widget": object, "Callable": Callable,
         "ui_state": NS(params=params, CP=object(), CP_SP=object(), is_offroad=lambda: offroad),
         "firmware_controller_profile": lambda cp, sp, **kw: True if available else None,
         "angle_controller_available": lambda cp, sp: available and value == 3}
  picker = _definitions("openpilot/nrdr/ui/settings/pidf_ground.py", env)["PidfGroundLayout"]
  assert picker._commit_controller_selection(value) == allowed
  assert params["NrdrLateralController"] == (value if allowed and value != 3 else 0)


@pytest.mark.parametrize("available", [False, True])
@pytest.mark.parametrize("offroad", [False, True])
def test_native_picker_only_offers_both_ptm_choices_for_supported_parked_cars(available, offroad):
  from collections.abc import Callable
  shown = []
  env = {"Widget": object, "Callable": Callable, "tr": lambda text: text,
         "ui_state": NS(params=MemoryParams(NrdrLateralController=0), CP=object(), CP_SP=object(), is_offroad=lambda: offroad),
         "firmware_controller_profile": lambda *_, **kw: True if available else None,
         "angle_controller_available": lambda *_: False,
         "MultiOptionDialog": lambda title, options, selected, **kwargs: NS(options=options, selected=selected),
         "gui_app": NS(push_widget=shown.append)}
  picker = _definitions("openpilot/nrdr/ui/settings/pidf_ground.py", env)["PidfGroundLayout"]
  picker.__new__(picker)._show_controller_selector()
  assert len(shown) == int(offroad)
  if offroad:
    assert shown[0].options == (["PIF Control", "PTM Controller", "PTM Testing"] if available else ["PIF Control"])


def test_angle_firmware_displays_angle_and_never_accepts_a_torque_choice():
  from collections.abc import Callable
  shown = []
  state = NS(params=MemoryParams(NrdrLateralController=0), CP=object(), CP_SP=object(), is_offroad=lambda: True)
  env = {"Widget": object, "Callable": Callable, "tr": lambda text: text, "ui_state": state,
         "firmware_controller_profile": lambda *_, **kw: None, "angle_controller_available": lambda *_: True,
         "MultiOptionDialog": lambda title, options, selected, **kw: NS(options=options, selection=selected, **kw),
         "DialogResult": NS(CONFIRM=1), "gui_app": NS(push_widget=shown.append)}
  picker = _definitions("openpilot/nrdr/ui/settings/pidf_ground.py", env)["PidfGroundLayout"]
  layout = picker.__new__(picker)
  layout._show_controller_selector()
  assert not shown
  assert layout._controller_label() == "Angle Controller"
  assert not layout._commit_controller_selection(0)
  assert not layout._commit_controller_selection(2)
  assert layout._commit_controller_selection(3)
  assert state.params["NrdrLateralController"] == 0


@pytest.mark.parametrize("controller", [0, 1, "1", b"1", 2, "2", b"2", 3, "3", b"3"])
@pytest.mark.parametrize("detected", [False, True])
def test_native_ptm_choices_hide_yaw_correction_and_keep_fixed_tuning_locked(controller, detected):
  from collections.abc import Callable
  from unittest.mock import Mock
  class Widget:
    def _update_state(self):
      pass
  env = {"Widget": Widget, "Callable": Callable, "tr": lambda text: text,
         "ui_state": NS(params=MemoryParams(NrdrLateralController=controller), CP=object(), CP_SP=object(), is_offroad=lambda: True),
         "firmware_controller_profile": lambda *_: None, "supports_interpolated_torque_pif": lambda *_: True,
         "angle_controller_available": lambda *_: detected,
         "tuning_write_allowed": tuning_write_allowed, "ANGLE_TUNING_KEYS": {"HondaClarityAngleCap3", "HondaEpsAngleRateLimit"}}
  picker = _definitions("openpilot/nrdr/ui/settings/pidf_ground.py", env)["PidfGroundLayout"]
  layout = picker.__new__(picker)
  layout._controller = Mock()
  angle = detected or controller in (3, "3", b"3")
  layout._tuning_items = {key: Mock() for key in ("NrdrDeviceYawCorrection", "LatPScaleStandard", *env["ANGLE_TUNING_KEYS"])}
  layout._update_state()
  layout._tuning_items["NrdrDeviceYawCorrection"].set_visible.assert_called_once_with(controller == 0 or angle)
  for key, item in layout._tuning_items.items():
    item.action_item.set_enabled.assert_called_once_with(detected if key in env["ANGLE_TUNING_KEYS"] else controller == 0 and not angle)
  description = layout._controller.set_description.call_args.args[0]
  assert "experimental and starts with the same PTM Timing Off behavior; no new tuning is deployed" in description
  assert "Change while parked. Applies next drive." in description


def _vision():
  params = MemoryParams(SmartCruiseControlVision=True)
  state = NS(disabled=0, enabled=1, entering=2, turning=3, leaving=4, overriding=5)
  env = {"np": np, "Params": lambda: params, "VisionState": state, "V_CRUISE_UNSET": 255., "MIN_V": 5., "messaging": NS(SubMaster=object)}
  env["custom"] = NS(LongitudinalPlanSP=NS(SmartCruiseControl=NS(VisionState=state)))
  cls = _definitions("openpilot/sunnypilot/selfdrive/controls/lib/smart_cruise_control/vision_controller.py", env)["SmartCruiseControlVision"]
  model = NS(orientationRate=NS(z=[.04] * 33), velocity=NS(x=[25.] * 33))
  sm = {"modelV2": model, "controlsState": NS(curvature=.002)}
  controller = cls()
  controller.state = state.turning
  controller.is_active = controller.is_enabled = True
  controller.output_v_target = 10
  return controller, params, sm, state


def test_vision_off_clears_an_active_curve_target_in_one_update():
  controller, params, sm, state = _vision()
  params["SmartCruiseControlVision"] = False
  controller.update(sm, True, False, 25., 0., 30.)
  assert controller.state == state.disabled and not controller.is_active
  assert controller.output_v_target == controller.get_v_target_from_control() == 255.
  assert controller.output_a_target == controller.get_a_target_from_control() == 0.


def test_bad_model_does_not_reenable_vision_in_same_frame():
  controller, _, sm, state = _vision()
  sm["modelV2"].orientationRate.z = []
  controller.update(sm, True, False, 25., 0., 30.)
  assert controller.state == state.disabled and not controller.is_active
  assert controller.output_v_target == 255.


def test_retired_overshoot_and_engine_braking_settings_cannot_be_written():
  from openpilot.nrdr.params.generated import ALL_KEYS
  for key in ("NrdrCruiseOverspeedAllowance", "NrdrExperimentalEngineBraking"):
    assert key not in ALL_KEYS
    assert not tuning_write_allowed(MemoryParams(), key)
